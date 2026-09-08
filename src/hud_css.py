"""
The HUD stylesheet.

Three cascading blocks lifted from the reference cockpit, emitted in order:

    BASE_CSS      design tokens, app shell, hero, KPI cards, dial, typography
    EXTENSIONS    certified-cockpit additions layered over the base
    PANELS_CSS    radial support panels, intelligence dock, news cards

They are data-independent, so they are kept verbatim rather than rewritten.
LOCAL_CSS holds this app's own overrides and is emitted last so it wins.
"""

BASE_CSS = """\n<style>

    :root {
        --void: #02070c;
        --void-soft: #06111a;
        --panel: rgba(5, 22, 33, 0.82);
        --panel-strong: rgba(6, 29, 43, 0.94);
        --line: rgba(80, 222, 255, 0.18);
        --line-strong: rgba(80, 222, 255, 0.42);
        --cyan: #52e7ff;
        --cyan-soft: #9af2ff;
        --blue: #3b82f6;
        --violet: #b88cff;
        --green: #42f5a7;
        --amber: #ffcb66;
        --red: #ff5d7a;
        --text: #e9fbff;
        --muted: #7fa6b5;
    }

    html, body, [class*="css"] {
        font-family: "Segoe UI", "Helvetica Neue", Arial, sans-serif;
    }

    .stApp {
        color: var(--text);
        background:
            radial-gradient(circle at 82% 4%, rgba(16, 121, 164, 0.18), transparent 28rem),
            radial-gradient(circle at 12% 35%, rgba(34, 86, 147, 0.10), transparent 34rem),
            linear-gradient(135deg, #02070c 0%, #04101a 48%, #02070c 100%);
    }

    .stApp::before {
        content: "";
        position: fixed;
        inset: 0;
        pointer-events: none;
        z-index: 0;
        opacity: 0.34;
        background-image:
            linear-gradient(rgba(82, 231, 255, 0.026) 1px, transparent 1px),
            linear-gradient(90deg, rgba(82, 231, 255, 0.026) 1px, transparent 1px);
        background-size: 44px 44px;
        mask-image: linear-gradient(to bottom, black, transparent 92%);
    }

    .stApp::after {
        content: "";
        position: fixed;
        inset: 0;
        pointer-events: none;
        z-index: 0;
        opacity: 0.11;
        background: repeating-linear-gradient(
            0deg,
            rgba(255,255,255,0.04) 0px,
            rgba(255,255,255,0.04) 1px,
            transparent 1px,
            transparent 4px
        );
    }

    header[data-testid="stHeader"] {
        background: linear-gradient(180deg, rgba(2, 7, 12, 0.96), rgba(2, 7, 12, 0));
    }

    [data-testid="stToolbar"] {
        right: 1.25rem;
    }

    .block-container {
        position: relative;
        z-index: 1;
        padding-top: 3.7rem !important;
        padding-bottom: 3rem !important;
        max-width: 1580px;
    }

    div[data-testid="stMainBlockContainer"],
    div[data-testid="stAppViewBlockContainer"] {
        padding-top: 3.7rem !important;
    }

    #MainMenu, footer {
        visibility: hidden;
    }

    hr {
        border-color: rgba(82, 231, 255, 0.12) !important;
    }

    [data-testid="stMarkdownContainer"] p,
    [data-testid="stMarkdownContainer"] li {
        color: #b8d4dc;
    }

    [data-testid="stMarkdownContainer"] h1,
    [data-testid="stMarkdownContainer"] h2,
    [data-testid="stMarkdownContainer"] h3,
    [data-testid="stMarkdownContainer"] h4 {
        color: #e9fbff;
        letter-spacing: -0.02em;
    }

    /* -------------------------------------------------
       HERO / COMMAND HEADER
       ------------------------------------------------- */

    .hud-hero {
        position: relative;
        min-height: 248px;
        display: grid;
        grid-template-columns: minmax(0, 1.55fr) minmax(260px, 0.7fr);
        align-items: center;
        gap: 2rem;
        overflow: hidden;
        padding: 2.1rem 2.35rem;
        margin: 0 0 1.3rem 0;
        background:
            linear-gradient(105deg, rgba(5, 27, 41, 0.94), rgba(3, 14, 23, 0.72)),
            radial-gradient(circle at 79% 50%, rgba(82, 231, 255, 0.15), transparent 13rem);
        border: 1px solid var(--line-strong);
        clip-path: polygon(0 0, calc(100% - 30px) 0, 100% 30px, 100% 100%, 30px 100%, 0 calc(100% - 30px));
        box-shadow:
            inset 0 0 55px rgba(42, 186, 230, 0.055),
            0 22px 70px rgba(0, 0, 0, 0.34);
    }

    .hud-hero::before {
        content: "";
        position: absolute;
        top: 0;
        left: -45%;
        width: 42%;
        height: 2px;
        background: linear-gradient(90deg, transparent, var(--cyan), transparent);
        box-shadow: 0 0 18px var(--cyan);
        animation: scan-horizontal 7s linear infinite;
    }

    .hud-hero::after {
        content: "";
        position: absolute;
        inset: 12px;
        pointer-events: none;
        opacity: 0.65;
        background:
            linear-gradient(var(--cyan), var(--cyan)) left top / 45px 1px no-repeat,
            linear-gradient(var(--cyan), var(--cyan)) left top / 1px 45px no-repeat,
            linear-gradient(var(--cyan), var(--cyan)) right bottom / 45px 1px no-repeat,
            linear-gradient(var(--cyan), var(--cyan)) right bottom / 1px 45px no-repeat;
    }

    .hero-copy, .hero-core {
        position: relative;
        z-index: 2;
    }

    .system-kicker,
    .module-code,
    .kpi-label,
    .scenario-summary-label,
    .readout-label {
        font-family: "Cascadia Mono", "SFMono-Regular", Consolas, monospace;
        text-transform: uppercase;
        letter-spacing: 0.16em;
    }

    .system-kicker {
        display: flex;
        align-items: center;
        gap: 0.65rem;
        color: var(--cyan);
        font-size: 0.70rem;
        font-weight: 700;
        margin-bottom: 0.8rem;
    }

    .system-kicker::before {
        content: "";
        width: 28px;
        height: 1px;
        background: var(--cyan);
        box-shadow: 0 0 10px var(--cyan);
    }

    .hero-title {
        margin: 0;
        color: #f2fdff;
        font-size: clamp(2.35rem, 4.5vw, 4.85rem);
        line-height: 0.94;
        font-weight: 300;
        letter-spacing: -0.055em;
        text-shadow: 0 0 34px rgba(82, 231, 255, 0.13);
    }

    .hero-title strong {
        color: var(--cyan);
        font-weight: 780;
        letter-spacing: 0.035em;
    }

    .hero-subtitle {
        max-width: 690px;
        margin-top: 1rem;
        color: #9bbdca;
        font-size: 0.96rem;
        line-height: 1.65;
    }

    .hero-status-row {
        display: flex;
        align-items: center;
        flex-wrap: wrap;
        gap: 0.6rem;
        margin-top: 1.35rem;
    }

    .status-pill, .data-pill {
        display: inline-flex;
        align-items: center;
        gap: 0.45rem;
        padding: 0.38rem 0.72rem;
        border: 1px solid rgba(82, 231, 255, 0.24);
        background: rgba(82, 231, 255, 0.055);
        color: #aeeffc;
        font-family: "Cascadia Mono", Consolas, monospace;
        font-size: 0.66rem;
        font-weight: 700;
        letter-spacing: 0.095em;
        text-transform: uppercase;
        clip-path: polygon(8px 0, 100% 0, 100% calc(100% - 8px), calc(100% - 8px) 100%, 0 100%, 0 8px);
    }

    .status-dot {
        width: 7px;
        height: 7px;
        border-radius: 50%;
        background: var(--green);
        box-shadow: 0 0 0 4px rgba(66, 245, 167, 0.10), 0 0 12px var(--green);
        animation: pulse-dot 1.9s ease-in-out infinite;
    }

    .hero-core {
        min-height: 190px;
        display: grid;
        place-items: center;
    }

    .arc-orb {
        position: relative;
        width: 176px;
        height: 176px;
        display: grid;
        place-items: center;
        border-radius: 50%;
        background:
            radial-gradient(circle, rgba(225, 252, 255, 0.98) 0 4%, var(--cyan) 5% 9%, rgba(82,231,255,0.17) 10% 24%, rgba(8,31,44,0.92) 25% 42%, transparent 43%),
            conic-gradient(from 25deg, transparent 0 8%, rgba(82,231,255,0.92) 9% 13%, transparent 14% 29%, rgba(82,231,255,0.42) 30% 33%, transparent 34% 61%, rgba(82,231,255,0.85) 62% 68%, transparent 69% 86%, rgba(82,231,255,0.42) 87% 90%, transparent 91%);
        border: 1px solid rgba(82, 231, 255, 0.55);
        box-shadow:
            0 0 24px rgba(82,231,255,0.40),
            0 0 80px rgba(44,171,215,0.20),
            inset 0 0 28px rgba(82,231,255,0.24);
        animation: orb-breathe 3.5s ease-in-out infinite;
    }

    .arc-orb::before,
    .arc-orb::after {
        content: "";
        position: absolute;
        border-radius: 50%;
    }

    .arc-orb::before {
        inset: -13px;
        border: 1px dashed rgba(82, 231, 255, 0.42);
        animation: rotate-cw 18s linear infinite;
    }

    .arc-orb::after {
        inset: 20px;
        border: 1px solid rgba(185, 244, 255, 0.34);
        border-left-color: transparent;
        border-right-color: transparent;
        animation: rotate-ccw 7s linear infinite;
    }

    .orb-readout {
        position: relative;
        z-index: 2;
        text-align: center;
        color: #eaffff;
        text-shadow: 0 0 12px var(--cyan);
    }

    .orb-number {
        display: block;
        font-family: "Cascadia Mono", Consolas, monospace;
        font-size: 1.75rem;
        font-weight: 750;
        line-height: 1;
    }

    .orb-label {
        display: block;
        margin-top: 0.35rem;
        color: var(--cyan-soft);
        font-family: "Cascadia Mono", Consolas, monospace;
        font-size: 0.51rem;
        letter-spacing: 0.14em;
        text-transform: uppercase;
    }

    /* -------------------------------------------------
       SECTION AND MODULE LANGUAGE
       ------------------------------------------------- */

    .section-heading {
        display: flex;
        align-items: flex-end;
        justify-content: space-between;
        gap: 1rem;
        margin: 1.1rem 0 1rem 0;
    }

    .section-title {
        display: flex;
        align-items: center;
        gap: 0.7rem;
        margin: 0 0 0.8rem 0;
        color: #e8fbff;
        font-size: 1.12rem;
        font-weight: 650;
        letter-spacing: 0.01em;
    }

    .section-title::before {
        content: "";
        width: 10px;
        height: 10px;
        background: var(--cyan);
        clip-path: polygon(50% 0, 100% 50%, 50% 100%, 0 50%);
        box-shadow: 0 0 14px var(--cyan);
    }

    .section-subtitle {
        max-width: 760px;
        color: var(--muted);
        font-size: 0.88rem;
        line-height: 1.55;
        margin: -0.25rem 0 1.2rem 0;
    }

    .module-code {
        color: var(--cyan);
        font-size: 0.61rem;
        font-weight: 750;
    }

    .attention-line {
        display: flex;
        justify-content: space-between;
        align-items: center;
        gap: 1rem;
        padding: 0.2rem 0 0.45rem 0;
    }

    .attention-copy {
        color: #cce8ef;
        font-size: 1.05rem;
    }

    .attention-copy strong {
        color: var(--cyan);
        font-size: 1.35rem;
        text-shadow: 0 0 15px rgba(82, 231, 255, 0.35);
    }

    .sync-copy {
        color: #547b8b;
        font-family: "Cascadia Mono", Consolas, monospace;
        font-size: 0.63rem;
        letter-spacing: 0.09em;
        text-transform: uppercase;
    }

    /* -------------------------------------------------
       KPI MODULES
       ------------------------------------------------- */

    .kpi-card {
        position: relative;
        min-height: 166px;
        overflow: hidden;
        padding: 1.25rem 1.35rem 1.15rem;
        background:
            linear-gradient(145deg, rgba(8, 34, 49, 0.94), rgba(3, 17, 27, 0.90)),
            radial-gradient(circle at 100% 0%, rgba(82,231,255,0.12), transparent 45%);
        border: 1px solid rgba(82, 231, 255, 0.20);
        clip-path: polygon(0 0, calc(100% - 20px) 0, 100% 20px, 100% 100%, 13px 100%, 0 calc(100% - 13px));
        box-shadow: inset 0 0 32px rgba(47, 201, 244, 0.025);
        transition: transform 180ms ease, border-color 180ms ease, background 180ms ease;
    }

    .kpi-card:hover {
        transform: translateY(-3px);
        border-color: rgba(82, 231, 255, 0.48);
        background:
            linear-gradient(145deg, rgba(9, 39, 56, 0.98), rgba(3, 18, 29, 0.94)),
            radial-gradient(circle at 100% 0%, rgba(82,231,255,0.17), transparent 48%);
    }

    .kpi-card::before {
        content: "";
        position: absolute;
        left: 0;
        top: 0;
        width: 34%;
        height: 2px;
        background: linear-gradient(90deg, var(--cyan), transparent);
        box-shadow: 0 0 12px rgba(82,231,255,0.55);
    }

    .kpi-card::after {
        content: attr(data-module);
        position: absolute;
        top: 0.86rem;
        right: 1rem;
        color: rgba(134, 205, 222, 0.30);
        font-family: "Cascadia Mono", Consolas, monospace;
        font-size: 0.54rem;
        letter-spacing: 0.14em;
    }

    .kpi-card:has(.kpi-alert)::before {
        background: linear-gradient(90deg, var(--red), transparent);
        box-shadow: 0 0 12px rgba(255,93,122,0.55);
    }

    .kpi-card:has(.kpi-watch)::before {
        background: linear-gradient(90deg, var(--amber), transparent);
        box-shadow: 0 0 12px rgba(255,203,102,0.50);
    }

    .kpi-card:has(.kpi-track)::before {
        background: linear-gradient(90deg, var(--green), transparent);
        box-shadow: 0 0 12px rgba(66,245,167,0.46);
    }

    .kpi-label {
        color: #78a4b4;
        font-size: 0.65rem;
        font-weight: 750;
        margin-bottom: 0.65rem;
    }

    .kpi-value {
        color: #f0fdff;
        font-family: "Cascadia Mono", "Segoe UI", monospace;
        font-size: clamp(1.85rem, 3vw, 2.65rem);
        font-weight: 560;
        line-height: 1.08;
        letter-spacing: -0.055em;
        text-shadow: 0 0 24px rgba(82,231,255,0.16);
    }

    .kpi-alert, .kpi-watch, .kpi-track {
        display: flex;
        align-items: center;
        gap: 0.45rem;
        margin-top: 0.78rem;
        font-family: "Cascadia Mono", Consolas, monospace;
        font-size: 0.72rem;
        font-weight: 700;
        letter-spacing: 0.015em;
    }

    .kpi-alert { color: var(--red); }
    .kpi-watch { color: var(--amber); }
    .kpi-track { color: var(--green); }

    .micro-line {
        position: absolute;
        right: 1.2rem;
        bottom: 1.15rem;
        width: 54px;
        height: 18px;
        opacity: 0.52;
        background: linear-gradient(155deg, transparent 0 15%, var(--cyan) 16% 19%, transparent 20% 34%, var(--cyan) 35% 39%, transparent 40% 51%, var(--cyan) 52% 56%, transparent 57% 70%, var(--cyan) 71% 75%, transparent 76%);
        clip-path: polygon(0 83%, 18% 58%, 33% 70%, 52% 20%, 68% 43%, 83% 8%, 100% 28%, 100% 100%, 0 100%);
        filter: drop-shadow(0 0 5px var(--cyan));
    }

    /* -------------------------------------------------
       PANELS / BRIEFINGS
       ------------------------------------------------- */

    .panel, .scenario-panel {
        position: relative;
        overflow: hidden;
        padding: 1.2rem 1.3rem;
        color: #c9e1e8;
        background: linear-gradient(145deg, rgba(7, 29, 42, 0.88), rgba(3, 17, 26, 0.82));
        border: 1px solid rgba(82, 231, 255, 0.17);
        clip-path: polygon(0 0, calc(100% - 15px) 0, 100% 15px, 100% 100%, 0 100%);
    }

    .panel::after, .scenario-panel::after {
        content: "";
        position: absolute;
        right: 0;
        top: 0;
        width: 38px;
        height: 1px;
        background: var(--cyan);
        box-shadow: 0 0 10px var(--cyan);
    }

    .scenario-panel {
        margin-top: 1rem;
        background:
            linear-gradient(145deg, rgba(8, 37, 53, 0.90), rgba(4, 19, 30, 0.88)),
            radial-gradient(circle at 92% 15%, rgba(82,231,255,0.11), transparent 45%);
    }

    .scenario-title {
        color: #e7fbff;
        font-size: 0.96rem;
        font-weight: 680;
        letter-spacing: 0.015em;
        margin-bottom: 0.45rem;
    }

    .scenario-description {
        color: #83a9b7;
        font-size: 0.84rem;
        line-height: 1.55;
    }

    .scenario-badge {
        display: inline-flex;
        align-items: center;
        margin-top: 0.85rem;
        padding: 0.28rem 0.58rem;
        color: var(--cyan-soft);
        background: rgba(82, 231, 255, 0.06);
        border: 1px solid rgba(82, 231, 255, 0.25);
        font-family: "Cascadia Mono", Consolas, monospace;
        font-size: 0.58rem;
        font-weight: 750;
        letter-spacing: 0.12em;
        clip-path: polygon(6px 0, 100% 0, 100% calc(100% - 6px), calc(100% - 6px) 100%, 0 100%, 0 6px);
    }

    .alert-card {
        position: relative;
        min-height: 94px;
        padding: 1rem 1rem 0.95rem 3.65rem;
        margin-bottom: 0.72rem;
        background: linear-gradient(100deg, rgba(8, 31, 44, 0.92), rgba(4, 17, 27, 0.78));
        border: 1px solid rgba(120, 204, 223, 0.13);
        border-left: 2px solid;
        clip-path: polygon(0 0, calc(100% - 12px) 0, 100% 12px, 100% 100%, 0 100%);
    }

    .alert-card::before {
        content: attr(data-index);
        position: absolute;
        left: 1rem;
        top: 1rem;
        width: 1.8rem;
        height: 1.8rem;
        display: grid;
        place-items: center;
        border: 1px solid currentColor;
        font-family: "Cascadia Mono", Consolas, monospace;
        font-size: 0.66rem;
        clip-path: polygon(50% 0, 100% 28%, 100% 72%, 50% 100%, 0 72%, 0 28%);
    }

    .alert-red { border-left-color: var(--red); color: var(--red); }
    .alert-amber { border-left-color: var(--amber); color: var(--amber); }
    .alert-green { border-left-color: var(--green); color: var(--green); }

    .alert-title {
        color: #e7f8fb;
        font-size: 0.87rem;
        font-weight: 680;
        margin-bottom: 0.3rem;
    }

    .alert-text {
        color: #83a8b5;
        font-size: 0.81rem;
        line-height: 1.45;
    }

    .scenario-summary {
        display: grid;
        grid-template-columns: repeat(3, 1fr);
        gap: 0.65rem;
        margin-top: 1rem;
    }

    .scenario-summary-item {
        position: relative;
        padding: 0.78rem 0.82rem;
        background: rgba(82, 231, 255, 0.035);
        border: 1px solid rgba(82, 231, 255, 0.13);
    }

    .scenario-summary-item::before {
        content: "";
        position: absolute;
        left: 0;
        top: 0;
        width: 14px;
        height: 1px;
        background: var(--cyan);
    }

    .scenario-summary-label {
        color: #648d9c;
        font-size: 0.56rem;
        font-weight: 700;
    }

    .scenario-summary-value {
        margin-top: 0.32rem;
        color: #e6faff;
        font-family: "Cascadia Mono", Consolas, monospace;
        font-size: 0.95rem;
        font-weight: 650;
    }

    .horizon-grid {
        display: grid;
        gap: 0.82rem;
    }

    .horizon-readout {
        display: flex;
        align-items: flex-end;
        justify-content: space-between;
        gap: 0.5rem;
        padding-bottom: 0.78rem;
        border-bottom: 1px solid rgba(82,231,255,0.10);
    }

    .horizon-readout:last-child {
        padding-bottom: 0;
        border-bottom: 0;
    }

    .nim-legend {
        display: flex;
        align-items: center;
        flex-wrap: wrap;
        gap: 1.45rem;
        margin: 0.15rem 0 0.8rem 0;
        color: #779eac;
        font-family: "Cascadia Mono", Consolas, monospace;
        font-size: 0.64rem;
        font-weight: 650;
        letter-spacing: 0.075em;
        text-transform: uppercase;
    }

    .legend-item {
        display: flex;
        align-items: center;
        gap: 0.48rem;
    }

    .legend-dot {
        width: 8px;
        height: 8px;
        display: inline-block;
        border-radius: 50%;
    }

    .legend-line {
        width: 25px;
        display: inline-block;
        border-top: 2px dashed;
    }

    .legend-actual {
        background: #52e7ff;
        box-shadow: 0 0 8px rgba(82,231,255,0.75);
    }

    .legend-budget { border-color: #577c8a; }
    .legend-forecast { border-color: #b88cff; }

    .diagnostic-grid {
        display: grid;
        grid-template-columns: repeat(4, minmax(0, 1fr));
        gap: 0.7rem;
        padding: 0.25rem 0.2rem;
    }

    .diagnostic-item {
        display: flex;
        align-items: center;
        gap: 0.75rem;
        min-width: 0;
        padding: 0.75rem;
        background: rgba(82,231,255,0.025);
        border: 1px solid rgba(82,231,255,0.09);
    }

    .diagnostic-value {
        overflow: hidden;
        margin-top: 0.18rem;
        color: #c8e5eb;
        font-family: "Cascadia Mono", Consolas, monospace;
        font-size: 0.67rem;
        text-overflow: ellipsis;
        white-space: nowrap;
    }

    .readout-label {
        color: #608997;
        font-size: 0.57rem;
        font-weight: 700;
    }

    .readout-value {
        color: #eaffff;
        font-family: "Cascadia Mono", Consolas, monospace;
        font-size: 1.18rem;
        font-weight: 600;
    }

    /* -------------------------------------------------
       STREAMLIT-SAFE INTEGRATED COMMAND SYSTEM
       ------------------------------------------------- */

    .integrated-system {
        position: relative;
        max-width: 1450px;
        overflow: hidden;
        margin: 1.25rem auto 1.5rem;
        padding: 1rem 1.1rem 0.8rem;
        background:
            radial-gradient(circle at 50% 49%, rgba(0, 157, 220, 0.12), transparent 31rem),
            linear-gradient(135deg, rgba(2, 13, 21, 0.94), rgba(3, 20, 30, 0.78));
        border: 1px solid rgba(41, 191, 236, 0.18);
        clip-path: polygon(0 0, calc(100% - 22px) 0, 100% 22px, 100% 100%, 22px 100%, 0 calc(100% - 22px));
        box-shadow: inset 0 0 70px rgba(0, 139, 190, 0.035), 0 24px 70px rgba(0,0,0,0.30);
    }

    .integrated-system::before {
        content: "";
        position: absolute;
        inset: 0;
        z-index: 0;
        pointer-events: none;
        opacity: 0.28;
        background-image:
            linear-gradient(rgba(35, 182, 225, 0.035) 1px, transparent 1px),
            linear-gradient(90deg, rgba(35, 182, 225, 0.035) 1px, transparent 1px);
        background-size: 24px 24px;
        mask-image: radial-gradient(circle at 50% 50%, black 0 43%, transparent 78%);
    }

    .integrated-system::after {
        content: "";
        position: absolute;
        top: 0;
        left: -35%;
        z-index: 1;
        width: 30%;
        height: 1px;
        pointer-events: none;
        background: linear-gradient(90deg, transparent, #52e7ff, transparent);
        box-shadow: 0 0 15px rgba(82,231,255,0.8);
        animation: system-scan 8s linear infinite;
    }

    .system-topline {
        position: relative;
        z-index: 4;
        display: grid;
        grid-template-columns: 1fr auto 1fr;
        align-items: center;
        gap: 1rem;
        padding: 0.15rem 0.25rem 0.65rem;
        color: #4a7483;
        font-family: "Cascadia Mono", Consolas, monospace;
        font-size: 0.54rem;
        font-weight: 700;
        letter-spacing: 0.12em;
        text-transform: uppercase;
    }

    .system-topline::before,
    .system-topline::after {
        content: "";
        height: 1px;
        background: linear-gradient(90deg, transparent, rgba(82,231,255,0.26));
    }

    .system-topline::after {
        background: linear-gradient(90deg, rgba(82,231,255,0.26), transparent);
    }

    .system-topline strong {
        color: #71dff3;
        font-weight: 750;
    }

    .system-grid {
        position: relative;
        z-index: 3;
        display: grid;
        grid-template-columns: minmax(255px, 0.78fr) minmax(590px, 1.72fr) minmax(275px, 0.84fr);
        align-items: center;
        gap: 1rem;
        min-height: 650px;
    }

    .dial-viewport {
        position: relative;
        z-index: 3;
        min-width: 0;
    }

    .dial-viewport::before {
        content: "";
        position: absolute;
        left: 50%;
        top: 50%;
        width: 74%;
        aspect-ratio: 1;
        transform: translate(-50%, -50%);
        border-radius: 50%;
        background: radial-gradient(circle, rgba(44,200,239,0.08), transparent 68%);
        filter: blur(12px);
        pointer-events: none;
    }

    .command-dial-html {
        position: relative;
        isolation: isolate;
        z-index: 2;
        width: min(100%, 680px);
        aspect-ratio: 1;
        margin: 0 auto;
        filter: drop-shadow(0 0 26px rgba(20, 158, 203, 0.11));
    }

    .command-dial-html::before {
        content: "";
        position: absolute;
        inset: 1.5%;
        z-index: 0;
        border: 1px solid rgba(82,231,255,0.18);
        border-radius: 50%;
        background:
            radial-gradient(circle, transparent 0 67%, rgba(20,152,196,0.035) 67.4% 68%, transparent 68.4%),
            radial-gradient(circle, rgba(23,168,211,0.08), transparent 69%);
        box-shadow:
            0 0 0 9px rgba(82,231,255,0.014),
            inset 0 0 48px rgba(20,171,217,0.055),
            0 0 48px rgba(20,171,217,0.05);
        pointer-events: none;
    }

    .command-dial-html::after {
        content: "";
        position: absolute;
        inset: 4.3%;
        z-index: 1;
        border: 1px dashed rgba(82,231,255,0.16);
        border-radius: 50%;
        pointer-events: none;
    }

    .dial-grid-disc-html {
        position: absolute;
        inset: 6.5%;
        z-index: 0;
        overflow: hidden;
        border: 1px solid rgba(82,231,255,0.08);
        border-radius: 50%;
        background:
            linear-gradient(rgba(82,231,255,0.035) 1px, transparent 1px),
            linear-gradient(90deg, rgba(82,231,255,0.035) 1px, transparent 1px),
            radial-gradient(circle, rgba(6,45,61,0.42), rgba(2,15,24,0.12) 61%, transparent 72%);
        background-size: 18px 18px, 18px 18px, auto;
        box-shadow: inset 0 0 72px rgba(0,0,0,0.62);
        pointer-events: none;
    }

    .dial-grid-disc-html::before,
    .dial-grid-disc-html::after {
        content: "";
        position: absolute;
        border-radius: 50%;
        pointer-events: none;
    }

    .dial-grid-disc-html::before {
        inset: 11%;
        border: 1px solid rgba(82,231,255,0.09);
        box-shadow:
            0 0 0 18px rgba(82,231,255,0.012),
            0 0 0 19px rgba(82,231,255,0.045),
            0 0 0 58px rgba(82,231,255,0.009),
            0 0 0 59px rgba(82,231,255,0.035);
    }

    .dial-grid-disc-html::after {
        inset: 26%;
        border: 1px dashed rgba(82,231,255,0.12);
    }

    .dial-crosshair-html {
        position: absolute;
        inset: 6%;
        z-index: 1;
        border-radius: 50%;
        pointer-events: none;
    }

    .dial-crosshair-html::before,
    .dial-crosshair-html::after {
        content: "";
        position: absolute;
        left: 50%;
        top: 50%;
        opacity: 0.42;
        background: repeating-linear-gradient(
            90deg,
            rgba(82,231,255,0.16) 0 3px,
            transparent 3px 10px
        );
        transform: translate(-50%, -50%);
    }

    .dial-crosshair-html::before {
        width: 100%;
        height: 1px;
    }

    .dial-crosshair-html::after {
        width: 100%;
        height: 1px;
        transform: translate(-50%, -50%) rotate(90deg);
    }

    .dial-tick-shell-html,
    .dial-rotor-html,
    .dial-annulus-bed-html {
        position: absolute;
        border-radius: 50%;
        pointer-events: none;
    }

    .dial-tick-shell-html {
        inset: 2.4%;
        z-index: 3;
        opacity: 0.70;
        background: repeating-conic-gradient(
            from -0.5deg,
            rgba(91,231,255,0.72) 0deg 0.45deg,
            transparent 0.45deg 3deg
        );
        -webkit-mask: radial-gradient(circle, transparent 0 95.1%, #000 95.3% 97.6%, transparent 97.8%);
        mask: radial-gradient(circle, transparent 0 95.1%, #000 95.3% 97.6%, transparent 97.8%);
        animation: rotate-cw 95s linear infinite;
    }

    .dial-rotor-html {
        z-index: 4;
        background: conic-gradient(
            from 6deg,
            transparent 0 8deg,
            rgba(82,231,255,0.90) 8deg 39deg,
            transparent 39deg 119deg,
            rgba(88,201,255,0.72) 119deg 157deg,
            transparent 157deg 238deg,
            rgba(184,140,255,0.72) 238deg 268deg,
            transparent 268deg 360deg
        );
        -webkit-mask: radial-gradient(circle, transparent 0 96.1%, #000 96.3% 98.4%, transparent 98.6%);
        mask: radial-gradient(circle, transparent 0 96.1%, #000 96.3% 98.4%, transparent 98.6%);
    }

    .dial-rotor-html.rotor-outer {
        inset: 0.8%;
        animation: rotate-cw 42s linear infinite;
    }

    .dial-rotor-html.rotor-inner {
        inset: 8.7%;
        opacity: 0.48;
        animation: rotate-ccw 31s linear infinite;
    }

    .dial-annulus-bed-html {
        inset: 7.2%;
        z-index: 5;
        background:
            repeating-conic-gradient(
                from -1deg,
                rgba(88,219,248,0.055) 0deg 1deg,
                transparent 1deg 6deg
            ),
            conic-gradient(
                from -30deg,
                rgba(4,43,58,0.96),
                rgba(6,63,82,0.76) 33.1%,
                rgba(4,38,58,0.94) 33.4%,
                rgba(18,48,76,0.86) 66.3%,
                rgba(5,37,54,0.94) 66.6%,
                rgba(7,60,75,0.88)
            );
        -webkit-mask: radial-gradient(circle, transparent 0 57.7%, #000 58.1% 98.2%, transparent 98.6%);
        mask: radial-gradient(circle, transparent 0 57.7%, #000 58.1% 98.2%, transparent 98.6%);
        box-shadow: 0 0 34px rgba(31,189,229,0.05);
    }

    .css-sector {
        position: absolute;
        inset: 7.2%;
        z-index: 8;
        border-radius: 50%;
        outline: none;
        opacity: 0.92;
        background:
            repeating-radial-gradient(
                circle,
                transparent 0 16px,
                rgba(113,225,248,0.065) 17px,
                transparent 18px 27px
            ),
            linear-gradient(145deg, rgba(14,126,157,0.94), rgba(4,30,44,0.98));
        -webkit-mask: radial-gradient(circle, transparent 0 57.7%, #000 58.1% 98.2%, transparent 98.6%);
        mask: radial-gradient(circle, transparent 0 57.7%, #000 58.1% 98.2%, transparent 98.6%);
        transform-origin: center;
        transition:
            transform 220ms cubic-bezier(.2,.8,.2,1),
            opacity 190ms ease,
            filter 190ms ease;
    }

    .dial-hit-copy {
        position: absolute;
        width: 1px;
        height: 1px;
        overflow: hidden;
        clip: rect(0 0 0 0);
        clip-path: inset(50%);
        white-space: nowrap;
    }

    .css-sector::before {
        content: "";
        position: absolute;
        inset: 0;
        border-radius: 50%;
        opacity: 0.54;
        background: repeating-conic-gradient(
            from -1deg,
            rgba(140,239,255,0.30) 0deg 0.35deg,
            transparent 0.35deg 4.5deg
        );
        -webkit-mask: radial-gradient(circle, transparent 0 90.5%, #000 90.8% 93%, transparent 93.3%);
        mask: radial-gradient(circle, transparent 0 90.5%, #000 90.8% 93%, transparent 93.3%);
    }

    .css-sector::after {
        content: "";
        position: absolute;
        inset: 2.2%;
        border: 1px solid rgba(160,242,255,0.32);
        border-radius: 50%;
        box-shadow: inset 0 0 30px rgba(74,220,255,0.08);
    }

    .css-sector-brief {
        clip-path: polygon(
            50% 50%,
            7.6% 23.5%,
            14.6% 14.6%,
            25% 6.7%,
            37.1% 1.7%,
            50% 0,
            62.9% 1.7%,
            75% 6.7%,
            85.4% 14.6%,
            92.4% 23.5%
        );
        background:
            repeating-radial-gradient(circle, transparent 0 16px, rgba(113,225,248,0.075) 17px, transparent 18px 27px),
            linear-gradient(180deg, rgba(11,126,158,0.95), rgba(4,38,52,0.98));
    }

    .css-sector-horizon {
        clip-path: polygon(
            50% 50%,
            48.3% 100%,
            37.1% 98.3%,
            25% 93.3%,
            14.6% 85.4%,
            6.7% 75%,
            1.7% 62.9%,
            0 50%,
            1.7% 37.1%,
            5.9% 26.5%
        );
        background:
            repeating-radial-gradient(circle, transparent 0 16px, rgba(99,195,255,0.075) 17px, transparent 18px 27px),
            linear-gradient(135deg, rgba(5,48,80,0.98), rgba(7,104,133,0.90));
    }

    .css-sector-scenario {
        clip-path: polygon(
            50% 50%,
            94.1% 26.5%,
            98.3% 37.1%,
            100% 50%,
            98.3% 62.9%,
            93.3% 75%,
            85.4% 85.4%,
            75% 93.3%,
            62.9% 98.3%,
            51.7% 100%
        );
        background:
            repeating-radial-gradient(circle, transparent 0 16px, rgba(188,155,255,0.08) 17px, transparent 18px 27px),
            linear-gradient(225deg, rgba(51,31,91,0.97), rgba(7,77,101,0.94));
    }

    .css-sector:hover,
    .css-sector:focus-visible {
        z-index: 13;
        opacity: 1 !important;
        transform: scale(1.048);
        filter:
            brightness(1.23)
            saturate(1.22)
            drop-shadow(0 0 10px rgba(87,225,255,0.58));
    }

    .css-sector:focus-visible {
        box-shadow: 0 0 0 2px #d8fbff;
    }

    .css-sector.is-active {
        z-index: 14;
        opacity: 1;
        transform: scale(1.074);
        filter:
            brightness(1.24)
            saturate(1.28)
            drop-shadow(0 0 13px rgba(87,225,255,0.72));
    }

    .css-sector.is-active::after {
        border-color: rgba(224,252,255,0.82);
        border-width: 2px;
        box-shadow:
            inset 0 0 38px rgba(74,220,255,0.16),
            0 0 16px rgba(74,220,255,0.20);
    }

    .sector-label-html {
        position: absolute;
        z-index: 16;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        gap: 0.16rem;
        pointer-events: none;
        color: #dffbff;
        font-family: "Cascadia Mono", Consolas, monospace;
        text-align: center;
        text-transform: uppercase;
        transition:
            transform 220ms cubic-bezier(.2,.8,.2,1),
            opacity 190ms ease,
            filter 190ms ease;
    }

    .sector-label-brief {
        top: 13.5%;
        left: 31%;
        width: 38%;
    }

    .sector-label-horizon {
        top: 64%;
        left: 4%;
        width: 34%;
    }

    .sector-label-scenario {
        top: 64%;
        right: 4%;
        width: 34%;
    }

    .sector-code-html {
        color: #63a7b7;
        font-size: clamp(0.36rem, 0.62vw, 0.50rem);
        font-weight: 750;
        letter-spacing: 0.16em;
    }

    .sector-title-html {
        color: #e8fdff;
        font-size: clamp(0.57rem, 1vw, 0.84rem);
        font-weight: 760;
        letter-spacing: 0.08em;
        line-height: 1.08;
        text-shadow: 0 0 10px rgba(99,225,255,0.34);
    }

    .sector-metric-html {
        color: #68e7ff;
        font-size: clamp(0.42rem, 0.77vw, 0.63rem);
        font-weight: 750;
        letter-spacing: 0.055em;
    }

    .sector-sub-html {
        color: #477887;
        font-size: clamp(0.30rem, 0.52vw, 0.43rem);
        font-weight: 650;
        letter-spacing: 0.10em;
        line-height: 1.25;
    }

    .sector-label-html.is-active {
        opacity: 1;
        filter: brightness(1.30) drop-shadow(0 0 7px rgba(82,231,255,0.56));
    }

    .sector-label-brief.is-active {
        transform: translateY(-7px) scale(1.05);
    }

    .sector-label-horizon.is-active {
        transform: translate(-7px, 5px) scale(1.05);
    }

    .sector-label-scenario.is-active {
        transform: translate(7px, 5px) scale(1.05);
    }

    .css-sector-brief:hover ~ .sector-label-brief,
    .css-sector-brief:focus-visible ~ .sector-label-brief {
        opacity: 1 !important;
        transform: translateY(-6px) scale(1.045);
        filter: brightness(1.25) drop-shadow(0 0 7px rgba(82,231,255,0.52));
    }

    .css-sector-horizon:hover ~ .sector-label-horizon,
    .css-sector-horizon:focus-visible ~ .sector-label-horizon {
        opacity: 1 !important;
        transform: translate(-6px, 5px) scale(1.045);
        filter: brightness(1.25) drop-shadow(0 0 7px rgba(82,231,255,0.52));
    }

    .css-sector-scenario:hover ~ .sector-label-scenario,
    .css-sector-scenario:focus-visible ~ .sector-label-scenario {
        opacity: 1 !important;
        transform: translate(6px, 5px) scale(1.045);
        filter: brightness(1.25) drop-shadow(0 0 7px rgba(82,231,255,0.52));
    }

    .dial-spoke-html,
    .dial-vector-line-html {
        position: absolute;
        left: 50%;
        top: 50%;
        z-index: 17;
        height: 1px;
        transform-origin: 0 50%;
        pointer-events: none;
    }

    .dial-spoke-html {
        width: 42.5%;
        opacity: 0.74;
        background: linear-gradient(90deg, transparent 0 38%, rgba(121,231,249,0.64) 52%, rgba(74,183,216,0.16));
        box-shadow: 0 0 5px rgba(82,231,255,0.17);
    }

    .dial-spoke-html::after {
        content: "";
        position: absolute;
        right: -2px;
        top: -2px;
        width: 5px;
        height: 5px;
        border: 1px solid rgba(123,234,251,0.66);
        border-radius: 50%;
        background: #0a2d3b;
        box-shadow: 0 0 8px rgba(82,231,255,0.55);
    }

    .dial-spoke-a { transform: rotate(-30deg); }
    .dial-spoke-b { transform: rotate(90deg); }
    .dial-spoke-c { transform: rotate(210deg); }

    .dial-vector-line-html {
        z-index: 15;
        width: 35%;
        opacity: 0.40;
        background: repeating-linear-gradient(
            90deg,
            rgba(95,220,246,0.65) 0 8px,
            transparent 8px 14px
        );
    }

    .dial-vector-a { transform: rotate(-90deg); }
    .dial-vector-b { transform: rotate(30deg); }
    .dial-vector-c { transform: rotate(150deg); }

    .css-core {
        position: absolute;
        left: 50%;
        top: 50%;
        z-index: 22;
        display: grid;
        width: 34%;
        aspect-ratio: 1;
        place-items: center;
        overflow: hidden;
        color: #eaffff !important;
        border: 1px solid rgba(115,231,249,0.66);
        border-radius: 50%;
        outline: none;
        background:
            radial-gradient(circle at 50% 45%, rgba(32,126,154,0.40), transparent 30%),
            radial-gradient(circle, #0b3c50 0, #062636 46%, #020f18 75%);
        box-shadow:
            inset 0 0 34px rgba(68,224,255,0.16),
            0 0 0 8px rgba(5,31,43,0.82),
            0 0 0 9px rgba(82,231,255,0.28),
            0 0 32px rgba(82,231,255,0.16);
        text-decoration: none !important;
        transform: translate(-50%, -50%);
        transition:
            transform 220ms cubic-bezier(.2,.8,.2,1),
            opacity 190ms ease,
            filter 190ms ease,
            border-color 190ms ease;
    }

    .css-core::before {
        content: "";
        position: absolute;
        inset: 5%;
        border: 1px dashed rgba(115,231,249,0.40);
        border-radius: 50%;
        animation: rotate-cw 24s linear infinite;
    }

    .css-core::after {
        content: "";
        position: absolute;
        inset: 14%;
        border: 2px solid transparent;
        border-top-color: rgba(162,243,255,0.92);
        border-right-color: rgba(108,208,255,0.36);
        border-radius: 50%;
        box-shadow: inset 0 0 18px rgba(82,231,255,0.07);
        animation: rotate-ccw 12s linear infinite;
    }

    .core-orbit-html,
    .core-reactor-html,
    .core-scan-html {
        position: absolute;
        border-radius: 50%;
        pointer-events: none;
    }

    .core-orbit-html {
        inset: 23%;
        opacity: 0.88;
        background: repeating-conic-gradient(
            from 0deg,
            #71eaff 0deg 5deg,
            transparent 5deg 17deg
        );
        -webkit-mask: radial-gradient(circle, transparent 0 78%, #000 80% 97%, transparent 99%);
        mask: radial-gradient(circle, transparent 0 78%, #000 80% 97%, transparent 99%);
        animation: rotate-cw 9s linear infinite;
    }

    .core-reactor-html {
        inset: 33%;
        border: 1px solid rgba(121,236,255,0.65);
        background:
            conic-gradient(from 45deg, rgba(82,231,255,0.85), transparent 14%, rgba(175,137,255,0.78) 26%, transparent 42%, rgba(82,231,255,0.85) 56%, transparent 72%, rgba(109,255,210,0.72) 87%, transparent),
            #062331;
        clip-path: polygon(50% 0, 88% 18%, 100% 50%, 82% 88%, 50% 100%, 12% 82%, 0 50%, 18% 12%);
        box-shadow: 0 0 16px rgba(82,231,255,0.42);
        animation: rotate-ccw 8s linear infinite;
    }

    .core-scan-html {
        left: 20%;
        right: 20%;
        top: 50%;
        height: 1px;
        border-radius: 0;
        background: linear-gradient(90deg, transparent, rgba(130,242,255,0.82), transparent);
        box-shadow: 0 0 8px rgba(82,231,255,0.62);
        animation: core-scan 3.8s ease-in-out infinite;
    }

    .core-copy-html {
        position: relative;
        z-index: 6;
        display: flex;
        flex-direction: column;
        align-items: center;
        gap: 0.18rem;
        padding: 0 0.7rem;
        color: #eaffff;
        font-family: "Cascadia Mono", Consolas, monospace;
        text-align: center;
        text-transform: uppercase;
    }

    .core-code-html {
        color: #5d96a5;
        font-size: clamp(0.32rem, 0.56vw, 0.45rem);
        font-weight: 750;
        letter-spacing: 0.16em;
    }

    .core-main-html {
        color: #f0feff;
        font-size: clamp(0.62rem, 1.12vw, 0.94rem);
        font-weight: 780;
        letter-spacing: 0.08em;
        line-height: 1.02;
        text-shadow: 0 0 11px rgba(93,230,255,0.62);
    }

    .core-online-html {
        display: inline-flex;
        align-items: center;
        gap: 0.34rem;
        color: #52f1b2;
        font-size: clamp(0.32rem, 0.56vw, 0.45rem);
        font-weight: 750;
        letter-spacing: 0.14em;
    }

    .core-online-html::before {
        content: "";
        width: 5px;
        height: 5px;
        border-radius: 50%;
        background: #52f1b2;
        box-shadow: 0 0 7px #52f1b2;
        animation: bar-pulse 2s ease-in-out infinite;
    }

    .core-hint-html {
        color: #426f7d;
        font-size: clamp(0.26rem, 0.45vw, 0.37rem);
        font-weight: 650;
        letter-spacing: 0.08em;
    }

    .css-core:hover,
    .css-core:focus-visible {
        opacity: 1 !important;
        border-color: #e0fbff;
        transform: translate(-50%, -50%) scale(1.06);
        filter: brightness(1.22) drop-shadow(0 0 13px rgba(82,231,255,0.68));
    }

    .css-core:focus-visible {
        box-shadow:
            0 0 0 2px #e0fbff,
            0 0 32px rgba(82,231,255,0.34);
    }

    .css-core.is-active {
        opacity: 1;
        border-color: #ffffff;
        transform: translate(-50%, -50%) scale(1.085);
        filter:
            brightness(1.24)
            saturate(1.22)
            drop-shadow(0 0 15px rgba(112,229,255,0.75));
    }

    .dial-cardinal-html {
        position: absolute;
        z-index: 18;
        color: #69b7c7;
        font-family: "Cascadia Mono", Consolas, monospace;
        font-size: clamp(0.32rem, 0.53vw, 0.44rem);
        font-weight: 750;
        letter-spacing: 0.08em;
        pointer-events: none;
        text-transform: uppercase;
    }

    .dial-cardinal-n { top: 0.6%; left: 50%; transform: translateX(-50%); }
    .dial-cardinal-e { right: 0.2%; top: 50%; transform: translateY(-50%); }
    .dial-cardinal-s { bottom: 0.6%; left: 50%; transform: translateX(-50%); }
    .dial-cardinal-w { left: 0.2%; top: 50%; transform: translateY(-50%); }

    .integrated-system.has-selection .css-sector:not(.is-active),
    .integrated-system.has-selection .css-core:not(.is-active) {
        opacity: 0.22;
        filter: saturate(0.42) brightness(0.62);
    }

    .integrated-system.has-selection .sector-label-html:not(.is-active) {
        opacity: 0.26;
        filter: saturate(0.48) brightness(0.66);
    }

    .integrated-system.has-selection .css-sector:not(.is-active):hover,
    .integrated-system.has-selection .css-sector:not(.is-active):focus-visible,
    .integrated-system.has-selection .css-core:not(.is-active):hover,
    .integrated-system.has-selection .css-core:not(.is-active):focus-visible {
        opacity: 0.90;
    }

    @keyframes core-scan {
        0%, 100% { transform: translateY(-11px); opacity: 0.22; }
        50% { transform: translateY(11px); opacity: 0.92; }
    }

    .telemetry-console {
        position: relative;
        z-index: 4;
        min-width: 0;
        padding: 0.95rem 0.9rem;
        background: linear-gradient(145deg, rgba(5,32,45,0.92), rgba(2,16,25,0.88));
        border: 1px solid rgba(82,231,255,0.20);
        box-shadow: inset 0 0 25px rgba(82,231,255,0.035);
    }

    .telemetry-console.console-left {
        clip-path: polygon(0 0, 86% 0, 100% 13%, 100% 87%, 86% 100%, 0 100%);
    }

    .telemetry-console.console-right {
        clip-path: polygon(14% 0, 100% 0, 100% 100%, 14% 100%, 0 87%, 0 13%);
    }

    .telemetry-console::after {
        content: "";
        position: absolute;
        top: 50%;
        width: 44px;
        height: 1px;
        background: linear-gradient(90deg, rgba(82,231,255,0.60), transparent);
        box-shadow: 0 0 7px rgba(82,231,255,0.30);
    }

    .console-left::after { left: 100%; }
    .console-right::after {
        right: 100%;
        transform: rotate(180deg);
    }

    .console-head {
        display: flex;
        align-items: center;
        justify-content: space-between;
        gap: 0.5rem;
        margin-bottom: 0.8rem;
        padding-bottom: 0.55rem;
        color: #72dced;
        border-bottom: 1px solid rgba(82,231,255,0.14);
        font-family: "Cascadia Mono", Consolas, monospace;
        font-size: 0.57rem;
        font-weight: 750;
        letter-spacing: 0.12em;
        text-transform: uppercase;
    }

    .console-head span:last-child {
        color: #376675;
        font-size: 0.48rem;
    }

    .console-row {
        display: grid;
        grid-template-columns: 1fr auto;
        align-items: center;
        gap: 0.65rem;
        min-width: 0;
        padding: 0.43rem 0;
        border-bottom: 1px solid rgba(82,231,255,0.07);
    }

    .console-row:last-of-type {
        border-bottom: 0;
    }

    .console-label {
        overflow: hidden;
        color: #4d7887;
        font-family: "Cascadia Mono", Consolas, monospace;
        font-size: 0.52rem;
        letter-spacing: 0.07em;
        text-overflow: ellipsis;
        text-transform: uppercase;
        white-space: nowrap;
    }

    .console-value {
        color: #c9f3f8;
        font-family: "Cascadia Mono", Consolas, monospace;
        font-size: 0.61rem;
        font-weight: 700;
        text-align: right;
        white-space: nowrap;
    }

    .console-value.signal-alert { color: var(--red); }
    .console-value.signal-watch { color: var(--amber); }
    .console-value.signal-track { color: var(--green); }

    .console-bars {
        display: flex;
        align-items: flex-end;
        gap: 3px;
        height: 28px;
        margin-top: 0.8rem;
        padding-top: 0.45rem;
        border-top: 1px solid rgba(82,231,255,0.09);
    }

    .console-bars span {
        flex: 1;
        min-width: 2px;
        background: linear-gradient(180deg, #65e9ff, rgba(25,104,130,0.24));
        box-shadow: 0 0 5px rgba(82,231,255,0.17);
        animation: bar-pulse 3.4s ease-in-out infinite;
    }

    .console-bars span:nth-child(2n) { animation-delay: -0.7s; }
    .console-bars span:nth-child(3n) { animation-delay: -1.4s; }

    .console-caption {
        margin-top: 0.55rem;
        color: #345e6c;
        font-family: "Cascadia Mono", Consolas, monospace;
        font-size: 0.45rem;
        letter-spacing: 0.08em;
        line-height: 1.45;
        text-transform: uppercase;
    }

    .system-bottom-rail {
        position: relative;
        z-index: 4;
        display: grid;
        grid-template-columns: 1fr auto 1fr;
        align-items: center;
        gap: 0.8rem;
        margin-top: -0.25rem;
        padding: 0.72rem 0.2rem 0.1rem;
        color: #3e6978;
        border-top: 1px solid rgba(82,231,255,0.11);
        font-family: "Cascadia Mono", Consolas, monospace;
        font-size: 0.51rem;
        letter-spacing: 0.09em;
        text-transform: uppercase;
    }

    .system-bottom-rail > span:last-child {
        text-align: right;
    }

    .system-reset {
        display: inline-flex;
        align-items: center;
        gap: 0.45rem;
        padding: 0.34rem 0.7rem;
        color: #78dcec !important;
        background: rgba(82,231,255,0.04);
        border: 1px solid rgba(82,231,255,0.22);
        text-decoration: none !important;
        transition: border-color 160ms ease, box-shadow 160ms ease, color 160ms ease;
    }

    .system-reset:hover {
        color: #ffffff !important;
        border-color: rgba(82,231,255,0.72);
        box-shadow: 0 0 16px rgba(82,231,255,0.12);
    }

    .system-reset.is-home {
        color: #416b79 !important;
        border-color: rgba(82,231,255,0.09);
        pointer-events: none;
    }

    .system-overview-note,
    .active-module-banner {
        position: relative;
        display: flex;
        align-items: center;
        justify-content: space-between;
        gap: 1rem;
        margin: 0.15rem 0 1.15rem;
        padding: 0.72rem 0.95rem;
        background: linear-gradient(90deg, rgba(82,231,255,0.065), rgba(82,231,255,0.01));
        border-left: 2px solid var(--cyan);
        border-top: 1px solid rgba(82,231,255,0.11);
        border-bottom: 1px solid rgba(82,231,255,0.07);
    }

    .overview-title,
    .active-module-name {
        color: #dffaff;
        font-family: "Cascadia Mono", Consolas, monospace;
        font-size: 0.67rem;
        font-weight: 750;
        letter-spacing: 0.09em;
        text-transform: uppercase;
    }

    .overview-copy,
    .active-module-state {
        color: #527d8c;
        font-family: "Cascadia Mono", Consolas, monospace;
        font-size: 0.55rem;
        letter-spacing: 0.07em;
        text-align: right;
        text-transform: uppercase;
    }

    @keyframes system-scan {
        from { transform: translateX(0); }
        to { transform: translateX(560%); }
    }

    @keyframes bar-pulse {
        0%, 100% { opacity: 0.45; filter: brightness(0.75); }
        50% { opacity: 1; filter: brightness(1.25); }
    }

    @media (max-width: 1120px) {
        .system-grid {
            grid-template-columns: minmax(140px, 0.46fr) minmax(500px, 1.7fr) minmax(140px, 0.46fr);
        }

        .console-row {
            grid-template-columns: 1fr;
            gap: 0.16rem;
        }

        .console-value {
            text-align: left;
        }
    }

    @media (max-width: 860px) {
        .integrated-system {
            padding-left: 0.7rem;
            padding-right: 0.7rem;
        }

        .system-grid {
            grid-template-columns: 1fr;
            min-height: 0;
        }

        .dial-viewport {
            grid-row: 1;
        }

        .telemetry-console {
            display: none;
        }

        .command-dial-html {
            width: min(100%, 660px);
        }

        .system-bottom-rail {
            grid-template-columns: 1fr auto;
        }

        .system-bottom-rail > span:last-child {
            display: none;
        }

        .system-overview-note,
        .active-module-banner {
            align-items: flex-start;
            flex-direction: column;
            gap: 0.3rem;
        }

        .overview-copy,
        .active-module-state {
            text-align: left;
        }
    }

    @media (max-width: 560px) {
        .sector-sub-html,
        .core-hint-html,
        .dial-cardinal-html {
            display: none;
        }

        .sector-label-horizon {
            left: 2%;
            width: 37%;
        }

        .sector-label-scenario {
            right: 2%;
            width: 37%;
        }
    }

    /* -------------------------------------------------
       STREAMLIT CONTROLS
       ------------------------------------------------- */

    [data-testid="stForm"] {
        padding: 1.2rem 1.25rem 1.3rem;
        background: linear-gradient(145deg, rgba(7, 29, 42, 0.85), rgba(3, 16, 25, 0.82));
        border: 1px solid rgba(82, 231, 255, 0.16);
        border-radius: 0;
        clip-path: polygon(0 0, calc(100% - 16px) 0, 100% 16px, 100% 100%, 0 100%);
    }

    .stSlider [data-baseweb="slider"] > div > div {
        background: rgba(82, 231, 255, 0.18);
    }

    .stSlider [role="slider"] {
        background: var(--cyan) !important;
        border-color: #d9fbff !important;
        box-shadow: 0 0 0 4px rgba(82,231,255,0.10), 0 0 16px rgba(82,231,255,0.75) !important;
    }

    .stSlider label, .stTextInput label {
        color: #a5c9d4 !important;
        font-family: "Cascadia Mono", Consolas, monospace !important;
        font-size: 0.69rem !important;
        letter-spacing: 0.045em;
        text-transform: uppercase;
    }

    div.stButton > button,
    div[data-testid="stFormSubmitButton"] > button {
        min-height: 2.65rem;
        color: var(--cyan-soft);
        background: linear-gradient(120deg, rgba(13, 65, 84, 0.92), rgba(5, 34, 49, 0.94));
        border: 1px solid rgba(82, 231, 255, 0.42);
        border-radius: 0;
        font-family: "Cascadia Mono", Consolas, monospace;
        font-size: 0.68rem;
        font-weight: 750;
        letter-spacing: 0.055em;
        text-transform: uppercase;
        clip-path: polygon(8px 0, 100% 0, 100% calc(100% - 8px), calc(100% - 8px) 100%, 0 100%, 0 8px);
        box-shadow: inset 0 0 15px rgba(82,231,255,0.035);
        transition: all 160ms ease;
    }

    div.stButton > button:hover,
    div[data-testid="stFormSubmitButton"] > button:hover {
        color: #ffffff;
        border-color: var(--cyan);
        background: linear-gradient(120deg, rgba(18, 89, 112, 0.95), rgba(6, 44, 61, 0.96));
        box-shadow: 0 0 22px rgba(82,231,255,0.15), inset 0 0 22px rgba(82,231,255,0.08);
        transform: translateY(-1px);
    }

    div.stButton > button:focus:not(:active),
    div[data-testid="stFormSubmitButton"] > button:focus:not(:active) {
        border-color: var(--cyan);
        box-shadow: 0 0 0 2px rgba(82,231,255,0.15);
    }

    [data-baseweb="input"] {
        background: rgba(3, 15, 24, 0.92) !important;
        border: 1px solid rgba(82,231,255,0.20) !important;
        border-radius: 0 !important;
    }

    [data-baseweb="input"]:focus-within {
        border-color: rgba(82,231,255,0.62) !important;
        box-shadow: 0 0 18px rgba(82,231,255,0.08);
    }

    [data-testid="stExpander"] {
        background: rgba(4, 18, 28, 0.68);
        border: 1px solid rgba(82, 231, 255, 0.13);
        border-radius: 0;
    }

    [data-testid="stExpander"] summary {
        color: #87afbd;
        font-family: "Cascadia Mono", Consolas, monospace;
        font-size: 0.68rem;
        letter-spacing: 0.04em;
        text-transform: uppercase;
    }

    [data-testid="stMetric"] {
        padding: 0.9rem 1rem;
        background: rgba(5, 28, 40, 0.76);
        border: 1px solid rgba(82,231,255,0.15);
    }

    [data-testid="stMetricLabel"] {
        color: #79a1af;
    }

    [data-testid="stMetricValue"] {
        color: #eaffff;
        font-family: "Cascadia Mono", Consolas, monospace;
    }

    [data-testid="stCaptionContainer"] {
        color: #557f8f;
        font-family: "Cascadia Mono", Consolas, monospace;
        font-size: 0.66rem;
    }

    [data-testid="stChatMessage"] {
        background: linear-gradient(120deg, rgba(6, 28, 41, 0.84), rgba(3, 16, 25, 0.80));
        border: 1px solid rgba(82, 231, 255, 0.13);
        border-radius: 0;
        margin-bottom: 0.65rem;
        clip-path: polygon(0 0, calc(100% - 12px) 0, 100% 12px, 100% 100%, 0 100%);
    }

    [data-testid="stChatMessage"] [data-testid="stChatMessageAvatarUser"] {
        background: rgba(184, 140, 255, 0.16);
        border: 1px solid rgba(184, 140, 255, 0.38);
    }

    [data-testid="stChatMessage"] [data-testid="stChatMessageAvatarAssistant"] {
        background: rgba(82, 231, 255, 0.12);
        border: 1px solid rgba(82, 231, 255, 0.38);
    }

    [data-testid="stVegaLiteChart"] {
        padding: 0.5rem 0.35rem 0.25rem;
        background:
            linear-gradient(180deg, rgba(6, 27, 39, 0.64), rgba(3, 15, 23, 0.42)),
            linear-gradient(rgba(82,231,255,0.025) 1px, transparent 1px),
            linear-gradient(90deg, rgba(82,231,255,0.025) 1px, transparent 1px);
        background-size: auto, 28px 28px, 28px 28px;
        border: 1px solid rgba(82,231,255,0.11);
    }

    .copilot-intro {
        display: grid;
        grid-template-columns: auto 1fr;
        align-items: center;
        gap: 1rem;
    }

    .copilot-glyph {
        width: 54px;
        height: 54px;
        display: grid;
        place-items: center;
        color: var(--cyan);
        border: 1px solid rgba(82,231,255,0.50);
        background: radial-gradient(circle, rgba(82,231,255,0.18), transparent 66%);
        font-family: "Cascadia Mono", Consolas, monospace;
        font-size: 1rem;
        clip-path: polygon(50% 0, 100% 25%, 100% 75%, 50% 100%, 0 75%, 0 25%);
        box-shadow: 0 0 24px rgba(82,231,255,0.11);
    }

    .copilot-name {
        color: #ecfdff;
        font-size: 0.98rem;
        font-weight: 680;
        margin-bottom: 0.22rem;
    }

    .copilot-copy {
        color: #789fac;
        font-size: 0.82rem;
        line-height: 1.5;
    }

    .copilot-context-strip {
        display:grid; grid-template-columns:repeat(4,minmax(0,1fr)); gap:.55rem; margin:.75rem 0 1rem;
    }
    .copilot-context-item {
        padding:.62rem .72rem; background:rgba(82,231,255,.025); border:1px solid rgba(82,231,255,.10);
    }
    .copilot-context-item span {
        display:block; color:#557f8f; font:700 .50rem "Cascadia Mono",Consolas,monospace; letter-spacing:.10em; text-transform:uppercase;
    }
    .copilot-context-item strong {
        display:block; margin-top:.18rem; color:#e7fbff; font-size:.80rem; font-weight:720;
    }
    .copilot-thread-label {
        color:#52e7ff; font:750 .52rem "Cascadia Mono",Consolas,monospace; letter-spacing:.12em; text-transform:uppercase; margin-bottom:.30rem;
    }
    .copilot-answer-label {
        color:#8eeaff; font:750 .50rem "Cascadia Mono",Consolas,monospace; letter-spacing:.12em; text-transform:uppercase; margin-bottom:.38rem;
    }
    .copilot-user-label {
        color:#b99cff; font:750 .50rem "Cascadia Mono",Consolas,monospace; letter-spacing:.12em; text-transform:uppercase; margin-bottom:.38rem;
    }
    .copilot-command-bar {
        display:flex; align-items:center; justify-content:space-between; gap:.8rem; margin:.55rem 0 .75rem;
        color:#567f8e; font:700 .52rem "Cascadia Mono",Consolas,monospace; letter-spacing:.08em; text-transform:uppercase;
    }
    .copilot-module-dock {
        display:grid; grid-template-columns:repeat(4,minmax(0,1fr)); gap:.55rem; margin:1rem 0 .55rem;
    }
    .copilot-module-link {
        display:flex; align-items:center; justify-content:center; min-height:42px; padding:.55rem .7rem;
        color:#9ac8d2 !important; background:rgba(82,231,255,.025); border:1px solid rgba(82,231,255,.12);
        text-decoration:none !important; font:750 .55rem "Cascadia Mono",Consolas,monospace; letter-spacing:.08em; text-transform:uppercase;
        transition:all 160ms ease;
    }
    .copilot-module-link:hover {
        color:#ecfdff !important; border-color:rgba(82,231,255,.42); background:rgba(82,231,255,.08); box-shadow:0 0 18px rgba(82,231,255,.08);
    }
    .copilot-evidence-note {
        color:#547987; font:650 .55rem "Cascadia Mono",Consolas,monospace; letter-spacing:.05em; margin-top:.3rem;
    }
    [data-testid="stChatMessage"] {
        padding:1rem 1.05rem;
    }
    [data-testid="stChatMessage"] p,
    [data-testid="stChatMessage"] li {
        color:#b9ced5; line-height:1.55;
    }
    [data-testid="stChatMessage"] strong { color:#effdff; }
    [data-testid="stChatMessageAvatarUser"],
    [data-testid="stChatMessageAvatarAssistant"] {
        border-radius:0 !important;
        box-shadow:none !important;
    }

    .system-footer {
        display: flex;
        align-items: center;
        justify-content: space-between;
        gap: 1rem;
        margin-top: 2.2rem;
        padding-top: 0.85rem;
        color: #496f7d;
        border-top: 1px solid rgba(82,231,255,0.10);
        font-family: "Cascadia Mono", Consolas, monospace;
        font-size: 0.57rem;
        letter-spacing: 0.08em;
        text-transform: uppercase;
    }

    code, pre {
        font-family: "Cascadia Mono", "SFMono-Regular", Consolas, monospace !important;
    }

    ::-webkit-scrollbar { width: 9px; height: 9px; }
    ::-webkit-scrollbar-track { background: #02080d; }
    ::-webkit-scrollbar-thumb { background: #124355; border: 2px solid #02080d; }
    ::-webkit-scrollbar-thumb:hover { background: #1b6077; }

    @keyframes scan-horizontal {
        from { transform: translateX(0); }
        to { transform: translateX(360%); }
    }

    @keyframes pulse-dot {
        0%, 100% { opacity: 0.65; transform: scale(0.88); }
        50% { opacity: 1; transform: scale(1.08); }
    }

    @keyframes rotate-cw { to { transform: rotate(360deg); } }
    @keyframes rotate-ccw { to { transform: rotate(-360deg); } }

    @keyframes orb-breathe {
        0%, 100% { filter: brightness(0.92); transform: scale(0.98); }
        50% { filter: brightness(1.13); transform: scale(1.015); }
    }

    @media (prefers-reduced-motion: reduce) {
        *, *::before, *::after {
            animation-duration: 0.01ms !important;
            animation-iteration-count: 1 !important;
            transition-duration: 0.01ms !important;
        }
    }

    @media (max-width: 900px) {
        .hud-hero {
            grid-template-columns: 1fr;
            padding: 1.55rem;
        }

        .hero-core {
            min-height: 160px;
        }

        .arc-orb {
            width: 142px;
            height: 142px;
        }

        .scenario-summary {
            grid-template-columns: 1fr;
        }

        .diagnostic-grid {
            grid-template-columns: 1fr 1fr;
        }

        .sync-copy {
            display: none;
        }
    }

</style>\n"""

EXTENSIONS_CSS = """\n<style>
    .kpi-neutral {
        display: flex;
        align-items: center;
        gap: 0.45rem;
        margin-top: 0.78rem;
        color: var(--cyan-soft);
        font-family: "Cascadia Mono", Consolas, monospace;
        font-size: 0.72rem;
        font-weight: 700;
        letter-spacing: 0.015em;
    }

    .kpi-card:has(.kpi-neutral)::before {
        background: linear-gradient(90deg, var(--cyan), transparent);
        box-shadow: 0 0 12px rgba(82,231,255,0.55);
    }

    .brief-grid-label {
        margin: 0.85rem 0 0.45rem;
        color: #608997;
        font-family: "Cascadia Mono", Consolas, monospace;
        font-size: 0.58rem;
        font-weight: 750;
        letter-spacing: 0.13em;
        text-transform: uppercase;
    }

    .alert-neutral {
        border-left-color: var(--cyan);
        color: var(--cyan);
    }

    .intel-card {
        position: relative;
        padding: 0.95rem 1rem;
        margin-bottom: 0.68rem;
        background: linear-gradient(100deg, rgba(8,31,44,0.92), rgba(4,17,27,0.78));
        border: 1px solid rgba(120,204,223,0.13);
        border-left: 2px solid rgba(82,231,255,0.52);
        clip-path: polygon(0 0, calc(100% - 12px) 0, 100% 12px, 100% 100%, 0 100%);
    }

    .intel-meta {
        color: #5f8d9d;
        font-family: "Cascadia Mono", Consolas, monospace;
        font-size: 0.57rem;
        font-weight: 700;
        letter-spacing: 0.08em;
        text-transform: uppercase;
    }

    .intel-headline {
        margin-top: 0.35rem;
        color: #e4f8fb;
        font-size: 0.84rem;
        font-weight: 650;
        line-height: 1.42;
    }

    .intel-detail {
        margin-top: 0.35rem;
        color: #7fa6b5;
        font-size: 0.76rem;
        line-height: 1.42;
    }

    .intel-link {
        display: inline-block;
        margin-top: 0.45rem;
        color: var(--cyan) !important;
        font-family: "Cascadia Mono", Consolas, monospace;
        font-size: 0.62rem;
        font-weight: 700;
        text-decoration: none !important;
    }

    .intel-link:hover {
        color: #dffcff !important;
        text-shadow: 0 0 10px rgba(82,231,255,0.55);
    }

    .certified-chip {
        display: inline-flex;
        align-items: center;
        gap: 0.35rem;
        padding: 0.25rem 0.5rem;
        color: #8eeaff;
        border: 1px solid rgba(82,231,255,0.22);
        background: rgba(82,231,255,0.04);
        font-family: "Cascadia Mono", Consolas, monospace;
        font-size: 0.56rem;
        font-weight: 700;
        letter-spacing: 0.08em;
        text-transform: uppercase;
    }
</style>\n"""

PANELS_CSS = """\n<style>
    .feed-strip {
        display:flex;
        flex-wrap:wrap;
        gap:0.42rem;
        margin:-0.1rem 0 1rem 0;
    }

    .feed-chip {
        display:inline-flex;
        align-items:center;
        gap:0.38rem;
        padding:0.28rem 0.52rem;
        color:#86C8D6;
        background:rgba(82,231,255,0.035);
        border:1px solid rgba(82,231,255,0.13);
        font-family:"Cascadia Mono",Consolas,monospace;
        font-size:0.55rem;
        font-weight:700;
        letter-spacing:0.08em;
        text-transform:uppercase;
    }

    .feed-chip::before {
        content:"";
        width:5px;
        height:5px;
        border-radius:50%;
        background:var(--green);
        box-shadow:0 0 8px rgba(66,245,167,0.8);
    }

    /* The core dial stays visually pure. Secondary intelligence sits
       outside the circle and is accessed through the dock below. */
    .system-grid {
        grid-template-columns:minmax(260px,0.72fr) minmax(560px,1.55fr) minmax(270px,0.76fr) !important;
        gap:0.85rem !important;
        min-height:660px;
    }

    .decision-panel,
    .focus-panel {
        position:relative;
        z-index:5;
        min-width:0;
        overflow:hidden;
        color:#BFDCE4;
        background:
            linear-gradient(145deg,rgba(4,25,37,0.94),rgba(2,15,24,0.92)),
            radial-gradient(circle at 100% 0%,rgba(82,231,255,0.08),transparent 48%);
        border:1px solid rgba(82,231,255,0.22);
        box-shadow:inset 0 0 36px rgba(82,231,255,0.025),0 18px 50px rgba(0,0,0,0.18);
    }

    .decision-panel {
        padding:1.02rem 1rem 0.82rem;
        clip-path:polygon(0 0,calc(100% - 16px) 0,100% 16px,100% 100%,0 100%);
    }

    .focus-panel {
        padding:1.05rem 1.05rem 1rem;
        clip-path:polygon(12px 0,100% 0,100% calc(100% - 14px),calc(100% - 14px) 100%,0 100%,0 12px);
    }

    .side-panel-head {
        display:flex;
        align-items:center;
        justify-content:space-between;
        gap:0.6rem;
        padding-bottom:0.72rem;
        border-bottom:1px solid rgba(82,231,255,0.14);
    }

    .side-panel-title {
        color:#E8FBFF;
        font-family:"Cascadia Mono",Consolas,monospace;
        font-size:0.72rem;
        font-weight:780;
        letter-spacing:0.12em;
        text-transform:uppercase;
    }

    .side-live {
        display:inline-flex;
        align-items:center;
        gap:0.35rem;
        color:#65E7B5;
        font-family:"Cascadia Mono",Consolas,monospace;
        font-size:0.50rem;
        font-weight:760;
        letter-spacing:0.12em;
        text-transform:uppercase;
    }

    .side-live::after {
        content:"";
        width:6px;
        height:6px;
        border-radius:50%;
        background:var(--green);
        box-shadow:0 0 10px rgba(66,245,167,0.85);
    }

    .decision-list {
        display:grid;
        gap:0;
    }

    .decision-item {
        display:grid;
        grid-template-columns:44px minmax(0,1fr) 18px;
        align-items:center;
        gap:0.72rem;
        min-height:92px;
        padding:0.78rem 0.05rem;
        border-bottom:1px solid rgba(82,231,255,0.10);
        color:inherit !important;
        text-decoration:none !important;
        transition:background 160ms ease,transform 160ms ease;
    }

    .decision-item:last-child { border-bottom:0; }

    .decision-item:hover {
        transform:translateX(3px);
        background:linear-gradient(90deg,rgba(82,231,255,0.055),transparent);
    }

    .decision-icon {
        width:38px;
        height:38px;
        display:grid;
        place-items:center;
        border-radius:50%;
        border:1px solid rgba(82,231,255,0.42);
        color:#7FEAFF;
        font-family:"Cascadia Mono",Consolas,monospace;
        font-size:0.9rem;
        box-shadow:inset 0 0 18px rgba(82,231,255,0.05),0 0 16px rgba(82,231,255,0.05);
    }

    .decision-icon.is-green {
        color:#55F1B0;
        border-color:rgba(66,245,167,0.55);
        box-shadow:inset 0 0 18px rgba(66,245,167,0.05),0 0 16px rgba(66,245,167,0.07);
    }

    .decision-icon.is-violet {
        color:#C5A7FF;
        border-color:rgba(184,140,255,0.55);
    }

    .decision-copy { min-width:0; }

    .decision-title {
        color:#E5F8FB;
        font-size:0.80rem;
        font-weight:720;
        line-height:1.25;
    }

    .decision-primary {
        margin-top:0.25rem;
        color:#7CCBDA;
        font-family:"Cascadia Mono",Consolas,monospace;
        font-size:0.60rem;
        font-weight:700;
        line-height:1.4;
    }

    .decision-secondary {
        margin-top:0.16rem;
        color:#577F8E;
        font-size:0.64rem;
        line-height:1.38;
    }

    .decision-arrow {
        color:#50CDE5;
        font-size:1.0rem;
        opacity:0.78;
    }

    .focus-head {
        display:grid;
        grid-template-columns:44px minmax(0,1fr) 20px;
        align-items:center;
        gap:0.72rem;
        padding-bottom:0.8rem;
        border-bottom:1px solid rgba(82,231,255,0.14);
    }

    .focus-glyph {
        width:40px;
        height:40px;
        display:grid;
        place-items:center;
        color:#79E9FF;
        border:1px solid rgba(82,231,255,0.42);
        font-family:"Cascadia Mono",Consolas,monospace;
        font-size:0.95rem;
        clip-path:polygon(50% 0,100% 25%,100% 75%,50% 100%,0 75%,0 25%);
        background:rgba(82,231,255,0.04);
    }

    .focus-title {
        color:#EAFBFF;
        font-size:1rem;
        font-weight:760;
        letter-spacing:0.02em;
    }

    .focus-subtitle {
        margin-top:0.18rem;
        color:#5F91A1;
        font-family:"Cascadia Mono",Consolas,monospace;
        font-size:0.48rem;
        font-weight:700;
        letter-spacing:0.09em;
        text-transform:uppercase;
    }

    .focus-open {
        color:#6BE4F7 !important;
        text-decoration:none !important;
        font-size:1rem;
    }

    .focus-metric-grid {
        display:grid;
        grid-template-columns:1fr 1fr;
        gap:0.55rem;
        margin-top:0.78rem;
    }

    .focus-metric {
        min-width:0;
        padding:0.62rem 0.65rem;
        background:rgba(82,231,255,0.025);
        border:1px solid rgba(82,231,255,0.09);
    }

    .focus-metric-label {
        color:#4E7E8E;
        font-family:"Cascadia Mono",Consolas,monospace;
        font-size:0.46rem;
        font-weight:720;
        letter-spacing:0.09em;
        text-transform:uppercase;
    }

    .focus-metric-value {
        margin-top:0.25rem;
        color:#EAFBFF;
        font-family:"Cascadia Mono",Consolas,monospace;
        font-size:0.86rem;
        font-weight:720;
    }

    .focus-metric-sub {
        margin-top:0.16rem;
        color:#5B8796;
        font-size:0.56rem;
        line-height:1.3;
    }

    .focus-chart-head {
        display:flex;
        align-items:center;
        justify-content:space-between;
        gap:0.5rem;
        margin-top:0.82rem;
        color:#6FA7B6;
        font-family:"Cascadia Mono",Consolas,monospace;
        font-size:0.48rem;
        font-weight:720;
        letter-spacing:0.09em;
        text-transform:uppercase;
    }

    .sensitivity-svg {
        width:100%;
        height:118px;
        display:block;
        margin-top:0.25rem;
        overflow:visible;
    }

    .focus-cta {
        display:flex;
        align-items:center;
        justify-content:center;
        min-height:34px;
        margin-top:0.55rem;
        color:#86ECFF !important;
        border:1px solid rgba(82,231,255,0.25);
        background:rgba(82,231,255,0.025);
        font-family:"Cascadia Mono",Consolas,monospace;
        font-size:0.53rem;
        font-weight:760;
        letter-spacing:0.08em;
        text-decoration:none !important;
        text-transform:uppercase;
        transition:background 150ms ease,border-color 150ms ease;
    }

    .focus-cta:hover {
        background:rgba(82,231,255,0.07);
        border-color:rgba(137,241,255,0.62);
    }

    .intelligence-dock {
        position:relative;
        z-index:6;
        max-width:1040px;
        margin:-0.25rem auto 1.45rem;
        padding:0.72rem 1rem 0.9rem;
        background:
            linear-gradient(180deg,rgba(4,24,35,0.86),rgba(2,13,21,0.94)),
            radial-gradient(circle at 50% 0%,rgba(82,231,255,0.08),transparent 60%);
        border:1px solid rgba(82,231,255,0.16);
        clip-path:polygon(24px 0,calc(100% - 24px) 0,100% 24px,100% 100%,0 100%,0 24px);
    }

    .dock-kicker {
        display:flex;
        align-items:center;
        justify-content:center;
        gap:0.65rem;
        color:#58CDE2;
        font-family:"Cascadia Mono",Consolas,monospace;
        font-size:0.52rem;
        font-weight:780;
        letter-spacing:0.20em;
        text-transform:uppercase;
    }

    .dock-kicker::before,
    .dock-kicker::after {
        content:"";
        width:95px;
        height:1px;
        background:linear-gradient(90deg,transparent,rgba(82,231,255,0.32));
    }

    .dock-kicker::after {
        background:linear-gradient(90deg,rgba(82,231,255,0.32),transparent);
    }

    .dock-actions {
        display:grid;
        grid-template-columns:repeat(3,minmax(0,1fr));
        gap:0.75rem;
        max-width:720px;
        margin:0.68rem auto 0;
    }

    .dock-action {
        display:grid;
        grid-template-columns:36px minmax(0,1fr);
        align-items:center;
        gap:0.62rem;
        min-height:56px;
        padding:0.55rem 0.72rem;
        color:#8BCDDD !important;
        background:rgba(82,231,255,0.018);
        border:1px solid rgba(82,231,255,0.20);
        text-decoration:none !important;
        clip-path:polygon(11px 0,100% 0,100% calc(100% - 11px),calc(100% - 11px) 100%,0 100%,0 11px);
        transition:transform 160ms ease,border-color 160ms ease,background 160ms ease;
    }

    .dock-action:hover {
        transform:translateY(-2px);
        color:#EAFBFF !important;
        border-color:rgba(116,236,255,0.68);
        background:rgba(82,231,255,0.055);
    }

    .dock-action.is-active {
        color:#EAFBFF !important;
        border-color:#58E4FF;
        background:linear-gradient(145deg,rgba(12,80,99,0.44),rgba(26,28,61,0.32));
        box-shadow:0 0 18px rgba(82,231,255,0.11),inset 0 0 18px rgba(82,231,255,0.04);
    }

    .dock-icon {
        width:34px;
        height:34px;
        display:grid;
        place-items:center;
        color:#62DDF3;
        border:1px solid rgba(82,231,255,0.30);
        border-radius:50%;
        font-family:"Cascadia Mono",Consolas,monospace;
        font-size:0.82rem;
    }

    .dock-copy { min-width:0; }

    .dock-title {
        display:block;
        color:#DFF8FC;
        font-family:"Cascadia Mono",Consolas,monospace;
        font-size:0.66rem;
        font-weight:780;
        letter-spacing:0.08em;
        text-transform:uppercase;
    }

    .dock-metric {
        display:block;
        margin-top:0.15rem;
        overflow:hidden;
        color:#548493;
        font-family:"Cascadia Mono",Consolas,monospace;
        font-size:0.46rem;
        font-weight:690;
        text-overflow:ellipsis;
        white-space:nowrap;
    }

    .trend-up { color:var(--green) !important; }
    .trend-down { color:var(--red) !important; }
    .trend-flat { color:#6F9DAA !important; }

    .strategy-explainer {
        margin:0.8rem 0 1rem;
        padding:1rem 1.05rem;
        background:
            linear-gradient(135deg,rgba(7,34,48,0.92),rgba(7,20,35,0.88)),
            radial-gradient(circle at 10% 0%,rgba(82,231,255,0.08),transparent 42%);
        border:1px solid rgba(82,231,255,0.18);
        clip-path:polygon(0 0,calc(100% - 16px) 0,100% 16px,100% 100%,0 100%);
    }

    .strategy-explainer-grid {
        display:grid;
        grid-template-columns:0.7fr 1.5fr;
        gap:1rem;
        align-items:center;
    }

    .strategy-score-bridge {
        color:#E9FBFF;
        font-family:"Cascadia Mono",Consolas,monospace;
        font-size:1.15rem;
        font-weight:760;
    }

    .strategy-score-bridge span { color:#66E5FA; }

    .strategy-explainer-copy {
        color:#7FA6B5;
        font-size:0.77rem;
        line-height:1.55;
    }

    .strategy-delta-strip {
        display:flex;
        flex-wrap:wrap;
        gap:0.4rem;
        margin-top:0.62rem;
    }

    .strategy-delta-pill {
        padding:0.26rem 0.48rem;
        border:1px solid rgba(82,231,255,0.15);
        background:rgba(82,231,255,0.025);
        color:#8FC8D5;
        font-family:"Cascadia Mono",Consolas,monospace;
        font-size:0.50rem;
        font-weight:700;
    }

    @media (max-width:1120px) {
        .system-grid {
            grid-template-columns:minmax(210px,0.62fr) minmax(520px,1.45fr) minmax(220px,0.64fr) !important;
            gap:0.55rem !important;
        }
        .decision-secondary { display:none; }
        .focus-metric-grid { grid-template-columns:1fr; }
        .sensitivity-svg { height:96px; }
    }

    @media (max-width:860px) {
        .system-grid { grid-template-columns:1fr !important; }
        .decision-panel,.focus-panel { display:none; }
        .dock-actions { grid-template-columns:1fr; }
        .strategy-explainer-grid { grid-template-columns:1fr; }
    }

    /* -------------------------------------------------
       CFO DECISION LAYER / MOTION
       ------------------------------------------------- */
    html { background:#02070c; scroll-behavior:smooth; }

    /* Chrome/Edge can animate same-origin query-parameter navigation.
       Streamlit still reruns Python, but the browser transition hides most
       of the hard page swap and makes vector changes feel continuous. */
    @view-transition { navigation: auto; }
    @keyframes vt-old { to { opacity:0; transform:scale(.998); } }
    @keyframes vt-new { from { opacity:0; transform:translateY(5px); } }
    ::view-transition-old(root) { animation:90ms ease-out both vt-old; }
    ::view-transition-new(root) { animation:220ms cubic-bezier(.2,.8,.2,1) both vt-new; }

    @keyframes page-enter {
        from { opacity:0.72; filter:blur(1px); }
        to { opacity:1; filter:blur(0); }
    }
    @keyframes module-enter {
        from { opacity:0; transform:translateY(8px); filter:blur(1.5px); }
        to { opacity:1; transform:translateY(0); filter:blur(0); }
    }
    .stApp { animation:page-enter 200ms ease-out both; }
    .active-module-banner,.system-overview-note,.decision-flow-card,.cfo-decision-panel,.cfo-change-panel,.intelligence-dock {
        animation:module-enter 260ms cubic-bezier(.2,.8,.2,1) both;
    }
    .executive-delta {
        display:flex; align-items:center; gap:.42rem; margin-top:.68rem; color:#9cecff;
        font-family:"Cascadia Mono",Consolas,monospace; font-size:.70rem; font-weight:700;
    }
    .executive-context { margin-top:.35rem; color:#6f98a7; font-size:.70rem; line-height:1.4; }
    .cfo-change-panel,.cfo-decision-panel {
        position:relative; min-width:0; min-height:410px; padding:1rem 1rem .9rem;
        background:linear-gradient(145deg,rgba(5,27,40,.95),rgba(2,14,23,.86));
        border:1px solid rgba(82,231,255,.18);
        clip-path:polygon(0 0,calc(100% - 13px) 0,100% 13px,100% 100%,0 100%);
    }
    .cfo-panel-kicker { color:#52e7ff; font:700 .56rem "Cascadia Mono",Consolas,monospace; letter-spacing:.16em; text-transform:uppercase; margin-bottom:.22rem; }
    .cfo-panel-title { color:#effdff; font-size:1rem; font-weight:700; margin-bottom:.8rem; }
    .change-row { display:block; text-decoration:none; color:inherit; padding:.84rem 0; border-top:1px solid rgba(82,231,255,.10); transition:transform 160ms ease; }
    .change-row:first-of-type { border-top:0; }
    .change-row:hover { transform:translateX(4px); }
    .change-row-head { display:flex; justify-content:space-between; gap:.6rem; align-items:baseline; }
    .change-name { color:#dff9ff; font-size:.80rem; font-weight:700; }
    .change-value { color:#52e7ff; font:750 .75rem "Cascadia Mono",Consolas,monospace; white-space:nowrap; }
    .change-detail { margin-top:.30rem; color:#7399a7; font-size:.68rem; line-height:1.45; }
    .decision-lens-item { padding:.78rem 0 .82rem; border-top:1px solid rgba(82,231,255,.10); }
    .decision-lens-item:first-of-type { border-top:0; }
    .decision-lens-title { color:#e9fbff; font-size:.78rem; font-weight:700; margin-bottom:.45rem; }
    .decision-lens-line { display:grid; grid-template-columns:50px 1fr; gap:.48rem; margin:.22rem 0; font-size:.66rem; line-height:1.42; }
    .decision-lens-label { color:#52e7ff; font:700 .55rem "Cascadia Mono",Consolas,monospace; letter-spacing:.08em; text-transform:uppercase; }
    .decision-lens-copy { color:#8db0bc; }
    .decision-flow-card { position:relative; padding:1rem 1.05rem; margin-bottom:.72rem; background:linear-gradient(145deg,rgba(7,31,44,.92),rgba(3,17,27,.82)); border:1px solid rgba(82,231,255,.14); clip-path:polygon(0 0,calc(100% - 12px) 0,100% 12px,100% 100%,0 100%); }
    .flow-title { color:#edfaff; font-size:.88rem; font-weight:700; margin-bottom:.62rem; }
    .flow-grid { display:grid; grid-template-columns:repeat(4,minmax(0,1fr)); gap:.48rem; }
    .flow-cell { padding:.58rem .62rem; background:rgba(82,231,255,.025); border:1px solid rgba(82,231,255,.08); min-width:0; }
    .flow-label { display:block; color:#52e7ff; font:700 .52rem "Cascadia Mono",Consolas,monospace; letter-spacing:.10em; text-transform:uppercase; margin-bottom:.28rem; }
    .flow-copy { color:#93b5c0; font-size:.68rem; line-height:1.42; }
    .decision-strip { display:grid; grid-template-columns:repeat(4,minmax(0,1fr)); gap:.72rem; margin:0 0 1rem; }
    .decision-strip-item { padding:.85rem .92rem; background:rgba(82,231,255,.025); border:1px solid rgba(82,231,255,.11); }
    .decision-strip-item strong { display:block; color:#e9fbff; font-size:.83rem; margin:.20rem 0 .28rem; }
    .decision-strip-item span:last-child { color:#789eab; font-size:.68rem; line-height:1.42; }
    .dock-metric { line-height:1.35; }
    .intelligence-dock { max-width:920px; margin-left:auto; margin-right:auto; }
    .dock-actions { gap:.85rem; }
    .dock-action { padding:1rem 1.1rem; min-height:78px; }

    .comparison-basis {
        display:flex; flex-wrap:wrap; gap:.45rem; margin:-.15rem 0 1rem;
    }
    .comparison-chip {
        display:inline-flex; align-items:center; gap:.35rem; padding:.30rem .55rem;
        color:#7fa8b5; background:rgba(82,231,255,.025); border:1px solid rgba(82,231,255,.10);
        font:700 .54rem "Cascadia Mono",Consolas,monospace; letter-spacing:.07em; text-transform:uppercase;
    }
    .comparison-chip strong { color:#bfeef7; font-weight:750; }

    .copilot-action {
        display:inline-flex; align-items:center; gap:.35rem; margin-top:.55rem; padding:.34rem .52rem;
        color:#8eeaff !important; background:rgba(82,231,255,.045); border:1px solid rgba(82,231,255,.18);
        text-decoration:none !important; font:750 .55rem "Cascadia Mono",Consolas,monospace; letter-spacing:.06em; text-transform:uppercase;
        transition:transform 150ms ease, border-color 150ms ease, background 150ms ease, box-shadow 150ms ease;
    }
    .copilot-action:hover {
        transform:translateX(2px); background:rgba(82,231,255,.09); border-color:rgba(82,231,255,.42);
        box-shadow:0 0 18px rgba(82,231,255,.09); color:#e5fcff !important;
    }


    .forward-lens-panel {
        position:relative; padding:1.05rem 1.05rem 1rem;
        background:linear-gradient(145deg,rgba(7,31,44,.92),rgba(3,17,27,.84));
        border:1px solid rgba(82,231,255,.15);
        clip-path:polygon(0 0,calc(100% - 14px) 0,100% 14px,100% 100%,0 100%);
    }
    .forward-lens-kicker {
        color:#52e7ff; font:750 .55rem "Cascadia Mono",Consolas,monospace;
        letter-spacing:.14em; text-transform:uppercase; margin-bottom:.28rem;
    }
    .forward-lens-title {
        color:#effdff; font-size:1rem; font-weight:720; margin-bottom:.75rem;
    }
    .forward-lens-row {
        display:grid; grid-template-columns:92px 1fr; gap:.72rem; align-items:start;
        padding:.70rem 0; border-top:1px solid rgba(82,231,255,.09);
    }
    .forward-lens-row:first-of-type { border-top:0; }
    .forward-lens-label {
        color:#52e7ff; font:750 .54rem "Cascadia Mono",Consolas,monospace;
        letter-spacing:.08em; text-transform:uppercase;
    }
    .forward-lens-value {
        color:#8fb2be; font-size:.72rem; line-height:1.48;
    }
    .forward-lens-value strong { color:#e6fbff; font-weight:720; }
    .forward-lens-meaning {
        margin-top:.85rem; padding:.78rem .82rem;
        background:rgba(82,231,255,.035); border:1px solid rgba(82,231,255,.10);
        color:#9fc1cb; font-size:.70rem; line-height:1.48;
    }
    .forward-lens-meaning strong {
        display:block; margin-bottom:.25rem; color:#dff9ff;
        font:750 .56rem "Cascadia Mono",Consolas,monospace;
        letter-spacing:.08em; text-transform:uppercase;
    }
    .module-action-row {
        display:flex; gap:.75rem; flex-wrap:wrap; margin-top:.85rem;
    }
    .module-action-link {
        flex:0 1 320px; display:flex; align-items:center; justify-content:center;
        min-height:44px; padding:.72rem 1rem; text-decoration:none !important;
        color:#d9f9ff !important;
        background:linear-gradient(90deg,rgba(13,92,116,.58),rgba(6,49,69,.42));
        border:1px solid rgba(82,231,255,.34);
        clip-path:polygon(0 0,calc(100% - 11px) 0,100% 11px,100% 100%,11px 100%,0 calc(100% - 11px));
        font-size:.78rem; font-weight:650; letter-spacing:.02em;
        transition:transform 160ms ease,box-shadow 160ms ease,border-color 160ms ease;
    }
    .module-action-link:hover {
        transform:translateY(-2px); border-color:rgba(82,231,255,.70);
        box-shadow:0 0 24px rgba(82,231,255,.11);
    }
    .scenario-impact-grid {
        display:grid; grid-template-columns:repeat(3,minmax(0,1fr));
        gap:.65rem; margin:.75rem 0 1rem;
    }
    .scenario-impact-cell {
        padding:.78rem .82rem; background:rgba(82,231,255,.025);
        border:1px solid rgba(82,231,255,.10);
    }
    .scenario-impact-label {
        color:#52e7ff; font:750 .52rem "Cascadia Mono",Consolas,monospace;
        letter-spacing:.08em; text-transform:uppercase;
    }
    .scenario-impact-value {
        margin-top:.28rem; color:#edfaff;
        font:700 .88rem "Cascadia Mono",Consolas,monospace;
    }
    .scenario-impact-copy {
        margin-top:.22rem; color:#749aa8; font-size:.65rem; line-height:1.4;
    }
    .scenario-decision-card {
        margin-top:.85rem; padding:1rem 1.05rem;
        background:linear-gradient(145deg,rgba(7,31,44,.90),rgba(3,17,27,.82));
        border:1px solid rgba(82,231,255,.14);
    }
    .scenario-decision-line {
        display:grid; grid-template-columns:68px 1fr; gap:.6rem;
        padding:.36rem 0; font-size:.70rem; line-height:1.45;
    }
    .scenario-decision-line span:first-child {
        color:#52e7ff; font:750 .53rem "Cascadia Mono",Consolas,monospace;
        letter-spacing:.07em; text-transform:uppercase;
    }
    .scenario-decision-line span:last-child { color:#8fb1bd; }

    .news-section-head {
        display:flex; align-items:flex-end; justify-content:space-between; gap:1rem; margin-bottom:.75rem;
    }
    .news-section-copy { color:#668e9d; font-size:.68rem; line-height:1.4; max-width:320px; text-align:right; }
    .news-card {
        position:relative; padding:1rem 1.05rem .95rem; margin-bottom:.72rem; overflow:hidden;
        background:linear-gradient(105deg,rgba(8,31,44,.95),rgba(4,17,27,.80));
        border:1px solid rgba(82,231,255,.14); border-left:2px solid rgba(82,231,255,.60);
        clip-path:polygon(0 0,calc(100% - 12px) 0,100% 12px,100% 100%,0 100%);
    }
    .news-card::after {
        content:""; position:absolute; right:-32px; top:-32px; width:90px; height:90px; border-radius:50%;
        border:1px solid rgba(82,231,255,.09); box-shadow:0 0 0 12px rgba(82,231,255,.018),0 0 0 24px rgba(82,231,255,.010);
    }
    .news-topline { display:flex; align-items:center; gap:.5rem; margin-bottom:.42rem; }
    .news-badge {
        display:inline-flex; align-items:center; gap:.30rem; padding:.20rem .42rem; color:#051219; background:#52e7ff;
        font:850 .50rem "Cascadia Mono",Consolas,monospace; letter-spacing:.10em; text-transform:uppercase;
    }
    .news-meta { color:#668f9f; font:700 .55rem "Cascadia Mono",Consolas,monospace; letter-spacing:.07em; text-transform:uppercase; }
    .news-headline { color:#edfaff; font-size:.86rem; font-weight:720; line-height:1.38; margin-bottom:.52rem; }
    .news-context-grid { display:grid; grid-template-columns:1fr; gap:.28rem; }
    .news-context-line { display:grid; grid-template-columns:82px 1fr; gap:.45rem; font-size:.72rem; line-height:1.4; }
    .news-context-label { color:#52e7ff; font:700 .52rem "Cascadia Mono",Consolas,monospace; letter-spacing:.07em; text-transform:uppercase; }
    .news-context-copy { color:#82a7b4; }
    .news-footer { display:flex; align-items:center; justify-content:space-between; gap:.75rem; margin-top:.58rem; }
    .news-source-link { color:#8eeaff !important; text-decoration:none !important; font:750 .57rem "Cascadia Mono",Consolas,monospace; text-transform:uppercase; letter-spacing:.06em; }
    .news-source-link:hover { color:#e5fcff !important; text-shadow:0 0 10px rgba(82,231,255,.4); }
    .news-public-note { color:#4f7786; font:650 .50rem "Cascadia Mono",Consolas,monospace; letter-spacing:.05em; text-transform:uppercase; }

    @media (max-width:1100px) { .flow-grid,.decision-strip { grid-template-columns:repeat(2,minmax(0,1fr)); } .news-section-head{align-items:flex-start;flex-direction:column;} .news-section-copy{text-align:left;} }
    @media (max-width:760px) { .flow-grid,.decision-strip { grid-template-columns:1fr; } .news-context-line{grid-template-columns:1fr;} }
</style>\n"""


# Overrides for this cockpit. Emitted after the three reference blocks so it
# wins on equal specificity.
LOCAL_CSS = """
<style>
    /* News is a fourth intelligence vector, so the dock grows from 3 to 4. */
    .dock-actions {
        grid-template-columns: repeat(4, minmax(0, 1fr));
        max-width: 980px;
    }

    @media (max-width: 1180px) {
        .dock-actions { grid-template-columns: repeat(2, minmax(0, 1fr)); }
    }

    @media (max-width: 700px) {
        .dock-actions { grid-template-columns: 1fr; }
    }

    /* -------------------------------------------------
       GREETING GATE
       The cockpit's front door: a name, and one control.
       ------------------------------------------------- */

    .cockpit-gate {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        gap: 2.6rem;
        min-height: 78vh;
        padding: 3rem 1.5rem;
        text-align: center;
    }

    .gate-kicker {
        display: flex;
        align-items: center;
        gap: 0.7rem;
        color: #52e7ff;
        font-family: "Cascadia Mono", Consolas, monospace;
        font-size: 0.62rem;
        font-weight: 780;
        letter-spacing: 0.26em;
        text-transform: uppercase;
    }

    .gate-kicker::before,
    .gate-kicker::after {
        content: "";
        width: 54px;
        height: 1px;
        background: linear-gradient(90deg, transparent, rgba(82, 231, 255, 0.55));
    }

    .gate-kicker::after {
        background: linear-gradient(90deg, rgba(82, 231, 255, 0.55), transparent);
    }

    .gate-greeting {
        margin: 0;
        color: #f2fdff;
        font-size: clamp(2.1rem, 5.4vw, 4.6rem);
        font-weight: 300;
        line-height: 1;
        letter-spacing: -0.045em;
        text-shadow: 0 0 38px rgba(82, 231, 255, 0.16);
    }

    .gate-greeting strong {
        color: var(--cyan);
        font-weight: 780;
        letter-spacing: 0.01em;
    }

    /* Same construction as the dial's core, sized to stand on its own. */
    .gate-orb {
        position: relative;
        display: grid;
        place-items: center;
        width: clamp(190px, 21vw, 250px);
        aspect-ratio: 1;
        overflow: hidden;
        color: #eaffff !important;
        border: 1px solid rgba(115, 231, 249, 0.66);
        border-radius: 50%;
        outline: none;
        background:
            radial-gradient(circle at 50% 45%, rgba(32, 126, 154, 0.40), transparent 30%),
            radial-gradient(circle, #0b3c50 0, #062636 46%, #020f18 75%);
        box-shadow:
            inset 0 0 34px rgba(68, 224, 255, 0.16),
            0 0 0 8px rgba(5, 31, 43, 0.82),
            0 0 0 9px rgba(82, 231, 255, 0.28),
            0 0 42px rgba(82, 231, 255, 0.20);
        text-decoration: none !important;
        transition:
            transform 220ms cubic-bezier(.2, .8, .2, 1),
            filter 190ms ease,
            border-color 190ms ease;
    }

    .gate-orb::before {
        content: "";
        position: absolute;
        inset: 5%;
        border: 1px dashed rgba(115, 231, 249, 0.40);
        border-radius: 50%;
        animation: rotate-cw 24s linear infinite;
    }

    .gate-orb::after {
        content: "";
        position: absolute;
        inset: 14%;
        border: 2px solid transparent;
        border-top-color: rgba(162, 243, 255, 0.92);
        border-right-color: rgba(108, 208, 255, 0.36);
        border-radius: 50%;
        box-shadow: inset 0 0 18px rgba(82, 231, 255, 0.07);
        animation: rotate-ccw 12s linear infinite;
    }

    .gate-orb:hover,
    .gate-orb:focus-visible {
        border-color: #e0fbff;
        transform: scale(1.06);
        filter: brightness(1.22) drop-shadow(0 0 16px rgba(82, 231, 255, 0.68));
    }

    .gate-orb:focus-visible {
        box-shadow:
            0 0 0 2px #e0fbff,
            0 0 36px rgba(82, 231, 255, 0.34);
    }

    /* The dial sizes its core copy off the viewport; here it is fixed. */
    .gate-orb .core-code-html { font-size: 0.50rem; }
    .gate-orb .core-main-html { font-size: 1.16rem; letter-spacing: 0.10em; }
    .gate-orb .core-online-html { font-size: 0.48rem; }
    .gate-orb .core-copy-html { gap: 0.34rem; }

    /* -------------------------------------------------
       HERO — COMPACT
       The hero states where and when; the dial does the explaining.
       ------------------------------------------------- */

    .hud-hero {
        display: block;
        min-height: 0;
        padding: 1.35rem 1.75rem 1.45rem;
        margin-bottom: 1.05rem;
    }

    .hud-hero::after { inset: 8px; }

    .hero-title { font-size: clamp(1.75rem, 3.1vw, 2.95rem); }

    .hero-status-row { margin-top: 0.95rem; }

    .weather-pill {
        gap: 0.5rem;
        border-color: rgba(82, 231, 255, 0.30);
        background: rgba(82, 231, 255, 0.085);
        text-transform: none;
        letter-spacing: 0.045em;
    }

    .weather-glyph {
        color: #9df0ff;
        font-size: 0.92rem;
        line-height: 1;
        text-shadow: 0 0 10px rgba(82, 231, 255, 0.55);
    }

    @media (max-width: 900px) {
        .hud-hero { padding: 1.15rem 1.25rem 1.25rem; }
    }
</style>
"""
