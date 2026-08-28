import io
from datetime import datetime, timedelta
from typing import Any

import xlsxwriter

from app.core.config import settings
from app.core.yandex_client import YandexDiskClient

TITLE_FORMAT = {
    'bold': True,
    'font_size': 14,
}

HEADER_FORMAT = {
    'bold': True,
    'bg_color': '#2F75B5',
    'font_color': 'white',
    'border': 1,
    'align': 'left',
}

CELL_FORMAT = {
    'border': 1,
    'align': 'left',
}

TOTAL_CELL_FORMAT = {
    'bold': True,
    'border': 1,
    'align': 'left',
}

HEADERS = ['Название проекта', 'Время сбора', 'Описание']

MAX_EXCEL_ROWS = 1_048_576
SERVICE_ROWS_COUNT = 4
MAX_PROJECTS_COUNT = MAX_EXCEL_ROWS - SERVICE_ROWS_COUNT

ERROR_NO_PROJECTS = 'Список проектов пуст. Нет данных для отчета'
ERROR_PROJECTS_LIMIT = 'Количество проектов: {} превышает лимит строк Excel {}'


def format_time_delta(delta: timedelta) -> str:
    total_minutes = int(delta.total_seconds() // 60)
    days = total_minutes // (24 * 60)
    hours = (total_minutes % (24 * 60)) // 60
    minutes = total_minutes % 60
    if days:
        return f'{days} дн. {hours} ч.'
    return f'{hours} ч. {minutes} мин.'


async def create_simple_report(
    charity_projects: list[Any],
    yandex_client: YandexDiskClient,
    folder: str = 'QRKot Reports'
) -> str:
    if not charity_projects:
        raise ValueError(ERROR_NO_PROJECTS)
    if len(charity_projects) > MAX_PROJECTS_COUNT:
        raise ValueError(ERROR_PROJECTS_LIMIT.format(
            len(charity_projects), MAX_PROJECTS_COUNT
        ))
    now = datetime.now()
    now_date_time = now.strftime(settings.report_format)
    safe_filename = f'Отчет_{now_date_time}'.replace(
        ':', '-').replace(' ', '_').replace('/', '-')
    upload_url, file_path = await yandex_client.create_excel_file(
        safe_filename, folder
    )
    output = io.BytesIO()
    workbook = xlsxwriter.Workbook(output)
    worksheet = workbook.add_worksheet('Отчет')
    title_format = workbook.add_format(TITLE_FORMAT)
    header_format = workbook.add_format(HEADER_FORMAT)
    cell_format = workbook.add_format(CELL_FORMAT)
    total_cell_format = workbook.add_format(TOTAL_CELL_FORMAT)
    worksheet.merge_range('A1:C1', f'Отчёт от {now_date_time}', title_format)
    for col, header in enumerate(HEADERS):
        worksheet.write(1, col, header, header_format)
    for row, project in enumerate(charity_projects, start=2):
        duration = format_time_delta(project.close_date - project.create_date)
        worksheet.write(row, 0, project.name, cell_format)
        worksheet.write(row, 1, duration, cell_format)
        worksheet.write(row, 2, project.description, cell_format)
    total_row = len(charity_projects) + 2
    worksheet.merge_range(
        total_row, 0,
        total_row, 2,
        f'Всего проектов: {len(charity_projects)}',
        total_cell_format
    )
    worksheet.set_column('A:A', 30)
    worksheet.set_column('B:B', 20)
    worksheet.set_column('C:C', 40)
    workbook.close()
    output.seek(0)
    await yandex_client.upload_file(upload_url, output.getvalue())
    return await yandex_client.publish_file(file_path)
