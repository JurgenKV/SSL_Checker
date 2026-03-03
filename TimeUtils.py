    # 0 - success > suc_const, 1 - success < suc_const, 2 - warning, 3 - expired

import datetime as dt
from CONST_COLUMN import WARNING_TIME_CONST, SUCCESS_TIME_CONST

def get_ssl_datetime_state(date_str):
    try:
        ssl_date = dt.datetime.strptime(date_str, "%d.%m.%Y")
        today = dt.datetime.today()
        delta = ssl_date - today
        print(delta)
        if delta.days > SUCCESS_TIME_CONST:
            return 0
        elif SUCCESS_TIME_CONST >= delta.days > WARNING_TIME_CONST:
            return 1
        elif 0 <= delta.days <= WARNING_TIME_CONST:
            return 2
        else:
            return 3
    except Exception as e:
        print(e)
        return 3