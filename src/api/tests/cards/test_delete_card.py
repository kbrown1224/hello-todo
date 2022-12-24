"""
Test Cases
* `delete /cards/{card_id}` empty database
* `delete /cards/{card_id}` one card database
* `delete /cards/{card_id}` many card database
"""
import pytest
from fastapi import status
from api.cards.models import Card, State, Priority

pytestmark = pytest.mark.anyio


@pytest.mark.num_cards(0)
async def test_delete_no_ticket(client, clean_db):
    response = await client.delete("/api/cards/1")
    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.num_cards(0)
async def test_delete_ticket_from_one(client, clean_db):
    card = Card(title="test", summary="test summary", state=State.TODO, priority=Priority.LOW)
    await card.save()

    response = await client.delete(f"/api/cards/{card.id}")
    card_exists = await Card.objects.filter(id=card.id).exists()

    assert response.status_code == status.HTTP_204_NO_CONTENT
    assert not card_exists


@pytest.mark.num_cards(0)
async def test_delete_ticket_from_many(client, clean_db):
    card_1 = Card(title="test 1", summary="test summary 1", state=State.TODO, priority=Priority.LOW)
    card_2 = Card(title="test 2", summary="test summary 2", state=State.TODO, priority=Priority.LOW)
    card_3 = Card(title="test 3", summary="test summary 3", state=State.TODO, priority=Priority.LOW)
    await card_1.save()
    await card_2.save()
    await card_3.save()

    initial_count = await Card.objects.count()

    delete_card_id = card_1.id
    remain_card_ids = [card_2.id, card_3.id]

    response = await client.delete(f"/api/cards/{delete_card_id}")

    final_count = await Card.objects.count()
    card_exists = await Card.objects.filter(id=card_1.id).exists()

    assert response.status_code == status.HTTP_204_NO_CONTENT
    assert not card_exists
    assert initial_count == 3
    assert final_count == 2

    for card_id in remain_card_ids:
        card = await Card.objects.get(id=card_id)
        assert card is not None
