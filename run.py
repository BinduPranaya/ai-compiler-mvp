import os
import sys
import subprocess

def install_requirements():
    print("Checking dependencies...")
    try:
        import fastapi
        import uvicorn
        import pydantic
        import dotenv
        print("All dependencies are already installed.")
    except ImportError:
        print("Missing dependencies. Installing from requirements.txt...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
            print("Dependencies installed successfully.")
        except Exception as e:
            print(f"Error installing dependencies: {e}")
            sys.exit(1)

def ensure_outputs_dir():
    os.makedirs("outputs", exist_ok=True)
    # Write a default empty generated.json if not present
    generated_file = os.path.join("outputs", "generated.json")
    if not os.path.exists(generated_file):
        with open(generated_file, "w") as f:
            f.write("{}")

def main():
    install_requirements()
    ensure_outputs_dir()
    
    print("\nStarting AI Compiler MVP Server...")
    print("Frontend is served at: http://127.0.0.1:8000/static/index.html")
    print("API documentation is at: http://127.0.0.1:8000/docs\n")
    
    try:
        import uvicorn
        uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=True)
    except KeyboardInterrupt:
        print("\nShutting down AI Compiler server. Goodbye!")

if __name__ == "__main__":
    main()
