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

    DATE_LIST = res_list


def group_columns_by_month(sheet, sheet_id, month):
    start_number = col2num(start_column)
    end_number = col2num(end_column)
    data = {
        "requests": [
            {
                "addDimensionGroup": {
                    "range": {
                        "dimension": "COLUMNS",
                        "sheetId": 0,
                        "startIndex": start_number,
                        "endIndex": end_number
                    }
                }
            }
        ]
    }
    results = sheet.batchUpdate(
        spreadsheetId=sheet_id, body=data).execute()


def group_columns_by_end_date(sheet, sheet_id, month, end_date):
    start_number = col2num(start_column)
    end_number = col2num(end_column)
    data = {
        "requests": [
            {
                "addDimensionGroup": {
                    "range": {
                        "dimension": "COLUMNS",
                        "sheetId": 0,
                        "startIndex": start_number,
                        "endIndex": end_number
                    }
                }
            }
        ]
    }
    results = sheet.batchUpdate(
        spreadsheetId=sheet_id, body=data).execute()


def group_columns_by_start_date(sheet, sheet_id, month, start_date):
    start_number = col2num(start_column)
    end_number = col2num(end_column)
    data = {
        "requests": [
            {
                "addDimensionGroup": {
                    "range": {
                        "dimension": "COLUMNS",
                        "sheetId": 0,
                        "startIndex": start_number,
                        "endIndex": end_number
                    }
                }
            }
        ]
    }
    results = sheet.batchUpdate(
        spreadsheetId=sheet_id, body=data).execute()


def manage_group():
    # 오늘을 기준으로 +10, -10 날짜
    today_date = datetime.datetime.now()
    start_date = datetime.datetime.now() + datetime.timedelta(days=-10)
    end_date = datetime.datetime.now() + datetime.timedelta(days=10)

    if start_date.month < today_date.month:
        # ex) 7.5 => 1~5 GROUP, 6.1 ~ 6.25 GROUP, 7.15 ~ 7.31 GROUP, 8~12 GROUP
        # group_columns_by_month : range(1, start_date.month - 1)
        # group_columns_by_month : range(today_date.month + 1, 12)
        # group_columns_by_end_date : start_date.month / end_date
        # group_columns_by_start_date : today_date.month / start_date
        pass
    elif end_date.month > today_date.month:
        # ex) 7.28 => 1~6 GROUP, 7.1 ~ start_date GROUP, enddate ~ 8.31 GROUP, 9~12 GROUP
        # group_columns_by_month : range(1, today.month - 1 )
        # group_columns_by_month : range(end_date.month + 1, 12)
        # group_columns_by_end_date : today_date.month / start_date
        # group_columns_by_start_date : end_date.month / end_date
        pass
    else:
        # ex) 7.15 => 7.5, 7.25
        # group_columns_by_month : range(1, today.month - 1)
        # group_columns_by_month : range(today.month + 1, 12)
        # group_columns_by_end_date : today_date.month / start_date
        # group_columns_by_start_date : today_date.month / end_date
        pass


if __name__ == "__main__":
    sheet = get_sheets_service()
    make_date_list()

    # write_data(
    #     sheet, '11AYfo9oaU2zMiRqQKFj5_CrxG6JIp3MTTalwgPmI0UQ', '시트1!E1', DATE_LIST)

    manage_group()

    group_columns(
        sheet, '11AYfo9oaU2zMiRqQKFj5_CrxG6JIp3MTTalwgPmI0UQ', 'E', 'AI')
