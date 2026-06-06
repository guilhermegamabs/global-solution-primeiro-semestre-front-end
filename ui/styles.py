import pathlib
import streamlit as st

_CSS_DIR = pathlib.Path(__file__).parent / "css"
_CSS_FILES = ["base.css", "layout.css", "badges.css", "cards.css"]


@st.cache_resource
def _loadCss() -> str:
    parts = [(_CSS_DIR / name).read_text(encoding="utf-8") for name in _CSS_FILES]
    return "<style>\n" + "\n".join(parts) + "\n</style>"


def injectStyles() -> None:
    st.markdown(_loadCss(), unsafe_allow_html=True)
