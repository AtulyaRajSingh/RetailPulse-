from __future__ import annotations

import pandas as pd

RECOMMENDATIONS = {
    "VIP Customers": "Invite to premium loyalty programs, early product access, and high-touch retention campaigns.",
    "Loyal Customers": "Use personalized bundles, replenishment reminders, and referral incentives.",
    "New Customers": "Guide toward second purchase with onboarding offers and category education.",
    "Regular Customers": "Promote cross-sell offers and convert to loyalty membership.",
    "At-Risk Customers": "Trigger win-back campaigns, replenishment discounts, and service recovery checks.",
    "Lost Customers": "Suppress expensive campaigns unless reactivation economics are favorable.",
}


def summarize_segments(segmented: pd.DataFrame) -> pd.DataFrame:
    summary = (
        segmented.groupby("segment", as_index=False)
        .agg(
            customers=("customer_id", "count"),
            avg_recency=("recency", "mean"),
            avg_frequency=("frequency", "mean"),
            total_revenue=("monetary", "sum"),
            avg_order_value=("avg_order_value", "mean"),
        )
        .round(2)
    )
    summary["recommendation"] = summary["segment"].map(RECOMMENDATIONS)
    return summary.sort_values("total_revenue", ascending=False)


def top_segment_actions(segmented: pd.DataFrame, top_n: int = 10) -> pd.DataFrame:
    actions = segmented.copy()
    actions["recommended_action"] = actions["segment"].map(RECOMMENDATIONS)
    return actions.sort_values(["rfm_score", "monetary"], ascending=False).head(top_n)
