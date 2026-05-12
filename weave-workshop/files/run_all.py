#!/usr/bin/env python3
"""Demo script showing how to run the complete grace_ system.

This gives you eyes on your terminal system!
"""

import subprocess
import time
import sys
import os

def main():
    print("🚀 Starting grace_ system with web interface...")
    print()
    print("This will start:")
    print("1. loom.py - The background daemon")
    print("2. web.py - The web interface at http://localhost:5000")
    print()
    print("Open your browser to http://localhost:5000 for visual exploration!")
    print("Press Ctrl+C to stop everything.")
    print()

    # Start loom in background
    print("Starting loom daemon...")
    loom_process = subprocess.Popen([sys.executable, "loom.py"])
    
    # Give loom time to start
    time.sleep(2)
    
    # Start web server
    print("Starting web interface...")
    try:
        web_process = subprocess.Popen([sys.executable, "web.py"])
        web_process.wait()
    except KeyboardInterrupt:
        print("\nShutting down...")
    finally:
        # Clean up processes
        loom_process.terminate()
        web_process.terminate()
        loom_process.wait()
        web_process.wait()
        print("All systems shut down. Farewell, soul.")

if __name__ == "__main__":
    main()