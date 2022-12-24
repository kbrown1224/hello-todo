import pytest
from httpx import AsyncClient
from api.main import create_app
import sqlalchemy
from api.cards.models import metadata, Card, State, Priority
from api.config import get_settings
import asyncio

settings = get_settings()


@pytest.fixture(autouse=True)
def testing_env(monkeypatch):
    monkeypatch.setenv("TESTING", "True")
    yield


@pytest.fixture
def anyio_backend():
    return 'asyncio'


@pytest.fixture
async def client() -> AsyncClient:
    app = create_app()
    async with AsyncClient(app=app, base_url="http://test") as client_:
        yield client_


@pytest.fixture(scope="function")
async def clean_db(request, faker):
    """Clear out the database after every test function"""
    await Card.objects.delete(each=True)

    faker.seed_instance(101)

    if marker := request.node.get_closest_marker("num_cards"):
        num_cards = marker.args[0]
        insert_tasks = [
            Card(
                title=faker.sentence()[:20],
                summary=faker.sentence(),
                state=State.TODO,
                priority=Priority.LOW
            ).save()
            for _ in range(num_cards)
        ]
        await asyncio.gather(*insert_tasks)

    yield

    await Card.objects.delete(each=True)


@pytest.fixture(params=list(State))
def state_option(request):
    return request.param


@pytest.fixture(params=list(Priority))
def priority_option(request):
    return request.param

