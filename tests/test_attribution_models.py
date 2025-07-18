"""
Unit tests for attribution models.
"""
import pytest
import pandas as pd
from datetime import datetime, timedelta
from unittest.mock import patch

from backend.app.services.attribution_models import (
    AttributionModel,
    FirstTouchAttribution,
    LastTouchAttribution,
    LinearAttribution,
    TimeDecayAttribution,
    UShapedAttribution,
    WShapedAttribution,
    DataDrivenAttribution,
    AttributionModelFactory,
    compare_attribution_models
)


class TestAttributionModelBase:
    """Test base attribution model functionality."""
    
    def test_validate_touchpoints_empty_list(self):
        """Test validation with empty touchpoint list."""
        model = FirstTouchAttribution()
        assert not model._validate_touchpoints([])
    
    def test_validate_touchpoints_missing_fields(self):
        """Test validation with missing required fields."""
        model = FirstTouchAttribution()
        invalid_touchpoints = [
            {'id': 'tp_1', 'timestamp': datetime.now()}
            # Missing channel_id
        ]
        assert not model._validate_touchpoints(invalid_touchpoints)
    
    def test_validate_touchpoints_valid(self, sample_touchpoints):
        """Test validation with valid touchpoints."""
        model = FirstTouchAttribution()
        assert model._validate_touchpoints(sample_touchpoints)
    
    def test_sort_touchpoints(self, sample_touchpoints):
        """Test touchpoint sorting by timestamp."""
        model = FirstTouchAttribution()
        # Reverse the order
        reversed_touchpoints = list(reversed(sample_touchpoints))
        sorted_touchpoints = model._sort_touchpoints(reversed_touchpoints)
        
        # Should be sorted by timestamp
        timestamps = [tp['timestamp'] for tp in sorted_touchpoints]
        assert timestamps == sorted(timestamps)


class TestFirstTouchAttribution:
    """Test first-touch attribution model."""
    
    def test_single_touchpoint(self):
        """Test attribution with single touchpoint."""
        model = FirstTouchAttribution()
        touchpoints = [
            {
                'id': 'tp_1',
                'timestamp': datetime(2024, 1, 1),
                'channel_id': 'ch_1'
            }
        ]
        
        attribution = model.calculate_attribution(touchpoints, 100.0)
        
        assert attribution['tp_1'] == 100.0
        assert len(attribution) == 1
    
    def test_multiple_touchpoints(self, sample_touchpoints):
        """Test attribution with multiple touchpoints."""
        model = FirstTouchAttribution()
        attribution = model.calculate_attribution(sample_touchpoints, 100.0)
        
        # First touchpoint should get all credit
        assert attribution['tp_1'] == 100.0
        assert attribution['tp_2'] == 0.0
        assert attribution['tp_3'] == 0.0
    
    def test_different_conversion_values(self, sample_touchpoints, conversion_value):
        """Test attribution with different conversion values."""
        model = FirstTouchAttribution()
        attribution = model.calculate_attribution(sample_touchpoints, conversion_value)
        
        assert attribution['tp_1'] == conversion_value
        assert sum(attribution.values()) == conversion_value
    
    def test_unsorted_touchpoints(self):
        """Test attribution with unsorted touchpoints."""
        model = FirstTouchAttribution()
        touchpoints = [
            {
                'id': 'tp_2',
                'timestamp': datetime(2024, 1, 2),
                'channel_id': 'ch_2'
            },
            {
                'id': 'tp_1',
                'timestamp': datetime(2024, 1, 1),  # Earlier timestamp
                'channel_id': 'ch_1'
            }
        ]
        
        attribution = model.calculate_attribution(touchpoints, 100.0)
        
        # tp_1 should get credit as it's chronologically first
        assert attribution['tp_1'] == 100.0
        assert attribution['tp_2'] == 0.0


class TestLastTouchAttribution:
    """Test last-touch attribution model."""
    
    def test_single_touchpoint(self):
        """Test attribution with single touchpoint."""
        model = LastTouchAttribution()
        touchpoints = [
            {
                'id': 'tp_1',
                'timestamp': datetime(2024, 1, 1),
                'channel_id': 'ch_1'
            }
        ]
        
        attribution = model.calculate_attribution(touchpoints, 100.0)
        
        assert attribution['tp_1'] == 100.0
        assert len(attribution) == 1
    
    def test_multiple_touchpoints(self, sample_touchpoints):
        """Test attribution with multiple touchpoints."""
        model = LastTouchAttribution()
        attribution = model.calculate_attribution(sample_touchpoints, 100.0)
        
        # Last touchpoint should get all credit
        assert attribution['tp_1'] == 0.0
        assert attribution['tp_2'] == 0.0
        assert attribution['tp_3'] == 100.0
    
    def test_unsorted_touchpoints(self):
        """Test attribution with unsorted touchpoints."""
        model = LastTouchAttribution()
        touchpoints = [
            {
                'id': 'tp_2',
                'timestamp': datetime(2024, 1, 2),
                'channel_id': 'ch_2'
            },
            {
                'id': 'tp_1',
                'timestamp': datetime(2024, 1, 1),
                'channel_id': 'ch_1'
            }
        ]
        
        attribution = model.calculate_attribution(touchpoints, 100.0)
        
        # tp_2 should get credit as it's chronologically last
        assert attribution['tp_1'] == 0.0
        assert attribution['tp_2'] == 100.0


class TestLinearAttribution:
    """Test linear attribution model."""
    
    def test_single_touchpoint(self):
        """Test attribution with single touchpoint."""
        model = LinearAttribution()
        touchpoints = [
            {
                'id': 'tp_1',
                'timestamp': datetime(2024, 1, 1),
                'channel_id': 'ch_1'
            }
        ]
        
        attribution = model.calculate_attribution(touchpoints, 100.0)
        
        assert attribution['tp_1'] == 100.0
    
    def test_multiple_touchpoints(self, sample_touchpoints):
        """Test attribution with multiple touchpoints."""
        model = LinearAttribution()
        attribution = model.calculate_attribution(sample_touchpoints, 100.0)
        
        # Each touchpoint should get equal credit
        expected_value = 100.0 / 3
        assert abs(attribution['tp_1'] - expected_value) < 0.001
        assert abs(attribution['tp_2'] - expected_value) < 0.001
        assert abs(attribution['tp_3'] - expected_value) < 0.001
        
        # Total should equal conversion value
        assert abs(sum(attribution.values()) - 100.0) < 0.001
    
    def test_varying_touchpoint_counts(self, touchpoint_count):
        """Test attribution with varying numbers of touchpoints."""
        model = LinearAttribution()
        touchpoints = []
        
        for i in range(touchpoint_count):
            touchpoints.append({
                'id': f'tp_{i}',
                'timestamp': datetime(2024, 1, 1) + timedelta(hours=i),
                'channel_id': f'ch_{i}'
            })
        
        attribution = model.calculate_attribution(touchpoints, 100.0)
        
        expected_value = 100.0 / touchpoint_count
        for tp_id in attribution:
            assert abs(attribution[tp_id] - expected_value) < 0.001


class TestTimeDecayAttribution:
    """Test time-decay attribution model."""
    
    def test_single_touchpoint(self):
        """Test attribution with single touchpoint."""
        model = TimeDecayAttribution(half_life_days=7)
        touchpoints = [
            {
                'id': 'tp_1',
                'timestamp': datetime(2024, 1, 1),
                'channel_id': 'ch_1'
            }
        ]
        
        attribution = model.calculate_attribution(touchpoints, 100.0)
        
        assert attribution['tp_1'] == 100.0
    
    def test_time_decay_weights(self):
        """Test that time decay gives more weight to recent touchpoints."""
        model = TimeDecayAttribution(half_life_days=7)
        touchpoints = [
            {
                'id': 'tp_1',
                'timestamp': datetime(2024, 1, 1),  # 14 days before conversion
                'channel_id': 'ch_1'
            },
            {
                'id': 'tp_2',
                'timestamp': datetime(2024, 1, 8),   # 7 days before conversion
                'channel_id': 'ch_2'
            },
            {
                'id': 'tp_3',
                'timestamp': datetime(2024, 1, 15),  # Conversion day
                'channel_id': 'ch_3'
            }
        ]
        
        attribution = model.calculate_attribution(touchpoints, 100.0)
        
        # More recent touchpoints should have higher attribution
        assert attribution['tp_3'] > attribution['tp_2']
        assert attribution['tp_2'] > attribution['tp_1']
        
        # Total should equal conversion value
        assert abs(sum(attribution.values()) - 100.0) < 0.001
    
    def test_different_half_life(self):
        """Test time decay with different half-life values."""
        touchpoints = [
            {
                'id': 'tp_1',
                'timestamp': datetime(2024, 1, 1),
                'channel_id': 'ch_1'
            },
            {
                'id': 'tp_2',
                'timestamp': datetime(2024, 1, 15),
                'channel_id': 'ch_2'
            }
        ]
        
        model_short = TimeDecayAttribution(half_life_days=3)
        model_long = TimeDecayAttribution(half_life_days=30)
        
        attr_short = model_short.calculate_attribution(touchpoints, 100.0)
        attr_long = model_long.calculate_attribution(touchpoints, 100.0)
        
        # Shorter half-life should give more weight to recent touchpoint
        assert attr_short['tp_2'] > attr_long['tp_2']
        assert attr_short['tp_1'] < attr_long['tp_1']


class TestUShapedAttribution:
    """Test U-shaped attribution model."""
    
    def test_single_touchpoint(self):
        """Test attribution with single touchpoint."""
        model = UShapedAttribution()
        touchpoints = [
            {
                'id': 'tp_1',
                'timestamp': datetime(2024, 1, 1),
                'channel_id': 'ch_1'
            }
        ]
        
        attribution = model.calculate_attribution(touchpoints, 100.0)
        
        assert attribution['tp_1'] == 100.0
    
    def test_two_touchpoints(self):
        """Test attribution with two touchpoints."""
        model = UShapedAttribution()
        touchpoints = [
            {
                'id': 'tp_1',
                'timestamp': datetime(2024, 1, 1),
                'channel_id': 'ch_1'
            },
            {
                'id': 'tp_2',
                'timestamp': datetime(2024, 1, 2),
                'channel_id': 'ch_2'
            }
        ]
        
        attribution = model.calculate_attribution(touchpoints, 100.0)
        
        # Should split equally between first and last
        assert attribution['tp_1'] == 50.0
        assert attribution['tp_2'] == 50.0
    
    def test_u_shaped_weights(self, sample_touchpoints):
        """Test U-shaped weighting with multiple touchpoints."""
        model = UShapedAttribution(
            first_touch_weight=0.4,
            last_touch_weight=0.4,
            middle_weight=0.2
        )
        attribution = model.calculate_attribution(sample_touchpoints, 100.0)
        
        # First and last should get higher weights
        assert attribution['tp_1'] == 40.0  # First touch
        assert attribution['tp_3'] == 40.0  # Last touch
        assert attribution['tp_2'] == 20.0  # Middle touch
        
        # Total should equal conversion value
        assert sum(attribution.values()) == 100.0
    
    def test_multiple_middle_touchpoints(self):
        """Test U-shaped attribution with multiple middle touchpoints."""
        model = UShapedAttribution(
            first_touch_weight=0.4,
            last_touch_weight=0.4,
            middle_weight=0.2
        )
        
        touchpoints = []
        for i in range(5):
            touchpoints.append({
                'id': f'tp_{i}',
                'timestamp': datetime(2024, 1, 1) + timedelta(days=i),
                'channel_id': f'ch_{i}'
            })
        
        attribution = model.calculate_attribution(touchpoints, 100.0)
        
        # First and last touchpoints
        assert attribution['tp_0'] == 40.0
        assert attribution['tp_4'] == 40.0
        
        # Middle touchpoints should split the middle weight equally
        middle_weight_per_tp = 20.0 / 3  # 3 middle touchpoints
        assert abs(attribution['tp_1'] - middle_weight_per_tp) < 0.001
        assert abs(attribution['tp_2'] - middle_weight_per_tp) < 0.001
        assert abs(attribution['tp_3'] - middle_weight_per_tp) < 0.001


class TestWShapedAttribution:
    """Test W-shaped attribution model."""
    
    def test_single_touchpoint(self):
        """Test attribution with single touchpoint."""
        model = WShapedAttribution()
        touchpoints = [
            {
                'id': 'tp_1',
                'timestamp': datetime(2024, 1, 1),
                'channel_id': 'ch_1'
            }
        ]
        
        # Should fall back to U-shaped for small journeys
        attribution = model.calculate_attribution(touchpoints, 100.0)
        
        assert attribution['tp_1'] == 100.0
    
    def test_two_touchpoints(self):
        """Test attribution with two touchpoints."""
        model = WShapedAttribution()
        touchpoints = [
            {
                'id': 'tp_1',
                'timestamp': datetime(2024, 1, 1),
                'channel_id': 'ch_1'
            },
            {
                'id': 'tp_2',
                'timestamp': datetime(2024, 1, 2),
                'channel_id': 'ch_2'
            }
        ]
        
        # Should fall back to U-shaped for small journeys
        attribution = model.calculate_attribution(touchpoints, 100.0)
        
        assert attribution['tp_1'] == 50.0
        assert attribution['tp_2'] == 50.0
    
    def test_w_shaped_weights(self):
        """Test W-shaped weighting with multiple touchpoints."""
        model = WShapedAttribution(
            first_touch_weight=0.3,
            lead_creation_weight=0.3,
            opportunity_creation_weight=0.3,
            middle_weight=0.1
        )
        
        touchpoints = []
        for i in range(6):
            touchpoints.append({
                'id': f'tp_{i}',
                'timestamp': datetime(2024, 1, 1) + timedelta(days=i),
                'channel_id': f'ch_{i}'
            })
        
        attribution = model.calculate_attribution(touchpoints, 100.0)
        
        # Should sum to conversion value
        assert abs(sum(attribution.values()) - 100.0) < 0.001
        
        # First touchpoint should have weight
        assert attribution['tp_0'] > 0


class TestDataDrivenAttribution:
    """Test data-driven attribution model."""
    
    def test_channel_weights(self):
        """Test that different channels get different weights."""
        model = DataDrivenAttribution()
        touchpoints = [
            {
                'id': 'tp_1',
                'timestamp': datetime(2024, 1, 1),
                'channel_id': 'ch_1',
                'channel_name': 'direct'
            },
            {
                'id': 'tp_2',
                'timestamp': datetime(2024, 1, 2),
                'channel_id': 'ch_2',
                'channel_name': 'display'
            }
        ]
        
        attribution = model.calculate_attribution(touchpoints, 100.0)
        
        # Direct should get more weight than display based on default weights
        assert attribution['tp_1'] > attribution['tp_2']
        
        # Total should equal conversion value
        assert abs(sum(attribution.values()) - 100.0) < 0.001
    
    def test_unknown_channel(self):
        """Test attribution with unknown channel."""
        model = DataDrivenAttribution()
        touchpoints = [
            {
                'id': 'tp_1',
                'timestamp': datetime(2024, 1, 1),
                'channel_id': 'ch_1',
                'channel_name': 'unknown_channel'
            }
        ]
        
        attribution = model.calculate_attribution(touchpoints, 100.0)
        
        # Should still work with default weight
        assert attribution['tp_1'] == 100.0


class TestAttributionModelFactory:
    """Test attribution model factory."""
    
    def test_create_model_valid(self, attribution_model_name):
        """Test creating valid attribution models."""
        model = AttributionModelFactory.create_model(attribution_model_name)
        assert isinstance(model, AttributionModel)
        assert model.name == attribution_model_name
    
    def test_create_model_invalid(self):
        """Test creating invalid attribution model."""
        with pytest.raises(ValueError):
            AttributionModelFactory.create_model('invalid_model')
    
    def test_get_available_models(self):
        """Test getting available models."""
        models = AttributionModelFactory.get_available_models()
        
        expected_models = [
            'first_touch',
            'last_touch',
            'linear',
            'time_decay',
            'u_shaped',
            'w_shaped',
            'data_driven'
        ]
        
        for model in expected_models:
            assert model in models
    
    def test_create_all_models(self):
        """Test creating all available models."""
        models = AttributionModelFactory.create_all_models()
        
        assert len(models) > 0
        for name, model in models.items():
            assert isinstance(model, AttributionModel)
            assert model.name == name


class TestCompareAttributionModels:
    """Test attribution model comparison."""
    
    def test_compare_all_models(self, sample_touchpoints):
        """Test comparing all attribution models."""
        df = compare_attribution_models(sample_touchpoints, 100.0)
        
        assert not df.empty
        assert len(df.columns) > 0  # Should have model columns
        assert len(df.index) == 3   # Should have 3 touchpoints
        
        # Each model column should sum to approximately 100.0
        for col in df.columns:
            assert abs(df[col].sum() - 100.0) < 0.001
    
    def test_compare_specific_models(self, sample_touchpoints):
        """Test comparing specific attribution models."""
        models = ['first_touch', 'last_touch', 'linear']
        df = compare_attribution_models(sample_touchpoints, 100.0, models)
        
        assert list(df.columns) == models
        assert len(df.index) == 3
    
    def test_compare_empty_touchpoints(self):
        """Test comparison with empty touchpoints."""
        df = compare_attribution_models([], 100.0)
        
        assert df.empty
    
    def test_compare_single_touchpoint(self):
        """Test comparison with single touchpoint."""
        touchpoints = [
            {
                'id': 'tp_1',
                'timestamp': datetime(2024, 1, 1),
                'channel_id': 'ch_1'
            }
        ]
        
        df = compare_attribution_models(touchpoints, 100.0)
        
        assert not df.empty
        assert len(df.index) == 1
        
        # All models should give 100% to the single touchpoint
        for col in df.columns:
            assert df[col].iloc[0] == 100.0


class TestAttributionEdgeCases:
    """Test edge cases and error handling."""
    
    def test_zero_conversion_value(self, sample_touchpoints):
        """Test attribution with zero conversion value."""
        model = LinearAttribution()
        attribution = model.calculate_attribution(sample_touchpoints, 0.0)
        
        for value in attribution.values():
            assert value == 0.0
    
    def test_negative_conversion_value(self, sample_touchpoints):
        """Test attribution with negative conversion value."""
        model = LinearAttribution()
        attribution = model.calculate_attribution(sample_touchpoints, -100.0)
        
        # Should handle negative values
        assert sum(attribution.values()) == -100.0
    
    def test_very_large_conversion_value(self, sample_touchpoints):
        """Test attribution with very large conversion value."""
        model = LinearAttribution()
        large_value = 1e9
        attribution = model.calculate_attribution(sample_touchpoints, large_value)
        
        assert abs(sum(attribution.values()) - large_value) < 1e-6
    
    def test_identical_timestamps(self):
        """Test attribution with identical timestamps."""
        model = LinearAttribution()
        same_time = datetime(2024, 1, 1, 12, 0, 0)
        
        touchpoints = [
            {
                'id': 'tp_1',
                'timestamp': same_time,
                'channel_id': 'ch_1'
            },
            {
                'id': 'tp_2',
                'timestamp': same_time,
                'channel_id': 'ch_2'
            }
        ]
        
        attribution = model.calculate_attribution(touchpoints, 100.0)
        
        # Should still work and sum to 100
        assert abs(sum(attribution.values()) - 100.0) < 0.001


class TestPerformance:
    """Test performance with large datasets."""
    
    @pytest.mark.slow
    def test_large_dataset_performance(self, large_touchpoint_dataset):
        """Test attribution model performance with large dataset."""
        import time
        
        model = LinearAttribution()
        
        start_time = time.time()
        attribution = model.calculate_attribution(large_touchpoint_dataset, 100.0)
        execution_time = time.time() - start_time
        
        # Should complete within reasonable time (adjust threshold as needed)
        assert execution_time < 5.0  # 5 seconds
        assert len(attribution) == len(large_touchpoint_dataset)
        assert abs(sum(attribution.values()) - 100.0) < 0.001
    
    @pytest.mark.slow
    def test_all_models_performance(self, large_touchpoint_dataset):
        """Test performance of all models with large dataset."""
        import time
        
        models = ['first_touch', 'last_touch', 'linear']
        
        start_time = time.time()
        df = compare_attribution_models(large_touchpoint_dataset, 100.0, models)
        execution_time = time.time() - start_time
        
        # Should complete within reasonable time
        assert execution_time < 10.0  # 10 seconds
        assert not df.empty