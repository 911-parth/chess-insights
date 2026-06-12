"""Core analysis helpers for chess-insights."""

import pandas as pd


def load_games(path):
    df = pd.read_csv(path)
    df["date"] = pd.to_datetime(df["date"], unit="s")
    df = df.sort_values("date").reset_index(drop=True)
    return df


def overall_stats(df):
    total = len(df)
    wins = (df["result"] == "win").sum()
    losses = (df["result"] == "loss").sum()
    draws = (df["result"] == "draw").sum()
    return {
        "games": total,
        "wins": int(wins),
        "losses": int(losses),
        "draws": int(draws),
        "win_rate": round(100 * wins / total, 1) if total else 0,
        "current_rating": int(df["my_rating"].iloc[-1]),
        "peak_rating": int(df["my_rating"].max()),
        "avg_opponent": int(df["opponent_rating"].mean()),
    }


def winrate_by_opening(df, min_games=10, top=10):
    g = df.groupby("opening").agg(
        games=("result", "size"),
        wins=("result", lambda s: (s == "win").sum()),
    )
    g = g[g["games"] >= min_games]
    g["win_rate"] = (100 * g["wins"] / g["games"]).round(1)
    return g.sort_values("games", ascending=False).head(top)


def winrate_by_color(df):
    return df.groupby("color")["result"].apply(
        lambda s: round(100 * (s == "win").mean(), 1)
    )


def winrate_by_time_control(df):
    g = df.groupby("time_control").agg(
        games=("result", "size"),
        wins=("result", lambda s: (s == "win").sum()),
    )
    g["win_rate"] = (100 * g["wins"] / g["games"]).round(1)
    return g.sort_values("games", ascending=False)


def games_by_hour(df):
    return df["date"].dt.hour.value_counts().sort_index()


def rating_over_time(df, time_control=None):
    sub = df if time_control is None else df[df["time_control"] == time_control]
    return sub.set_index("date")["my_rating"]


def tilt_check(df):
    """How often do I lose right after losing? (revenge games are a trap)"""
    results = df["result"].values
    after_loss = [results[i + 1] for i in range(len(results) - 1) if results[i] == "loss"]
    after_win = [results[i + 1] for i in range(len(results) - 1) if results[i] == "win"]
    if not after_loss or not after_win:
        return None
    loss_after_loss = sum(r == "loss" for r in after_loss) / len(after_loss)
    loss_after_win = sum(r == "loss" for r in after_win) / len(after_win)
    return {
        "loss_rate_after_loss": round(100 * loss_after_loss, 1),
        "loss_rate_after_win": round(100 * loss_after_win, 1),
    }
