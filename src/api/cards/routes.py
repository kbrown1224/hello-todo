import pendulum
from fastapi import APIRouter, Depends, Query, status, Body, HTTPException
from .service import valid_card_id
from . import models
from loguru import logger
from textwrap import dedent

router = APIRouter(tags=["Cards"], prefix="/cards")


@router.post(
    "/",
    response_model=models.CardRead,
    status_code=status.HTTP_201_CREATED,
    description="Create a card in the description",
    response_description="Return created card object",
    summary="Create card",
)
async def create_card(card: models.CardCreate):
    db_card = models.Card.from_orm(card)

    if db_card.state == models.State.DONE:
        now = pendulum.now()
        db_card.started_dttm = now
        db_card.finished_dttm = now
    elif db_card.state == models.State.IN_PROGRESS:
        db_card.started_dttm = pendulum.now()

    await db_card.save()
    return db_card


@router.get(
    "/{card_id}",
    response_model=models.CardRead,
    status_code=status.HTTP_200_OK,
    description="Get a card in the description",
    response_description="Return card object",
    summary="Get card",
)
async def get_card(card: models.Card = Depends(valid_card_id)):
    return card


@router.delete(
    "/{card_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    description="Delete a card in the description",
    response_description="None",
    summary="Delete card",
)
async def delete_card(card: models.Card = Depends(valid_card_id)):
    await card.delete()


@router.patch(
    "/{card_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    description="Update a card in the description",
    response_description="None",
    summary="Update card",
)
async def update_card(*, card: models.Card = Depends(valid_card_id), card_update: models.CardUpdate):
    update_data = card_update.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(card, key, value)

    await card.update()

    return card


@router.get(
    "/count/",
    status_code=status.HTTP_200_OK,
    description="Count of cards in description",
    response_description="Integer count of cards",
    summary="Count cards",
)
async def count_cards():
    n = await models.Card.objects.count()
    return {"count": n}


@router.get(
    "/filter/",
    response_model=models.FilteredCards,
    status_code=status.HTTP_200_OK,
    description="Read cards in the description",
    response_description="List of cards",
    summary="Read cards",
)
async def filter_cards(
        *,
        states: list[models.State] = Query(None),
        priorities: list[models.Priority] = Query(None),
        lowest_create_date: pendulum.Date = Query(None),
        highest_create_date: pendulum.Date = Query(None)
):
    logger.debug(
        "Read Card Filters\n"
        "states={states};\n"
        "priorities={priorities};\n"
        "lowest_create_date={lowest_create_date}\n"
        "highest_create_date={highest_create_date}",
        states=states,
        priorities=priorities,
        lowest_create_date=lowest_create_date,
        highest_create_date=highest_create_date
    )

    if lowest_create_date and highest_create_date and lowest_create_date > highest_create_date:
        logger.error(
            "Bad dates in filters;\n"
            "lowest_create_date={lcd}\n"
            "highest_create_date={hcd}",
            lcd=lowest_create_date,
            hcd=highest_create_date
        )

        error_message = "Bad dates provided, highest_create_date must be after lowest_create_date"
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error_message
        )

    query = models.Card.objects
    filters = []
    if states is not None:
        query = query.filter(models.Card.state.in_(states))
        filters.append(
            models.Filter(
                field="state",
                operator=models.Operator.IN,
                value=states
            )
        )

    if priorities is not None:
        query = query.filter(models.Card.priority.in_(priorities))
        filters.append(
            models.Filter(
                field="priority",
                operator=models.Operator.IN,
                value=priorities
            )
        )

    if lowest_create_date is not None:
        query = query.filter(models.Card.created_dttm >= lowest_create_date)
        filters.append(
            models.Filter(
                field="created_dttm",
                operator=models.Operator.GREATER_THAN,
                value=lowest_create_date
            )
        )

    if highest_create_date is not None:
        query = query.filter(models.Card.created_dttm <= highest_create_date)
        filters.append(
            models.Filter(
                field="created_dttm",
                operator=models.Operator.LESS_THAN,
                value=highest_create_date
            )
        )

    cards = await query.all()

    return models.FilteredCards(offset=0, filters=filters, cards=cards)


@router.patch(
    "/start/{card_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    description="Start a card in the description",
    response_description="None",
    summary="Start card",
)
async def start_card(card: models.Card = Depends(valid_card_id)):
    card.state = models.State.IN_PROGRESS
    card.started_dttm = pendulum.now()
    await card.update()


@router.patch(
    "/finish/{card_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    description="Finish a card in the description",
    response_description="None",
    summary="Finish card",
)
async def finish_card(card: models.Card = Depends(valid_card_id)):
    if card.state == models.State.TODO:
        card.started_dttm = pendulum.now()

    card.state = models.State.DONE
    card.finished_dttm = pendulum.now()

    await card.update()
