from httpx import AsyncClient, Client, QueryParams
from fastapi import status
from api.cards.models import CardCreate, CardUpdate, CardRead, Priority, State
from api.config import get_settings
import pendulum

settings = get_settings()


class ClientError(Exception):
    pass


class InvalidCardIdError(ClientError):
    pass


class BadRequestError(ClientError):
    pass


class InternalServerError(ClientError):
    pass


STATUS_ERROR_MAP = {
    status.HTTP_404_NOT_FOUND: InvalidCardIdError,
    status.HTTP_422_UNPROCESSABLE_ENTITY: BadRequestError,
    status.HTTP_500_INTERNAL_SERVER_ERROR: InternalServerError
}


def raise_for_bad_status(response):
    error = STATUS_ERROR_MAP.get(response.status_code)
    if error is not None:
        raise error


class AsyncCardClient:
    def __init__(self):
        # self._client = AsyncClient(base_url="http://127.0.0.1:8000")
        self._client = AsyncClient(base_url=f"http://{settings.server.HOST}:{settings.server.PORT}")

    async def is_healthy(self) -> bool:
        response = await self._client.get("/api/health")
        raise_for_bad_status(response)

        return response.json()

    async def get_db_path(self) -> str:
        response = await self._client.get("/api/db/path")
        raise_for_bad_status(response)

        return response.json()

    async def create_card(self, card: CardCreate) -> CardRead:
        response = await self._client.post("/api/cards/", json=card.dict())
        raise_for_bad_status(response)

        return CardRead.from_dict(response.json())

    async def get_card(self, card_id: int) -> CardRead:
        response = await self._client.get(f"/api/cards/{card_id}")
        raise_for_bad_status(response)

        return CardRead.from_dict(response.json())

    async def delete_card(self, card_id: int) -> None:
        response = await self._client.delete(f"/api/cards/{card_id}")
        raise_for_bad_status(response)

    async def update_card(self, card_id: int, card_updates: CardUpdate) -> None:
        body = card_updates.dict(exclude_unset=True)
        response = await self._client.patch(f"/api/cards/{card_id}", json=body)
        raise_for_bad_status(response)

    async def get_card_count(self) -> int:
        response = await self._client.get("/api/cards/count/")
        raise_for_bad_status(response)

        return response.json().get("count")

    async def get_cards(
            self,
            lowest_create_date: pendulum.Date | None = None,
            highest_create_date: pendulum.Date | None = None,
            priorities: list[Priority] | None = None,
            states: list[State] | None = None
    ) -> list[CardRead]:
        query_params_data = {}
        if lowest_create_date is not None:
            query_params_data["lowest_create_date"] = lowest_create_date

        if highest_create_date is not None:
            query_params_data["highest_create_date"] = highest_create_date

        if priorities is not None:
            priority_values = [priority.value for priority in priorities]
            query_params_data["priorities"] = priority_values

        if states is not None:
            state_values = [state.value for state in states]
            query_params_data["states"] = state_values

        query_params = QueryParams(**query_params_data)
        response = await self._client.get("/api/cards/filter/", params=query_params)
        raise_for_bad_status(response)

        return [CardRead.from_dict(item) for item in response.json()["cards"]]

    async def start_card(self, card_id: int) -> None:
        response = await self._client.patch(f"/api/cards/start/{card_id}")
        raise_for_bad_status(response)

    async def finish_card(self, card_id: int) -> None:
        response = await self._client.patch(f"/api/cards/finish/{card_id}")
        raise_for_bad_status(response)

    async def close(self):
        if not self._client.is_closed:
            await self._client.aclose()


class SyncCardClient:
    def __init__(self):
        self._client = Client(base_url=f"http://{settings.server.HOST}:{settings.server.PORT}")

    def is_healthy(self) -> bool:
        response = self._client.get("/api/health")
        raise_for_bad_status(response)

        return response.json()

    def get_db_path(self) -> str:
        response = self._client.get("/api/db/path")
        raise_for_bad_status(response)

        return response.json()

    def create_card(self, card: CardCreate) -> CardRead:
        response = self._client.post("/api/cards/", json=card.dict())
        raise_for_bad_status(response)

        return CardRead.from_dict(response.json())

    def get_card(self, card_id: int) -> CardRead:
        response = self._client.get(f"/api/cards/{card_id}")
        raise_for_bad_status(response)

        return CardRead.from_dict(response.json())

    def delete_card(self, card_id: int) -> None:
        response = self._client.delete(f"/api/cards/{card_id}")
        raise_for_bad_status(response)

    def update_card(self, card_id: int, card_updates: CardUpdate) -> None:
        body = card_updates.dict(exclude_unset=True)
        response = self._client.patch(f"/api/cards/{card_id}", json=body)
        raise_for_bad_status(response)

    def get_card_count(self) -> int:
        response = self._client.get("/api/cards/count/")
        raise_for_bad_status(response)

        return response.json().get("count")

    def get_cards(
            self,
            lowest_create_date: pendulum.Date | None = None,
            highest_create_date: pendulum.Date | None = None,
            priorities: list[Priority] | None = None,
            states: list[State] | None = None
    ) -> list[CardRead]:
        query_params_data = {}
        if lowest_create_date is not None:
            query_params_data["lowest_create_date"] = lowest_create_date

        if highest_create_date is not None:
            query_params_data["highest_create_date"] = highest_create_date

        if priorities is not None:
            priority_values = [priority.value for priority in priorities]
            query_params_data["priorities"] = priority_values

        if states is not None:
            state_values = [state.value for state in states]
            query_params_data["states"] = state_values

        query_params = QueryParams(**query_params_data)
        response = self._client.get("/api/cards/filter/", params=query_params)
        raise_for_bad_status(response)

        return [CardRead.from_dict(item) for item in response.json()["cards"]]

    def start_card(self, card_id: int) -> None:
        response = self._client.patch(f"/api/cards/start/{card_id}")
        raise_for_bad_status(response)

    def finish_card(self, card_id: int) -> None:
        response = self._client.patch(f"/api/cards/finish/{card_id}")
        raise_for_bad_status(response)

