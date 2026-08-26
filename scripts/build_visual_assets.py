#!/usr/bin/env python3
"""Render portfolio figures directly from reconciled project evidence."""

from __future__ import annotations

import json
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "images"
DATA = json.loads((ROOT / "analysis" / "executive_summary.json").read_text())
S, F = DATA["summary"], DATA["findings"]
BG, SURFACE, TEXT, MUTED, GOLD, BLUE, RED, GREEN = "#11161a", "#171e22", "#edece8", "#a3acae", "#d0ac76", "#88a8bf", "#da8578", "#94b99f"
plt.rcParams.update({"font.family": "DejaVu Sans"})


def frame(kicker: str, title: str, subtitle: str):
    fig, ax = plt.subplots(figsize=(16, 9), facecolor=BG)
    ax.set_facecolor(BG)
    ax.set_xlim(0, 16)
    ax.set_ylim(0, 9)
    ax.axis("off")
    ax.text(.78, 8.15, kicker.upper(), color=GOLD, fontsize=11, weight="bold")
    ax.text(.78, 7.35, title, color=TEXT, fontsize=30, weight="bold")
    ax.text(.81, 6.88, subtitle, color=MUTED, fontsize=11.5)
    ax.text(.81, .44, "Independent portfolio project · Zivan Devitt · Fictional company and data", color="#788286", fontsize=9)
    return fig, ax


def save(fig, filename: str) -> None:
    fig.savefig(OUT / filename, dpi=140, bbox_inches="tight", facecolor=BG)
    plt.close(fig)


def hero() -> None:
    fig, ax = frame("Morrowfield / The Availability Gap", "99.2% available. So where did R685k go?", "A healthy national figure concealed a narrow supplier, store and product problem.")
    cards = [("CHAIN-WIDE AVAILABILITY", f"{S['availability_pct'] * 100:.1f}%", "Above the 94% operating target"), ("ESTIMATED MISSED SALES", f"R{S['estimated_lost_sales'] / 1000:.1f}k", "Modelled tracked-range exposure"), ("LEAD SUPPLIER SHARE", f"{F['top_supplier_lost_sales_share'] * 100:.1f}%", F["top_supplier_name"])]
    for idx, (label, value, note) in enumerate(cards):
        x = .86 + idx * 5.05
        ax.add_patch(plt.Rectangle((x, 4.17), 4.66, 1.85, facecolor=SURFACE, edgecolor="#30383c", linewidth=.9))
        ax.text(x + .22, 5.66, label, color=MUTED, fontsize=9)
        ax.text(x + .22, 4.92, value, color=GOLD if idx else TEXT, fontsize=29, weight="bold")
        ax.text(x + .22, 4.48, note, color=MUTED, fontsize=9)
    ax.text(.89, 3.35, f"{S['sales_records']:,} sales rows     {S['inventory_records']:,} inventory observations     {S['purchase_orders']:,} supplier orders", color=TEXT, fontsize=12)
    ax.plot([.86, 15.28], [2.86, 2.86], color="#30383c", linewidth=1)
    ax.text(.89, 2.28, "The real assignment", color=GOLD, fontsize=10, weight="bold")
    ax.text(.89, 1.76, "Connect supplier service, store availability, promotions and gross margin — then show management what to fix.", color=MUTED, fontsize=11.2)
    save(fig, "hero-linkedin.png")


def insight() -> None:
    frame_data = pd.read_csv(ROOT / "analysis" / "supplier_performance.csv").head(6)
    fig, ax = frame("Evidence / Supplier concentration", "One supplier explained most of the exposure.", "Purchase-order reliability and stock outcomes are associated; the exact operating cause needs confirmation.")
    maximum = frame_data.estimated_lost_sales.max()
    for index, row in enumerate(frame_data.itertuples(index=False)):
        y = 5.76 - index * .67
        bar_width = 8.25 * float(row.estimated_lost_sales) / maximum
        color = GOLD if index == 0 else BLUE
        ax.text(.82, y + .04, row.SupplierName, color=TEXT if index == 0 else MUTED, fontsize=10, va="center")
        ax.barh(y, bar_width, height=.28, left=5.37, color=color)
        ax.text(5.52 + bar_width, y, f"R{row.estimated_lost_sales / 1000:,.1f}k", color=TEXT, fontsize=9.3, va="center")
    ax.text(.85, 1.25, f"Top supplier share: {F['top_supplier_lost_sales_share'] * 100:.1f}%     Fill rate: {F['top_supplier_fill_rate'] * 100:.1f}%     On-time delivery: {F['top_supplier_on_time_rate'] * 100:.1f}%", color=GOLD, fontsize=12)
    save(fig, "key-insight.png")


def cleaning() -> None:
    quality = pd.read_csv(ROOT / "qa" / "data_quality_log.csv")
    chosen = quality[quality.issue.str.contains("repeated sales|date|whitespace in store|unmapped|keys absent|returns", case=False, regex=True)].head(7)
    fig, ax = frame("Evidence / Source quality", "Clean the source. Keep the judgement.", "Duplicates and invalid keys are handled differently from legitimate returns.")
    y = 5.84
    for index, row in enumerate(chosen.itertuples(index=False)):
        ax.text(.90, y, f"{index + 1:02d}", color=GOLD, fontsize=10, weight="bold")
        label = row.issue if len(row.issue) < 66 else row.issue[:63] + "…"
        ax.text(1.42, y, label, color=TEXT, fontsize=10.5)
        ax.text(13.85, y, f"{int(row.records_affected):,}", color=MUTED, fontsize=10.5, ha="right")
        ax.plot([1.4, 14.0], [y - .20, y - .20], color="#30383c", linewidth=.7)
        y -= .60
    ax.text(.9, 1.09, f"{S['quality_issues']} documented issue types     {S['quarantined_sales_records']} unmapped rows quarantined     {S['return_records']:,} valid returns retained", color=GOLD, fontsize=10.7)
    save(fig, "data-cleaning.png")


def architecture() -> None:
    fig, ax = frame("Evidence / Project architecture", "From raw extract to management decision.", "Each stage has a reviewable source file, explicit business rule and reconciled output.")
    columns = [
        ("SOURCE SYSTEMS", ["Weekly POS sales and returns", "Tracked inventory observations", "Supplier purchase orders", "Store-week sales targets"]),
        ("ANALYTICAL WORK", ["Data quality and controlled cleaning", "Conformed analytical dimensions", "SQL and weighted KPI calculations", "Supplier, SKU and margin diagnosis"]),
        ("MANAGEMENT OUTPUTS", ["Fourteen-sheet Excel workbook", "Seven-page interactive dashboard", "Financial opportunity scenario", "Prioritised action centre"]),
    ]
    for index, (heading, items) in enumerate(columns):
        x = .94 + index * 5.08
        ax.add_patch(plt.Rectangle((x, 2.25), 4.62, 3.68, facecolor=SURFACE, edgecolor="#30383c", linewidth=.9))
        ax.text(x + .21, 5.42, heading, color=GOLD, fontsize=10, weight="bold")
        for j, item in enumerate(items):
            ax.text(x + .21, 4.66 - j * .64, item, color=TEXT if j < 2 else MUTED, fontsize=9.6)
        if index < len(columns) - 1:
            ax.annotate("", xy=(x + 5.00, 4.10), xytext=(x + 4.70, 4.10), arrowprops={"arrowstyle": "->", "color": GOLD, "lw": 1.4})
    ax.text(.97, 1.22, "Excel  /  SQL  /  Power Query  /  Power BI-ready DAX  /  Python  /  SQLite  /  Interactive HTML", color=MUTED, fontsize=10.7)
    save(fig, "tools-architecture.png")


if __name__ == "__main__":
    hero()
    insight()
    cleaning()
    architecture()
    print(json.dumps({"status": "ok", "images": ["hero-linkedin.png", "key-insight.png", "data-cleaning.png", "tools-architecture.png"]}))
