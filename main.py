from SSLRequest import *
from CSVWorker import *
#from Certificate import certificate_list



path_of_copy = load_csv('test.csv')
csv_data = get_csv_data_dict(path_of_copy)
new_csv_data = get_new_csv_data_with_ssl(csv_data)
save_csv(new_csv_data, path_of_copy)
#certificate_list = Certificate.init_data_from_dict(csv_data)

