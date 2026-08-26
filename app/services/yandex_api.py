import io
from datetime import datetime, timedelta
from typing import Any, List

import xlsxwriter

from app.core.config import settings
from app.core.yandex_client import YandexDiskClient


def format_time_delta(delta: timedelta) -> str:
    total_minutes = int(delta.total_seconds() // 60)
    days = total_minutes // (24 * 60)
    hours = (total_minutes % (24 * 60)) // 60
    minutes = total_minutes % 60
    if days:
        return f'{days} дн. {hours} ч.'
    return f'{hours} ч. {minutes} мин.'


async def create_simple_report(
    charity_projects: List[Any],
    yandex_client: YandexDiskClient,
    folder: str = 'QRKot Reports'
) -> str:
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
    title_format = workbook.add_format({'bold': True, 'font_size': 14})
    header_format = workbook.add_format({
        'bold': True,
        'bg_color': '#2F75B5',
        'font_color': 'white',
        'border': 1,
        'align': 'left'
    })
    cell_format = workbook.add_format({'border': 1, 'align': 'left'})
    total_cell_format = workbook.add_format(
        {'bold': True, 'border': 1, 'align': 'left'}
    )
    worksheet.merge_range('A1:C1', f'Отчёт от {now_date_time}', title_format)
    for col, header in enumerate(
        ['Название проекта', 'Время сбора', 'Описание']
    ):
        worksheet.write(1, col, header, header_format)
    current_row = 2
    for project in charity_projects:
        duration = format_time_delta(project.close_date - project.create_date)
        worksheet.write(current_row, 0, project.name, cell_format)
        worksheet.write(current_row, 1, duration, cell_format)
        worksheet.write(current_row, 2, project.description, cell_format)
        current_row += 1
    worksheet.merge_range(
        current_row, 0,
        current_row, 2,
        f'Всего проектов: {len(charity_projects)}',
        total_cell_format
    )
    worksheet.set_column('A:A', 30)
    worksheet.set_column('B:B', 20)
    worksheet.set_column('C:C', 40)
    workbook.close()
    output.seek(0)
    await yandex_client.upload_file(upload_url, output.getvalue())
    public_url = await yandex_client.publish_file(file_path)
    return public_url
