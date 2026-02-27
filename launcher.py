"""
Launcher for Tea Flavor Aggregator.
Starts Streamlit via its internal bootstrap API (no subprocess needed).
Works both as a plain script and as a PyInstaller bundle.
"""

import sys
import os


def get_base_path() -> str:
    """Return the directory where app.py and other sources live."""
    if getattr(sys, "frozen", False):
        # PyInstaller extracts everything to sys._MEIPASS
        return sys._MEIPASS
    return os.path.dirname(os.path.abspath(__file__))


def main():
    base = get_base_path()

    # Make sure our modules (app, scrapers, aggregator, taxonomy) are importable
    if base not in sys.path:
        sys.path.insert(0, base)

    app_path = os.path.join(base, "app.py")

    # Streamlit configuration via env vars (before importing streamlit)
    os.environ.setdefault("STREAMLIT_SERVER_PORT", "8501")
    os.environ.setdefault("STREAMLIT_SERVER_HEADLESS", "false")
    os.environ.setdefault("STREAMLIT_BROWSER_GATHER_USAGE_STATS", "false")
    os.environ.setdefault("STREAMLIT_SERVER_ENABLE_CORS", "false")

    # Use Streamlit's internal bootstrap — no subprocess required
    from streamlit.web import bootstrap
    bootstrap.run(app_path, "", [], {})


if __name__ == "__main__":
    main()
