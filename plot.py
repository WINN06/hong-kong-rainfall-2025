# /// script
# requires-python = ">=3.10"
# dependencies = ["matplotlib"]
# ///

"""Turn the cached daily rainfall data into a month-by-day calendar picture.

Run with:

    uv run plot.py
"""

import calendar
import json
from datetime import date
from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap, PowerNorm
from matplotlib.patches import Rectangle


FILE = "open-meteo-hong-kong-daily-rainfall-2025.json"
PICTURE = "hong-kong-rainfall-2025.png"

HERE = Path(__file__).parent
DATA = HERE / "data" / FILE
OUT = HERE / "out"

PAPER = "#f8f5ef"
INK = "#16343d"
MUTED = "#66767a"
ACCENT = "#e47a45"
RAIN_COLOURS = ["#f4f2e8", "#b7ded8", "#57a6ad", "#1f6b83", "#123b5d"]


def load_rainfall(path):
    """Return (date, rainfall) pairs and the unit declared by the source."""
    payload = json.loads(path.read_text(encoding="utf-8"))
    daily = payload["daily"]
    dates = daily["time"]
    amounts = daily["precipitation_sum"]
    unit = payload["daily_units"]["precipitation_sum"]

    if len(dates) != len(amounts):
        raise ValueError("The source contains different numbers of dates and values")

    records = []
    for day_text, amount in zip(dates, amounts):
        if amount is not None:
            records.append((date.fromisoformat(day_text), float(amount)))
    if not records:
        raise ValueError("No usable rainfall values were found")
    return records, unit


def arrange_by_month(records):
    """Place daily values in a 12 by 31 grid and total each month."""
    grid = [[float("nan") for _ in range(31)] for _ in range(12)]
    monthly_totals = [0.0 for _ in range(12)]

    for day, amount in records:  # the visible loop over every measurement
        grid[day.month - 1][day.day - 1] = amount
        monthly_totals[day.month - 1] += amount
    return grid, monthly_totals


def draw(records, unit, output_path):
    """Draw and save the final heatmap and monthly summary."""
    grid, monthly_totals = arrange_by_month(records)
    total = sum(amount for _, amount in records)
    wettest = max(records, key=lambda item: item[1])
    top_five = sorted(records, key=lambda item: item[1], reverse=True)[:5]
    top_five_share = sum(amount for _, amount in top_five) / total * 100

    cmap = LinearSegmentedColormap.from_list("rain", RAIN_COLOURS)
    cmap.set_bad("#e5e1d8")
    norm = PowerNorm(gamma=0.55, vmin=0, vmax=wettest[1])

    fig = plt.figure(figsize=(14, 7.4), facecolor=PAPER)
    layout = fig.add_gridspec(
        1,
        2,
        left=0.08,
        right=0.94,
        top=0.76,
        bottom=0.19,
        width_ratios=(4.4, 1.25),
        wspace=0.24,
    )
    heat = fig.add_subplot(layout[0, 0])
    totals = fig.add_subplot(layout[0, 1], sharey=heat)

    image = heat.imshow(grid, cmap=cmap, norm=norm, aspect="auto")
    heat.set_facecolor(PAPER)
    heat.set_xticks(range(0, 31, 5), labels=range(1, 32, 5))
    heat.set_yticks(range(12), labels=[calendar.month_abbr[i] for i in range(1, 13)])
    heat.tick_params(axis="both", colors=INK, length=0, pad=8, labelsize=10)
    heat.xaxis.tick_top()
    heat.xaxis.set_label_position("top")
    heat.set_xlabel("DAY OF MONTH", color=MUTED, fontsize=9, labelpad=12, fontweight="bold")
    heat.set_xticks([x - 0.5 for x in range(1, 31)], minor=True)
    heat.set_yticks([y - 0.5 for y in range(1, 12)], minor=True)
    heat.grid(which="minor", color=PAPER, linewidth=1.1)
    heat.tick_params(which="minor", bottom=False, left=False)
    for spine in heat.spines.values():
        spine.set_visible(False)

    for rank, (heavy_day, _) in enumerate(top_five, start=1):
        heavy_x = heavy_day.day - 1
        heavy_y = heavy_day.month - 1
        heat.add_patch(
            Rectangle(
                (heavy_x - 0.48, heavy_y - 0.48),
                0.96,
                0.96,
                fill=False,
                edgecolor=ACCENT,
                linewidth=2.5 if rank == 1 else 1.8,
            )
        )

    wettest_day, wettest_amount = wettest
    x = wettest_day.day - 1
    y = wettest_day.month - 1
    label_offset = (-105, -42) if wettest_day.day > 20 else (35, -42)
    heat.annotate(
        f"wettest of five\n{wettest_day:%d %b} · {wettest_amount:.1f} {unit}",
        xy=(x, y),
        xytext=label_offset,
        textcoords="offset points",
        color=INK,
        fontsize=9,
        fontweight="bold",
        arrowprops={"arrowstyle": "-", "color": ACCENT, "linewidth": 1.4},
    )

    bar_colours = [cmap(norm(value)) for value in monthly_totals]
    totals.barh(range(12), monthly_totals, color=bar_colours, height=0.66)
    totals.set_xlim(0, max(monthly_totals) * 1.23)
    totals.tick_params(axis="y", left=False, labelleft=False)
    totals.tick_params(axis="x", colors=INK, length=0, pad=8, labelsize=9)
    totals.xaxis.tick_top()
    totals.xaxis.set_label_position("top")
    totals.set_xlabel("MONTHLY TOTAL (MM)", color=MUTED, fontsize=9, labelpad=12, fontweight="bold")
    totals.grid(axis="x", color="#d9d5cd", linewidth=0.8)
    totals.set_axisbelow(True)
    totals.set_facecolor(PAPER)
    for month, value in enumerate(monthly_totals):
        totals.text(value + max(monthly_totals) * 0.025, month, f"{value:.0f}", va="center", color=INK, fontsize=9)
    for spine in totals.spines.values():
        spine.set_visible(False)

    colour_bar = fig.colorbar(
        image,
        ax=heat,
        orientation="horizontal",
        fraction=0.055,
        pad=0.12,
        aspect=45,
    )
    colour_bar.outline.set_visible(False)
    colour_bar.ax.tick_params(colors=MUTED, labelsize=8, length=0)
    colour_bar.set_label(f"DAILY PRECIPITATION ({unit.upper()})", color=MUTED, fontsize=8, labelpad=7)

    fig.text(
        0.08,
        0.925,
        "Hong Kong’s rain arrived in bursts in 2025",
        color=INK,
        fontsize=24,
        fontweight="bold",
    )
    fig.text(
        0.08,
        0.865,
        f"The five wettest days supplied {top_five_share:.0f}% of the year’s {total:,.0f} {unit}; "
        "most winter days stayed dry.",
        color=MUTED,
        fontsize=12,
    )
    fig.text(
        0.08,
        0.055,
        "Each square is one day. Orange outlines mark the five wettest days; grey squares are dates that do not exist.",
        color=MUTED,
        fontsize=9,
    )
    fig.text(
        0.94,
        0.055,
        "Source: Open-Meteo Historical Weather API · 22.32°N, 114.17°E",
        color=MUTED,
        fontsize=9,
        ha="right",
    )

    OUT.mkdir(exist_ok=True)
    fig.savefig(output_path, dpi=180, facecolor=fig.get_facecolor())
    plt.close(fig)
    return total, wettest, top_five_share


def main():
    records, unit = load_rainfall(DATA)
    total, wettest, share = draw(records, unit, OUT / PICTURE)
    print(
        f"{DATA.name}: {len(records)} daily values, {records[0][0]} to {records[-1][0]}"
    )
    print(f"annual total: {total:.1f} {unit}")
    print(f"wettest day: {wettest[0]} ({wettest[1]:.1f} {unit})")
    print(f"five wettest days: {share:.1f}% of the annual total")
    print(f"saved out/{PICTURE}")


if __name__ == "__main__":
    main()

