"""Launch the BizSim server."""
import sys
import os

# Ensure the project root is on the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from server.app import start_app

if __name__ == "__main__":
    start_app()
