class execute:
    def __init__(self):
        self.main_url = "https://judgment.judicial.gov.tw/FJUD/Default_AD.aspx"
        self = req_data = {
            '__VIEWSTATE': state_dict['VIEWSTATE'],
            '__VIEWSTATEGENERATOR': state_dict['VIEWSTATEGENERATOR'],
            '__EVENTVALIDATION': state_dict['EVENTVALIDATION'],
            'judtype': judtype,
            'whosub': whosub,
            'jud_court': jud_court,
            'jud_sys': jud_sys,
            'dy1': int(start_date.split('-')[0]),
            'dm1': int(start_date.split('-')[1]),
            'dd1': int(start_date.split('-')[2]),
            'dy2': int(end_date.split('-')[0]),
            'dm2': int(end_date.split('-')[1]),
            'dd2': int(end_date.split('-')[2]),
            'ctl00$cp_content$btnSimpleQry': SimpleQry
        }


if __name__ == '__main__':
    execute()
