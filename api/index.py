from streamlit.web.bootstrap import run
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

if __name__ == "__main__":
    run(str(Path(__file__).parent.parent / "app.py"), '', [], {})
