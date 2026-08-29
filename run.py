"""
AegisMesh — Single-Command Prototype Launcher
Run: python run.py
"""
import sys
import os
import webbrowser
import threading
import time

def open_browser():
    time.sleep(1.2)
    url = "http://127.0.0.1:8000"
    print(f"\n[+] Opening AegisMesh Cyber Dashboard in browser: {url}\n")
    webbrowser.open(url)

def main():
    print("=" * 72)
    print("  AEGISMESH — Secure Hybrid Datacenter & Cloud Security Decision Engine")
    print("  Cisco Virtual Internship 2026 Cyber Security Prototype")
    print("  MODE: SIMULATION MODE (Demonstration Telemetry)")
    print("=" * 72)
    print("  [•] API Documentation: http://127.0.0.1:8000/api/docs")
    print("  [•] Command Dashboard: http://127.0.0.1:8000/")
    print("=" * 72)

    # Launch browser in background thread
    threading.Thread(target=open_browser, daemon=True).start()

    import uvicorn
    uvicorn.run("backend.app.main:app", host="127.0.0.1", port=8000, reload=False, log_level="info")

if __name__ == "__main__":
    main()
