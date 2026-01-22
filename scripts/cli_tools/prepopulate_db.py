import asyncio
from decimal import Decimal
from pathlib import Path
from typing import Annotated

import typer
from sqlalchemy import text
from sqlalchemy.exc import IntegrityError

from src.apps.authentication.user.domain.models import User
from src.apps.hotel.hotels.domain.models import Hotel
from src.apps.hotel.rooms.domain.models import Room
from src.common.interfaces import SecurityGatewayProto
from src.config import create_configs
from src.ioc.registry import get_providers
from src.setup.common import create_async_container

database_migration_app = typer.Typer(help="Postgres data migration commands")
config = create_configs()


async def _load_permissions() -> None:
    """Load base permissions from SQL file into the database."""
    async_container = create_async_container(get_providers(), config=config)
    sql_file = Path(__file__).parent.parent.parent / "src" / "infrastructure" / "migrations" / "permissions.sql"

    if not sql_file.exists():
        typer.secho(
            f"Warning: {sql_file} not found, skipping permissions load",
            fg=typer.colors.YELLOW,
            bold=True,
        )
        return

    sql_content = sql_file.read_text()

    async with async_container() as request_container:
        from sqlalchemy.ext.asyncio import AsyncEngine

        engine = await request_container.get(AsyncEngine)

        async with engine.begin() as conn:
            raw_conn = await conn.get_raw_connection()

            try:
                await raw_conn.driver_connection.execute(sql_content)
                typer.secho("Permissions loaded successfully", fg=typer.colors.BLUE)

            except Exception as exc:
                typer.secho("Error loading permissions", fg=typer.colors.RED)
                raise exc


async def _load_samples() -> None:
    """Load sample data into the database."""
    async_container = create_async_container(get_providers(), config=config)

    async with async_container() as request_container:
        from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession

        engine = await request_container.get(AsyncEngine)
        security = await request_container.get(SecurityGatewayProto)

        async with AsyncSession(engine) as session:
            result = await session.execute(text("SELECT id FROM roles WHERE name = 'manager'"))
            manager_role_id = result.scalar_one_or_none()

            if not manager_role_id:
                typer.secho("Error: Manager role not found", fg=typer.colors.RED, bold=True)
                return

            managers = []
            sample_password: str = await security.hash_password("Password123")

            try:
                for i in range(1, 4):
                    manager = User(
                        email=f"manager{i}@hotel.com",
                        hashed_password=sample_password,
                        role_id=manager_role_id,
                        name=f"Manager {i}",
                        phone=f"+7900000000{i}",
                        is_active=True,
                    )
                    session.add(manager)
                    managers.append(manager)

                await session.flush()

                hotels_data = [
                    {
                        "name": "Grand Palace Hotel",
                        "location": "Moscow, Red Square",
                        "services": {
                            "wifi": True,
                            "parking": True,
                            "pool": True,
                            "gym": True,
                        },
                    },
                    {
                        "name": "Seaside Resort",
                        "location": "Sochi, Beach Boulevard",
                        "services": {
                            "wifi": True,
                            "beach": True,
                            "spa": True,
                            "restaurant": True,
                        },
                    },
                    {
                        "name": "Mountain View Lodge",
                        "location": "Krasnaya Polyana, Mountain Road",
                        "services": {
                            "wifi": True,
                            "ski": True,
                            "sauna": True,
                            "bar": True,
                        },
                    },
                ]

                rooms_templates = [
                    {
                        "name": "Standard Room",
                        "price": Decimal("2500.00"),
                        "services": {"wifi": True, "tv": True},
                    },
                    {
                        "name": "Deluxe Room",
                        "price": Decimal("4000.00"),
                        "services": {"wifi": True, "tv": True, "minibar": True},
                    },
                    {
                        "name": "Suite",
                        "price": Decimal("7500.00"),
                        "services": {
                            "wifi": True,
                            "tv": True,
                            "minibar": True,
                            "jacuzzi": True,
                        },
                    },
                    {
                        "name": "Family Room",
                        "price": Decimal("5500.00"),
                        "services": {"wifi": True, "tv": True, "kitchen": True},
                    },
                    {
                        "name": "Presidential Suite",
                        "price": Decimal("15000.00"),
                        "services": {
                            "wifi": True,
                            "tv": True,
                            "minibar": True,
                            "jacuzzi": True,
                            "balcony": True,
                        },
                    },
                ]

                for manager, hotel_data in zip(managers, hotels_data, strict=False):
                    hotel = Hotel(
                        name=hotel_data["name"],
                        location=hotel_data["location"],
                        services=hotel_data["services"],
                        rooms_quantity=10,
                        owner=manager.id,
                        is_active=True,
                    )
                    session.add(hotel)
                    await session.flush()

                    for room_template in rooms_templates:
                        room = Room(
                            hotel_id=hotel.id,
                            owner=manager.id,
                            name=room_template["name"],
                            description=f"Comfortable {room_template['name'].lower()} at {hotel.name}",
                            price=room_template["price"],
                            services=room_template["services"],
                            image_id=None,
                            quantity=2,
                        )
                        session.add(room)

                await session.commit()
                typer.secho("Sample data loaded successfully", fg=typer.colors.BLUE)

            except IntegrityError:
                typer.secho(
                    "Sample data already exists in database. Skipping...",
                    fg=typer.colors.YELLOW,
                )


async def load_permissions() -> None:
    """Load base permissions into the database."""
    await _load_permissions()


async def load_samples() -> None:
    """Load sample data into the database."""
    await _load_samples()


async def _migrate(load_samples: bool = False) -> None:
    """Migrate data into the database."""
    typer.secho("=" * 80, fg=typer.colors.CYAN)
    typer.secho("Starting data migration...", fg=typer.colors.CYAN, bold=True)
    typer.secho("=" * 80, fg=typer.colors.CYAN)

    try:
        await _load_permissions()

        if load_samples:
            await _load_samples()

        typer.secho("=" * 80, fg=typer.colors.GREEN)
        typer.secho("All data migrated successfully!", fg=typer.colors.GREEN, bold=True)
        typer.secho("=" * 80, fg=typer.colors.GREEN)

    except Exception as exc:
        typer.secho(f"Migration failed: {exc}", fg=typer.colors.RED, bold=True)
        raise typer.Exit(1) from exc


@database_migration_app.command("migrate")
def migrate(
    load_samples: Annotated[bool, typer.Option(help="Prepopulate database with samples.")] = False,
) -> None:
    """Prepopulate database with base permissions and samples."""
    try:
        load_samples = load_samples or False
        asyncio.run(_migrate(load_samples=load_samples))
    except typer.Exit:
        raise
    except Exception as exc:
        typer.secho(f"Unexpected error: {exc}", fg=typer.colors.RED)
        raise typer.Exit(1) from exc
