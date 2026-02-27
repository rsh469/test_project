"""
Descriptor extraction and aggregation from collected tea reviews.
"""

import re
from collections import Counter, defaultdict
from dataclasses import dataclass
import pandas as pd

from taxonomy import KEYWORD_MAP, FLAVOR_WHEEL, CATEGORY_COLORS
from scrapers import ReviewEntry


@dataclass
class DescriptorHit:
    keyword: str
    category: str
    subcategory: str
    color: str
    count: int
    source: str


def _normalize(text: str) -> str:
    """Lowercase, remove punctuation noise."""
    return re.sub(r"[^\w\s'-]", " ", text.lower())


def extract_descriptors(text: str) -> list[dict]:
    """
    Scan text for flavor/aroma keywords from the taxonomy.
    Returns list of matched keyword dicts.
    """
    normalized = _normalize(text)
    hits = []
    for keyword, meta in KEYWORD_MAP.items():
        # whole-word matching (at least 3 chars)
        pattern = r"\b" + re.escape(keyword) + r"\b"
        count = len(re.findall(pattern, normalized))
        if count > 0:
            hits.append({
                "keyword": keyword,
                "category": meta["category"],
                "subcategory": meta["subcategory"],
                "color": meta["color"],
                "count": count,
            })
    return hits


def aggregate(reviews: list[ReviewEntry]) -> dict:
    """
    Full aggregation pipeline.
    Returns a dict with several DataFrames and summary structures.
    """
    if not reviews:
        return {}

    # ------------------------------------------------------------------
    # 1. Extract all descriptor hits per review
    # ------------------------------------------------------------------
    rows = []
    for rev in reviews:
        hits = extract_descriptors(rev.text)
        for h in hits:
            rows.append({
                "source": rev.source,
                "tea_name": rev.tea_name,
                "keyword": h["keyword"],
                "category": h["category"],
                "subcategory": h["subcategory"],
                "color": h["color"],
                "count": h["count"],
            })

    if not rows:
        return {"empty": True, "reviews_total": len(reviews)}

    df = pd.DataFrame(rows)

    # ------------------------------------------------------------------
    # 2. Global keyword frequency
    # ------------------------------------------------------------------
    kw_freq = (
        df.groupby(["keyword", "category", "subcategory", "color"])["count"]
        .sum()
        .reset_index()
        .sort_values("count", ascending=False)
    )

    # ------------------------------------------------------------------
    # 3. Category totals (for the wheel)
    # ------------------------------------------------------------------
    cat_totals = (
        df.groupby(["category", "color"])["count"]
        .sum()
        .reset_index()
        .sort_values("count", ascending=False)
    )

    # ------------------------------------------------------------------
    # 4. Subcategory totals
    # ------------------------------------------------------------------
    sub_totals = (
        df.groupby(["category", "subcategory", "color"])["count"]
        .sum()
        .reset_index()
        .sort_values("count", ascending=False)
    )

    # ------------------------------------------------------------------
    # 5. Source breakdown
    # ------------------------------------------------------------------
    source_cat = (
        df.groupby(["source", "category"])["count"]
        .sum()
        .reset_index()
    )

    # ------------------------------------------------------------------
    # 6. Per-source top keywords (for source comparison)
    # ------------------------------------------------------------------
    source_kw = (
        df.groupby(["source", "keyword", "category"])["count"]
        .sum()
        .reset_index()
        .sort_values("count", ascending=False)
    )

    # ------------------------------------------------------------------
    # 7. Sunburst data: category -> subcategory -> keyword
    # ------------------------------------------------------------------
    sunburst_df = kw_freq[kw_freq["count"] > 0].copy()

    # ------------------------------------------------------------------
    # 8. Radar / Spider chart data: top categories normalised 0-1
    # ------------------------------------------------------------------
    total_mentions = cat_totals["count"].sum()
    radar_data = cat_totals.copy()
    radar_data["share"] = radar_data["count"] / total_mentions if total_mentions else 0

    # ------------------------------------------------------------------
    # 9. Wordcloud data
    # ------------------------------------------------------------------
    wc_data = dict(zip(kw_freq["keyword"], kw_freq["count"]))

    return {
        "empty": False,
        "reviews_total": len(reviews),
        "raw_df": df,
        "kw_freq": kw_freq,
        "cat_totals": cat_totals,
        "sub_totals": sub_totals,
        "source_cat": source_cat,
        "source_kw": source_kw,
        "sunburst_df": sunburst_df,
        "radar_data": radar_data,
        "wc_data": wc_data,
        "total_mentions": int(total_mentions),
    }


def build_sunburst_data(sunburst_df: pd.DataFrame) -> dict:
    """Build plotly-compatible sunburst data from aggregation."""
    labels = ["Вкусо-ароматические категории"]
    parents = [""]
    values = [0]
    colors = ["#FFFFFF"]

    # Category level
    cat_map = {}
    for _, row in sunburst_df.groupby(["category", "color"])["count"].sum().reset_index().iterrows():
        cat = row["category"]
        labels.append(cat)
        parents.append("Вкусо-ароматические категории")
        values.append(int(row["count"]))
        colors.append(row["color"])
        cat_map[cat] = row["color"]

    # Subcategory level
    sub_map = {}
    for _, row in sunburst_df.groupby(["category", "subcategory", "color"])["count"].sum().reset_index().iterrows():
        sub_key = f"{row['subcategory']} ({row['category']})"
        labels.append(sub_key)
        parents.append(row["category"])
        values.append(int(row["count"]))
        # slightly lighter shade for subcategory
        colors.append(row["color"] + "CC")
        sub_map[(row["category"], row["subcategory"])] = sub_key

    # Keyword level (top 60 only to keep chart readable)
    top_kw = sunburst_df.nlargest(60, "count")
    for _, row in top_kw.iterrows():
        sub_key = sub_map.get((row["category"], row["subcategory"]))
        if sub_key:
            labels.append(row["keyword"])
            parents.append(sub_key)
            values.append(int(row["count"]))
            colors.append(row["color"] + "88")

    return {"labels": labels, "parents": parents, "values": values, "colors": colors}


def build_radar_data(radar_data: pd.DataFrame) -> dict:
    """Build radar chart compatible data."""
    categories = radar_data["category"].tolist()
    shares = radar_data["share"].tolist()
    # Close the radar polygon
    return {
        "categories": categories + [categories[0]] if categories else [],
        "values": shares + [shares[0]] if shares else [],
    }
