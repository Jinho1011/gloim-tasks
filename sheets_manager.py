from __future__ import print_function
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import sheets_init
import datetime
import calendar
import pickle
import os.path
import pandas

SPACE_INDEX = 5
DATE_LIST = sheets_init.make_date_list()
SHEET = sheets_init.get_sheets_service()


def main():
    # while True
    # # 1행 ~ n행까지 가져옴
    # # # IF 색상 AND 시작일 AND 종료일 AND 해당 범위에 색칠X
    # # # # 시작일부터 종료일까지 색칠
    pass


if __name__ == '__main__':
    main()
