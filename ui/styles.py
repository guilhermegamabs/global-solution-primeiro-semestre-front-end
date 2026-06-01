import streamlit as st

_IGNIS_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');

:root {
    --ignis-bg:       oklch(0.10 0.000   0);
    --ignis-surface:  oklch(0.16 0.000   0);
    --ignis-border:   oklch(0.22 0.004 353);
    --ignis-brand:    oklch(0.62 0.220 353);
    --ignis-critical: oklch(0.55 0.230  22);
    --ignis-warning:  oklch(0.67 0.210  42);
    --ignis-caution:  oklch(0.75 0.170  75);
    --ignis-safe:     oklch(0.70 0.180 145);
    --ignis-ink:      oklch(0.93 0.005 353);
    --ignis-muted:    oklch(0.60 0.008 353);
    --ignis-faint:    oklch(0.40 0.005 353);
    --ignis-mono:     'JetBrains Mono', 'Courier New', monospace;
    --ignis-sans:     'Inter', system-ui, -apple-system, sans-serif;
    --ignis-radius:   6px;
}

[data-testid="stSidebar"] > div:first-child {
    background: oklch(0.12 0.000 0) !important;
    border-right: 1px solid var(--ignis-border);
}

.ignis-header {
    display: flex;
    align-items: center;
    gap: 10px;
    margin-bottom: 20px;
    padding-bottom: 16px;
    border-bottom: 1px solid var(--ignis-border);
}

.ignis-wordmark {
    font-family: var(--ignis-mono);
    font-size: 17px;
    font-weight: 700;
    color: var(--ignis-brand);
    letter-spacing: 0.12em;
}

.ignis-status-dot {
    width: 7px;
    height: 7px;
    border-radius: 50%;
    background: var(--ignis-safe);
    display: inline-block;
    animation: ignis-pulse-safe 2.5s ease-in-out infinite;
}

.ignis-status-dot--alert {
    width: 7px;
    height: 7px;
    border-radius: 50%;
    background: var(--ignis-critical);
    display: inline-block;
    animation: ignis-pulse-alert 1.2s ease-in-out infinite;
}

@keyframes ignis-pulse-safe {
    0%, 100% { opacity: 1; }
    50%       { opacity: 0.40; }
}

@keyframes ignis-pulse-alert {
    0%, 100% { opacity: 1; }
    50%       { opacity: 0.20; }
}

@media (prefers-reduced-motion: reduce) {
    .ignis-status-dot,
    .ignis-status-dot--alert {
        animation: none;
    }
}

.ignis-section-label {
    font-family: var(--ignis-mono);
    font-size: 10px;
    text-transform: uppercase;
    letter-spacing: 0.10em;
    color: var(--ignis-faint);
    margin: 0 0 10px;
    padding-bottom: 8px;
    border-bottom: 1px solid var(--ignis-border);
}

.ignis-empty {
    text-align: center;
    padding: 56px 20px;
}

.ignis-empty-icon {
    font-size: 32px;
    margin-bottom: 14px;
    opacity: 0.40;
    color: var(--ignis-safe);
}

.ignis-empty-title {
    font-family: var(--ignis-sans);
    font-size: 16px;
    font-weight: 600;
    color: var(--ignis-ink);
    margin-bottom: 8px;
}

.ignis-empty-body {
    font-family: var(--ignis-sans);
    font-size: 13px;
    color: var(--ignis-muted);
    max-width: 38ch;
    margin: 0 auto;
    line-height: 1.6;
    text-wrap: pretty;
}

[data-testid="stExpander"] summary {
    font-family: var(--ignis-mono) !important;
    font-size: 11px !important;
    letter-spacing: 0.05em !important;
    color: var(--ignis-muted) !important;
    text-transform: uppercase;
}
</style>
"""


def inject_styles() -> None:
    st.markdown(_IGNIS_CSS, unsafe_allow_html=True)
