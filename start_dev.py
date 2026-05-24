import subprocess
import os
import sys
import time

def start_services():
    # Get the root directory
    root_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Path to backend and frontend
    backend_dir = os.path.join(root_dir, "backend")
    frontend_dir = os.path.join(root_dir, "frontend")
    
    print("🚀 Starting Newsletter Herald Services...")

    # Start Backend (FastAPI) using the virtual environment if it exists
    print("📂 Starting Backend on http://localhost:8000")
    
    python_exe = "python"
    venv_exists = False
    if os.name == 'nt':
        venv_python = os.path.join(backend_dir, "venv", "Scripts", "python.exe")
        if os.path.exists(venv_python):
            python_exe = venv_python
            venv_exists = True
    else:
        venv_python = os.path.join(backend_dir, "venv", "bin", "python")
        if os.path.exists(venv_python):
            python_exe = venv_python
            venv_exists = True

    # Check if uvicorn is installed in the selected python environment
    try:
        subprocess.check_call([python_exe, "-m", "uvicorn", "--version"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("⚠️  Uvicorn not found in backend environment. Installing dependencies...")
        subprocess.check_call([python_exe, "-m", "pip", "install", "-r", os.path.join(backend_dir, "requirements.txt")])

    backend_process = subprocess.Popen(
        [python_exe, "-m", "uvicorn", "main:app", "--reload"],
        cwd=backend_dir,
        shell=True if os.name == 'nt' else False
    )

    # Give backend a moment to start
    time.sleep(2)

    # Start Frontend (Next.js)
    print("📂 Starting Frontend on http://localhost:3000")
    frontend_process = subprocess.Popen(
        ["npm", "run", "dev"],
        cwd=frontend_dir,
        shell=True if os.name == 'nt' else False
    )

    try:
        # Keep the script running while services are active
        while True:
            time.sleep(1)
            if backend_process.poll() is not None:
                print("❌ Backend process stopped.")
                break
            if frontend_process.poll() is not None:
                print("❌ Frontend process stopped.")
                break
    except KeyboardInterrupt:
        print("\n🛑 Stopping services...")
        backend_process.terminate()
        frontend_process.terminate()
        print("✅ Services stopped.")
        sys.exit(0)

if __name__ == "__main__":
    start_services()
