"""
Attribution models for multi-touch attribution analysis.
"""
import math
from abc import ABC, abstractmethod
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import numpy as np
import pandas as pd

from backend.app.utils.logging import LoggerMixin, log_attribution_calculation
from config.settings import get_attribution_settings


class AttributionModel(ABC, LoggerMixin):
    """Abstract base class for attribution models."""
    
    def __init__(self, name: str):
        self.name = name
        self.settings = get_attribution_settings()
    
    @abstractmethod
    def calculate_attribution(
        self,
        touchpoints: List[Dict],
        conversion_value: float = 1.0
    ) -> Dict[str, float]:
        """
        Calculate attribution weights for touchpoints.
        
        Args:
            touchpoints: List of touchpoint dictionaries
            conversion_value: Value of the conversion to attribute
            
        Returns:
            Dictionary mapping touchpoint IDs to attribution weights
        """
        pass
    
    def _validate_touchpoints(self, touchpoints: List[Dict]) -> bool:
        """Validate touchpoint data."""
        if not touchpoints:
            self.logger.warning("No touchpoints provided for attribution")
            return False
        
        required_fields = ['id', 'timestamp', 'channel_id']
        for tp in touchpoints:
            for field in required_fields:
                if field not in tp:
                    self.logger.error(f"Missing required field '{field}' in touchpoint")
                    return False
        
        return True
    
    def _sort_touchpoints(self, touchpoints: List[Dict]) -> List[Dict]:
        """Sort touchpoints by timestamp."""
        return sorted(touchpoints, key=lambda x: x['timestamp'])


class FirstTouchAttribution(AttributionModel):
    """First-touch attribution model - gives 100% credit to first touchpoint."""
    
    def __init__(self):
        super().__init__("first_touch")
    
    def calculate_attribution(
        self,
        touchpoints: List[Dict],
        conversion_value: float = 1.0
    ) -> Dict[str, float]:
        """Give 100% attribution to the first touchpoint."""
        if not self._validate_touchpoints(touchpoints):
            return {}
        
        sorted_touchpoints = self._sort_touchpoints(touchpoints)
        first_touchpoint = sorted_touchpoints[0]
        
        attribution = {tp['id']: 0.0 for tp in touchpoints}
        attribution[first_touchpoint['id']] = conversion_value
        
        self.logger.info(
            "First-touch attribution calculated",
            touchpoint_count=len(touchpoints),
            first_touchpoint_id=first_touchpoint['id']
        )
        
        return attribution


class LastTouchAttribution(AttributionModel):
    """Last-touch attribution model - gives 100% credit to last touchpoint."""
    
    def __init__(self):
        super().__init__("last_touch")
    
    def calculate_attribution(
        self,
        touchpoints: List[Dict],
        conversion_value: float = 1.0
    ) -> Dict[str, float]:
        """Give 100% attribution to the last touchpoint."""
        if not self._validate_touchpoints(touchpoints):
            return {}
        
        sorted_touchpoints = self._sort_touchpoints(touchpoints)
        last_touchpoint = sorted_touchpoints[-1]
        
        attribution = {tp['id']: 0.0 for tp in touchpoints}
        attribution[last_touchpoint['id']] = conversion_value
        
        self.logger.info(
            "Last-touch attribution calculated",
            touchpoint_count=len(touchpoints),
            last_touchpoint_id=last_touchpoint['id']
        )
        
        return attribution


class LinearAttribution(AttributionModel):
    """Linear attribution model - distributes credit equally across all touchpoints."""
    
    def __init__(self):
        super().__init__("linear")
    
    def calculate_attribution(
        self,
        touchpoints: List[Dict],
        conversion_value: float = 1.0
    ) -> Dict[str, float]:
        """Distribute attribution equally across all touchpoints."""
        if not self._validate_touchpoints(touchpoints):
            return {}
        
        weight_per_touchpoint = conversion_value / len(touchpoints)
        attribution = {tp['id']: weight_per_touchpoint for tp in touchpoints}
        
        self.logger.info(
            "Linear attribution calculated",
            touchpoint_count=len(touchpoints),
            weight_per_touchpoint=weight_per_touchpoint
        )
        
        return attribution


class TimeDecayAttribution(AttributionModel):
    """Time-decay attribution model - gives more credit to touchpoints closer to conversion."""
    
    def __init__(self, half_life_days: Optional[int] = None):
        super().__init__("time_decay")
        self.half_life_days = half_life_days or self.settings.time_decay_half_life
    
    def calculate_attribution(
        self,
        touchpoints: List[Dict],
        conversion_value: float = 1.0
    ) -> Dict[str, float]:
        """
        Calculate time-decay attribution based on exponential decay.
        
        Uses the formula: weight = 2^(-days_to_conversion / half_life)
        """
        if not self._validate_touchpoints(touchpoints):
            return {}
        
        sorted_touchpoints = self._sort_touchpoints(touchpoints)
        
        # Assume conversion happens at the end of the journey
        conversion_time = sorted_touchpoints[-1]['timestamp']
        
        weights = []
        for tp in sorted_touchpoints:
            days_to_conversion = (conversion_time - tp['timestamp']).total_seconds() / (24 * 3600)
            # Prevent negative days (touchpoint after conversion)
            days_to_conversion = max(0, days_to_conversion)
            weight = 2 ** (-days_to_conversion / self.half_life_days)
            weights.append(weight)
        
        # Normalize weights to sum to conversion_value
        total_weight = sum(weights)
        if total_weight == 0:
            return {tp['id']: 0.0 for tp in touchpoints}
        
        attribution = {}
        for i, tp in enumerate(sorted_touchpoints):
            attribution[tp['id']] = (weights[i] / total_weight) * conversion_value
        
        self.logger.info(
            "Time-decay attribution calculated",
            touchpoint_count=len(touchpoints),
            half_life_days=self.half_life_days,
            total_weight=total_weight
        )
        
        return attribution


class UShapedAttribution(AttributionModel):
    """
    U-shaped attribution model - gives more credit to first and last touchpoints,
    distributes remaining credit equally among middle touchpoints.
    """
    
    def __init__(
        self,
        first_touch_weight: Optional[float] = None,
        last_touch_weight: Optional[float] = None,
        middle_weight: Optional[float] = None
    ):
        super().__init__("u_shaped")
        self.first_touch_weight = first_touch_weight or self.settings.u_shaped_first_touch_weight
        self.last_touch_weight = last_touch_weight or self.settings.u_shaped_last_touch_weight
        self.middle_weight = middle_weight or self.settings.u_shaped_middle_weight
    
    def calculate_attribution(
        self,
        touchpoints: List[Dict],
        conversion_value: float = 1.0
    ) -> Dict[str, float]:
        """Calculate U-shaped attribution."""
        if not self._validate_touchpoints(touchpoints):
            return {}
        
        sorted_touchpoints = self._sort_touchpoints(touchpoints)
        touchpoint_count = len(sorted_touchpoints)
        
        attribution = {tp['id']: 0.0 for tp in touchpoints}
        
        if touchpoint_count == 1:
            # Only one touchpoint gets all credit
            attribution[sorted_touchpoints[0]['id']] = conversion_value
        elif touchpoint_count == 2:
            # Split between first and last
            attribution[sorted_touchpoints[0]['id']] = conversion_value * 0.5
            attribution[sorted_touchpoints[1]['id']] = conversion_value * 0.5
        else:
            # U-shaped distribution
            first_id = sorted_touchpoints[0]['id']
            last_id = sorted_touchpoints[-1]['id']
            
            attribution[first_id] = conversion_value * self.first_touch_weight
            attribution[last_id] = conversion_value * self.last_touch_weight
            
            # Distribute middle weight among middle touchpoints
            middle_touchpoints = sorted_touchpoints[1:-1]
            if middle_touchpoints:
                middle_weight_per_tp = (conversion_value * self.middle_weight) / len(middle_touchpoints)
                for tp in middle_touchpoints:
                    attribution[tp['id']] = middle_weight_per_tp
        
        self.logger.info(
            "U-shaped attribution calculated",
            touchpoint_count=touchpoint_count,
            first_touch_weight=self.first_touch_weight,
            last_touch_weight=self.last_touch_weight
        )
        
        return attribution


class WShapedAttribution(AttributionModel):
    """
    W-shaped attribution model - gives credit to first touch, lead creation, 
    opportunity creation, and distributes remaining among other touchpoints.
    """
    
    def __init__(
        self,
        first_touch_weight: Optional[float] = None,
        lead_creation_weight: Optional[float] = None,
        opportunity_creation_weight: Optional[float] = None,
        middle_weight: Optional[float] = None
    ):
        super().__init__("w_shaped")
        self.first_touch_weight = first_touch_weight or self.settings.w_shaped_first_touch_weight
        self.lead_creation_weight = lead_creation_weight or self.settings.w_shaped_lead_creation_weight
        self.opportunity_creation_weight = opportunity_creation_weight or self.settings.w_shaped_opportunity_creation_weight
        self.middle_weight = middle_weight or self.settings.w_shaped_middle_weight
    
    def calculate_attribution(
        self,
        touchpoints: List[Dict],
        conversion_value: float = 1.0
    ) -> Dict[str, float]:
        """Calculate W-shaped attribution."""
        if not self._validate_touchpoints(touchpoints):
            return {}
        
        sorted_touchpoints = self._sort_touchpoints(touchpoints)
        touchpoint_count = len(sorted_touchpoints)
        
        attribution = {tp['id']: 0.0 for tp in touchpoints}
        
        if touchpoint_count <= 2:
            # Fall back to U-shaped for small journeys
            u_shaped = UShapedAttribution()
            return u_shaped.calculate_attribution(touchpoints, conversion_value)
        
        # Identify key touchpoints
        first_tp = sorted_touchpoints[0]
        last_tp = sorted_touchpoints[-1]
        
        # For simplified W-shaped, use middle touchpoint as "opportunity creation"
        middle_index = len(sorted_touchpoints) // 2
        opportunity_tp = sorted_touchpoints[middle_index]
        
        # For lead creation, use touchpoint 1/3 through the journey
        lead_index = len(sorted_touchpoints) // 3
        lead_tp = sorted_touchpoints[lead_index] if lead_index > 0 else first_tp
        
        # Assign weights to key touchpoints
        attribution[first_tp['id']] += conversion_value * self.first_touch_weight
        
        if lead_tp['id'] != first_tp['id']:
            attribution[lead_tp['id']] += conversion_value * self.lead_creation_weight
        
        if opportunity_tp['id'] not in [first_tp['id'], lead_tp['id']]:
            attribution[opportunity_tp['id']] += conversion_value * self.opportunity_creation_weight
        
        # Distribute remaining weight among other touchpoints
        key_touchpoint_ids = {first_tp['id'], lead_tp['id'], opportunity_tp['id']}
        other_touchpoints = [tp for tp in sorted_touchpoints if tp['id'] not in key_touchpoint_ids]
        
        if other_touchpoints:
            remaining_weight = conversion_value * self.middle_weight
            weight_per_other = remaining_weight / len(other_touchpoints)
            for tp in other_touchpoints:
                attribution[tp['id']] += weight_per_other
        
        self.logger.info(
            "W-shaped attribution calculated",
            touchpoint_count=touchpoint_count,
            key_touchpoints=len(key_touchpoint_ids),
            other_touchpoints=len(other_touchpoints)
        )
        
        return attribution


class DataDrivenAttribution(AttributionModel):
    """
    Data-driven attribution model using machine learning to determine optimal weights.
    This is a simplified implementation using conversion likelihood.
    """
    
    def __init__(self):
        super().__init__("data_driven")
    
    def calculate_attribution(
        self,
        touchpoints: List[Dict],
        conversion_value: float = 1.0
    ) -> Dict[str, float]:
        """
        Calculate data-driven attribution based on channel performance.
        
        This is a simplified implementation that weights channels by their
        historical conversion rates.
        """
        if not self._validate_touchpoints(touchpoints):
            return {}
        
        # For now, use a simplified approach based on channel type
        # In a real implementation, this would use ML models trained on historical data
        
        channel_weights = {
            'organic_search': 1.2,
            'paid_search': 1.1,
            'social': 0.9,
            'email': 1.0,
            'direct': 1.3,
            'referral': 1.0,
            'display': 0.8
        }
        
        weights = []
        for tp in touchpoints:
            channel_name = tp.get('channel_name', 'unknown')
            weight = channel_weights.get(channel_name.lower(), 1.0)
            weights.append(weight)
        
        # Normalize weights
        total_weight = sum(weights)
        if total_weight == 0:
            return {tp['id']: 0.0 for tp in touchpoints}
        
        attribution = {}
        for i, tp in enumerate(touchpoints):
            attribution[tp['id']] = (weights[i] / total_weight) * conversion_value
        
        self.logger.info(
            "Data-driven attribution calculated",
            touchpoint_count=len(touchpoints),
            total_weight=total_weight
        )
        
        return attribution


class AttributionModelFactory:
    """Factory class for creating attribution models."""
    
    _models = {
        'first_touch': FirstTouchAttribution,
        'last_touch': LastTouchAttribution,
        'linear': LinearAttribution,
        'time_decay': TimeDecayAttribution,
        'u_shaped': UShapedAttribution,
        'w_shaped': WShapedAttribution,
        'data_driven': DataDrivenAttribution,
    }
    
    @classmethod
    def create_model(cls, model_name: str, **kwargs) -> AttributionModel:
        """Create an attribution model by name."""
        if model_name not in cls._models:
            raise ValueError(f"Unknown attribution model: {model_name}")
        
        model_class = cls._models[model_name]
        return model_class(**kwargs)
    
    @classmethod
    def get_available_models(cls) -> List[str]:
        """Get list of available attribution models."""
        return list(cls._models.keys())
    
    @classmethod
    def create_all_models(cls) -> Dict[str, AttributionModel]:
        """Create instances of all available models."""
        return {name: cls.create_model(name) for name in cls._models.keys()}


def compare_attribution_models(
    touchpoints: List[Dict],
    conversion_value: float = 1.0,
    models: Optional[List[str]] = None
) -> pd.DataFrame:
    """
    Compare attribution results across different models.
    
    Args:
        touchpoints: List of touchpoint dictionaries
        conversion_value: Value of the conversion
        models: List of model names to compare (None for all)
        
    Returns:
        DataFrame with attribution results by model and touchpoint
    """
    if models is None:
        models = AttributionModelFactory.get_available_models()
    
    results = []
    
    for model_name in models:
        try:
            model = AttributionModelFactory.create_model(model_name)
            attribution = model.calculate_attribution(touchpoints, conversion_value)
            
            for tp_id, weight in attribution.items():
                results.append({
                    'model': model_name,
                    'touchpoint_id': tp_id,
                    'attribution_weight': weight
                })
        except Exception as e:
            # Log error but continue with other models
            pass
    
    if not results:
        return pd.DataFrame()
    
    df = pd.DataFrame(results)
    return df.pivot(index='touchpoint_id', columns='model', values='attribution_weight').fillna(0)