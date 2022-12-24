"""Command Line Interface (CLI) for cards project."""
import api
import cli
from api.cards.client import SyncCardClient
from api.cards.models import CardCreate, CardUpdate, CardRead, Priority, State

from rich.console import Console
from rich.panel import Panel
from rich import box
from rich.table import Table
from rich.layout import Layout
import typer
import pendulum
import termcharts as tc
import datetime as dt


app = typer.Typer(add_completion=False)
console = Console(emoji=True)
client = SyncCardClient()


def make_cards_table(cards_: list[CardRead]):
    def format_dttm(dttm: pendulum.DateTime | None):
        return "" if dttm is None else dttm.strftime("%m/%d %I:%M %p")

    def format_priority(priority: Priority):
        style_map = {
            Priority.LOW: "[bold green]",
            Priority.MEDIUM: "[bold blue]",
            Priority.HIGH: "[bold bright_magenta]",
            Priority.URGENT: "[bold red]"
        }
        return f"{style_map.get(priority, '')}{priority.value}"

    def format_state(state: State):
        style_map = {
            State.TODO: "[bold blue]",
            State.IN_PROGRESS: "[bold green]",
            State.DONE: "[bold gray_74]",
        }
        return f"{style_map.get(state)}{state.value}"

    def get_row_style(card_: CardRead):
        return "dim" if card_.state == State.DONE else ""

    table = Table(
        title="My TODO List",
        expand=True,
        box=box.HEAVY_EDGE,
        header_style="bold magenta",
        title_style="bold green",
        highlight=True
    )

    table.add_column("ID", justify="center")
    table.add_column("Title", style="green", justify="left", width=20)
    table.add_column("Summary", justify="left", width=40)
    table.add_column("State", justify="right")
    table.add_column("Priority", justify="right")
    table.add_column("Created", justify="right")
    table.add_column("Started", justify="right")
    table.add_column("Finished", justify="right")

    cards_.sort(key=lambda x: (x.state, x.priority))

    for card in cards_:
        table.add_row(
            str(card.id),
            card.title,
            card.summary,
            format_state(card.state),
            format_priority(card.priority),
            format_dttm(card.created_dttm),
            format_dttm(card.started_dttm),
            format_dttm(card.finished_dttm),
            style=get_row_style(card)
        )

    return table


@app.callback(invoke_without_command=True)
def main(ctx: typer.Context):
    """
    Cards is a small command line task tracking application.
    """

    def make_layout() -> Layout:
        """Define the layout."""
        layout_ = Layout(name="root")

        layout_.split(
            Layout(name="spacer", size=2),
            Layout(name="header", size=2),
            Layout(name="main", ratio=1),
            Layout(name="footer", size=2),
        )

        layout_["main"].split_row(
            Layout(name="left_spacer", size=4),
            Layout(name="main_content", ratio=1),
            Layout(name="right_spacer", size=4)
        )

        layout_["main_content"].split_column(
            Layout(name="table_container", ratio=2),
            Layout(name="bottom"),

        )
        layout_["bottom"].split_row(
            Layout(name="left_chart"),
            Layout(name="right_chart")
        )
        layout_["spacer"].update("")
        layout_["header"].update(Panel(
            "",
            title="Daily TODO List & Time Tracker",
            style="black on green",
            box=box.SIMPLE,
            padding=1,
        ))
        layout_["left_spacer"].update(
            Panel(
                "",
                style="black on green",
                box=box.SIMPLE,
                padding=1,
            )
        )
        layout_["right_spacer"].update(
            Panel(
                "",
                style="white on green",
                box=box.SIMPLE,
                padding=1,
            )
        )
        layout_["footer"].update(
            Panel(
                "",
                style="white on green",
                box=box.SIMPLE,
                padding=1,
            )
        )
        return layout_

    def make_priority_chart():
        chart = [
            tc.bar({'roll': 24, 'bss':10, 'wes':30, 'ewfwef':50}, title='', rich=True)
        ]
        return Panel(chart[0], border_style="bright_green", expand=True)

    def make_state_chart():
        chart = [
            tc.bar({'roll': 24, 'bss':10, 'wes':30, 'ewfwef':50}, title='', rich=True)
        ]
        return Panel(chart[0], border_style="bright_green", expand=True)

    if ctx.invoked_subcommand is None:

        layout = make_layout()
        cards = client.get_cards()
        cards_table = make_cards_table(cards)
        priority_chart = make_priority_chart()
        state_chart = make_state_chart()
        layout["left_chart"].update(priority_chart)
        layout["right_chart"].update(state_chart)
        layout["table_container"].update(Panel(cards_table, border_style="bright_green"))
        console.print(layout)


@app.command()
def version():
    """Return version of cards application"""
    console.print({
        "API Version": api.__version__,
        "CLI Version": cli.__version__
    })


@app.command()
def add(
        *,
        title: str = typer.Argument(..., help="Title of the card"),
        summary: str = typer.Argument(..., help="Short summary of the card"),
        state: State = State.TODO,
        priority: Priority = Priority.LOW
):
    """
    Add a card to the to-do list
    """
    card = CardCreate(title=title, summary=summary, state=state, priority=priority)
    client.create_card(card)


@app.command()
def delete(card_id: int = typer.Argument(..., help="ID of the card you want to delete")):
    """
    Delete a card from the to-do list
    """
    client.delete_card(card_id)


@app.command()
def update(
        *,
        card_id: int = typer.Argument(..., help="ID of the card you want to update"),
        title: str = typer.Option(None, '-t', '--title', help="New title for the card"),
        summary: str = typer.Option(None, '-s', '--summary', help="New summary for the card"),
        priority: Priority = typer.Option(None, '-p', '--priority', help="New priority for the card")
):
    """
    Update a card on the to-do list
    """
    if all(option is None for option in [title, summary, priority]):
        console.print("[bold red]No updates provided")
        raise typer.Exit(0)

    update_data = CardUpdate()
    if title is not None:
        update_data.title = title

    if summary is not None:
        update_data.summary = summary

    if priority is not None:
        update_data.priority = priority

    client.update_card(card_id, card_updates=update_data)


@app.command()
def start(card_id: int = typer.Argument(..., help="ID of the card you want to start")):
    """
    Start a card on the to-do list
    """
    client.start_card(card_id)


@app.command()
def finish(card_id: int = typer.Argument(..., help="ID of the card you want to finish"),):
    """
    Finish a card on the to-do list
    """
    client.finish_card(card_id)


@app.command()
def count():
    """
    Count the cards on the to-do list
    """
    card_count = client.get_card_count()
    console.print(f"There are {card_count} cards in the database")


def datetime_to_pendulum_date(dttm: dt.datetime) -> pendulum.date:
    return pendulum.instance(dttm).date()


@app.command(name="list")
def list_(
        *,
        states: list[State] = typer.Option(None, '-s', '--states', help="States to filter results"),
        priorities: list[Priority] = typer.Option(None, '-p', '--priorities', help="Priorities to filter results"),
        lowest_create_date: dt.datetime = typer.Option(
            None,
            '-l',
            '--lowest-create-date',
            help="Lowest Date for filtering",
            formats=["%Y-%m-%d"],
        ),
        highest_create_date: dt.datetime = typer.Option(
            None,
            '-h',
            '--highest-create-date',
            help="Lowest Date for filtering",
            formats=["%Y-%m-%d"],
        )
):
    """
    List cards of different states and priorities
    """
    if lowest_create_date is not None:
        lowest_create_date = datetime_to_pendulum_date(lowest_create_date)

    if highest_create_date is not None:
        highest_create_date = datetime_to_pendulum_date(highest_create_date)

    cards = client.get_cards(
        highest_create_date=highest_create_date,
        lowest_create_date=lowest_create_date,
        states=states,
        priorities=priorities
    )
    cards_table = make_cards_table(cards)
    console.print(cards_table)
