"""
Agent services: customer segmentation, insights, and basic support/sales intent handling.
"""
from __future__ import annotations

from typing import Any, Dict, List, Optional, Sequence, Tuple

try:
    import pandas as pd  # type: ignore
except Exception:  # pandas is optional in this environment
    pd = None  # type: ignore

try:
    from backend.app.utils.logging import LoggerMixin
except Exception:  # fallback minimal logger
    class LoggerMixin:  # type: ignore
        @property
        def logger(self):
            class _L:
                def info(self, *a, **k):
                    pass
                def error(self, *a, **k):
                    pass
                def warning(self, *a, **k):
                    pass
            return _L()


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

        # If pandas is available, use it; otherwise do a pure-Python fallback
        if pd is not None:
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
                labels = self._quantile_bucket_labels_df(df_filled, num_clusters)
                customer_ids = [str(c.id) for c in customers]
                segments = {customer_ids[i]: int(labels[i]) for i in range(len(customer_ids))}
                return {"segments": segments, "centroids": [], "features": features}

            model = KMeans(n_clusters=num_clusters, n_init=10, random_state=42)
            labels = model.fit_predict(df_filled.values)

            # Build response
            customer_ids = [str(c.id) for c in customers]
            segments = {customer_ids[i]: int(labels[i]) for i in range(len(customer_ids))}
            centroids = model.cluster_centers_.tolist()
        else:
            # Pure-Python fallback: quantile bucketing on the first feature
            matrix = self._extract_feature_matrix(customers, features)
            first_feature = [row[0] if row else 0.0 for row in matrix]
            labels = self._quantile_bucket_labels_list(first_feature, num_clusters)
            customer_ids = [str(c.id) for c in customers]
            segments = {customer_ids[i]: int(labels[i]) for i in range(len(customer_ids))}
            centroids = []

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
        insights: List[str] = []
        summary: Dict[str, Dict[str, float]] = {}

        if pd is not None:
            df = self._customers_to_dataframe(customers, list(self.DEFAULT_FEATURES))
            df_filled = df.fillna(0)
            df_filled["segment"] = [segments.get(str(c.id), -1) for c in customers]

            for segment_id, group in df_filled.groupby("segment"):
                seg_summary = {
                    "avg_total_conversions": float(group["total_conversions"].mean()),
                    "avg_total_value": float(group["total_conversion_value"].mean()),
                    "avg_touchpoints": float(group["total_touchpoints"].mean()),
                }
                summary[str(int(segment_id))] = seg_summary
                insights.append(
                    f"Segment {int(segment_id)}: avg conversions {seg_summary['avg_total_conversions']:.2f}, "
                    f"avg value ${seg_summary['avg_total_value']:.2f}, avg touchpoints {seg_summary['avg_touchpoints']:.1f}."
                )
        else:
            # Pure-Python aggregation
            buckets: Dict[int, Dict[str, float]] = {}
            counts: Dict[int, int] = {}
            for c in customers:
                seg = int(segments.get(str(c.id), -1))
                if seg not in buckets:
                    buckets[seg] = {
                        "total_conversions": 0.0,
                        "total_conversion_value": 0.0,
                        "total_touchpoints": 0.0,
                    }
                    counts[seg] = 0
                buckets[seg]["total_conversions"] += float(getattr(c, "total_conversions", 0) or 0)
                buckets[seg]["total_conversion_value"] += float(getattr(c, "total_conversion_value", 0.0) or 0.0)
                buckets[seg]["total_touchpoints"] += float(getattr(c, "total_touchpoints", 0) or 0)
                counts[seg] += 1

            for seg, vals in buckets.items():
                n = max(1, counts.get(seg, 1))
                seg_summary = {
                    "avg_total_conversions": vals["total_conversions"] / n,
                    "avg_total_value": vals["total_conversion_value"] / n,
                    "avg_touchpoints": vals["total_touchpoints"] / n,
                }
                summary[str(seg)] = {k: float(v) for k, v in seg_summary.items()}
                insights.append(
                    f"Segment {seg}: avg conversions {seg_summary['avg_total_conversions']:.2f}, "
                    f"avg value ${seg_summary['avg_total_value']:.2f}, avg touchpoints {seg_summary['avg_touchpoints']:.1f}."
                )

        return {"summary": summary, "insights": insights}

    async def _load_customers(self, db_session: Any) -> List[Any]:
        try:
            # Import locally to avoid hard dependency at module import time
            from sqlalchemy import select as sa_select  # type: ignore
            from backend.app.models.customer import Customer as SA_Customer  # type: ignore
        except Exception:
            return []
        try:
            # Support both sync and async sessions
            if hasattr(db_session, "execute") and db_session.__class__.__name__.lower().startswith("async"):  # type: ignore[attr-defined]
                result = await db_session.execute(sa_select(SA_Customer))  # type: ignore[misc]
                return list(result.scalars().all())
            else:
                result = db_session.execute(sa_select(SA_Customer))  # type: ignore[misc]
                return list(result.scalars().all())
        except Exception:
            return []

    def _customers_to_dataframe(self, customers: List[Any], features: List[str]):  # type: ignore[override]
        assert pd is not None
        rows: List[Dict[str, Any]] = []
        for c in customers:
            row: Dict[str, Any] = {f: float(getattr(c, f, 0) or 0) for f in features}
            row["id"] = str(c.id)
            rows.append(row)
        if not rows:
            return pd.DataFrame(columns=["id", *features])
        return pd.DataFrame(rows).set_index("id")

    def _extract_feature_matrix(self, customers: List[Customer], features: List[str]) -> List[List[float]]:
        matrix: List[List[float]] = []
        for c in customers:
            row = [float(getattr(c, f, 0) or 0) for f in features]
            matrix.append(row)
        return matrix

    def _quantile_bucket_labels_df(self, df: 'pd.DataFrame', k: int) -> List[int]:
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

    def _quantile_bucket_labels_list(self, values: List[float], k: int) -> List[int]:
        n = len(values)
        if n == 0:
            return []
        if k <= 1:
            return [0] * n
        # Compute quantile thresholds
        sorted_vals = sorted((v if v is not None else 0.0) for v in values)
        thresholds: List[float] = []
        for i in range(1, k):
            idx = int(round(i * n / k)) - 1
            idx = min(max(idx, 0), n - 1)
            thresholds.append(sorted_vals[idx])
        # Assign labels
        labels: List[int] = []
        for v in values:
            label = 0
            for t in thresholds:
                if v > t:
                    label += 1
            labels.append(min(label, k - 1))
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
