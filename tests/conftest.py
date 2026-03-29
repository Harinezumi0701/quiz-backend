import pytest
from httpx import ASGITransport, AsyncClient

from app.main import app

# Exclude legacy test scripts that predate the CI setup and are not structured for pytest
collect_ignore = ["test_api.py", "test_dashboard.py", "check_db.py", "verify_filters.py"]


@pytest.fixture
async def client():
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as ac:
        yield ac
