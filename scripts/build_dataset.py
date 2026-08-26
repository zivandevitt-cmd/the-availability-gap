#!/usr/bin/env python3
"""Generate and audit the synthetic Morrowfield retail analytics portfolio.

The company, suppliers, commercial data and operating events are fictional.
All outputs are deterministic so that reviewers can reproduce the portfolio.
"""

from __future__ import annotations

import json
import math
import sqlite3
from dataclasses import asdict, dataclass
from datetime import date, timedelta
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"
CLEAN = ROOT / "data" / "clean"
ANALYSIS = ROOT / "analysis"
QA = ROOT / "qa"
SEED = 240826
rng = np.random.default_rng(SEED)

for directory in [RAW, CLEAN, ANALYSIS, QA, ROOT / "documentation", ROOT / "sql", ROOT / "powerbi", ROOT / "dashboard", ROOT / "excel", ROOT / "images", ROOT / "portfolio"]:
    directory.mkdir(parents=True, exist_ok=True)


SUPPLIER_RECORDS = [
    ("SUP001", "Karoo Milling Cooperative", "Bloemfontein", "Free State", 0.943, 0.931, 4, "Ambient"),
    ("SUP002", "North Coast Cold Stores", "Durban", "KwaZulu-Natal", 0.921, 0.904, 3, "Chilled"),
    ("SUP003", "Cape Orchard & Press", "Paarl", "Western Cape", 0.956, 0.946, 4, "Ambient"),
    ("SUP004", "Highveld Homecare Works", "Johannesburg", "Gauteng", 0.949, 0.928, 5, "Ambient"),
    ("SUP005", "Lowveld Personal Care", "Mbombela", "Mpumalanga", 0.935, 0.914, 5, "Ambient"),
    ("SUP006", "Drakensberg Breakfast Foods", "Pietermaritzburg", "KwaZulu-Natal", 0.952, 0.938, 4, "Ambient"),
    ("SUP007", "Midlands Fresh Logistics", "Howick", "KwaZulu-Natal", 0.938, 0.916, 3, "Chilled"),
    ("SUP008", "Estuary Import Merchants", "Gqeberha", "Eastern Cape", 0.907, 0.881, 7, "Ambient"),
    ("SUP009", "Stellenridge Beverage Co.", "Stellenbosch", "Western Cape", 0.966, 0.952, 4, "Ambient"),
    ("SUP010", "Bayline Household Supply", "East London", "Eastern Cape", 0.928, 0.902, 6, "Ambient"),
    ("SUP011", "Savanna Brand Partners", "Pretoria", "Gauteng", 0.942, 0.919, 5, "Ambient"),
    ("SUP012", "Peninsula Ambient Foods", "Cape Town", "Western Cape", 0.961, 0.949, 4, "Ambient"),
]


STORE_RECORDS = {
    "Gauteng": [
        ("Rosebank", "Johannesburg"), ("Fourways Crossing", "Johannesburg"),
        ("Menlyn", "Pretoria"), ("Centurion East", "Centurion"),
        ("Sandton Village", "Johannesburg"), ("Bedfordview", "Ekurhuleni"),
        ("Midrand West", "Midrand"), ("Waterfall", "Midrand"),
        ("Irene Link", "Centurion"), ("Bryanston", "Johannesburg"),
        ("Lynnwood", "Pretoria"), ("Randpark Ridge", "Randburg"),
    ],
    "Western Cape": [
        ("Sea Point", "Cape Town"), ("Claremont", "Cape Town"),
        ("Durbanville", "Cape Town"), ("Stellenbosch", "Stellenbosch"),
        ("Paarl Main", "Paarl"), ("Table View", "Cape Town"),
        ("Somerset West", "Somerset West"), ("George", "George"),
        ("Tokai", "Cape Town"),
    ],
    "KwaZulu-Natal": [
        ("Umhlanga", "Durban"), ("Ballito Junction", "Ballito"),
        ("Hillcrest", "Durban"), ("Durban North", "Durban"),
        ("Westville", "Durban"), ("Pietermaritzburg", "Pietermaritzburg"),
        ("Mount Edgecombe", "Durban"), ("Amanzimtoti", "Amanzimtoti"),
        ("Richards Bay", "Richards Bay"),
    ],
    "Eastern Cape": [
        ("Walmer", "Gqeberha"), ("Beacon Bay", "East London"),
        ("Mthatha Plaza", "Mthatha"), ("Newton Park", "Gqeberha"),
        ("Jeffreys Bay", "Jeffreys Bay"), ("Makhanda", "Makhanda"),
    ],
}


# Category, product description, brand, supplier, list price, unit-cost ratio,
# and demand weight. The selected items represent a focused trading assortment,
# not every item stocked in a real supermarket.
CATALOG = [
    ("Pantry Staples", "White maize meal 5 kg", "Stonepath", "SUP001", 84.99, .747, 1.82),
    ("Pantry Staples", "Cake wheat flour 2.5 kg", "Stonepath", "SUP001", 43.49, .714, 1.21),
    ("Pantry Staples", "Brown bread flour 2.5 kg", "Stonepath", "SUP001", 48.99, .723, .86),
    ("Pantry Staples", "Long-grain rice 2 kg", "Riverbend", "SUP008", 69.95, .754, 1.46),
    ("Pantry Staples", "Basmati rice 1 kg", "Riverbend", "SUP008", 53.95, .716, .78),
    ("Pantry Staples", "Sunflower cooking oil 2 L", "Tablelands", "SUP012", 95.90, .791, 1.51),
    ("Pantry Staples", "Chopped tomatoes 410 g", "Tablelands", "SUP012", 19.49, .672, 1.08),
    ("Pantry Staples", "Baked beans 410 g", "Tablelands", "SUP012", 17.99, .697, 1.28),
    ("Pantry Staples", "Smooth peanut butter 800 g", "Field Kitchen", "SUP011", 73.99, .728, 1.12),
    ("Pantry Staples", "Spaghetti 500 g", "Tablelands", "SUP012", 24.49, .658, 1.11),
    ("Pantry Staples", "Macaroni 500 g", "Tablelands", "SUP012", 25.49, .661, .92),
    ("Pantry Staples", "Chicken stock cubes 24 pack", "Field Kitchen", "SUP011", 37.99, .634, .79),
    ("Pantry Staples", "Tomato sauce 700 ml", "Field Kitchen", "SUP011", 39.49, .685, 1.17),
    ("Pantry Staples", "Pilchards in tomato 400 g", "Harbour Table", "SUP008", 29.99, .718, 1.04),
    ("Chilled Dairy", "Full-cream fresh milk 2 L", "Northfield Dairy", "SUP002", 36.99, .781, 2.13),
    ("Chilled Dairy", "Low-fat fresh milk 2 L", "Northfield Dairy", "SUP002", 37.99, .788, 1.57),
    ("Chilled Dairy", "Plain cultured yoghurt 1 kg", "Northfield Dairy", "SUP002", 49.49, .739, 1.31),
    ("Chilled Dairy", "Cheddar cheese block 700 g", "Northfield Dairy", "SUP002", 109.95, .812, 1.29),
    ("Chilled Dairy", "Mature cheddar 400 g", "Northfield Dairy", "SUP002", 79.95, .788, .82),
    ("Chilled Dairy", "Salted farm butter 500 g", "Midlands Table", "SUP007", 89.49, .806, 1.09),
    ("Chilled Dairy", "Free-range eggs 18 pack", "Midlands Table", "SUP007", 67.99, .768, 1.51),
    ("Chilled Dairy", "Strawberry yoghurt 6 pack", "Northfield Dairy", "SUP002", 42.99, .713, 1.16),
    ("Chilled Dairy", "Greek-style yoghurt 500 g", "Midlands Table", "SUP007", 39.95, .687, .93),
    ("Chilled Dairy", "Whipping cream 250 ml", "Midlands Table", "SUP007", 32.49, .712, .71),
    ("Chilled Dairy", "Fresh mozzarella 200 g", "Midlands Table", "SUP007", 46.95, .698, .59),
    ("Chilled Dairy", "Cottage cheese 250 g", "Northfield Dairy", "SUP002", 31.49, .695, .68),
    ("Breakfast", "Wholegrain oats 1 kg", "Summit Grain", "SUP006", 44.95, .694, 1.44),
    ("Breakfast", "Instant oats original 500 g", "Summit Grain", "SUP006", 37.49, .652, 1.09),
    ("Breakfast", "Bran flakes 750 g", "Summit Grain", "SUP006", 54.95, .691, 1.08),
    ("Breakfast", "Granola cranberry 600 g", "Orchard Morning", "SUP003", 79.95, .658, .84),
    ("Breakfast", "Corn flakes 1 kg", "Summit Grain", "SUP006", 59.99, .714, 1.26),
    ("Breakfast", "Wheat biscuits 900 g", "Summit Grain", "SUP006", 64.99, .724, 1.18),
    ("Breakfast", "Crunchy peanut clusters 450 g", "Orchard Morning", "SUP003", 61.49, .641, .68),
    ("Breakfast", "Fruit muesli 750 g", "Orchard Morning", "SUP003", 72.99, .672, .77),
    ("Breakfast", "Instant maize porridge 1 kg", "Summit Grain", "SUP006", 39.95, .718, 1.13),
    ("Breakfast", "Berry breakfast biscuits 300 g", "Field Kitchen", "SUP011", 35.49, .638, .73),
    ("Breakfast", "Honey oat clusters 450 g", "Orchard Morning", "SUP003", 68.95, .654, .65),
    ("Household Care", "Laundry powder 3 kg", "Clearwell", "SUP004", 109.95, .718, 1.41),
    ("Household Care", "Dishwashing liquid 750 ml", "Clearwell", "SUP004", 31.95, .642, 1.63),
    ("Household Care", "All-purpose cleaner 1 L", "Bayline", "SUP010", 39.49, .663, 1.17),
    ("Household Care", "Toilet cleaner 750 ml", "Bayline", "SUP010", 32.95, .641, 1.12),
    ("Household Care", "Fabric conditioner 2 L", "Clearwell", "SUP004", 74.95, .688, 1.03),
    ("Household Care", "Bleach original 1.5 L", "Bayline", "SUP010", 28.49, .674, 1.08),
    ("Household Care", "Laundry capsules 24 pack", "Clearwell", "SUP004", 119.95, .704, .78),
    ("Household Care", "Kitchen degreaser 500 ml", "Bayline", "SUP010", 42.95, .623, .77),
    ("Household Care", "Bin liners 30 pack", "Home Ledger", "SUP011", 37.99, .615, .86),
    ("Household Care", "Handwash refill 750 ml", "Clearwell", "SUP004", 49.49, .651, .96),
    ("Household Care", "Multipurpose wipes 80 pack", "Home Ledger", "SUP011", 43.95, .627, .88),
    ("Household Care", "Floor cleaner 1 L", "Bayline", "SUP010", 37.49, .641, .72),
    ("Household Care", "Laundry bar 500 g", "Clearwell", "SUP004", 24.95, .702, 1.04),
    ("Personal Care", "Daily shampoo 400 ml", "Good Harbour", "SUP005", 54.95, .644, 1.21),
    ("Personal Care", "Nourishing conditioner 400 ml", "Good Harbour", "SUP005", 57.95, .632, .93),
    ("Personal Care", "Fresh deodorant 150 ml", "Good Harbour", "SUP005", 39.95, .613, 1.38),
    ("Personal Care", "Sensitive toothpaste 100 ml", "Brightline", "SUP011", 37.49, .619, 1.11),
    ("Personal Care", "Family toothpaste 150 ml", "Brightline", "SUP011", 33.95, .644, 1.22),
    ("Personal Care", "Body lotion 400 ml", "Good Harbour", "SUP005", 69.95, .648, 1.01),
    ("Personal Care", "Gentle body wash 500 ml", "Good Harbour", "SUP005", 58.49, .629, 1.12),
    ("Personal Care", "Disposable razors 5 pack", "Brightline", "SUP011", 45.95, .607, .77),
    ("Personal Care", "Moisture soap 4 pack", "Good Harbour", "SUP005", 44.49, .656, 1.07),
    ("Personal Care", "Daily sunscreen SPF30 100 ml", "Brightline", "SUP011", 94.95, .614, .61),
    ("Personal Care", "Cotton buds 200 pack", "Brightline", "SUP011", 23.49, .588, .74),
    ("Snacks & Drinks", "Apple juice 1 L", "Cape Press", "SUP003", 34.95, .714, 1.22),
    ("Snacks & Drinks", "Orange juice 1 L", "Cape Press", "SUP003", 36.95, .731, 1.31),
    ("Snacks & Drinks", "Sparkling water 6 pack", "Ridgewater", "SUP009", 49.95, .672, 1.12),
    ("Snacks & Drinks", "Still water 6 pack", "Ridgewater", "SUP009", 43.95, .703, 1.19),
    ("Snacks & Drinks", "Cola zero sugar 2 L", "Ridgewater", "SUP009", 29.95, .692, 1.37),
    ("Snacks & Drinks", "Ginger beer 2 L", "Ridgewater", "SUP009", 32.49, .684, .96),
    ("Snacks & Drinks", "Salted potato crisps 125 g", "Field Kitchen", "SUP011", 24.95, .612, 1.58),
    ("Snacks & Drinks", "Cheddar potato crisps 125 g", "Field Kitchen", "SUP011", 25.49, .618, 1.32),
    ("Snacks & Drinks", "Roasted mixed nuts 250 g", "Cape Press", "SUP003", 64.95, .671, .84),
    ("Snacks & Drinks", "Dark chocolate slab 100 g", "Field Kitchen", "SUP011", 29.95, .623, 1.05),
    ("Snacks & Drinks", "Milk chocolate slab 100 g", "Field Kitchen", "SUP011", 28.49, .634, 1.12),
    ("Snacks & Drinks", "Fruit juice boxes 6 pack", "Cape Press", "SUP003", 46.99, .682, .93),
    ("Snacks & Drinks", "Rooibos iced tea 1.5 L", "Ridgewater", "SUP009", 37.49, .652, .81),
    ("Snacks & Drinks", "Trail mix cranberry 200 g", "Cape Press", "SUP003", 48.95, .636, .76),
    ("Snacks & Drinks", "Cheese crackers 200 g", "Field Kitchen", "SUP011", 29.49, .617, .97),
    ("Snacks & Drinks", "Salted popcorn 100 g", "Field Kitchen", "SUP011", 19.95, .601, 1.04),
]


@dataclass
class QualityIssue:
    issue: str
    table: str
    records_affected: int
    detection_method: str
    cleaning_decision: str
    business_rule: str
    final_treatment: str


def rounded(value: float, digits: int = 2) -> float:
    return round(float(value), digits)


def make_dimensions() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    suppliers = pd.DataFrame(
        SUPPLIER_RECORDS,
        columns=["SupplierID", "SupplierName", "SupplierCity", "SupplierRegion", "ContractFillRate", "ContractOnTimeRate", "ContractLeadDays", "TemperatureBand"],
    )
    region_records = [("REG01", "Gauteng", "Central"), ("REG02", "Western Cape", "Coastal South"), ("REG03", "KwaZulu-Natal", "Coastal East"), ("REG04", "Eastern Cape", "Coastal East")]
    regions = pd.DataFrame(region_records, columns=["RegionID", "Region", "OperatingCorridor"])
    region_lookup = dict(zip(regions.Region, regions.RegionID))
    format_cycle = ["Market", "Food Hall", "Market", "Neighbourhood", "Food Hall", "Market", "Neighbourhood", "Market", "Food Hall", "Market", "Neighbourhood", "Market"]
    region_factor = {"Gauteng": 1.19, "Western Cape": 1.08, "KwaZulu-Natal": 1.02, "Eastern Cape": .84}
    stores_list: list[dict[str, Any]] = []
    counter = 1
    for region, locations in STORE_RECORDS.items():
        for index, (location, city) in enumerate(locations):
            store_format = format_cycle[(index + counter // 7) % len(format_cycle)]
            format_size = {"Neighbourhood": 620, "Market": 1240, "Food Hall": 1810}[store_format]
            size = int(format_size * rng.uniform(.79, 1.17))
            quality = float(np.clip(rng.normal(1, .105), .79, 1.23))
            stores_list.append({
                "StoreID": f"ST{counter:03d}", "StoreName": f"Morrowfield {location}", "City": city,
                "RegionID": region_lookup[region], "Region": region, "StoreFormat": store_format,
                "SellingAreaSqm": size, "OperatingSince": date(2018 + int(rng.integers(0, 7)), int(rng.integers(1, 13)), int(rng.integers(1, 26))).isoformat(),
                "CommercialIndex": rounded(region_factor[region] * quality, 3),
                "Cluster": {"Gauteng": "Inland", "Western Cape": "Cape", "KwaZulu-Natal": "East Coast", "Eastern Cape": "East Coast"}[region],
                "RegionalManager": {"Gauteng": "N. Maseko", "Western Cape": "S. Daniels", "KwaZulu-Natal": "T. Naidoo", "Eastern Cape": "L. Mbeki"}[region],
            })
            counter += 1
    stores = pd.DataFrame(stores_list)

    products_list: list[dict[str, Any]] = []
    for index, (category, product, brand, supplier, price, cost_ratio, demand) in enumerate(CATALOG, start=1):
        adjustment = float(rng.uniform(.991, 1.013))
        list_price = rounded(price * adjustment)
        unit_cost = rounded(list_price * cost_ratio * rng.uniform(.978, 1.019))
        products_list.append({
            "ProductID": f"PR{index:03d}", "ProductName": product, "Brand": brand,
            "Category": category, "SupplierID": supplier, "ListUnitPrice": list_price,
            "StandardUnitCost": unit_cost, "BaseUnitMarginPct": rounded((list_price - unit_cost) / list_price, 4),
            "DemandWeight": demand, "StorageType": "Chilled" if category == "Chilled Dairy" else "Ambient",
            "RangeTier": "Core" if demand >= 1.06 else ("Support" if demand >= .79 else "Tail"),
            "InventoryTracked": demand >= .92 or (supplier == "SUP002" and demand >= .68),
        })
    products = pd.DataFrame(products_list)

    first = date(2026, 2, 23)
    weeks = [first + timedelta(days=i * 7) for i in range(26)]
    calendar = pd.DataFrame([{
        "DateKey": int((first + timedelta(days=i)).strftime("%Y%m%d")),
        "CalendarDate": (first + timedelta(days=i)).isoformat(),
        "WeekStartDate": (first + timedelta(days=i - (i % 7))).isoformat(),
        "WeekNumber": (first + timedelta(days=i)).isocalendar().week,
        "MonthStart": (first + timedelta(days=i)).replace(day=1).isoformat(),
        "MonthLabel": (first + timedelta(days=i)).strftime("%b %Y"),
        "QuarterLabel": f"Q{((first + timedelta(days=i)).month - 1) // 3 + 1} {(first + timedelta(days=i)).year}",
        "DayName": (first + timedelta(days=i)).strftime("%A"),
        "IsWeekend": (first + timedelta(days=i)).weekday() >= 5,
    } for i in range(26 * 7)])
    return suppliers, regions, stores, products, calendar


def is_listed(store: pd.Series, product: pd.Series) -> bool:
    if store.StoreFormat == "Food Hall":
        return True
    if store.StoreFormat == "Market":
        return not (product.RangeTier == "Tail" and int(store.StoreID[2:]) % 4 == 1 and int(product.ProductID[2:]) % 3 == 0)
    return product.RangeTier != "Tail" or int(product.ProductID[2:]) % 6 == int(store.StoreID[2:]) % 6


def supplier_shock(supplier_id: str, region: str, week: date) -> float:
    if supplier_id == "SUP002" and region in {"KwaZulu-Natal", "Eastern Cape"}:
        if date(2026, 5, 18) <= week <= date(2026, 7, 13):
            return .61 if region == "KwaZulu-Natal" else .70
        if date(2026, 7, 20) <= week <= date(2026, 8, 3):
            return .36 if region == "KwaZulu-Natal" else .41
    if supplier_id == "SUP008" and region == "Eastern Cape" and date(2026, 6, 8) <= week <= date(2026, 7, 6):
        return .36
    if supplier_id == "SUP001" and region == "Gauteng" and date(2026, 4, 13) <= week <= date(2026, 4, 27):
        return .23
    return 0.0


def seasonal_factor(category: str, week: date) -> float:
    winter = {5: .05, 6: .11, 7: .14, 8: .08}.get(week.month, 0)
    if category == "Breakfast":
        return 1 + winter * 1.35
    if category == "Pantry Staples":
        return 1 + winter * .77
    if category == "Snacks & Drinks":
        return 1 - winter * .46
    if category == "Personal Care":
        return 1 - winter * .13
    return 1 + winter * .25


def promotion_for(store: pd.Series, product: pd.Series, week: date) -> tuple[str, float, float]:
    if store.Region == "Gauteng" and product.Category in {"Household Care", "Personal Care"} and date(2026, 6, 15) <= week <= date(2026, 7, 27):
        return "Winter Price Lock", float(np.clip(rng.normal(.202, .033), .137, .278)), float(rng.uniform(1.15, 1.37))
    if store.Region == "KwaZulu-Natal" and product.Category == "Chilled Dairy" and date(2026, 5, 25) <= week <= date(2026, 6, 15):
        return "Cold Basket Event", float(np.clip(rng.normal(.118, .021), .078, .167)), float(rng.uniform(1.10, 1.25))
    if product.Category in {"Pantry Staples", "Breakfast"} and week.day >= 22:
        return "Month-end Essentials", float(np.clip(rng.normal(.092, .018), .042, .137)), float(rng.uniform(1.07, 1.18))
    if week == date(2026, 3, 30) and product.Category in {"Snacks & Drinks", "Chilled Dairy"}:
        return "Easter Basket", float(np.clip(rng.normal(.104, .017), .072, .154)), float(rng.uniform(1.15, 1.31))
    if rng.random() < .083:
        return "Store Manager Markdown", float(np.clip(rng.normal(.073, .022), .028, .15)), float(rng.uniform(1.02, 1.11))
    return "No promotion", 0.0, 1.0


def demand_for(store: pd.Series, product: pd.Series, week: date, promotion_lift: float) -> int:
    format_factor = {"Neighbourhood": .78, "Market": 1.03, "Food Hall": 1.32}[store.StoreFormat]
    category_factor = {"Pantry Staples": 1.14, "Chilled Dairy": 1.20, "Breakfast": .97, "Household Care": .83, "Personal Care": .72, "Snacks & Drinks": 1.08}[product.Category]
    local_affinity = 1.0
    if store.Region == "KwaZulu-Natal" and product.Category == "Chilled Dairy":
        local_affinity = 1.09
    if store.Region == "Western Cape" and product.Category == "Snacks & Drinks":
        local_affinity = 1.10
    if store.Region == "Eastern Cape" and product.Category == "Pantry Staples":
        local_affinity = 1.14
    trading_trend = 1 + ((week - date(2026, 2, 23)).days / 7) * .0029
    expectation = 28.0 * product.DemandWeight * store.CommercialIndex * format_factor * category_factor * local_affinity * seasonal_factor(product.Category, week) * promotion_lift * trading_trend
    stochastic = float(np.clip(rng.lognormal(0, .18), .58, 1.71))
    return max(2, int(round(expectation * stochastic)))


def make_operational_facts(stores: pd.DataFrame, products: pd.DataFrame, suppliers: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    weeks = [date(2026, 2, 23) + timedelta(days=i * 7) for i in range(26)]
    supplier_lookup = suppliers.set_index("SupplierID").to_dict("index")
    purchase_orders: list[dict[str, Any]] = []
    fulfillment: dict[tuple[str, str, str], dict[str, Any]] = {}
    order_counter = 1
    for week in weeks:
        for _, store in stores.iterrows():
            supplier_ids = products[products.apply(lambda row: is_listed(store, row), axis=1)].SupplierID.unique()
            for supplier_id in supplier_ids:
                if rng.random() > .51:
                    continue
                supplier = supplier_lookup[supplier_id]
                shock = supplier_shock(supplier_id, store.Region, week)
                fill = float(np.clip(rng.normal(supplier["ContractFillRate"] - shock * .58, .045 + shock * .09), .33, 1.0))
                on_time_probability = max(.13, supplier["ContractOnTimeRate"] - shock * .79)
                is_late = bool(rng.random() > on_time_probability)
                days_late = int(rng.integers(1, 7 if shock > .4 else 4)) if is_late else 0
                ordered_units = int(round(rng.uniform(115, 395) * store.CommercialIndex))
                received_units = int(round(ordered_units * fill))
                promised = week + timedelta(days=int(supplier["ContractLeadDays"]))
                received = promised + timedelta(days=days_late)
                purchase_orders.append({
                    "PurchaseOrderID": f"PO{order_counter:06d}", "OrderWeekStart": week.isoformat(),
                    "StoreID": store.StoreID, "SupplierID": supplier_id, "OrderDate": (week - timedelta(days=2)).isoformat(),
                    "PromisedDate": promised.isoformat(), "ReceivedDate": received.isoformat(),
                    "OrderedUnits": ordered_units, "ReceivedUnits": received_units, "FillRate": rounded(fill, 4),
                    "DaysLate": days_late, "OnTimeFlag": not is_late, "TemperatureBand": supplier["TemperatureBand"],
                    "DeliveryStatus": "Late / short" if is_late and fill < .90 else ("Late" if is_late else ("Short" if fill < .90 else "Complete")),
                })
                fulfillment[(store.StoreID, supplier_id, week.isoformat())] = {"fill": fill, "late": days_late, "shock": shock}
                order_counter += 1

    inventory: list[dict[str, Any]] = []
    sales: list[dict[str, Any]] = []
    targets: list[dict[str, Any]] = []
    previous_closing: dict[tuple[str, str], int] = {}
    inventory_counter = sales_counter = 1

    for week in weeks:
        week_key = week.isoformat()
        for _, store in stores.iterrows():
            store_net = 0.0
            for _, product in products.iterrows():
                if not is_listed(store, product):
                    continue
                campaign, discount_rate, lift = promotion_for(store, product, week)
                expected = demand_for(store, product, week, lift)
                record = fulfillment.get((store.StoreID, product.SupplierID, week_key))
                shock = supplier_shock(product.SupplierID, store.Region, week)
                baseline_fill = float(supplier_lookup[product.SupplierID]["ContractFillRate"])
                fill_rate = record["fill"] if record else float(np.clip(rng.normal(baseline_fill - shock * .36, .033), .40, 1.0))
                late_days = record["late"] if record else (int(rng.integers(1, 4)) if shock > .45 and rng.random() < .40 else 0)
                base_cover = {"Neighbourhood": 1.12, "Market": 1.31, "Food Hall": 1.40}[store.StoreFormat]
                prior = previous_closing.get((store.StoreID, product.ProductID), int(round(expected * rng.uniform(.42, .89))))
                reorder = max(0, int(round(expected * base_cover - prior)))
                if shock > 0:
                    reorder = int(round(reorder * (1.04 + shock * .18)))
                delivery_penalty = max(.43, 1 - late_days * .11)
                received = int(round(reorder * fill_rate * delivery_penalty))
                physical = prior + received
                shelf_execution = float(np.clip(rng.normal(.979 - (.024 if store.Region == "Eastern Cape" else 0), .018), .90, 1.0))
                available_units = max(0, int(round(physical * shelf_execution)))
                sold_units = min(expected, available_units)
                unfilled = max(0, expected - sold_units)
                # A demand-shortfall adjustment prevents every missing unit from
                # being presented as an observable, guaranteed lost purchase.
                capture_factor = .74 if product.Category == "Chilled Dairy" else .68
                estimated_lost_units = int(round(unfilled * capture_factor))
                unit_realized = rounded(product.ListUnitPrice * (1 - discount_rate))
                lost_sales = rounded(estimated_lost_units * unit_realized)
                lost_gp = rounded(estimated_lost_units * max(unit_realized - product.StandardUnitCost, 0))
                closing = max(0, physical - sold_units)
                previous_closing[(store.StoreID, product.ProductID)] = closing
                availability_pct = rounded(sold_units / expected, 4)

                if bool(product.InventoryTracked):
                    inventory.append({
                        "InventoryRecordID": f"IN{inventory_counter:06d}", "WeekStartDate": week_key,
                        "StoreID": store.StoreID, "ProductID": product.ProductID, "SupplierID": product.SupplierID,
                        "OpeningUnits": prior, "OrderedUnits": reorder, "ReceivedUnits": received,
                        "ExpectedDemandUnits": expected, "FulfilledDemandUnits": sold_units,
                        "ClosingUnits": closing, "DaysCover": rounded(closing / max(expected / 7, .01), 1),
                        "AvailabilityRate": availability_pct, "StockoutHours": rounded((1 - availability_pct) * 7 * 12, 1),
                        "EstimatedLostUnits": estimated_lost_units, "EstimatedLostSales": lost_sales,
                        "EstimatedLostGrossProfit": lost_gp, "LateDeliveryDays": late_days,
                    })
                    inventory_counter += 1

                if sold_units <= 0:
                    continue
                unit_cost = rounded(product.StandardUnitCost * rng.uniform(.985, 1.016))
                gross = rounded(sold_units * product.ListUnitPrice)
                discount = rounded(gross * discount_rate)
                net = rounded(gross - discount)
                cost = rounded(sold_units * unit_cost)
                gp = rounded(net - cost)
                sales.append({
                    "SalesRecordID": f"SL{sales_counter:06d}", "WeekStartDate": week_key,
                    "StoreID": store.StoreID, "ProductID": product.ProductID, "SupplierID": product.SupplierID,
                    "RecordType": "Sale", "Units": sold_units, "ListUnitPrice": product.ListUnitPrice,
                    "DiscountRate": rounded(discount_rate, 4), "GrossSales": gross,
                    "DiscountAmount": discount, "NetSales": net, "UnitCost": unit_cost,
                    "CostOfGoodsSold": cost, "GrossProfit": gp, "PromotionName": campaign,
                    "BasketCount": max(1, int(round(sold_units / rng.uniform(1.12, 1.88)))),
                })
                sales_counter += 1
                store_net += net

                if rng.random() < .015:
                    return_units = -max(1, int(round(sold_units * rng.uniform(.018, .084))))
                    return_gross = rounded(return_units * product.ListUnitPrice)
                    return_discount = rounded(return_gross * discount_rate)
                    return_net = rounded(return_gross - return_discount)
                    return_cost = rounded(return_units * unit_cost)
                    sales.append({
                        "SalesRecordID": f"SL{sales_counter:06d}", "WeekStartDate": week_key,
                        "StoreID": store.StoreID, "ProductID": product.ProductID, "SupplierID": product.SupplierID,
                        "RecordType": "Return", "Units": return_units, "ListUnitPrice": product.ListUnitPrice,
                        "DiscountRate": rounded(discount_rate, 4), "GrossSales": return_gross,
                        "DiscountAmount": return_discount, "NetSales": return_net, "UnitCost": unit_cost,
                        "CostOfGoodsSold": return_cost, "GrossProfit": rounded(return_net - return_cost),
                        "PromotionName": campaign, "BasketCount": -1,
                    })
                    sales_counter += 1
                    store_net += return_net

            ambition = {"Gauteng": 1.025, "Western Cape": 1.012, "KwaZulu-Natal": 1.035, "Eastern Cape": 1.045}[store.Region]
            # Targets are prospective management expectations, not a rounded
            # percentage forced to reconcile to the eventual actual.
            normalised_target = store_net * ambition + rng.normal(950, 1720)
            targets.append({
                "TargetID": f"TG{len(targets) + 1:05d}", "WeekStartDate": week_key,
                "StoreID": store.StoreID, "NetSalesTarget": rounded(max(normalised_target, 3000)),
                "GrossMarginTarget": .29, "AvailabilityTarget": .94, "SupplierFillRateTarget": .95,
                "OnTimeDeliveryTarget": .93,
            })

    return pd.DataFrame(purchase_orders), pd.DataFrame(inventory), pd.DataFrame(sales), pd.DataFrame(targets)


def choose(df: pd.DataFrame, n: int, forbidden: set[int] | None = None) -> list[int]:
    candidates = [int(x) for x in df.index if forbidden is None or int(x) not in forbidden]
    return [int(x) for x in rng.choice(candidates, min(n, len(candidates)), replace=False)]


def emit_raw_and_clean(
    suppliers: pd.DataFrame, regions: pd.DataFrame, stores: pd.DataFrame,
    products: pd.DataFrame, calendar: pd.DataFrame, purchase_orders: pd.DataFrame,
    inventory: pd.DataFrame, sales: pd.DataFrame, targets: pd.DataFrame,
) -> tuple[dict[str, pd.DataFrame], list[QualityIssue]]:
    issues: list[QualityIssue] = []
    raw_sales = sales.copy().astype({"WeekStartDate": "object", "StoreID": "object", "ProductID": "object", "DiscountRate": "object", "UnitCost": "object", "PromotionName": "object"})
    used: set[int] = set()

    duplicate_ix = choose(raw_sales, 137)
    date_ix = choose(raw_sales, 226, used); used.update(date_ix)
    raw_sales.loc[date_ix, "WeekStartDate"] = pd.to_datetime(raw_sales.loc[date_ix, "WeekStartDate"]).dt.strftime("%d/%m/%Y")
    issues.append(QualityIssue("Mixed ISO and day-first date formats", "FactSalesWeekly", len(date_ix), "Regex profile and parsed-date exception check", "Parse known ISO and DD/MM/YYYY patterns explicitly", "Reporting week is always a valid Monday", "Converted every recoverable date to ISO YYYY-MM-DD"))

    whitespace_ix = choose(raw_sales, 181, used); used.update(whitespace_ix)
    raw_sales.loc[whitespace_ix, "StoreID"] = raw_sales.loc[whitespace_ix, "StoreID"] + "  "
    issues.append(QualityIssue("Trailing whitespace in store keys", "FactSalesWeekly", len(whitespace_ix), "Compare key length and stripped key to store master", "Trim leading and trailing whitespace before joins", "Valid store keys follow ST plus three digits", "Keys normalised and matched to DimStores"))

    discount_ix = choose(raw_sales, 114, used); used.update(discount_ix)
    raw_sales.loc[discount_ix, "DiscountRate"] = raw_sales.loc[discount_ix, "DiscountRate"].map(lambda x: f"{float(x) * 100:.2f}%")
    issues.append(QualityIssue("Discount percentages delivered as text", "FactSalesWeekly", len(discount_ix), "Type profile and trailing-percent regex", "Strip percent sign and divide by 100", "DiscountRate must be a decimal between 0 and 0.60", "Parsed to decimal; source financial amounts retained"))

    cost_ix = choose(raw_sales, 31, used); used.update(cost_ix)
    raw_sales.loc[cost_ix, "UnitCost"] = None
    issues.append(QualityIssue("Missing transaction unit costs", "FactSalesWeekly", len(cost_ix), "Null scan and product-master lookup", "Recover from CostOfGoodsSold divided by Units", "Recorded transaction totals take priority over standard product costs", "Restored unit cost without changing transaction totals"))

    blank_promo_candidates = raw_sales.index[raw_sales.PromotionName == "No promotion"].tolist()
    promo_ix = [int(x) for x in rng.choice(blank_promo_candidates, 149, replace=False)]
    raw_sales.loc[promo_ix, "PromotionName"] = None
    issues.append(QualityIssue("Blank promotion descriptions on non-promoted rows", "FactSalesWeekly", len(promo_ix), "Null scan checked against zero discount", "Assign No promotion only when DiscountRate equals zero", "A missing promotion label never implies a discount", "Filled non-promoted blanks; no value changes"))

    invalid_store_ix = choose(raw_sales, 19, used); used.update(invalid_store_ix)
    raw_sales.loc[invalid_store_ix, "StoreID"] = [f"ST9{n:02d}" for n in range(19)]
    issues.append(QualityIssue("Store keys absent from approved store master", "FactSalesWeekly", len(invalid_store_ix), "Left anti-join to DimStores", "Quarantine rows; do not guess store identity", "Commercial reporting includes approved mapped stores only", "Excluded from clean fact and saved to quarantine_sales.csv"))

    invalid_product_ix = choose(raw_sales, 13, used); used.update(invalid_product_ix)
    raw_sales.loc[invalid_product_ix, "ProductID"] = [f"PR9{n:02d}" for n in range(13)]
    issues.append(QualityIssue("Product keys absent from approved assortment", "FactSalesWeekly", len(invalid_product_ix), "Left anti-join to DimProducts", "Quarantine rows; product identity cannot be recovered reliably", "Measures exclude unapproved or unmapped products", "Excluded from clean fact and saved to quarantine_sales.csv"))

    raw_sales = pd.concat([raw_sales, raw_sales.loc[duplicate_ix]], ignore_index=True)
    issues.append(QualityIssue("Exact repeated sales extracts", "FactSalesWeekly", len(duplicate_ix), "Duplicate SalesRecordID plus row-hash comparison", "Retain first identical record; investigate conflicting duplicates", "SalesRecordID must be unique", "Removed exact duplicate extract records"))

    raw_inventory = inventory.copy().astype({"WeekStartDate": "object", "StoreID": "object"})
    inventory_dup_ix = choose(raw_inventory, 83)
    inventory_space_ix = choose(raw_inventory, 96)
    raw_inventory.loc[inventory_space_ix, "StoreID"] = " " + raw_inventory.loc[inventory_space_ix, "StoreID"]
    raw_inventory = pd.concat([raw_inventory, raw_inventory.loc[inventory_dup_ix]], ignore_index=True)
    issues.append(QualityIssue("Repeated inventory snapshot rows", "FactInventoryWeekly", len(inventory_dup_ix), "Duplicate InventoryRecordID and full-row comparison", "Retain first identical inventory record", "One approved snapshot per inventory record ID", "Removed repeated weekly snapshot records"))
    issues.append(QualityIssue("Whitespace in inventory store keys", "FactInventoryWeekly", len(inventory_space_ix), "Compare source key against trimmed store master", "Trim before supplier, store and product joins", "Inventory scope must match an approved store", "Normalised keys and validated all relationships"))

    raw_products = products.copy().astype({"Category": "object", "SupplierID": "object", "ProductName": "object"})
    product_category_ix = choose(raw_products, 16)
    variant = {"Pantry Staples": "pantry staples ", "Chilled Dairy": "CHILLED DAIRY", "Breakfast": "break fast", "Household Care": "Home Care ", "Personal Care": "personal-care", "Snacks & Drinks": "Snacks and Drinks"}
    raw_products.loc[product_category_ix, "Category"] = raw_products.loc[product_category_ix, "Category"].map(variant)
    issues.append(QualityIssue("Inconsistent category labels in product master", "DimProducts", len(product_category_ix), "Distinct category profile against six approved categories", "Apply controlled category crosswalk", "Category labels must match the approved trading hierarchy", "Mapped all variants to one canonical category"))

    product_supplier_ix = choose(raw_products, 3)
    raw_products.loc[product_supplier_ix, "SupplierID"] = None
    issues.append(QualityIssue("Missing supplier mappings in product master", "DimProducts", len(product_supplier_ix), "Null scan and supplier match from approved product crosswalk", "Recover supplier from controlled ProductID crosswalk", "Every product has exactly one primary supplier", "Restored mappings and validated supplier referential integrity"))

    product_dups = raw_products.loc[choose(raw_products, 4)].copy()
    product_dups["ProductName"] = product_dups["ProductName"] + " "
    raw_products = pd.concat([raw_products, product_dups], ignore_index=True)
    issues.append(QualityIssue("Duplicate product master records with spacing differences", "DimProducts", len(product_dups), "Duplicate ProductID after whitespace normalisation", "Keep the first approved master record", "ProductID is the unique product dimension key", "Collapsed duplicate product master records"))

    raw_stores = stores.copy().astype({"Region": "object", "StoreName": "object"})
    store_region_ix = choose(raw_stores, 7)
    region_variant = {"Gauteng": "GAUTENG ", "Western Cape": "Western cape", "KwaZulu-Natal": "KZN", "Eastern Cape": "Eastern-Cape"}
    raw_stores.loc[store_region_ix, "Region"] = raw_stores.loc[store_region_ix, "Region"].map(region_variant)
    issues.append(QualityIssue("Region naming variants in store master", "DimStores", len(store_region_ix), "Distinct-value audit against regional hierarchy", "Map approved aliases through the region crosswalk", "Each store maps to exactly one authorised region", "Standardised all region aliases"))

    raw_purchase_orders = purchase_orders.copy()
    early_count = int((pd.to_datetime(raw_purchase_orders.ReceivedDate) < pd.to_datetime(raw_purchase_orders.PromisedDate)).sum())
    return_count = int((sales.RecordType == "Return").sum())
    issues.append(QualityIssue("Negative sales records representing valid customer returns", "FactSalesWeekly", return_count, "RecordType, negative unit and signed-value reconciliation", "Retain legitimate returns rather than deleting negative values", "Returns reverse revenue, units, discount and cost consistently", "Kept all valid returns in commercial totals"))

    raw_map = {
        "DimSuppliers": suppliers, "DimRegions": regions, "DimStores": raw_stores,
        "DimProducts": raw_products, "DimCalendar": calendar,
        "FactPurchaseOrders": raw_purchase_orders, "FactInventoryWeekly": raw_inventory,
        "FactSalesWeekly": raw_sales, "FactStoreTargets": targets,
    }
    for name, frame in raw_map.items():
        frame.to_csv(RAW / f"{name}.csv", index=False)

    # Clean exclusively from the corrupted source copies. Original frames are
    # used only as controlled master crosswalks, never as a reporting shortcut.
    clean_stores = raw_stores.copy()
    clean_stores["Region"] = clean_stores.Region.astype(str).str.strip().replace({"GAUTENG": "Gauteng", "Western cape": "Western Cape", "KZN": "KwaZulu-Natal", "Eastern-Cape": "Eastern Cape"})
    clean_stores["StoreName"] = clean_stores.StoreName.str.strip()

    clean_products = raw_products.copy()
    clean_products["ProductName"] = clean_products.ProductName.str.strip()
    clean_products = clean_products.drop_duplicates("ProductID", keep="first").copy()
    category_map = {"pantry staples": "Pantry Staples", "chilled dairy": "Chilled Dairy", "break fast": "Breakfast", "home care": "Household Care", "personal-care": "Personal Care", "snacks and drinks": "Snacks & Drinks"}
    clean_products["Category"] = clean_products.Category.astype(str).str.strip().map(lambda value: category_map.get(value.lower(), value))
    supplier_master = dict(zip(products.ProductID, products.SupplierID))
    clean_products["SupplierID"] = clean_products.SupplierID.fillna(clean_products.ProductID.map(supplier_master))
    clean_products["InventoryTracked"] = clean_products.InventoryTracked.astype(bool)

    cleaned_sales = raw_sales.drop_duplicates("SalesRecordID", keep="first").copy()
    cleaned_sales["StoreID"] = cleaned_sales.StoreID.astype(str).str.strip()
    cleaned_sales["ProductID"] = cleaned_sales.ProductID.astype(str).str.strip()

    def parse_known_date(value: Any) -> str:
        text = str(value)
        return pd.to_datetime(text, dayfirst="/" in text).date().isoformat()

    cleaned_sales["WeekStartDate"] = cleaned_sales.WeekStartDate.map(parse_known_date)
    cleaned_sales["DiscountRate"] = cleaned_sales.DiscountRate.map(lambda value: float(str(value).rstrip("%")) / (100 if str(value).endswith("%") else 1))
    missing_cost = cleaned_sales.UnitCost.isna()
    cleaned_sales.loc[missing_cost, "UnitCost"] = (cleaned_sales.loc[missing_cost, "CostOfGoodsSold"] / cleaned_sales.loc[missing_cost, "Units"]).round(2)
    cleaned_sales["UnitCost"] = cleaned_sales.UnitCost.astype(float)
    cleaned_sales.loc[cleaned_sales.PromotionName.isna() & (cleaned_sales.DiscountRate == 0), "PromotionName"] = "No promotion"
    invalid = ~cleaned_sales.StoreID.isin(clean_stores.StoreID) | ~cleaned_sales.ProductID.isin(clean_products.ProductID)
    quarantine = cleaned_sales.loc[invalid].copy()
    cleaned_sales = cleaned_sales.loc[~invalid].copy()
    quarantine.to_csv(QA / "quarantine_sales.csv", index=False)

    clean_inventory = raw_inventory.drop_duplicates("InventoryRecordID", keep="first").copy()
    clean_inventory["StoreID"] = clean_inventory.StoreID.astype(str).str.strip()

    clean_map = {
        "DimSuppliers": suppliers.copy(), "DimRegions": regions.copy(), "DimStores": clean_stores,
        "DimProducts": clean_products, "DimCalendar": calendar.copy(),
        "FactPurchaseOrders": raw_purchase_orders.copy(), "FactInventoryWeekly": clean_inventory,
        "FactSalesWeekly": cleaned_sales, "FactStoreTargets": targets.copy(),
    }
    for name, frame in clean_map.items():
        frame.to_csv(CLEAN / f"{name}.csv", index=False)

    issue_frame = pd.DataFrame([asdict(issue) for issue in issues])
    issue_frame.to_csv(QA / "data_quality_log.csv", index=False)
    return clean_map, issues


def named_rows(frame: pd.DataFrame, precision: int = 4) -> list[dict[str, Any]]:
    result = []
    for item in frame.to_dict("records"):
        clean_item: dict[str, Any] = {}
        for key, value in item.items():
            if isinstance(value, (np.integer,)):
                clean_item[key] = int(value)
            elif isinstance(value, (np.floating, float)):
                clean_item[key] = rounded(value, precision) if math.isfinite(float(value)) else None
            elif isinstance(value, (np.bool_,)):
                clean_item[key] = bool(value)
            else:
                clean_item[key] = value
        result.append(clean_item)
    return result


def aggregate_sales(frame: pd.DataFrame, columns: list[str]) -> pd.DataFrame:
    result = frame.groupby(columns, as_index=False, observed=True).agg(
        gross_sales=("GrossSales", "sum"), discount_amount=("DiscountAmount", "sum"),
        net_sales=("NetSales", "sum"), gross_profit=("GrossProfit", "sum"),
        units=("Units", "sum"), records=("SalesRecordID", "count"),
    )
    result["gross_margin_pct"] = result.gross_profit / result.net_sales.replace(0, np.nan)
    result["discount_pct"] = result.discount_amount / result.gross_sales.replace(0, np.nan)
    return result


def aggregate_inventory(frame: pd.DataFrame, columns: list[str]) -> pd.DataFrame:
    result = frame.groupby(columns, as_index=False, observed=True).agg(
        expected_units=("ExpectedDemandUnits", "sum"), fulfilled_units=("FulfilledDemandUnits", "sum"),
        estimated_lost_units=("EstimatedLostUnits", "sum"), estimated_lost_sales=("EstimatedLostSales", "sum"),
        estimated_lost_gp=("EstimatedLostGrossProfit", "sum"), stockout_hours=("StockoutHours", "sum"),
        inventory_records=("InventoryRecordID", "count"), late_delivery_days=("LateDeliveryDays", "sum"),
        ordered_units=("OrderedUnits", "sum"), received_units=("ReceivedUnits", "sum"),
    )
    result["availability_pct"] = result.fulfilled_units / result.expected_units.replace(0, np.nan)
    return result


def build_analysis(clean: dict[str, pd.DataFrame], quality: list[QualityIssue]) -> dict[str, Any]:
    stores, products, suppliers = clean["DimStores"], clean["DimProducts"], clean["DimSuppliers"]
    sales = clean["FactSalesWeekly"].merge(stores[["StoreID", "StoreName", "Region", "StoreFormat", "RegionalManager"]], on="StoreID", how="left", validate="many_to_one").merge(products[["ProductID", "ProductName", "Category", "Brand", "RangeTier"]], on="ProductID", how="left", validate="many_to_one").merge(suppliers[["SupplierID", "SupplierName"]], on="SupplierID", how="left", validate="many_to_one")
    inventory = clean["FactInventoryWeekly"].merge(stores[["StoreID", "StoreName", "Region", "StoreFormat"]], on="StoreID", how="left", validate="many_to_one").merge(products[["ProductID", "ProductName", "Category", "Brand"]], on="ProductID", how="left", validate="many_to_one").merge(suppliers[["SupplierID", "SupplierName"]], on="SupplierID", how="left", validate="many_to_one")
    orders = clean["FactPurchaseOrders"].merge(stores[["StoreID", "StoreName", "Region"]], on="StoreID", how="left", validate="many_to_one").merge(suppliers[["SupplierID", "SupplierName"]], on="SupplierID", how="left", validate="many_to_one")
    targets = clean["FactStoreTargets"].merge(stores[["StoreID", "StoreName", "Region", "StoreFormat"]], on="StoreID", how="left", validate="many_to_one")
    for frame in [sales, inventory]:
        frame["month"] = pd.to_datetime(frame.WeekStartDate).dt.strftime("%b %Y")
        frame["month_sort"] = pd.to_datetime(frame.WeekStartDate).dt.strftime("%Y-%m")
    orders["month"] = pd.to_datetime(orders.OrderWeekStart).dt.strftime("%b %Y")
    orders["month_sort"] = pd.to_datetime(orders.OrderWeekStart).dt.strftime("%Y-%m")
    targets["month"] = pd.to_datetime(targets.WeekStartDate).dt.strftime("%b %Y")
    targets["month_sort"] = pd.to_datetime(targets.WeekStartDate).dt.strftime("%Y-%m")

    financial_cols = ["GrossSales", "DiscountAmount", "NetSales", "CostOfGoodsSold", "GrossProfit"]
    summary = {
        "reporting_start": str(sales.WeekStartDate.min()),
        "reporting_end": (pd.to_datetime(sales.WeekStartDate.max()) + pd.Timedelta(days=6)).date().isoformat(),
        "sales_records": int(len(sales)), "inventory_records": int(len(inventory)),
        "purchase_orders": int(len(orders)), "stores": int(stores.StoreID.nunique()),
        "products": int(products.ProductID.nunique()), "suppliers": int(suppliers.SupplierID.nunique()),
        "regions": int(stores.Region.nunique()), "weeks": int(sales.WeekStartDate.nunique()),
        "gross_sales": rounded(sales.GrossSales.sum()), "discount_amount": rounded(sales.DiscountAmount.sum()),
        "net_sales": rounded(sales.NetSales.sum()), "cost_of_goods_sold": rounded(sales.CostOfGoodsSold.sum()),
        "gross_profit": rounded(sales.GrossProfit.sum()), "gross_margin_pct": rounded(sales.GrossProfit.sum() / sales.NetSales.sum(), 6),
        "discount_pct": rounded(sales.DiscountAmount.sum() / sales.GrossSales.sum(), 6),
        "sales_target": rounded(targets.NetSalesTarget.sum()),
        "target_attainment_pct": rounded(sales.NetSales.sum() / targets.NetSalesTarget.sum(), 6),
        "availability_pct": rounded(inventory.FulfilledDemandUnits.sum() / inventory.ExpectedDemandUnits.sum(), 6),
        "availability_target": .94,
        "estimated_lost_sales": rounded(inventory.EstimatedLostSales.sum()),
        "estimated_lost_gross_profit": rounded(inventory.EstimatedLostGrossProfit.sum()),
        "estimated_lost_units": int(inventory.EstimatedLostUnits.sum()),
        "supplier_fill_rate": rounded(orders.ReceivedUnits.sum() / orders.OrderedUnits.sum(), 6),
        "on_time_rate": rounded(orders.OnTimeFlag.astype(int).mean(), 6),
        "return_records": int((sales.RecordType == "Return").sum()),
        "quarantined_sales_records": int(pd.read_csv(QA / "quarantine_sales.csv").shape[0]),
        "quality_issues": len(quality),
        "raw_sales_records": int(pd.read_csv(RAW / "FactSalesWeekly.csv").shape[0]),
        "raw_inventory_records": int(pd.read_csv(RAW / "FactInventoryWeekly.csv").shape[0]),
    }
    summary["total_fact_rows"] = summary["sales_records"] + summary["inventory_records"] + summary["purchase_orders"] + len(targets)

    weekly_sales = aggregate_sales(sales, ["WeekStartDate"])
    weekly_inv = aggregate_inventory(inventory, ["WeekStartDate"])
    weekly_target = targets.groupby("WeekStartDate", as_index=False).NetSalesTarget.sum().rename(columns={"NetSalesTarget": "sales_target"})
    weekly = weekly_sales.merge(weekly_inv, on="WeekStartDate").merge(weekly_target, on="WeekStartDate")
    weekly["week_label"] = pd.to_datetime(weekly.WeekStartDate).dt.strftime("%d %b")
    weekly["target_attainment_pct"] = weekly.net_sales / weekly.sales_target

    month_sales = aggregate_sales(sales, ["month_sort", "month"])
    month_inv = aggregate_inventory(inventory, ["month_sort", "month"])
    month_target = targets.groupby(["month_sort", "month"], as_index=False).NetSalesTarget.sum().rename(columns={"NetSalesTarget": "sales_target"})
    monthly = month_sales.merge(month_inv, on=["month_sort", "month"]).merge(month_target, on=["month_sort", "month"])

    region_sales = aggregate_sales(sales, ["Region"])
    region_inv = aggregate_inventory(inventory, ["Region"])
    region_target = targets.groupby("Region", as_index=False).NetSalesTarget.sum().rename(columns={"NetSalesTarget": "sales_target"})
    regions = region_sales.merge(region_inv, on="Region").merge(region_target, on="Region")
    regions["sales_share_pct"] = regions.net_sales / regions.net_sales.sum()
    regions["target_attainment_pct"] = regions.net_sales / regions.sales_target

    store_sales = aggregate_sales(sales, ["StoreID", "StoreName", "Region", "StoreFormat"])
    store_inv = aggregate_inventory(inventory, ["StoreID", "StoreName", "Region", "StoreFormat"])
    store_target = targets.groupby(["StoreID"], as_index=False).NetSalesTarget.sum().rename(columns={"NetSalesTarget": "sales_target"})
    store_perf = store_sales.merge(store_inv, on=["StoreID", "StoreName", "Region", "StoreFormat"]).merge(store_target, on="StoreID")
    store_perf["target_attainment_pct"] = store_perf.net_sales / store_perf.sales_target
    store_perf = store_perf.sort_values("estimated_lost_sales", ascending=False)

    category_sales = aggregate_sales(sales, ["Category"])
    category_inv = aggregate_inventory(inventory, ["Category"])
    categories = category_sales.merge(category_inv, on="Category", how="left")
    categories["sales_share_pct"] = categories.net_sales / categories.net_sales.sum()

    product_sales = aggregate_sales(sales, ["ProductID", "ProductName", "Category", "SupplierID", "SupplierName"])
    product_inv = aggregate_inventory(inventory, ["ProductID", "ProductName", "Category", "SupplierID", "SupplierName"])
    product_perf = product_sales.merge(product_inv, on=["ProductID", "ProductName", "Category", "SupplierID", "SupplierName"], how="left")
    product_perf["estimated_lost_sales"] = product_perf.estimated_lost_sales.fillna(0)
    product_perf["estimated_lost_gp"] = product_perf.estimated_lost_gp.fillna(0)
    product_perf = product_perf.sort_values("estimated_lost_sales", ascending=False)
    product_perf["lost_sales_share_pct"] = product_perf.estimated_lost_sales / max(product_perf.estimated_lost_sales.sum(), 1)
    product_perf["cumulative_lost_sales_pct"] = product_perf.lost_sales_share_pct.cumsum()

    supplier_orders = orders.groupby(["SupplierID", "SupplierName"], as_index=False).agg(
        order_count=("PurchaseOrderID", "count"), ordered_units=("OrderedUnits", "sum"),
        received_units=("ReceivedUnits", "sum"), late_orders=("DaysLate", lambda col: int((col > 0).sum())),
        mean_days_late=("DaysLate", "mean"),
    )
    supplier_orders["fill_rate"] = supplier_orders.received_units / supplier_orders.ordered_units
    supplier_orders["on_time_rate"] = 1 - supplier_orders.late_orders / supplier_orders.order_count
    supplier_inv = aggregate_inventory(inventory, ["SupplierID", "SupplierName"])
    supplier_perf = supplier_orders.merge(supplier_inv, on=["SupplierID", "SupplierName"], how="left", suffixes=("", "_inventory")).fillna(0)
    supplier_perf["lost_sales_share_pct"] = supplier_perf.estimated_lost_sales / max(supplier_perf.estimated_lost_sales.sum(), 1)
    supplier_perf = supplier_perf.sort_values("estimated_lost_sales", ascending=False)

    promo = aggregate_sales(sales, ["PromotionName", "Region", "Category"])
    promo["promotion_flag"] = promo.PromotionName != "No promotion"

    region_supplier = aggregate_inventory(inventory, ["Region", "SupplierID", "SupplierName", "Category"])
    region_supplier = region_supplier.sort_values("estimated_lost_sales", ascending=False)
    region_week = aggregate_inventory(inventory, ["WeekStartDate", "Region"])
    region_week["week_label"] = pd.to_datetime(region_week.WeekStartDate).dt.strftime("%d %b")

    # Compact common-grain dashboard model: region × store × product × week.
    # This preserves every filter while avoiding raw detail duplication.
    sales_cube = aggregate_sales(sales, ["WeekStartDate", "month_sort", "month", "StoreID", "StoreName", "Region", "StoreFormat", "ProductID", "ProductName", "Category", "SupplierID", "SupplierName"])
    inv_cube = aggregate_inventory(inventory, ["WeekStartDate", "month_sort", "month", "StoreID", "StoreName", "Region", "StoreFormat", "ProductID", "ProductName", "Category", "SupplierID", "SupplierName"])
    dashboard_cube = sales_cube.merge(inv_cube, on=["WeekStartDate", "month_sort", "month", "StoreID", "StoreName", "Region", "StoreFormat", "ProductID", "ProductName", "Category", "SupplierID", "SupplierName"], how="outer")
    numeric_columns = dashboard_cube.select_dtypes(include="number").columns
    dashboard_cube[numeric_columns] = dashboard_cube[numeric_columns].fillna(0)
    # The self-contained report embeds dense integer-coded records rather than
    # repeatedly serialising every text dimension on each row.
    dimensions = {
        "weeks": sorted(dashboard_cube.WeekStartDate.unique().tolist()),
        "regions": sorted(dashboard_cube.Region.unique().tolist()),
        "stores": [{"id": row.StoreID, "name": row.StoreName, "region": row.Region, "format": row.StoreFormat} for _, row in stores.iterrows()],
        "categories": sorted(dashboard_cube.Category.unique().tolist()),
        "products": [{"id": row.ProductID, "name": row.ProductName, "category": row.Category, "supplier": row.SupplierID, "tracked": bool(row.InventoryTracked)} for _, row in products.iterrows()],
        "suppliers": [{"id": row.SupplierID, "name": row.SupplierName} for _, row in suppliers.iterrows()],
    }
    week_codes = {key: index for index, key in enumerate(dimensions["weeks"])}
    store_codes = {item["id"]: index for index, item in enumerate(dimensions["stores"])}
    product_codes = {item["id"]: index for index, item in enumerate(dimensions["products"])}
    cube_records: list[list[Any]] = []
    for row in dashboard_cube.itertuples(index=False):
        cube_records.append([
            week_codes[row.WeekStartDate], store_codes[row.StoreID], product_codes[row.ProductID],
            rounded(row.gross_sales), rounded(row.discount_amount), rounded(row.net_sales), rounded(row.gross_profit),
            int(row.units), int(row.expected_units), int(row.fulfilled_units), rounded(row.estimated_lost_sales),
            rounded(row.estimated_lost_gp), rounded(row.stockout_hours, 1), int(row.records),
        ])

    target_records = [[week_codes[row.WeekStartDate], store_codes[row.StoreID], rounded(row.NetSalesTarget)] for row in clean["FactStoreTargets"].itertuples(index=False)]
    supplier_record_dimensions = {item["id"]: index for index, item in enumerate(dimensions["suppliers"])}
    order_records = [[week_codes[row.OrderWeekStart], store_codes[row.StoreID], supplier_record_dimensions[row.SupplierID], int(row.OrderedUnits), int(row.ReceivedUnits), int(row.DaysLate), 1 if bool(row.OnTimeFlag) else 0] for row in clean["FactPurchaseOrders"].itertuples(index=False)]

    top_supplier = supplier_perf.iloc[0]
    top_products = product_perf.head(10)
    top_regions = regions.sort_values("estimated_lost_sales", ascending=False)
    discount_region = regions.sort_values("discount_pct", ascending=False).iloc[0]
    comparison_regions = regions[regions.Region != discount_region.Region]
    nonpromoted = sales[sales.PromotionName == "No promotion"]
    winter = sales[sales.PromotionName == "Winter Price Lock"]

    findings = {
        "top_supplier_name": str(top_supplier.SupplierName),
        "top_supplier_id": str(top_supplier.SupplierID),
        "top_supplier_lost_sales": rounded(top_supplier.estimated_lost_sales),
        "top_supplier_lost_sales_share": rounded(top_supplier.lost_sales_share_pct, 6),
        "top_supplier_fill_rate": rounded(top_supplier.fill_rate, 6),
        "top_supplier_on_time_rate": rounded(top_supplier.on_time_rate, 6),
        "top_ten_product_lost_share": rounded(top_products.estimated_lost_sales.sum() / max(summary["estimated_lost_sales"], 1), 6),
        "top_ten_product_lost_sales": rounded(top_products.estimated_lost_sales.sum()),
        "top_region_name": str(top_regions.iloc[0].Region),
        "top_region_lost_sales": rounded(top_regions.iloc[0].estimated_lost_sales),
        "top_region_availability": rounded(top_regions.iloc[0].availability_pct, 6),
        "discount_region_name": str(discount_region.Region),
        "discount_region_sales_share": rounded(discount_region.sales_share_pct, 6),
        "discount_region_margin": rounded(discount_region.gross_margin_pct, 6),
        "discount_region_discount": rounded(discount_region.discount_pct, 6),
        "other_regions_margin": rounded(comparison_regions.gross_profit.sum() / comparison_regions.net_sales.sum(), 6),
        "other_regions_discount": rounded(comparison_regions.discount_amount.sum() / comparison_regions.gross_sales.sum(), 6),
        "winter_promotion_margin": rounded(winter.GrossProfit.sum() / winter.NetSales.sum(), 6),
        "nonpromoted_margin": rounded(nonpromoted.GrossProfit.sum() / nonpromoted.NetSales.sum(), 6),
        "winter_promotion_sales": rounded(winter.NetSales.sum()),
        "priority_store_count": int((store_perf.estimated_lost_sales > store_perf.estimated_lost_sales.quantile(.75)).sum()),
    }
    recoverable_sales = summary["estimated_lost_sales"] * .58
    recoverable_gp = summary["estimated_lost_gross_profit"] * .58
    findings["illustrative_recovery_rate"] = .58
    findings["illustrative_recoverable_sales"] = rounded(recoverable_sales)
    findings["illustrative_recoverable_gross_profit"] = rounded(recoverable_gp)

    actions = [
        {
            "priority": "P1 — Immediate", "issue": f"Escalate {findings['top_supplier_name']} cold-chain delivery failures",
            "business_area": "Supplier service / chilled availability", "driver": "Repeated late and incomplete deliveries in affected coastal stores",
            "severity": "Critical", "financial_impact": findings["top_supplier_lost_sales"],
            "recommended_action": "Agree a two-week recovery plan, reserve daily allocation for the highest-loss chilled SKUs and track every missed delivery.",
            "owner": "Head of Supply Chain", "deadline": "Within 48 hours", "evidence_status": "Observed association; operating cause requires supplier confirmation",
        },
        {
            "priority": "P1 — Immediate", "issue": f"Protect {findings['top_region_name']} priority stores from repeated stockouts",
            "business_area": "Store replenishment", "driver": "Loss exposure concentrated in a small set of tracked store-SKU combinations",
            "severity": "Critical", "financial_impact": rounded(top_regions.iloc[0].estimated_lost_sales * .55),
            "recommended_action": "Introduce twice-weekly exception reviews for the highest-loss stores and move available stock across nearby branches.",
            "owner": "Regional Operations Manager", "deadline": "This trading week", "evidence_status": "Verified store and SKU concentration",
        },
        {
            "priority": "P2 — High", "issue": f"Reset discount guardrails in {findings['discount_region_name']}",
            "business_area": "Promotions and commercial margin", "driver": "Deep winter household and personal-care promotions reduce realised gross margin",
            "severity": "High", "financial_impact": rounded(max(findings["other_regions_margin"] - findings["discount_region_margin"], 0) * float(discount_region.net_sales) * .38),
            "recommended_action": "Review campaign depth by SKU, require a minimum realised-margin threshold and test narrower offers before renewal.",
            "owner": "Commercial Finance Lead", "deadline": "Next promotion review", "evidence_status": "Observed margin association; incremental demand not experimentally isolated",
        },
        {
            "priority": "P2 — High", "issue": "Rebalance reorder buffers for chilled core lines",
            "business_area": "Inventory planning", "driver": "Short shelf-life items have little tolerance for delivery slippage",
            "severity": "High", "financial_impact": rounded(findings["top_supplier_lost_sales"] * .22),
            "recommended_action": "Adjust safety stock on the most material lines after checking expiry exposure and available cold-room capacity.",
            "owner": "Demand Planning Manager", "deadline": "Within two weeks", "evidence_status": "Recommended control; benefit is an illustrative opportunity",
        },
        {
            "priority": "P3 — Monitor", "issue": "Track supplier service and availability together",
            "business_area": "Management reporting", "driver": "Sales-only reporting masks delivery reliability and unmet demand",
            "severity": "Medium", "financial_impact": 0,
            "recommended_action": "Publish one weekly exception pack with weighted availability, fill rate, late orders, loss exposure and accountable owners.",
            "owner": "Retail Performance Analyst", "deadline": "Weekly Monday review", "evidence_status": "Reporting improvement; no standalone savings claimed",
        },
    ]

    output_frames = {
        "weekly_performance": weekly,
        "monthly_performance": monthly,
        "region_performance": regions,
        "store_performance": store_perf,
        "category_performance": categories,
        "product_performance": product_perf,
        "supplier_performance": supplier_perf,
        "promotion_performance": promo,
        "region_supplier_drivers": region_supplier,
        "region_weekly_availability": region_week,
        "management_actions": pd.DataFrame(actions),
    }
    for name, frame in output_frames.items():
        frame.to_csv(ANALYSIS / f"{name}.csv", index=False, float_format="%.6f")

    dashboard = {
        "meta": {
            "company": "Morrowfield Food Co.", "project": "The Availability Gap", "analyst": "Zivan Devitt",
            "portfolio_disclaimer": "Independent portfolio project. The company and dataset are fictional and simulate a realistic retail analytics assignment.",
            "data_as_of": summary["reporting_end"], "currency": "ZAR", "seed": SEED,
            "source_note": "Cleaned weekly POS, tracked inventory snapshots, supplier purchase orders and store targets.",
        },
        "summary": summary, "findings": findings, "dimensions": dimensions,
        "cube_fields": ["week", "store", "product", "gross_sales", "discount_amount", "net_sales", "gross_profit", "units", "expected_units", "fulfilled_units", "lost_sales", "lost_gp", "stockout_hours", "sales_records"],
        "cube": cube_records, "targets": target_records, "orders": order_records,
        "weekly": named_rows(weekly), "monthly": named_rows(monthly), "regions": named_rows(regions),
        "stores": named_rows(store_perf), "categories": named_rows(categories),
        "products": named_rows(product_perf), "suppliers": named_rows(supplier_perf),
        "region_supplier": named_rows(region_supplier), "region_week": named_rows(region_week),
        "promotions": named_rows(promo), "actions": actions, "quality": [asdict(q) for q in quality],
    }
    (ANALYSIS / "dashboard_data.json").write_text(json.dumps(dashboard, separators=(",", ":"), ensure_ascii=False), encoding="utf-8")
    (ANALYSIS / "executive_summary.json").write_text(json.dumps({"summary": summary, "findings": findings, "actions": actions}, indent=2), encoding="utf-8")

    checks = {
        "sales_record_id_unique": bool(clean["FactSalesWeekly"].SalesRecordID.is_unique),
        "inventory_record_id_unique": bool(clean["FactInventoryWeekly"].InventoryRecordID.is_unique),
        "store_dimension_key_unique": bool(stores.StoreID.is_unique),
        "product_dimension_key_unique": bool(products.ProductID.is_unique),
        "supplier_dimension_key_unique": bool(suppliers.SupplierID.is_unique),
        "all_sales_store_keys_match": bool(clean["FactSalesWeekly"].StoreID.isin(stores.StoreID).all()),
        "all_sales_product_keys_match": bool(clean["FactSalesWeekly"].ProductID.isin(products.ProductID).all()),
        "all_sales_supplier_keys_match": bool(clean["FactSalesWeekly"].SupplierID.isin(suppliers.SupplierID).all()),
        "all_inventory_store_keys_match": bool(clean["FactInventoryWeekly"].StoreID.isin(stores.StoreID).all()),
        "all_inventory_product_keys_match": bool(clean["FactInventoryWeekly"].ProductID.isin(products.ProductID).all()),
        "net_sales_equals_gross_less_discount": bool(np.isclose(clean["FactSalesWeekly"].NetSales, clean["FactSalesWeekly"].GrossSales - clean["FactSalesWeekly"].DiscountAmount, atol=.011).all()),
        "gross_profit_equals_net_sales_less_cost": bool(np.isclose(clean["FactSalesWeekly"].GrossProfit, clean["FactSalesWeekly"].NetSales - clean["FactSalesWeekly"].CostOfGoodsSold, atol=.011).all()),
        "returns_carry_negative_units": bool((clean["FactSalesWeekly"].query("RecordType == 'Return'").Units < 0).all()),
        "availability_inside_zero_one": bool(clean["FactInventoryWeekly"].AvailabilityRate.between(0, 1).all()),
        "loss_estimate_nonnegative": bool((clean["FactInventoryWeekly"].EstimatedLostSales >= 0).all()),
        "weighted_availability_reconciles": bool(np.isclose(summary["availability_pct"], inventory.FulfilledDemandUnits.sum() / inventory.ExpectedDemandUnits.sum(), atol=.000001)),
        "supplier_loss_reconciles": bool(np.isclose(supplier_perf.estimated_lost_sales.sum(), summary["estimated_lost_sales"], atol=.02)),
        "regional_net_sales_reconciles": bool(np.isclose(regions.net_sales.sum(), summary["net_sales"], atol=.02)),
        "store_net_sales_reconciles": bool(np.isclose(store_perf.net_sales.sum(), summary["net_sales"], atol=.02)),
        "category_net_sales_reconciles": bool(np.isclose(categories.net_sales.sum(), summary["net_sales"], atol=.02)),
        "weekly_net_sales_reconciles": bool(np.isclose(weekly.net_sales.sum(), summary["net_sales"], atol=.02)),
        "target_totals_reconcile": bool(np.isclose(targets.NetSalesTarget.sum(), summary["sales_target"], atol=.02)),
        "quarantine_count_reconciles": bool(summary["quarantined_sales_records"] == 32),
    }
    (QA / "reconciliation_checks.json").write_text(json.dumps({"checks": checks, "passed": all(checks.values()), "summary": summary, "findings": findings}, indent=2), encoding="utf-8")

    database_path = CLEAN / "morrowfield_analytics.sqlite"
    with sqlite3.connect(database_path) as connection:
        for name, frame in clean.items():
            frame.to_sql(name, connection, index=False, if_exists="replace")
        for name, frame in output_frames.items():
            frame.to_sql(f"analysis_{name}", connection, index=False, if_exists="replace")
        connection.executescript("""
            CREATE INDEX IF NOT EXISTS idx_sales_week_store_product ON FactSalesWeekly (WeekStartDate, StoreID, ProductID);
            CREATE INDEX IF NOT EXISTS idx_inventory_week_store_product ON FactInventoryWeekly (WeekStartDate, StoreID, ProductID);
            CREATE INDEX IF NOT EXISTS idx_orders_supplier_week ON FactPurchaseOrders (SupplierID, OrderWeekStart);
            CREATE INDEX IF NOT EXISTS idx_targets_store_week ON FactStoreTargets (StoreID, WeekStartDate);
        """)

    if not all(checks.values()):
        failures = [name for name, passed in checks.items() if not passed]
        raise RuntimeError(f"Reconciliation failed: {', '.join(failures)}")
    return dashboard


def main() -> None:
    suppliers, regions, stores, products, calendar = make_dimensions()
    purchase_orders, inventory, sales, targets = make_operational_facts(stores, products, suppliers)
    clean, quality = emit_raw_and_clean(suppliers, regions, stores, products, calendar, purchase_orders, inventory, sales, targets)
    dashboard = build_analysis(clean, quality)
    print(json.dumps({"status": "ok", "summary": dashboard["summary"], "findings": dashboard["findings"], "directory": str(ROOT)}, indent=2))


if __name__ == "__main__":
    main()
