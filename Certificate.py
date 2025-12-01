
class Certificate:
    def __init__(self, name, domain , create_date, end_date):
        self.name = name
        self.domain = domain
        self.create_date = create_date
        self.end_date = end_date

    @staticmethod
    def init_data_from_dict(csv_dict):
        temp_certificate_list = list()

        print(csv_dict)