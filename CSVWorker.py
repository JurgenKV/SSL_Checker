import csv
import shutil
from idlelib.iomenu import encoding
from pathlib import Path
from typing import List, Dict

from SSLRequest import get_certificate_data
from Certificate import *
import CONST_COLUMN as CONST

def load_csv(file):
    original_path = Path(file)

    if not original_path.is_file():
        raise FileNotFoundError(f"Файл не найден: {file}")

    copy_path = original_path.with_name(f"{original_path.stem}_result{original_path.suffix}")
    shutil.copy2(original_path, copy_path)
    return copy_path


def get_csv_data_dict(copy_file_path):
    with open(copy_file_path, mode='r', encoding='cp1251', newline='') as f:
        reader = csv.DictReader(f,delimiter=';')
        data = list(reader)  # список словарей
        return data

def get_new_csv_data_with_ssl(list_of_dicts):
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

    return list_of_dicts
def save_csv(list_of_dicts, file_path):
    # Берём заголовки из ключей первого словаря
    fieldnames = list_of_dicts[0].keys()

    with open(file_path, mode='w', encoding='cp1251', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, delimiter=';')
        writer.writeheader()
        writer.writerows(list_of_dicts)