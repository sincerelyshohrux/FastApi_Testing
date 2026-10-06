from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env")

    # Ishchi baza: server (fastapi dev) shu bazaga yozadi.
    database_url: str = (
        "postgresql+psycopg://postgres:postgres@localhost:5432/cars"
    )

    # Test bazasi: ishchi bazadan boshqa bo'lishi SHART.
    test_database_url: str = (
        "postgresql+psycopg://postgres:postgres@localhost:5432/cars_test"
    )

    # Yozish amallari uchun kalit ("X-API-Key" header).
    api_key: str = "dev-api-key"

    # True bo'lsa har SQL konsolga chiqadi (SQL_ECHO=1).
    sql_echo: bool = False


settings = Settings()