# ============================================
# Streamlit + Cloudflare Tunnel
# ============================================

import os
import time
import subprocess

print("1️⃣ Stopping old Streamlit and LocalTunnel...")

os.system("pkill -f streamlit || true")
os.system("pkill -f 'lt --port 8501' || true")
os.system("pkill -f cloudflared || true")

time.sleep(2)

print("2️⃣ Starting Streamlit...")

os.system(
    "streamlit run app.py "
    "--server.port 8501 "
    "--server.address 0.0.0.0 "
    "> /content/streamlit.log 2>&1 &"
)

time.sleep(5)

print("3️⃣ Checking Streamlit...")

os.system("cat /content/streamlit.log")

print("\n4️⃣ Installing Cloudflare Tunnel...")

if not os.path.exists("/content/cloudflared"):
    os.system(
        "wget -q "
        "https://github.com/cloudflare/cloudflared/releases/latest/download/"
        "cloudflared-linux-amd64 "
        "-O /content/cloudflared"
    )
    os.system("chmod +x /content/cloudflared")

print("5️⃣ Starting Cloudflare Tunnel...")

os.system(
    "nohup /content/cloudflared tunnel "
    "--url http://localhost:8501 "
    "--no-autoupdate "
    "> /content/cloudflared.log 2>&1 &"
)

time.sleep(8)

print("\n============================================")
print("🚀 YOUR STREAMLIT PUBLIC URL")
print("============================================\n")

os.system("grep -o 'https://[-a-zA-Z0-9]*\\.trycloudflare\\.com' /content/cloudflared.log | head -1")

print("\n============================================")
print("Open the https://....trycloudflare.com URL above")
print("============================================")