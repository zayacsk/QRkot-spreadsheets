from typing import Optional

import httpx
from fastapi import HTTPException, status

from app.core.config import settings

ERROR_UPLOAD_HREF_NOT_FOUND = 'Не удалось получить ссылку для загрузки'
ERROR_PUBLIC_URL_NOT_FOUND = 'Ссылка не была получена со стороны Яндекс Диска'
ERROR_TOKEN_MISSING = (
    'Яндекс Диск не настроен. Пожалуйста, '
    'добавьте YANDEX_DISK_TOKEN в .env-файл'
)
YANDEX_DISK_HEADERS = {
    'Authorization': f'OAuth {settings.yandex_disk_token}'
}
UPLOAD_URL = f'{settings.yandex_disk_base_url}/resources/upload'
PUBLISH_URL = f'{settings.yandex_disk_base_url}/resources/publish'
RESOURCES_URL = f'{settings.yandex_disk_base_url}/resources'
EXCEL_CONTENT_TYPE = (
    'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
)


class YandexDiskClient:
    def __init__(self):
        self._client: Optional[httpx.AsyncClient] = None

    async def __aenter__(self):
        self._client = httpx.AsyncClient(timeout=30.0)
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self._client:
            await self._client.aclose()

    async def create_excel_file(
        self,
        title: str,
        folder: str = 'Reports'
    ) -> tuple[str, str]:
        await self._create_folder(folder)
        file_path = f'disk:/{folder}/{title}.xlsx'
        response = await self._client.get(
            UPLOAD_URL,
            headers=YANDEX_DISK_HEADERS,
            params={'path': file_path, 'overwrite': 'true'}
        )
        response.raise_for_status()
        return response.json()['href'], file_path

    async def upload_file(
        self,
        upload_url: str,
        content: bytes
    ):
        response = await self._client.put(
            upload_url,
            content=content,
            headers={'Content-Type': EXCEL_CONTENT_TYPE}
        )
        response.raise_for_status()

    async def publish_file(self, file_path: str) -> str:
        response = await self._client.put(
            PUBLISH_URL,
            headers=YANDEX_DISK_HEADERS,
            params={'path': file_path}
        )
        response.raise_for_status()
        response = await self._client.get(
            RESOURCES_URL,
            headers=YANDEX_DISK_HEADERS,
            params={'path': file_path}
        )
        response.raise_for_status()
        return response.json()['public_url']

    async def _create_folder(self, folder: str):
        try:
            await self._client.put(
                RESOURCES_URL,
                headers=YANDEX_DISK_HEADERS,
                params={'path': f'disk:/{folder}'}
            )
        except httpx.HTTPStatusError as error:
            if error.response.status_code != status.HTTP_409_CONFLICT:
                raise


async def get_yandex_client():
    if settings.yandex_disk_token is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=ERROR_TOKEN_MISSING
        )
    async with YandexDiskClient() as client:
        yield client
