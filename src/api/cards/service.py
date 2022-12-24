from ormar.exceptions import NoMatch
from .exceptions import invalid_card_id_exception
from .models import Card


async def valid_card_id(card_id: int):
    try:
        return await Card.objects.get(id=card_id)
    except NoMatch as e:
        raise invalid_card_id_exception from e
