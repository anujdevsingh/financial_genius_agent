import subprocess
import sys

def install_dependencies():
    """Install all required dependencies for FinGenius AI."""
    subprocess.check_call([
        sys.executable, "-m", "pip", "install", "-r", "requirements.txt", "-q"
    ])
    print("All dependencies installed successfully!")

if __name__ == "__main__":
    install_dependencies()
