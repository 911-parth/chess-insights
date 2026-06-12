"""Download games for a Lichess user and save them as a CSV.

Usage:
    python src/fetch_games.py <username> [max_games]

The Lichess export API is free and doesn't need a token for public games.
Docs: https://lichess.org/api#tag/Games/operation/apiGamesUser
"""

import csv
import json
import sys

import requests

API_URL = "https://lichess.org/api/games/user/{user}"

FIELDS = [
    "date", "time_control", "color", "opponent", "opponent_rating",
    "my_rating", "result", "opening", "moves_count", "termination",
]


def fetch_games(username, max_games=1000):
    params = {
        "max": max_games,
        "opening": "true",
        "moves": "false",
        "pgnInJson": "false",
    }
    headers = {"Accept": "application/x-ndjson"}
    resp = requests.get(
        API_URL.format(user=username),
        params=params,
        headers=headers,
        stream=True,
        timeout=60,
    )
    resp.raise_for_status()

    games = []
    for line in resp.iter_lines():
        if not line:
            continue
        games.append(parse_game(json.loads(line), username))
    return games


def parse_game(g, username):
    me_is_white = g["players"]["white"].get("user", {}).get("name", "").lower() == username.lower()
    me = g["players"]["white" if me_is_white else "black"]
    opp = g["players"]["black" if me_is_white else "white"]

    winner = g.get("winner")  # "white", "black" or missing on draws
    if winner is None:
        result = "draw"
    elif (winner == "white") == me_is_white:
        result = "win"
    else:
        result = "loss"

    return {
        "date": g["createdAt"] // 1000,  # epoch ms -> s, formatted later
        "time_control": g.get("speed", "unknown"),
        "color": "white" if me_is_white else "black",
        "opponent": opp.get("user", {}).get("name", "anonymous"),
        "opponent_rating": opp.get("rating", ""),
        "my_rating": me.get("rating", ""),
        "result": result,
        "opening": g.get("opening", {}).get("name", "Unknown"),
        "moves_count": len(g.get("moves", "").split()) if g.get("moves") else "",
        "termination": g.get("status", ""),
    }


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)
    username = sys.argv[1]
    max_games = int(sys.argv[2]) if len(sys.argv) > 2 else 1000

    print(f"Fetching up to {max_games} games for {username}...")
    games = fetch_games(username, max_games)
    print(f"Got {len(games)} games.")

    out = "data/my_games.csv"
    with open(out, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(games)
    print(f"Saved to {out}")
    print("Now run: python run_analysis.py data/my_games.csv")


if __name__ == "__main__":
    main()
