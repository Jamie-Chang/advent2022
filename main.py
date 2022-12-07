import importlib
from typing import Optional
import typer

from common import get_input

app = typer.Typer()


@app.command()
def run(day: Optional[int] = None):
    """Run the code for a certain day."""
    if day:
        module = importlib.import_module(f"d{day}")
        typer.echo(f"day {day}: {module.run(get_input(day=day))}")
        return

    for day in range(1, 26):
        try:
            module = importlib.import_module(f"d{day}")
        except ModuleNotFoundError:
            return
        typer.echo(f"day {day}: {module.run(get_input(day=day))}")


if __name__ == "__main__":
    app()
