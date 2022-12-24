from textual.app import App, ComposeResult
from textual.widgets import Header, Footer, Button, Static, Placeholder
from textual import events, log
from textual.containers import Vertical, Horizontal, Container
from textual.widget import Widget
from textual.reactive import reactive
from textual.message import Message, MessageTarget
from api.cards.client import SyncCardClient
from api.cards.models import CardRead, State



class Title(Static):
    DEFAULT_CSS = """
    Title {
        content-align: center middle;
        text-opacity: 80%;
        color: auto;
        padding: 0;
        border: hkey white;
    }
    """


class CardList(Vertical):
    DEFAULT_CSS = """
    CardList {
        height: 100%;
        width: 32%;
        row-span: 2;
        margin-top: 2;
        margin-left: 3;
        margin-right: 3;
    }
    """

    def __init__(
            self, title,
            *children: Widget,
            name: str | None = None,
            id: str | None = None,
            classes: str | None = None,
    ):
        super().__init__(Title(title), *children, id=id, classes=classes, name=name)



class CardMiniTitle(Static):
    pass


class BaseButton(Button):
    DEFAULT_CSS = """
    BaseButton {
        height: 100%;
        width: 50%;
        margin-right: 2;
        margin-left: 2;
    }
    """


class InfoButton(BaseButton):
    DEFAULT_CLASSES = "bg-dark"

    class Selected(Message):
        """Color selected message."""

        def __init__(self, sender: MessageTarget, card: CardRead) -> None:
            self.card = card
            super().__init__(sender)

    def __init__(
            self,
            card: CardRead = None,
            *,
            name: str | None = None,
            id: str | None = None,
            classes: str | None = None,
    ):
        super().__init__(label="Info", disabled=False, name=name, id=id, classes=classes)
        self.card = card

    async def on_click(self, event: events.Click) -> None:
        log(event)
        log(f"info button clicked - {self.card.id}")
        await self.emit(self.Selected(self, self.card))


class StartButton(BaseButton):
    DEFAULT_CLASSES = "bg-blue"

    def __init__(
            self,
            card: CardRead = None,
            *,
            name: str | None = None,
            id: str | None = None,
            classes: str | None = None,
    ):
        super().__init__(label="Start", disabled=False, name=name, id=id, classes=classes)
        self.card = card

    def on_click(self, event: events.Click) -> None:
        log(event)
        log("start button clicked")


class FinishButton(BaseButton):
    DEFAULT_CLASSES = "bg-green"

    def __init__(
            self,
            card: CardRead = None,
            *,
            name: str | None = None,
            id: str | None = None,
            classes: str | None = None,
    ):
        super().__init__(label="Finish", disabled=False, name=name, id=id, classes=classes)
        self.card = card


    def on_click(self, event: events.Click) -> None:
        log(event)
        log("finish button clicked")


class CardMini(Static):
    DEFAULT_CSS = """
    CardMini {
        color: auto;
        border: white;
        margin-left: 2;
        margin-right: 2;
        height: 6;
    }
    """

    def __init__(self, card: CardRead) -> None:
        super().__init__(card.title)
        self.card = card

    def on_click(self) -> None:
        log(self.card.id)

    def compose(self) -> ComposeResult:
        info_button = InfoButton(card=self.card)
        match self.card.state:
            case State.TODO:
                button_row = Horizontal(info_button, StartButton(card=self.card))
            case State.IN_PROGRESS:
                button_row = Horizontal(info_button, FinishButton(card=self.card))
            case State.DONE:
                button_row = Horizontal(info_button)
            case _:
                button_row = Horizontal(info_button)

        yield CardMiniTitle(self.card.title)
        yield button_row


class CardDetails(Static):
    DEFAULT_CSS = """
    CardDetails {
        border: heavy white;
        height: 100%
    }
    """

    selected_card: reactive[CardRead | None] = reactive(None)
    title = reactive("")

    def compute_title(self):
        return self.selected_card.title if self.selected_card is not None else "Something else here"

    def compose(self) -> ComposeResult:
        yield Static(self.title, id="test-details")


class CardsApp(App):
    CSS_PATH = "app.css"
    BINDINGS = [("q", "request_quit", "Quit")]
    client = SyncCardClient()
    selected_card = reactive(None)

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        yield Container(
            Horizontal(
                CardList(id="todo-list", title="ToDo", classes="bg-dark"),
                CardList(id="in-progress-list", title="In Progress", classes="bg-blue"),
                CardList(id="done-list", title="Done", classes="bg-green"),
                id="board-container",
            ),
            Horizontal(CardDetails("Details Here", id="card-details")),
            id="screen-container",
        )
        yield Footer()

    def load_cards(self, cards_: list[CardRead], list_id: str, state: State) -> None:
        list_widget = self.query_one(list_id)
        filtered_cards = [card for card in cards_ if card.state == state]
        for card in filtered_cards:
            list_widget.mount(CardMini(card))

    def on_mount(self) -> None:
        cards = self.client.get_cards()

        self.load_cards(cards, "#todo-list", State.TODO)
        self.load_cards(cards, "#in-progress-list", State.IN_PROGRESS)
        self.load_cards(cards, "#done-list", State.DONE)

    def action_request_quit(self) -> None:
        self.exit()

    def on_info_button_selected(self, message: InfoButton.Selected) -> None:
        log(message.card)
        self.query_one(CardDetails).selected_card = message.card
        self.query_one(CardDetails).refresh()


if __name__ == "__main__":
    CardsApp().run()
