"""
AI-Native CFO Morning Cockpit.

The shell: page setup, the stylesheet, the greeting gate, the hero, the
executive KPI strip, the radial command dial, the intelligence dock, and the
dispatch into whichever module the ``module`` query parameter selects.
Everything below the dispatch lives in ``src/modules``.
"""

import html

import streamlit as st

from src.cockpit_state import build_state
from src.extended_data_loader import datasets_available
from src.hud import (
    active_class,
    arrow_delta,
    build_rate_sensitivity_svg,
    enter_url,
    get_selected_module,
    has_entered,
    module_url,
    render_html,
    safe_float,
    scroll_to_module_output,
)
from src.hud_css import BASE_CSS, EXTENSIONS_CSS, LOCAL_CSS, PANELS_CSS
from src.modules import MODULE_METADATA, RENDERERS
from src.modules.copilot import consume_investigation_topic
from src.weather import get_local_weather

# The rail shown in place of the dial once a module is open: every vector,
# in the dial's own order, with the intelligence lenses after the four modules.
RAIL_MODULES = (
    ("brief", "Morning Brief"),
    ("horizon", "Horizon"),
    ("scenario", "What-If Engine"),
    ("copilot", "CFO Copilot"),
    ("treasury", "Treasury"),
    ("peers", "Peers"),
    ("strategy", "Strategy"),
    ("news", "News"),
)

st.set_page_config(
    page_title="A.R.C. | CFO Command",
    page_icon="◉",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# Emitted in cascade order; LOCAL_CSS last so this cockpit's overrides win.
for stylesheet in (BASE_CSS, EXTENSIONS_CSS, PANELS_CSS, LOCAL_CSS):
    render_html(stylesheet)

# The greeting stands alone: no state, no data load, one way forward.
if not has_entered():
    render_html(
        f"""
        <div class="cockpit-gate">
            <div class="gate-kicker">AI CFO Command Center</div>
            <h1 class="gate-greeting">Good morning <strong>Ferdinand</strong></h1>
            <a class="gate-orb" href="{enter_url()}" target="_self" aria-label="Start explore">
                <span class="core-orbit-html" aria-hidden="true"></span>
                <span class="core-reactor-html" aria-hidden="true"></span>
                <span class="core-scan-html" aria-hidden="true"></span>
                <span class="core-copy-html">
                    <span class="core-code-html">Enter cockpit</span>
                    <strong class="core-main-html">Start<br>Explore</strong>
                    <span class="core-online-html">Systems ready</span>
                </span>
            </a>
        </div>
        """
    )
    st.stop()

s = build_state()
selected_module = get_selected_module()
active_module_name, active_module_description = MODULE_METADATA[selected_module]

# One-click handoffs from a decision lens must arm the Copilot before it renders.
consume_investigation_topic(selected_module)

# Only a fresh selection scrolls; widget reruns inside a module must not yank
# the viewer back up to the banner.
arrived_at_module = st.session_state.get("last_rendered_module") != selected_module
st.session_state["last_rendered_module"] = selected_module


# ============================================================
# HERO
# ============================================================

home_href = module_url("home")
weather = get_local_weather()

if weather is None:
    weather_pill = ""
else:
    weather_place = html.escape(weather["place"])
    weather_label = html.escape(weather["label"])
    weather_range = (
        ""
        if weather["high_c"] is None or weather["low_c"] is None
        else f" · H {weather['high_c']:.0f}° L {weather['low_c']:.0f}°"
    )
    weather_pill = (
        f'<span class="data-pill weather-pill">'
        f'<span class="weather-glyph">{weather["glyph"]}</span>'
        f'{weather_place} / {weather["temperature_c"]:.0f}°C · '
        f'{weather_label}{weather_range}</span>'
    )

# One frozen line: the identity, the dates the cockpit is reading, and the
# local conditions. It stays pinned so the reporting basis is never scrolled
# out of view while a module is being read.
render_html(
    f"""
    <div class="hud-hero" id="command-bar">
        <a class="system-kicker hero-home-link" href="{home_href}" target="_self"
           aria-label="Back to the CFO overview">
            <span class="hero-home-glyph" aria-hidden="true">&#8962;</span>
            AI CFO COMMAND CENTER
        </a>
        <div class="hero-status-row">
            <span class="data-pill">Live data / {s.live_date}</span>
            <span class="data-pill">Close / {s.close_date}</span>
            <span class="data-pill">{s.executive_change_count} changes summarized</span>
            {weather_pill}
        </div>
    </div>
    """
)


# ============================================================
# EXECUTIVE SNAPSHOT — CURRENT + CHANGE + CONTEXT
# ============================================================

# The snapshot and the dial belong to the overview; opening a module goes
# straight to that module's own readout.
if selected_module == "home":
    # Rendered as one grid rather than four st.columns: the hover explanation has
    # to escape its own card, and a Streamlit column wrapper clips it.
    kpi_cards_html = "".join(
        f"""
        <div class="kpi-slot" tabindex="0">
            <div class="kpi-card" data-module="{card['code']}">
                <div class="kpi-label">{card['label']}</div>
                <div class="kpi-value">{card['value']}</div>
                <div class="executive-delta">{arrow_delta(card['delta_pp'])} vs {s.previous_month_label}</div>
                <div class="executive-context">{card['context']}</div>
                <span class="micro-line"></span>
                <span class="kpi-hint" aria-hidden="true">why · impact · next</span>
            </div>
            <div class="kpi-explain" role="tooltip">
                <div class="kpi-explain-head">{card['label']}</div>
                <div class="kpi-explain-row">
                    <span class="kpi-explain-tag">Why</span>
                    <p class="kpi-explain-copy">{card['why']}</p>
                </div>
                <div class="kpi-explain-row">
                    <span class="kpi-explain-tag">Impact</span>
                    <p class="kpi-explain-copy">{card['impact']}</p>
                </div>
                <div class="kpi-explain-row">
                    <span class="kpi-explain-tag">Next</span>
                    <p class="kpi-explain-copy">{card['next']}</p>
                </div>
                <a class="kpi-explain-link" href="{module_url(card['module'])}" target="_self">Open the full lens &rarr;</a>
            </div>
        </div>
        """
        for card in s.kpi_cards
    )

    render_html(f'<div class="kpi-row">{kpi_cards_html}</div>')


# ============================================================
# NAVIGATION — RADIAL COMMAND DIAL
# ============================================================

selection_class = "has-selection" if selected_module != "home" else ""


def dial(module):
    return active_class(module, selected_module)


if selected_module == "home":
    render_html(
        f"""
        <div class="integrated-system {selection_class}" id="radial-command">
            <div class="system-topline"><span></span><span><strong>CFO decision cockpit</strong> / live {s.live_date}</span><span></span></div>
            <div class="system-grid is-solo">
                <div class="dial-viewport">
                    <div class="command-dial-html" role="navigation" aria-label="Interactive CFO command dial">
                        <span class="dial-grid-disc-html" aria-hidden="true"></span><span class="dial-crosshair-html" aria-hidden="true"></span><span class="dial-tick-shell-html" aria-hidden="true"></span><span class="dial-rotor-html rotor-outer" aria-hidden="true"></span><span class="dial-rotor-html rotor-inner" aria-hidden="true"></span><span class="dial-annulus-bed-html" aria-hidden="true"></span>
                        <a class="css-sector css-sector-brief {dial('brief')}" href="{module_url('brief')}" target="_self" aria-label="Open Morning Brief" title="Morning Brief — click to open"><span class="dial-hit-copy">Morning Brief</span></a>
                        <a class="css-sector css-sector-horizon {dial('horizon')}" href="{module_url('horizon')}" target="_self" aria-label="Open Horizon" title="Horizon — click to open"><span class="dial-hit-copy">Horizon</span></a>
                        <a class="css-sector css-sector-scenario {dial('scenario')}" href="{module_url('scenario')}" target="_self" aria-label="Open What-If Engine" title="What-If Engine — click to open"><span class="dial-hit-copy">What-If Engine</span></a>
                        <span class="sector-label-html sector-label-brief {dial('brief')}"><strong class="sector-title-html">Morning Brief</strong><span class="sector-metric-html">NIM {s.cert_current_nim:.2f}% · {s.nim_mom_bps:+.1f} bps MoM</span><span class="sector-sub-html">Change · context · impact · next</span></span>
                        <span class="sector-label-html sector-label-horizon {dial('horizon')}"><strong class="sector-title-html">Horizon</strong><span class="sector-metric-html">{s.cert_nim_months}M actuals · latest {s.cert_current_nim:.2f}%</span><span class="sector-sub-html">Trend · run-rate · stress path</span></span>
                        <span class="sector-label-html sector-label-scenario {dial('scenario')}"><strong class="sector-title-html">What-If Engine</strong><span class="sector-metric-html">ECB ±100 bps · 365D max</span><span class="sector-sub-html">Simulate · quantify · compare</span></span>
                        <span class="dial-vector-line-html dial-vector-a" aria-hidden="true"></span><span class="dial-vector-line-html dial-vector-b" aria-hidden="true"></span><span class="dial-vector-line-html dial-vector-c" aria-hidden="true"></span><span class="dial-spoke-html dial-spoke-a" aria-hidden="true"></span><span class="dial-spoke-html dial-spoke-b" aria-hidden="true"></span><span class="dial-spoke-html dial-spoke-c" aria-hidden="true"></span>
                        <a class="css-core {dial('copilot')}" href="{module_url('copilot')}" target="_self" aria-label="Open CFO Copilot" title="Ask CFO Copilot — click to open"><span class="core-orbit-html" aria-hidden="true"></span><span class="core-reactor-html" aria-hidden="true"></span><span class="core-scan-html" aria-hidden="true"></span><span class="core-copy-html"><span class="core-code-html">AI / Investigate</span><strong class="core-main-html">Ask CFO<br>Copilot</strong><span class="core-online-html">Question → evidence</span><span class="core-hint-html">Select core to investigate</span></span></a>
                        <span class="dial-cardinal-html dial-cardinal-n" aria-hidden="true">N / 000</span><span class="dial-cardinal-html dial-cardinal-e" aria-hidden="true">E / 090</span><span class="dial-cardinal-html dial-cardinal-s" aria-hidden="true">S / 180</span><span class="dial-cardinal-html dial-cardinal-w" aria-hidden="true">W / 270</span>
                    </div>
                </div>

            </div>
            <div class="system-bottom-rail"><span>Current view / {active_module_name}</span><a class="system-reset {'is-home' if selected_module == 'home' else ''}" href="{module_url('home')}" target="_self">◎ Overview</a><span>Select a vector to investigate</span></div>
        </div>
        """
    )

    # ============================================================
    # INTELLIGENCE DOCK
    # ============================================================

    top_strategy_name = (
        html.escape(str(s.top_strategy["company_name"])) if s.top_strategy is not None else "—"
    )
    news_focus = (
        html.escape(str(s.geo_focus["country"])) if s.geo_focus is not None else "—"
    )

    render_html(
        f"""
        <div class="intelligence-dock">
            <div class="dock-kicker">Explore intelligence</div>
            <div class="dock-actions">
                <a class="dock-action {dial('strategy')}" href="{module_url('strategy')}" target="_self"><span class="dock-icon">◎</span><span class="dock-copy"><strong class="dock-title">Strategy</strong><span class="dock-metric">#1 {top_strategy_name} · why it ranks first</span></span></a>
                <a class="dock-action {dial('peers')}" href="{module_url('peers')}" target="_self"><span class="dock-icon">◌</span><span class="dock-copy"><strong class="dock-title">Peers</strong><span class="dock-metric">ROE proxy {s.roe_peer_gap_pp:+.1f}pp vs median · directional</span></span></a>
                <a class="dock-action {dial('treasury')}" href="{module_url('treasury')}" target="_self"><span class="dock-icon">△</span><span class="dock-copy"><strong class="dock-title">Treasury</strong><span class="dock-metric">+50bp impact {s.treasury_rate50_text} · evaluate hedge options</span></span></a>
                <a class="dock-action {dial('news')}" href="{module_url('news')}" target="_self"><span class="dock-icon">◇</span><span class="dock-copy"><strong class="dock-title">News</strong><span class="dock-metric">{news_focus} highest attention · {s.high_impact_news_count} high impact</span></span></a>
            </div>
        </div>
        """
    )

else:
    # In a module the dial is put away: the rail keeps every vector one click
    # away, and the command-bar title is the way back to the overview.
    rail_links = "".join(
        f'''<a class="rail-link {dial(code)}" href="{module_url(code)}" target="_self">{label}</a>'''
        for code, label in RAIL_MODULES
    )

    render_html(
        f'''
        <div class="module-rail">
            <a class="rail-home" href="{module_url('home')}" target="_self">&#9678; Overview</a>
            <nav class="rail-links" aria-label="Cockpit modules">{rail_links}</nav>
        </div>
        '''
    )


# ============================================================
# MODULE OUTPUT
# ============================================================

if selected_module == "home":
    render_html(
        """
        <div class="system-overview-note" id="module-output">
            <span class="overview-title">Today at a glance</span>
            <span class="overview-copy">Start with Morning Brief for changes, Horizon for the forward view, What-If for decisions under stress, or ask Copilot to investigate.</span>
        </div>
        """
    )

    overview_left, overview_right = st.columns([1, 1])
    with overview_left:
        render_html(
            f"""
            <div class="panel">
                <div class="readout-label">Rate sensitivity / treasury economic value</div>
                {build_rate_sensitivity_svg(s.treasury_scenarios)}
                <div class="copilot-evidence-note">
                    Pure parallel rate shocks only; scenarios that also move credit
                    spreads are excluded so the curve stays comparable.
                </div>
            </div>
            """
        )
    with overview_right:
        render_html(
            f"""
            <div class="panel">
                <div class="readout-label">Standing position</div>
                <div class="copilot-context-strip">
                    <div class="copilot-context-item"><span>NIM</span><strong>{s.cert_current_nim:.2f}%</strong></div>
                    <div class="copilot-context-item"><span>Loans</span><strong>€{s.current_loans_m / 1000:.1f}bn</strong></div>
                    <div class="copilot-context-item"><span>Deposits</span><strong>€{s.current_deposits_m / 1000:.1f}bn</strong></div>
                    <div class="copilot-context-item"><span>ECB</span><strong>{s.ecb_rate_pct:.2f}%</strong></div>
                </div>
                <div class="copilot-evidence-note">
                    Stage 2 {s.stage_2_share_pct:.1f}% · Stage 3 {s.stage_3_share_pct:.2f}% ·
                    {s.current_credit_watch_count} credit watch(es) on the latest observation.
                </div>
            </div>
            """
        )

else:
    render_html(
        f"""
        <div class="active-module-banner" id="module-output">
            <span class="active-module-name">{active_module_name}</span>
            <span class="active-module-state">{active_module_description}</span>
        </div>
        """
    )

    # A signal pushed here from the News module explains itself once.
    applied_signal = st.session_state.pop("scenario_from_signal", None)
    if applied_signal and selected_module == "scenario":
        st.info(f"Assumptions pre-filled from an overnight news signal: {applied_signal}.")

    RENDERERS[selected_module](s)

    if arrived_at_module:
        scroll_to_module_output()


# ============================================================
# SYSTEM FOOTER
# ============================================================

dataset_status = datasets_available()
missing_datasets = [name for name, ok in dataset_status.items() if not ok]

if missing_datasets:
    dataset_note = (
        f"{len(missing_datasets)} dataset(s) missing — run "
        "python -m src.generators.generate_all_data"
    )
else:
    dataset_note = f"{len(dataset_status)} datasets loaded"

render_html(
    f"""
    <div class="system-footer">
        <span>Synthetic data · illustrative only · not for financial decisions</span>
        <span>{dataset_note}</span>
        <span>Live data / {s.live_date} · close / {s.close_date}</span>
    </div>
    """
)
