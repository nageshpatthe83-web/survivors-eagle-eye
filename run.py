"""
Project Eagle Eye - 1-Click Platform Launcher
Team Survivors | Track 01 - Emerson | Code Apex Hackathon
"""

import os
import sys
import webbrowser
import threading
import time

def main():
    print("=" * 65)
    print("  PROJECT EAGLE EYE — AI Control Panel Quality Inspection")
    print("  CODE APEX Hackathon | Track 01 — Emerson")
    print("  Team: TEAM SURVIVORS")
    print("  Members: Nagesh Patthe (Lead), Abhijeet More, Shubham Yadav, Prathmesh Dandge")
    print("=" * 65)

    from backend.server import app, init_db
    from backend.generate_samples import run_generate_all

    print("\n[1/3] Initializing SQLite database...")
    init_db()

    print("[2/3] Verifying and generating synthetic industrial test assets...")
    run_generate_all()

    port = 5050
    url = f"http://localhost:{port}"

    def open_browser():
        time.sleep(1.2)
        print(f"\n[3/3] Opening Project Eagle Eye in your browser: {url}\n")
        try:
            webbrowser.open(url)
        except Exception:
            pass

    threading.Thread(target=open_browser, daemon=True).start()

    print(f"[*] Starting Eagle Eye Web Server on {url} (Ctrl+C to stop)...")
    app.run(host="0.0.0.0", port=port, debug=False)

if __name__ == "__main__":
    main()
