"""
Pytest configuration and shared fixtures for Multi-Touch Attribution Platform tests.
"""
import asyncio
import pytest
import pytest_asyncio
from typing import AsyncGenerator, Generator
from unittest.mock import Mock, AsyncMock

import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from httpx import AsyncClient

from backend.app.main import app
from backend.app.models.base import Base
from backend.app.core.database import get_db_session
from backend.app.services.attribution_models import AttributionModelFactory
from config.settings import get_settings


# Test database URL
TEST_DATABASE_URL = "sqlite:///./test.db"


@pytest.fixture(scope="session")
def event_loop() -> Generator:
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def test_settings():
    """Test settings fixture."""
    settings = get_settings()
    settings.testing = True
    settings.database.url = TEST_DATABASE_URL
    return settings


@pytest.fixture
def test_engine():
    """Create test database engine."""
    engine = create_engine(
        TEST_DATABASE_URL,
        connect_args={"check_same_thread": False}
    )
    Base.metadata.create_all(bind=engine)
    yield engine
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def test_db_session(test_engine):
    """Create test database session."""
    TestingSessionLocal = sessionmaker(
        autocommit=False,
        autoflush=False,
        bind=test_engine
    )
    
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture
def override_get_db(test_db_session):
    """Override the get_db dependency."""
    def _override_get_db():
        try:
            yield test_db_session
        finally:
            test_db_session.close()
    
    app.dependency_overrides[get_db_session] = _override_get_db
    yield
    app.dependency_overrides.clear()


@pytest_asyncio.fixture
async def test_client(override_get_db) -> AsyncGenerator[AsyncClient, None]:
    """Create test HTTP client."""
    async with AsyncClient(
        app=app,
        base_url="http://test"
    ) as client:
        yield client


@pytest.fixture
def sample_touchpoints():
    """Sample touchpoint data for testing."""
    return [
        {
            'id': 'tp_1',
            'timestamp': pd.Timestamp('2024-01-01 10:00:00'),
            'channel_id': 'ch_1',
            'channel_name': 'organic_search',
            'customer_id': 'cust_1',
            'cost': 0.0
        },
        {
            'id': 'tp_2',
            'timestamp': pd.Timestamp('2024-01-02 14:00:00'),
            'channel_id': 'ch_2',
            'channel_name': 'paid_search',
            'customer_id': 'cust_1',
            'cost': 5.50
        },
        {
            'id': 'tp_3',
            'timestamp': pd.Timestamp('2024-01-03 16:00:00'),
            'channel_id': 'ch_3',
            'channel_name': 'email',
            'customer_id': 'cust_1',
            'cost': 0.10
        }
    ]


@pytest.fixture
def sample_conversion():
    """Sample conversion data for testing."""
    return {
        'id': 'conv_1',
        'customer_id': 'cust_1',
        'timestamp': pd.Timestamp('2024-01-03 18:00:00'),
        'value': 100.00,
        'conversion_type': 'purchase'
    }


@pytest.fixture
def sample_customer_journey(sample_touchpoints, sample_conversion):
    """Sample customer journey with touchpoints and conversion."""
    return {
        'customer_id': 'cust_1',
        'touchpoints': sample_touchpoints,
        'conversions': [sample_conversion]
    }


@pytest.fixture
def mock_redis():
    """Mock Redis client for testing."""
    mock_redis = Mock()
    mock_redis.get = Mock(return_value=None)
    mock_redis.set = Mock(return_value=True)
    mock_redis.delete = Mock(return_value=True)
    mock_redis.exists = Mock(return_value=False)
    return mock_redis


@pytest.fixture
def mock_celery():
    """Mock Celery for testing."""
    mock_celery = Mock()
    mock_celery.send_task = Mock(return_value=Mock(id='task_123'))
    return mock_celery


@pytest.fixture
def attribution_models():
    """Attribution models for testing."""
    return AttributionModelFactory.create_all_models()


@pytest.fixture
def sample_attribution_data():
    """Sample data for attribution testing."""
    return pd.DataFrame({
        'touchpoint_id': ['tp_1', 'tp_2', 'tp_3'],
        'customer_id': ['cust_1', 'cust_1', 'cust_1'],
        'timestamp': [
            '2024-01-01 10:00:00',
            '2024-01-02 14:00:00', 
            '2024-01-03 16:00:00'
        ],
        'channel': ['organic_search', 'paid_search', 'email'],
        'cost': [0.0, 5.50, 0.10],
        'conversion_value': [0, 0, 100]
    })


@pytest.fixture
def mock_db_session():
    """Mock database session for testing."""
    session = Mock()
    session.query = Mock()
    session.add = Mock()
    session.commit = Mock()
    session.rollback = Mock()
    session.close = Mock()
    return session


@pytest.fixture
def mock_api_client():
    """Mock API client for frontend testing."""
    client = AsyncMock()
    client.get = AsyncMock()
    client.post = AsyncMock()
    client.put = AsyncMock()
    client.delete = AsyncMock()
    client.check_health = AsyncMock(return_value=True)
    return client


# Test data factories
class TouchpointFactory:
    """Factory for creating test touchpoint objects."""
    
    @staticmethod
    def create(**kwargs):
        """Create a touchpoint with default values."""
        defaults = {
            'id': 'tp_test',
            'customer_id': 'cust_test',
            'channel_id': 'ch_test',
            'timestamp': pd.Timestamp.now(),
            'touchpoint_type': 'click',
            'cost': 0.0
        }
        defaults.update(kwargs)
        return defaults


class ConversionFactory:
    """Factory for creating test conversion objects."""
    
    @staticmethod
    def create(**kwargs):
        """Create a conversion with default values."""
        defaults = {
            'id': 'conv_test',
            'customer_id': 'cust_test',
            'timestamp': pd.Timestamp.now(),
            'value': 100.0,
            'conversion_type': 'purchase'
        }
        defaults.update(kwargs)
        return defaults


class CustomerFactory:
    """Factory for creating test customer objects."""
    
    @staticmethod
    def create(**kwargs):
        """Create a customer with default values."""
        defaults = {
            'id': 'cust_test',
            'external_customer_id': 'ext_cust_test',
            'email': 'test@example.com',
            'total_conversions': 0,
            'total_conversion_value': 0.0,
            'total_touchpoints': 0
        }
        defaults.update(kwargs)
        return defaults


# Performance testing fixtures
@pytest.fixture
def large_touchpoint_dataset():
    """Large dataset for performance testing."""
    import random
    from datetime import datetime, timedelta
    
    data = []
    base_time = datetime(2024, 1, 1)
    
    for i in range(10000):
        data.append({
            'id': f'tp_{i}',
            'customer_id': f'cust_{i % 1000}',
            'channel_id': f'ch_{random.randint(1, 10)}',
            'timestamp': base_time + timedelta(
                days=random.randint(0, 365),
                hours=random.randint(0, 23),
                minutes=random.randint(0, 59)
            ),
            'touchpoint_type': random.choice(['click', 'impression', 'visit']),
            'cost': round(random.uniform(0, 10), 2)
        })
    
    return data


# Parametrized fixtures for different test scenarios
@pytest.fixture(params=[
    'first_touch',
    'last_touch', 
    'linear',
    'time_decay',
    'u_shaped',
    'w_shaped'
])
def attribution_model_name(request):
    """Parametrized attribution model names."""
    return request.param


@pytest.fixture(params=[1, 2, 3, 5, 10])
def touchpoint_count(request):
    """Parametrized touchpoint counts for testing."""
    return request.param


@pytest.fixture(params=[1.0, 10.0, 100.0, 1000.0])
def conversion_value(request):
    """Parametrized conversion values for testing."""
    return request.param


# Error simulation fixtures
@pytest.fixture
def mock_db_error():
    """Mock database error for testing."""
    def _raise_db_error(*args, **kwargs):
        raise Exception("Database connection error")
    return _raise_db_error


@pytest.fixture
def mock_network_error():
    """Mock network error for testing."""
    def _raise_network_error(*args, **kwargs):
        raise Exception("Network timeout error")
    return _raise_network_error