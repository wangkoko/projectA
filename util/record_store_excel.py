
"""
ExcelDictReader使用說明
=====================

參數：
* `excel_path`: Excel檔案的路徑
* `key`: 欲查詢的字典鍵

方法：
* `load_data()`: 讀取Excel檔案並轉換成字典
* `search_dict(key_value)`: 依據指定的鍵值查詢字典

範例使用：
'''python
reader = ExcelDictReader('example.xlsx')
reader.load_data()
result = reader.search_dict('最終訂單編號', '2205-20200102007')
print(result)
'''
"""

import pandas as pd
import argparse
import logging

class ExcelDictReader:
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)

    def __init__(self, excel_path):
        self.excel_path = excel_path
        self.data_dict = {}

    @property
    def num_pages(self):
        return len(self.data_dict)

    def num_data_page(self):
        return [(idx, len(items)) for idx, items in enumerate(self.data_dict.values())]

    def dump_data_page(self, idx):
        if idx > self.num_pages:
            ExcelDictReader.logger.debug(f"only ({self.num_pages}) could be shown x({idx})")
            return
        for key_idx, key in enumerate(self.data_dict):
            if idx == key_idx:
                ExcelDictReader.logger.debug(f"page[{idx}] : {self.data_dict[key]}")

    def dump_page_keys(self):
        for key in self.data_dict.keys():
            ExcelDictReader.logger.debug(key)

    def get_data(self, id):
        if id >= self.num_pages:
            return None
        for key_idx, key in enumerate(self.data_dict):
            if id == key_idx:
                return self.data_dict[key]
        return None

    def load_data(self):
        sheets = pd.read_excel(self.excel_path, sheet_name=None)
        for i, sheet in enumerate(sheets.values()):
            if sheet is not None:
                df = pd.DataFrame(sheet)
                # 使用列名來取代 'Sheet Name'
                sheet_name = str(i) + '-' + df.columns[0].strip()
                self.data_dict[sheet_name] = df.to_dict(orient='records')

    def search_dict(self, key, value):
        ExcelDictReader.logger.debug(f'search dict key ({key}) : val ({value})')
        if self.data_dict is None:
            return None
        
        for key_page in self.data_dict:
            page_dict = self.data_dict.get(key_page)
            if page_dict[-1].get(key) is None:
                ExcelDictReader.logger.debug(f'in {key_page} no key with ({key})')
                continue
            ExcelDictReader.logger.debug(f'keep searching {key} in page({key_page})')
            for row, entry in enumerate(page_dict):
                if entry.get(key) == value:
                    #ExcelDictReader.logger.debug(f'found entry({row}) : {entry}')
                    return entry
        return None

if __name__ == '__main__':
    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
    ExcelDictReader.logger.addHandler(handler)

    parser = argparse.ArgumentParser(description='ExcelDictReader')
    parser.add_argument('-e', '--excel_path', required=True, help='Path to Excel file')
    parser.add_argument('-k', '--key', default='', help='Key to search in dictionary')

    args = parser.parse_args()

    reader = ExcelDictReader(args.excel_path)
    reader.load_data()

    print(f'excel with ({reader.num_pages}) sub pages')
    #print(reader.data_dict)
    reader.dump_page_keys()
    print(f'excel with data in each page ({reader.num_data_page()})')
    # for idx in range(0, reader.num_pages):
    #     reader.dump_data_page(idx)

    for idx in range(0, reader.num_pages):
        data_dict = reader.get_data(idx)
        #print(f'dump data in page({idx}) : keys ({data_dict[0].keys()})')
        # for num, entry in enumerate(data_dict):
        #     print(f'record [{num}] : {entry}')

    key = 'SN'
    key_2 = '專案代號'
    val = 'P2347002'

    print(f'search key : ({key}) val : ({val})')
    result = reader.search_dict(key, val)

    if result:
        print(result)
    else:
        print("No matching data found.")