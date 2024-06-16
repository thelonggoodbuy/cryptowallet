import asyncio
import typer
from db_config.database import init_models

cli = typer.Typer()


@cli.command()
def db_init_models():
    asyncio.run(init_models())
    print("Done")


if __name__ == "__main__":
    cli()
