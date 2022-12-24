"""
Test Cases
* `patch /cards/{card_id}` the title of a card
* `patch /cards/{card_id}` the summary of a card
* `patch /cards/{card_id}` the priority of a card
* `patch /cards/{card_id}` title, summary, priority of a card at the same time
* `patch /cards/{card_id}` empty database
* `patch /cards/{card_id}` many card database
"""
import pytest
from fastapi import status
from api.cards.models import Card, State, Priority

pytestmark = pytest.mark.anyio


@pytest.fixture
def sample_card():
    return Card(
        title="og title",
        summary="og summary",
        state=State.TODO,
        priority=Priority.LOW
    )


@pytest.mark.num_cards(0)
async def test_update_title(client, clean_db, sample_card):
    original_card = sample_card
    await original_card.save()

    body = {"title": "new test"}

    response = await client.patch(f"/api/cards/{original_card.id}", json=body)
    updated_card = await Card.objects.get(id=original_card.id)

    assert response.status_code == status.HTTP_204_NO_CONTENT
    assert updated_card.id == original_card.id
    assert updated_card.title == body["title"]
    assert updated_card.summary == original_card.summary
    assert updated_card.state.value == original_card.state.value
    assert updated_card.priority.value == original_card.priority.value


@pytest.mark.num_cards(0)
async def test_update_summary(client, clean_db, sample_card):
    original_card = sample_card
    await original_card.save()

    body = {"summary": "new summary"}

    response = await client.patch(f"/api/cards/{original_card.id}", json=body)
    updated_card = await Card.objects.get(id=original_card.id)

    assert response.status_code == status.HTTP_204_NO_CONTENT
    assert updated_card.id == original_card.id
    assert updated_card.title == original_card.title
    assert updated_card.summary == body["summary"]
    assert updated_card.state.value == original_card.state.value
    assert updated_card.priority.value == original_card.priority.value


@pytest.mark.num_cards(0)
async def test_update_priority(client, clean_db, sample_card):
    original_card = sample_card
    await original_card.save()

    body = {"priority": Priority.MEDIUM.value}

    response = await client.patch(f"/api/cards/{original_card.id}", json=body)
    updated_card = await Card.objects.get(id=original_card.id)

    assert response.status_code == status.HTTP_204_NO_CONTENT
    assert updated_card.id == original_card.id
    assert updated_card.title == original_card.title
    assert updated_card.summary == original_card.summary
    assert updated_card.state.value == original_card.state.value
    assert updated_card.priority.value == body["priority"]


@pytest.mark.num_cards(0)
async def test_update_multiple_fields(client, clean_db, sample_card):
    original_card = sample_card
    await original_card.save()

    body = {
        "title": "new test",
        "summary": "new summary",
        "priority": Priority.MEDIUM.value
    }

    response = await client.patch(f"/api/cards/{original_card.id}", json=body)
    updated_card = await Card.objects.get(id=original_card.id)

    assert response.status_code == status.HTTP_204_NO_CONTENT
    assert updated_card.id == original_card.id
    assert updated_card.title == body["title"]
    assert updated_card.summary == body["summary"]
    assert updated_card.state.value == original_card.state.value
    assert updated_card.priority.value == body["priority"]


@pytest.mark.num_cards(0)
async def test_update_multiple_fields(client, clean_db, sample_card):
    original_card = sample_card
    other_card_1 = Card(title="other 1")
    other_card_2 = Card(title="other 2")
    await original_card.save()
    await other_card_1.save()
    await other_card_2.save()

    body = {
        "title": "new test",
        "summary": "new summary",
        "priority": Priority.MEDIUM.value
    }

    response = await client.patch(f"/api/cards/{original_card.id}", json=body)
    updated_card = await Card.objects.get(id=original_card.id)

    assert response.status_code == status.HTTP_204_NO_CONTENT
    assert updated_card.id == original_card.id
    assert updated_card.title == body["title"]
    assert updated_card.summary == body["summary"]
    assert updated_card.state.value == original_card.state.value
    assert updated_card.priority.value == body["priority"]

    for other_card in [other_card_1, other_card_2]:
        db_other_card = await Card.objects.get(id=other_card.id)
        assert db_other_card == other_card
