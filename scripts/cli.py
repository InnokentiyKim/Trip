import typer

from scripts.cli_tools.prepopulate_db import database_migration_app

app = typer.Typer()

app.add_typer(database_migration_app, name="database_data")


if __name__ == "__main__":
    app()
