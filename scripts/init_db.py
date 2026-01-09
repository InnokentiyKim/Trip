from pathlib import Path


async def load_permissions(container) -> None:
    sql_file = Path(__file__).parent.parent / "src" / "infrastructure" / "migrations" / "permissions.sql"

    if not sql_file.exists():
        print(f"Warning: {sql_file} not found, skipping permissions load")
        return

    sql_content = sql_file.read_text()

    async with container() as request_container:
        from sqlalchemy.ext.asyncio import AsyncEngine
        engine = await request_container.get(AsyncEngine)

        async with engine.begin() as conn:
            raw_conn = await conn.get_raw_connection()

            try:
                await raw_conn.driver_connection.execute(sql_content)
                print("Permissions loaded successfully")

            except Exception as e:
                print(f"Error loading permissions: {e}")
