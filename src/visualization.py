"""Visualization helpers.

Keep charts simple and readable for GitHub screenshots and portfolio presentation.
"""

from __future__ import annotations

from pathlib import Path
import matplotlib.pyplot as plt


def save_current_figure(path: str | Path, dpi: int = 150) -> None:
    """Save current matplotlib figure and create parent folders if needed."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    plt.tight_layout()
    plt.savefig(path, dpi=dpi, bbox_inches="tight")
