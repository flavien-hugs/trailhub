import pytest
from beanie import init_beanie
from httpx import ASGITransport, AsyncClient
from mongomock_motor import AsyncMongoMockClient

from src.config import settings

__client = AsyncMongoMockClient()


@pytest.fixture()
def fake_data():
    import faker

    return faker.Faker()


@pytest.fixture
async def fixture_app():
    from src.main import app
    yield app


@pytest.fixture()
def fixture_model():
    from src import models

    return models


@pytest.fixture(autouse=True)
async def mongo_mock_client(fixture_app, fixture_model):
    fixture_app.mongodb_client = __client[settings.MONGO_DB]
    await init_beanie(
        database=fixture_app.mongodb_client,
        document_models=[fixture_model.TrailHubModel],
    )
    yield __client


@pytest.fixture(autouse=True)
async def clean_db(mongo_mock_client, fixture_model):
    for model in [fixture_model.TrailHubModel]:
        await model.delete_all()


@pytest.fixture
async def http_client_api(clean_db, fixture_app):
    async with AsyncClient(
            transport=ASGITransport(app=fixture_app),
            base_url="http://api.trailhub.com"
    ) as ac:
        yield ac


@pytest.fixture
def trailhub_data(fake_data):
    return {
        "user_id": fake_data.uuid4(cast_to=str),
        "source": fake_data.name(),
        "message": fake_data.text(),
    }


@pytest.fixture
async def create_trailhub(fixture_model, trailhub_data, fake_data):
    trailhub = await fixture_model.TrailHubModel(
        **trailhub_data, address_ip=fake_data.ipv6()
    ).create()
    return trailhub
