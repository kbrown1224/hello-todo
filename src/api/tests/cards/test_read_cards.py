"""
Test Cases
* `get /cards/filter` empty database
* `get /cards/filter` one card database
* `get /cards/filter` many card database
* `get /cards/filter` filtering
"""
import pytest
from fastapi import status
from api.cards.models import Card, State, Priority
import pendulum
from httpx import QueryParams

pytestmark = pytest.mark.anyio


@pytest.mark.num_cards(0)
async def test_read_empty(client, clean_db):
    response = await client.get("/api/cards/filter/")
    data = response.json()
    cards = data["cards"]

    assert response.status_code == status.HTTP_200_OK
    assert len(cards) == 0


@pytest.mark.num_cards(1)
async def test_read_one(client, clean_db):
    response = await client.get("/api/cards/filter/")
    data = response.json()
    cards = data["cards"]

    assert response.status_code == status.HTTP_200_OK
    assert len(cards) == 1


@pytest.mark.num_cards(5)
async def test_read_many(client, clean_db):
    response = await client.get("/api/cards/filter/")
    data = response.json()
    cards = data["cards"]

    assert response.status_code == status.HTTP_200_OK
    assert len(cards) == 5


@pytest.fixture()
def sample_cards():
    return [
        Card(title="title 1", state=State.TODO, priority=Priority.LOW, created_dttm=pendulum.DateTime(2022, 1, 1, 10, 10, 10)),
        Card(title="title 2", state=State.TODO, priority=Priority.MEDIUM, created_dttm=pendulum.DateTime(2022, 2, 1, 10, 10, 10)),
        Card(title="title 3", state=State.TODO, priority=Priority.HIGH, created_dttm=pendulum.DateTime(2022, 3, 1, 10, 10, 10)),
        Card(title="title 4", state=State.TODO, priority=Priority.URGENT, created_dttm=pendulum.DateTime(2022, 4, 1, 10, 10, 10)),
        Card(title="title 5", state=State.IN_PROGRESS, priority=Priority.LOW, created_dttm=pendulum.DateTime(2022, 5, 1, 10, 10, 10)),
        Card(title="title 6", state=State.DONE, priority=Priority.LOW, created_dttm=pendulum.DateTime(2022, 6, 1, 10, 10, 10)),
    ]


@pytest.mark.num_cards(0)
@pytest.mark.parametrize(
    "query_params, result_ids",
    [
        # Tests lowest_create_date
        (QueryParams(lowest_create_date=pendulum.Date(2022, 5, 15)), (6,)),
        (QueryParams(lowest_create_date=pendulum.Date(2022, 2, 15)), (3, 4, 5, 6,)),
        # Tests highest_create_date
        (QueryParams(highest_create_date=pendulum.Date(2022, 2, 15)), (1, 2,)),
        (QueryParams(highest_create_date=pendulum.Date(2022, 5, 15)), (1, 2, 3, 4, 5)),
        # Tests states
        (QueryParams(states=[State.TODO.value]), (1, 2, 3, 4)),
        (QueryParams(states=[State.IN_PROGRESS.value]), (5, )),
        (QueryParams(states=[State.DONE.value]), (6, )),
        (QueryParams(states=[State.TODO.value, State.IN_PROGRESS.value]), (1, 2, 3, 4, 5)),
        (QueryParams(states=[State.TODO.value, State.DONE.value]), (1, 2, 3, 4, 6)),
        (QueryParams(states=[State.DONE.value, State.IN_PROGRESS.value]), (5, 6)),
        # Tests priorities
        (QueryParams(priorities=[Priority.LOW.value]), (1, 5, 6,)),
        (QueryParams(priorities=[Priority.MEDIUM.value]), (2,)),
        (QueryParams(priorities=[Priority.HIGH.value]), (3,)),
        (QueryParams(priorities=[Priority.URGENT.value]), (4,)),
        (QueryParams(priorities=[Priority.LOW.value, Priority.MEDIUM.value]), (1, 2, 5, 6,)),
        (QueryParams(priorities=[Priority.LOW.value, Priority.HIGH.value]), (1, 3, 5, 6,)),
        (QueryParams(priorities=[Priority.LOW.value, Priority.URGENT.value]), (1, 4, 5, 6,)),
        (QueryParams(priorities=[Priority.MEDIUM.value, Priority.HIGH.value]), (2, 3,)),
        (QueryParams(priorities=[Priority.MEDIUM.value, Priority.URGENT.value]), (2, 4,)),
        (QueryParams(priorities=[Priority.HIGH.value, Priority.URGENT.value]), (3, 4,)),
        # Tests Combos
        (
            QueryParams(
                priorities=[Priority.MEDIUM.value, Priority.HIGH.value],
                states=[State.TODO.value, State.IN_PROGRESS.value],
                lowest_create_date=pendulum.Date(2022, 2, 15),
                highest_create_date=pendulum.Date(2022, 5, 15)
            ),
            (3,)
        ),
    ]
)
async def test_read_filtered(client, clean_db, sample_cards, query_params, result_ids):
    for card in sample_cards:
        await card.save()

    response = await client.get("/api/cards/filter/", params=query_params)
    data = response.json()
    cards = data["cards"]

    assert response.status_code == status.HTTP_200_OK
    assert len(cards) == len(result_ids)
    assert all(card["id"] in result_ids for card in cards)


async def test_bad_dates(client):
    query_params = QueryParams(
        lowest_create_date=pendulum.Date(2022, 6, 1),
        highest_create_date=pendulum.Date(2022, 5, 1)
    )
    response = await client.get("/api/cards/filter/", params=query_params)
    data = response.json()

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert data['detail'] == 'Bad dates provided, highest_create_date must be after lowest_create_date'
