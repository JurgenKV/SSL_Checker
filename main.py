from SSLRequest import *
from CSVWorker import *
from UI import build_ui, openOutputFile


#from Certificate import certificate_list

def main_processing(filepath: str) -> str:

    filepath = load_csv(filepath)

    csv_data = get_csv_data_dict(filepath)
    new_csv_data = get_new_csv_data_with_ssl(csv_data)
    output_file_path = save_colored_excel(new_csv_data, filepath)
    certificate_list = Certificate.init_data_from_dict(csv_data)
    openOutputFile(output_file_path)
    return f"Файл '{filepath}' успешно проверен."

if __name__ == "__main__":
    # Запускаем UI
    build_ui()