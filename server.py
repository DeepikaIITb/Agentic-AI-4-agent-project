#!/usr/bin/env python3
"""Start the dashboard server: python server.py"""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))

import uvicorn

if __name__ == "__main__":
    print("\n🎓 Agentic Curriculum Dashboard")
    print("━" * 40)
    print("➜  Open in browser: http://localhost:8000")
    print("━" * 40 + "\n")
    uvicorn.run("api.app:app", host="0.0.0.0", port=8000, reload=False)
