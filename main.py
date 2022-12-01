import importlib
from typing import Optional
import typer

app = typer.Typer()


@app.command()
def run(day: Optional[int] = None):
    """Run the code for a certain day."""
    if day:
        module = importlib.import_module(f"d{day}")
        typer.echo(f"day {day}: {module.run()}")
        return

    for day in range(1, 26):
        try:
            module = importlib.import_module(f"d{day}")
        except ModuleNotFoundError:
            return
        typer.echo(f"day {day}: {module.run()}")


if __name__ == "__main__":
    app()
