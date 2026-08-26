#!/usr/bin/env python3
"""Build the dependency-free report and its independent source-control metrics."""

from __future__ import annotations

import json
import base64
import gzip
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
DASHBOARD = ROOT / "dashboard"
QA = ROOT / "qa"


def expected(region: str | None = None, category: str | None = None) -> dict[str, float | int]:
    stores = pd.read_csv(ROOT / "data" / "clean" / "DimStores.csv")
    products = pd.read_csv(ROOT / "data" / "clean" / "DimProducts.csv")
    sales = pd.read_csv(ROOT / "data" / "clean" / "FactSalesWeekly.csv")
    inventory = pd.read_csv(ROOT / "data" / "clean" / "FactInventoryWeekly.csv")
    targets = pd.read_csv(ROOT / "data" / "clean" / "FactStoreTargets.csv")
    if region:
        approved_stores = set(stores.loc[stores.Region == region, "StoreID"])
        sales = sales[sales.StoreID.isin(approved_stores)]
        inventory = inventory[inventory.StoreID.isin(approved_stores)]
        targets = targets[targets.StoreID.isin(approved_stores)]
    if category:
        approved_products = set(products.loc[products.Category == category, "ProductID"])
        sales = sales[sales.ProductID.isin(approved_products)]
        inventory = inventory[inventory.ProductID.isin(approved_products)]
    return {
        "Net Sales": round(float(sales.NetSales.sum()), 2),
        "Gross Profit": round(float(sales.GrossProfit.sum()), 2),
        "Gross Margin": float(sales.GrossProfit.sum() / sales.NetSales.sum()),
        "Weighted Availability": float(inventory.FulfilledDemandUnits.sum() / inventory.ExpectedDemandUnits.sum()),
        "Estimated Lost Sales": round(float(inventory.EstimatedLostSales.sum()), 2),
        "Estimated Lost Gross Profit": round(float(inventory.EstimatedLostGrossProfit.sum()), 2),
        "Sales Records": int(len(sales)),
        "Sales Target": None if category else round(float(targets.NetSalesTarget.sum()), 2),
    }


def main() -> None:
    template = (DASHBOARD / "dashboard-template.html").read_text(encoding="utf-8")
    raw_payload = (ROOT / "analysis" / "dashboard_data.json").read_bytes()
    compressed_payload = gzip.compress(raw_payload, compresslevel=9, mtime=0)
    payload = json.dumps(
        {
            "encoding": "gzip-base64",
            "payload": base64.b64encode(compressed_payload).decode("ascii"),
        },
        separators=(",", ":"),
    )
    if "__MORROWFIELD_DATA__" not in template:
        raise ValueError("Dashboard data insertion marker is missing")
    report = template.replace("__MORROWFIELD_DATA__", payload.replace("</", "<\\/"), 1)
    destination = DASHBOARD / "Morrowfield_Availability_Margin_Dashboard.html"
    destination.write_text(report, encoding="utf-8")
    snapshots = {
        "baseline": expected(),
        "region_kwazulu_natal": {"filter": {"Region": ["KwaZulu-Natal"]}, "metrics": expected(region="KwaZulu-Natal")},
        "category_chilled_dairy": {"filter": {"Category": ["Chilled Dairy"]}, "metrics": expected(category="Chilled Dairy")},
        "region_and_category": {"filter": {"Region": ["KwaZulu-Natal"], "Category": ["Chilled Dairy"]}, "metrics": expected(region="KwaZulu-Natal", category="Chilled Dairy")},
    }
    (QA / "expected_dashboard_metrics.json").write_text(json.dumps(snapshots, indent=2), encoding="utf-8")
    print(json.dumps({"status": "ok", "dashboard": str(destination), "bytes": destination.stat().st_size, "snapshots": list(snapshots)}))


if __name__ == "__main__":
    main()
