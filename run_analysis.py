"""Entry point: load a games CSV, print a summary and generate all charts.

    python run_analysis.py data/sample_games.csv
"""

import sys

from src import analysis, charts


def main():
    path = sys.argv[1] if len(sys.argv) > 1 else "data/sample_games.csv"
    df = analysis.load_games(path)

    stats = analysis.overall_stats(df)
    print(f"\n=== {path} ===")
    print(f"Games:        {stats['games']}")
    print(f"Record:       {stats['wins']}W / {stats['losses']}L / {stats['draws']}D")
    print(f"Win rate:     {stats['win_rate']}%")
    print(f"Rating:       {stats['current_rating']} (peak {stats['peak_rating']})")
    print(f"Avg opponent: {stats['avg_opponent']}")

    tilt = analysis.tilt_check(df)
    if tilt:
        print(f"\nTilt check:")
        print(f"  loss rate after a loss: {tilt['loss_rate_after_loss']}%")
        print(f"  loss rate after a win:  {tilt['loss_rate_after_win']}%")
        diff = tilt['loss_rate_after_loss'] - tilt['loss_rate_after_win']
        if diff > 5:
            print(f"  -> I lose {diff:.0f} points more often right after losing. Take a break.")

    charts.save_all(df)
    print("\nCharts saved to charts/")


if __name__ == "__main__":
    main()
