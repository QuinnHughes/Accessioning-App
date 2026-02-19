#!/usr/bin/env python3
"""
Launcher for Accessioning App
Starts the backend server and opens the browser
"""

import os
import sys
import time
import webbrowser
import subprocess
import traceback
from pathlib import Path

def main():
    try:
        # Get the directory where the executable is located
        if getattr(sys, 'frozen', False):
            # Running as compiled executable
            app_dir = Path(sys._MEIPASS)
            exe_dir = Path(sys.executable).parent
        else:
            # Running as script
            app_dir = Path(__file__).parent
            exe_dir = app_dir
        
        print("=" * 60)
        print("Accessioning App")
        print("=" * 60)
        print(f"Starting application...")
        print(f"App directory: {app_dir}")
        print(f"Executable directory: {exe_dir}")
        
        # Set environment variables
        os.environ['PYTHONPATH'] = str(app_dir / 'Backend')
        
        # Start uvicorn server
        port = 8000
        print(f"\nStarting backend server on port {port}...")
        
        # Add Backend to path and import
        backend_path = app_dir / 'Backend' if getattr(sys, 'frozen', False) else app_dir / 'Backend'
        sys.path.insert(0, str(backend_path))
        sys.path.insert(0, str(app_dir))
        
        print(f"Python path includes: {backend_path}")
        
        print("\n→ Make sure PostgreSQL is running with 'accessioning_app' database")
        print("  Default connection: postgresql://postgres:password@localhost:5432/accessioning_app")
        
        import uvicorn
        # Import main module from Backend
        import main
        app = main.app
        
        # Open browser after short delay
        def open_browser():
            time.sleep(2)
            url = f"http://localhost:{port}"
            print(f"\nOpening browser at {url}")
            webbrowser.open(url)
        
        import threading
        threading.Thread(target=open_browser, daemon=True).start()
        
        # Start server
        print("\n" + "=" * 60)
        print("Server starting... Press CTRL+C to stop")
        print("=" * 60 + "\n")
        uvicorn.run(app, host="127.0.0.1", port=port, log_level="info")
        
    except KeyboardInterrupt:
        print("\n\nShutting down gracefully...")
    except Exception as e:
        print("\n" + "=" * 60)
        print("ERROR: Application failed to start")
        print("=" * 60)
        print(f"\n{type(e).__name__}: {e}\n")
        print("Full traceback:")
        traceback.print_exc()
        print("\n" + "=" * 60)
        print("\nPress Enter to exit...")
        input()
        sys.exit(1)

if __name__ == "__main__":
    main()
