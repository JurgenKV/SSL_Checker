import csv

from openpyxl.worksheet.worksheet import Worksheet

import CONST_COLUMN as CONST


from openpyxl import Workbook
from openpyxl.styles import PatternFill, Font
from pathlib import Path
from typing import List, Dict

from SSLRequest import get_certificate_data
from UI import change_progress_ui
from TimeUtils import get_ssl_datetime_state

from UI import get_include_Success, get_include_warning, get_include_Error
# const style color
EXPIRE_FILL = PatternFill(start_color="F8CBAD", end_color="F8CBAD", fill_type="solid")  # Красный фон (ошибка)
SUCCESS_FILL = PatternFill(start_color="ABF5D1", end_color="ABF5D1", fill_type="solid")  # Зелёный фон (успех)
WARNING_FILL = PatternFill(start_color="FFF0B3", end_color="FFF0B3", fill_type="solid")
ERROR_FILL = PatternFill(start_color="FFBDAD", end_color="FFBDAD", fill_type="solid")
BLACK_FILL = PatternFill(start_color="000000", end_color="000000", fill_type="solid")

BOLD_FILL = Font(bold=True)

class SectionsState:
    Expire_section = False
    Warning_section = False
    Error_section = False
    Success_section = False

    def __init__(self, expire, warning, error, success):
        self.Expire_section = expire
        self.Warning_section = warning
        self.Error_section = error
        self.Success_section = success

def load_csv(file):
    original_path = Path(file)

    if not original_path.is_file():
        raise FileNotFoundError(f"Файл не найден: {file}")

    #return csv_to_excel_manual(original_path)
    return original_path

def get_csv_data_dict(copy_file_path):
    with open(copy_file_path, mode='r', encoding='cp1251', newline='') as f:
        reader = csv.DictReader(f,delimiter=';')
        data = list(reader)  # список словарей
        return data

def get_new_csv_data_with_ssl(list_of_dicts):
    i = 0
    for dictionary in list_of_dicts:

        if dictionary[CONST.NAME] is None:
            break

        ssl_data = get_certificate_data(dictionary[CONST.NAME])
        if ssl_data is not None:
            dictionary[CONST.DOMAIN_NAME] = ssl_data.domain
            dictionary[CONST.END_DATE] = ssl_data.end_date
            print(ssl_data.domain)
        else:
            dictionary[CONST.INFO] = CONST.SSL_ERROR_TEMPLATE
        i+=1
        change_progress_ui(len(list_of_dicts), i)

    return list_of_dicts

def save_completed_excel(list_of_dicts: List[Dict], output_path: Path):
    if not list_of_dicts:
        raise ValueError("Нет данных для сохранения")

    output_file_path = output_path.parent / "output.xlsx"

    # Создаём новую книгу Excel
    wb = Workbook()
    # Создаем первую страницу со статусами SSL
    create_ssl_page_output(wb, list_of_dicts)
    # Создаем вторую страницу с распределением по владельцам доменов
    create_owner_ssl_page_output(wb, list_of_dicts)
    # Создаем третью страницу с распределением по админам доменов
    create_admin_ssl_page_output(wb, list_of_dicts)
    # Сохраняем
    wb.save(output_file_path)
    print(f"Результат сохранён в: {output_file_path}")
    return output_file_path

def create_ssl_page_output(wb: Workbook, list_of_dicts: List[Dict]):
    ws = wb.active
    ws.title = "Результаты SSL"

    # Заголовки
    headers = list(list_of_dicts[0].keys())
    ws.append(headers)

    # Форматируем заголовки
    for col in range(1, len(headers) + 1):
        ws.cell(row=1, column=col).font = BOLD_FILL

    # Заполняем строки и применяем цвета
    for row_idx, row_data in enumerate(list_of_dicts, start=2):
        for col_idx, header in enumerate(headers, start=1):
            value = row_data.get(header, "")
            cell = ws.cell(row=row_idx, column=col_idx, value=value)

            # Пример: раскраска всей строки, если в колонке INFO есть ошибка
            if header == CONST.INFO and CONST.SSL_ERROR_TEMPLATE in str(value):
                # Раскрасить ВСЮ строку в красный
                # for c in range(1, len(headers) + 1):
                #     ws.cell(row=row_idx, column=c).fill = error_fill
                # break
                cell.fill = ERROR_FILL
            elif header == CONST.END_DATE and value:
                # Можно раскрасить только ячейку с датой, например, зелёным
                code = get_ssl_datetime_state(value)
                if code == 0:
                    cell.fill = SUCCESS_FILL
                    for c in range(1, len(headers) + 1):
                        ws.cell(row=row_idx, column=c).fill = SUCCESS_FILL
                elif code == 1:
                    cell.fill = SUCCESS_FILL
                elif code == 2:
                    cell.fill = WARNING_FILL
                else:
                    for c in range(1, len(headers) + 1):
                        ws.cell(row=row_idx, column=c).fill = EXPIRE_FILL


def create_owner_ssl_page_output(wb: Workbook, list_of_dicts: List[Dict]):
    """
    Создает лист с отчетом, сгруппированным по владельцам.
    """
    ws_owners = wb.create_sheet(title="По Владельцам")
    current_row = 1  # Текущая строка для записи данных

    # Получаем список уникальных владельцев
    owners = get_owners_list(list_of_dicts)

    # Формируем отчет для каждого владельца
    for owner in owners:
        section_state = SectionsState(
            is_contain_section_values(list_of_dicts, owner, 2, True),
            is_contain_section_values(list_of_dicts, owner, 1, True),
            is_contain_section_values(list_of_dicts, owner, 3, True),
            is_contain_section_values(list_of_dicts, owner, 0, True)
        )
        # Заголовок администратора
        if (section_state.Expire_section == 0 and
                (section_state.Warning_section & get_include_warning()) == 0 and
                (section_state.Error_section & get_include_Error()) == 0 and
                (section_state.Success_section & get_include_Success()) == 0):
            continue

        #if section_state.Expire_section == 0 and section_state.Warning_section == 0 and section_state.Error_section == 0:
        #    continue

        ws_owners.cell(row=current_row, column=1, value=owner).font = BOLD_FILL
        current_row += 1
        # Добавляем домены в зоне ERROR (code == 2)
        if section_state.Expire_section:
            for c in range(1, 5):
                ws_owners.cell(row=current_row, column=c, value="EXPIRE").fill = EXPIRE_FILL
            current_row += 1
            current_row = get_section_by_state(list_of_dicts, ws_owners, owner, 2, current_row, True)
        # Добавляем домены в зоне WARNING (code == 1)
        if section_state.Warning_section and get_include_warning():
            for c in range(1, 5):
                ws_owners.cell(row=current_row, column=c, value="WARNING").fill = WARNING_FILL
            current_row += 1
            current_row = get_section_by_state(list_of_dicts, ws_owners, owner, 1, current_row,True)
        if section_state.Error_section and get_include_Error():
            for c in range(1, 5):
                ws_owners.cell(row=current_row, column=c, value="ERRORS").fill = ERROR_FILL
            current_row += 1
            current_row = get_section_by_state(list_of_dicts, ws_owners, owner, 3, current_row,True)
        if section_state.Success_section and get_include_Success():
            for c in range(1, 5):
                ws_owners.cell(row=current_row, column=c, value="SUCCESS").fill = SUCCESS_FILL
            current_row += 1
            current_row = get_section_by_state(list_of_dicts, ws_owners, owner, 0, current_row,True)

        # Разделитель между администраторами
        current_row += 1
        for c in range(1, 5):
            ws_owners.cell(row=current_row, column=c).fill = BLACK_FILL
        current_row += 1
        # break

    # Автоподбор ширины колонок
    column_size_auto(ws_owners)


def create_admin_ssl_page_output(wb: Workbook, list_of_dicts: List[Dict]):
    """
    Создает лист с отчетом, сгруппированным по администраторам.
    """
    ws_admins = wb.create_sheet(title="По Админам")
    current_row = 1  # Текущая строка для записи данных
    # Получаем список уникальных администраторов
    admins = get_admins_list(list_of_dicts)

    # Формируем отчет для каждого администратора
    for admin in admins:
        section_state = SectionsState(
            is_contain_section_values(list_of_dicts, admin, 2, False),
            is_contain_section_values(list_of_dicts, admin, 1, False),
            is_contain_section_values(list_of_dicts, admin, 3, False),
            is_contain_section_values(list_of_dicts, admin, 0, False)
        )
        # Заголовок администратора
        if (section_state.Expire_section == 0 and
                (section_state.Warning_section & get_include_warning()) == 0 and
                (section_state.Error_section & get_include_Error()) == 0 and
                (section_state.Success_section & get_include_Success()) == 0):
            continue

        #if section_state.Expire_section == 0 and section_state.Warning_section == 0 and section_state.Error_section == 0:
        #    continue

        ws_admins.cell(row=current_row, column=1, value=admin).font = BOLD_FILL
        current_row += 1
        # Добавляем домены в зоне ERROR (code == 2)
        if section_state.Expire_section:
            for c in range(1, 5):
                ws_admins.cell(row=current_row, column=c, value="EXPIRE").fill = EXPIRE_FILL
            current_row += 1
            current_row = get_section_by_state(list_of_dicts, ws_admins, admin,2, current_row, False)
        # Добавляем домены в зоне WARNING (code == 1)
        if section_state.Warning_section and get_include_warning():
            for c in range(1, 5):
                ws_admins.cell(row=current_row, column=c, value="WARNING").fill = WARNING_FILL
            current_row += 1
            current_row = get_section_by_state(list_of_dicts, ws_admins, admin, 1, current_row, False)
        if section_state.Error_section and get_include_Error():
            for c in range(1, 5):
                ws_admins.cell(row=current_row, column=c, value="ERRORS").fill = ERROR_FILL
            current_row += 1
            current_row = get_section_by_state(list_of_dicts, ws_admins, admin, 3, current_row, False)
        if section_state.Success_section and get_include_Success():
            for c in range(1, 5):
                ws_admins.cell(row=current_row, column=c, value="SUCCESS").fill = SUCCESS_FILL
            current_row += 1
            current_row = get_section_by_state(list_of_dicts, ws_admins, admin, 0, current_row,True)

        # Разделитель между администраторами
        current_row += 1
        for c in range(1, 5):
            ws_admins.cell(row=current_row, column=c).fill = BLACK_FILL
        current_row += 1

    # Автоподбор ширины колонок
    column_size_auto(ws_admins)

def column_size_auto(ws: Worksheet):
    for col in ws.columns:
        max_length = 0
        column = col[0].column_letter
        for cell in col:
            try:
                if len(str(cell.value)) > max_length:
                    max_length = len(str(cell.value))
            except:
                pass
        adjusted_width = min(max_length + 2, 50)
        ws.column_dimensions[column].width = adjusted_width

def get_owners_list(list_of_dicts: List[Dict]):
    owners_list = []
    for dictionary in list_of_dicts:
        owners_list.append(dictionary.get(CONST.OWNER))
    owners_list = sorted(set(owners_list))
    return owners_list

def get_admins_list(list_of_dicts: List[Dict]):
    admins_list = []
    for dictionary in list_of_dicts:
        admins_list.append(dictionary.get(CONST.ADMIN))
    owners_list = sorted(set(admins_list))
    return owners_list

def get_section_by_state(list_of_dicts: List[Dict], ws: Worksheet, name, code_num ,current_row, is_owner):
    if is_owner:
        for dictionary in list_of_dicts:
            if dictionary[CONST.OWNER] == name:
                end_date = dictionary[CONST.END_DATE]
                code = get_ssl_datetime_state(end_date)
                if code == code_num:
                    ws.cell(row=current_row, column=1, value=dictionary[CONST.NAME])
                    ws.cell(row=current_row, column=2, value=dictionary[CONST.DOMAIN_NAME])
                    ws.cell(row=current_row, column=3, value=dictionary[CONST.INFO])
                    ws.cell(row=current_row, column=4, value=dictionary[CONST.END_DATE])
                    current_row += 1
    else:
        for dictionary in list_of_dicts:
            if dictionary[CONST.ADMIN] == name:
                end_date = dictionary[CONST.END_DATE]
                code = get_ssl_datetime_state(end_date)
                if code == code_num:
                    ws.cell(row=current_row, column=1, value=dictionary[CONST.NAME])
                    ws.cell(row=current_row, column=2, value=dictionary[CONST.DOMAIN_NAME])
                    ws.cell(row=current_row, column=3, value=dictionary[CONST.INFO])
                    ws.cell(row=current_row, column=4, value=dictionary[CONST.END_DATE])
                    current_row += 1
    return current_row

def is_contain_section_values(list_of_dicts: List[Dict], name, code_num, is_owner):
    if is_owner:
        for dictionary in list_of_dicts:
            if dictionary[CONST.OWNER] == name:
                end_date = dictionary[CONST.END_DATE]
                code = get_ssl_datetime_state(end_date)
                if code == code_num:
                    return True
    else:
        for dictionary in list_of_dicts:
            if dictionary[CONST.ADMIN] == name:
                end_date = dictionary[CONST.END_DATE]
                code = get_ssl_datetime_state(end_date)
                if code == code_num:
                    return True
    return False

