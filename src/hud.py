"""
HUD primitives: routing, formatting and status classes.

The cockpit navigates through the ``module`` query parameter rather than
Streamlit tabs, so every vector is a plain anchor and the browser's back button
works. These helpers are shared by the shell and by every module renderer.
"""

import pandas as pd
import streamlit as st
import streamlit.components.v1 as components
from textwrap import dedent

# Every navigable vector. "home" is the collapsed overview state.
VALID_MODULES = {
    "home",
    "brief",
    "horizon",
    "scenario",
    "treasury",
    "peers",
    "strategy",
    "news",
    "copilot",
}

DEFAULT_MODULE = "home"


def render_html(content):
    """Emit raw HTML, stripped of the indentation of its surrounding source."""
    st.html(dedent(content).strip())


def safe_float(value, default=0.0):
    if value is None or pd.isna(value):
        return default
    return float(value)


# ------------------------------------------------------------------
# Routing
# ------------------------------------------------------------------

def get_query_value(key, default=""):
    """Read one query-parameter value across Streamlit versions."""
    try:
        value = st.query_params.get(key, default)
    except AttributeError:
        value = st.experimental_get_query_params().get(key, [default])

    if isinstance(value, list):
        value = value[-1] if value else default

    return str(value) if value is not None else str(default)


def clear_query_value(key):
    """Consume a one-shot parameter so it does not re-fire on the next rerun."""
    try:
        if key in st.query_params:
            del st.query_params[key]
    except (AttributeError, KeyError):
        pass


def get_selected_module():
    """Return the module selected through the radial HUD."""
    selected = get_query_value("module", DEFAULT_MODULE).lower()

    if selected not in VALID_MODULES:
        return DEFAULT_MODULE

    return selected


def navigate_to_module(module):
    """Update radial navigation state across Streamlit versions."""
    if module not in VALID_MODULES:
        return

    try:
        st.query_params["module"] = module
    except AttributeError:
        st.experimental_set_query_params(module=module)

    st.rerun()


def module_url(module):
    """
    Build a vector's destination.

    Selecting a module scrolls to the output panel; going home returns to the
    top of the cockpit, where the snapshot and the dial live.
    """
    anchor = "command-bar" if module == "home" else "module-output"
    return f"?module={module}#{anchor}"


def investigate_url(topic):
    """One-click handoff from a decision lens into the Copilot."""
    return f"?module=copilot&investigate={topic}#module-output"


def active_class(module, selected_module):
    return "is-active" if selected_module == module else ""


# ------------------------------------------------------------------
# Entry gate
# ------------------------------------------------------------------

def has_entered():
    """
    True once the viewer has passed the greeting screen.

    A bare URL opens on the greeting; every in-cockpit link carries either
    ``module`` or the one-off ``enter`` flag, so navigating back with the
    browser button returns to the greeting rather than trapping the viewer.
    """
    return bool(get_query_value("module") or get_query_value("enter"))


def enter_url():
    """The greeting screen's way into the cockpit."""
    return "?enter=1"


# ------------------------------------------------------------------
# Scroll
# ------------------------------------------------------------------

def scroll_to_module_output():
    """
    Put the selected module under the viewer's eyes without a manual scroll.

    A ``#module-output`` fragment alone is unreliable here: Streamlit paints
    the module after the browser has already tried to honour the hash, so the
    jump lands on an element that does not exist yet. This retries from inside
    a zero-height component until the banner has actually rendered.

    The jump is then re-asserted for a short settling window. Streamlit runs
    scroll adjustments of its own after the module paints — the chat view
    scrolls itself to the bottom — which would otherwise leave the banner
    parked underneath the frozen command bar. ``scroll-margin-top`` on the
    target is what keeps it clear of that bar.
    """
    components.html(
        """
        <script>
        (function () {
            let attempts = 0;
            let settled = 0;

            function jump() {
                let target = null;
                try {
                    target = window.parent.document
                        .getElementById("module-output");
                } catch (err) {
                    // Parent DOM out of reach; the link's #module-output
                    // fragment is the fallback.
                    return;
                }

                if (target) {
                    target.scrollIntoView({behavior: "auto", block: "start"});
                    // Keep re-asserting briefly so a later scroll by Streamlit
                    // does not leave the banner behind the command bar.
                    if (settled++ < 24) {
                        window.setTimeout(jump, 60);
                    }
                    return;
                }

                if (attempts++ < 40) {
                    window.setTimeout(jump, 50);
                }
            }

            jump();
        })();
        </script>
        """,
        height=0,
    )


# ------------------------------------------------------------------
# Formatting
# ------------------------------------------------------------------

def arrow_delta(value, unit="pp"):
    """
    A signed movement with its direction.

    Capital ratios move in hundredths of a point, and one decimal renders a
    real move as "0.0". Small non-zero values get a second decimal so the
    arrow and the number never contradict each other.
    """
    arrow = "↑" if value > 0 else "↓" if value < 0 else "→"
    magnitude = abs(value)
    precision = 2 if 0 < magnitude < 0.1 else 1
    return f"{arrow} {magnitude:.{precision}f}{unit}"


def clip_ui_text(value, max_chars=62):
    """Trim copy to fit a fixed HUD slot without wrapping the layout."""
    text_value = str(value or "").strip()
    if len(text_value) <= max_chars:
        return text_value
    return text_value[: max_chars - 1].rstrip() + "…"


def format_eur_millions(value):
    return f"€{value:,.0f}m"


def format_eur_billions(value_m):
    """Render a EUR-millions figure in billions, as the KPI cards do."""
    return f"€{value_m / 1000:.1f}bn"


# ------------------------------------------------------------------
# Status classes
# ------------------------------------------------------------------

def status_class(status):
    if status == "ALERT":
        return "kpi-alert"
    if status == "WATCH":
        return "kpi-watch"
    return "kpi-track"


def alert_class(status):
    if status == "ALERT":
        return "alert-red"
    if status == "WATCH":
        return "alert-amber"
    return "alert-green"


def signal_class(status):
    if status == "ALERT":
        return "signal-alert"
    if status == "WATCH":
        return "signal-watch"
    return "signal-track"


def threshold_status(value, amber_threshold, red_threshold, lower_is_better=False):
    """
    Classify a metric as TRACK / WATCH / ALERT.

    ``lower_is_better`` marks metrics where a higher reading is the bad
    direction, such as cost-to-income or the Stage 3 ratio.
    """
    if lower_is_better:
        if value >= red_threshold:
            return "ALERT"
        if value >= amber_threshold:
            return "WATCH"
        return "TRACK"

    if value <= red_threshold:
        return "ALERT"
    if value <= amber_threshold:
        return "WATCH"
    return "TRACK"


# ------------------------------------------------------------------
# Inline SVG
# ------------------------------------------------------------------

def build_rate_sensitivity_svg(df, width=300, height=118):
    """
    A compact rate-sensitivity spark chart for the home HUD.

    Drawn as inline SVG rather than a chart object because it sits inside an
    HTML panel, where a Streamlit chart would break the card layout. Only pure
    rate shocks are plotted; scenarios that also move credit spreads would make
    the curve non-comparable.
    """
    empty = '<svg class="sensitivity-svg" viewBox="0 0 300 118"></svg>'

    if df is None or df.empty:
        return empty

    local = df.copy()
    for column in [
        "rate_shock_bps",
        "credit_spread_shock_bps",
        "economic_value_impact_m",
    ]:
        local[column] = pd.to_numeric(local[column], errors="coerce")

    local["credit_spread_shock_bps"] = local["credit_spread_shock_bps"].fillna(0.0)
    local = local[local["credit_spread_shock_bps"].abs() < 0.001]
    local = local.dropna(
        subset=["rate_shock_bps", "economic_value_impact_m"]
    ).sort_values("rate_shock_bps")

    if len(local) < 2:
        return empty

    x_values = local["rate_shock_bps"].astype(float).tolist()
    y_values = local["economic_value_impact_m"].astype(float).tolist()

    left, right, top, bottom = 24.0, width - 12.0, 12.0, height - 22.0
    x_min, x_max = min(x_values), max(x_values)
    y_min, y_max = min(y_values + [0.0]), max(y_values + [0.0])

    if x_max == x_min:
        x_max = x_min + 1.0
    if y_max == y_min:
        y_max = y_min + 1.0

    def sx(x):
        return left + (x - x_min) / (x_max - x_min) * (right - left)

    def sy(y):
        return bottom - (y - y_min) / (y_max - y_min) * (bottom - top)

    points = " ".join(f"{sx(x):.1f},{sy(y):.1f}" for x, y in zip(x_values, y_values))
    zero_y = sy(0.0)

    circles = []
    labels = []
    for x, y in zip(x_values, y_values):
        px, py = sx(x), sy(y)
        circles.append(
            f'<circle cx="{px:.1f}" cy="{py:.1f}" r="3.4" fill="#E6F5E9" '
            f'stroke="#13AC33" stroke-width="1.2" />'
        )
        labels.append(
            f'<text x="{px:.1f}" y="{height - 5:.1f}" text-anchor="middle" '
            f'fill="#476F51" font-size="8" '
            f'font-family="Cascadia Mono, Consolas, monospace">{x:+.0f}bp</text>'
        )

    return (
        f'<svg class="sensitivity-svg" viewBox="0 0 {width} {height}" role="img" '
        f'aria-label="Treasury economic-value sensitivity to pure rate shocks">'
        f'<line x1="{left}" y1="{zero_y:.1f}" x2="{right}" y2="{zero_y:.1f}" '
        f'stroke="#184523" stroke-width="1" stroke-dasharray="3 4" />'
        f'<line x1="{left}" y1="{top}" x2="{left}" y2="{bottom}" '
        f'stroke="#1B231D" stroke-width="1" />'
        f'<polyline points="{points}" fill="none" stroke="#13AC33" '
        f'stroke-width="2.2" filter="drop-shadow(0 0 4px rgba(19,172,51,0.35))" />'
        + "".join(circles)
        + "".join(labels)
        + "</svg>"
    )
