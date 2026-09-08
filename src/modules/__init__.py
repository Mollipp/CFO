"""One renderer per navigable cockpit vector."""

from src.modules.brief import render_brief
from src.modules.copilot import render_copilot
from src.modules.horizon import render_horizon
from src.modules.news import render_news
from src.modules.peers import render_peers
from src.modules.scenario import render_scenario
from src.modules.strategy import render_strategy
from src.modules.treasury import render_treasury

# Maps the ``module`` query parameter to its renderer. "home" has no renderer;
# the shell shows the overview note instead.
RENDERERS = {
    "brief": render_brief,
    "horizon": render_horizon,
    "scenario": render_scenario,
    "treasury": render_treasury,
    "peers": render_peers,
    "strategy": render_strategy,
    "news": render_news,
    "copilot": render_copilot,
}

# Title and one-line description shown in the active-module banner.
MODULE_METADATA = {
    "home": (
        "CFO overview",
        "Current state, changes and next investigations",
    ),
    "brief": (
        "Module 01 / Morning Brief",
        "What changed, why it matters and what to investigate next",
    ),
    "horizon": (
        "Module 02 / Horizon",
        "Deterministic run-rate outlook from the certified actuals",
    ),
    "scenario": (
        "Module 03 / What-If Engine",
        "Governed balance-sheet shock simulation",
    ),
    "copilot": (
        "Module 04 / CFO Copilot",
        "Conversational investigation over governed finance data",
    ),
    "treasury": (
        "Intelligence 05 / Treasury",
        "Portfolio sensitivity, scenario impacts and hedge alternatives",
    ),
    "peers": (
        "Intelligence 06 / Peers",
        "Directional European peer positioning and performance comparison",
    ),
    "strategy": (
        "Intelligence 07 / Strategy",
        "Strategic opportunity radar and capability-gap intelligence",
    ),
    "news": (
        "Intelligence 08 / News",
        "Overnight external developments and their potential bank impact",
    ),
}

__all__ = ["RENDERERS", "MODULE_METADATA"]
