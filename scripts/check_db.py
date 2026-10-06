from sqlalchemy import text

from app.db import engine

with engine.connect() as connection:
    row = connection.execute(
        text(
            "SELECT current_user, current_database(),"
            "current_setting('server_version')"
        )
    ).one()
    print(row)