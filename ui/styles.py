# ============================================================
# ui/styles.py — CSS loader
# ============================================================

import os
import streamlit.components.v1 as components


def load_css():
    css_path = os.path.join(os.path.dirname(__file__), "..", "style.css")
    css_path = os.path.abspath(css_path)
    if not os.path.exists(css_path):
        return
    with open(css_path) as f:
        css = f.read()
    html = (
        "<link href='https://fonts.googleapis.com/css2?"
        "family=Inter:wght@300;400;500;600;700"
        "&family=JetBrains+Mono:wght@400;600"
        "&display=swap' rel='stylesheet'>"
        f"<style>{css}</style>"
    )
    components.html(html, height=0)
