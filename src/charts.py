"""Chart generation. Everything is saved to charts/ as PNG."""

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from . import analysis

COLORS = {"win": "#4caf50", "loss": "#e53935", "draw": "#9e9e9e"}


def save_all(df, outdir="charts"):
    rating_chart(df, f"{outdir}/rating_over_time.png")
    openings_chart(df, f"{outdir}/openings.png")
    time_control_chart(df, f"{outdir}/time_controls.png")
    hour_chart(df, f"{outdir}/games_by_hour.png")
    color_chart(df, f"{outdir}/winrate_by_color.png")


def rating_chart(df, path):
    fig, ax = plt.subplots(figsize=(10, 5))
    for tc in df["time_control"].unique():
        series = analysis.rating_over_time(df, tc)
        if len(series) < 20:
            continue
        ax.plot(series.index, series.values, label=tc, linewidth=1.2)
    ax.set_title("Rating over time")
    ax.set_ylabel("Rating")
    ax.legend()
    ax.grid(alpha=0.3)
    fig.tight_layout()
    fig.savefig(path, dpi=120)
    plt.close(fig)


def openings_chart(df, path):
    data = analysis.winrate_by_opening(df)
    fig, ax = plt.subplots(figsize=(10, 6))
    bars = ax.barh(data.index[::-1], data["win_rate"][::-1], color="#5c6bc0")
    ax.axvline(50, color="#e53935", linestyle="--", linewidth=1, label="50%")
    ax.set_title("Win rate by opening (most played)")
    ax.set_xlabel("Win rate (%)")
    for bar, n in zip(bars, data["games"][::-1]):
        ax.text(bar.get_width() + 0.5, bar.get_y() + bar.get_height() / 2,
                f"{n} games", va="center", fontsize=8, color="#666")
    ax.legend()
    fig.tight_layout()
    fig.savefig(path, dpi=120)
    plt.close(fig)


def time_control_chart(df, path):
    data = analysis.winrate_by_time_control(df)
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.bar(data.index, data["win_rate"], color="#26a69a")
    ax.axhline(50, color="#e53935", linestyle="--", linewidth=1)
    ax.set_title("Win rate by time control")
    ax.set_ylabel("Win rate (%)")
    for i, (n, wr) in enumerate(zip(data["games"], data["win_rate"])):
        ax.text(i, wr + 1, f"{n} games", ha="center", fontsize=8, color="#666")
    fig.tight_layout()
    fig.savefig(path, dpi=120)
    plt.close(fig)


def hour_chart(df, path):
    data = analysis.games_by_hour(df)
    fig, ax = plt.subplots(figsize=(10, 4))
    ax.bar(data.index, data.values, color="#7e57c2")
    ax.set_title("When do I play? (games by hour of day)")
    ax.set_xlabel("Hour")
    ax.set_ylabel("Games")
    ax.set_xticks(range(0, 24))
    fig.tight_layout()
    fig.savefig(path, dpi=120)
    plt.close(fig)


def color_chart(df, path):
    data = analysis.winrate_by_color(df)
    fig, ax = plt.subplots(figsize=(6, 5))
    ax.bar(data.index, data.values, color=["#424242", "#bdbdbd"])
    ax.axhline(50, color="#e53935", linestyle="--", linewidth=1)
    ax.set_title("Win rate by color")
    ax.set_ylabel("Win rate (%)")
    fig.tight_layout()
    fig.savefig(path, dpi=120)
    plt.close(fig)
