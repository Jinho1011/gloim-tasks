from __future__ import print_function
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import datetime
import calendar
import pickle
import os.path
import pandas

DATE_LIST = []


def get_sheets_service():
    SCOPES = ['https://www.googleapis.com/auth/drive',
              'https://www.googleapis.com/auth/drive.file',
              'https://www.googleapis.com/auth/spreadsheets']
    creds = None
    if os.path.exists('.config/token-sheets.pickle'):
        with open('.config/token-sheets.pickle', 'rb') as token:
            creds = pickle.load(token)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                '.config/credentials-sheets.json', SCOPES)
            creds = flow.run_local_server(port=3030)
        with open('.config/token-sheets.pickle', 'wb') as token:
            pickle.dump(creds, token)

    service = build('sheets', 'v4', credentials=creds)
    return service.spreadsheets()


def col2num(col_str):
    expn = 0
    col_num = 0
    for char in reversed(col_str):
        col_num += (ord(char) - ord('A') + 1) * (26 ** expn)
        expn += 1

    return col_num


def write_data(sheet, sheet_id, range, content):
    body = {
        'values': [
            content
        ]
    }

    result = sheet.values().update(
        spreadsheetId=sheet_id, range=range, body=body, valueInputOption='USER_ENTERED').execute()


def make_date_list():
    dt_index = pandas.date_range(start='20200101', end='20201231')
    dt_list = dt_index.tolist()
    res_list = []
    last_list = ['01-31', '02-29', '03-31', '04-30', '05-31',
                 '06-30', '07-31', '08-31', '09-30', '10-31', '11-30', '12-31']

    for dt in dt_list:
        res_list.append(dt.strftime("%m-%d"))

    for res in res_list:
        if res in last_list:
            res_list.insert(res_list.index(res) + 1, '')

    global DATE_LIST
    DATE_LIST = res_list


def group_columns_by_month(sheet, sheet_id, month):
    month_index = '0' + str(month) if month < 10 else str(month)
    month_range = calendar.monthrange(datetime.datetime.now().year, month)
    month_list = [DATE_LIST.index(l)
                  for l in DATE_LIST if l.startswith(month_index)]

    data = {
        "requests": [
            {
                "addDimensionGroup": {
                    "range": {
                        "dimension": "COLUMNS",
                        "sheetId": 0,
                        "startIndex": month_list[0] + 4,
                        "endIndex": month_list[-1] + 4
                    }
                }
            }
        ]
    }

    results = sheet.batchUpdate(
        spreadsheetId=sheet_id, body=data).execute()


def group_columns_by_end_date(sheet, sheet_id, month, end_date):
    month_index = '0' + str(month) if month < 10 else str(month)
    start_date = month_index + '-01'
    end_date = end_date.strftime("%m-%d")

    data = {
        "requests": [
            {
                "addDimensionGroup": {
                    "range": {
                        "dimension": "COLUMNS",
                        "sheetId": 0,
                        "startIndex": DATE_LIST.index(start_date) + 4,
                        "endIndex": DATE_LIST.index(end_date) + 4
                    }
                }
            }
        ]
    }

    results = sheet.batchUpdate(
        spreadsheetId=sheet_id, body=data).execute()


def group_columns_by_start_date(sheet, sheet_id, month, start_date):
    month_index = '0' + str(month) if month < 10 else str(month)
    start_date = start_date.strftime("%m-%d")
    last_day_of_month = calendar.monthrange(
        datetime.datetime.now().year, month)[1]
    if last_day_of_month < 10:
        last_day_of_month = '0' + str(last_day_of_month)
    else:
        last_day_of_month = str(last_day_of_month)
    end_date = month_index + '-' + last_day_of_month

    data = {
        "requests": [
            {
                "addDimensionGroup": {
                    "range": {
                        "dimension": "COLUMNS",
                        "sheetId": 0,
                        "startIndex": DATE_LIST.index(start_date) + 4,
                        "endIndex": DATE_LIST.index(end_date) + 4
                    }
                }
            }
        ]
    }

    results = sheet.batchUpdate(
        spreadsheetId=sheet_id, body=data).execute()


def manage_group(sheet, sheet_id):
    # 오늘을 기준으로 +10, -10 날짜
    today_date = datetime.datetime.now()
    start_date = datetime.datetime.now() + datetime.timedelta(days=-10)
    end_date = datetime.datetime.now() + datetime.timedelta(days=10)

    if start_date.month < today_date.month:
        for i in range(1, 13):
            if i not in [start_date.month, today_date.month]:
                group_columns_by_month(sheet, sheet_id, i)
        group_columns_by_end_date(sheet, sheet_id, start_date.month, end_date)
        group_columns_by_start_date(
            sheet, sheet_id, today_date.month, start_date)
    elif end_date.month > today_date.month:
        for i in range(1, 13):
            if i not in [today_date.month, end_date.month]:
                group_columns_by_month(sheet, sheet_id, i)
        group_columns_by_end_date(
            sheet, sheet_id, start_date.month, start_date)
        group_columns_by_start_date(
            sheet, sheet_id, end_date.month, end_date)
    else:
        for i in range(1, 13):
            if i is not today_date.month:
                group_columns_by_month(sheet, sheet_id, i)
        group_columns_by_end_date(
            sheet, sheet_id, today_date.month, start_date)
        group_columns_by_start_date(
            sheet, sheet_id, today_date.month, end_date)


if __name__ == "__main__":
    sheet = get_sheets_service()
    make_date_list()

    # write_data(
    #     sheet, '11AYfo9oaU2zMiRqQKFj5_CrxG6JIp3MTTalwgPmI0UQ', '시트1!E1', DATE_LIST)

    manage_group(sheet, '11AYfo9oaU2zMiRqQKFj5_CrxG6JIp3MTTalwgPmI0UQ')
