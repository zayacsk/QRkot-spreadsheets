from typing import Optional

from pydantic import EmailStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_title: str = 'Благотворительный фонд поддержки котиков QRKot'
    app_description: str = 'Сервис для поддержки котиков'
    database_url: str | None = 'sqlite+aiosqlite:///./cat_charity.db'
    secret: str = 'SECRET'
    first_superuser_email: Optional[EmailStr] = 'root@admin.ru'
    first_superuser_password: Optional[str] = 'root'
    yandex_disk_token: Optional[str] = None
    report_format: str = '%Y.%m.%d %H:%M:%S'
    model_config = SettingsConfigDict(env_file='.env')


settings = Settings()
