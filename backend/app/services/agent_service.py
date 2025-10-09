"""
Agent services: customer segmentation, insights, and basic support/sales intent handling.
"""
from __future__ import annotations

from typing import Any, Dict, List, Optional, Sequence, Tuple

import pandas as pd
from sqlalchemy import select

from backend.app.models.customer import Customer
from backend.app.utils.logging import LoggerMixin


class CustomerSegmentationService(LoggerMixin):
    """Service for segmenting customers and generating insights."""

    DEFAULT_FEATURES: Sequence[str] = (
        "total_conversions",
        "total_conversion_value",
        "total_touchpoints",
        "average_time_to_conversion",
        "customer_lifetime_days",
        "data_quality_score",
    )

    async def segment_customers(
        self,
        db_session: Any,
        num_clusters: int = 4,
        feature_names: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """Compute k-means segments for customers based on numeric features.

        Returns a mapping with labels per customer and cluster centroids.
        """
        if db_session is None:
            # No database available; return empty segmentation
            return {"segments": {}, "centroids": [], "features": feature_names or list(self.DEFAULT_FEATURES)}

        features = feature_names or list(self.DEFAULT_FEATURES)

        # Load customers
        customers = await self._load_customers(db_session)
        if not customers:
            return {"segments": {}, "centroids": [], "features": features}

        df = self._customers_to_dataframe(customers, features)
        if df.empty:
            return {"segments": {}, "centroids": [], "features": features}

        # Fill missing values
        df_filled = df.fillna(0)

        # Train k-means (import lazily to avoid heavy import at startup)
        try:
            from sklearn.cluster import KMeans  # type: ignore
        except Exception:
            # Fallback: simple quantile-based bucketing if sklearn unavailable
            labels = self._quantile_bucket_labels(df_filled, num_clusters)
            customer_ids = [str(c.id) for c in customers]
            segments = {customer_ids[i]: int(labels[i]) for i in range(len(customer_ids))}
            return {"segments": segments, "centroids": [], "features": features}

        model = KMeans(n_clusters=num_clusters, n_init=10, random_state=42)
        labels = model.fit_predict(df_filled.values)

        # Build response
        customer_ids = [str(c.id) for c in customers]
        segments = {customer_ids[i]: int(labels[i]) for i in range(len(customer_ids))}
        centroids = model.cluster_centers_.tolist()

        self.logger.info(
            "Customer segmentation computed",
            customers=len(customer_ids),
            clusters=num_clusters,
            features=features,
        )

        return {"segments": segments, "centroids": centroids, "features": features}

    async def generate_segment_insights(self, db_session: Any, num_clusters: int = 4) -> Dict[str, Any]:
        """Compute high-level insights per segment."""
        segmentation = await self.segment_customers(db_session=db_session, num_clusters=num_clusters)
        segments = segmentation.get("segments", {})
        if not segments:
            return {"segments": {}, "insights": []}

        # Load customers again to compute aggregates
        customers = await self._load_customers(db_session)
        df = self._customers_to_dataframe(customers, list(self.DEFAULT_FEATURES))
        df_filled = df.fillna(0)

        # Attach labels
        df_filled["segment"] = [segments.get(str(c.id), -1) for c in customers]

        insights: List[str] = []
        summary: Dict[str, Dict[str, float]] = {}
        for segment_id, group in df_filled.groupby("segment"):
            seg_summary = {
                "avg_total_conversions": float(group["total_conversions"].mean()),
                "avg_total_value": float(group["total_conversion_value"].mean()),
                "avg_touchpoints": float(group["total_touchpoints"].mean()),
            }
            summary[str(int(segment_id))] = seg_summary

            # Narrative insight
            insights.append(
                f"Segment {int(segment_id)}: avg conversions {seg_summary['avg_total_conversions']:.2f}, "
                f"avg value ${seg_summary['avg_total_value']:.2f}, avg touchpoints {seg_summary['avg_touchpoints']:.1f}."
            )

        return {"summary": summary, "insights": insights}

    async def _load_customers(self, db_session: Any) -> List[Customer]:
        try:
            # Support both sync and async sessions
            if hasattr(db_session, "execute") and db_session.__class__.__name__.lower().startswith("async"):  # type: ignore[attr-defined]
                result = await db_session.execute(select(Customer))  # type: ignore[misc]
                return list(result.scalars().all())
            else:
                result = db_session.execute(select(Customer))  # type: ignore[misc]
                return list(result.scalars().all())
        except Exception:
            return []

    def _customers_to_dataframe(self, customers: List[Customer], features: List[str]) -> pd.DataFrame:
        rows: List[Dict[str, Any]] = []
        for c in customers:
            row: Dict[str, Any] = {f: float(getattr(c, f, 0) or 0) for f in features}
            row["id"] = str(c.id)
            rows.append(row)
        if not rows:
            return pd.DataFrame(columns=["id", *features])
        return pd.DataFrame(rows).set_index("id")

    def _quantile_bucket_labels(self, df: pd.DataFrame, k: int) -> List[int]:
        # Use the first feature to produce k quantile buckets as a rough fallback
        if df.shape[0] == 0:
            return []
        if k <= 1:
            return [0] * df.shape[0]
        first_col = df.columns[0]
        try:
            q = pd.qcut(df[first_col], q=k, labels=False, duplicates="drop")
            labels = q.fillna(0).astype(int).tolist()
        except Exception:
            labels = [0] * df.shape[0]
        return labels


class SupportSalesAgentService(LoggerMixin):
    """Very lightweight rule-based support/sales responder (placeholder)."""

    def handle_support_inquiry(self, message: str, customer_id: Optional[str] = None) -> Dict[str, Any]:
        text = (message or "").lower()
        if any(k in text for k in ("refund", "return", "cancel")):
            intent = "billing"
            response = "I can help with billing. I've queued your request; our team will follow up."
        elif any(k in text for k in ("error", "bug", "issue", "broken", "not working")):
            intent = "technical_support"
            response = "Sorry about that. I've captured details and created a support ticket."
        elif any(k in text for k in ("invoice", "payment", "charge")):
            intent = "billing"
            response = "I can help with invoices and charges. Please share the invoice number."
        else:
            intent = "general"
            response = "Thanks for reaching out! A specialist will be with you shortly."

        self.logger.info("Support inquiry handled", intent=intent, customer_id=customer_id)
        return {"intent": intent, "response": response, "customer_id": customer_id}

    def handle_sales_inquiry(self, message: str, customer_id: Optional[str] = None) -> Dict[str, Any]:
        text = (message or "").lower()
        if any(k in text for k in ("pricing", "price", "quote")):
            intent = "pricing"
            suggestions = [
                "Share pricing tiers and ROI calculator",
                "Offer a 14-day pilot with success criteria",
            ]
        elif any(k in text for k in ("demo", "trial", "evaluation")):
            intent = "demo"
            suggestions = [
                "Schedule a tailored demo",
                "Send case studies relevant to the prospect's industry",
            ]
        else:
            intent = "discovery"
            suggestions = [
                "Confirm use case and decision timeline",
                "Identify stakeholders and next best action",
            ]

        self.logger.info("Sales inquiry handled", intent=intent, customer_id=customer_id)
        return {"intent": intent, "next_best_actions": suggestions, "customer_id": customer_id}
