from pathlib import Path
from sqlalchemy import text


async def load_permissions(container) -> None:
    sql_file = Path(__file__).parent.parent / "src" / "infrastructure" / "migrations" / "permissions.sql"

    if not sql_file.exists():
        print(f"Warning: {sql_file} not found, skipping permissions load")
        return

    sql_content = sql_file.read_text()

    async with container() as request_container:
        from sqlalchemy.ext.asyncio import AsyncSession
        session = await request_container.get(AsyncSession)

        try:
            statements = [
                stmt.strip()
                for stmt in sql_content.split(';')
                if stmt.strip() and not stmt.strip().startswith('--')
            ]

            for statement in statements:
                await session.execute(text(statement))

            await session.commit()
            print("Permissions loaded successfully")

        except Exception as e:
            await session.rollback()
            print(f"Error loading permissions: {e}")
