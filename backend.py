

import os
import re
import json
from pathlib import Path
from typing import TypedDict

import chromadb
from pypdf import PdfReader
from sentence_transformers import SentenceTransformer
from google import genai
from langgraph.graph import StateGraph, START, END


# ============================================================
# CONFIG
# ============================================================

PDF_PATH = Path("data/1.pdf")

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY not found.")

client = genai.Client(
    api_key=GEMINI_API_KEY
)

MODEL_NAME = "gemini-3.5-flash-lite"


# ============================================================
# EMBEDDING MODEL
# ============================================================

embedding_model = SentenceTransformer(
    "BAAI/bge-small-en-v1.5"
)


# ============================================================
# PDF EXTRACTION
# ============================================================

def clean_text(text):
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def load_pdf():

    reader = PdfReader(
        str(PDF_PATH)
    )

    documents = []

    for page_number, page in enumerate(
        reader.pages,
        start=1
    ):

        text = page.extract_text()

        if text:

            documents.append({
                "text": clean_text(text),
                "page": page_number,
                "source": PDF_PATH.name
            })

    return documents


# ============================================================
# CHUNKING
# ============================================================

def create_chunks(
    documents,
    chunk_size=500,
    overlap=50
):

    chunks = []
    all_words = []

    for doc in documents:

        words = doc["text"].split()

        for word in words:

            all_words.append({
                "word": word,
                "page": doc["page"],
                "source": doc["source"]
            })

    start = 0
    chunk_id = 0

    while start < len(all_words):

        end = min(
            start + chunk_size,
            len(all_words)
        )

        chunk_items = all_words[
            start:end
        ]

        chunk_text = " ".join(
            item["word"]
            for item in chunk_items
        )

        chunks.append({

            "id": f"chunk_{chunk_id}",

            "text": chunk_text,

            "source":
                chunk_items[0]["source"],

            "start_page":
                chunk_items[0]["page"],

            "end_page":
                chunk_items[-1]["page"]
        })

        chunk_id += 1

        start += (
            chunk_size - overlap
        )

    return chunks


# ============================================================
# CHROMADB
# ============================================================

chroma_client = chromadb.PersistentClient(
    path="chroma_db"
)

collection = chroma_client.get_or_create_collection(
    name="research_documents"
)


# ============================================================
# INDEX DOCUMENT
# ============================================================

def build_index():

    documents = load_pdf()

    chunks = create_chunks(
        documents
    )

    existing = collection.count()

    if existing == 0:

        texts = [
            chunk["text"]
            for chunk in chunks
        ]

        embeddings = embedding_model.encode(
            texts,
            show_progress_bar=False
        )

        ids = [
            chunk["id"]
            for chunk in chunks
        ]

        metadatas = [

            {
                "source":
                    chunk["source"],

                "start_page":
                    chunk["start_page"],

                "end_page":
                    chunk["end_page"]
            }

            for chunk in chunks
        ]

        collection.add(
            ids=ids,
            documents=texts,
            embeddings=embeddings.tolist(),
            metadatas=metadatas
        )

    return collection.count()


chunk_count = build_index()


# ============================================================
# DOCUMENT SEARCH
# ============================================================

def document_search(
    query,
    top_k=3
):

    query_embedding = embedding_model.encode(
        query
    ).tolist()

    results = collection.query(

        query_embeddings=[
            query_embedding
        ],

        n_results=top_k
    )

    documents = results["documents"][0]

    metadatas = results["metadatas"][0]

    output = []

    for doc, metadata in zip(
        documents,
        metadatas
    ):

        output.append({

            "text":
                doc,

            "source":
                metadata["source"],

            "start_page":
                metadata["start_page"],

            "end_page":
                metadata["end_page"]
        })

    return output


# ============================================================
# SUMMARIZER
# ============================================================

def summarize_text(text):

    prompt = f"""
You are a research document assistant.

Summarize the following document content.

Use ONLY the provided content.
Do not add outside information.

Document Content:

{text}

Provide:

1. Main idea
2. Important points
3. Key concepts
"""

    response = client.models.generate_content(

        model=MODEL_NAME,

        contents=prompt
    )

    return response.text


# ============================================================
# CALCULATOR
# ============================================================

def calculator(expression):

    allowed_chars = (
        "0123456789+-*/().% "
    )

    if not all(
        char in allowed_chars
        for char in expression
    ):

        return "Invalid mathematical expression."

    try:

        return eval(
            expression,
            {"__builtins__": {}},
            {}
        )

    except Exception:

        return "Could not calculate the expression."


# ============================================================
# TOOL SELECTION
# ============================================================

def llm_select_tool(query):

    prompt = f"""
You are a tool-selection system for an AI Research Document Assistant.

Available tools:

document_search
- Use for questions about the research document.

summarizer
- Use when the user explicitly asks for a summary.

calculator
- Use for mathematical calculations.

User Query:

{query}

Return ONLY one of these exact tool names:

document_search
summarizer
calculator
"""

    response = client.models.generate_content(

        model=MODEL_NAME,

        contents=prompt
    )

    tool = response.text.strip().lower()

    valid_tools = [
        "document_search",
        "summarizer",
        "calculator"
    ]

    if tool not in valid_tools:

        tool = "document_search"

    return tool


# ============================================================
# AGENT STATE
# ============================================================

class AgentState(TypedDict):

    query: str
    tool: str
    tool_result: str
    final_answer: str
    conversation_history: list


# ============================================================
# TOOL NODES
# ============================================================

def document_search_node(state):

    results = document_search(
        state["query"]
    )

    output = []

    for result in results:

        output.append({

            "source":
                result["source"],

            "start_page":
                result["start_page"],

            "end_page":
                result["end_page"],

            "text":
                result["text"]
        })

    return {

        "tool_result":

            json.dumps(
                output,
                indent=2
            )
    }


def summarizer_node(state):

    results = document_search(
        state["query"]
    )

    combined_text = "\n\n".join(

        result["text"]

        for result in results
    )

    summary = summarize_text(
        combined_text
    )

    sources = []

    for result in results:

        sources.append({

            "source":
                result["source"],

            "start_page":
                result["start_page"],

            "end_page":
                result["end_page"]
        })

    return {

        "tool_result":

            json.dumps({

                "summary":
                    summary,

                "sources":
                    sources

            })
    }


def calculator_node(state):

    query = state["query"]

    # Example:
    # "25% of 800"

    match = re.search(
        r"(\d+(?:\.\d+)?)\s*%\s*of\s*(\d+(?:\.\d+)?)",
        query,
        re.IGNORECASE
    )

    if match:

        percentage = float(
            match.group(1)
        )

        number = float(
            match.group(2)
        )

        result = (
            percentage / 100
        ) * number

    else:

        expression = re.sub(
            r"[^0-9+\-*/().% ]",
            "",
            query
        )

        result = calculator(
            expression
        )

    return {

        "tool_result":

            json.dumps({

                "expression":
                    query,

                "result":
                    result

            })
    }


# ============================================================
# SELECT TOOL
# ============================================================

def select_tool(state):

    return {

        "tool":

            llm_select_tool(
                state["query"]
            )
    }


# ============================================================
# RUN TOOL
# ============================================================

def run_selected_tool(state):

    tool = state["tool"]

    if tool == "document_search":

        return document_search_node(
            state
        )

    if tool == "summarizer":

        return summarizer_node(
            state
        )

    if tool == "calculator":

        return calculator_node(
            state
        )

    return {

        "tool_result":

            json.dumps({

                "error":
                    "Unknown tool."

            })
    }


# ============================================================
# FINAL ANSWER
# ============================================================

def final_answer_node(state):

    history = state.get(
        "conversation_history",
        []
    )

    history_text = ""

    for message in history:

        history_text += (

            f"User: {message['user']}\n"

            f"Assistant: {message['assistant']}\n\n"
        )

    prompt = f"""
You are an AI Research Document Assistant.

Previous Conversation:

{history_text}

Current Question:

{state["query"]}

Selected Tool:

{state["tool"]}

Tool Result:

{state["tool_result"]}

Instructions:

1. Use previous conversation for context.

2. Use the tool result to answer.

3. For document questions, use ONLY retrieved document information.

4. Do not invent facts.

5. Answer clearly and concisely.

6. Mention source pages when available.

7. Never invent page numbers or sources.
"""

    response = client.models.generate_content(

        model=MODEL_NAME,

        contents=prompt
    )

    return {

        "final_answer":
            response.text
    }


# ============================================================
# LANGGRAPH
# ============================================================

graph = StateGraph(
    AgentState
)

graph.add_node(
    "select_tool",
    select_tool
)

graph.add_node(
    "run_tool",
    run_selected_tool
)

graph.add_node(
    "final_answer",
    final_answer_node
)

graph.add_edge(
    START,
    "select_tool"
)

graph.add_edge(
    "select_tool",
    "run_tool"
)

graph.add_edge(
    "run_tool",
    "final_answer"
)

graph.add_edge(
    "final_answer",
    END
)

agent = graph.compile()


# ============================================================
# CHAT FUNCTION
# ============================================================

def chat_with_agent(
    query,
    conversation_history
):

    initial_state = {

        "query":
            query,

        "tool":
            "",

        "tool_result":
            "",

        "final_answer":
            "",

        "conversation_history":
            conversation_history.copy()
    }

    result = agent.invoke(
        initial_state
    )

    return (
        result["final_answer"],
        result
    )


# ============================================================
# READY
# ============================================================

print(
    f"Backend ready ✅ | "
    f"Indexed chunks: {chunk_count}"
)