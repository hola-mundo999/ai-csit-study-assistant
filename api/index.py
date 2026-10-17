import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

# Import the Streamlit app module
import app as streamlit_app

# Vercel expects app or handler
app = streamlit_app