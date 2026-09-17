

import streamlit as st
import json

from backend import chat_with_agent


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="AI Research & Document Assistant",
    page_icon="🤖",
    layout="wide"
)


# ============================================================
# TITLE
# ============================================================

st.title("🤖 AI Research & Document Assistant")

st.caption(
    "Agentic RAG system with document search, summarization, "
    "calculator, conversation memory, and source citations."
)


# ============================================================
# SESSION MEMORY
# ============================================================

if "conversation_history" not in st.session_state:

    st.session_state.conversation_history = []


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    st.header("🛠️ Available Tools")

    st.write("📚 Document Search")
    st.write("📝 Summarizer")
    st.write("🧮 Calculator")

    st.divider()

    st.subheader("🧠 Agent Features")

    st.write("✅ LLM-based tool selection")
    st.write("✅ Semantic retrieval")
    st.write("✅ Conversation memory")
    st.write("✅ Source/page tracking")
    st.write("✅ LangGraph workflow")

    st.divider()

    if st.button("🗑️ Clear Conversation"):

        st.session_state.conversation_history = []

        st.rerun()


# ============================================================
# DISPLAY CHAT HISTORY
# ============================================================

for message in st.session_state.conversation_history:

    with st.chat_message("user"):

        st.write(message["user"])

    with st.chat_message("assistant"):

        st.write(message["assistant"])


# ============================================================
# CHAT INPUT
# ============================================================

query = st.chat_input(
    "Ask something about your research document..."
)


# ============================================================
# PROCESS QUERY
# ============================================================

if query:

    # --------------------------------------------------------
    # Display user message
    # --------------------------------------------------------

    with st.chat_message("user"):

        st.write(query)


    # --------------------------------------------------------
    # Run Agent
    # --------------------------------------------------------

    with st.spinner("🤖 Agent is thinking..."):

        answer, result = chat_with_agent(

            query,

            st.session_state.conversation_history

        )


    # --------------------------------------------------------
    # Display Assistant Answer
    # --------------------------------------------------------

    with st.chat_message("assistant"):

        st.write(answer)


        # ----------------------------------------------------
        # Tool Used
        # ----------------------------------------------------

        selected_tool = result.get(
            "tool",
            ""
        )

        if selected_tool:

            st.caption(
                f"🔧 Tool used: `{selected_tool}`"
            )


        # ----------------------------------------------------
        # Sources
        # ----------------------------------------------------

        tool_result = result.get(
            "tool_result",
            ""
        )


        if selected_tool == "document_search":

            try:

                sources = json.loads(
                    tool_result
                )

                if sources:

                    st.markdown(
                        "### 📚 Sources"
                    )

                    for source in sources:

                        st.write(
                            f"📄 **{source['source']}** "
                            f"— Pages "
                            f"{source['start_page']}-"
                            f"{source['end_page']}"
                        )

            except Exception:

                pass


        elif selected_tool == "summarizer":

            try:

                summary_data = json.loads(
                    tool_result
                )

                sources = summary_data.get(
                    "sources",
                    []
                )

                if sources:

                    st.markdown(
                        "### 📚 Sources"
                    )

                    for source in sources:

                        st.write(
                            f"📄 **{source['source']}** "
                            f"— Pages "
                            f"{source['start_page']}-"
                            f"{source['end_page']}"
                        )

            except Exception:

                pass


    # ========================================================
    # SAVE CONVERSATION
    # ========================================================

    st.session_state.conversation_history.append(

        {
            "user":
                query,

            "assistant":
                answer
        }

    )