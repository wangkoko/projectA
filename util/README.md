# PDFParser README
=====================

### Introduction
------------------

PDFParser is a simple yet powerful tool for parsing PDF files and extracting valuable information.

#### Features
---------------

##### Extract text from PDF
##### Support multiple languages

* Parse the content and page information of PDF files.
* Support multiple languages and can be customized to extract specific language.

##### Match patterns
-------------------

* Based on specified patterns, match the PDF text and get the needed information.
* Support various pattern types and can be defined as needed.

### Usage
-------------

#### Initialization
------------------

1. Initialize `config.json` for configuration.
2. Set language and mode according to your needs.

##### Extract Text from PDF
-------------------------

1. Pass PDF file to parser for processing.
2. Choose whether to execute OCR on images or not (default is not).

#### Match Patterns
-------------------

1. Based on specified patterns, match PDF text.
2. Get the needed information.

### Implementation Details
---------------------------

#### extract_images_and_perform_ocr

* This function takes a PDF file and extracts images with their basic information.
* It uses PyPDF2 to read PDF files and Pillow (PIL) for image processing.
* The extracted images are then processed using OCR (Optical Character Recognition) technology from Tesseract-OCR.

#### extract_data

* This function uses the matched patterns to extract specific data from the parsed text.
* It takes a dictionary of patterns as input, where each pattern is associated with a regular expression and a corresponding key in the output dictionary.
* The function iterates through the patterns and uses the `re.search` function to find matches in the parsed text.

### Configuration
-----------------

The configuration file (`config.json`) should contain an array of objects, each representing a language and its corresponding patterns.

Example:
```json
[
  {
    "lang": "en",
    "patterns": [
      {"name": "date", "regex": "\\d{4}-\\d{2}-\\d{2}"}
    ]
  },
  {
    "lang": "zh",
    "patterns": [
      {"name": "name", "regex": "[\\u4e00-\\u9fa5]+"}
    ]
  }
]

# 新增類別 Prompt
=====================

## 指定類別名稱和功能
---------------------------

* `請將 "PDFParser" 和 "extract_text_from_pdf" 的功能整合到一個新類別中，並將其命名為 "PdfExtractor"`
* `新類別 PdfExtractor 需要具備 "extract_text_from_pdf" 這個方法`

## 指定新類別的屬性和方法
---------------------------

* `請將 "lang" 和 "patterns" 的屬性整合到一個新類別中，並將其命名為 "PdfParserConfig"`
* `新類別 PdfParserConfig 需要具備 "lang" 和 "patterns" 這兩個屬性`

## 指定新類別的方法
---------------------------

* `請將 "extract_images_and_perform_ocr" 的方法整合到一個新類別中，並將其命名為 "PdfImageProcessor"`
* `新類別 PdfImageProcessor 需要具備 "extract_images_and_perform_ocr" 這個方法`

## 指定新類別的使用範圍
---------------------------

* `請將 "PdfParserConfig" 和 "PdfImageProcessor" 的方法整合到一個新的類別中，並將其命名為 "PdfProcessor"`
* `新類別 PdfProcessor 需要具備 "extract_text_from_pdf"、"extract_images_and_perform_ocr" 這兩個方法`

### RecordStore Class介紹
#### 使用說明

*   `RecordStore` class 是一個用於管理根目錄下的子目錄的類別。
*   它會在指定的根目錄下找到葉子目錄，並將其相對路徑儲存在列表中。

### Methods和Attributes介紹
#### get_leaf_folders
取得根目錄下所有葉子目錄的相對路徑列表。

#### find_path_by_name
根據傳入的名稱查找相應的葉子目錄，若找到則回傳該葉子目錄的路徑。

#### absolute_root_path
返回根目錄的絕對路徑。

### Usage範例

```python
if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--root', default='.')
    args = parser.parse_args()

    record_store = RecordStore(args.root)

    # 取得子目錄列表
    leaf_folders = record_store.get_leaf_folders()
    for folder, path in leaf_folders:
        print(f'{folder}: {path}')

    # 查找特定名子的子目錄
    name = 'my_folder'
    path = record_store.find_path_by_name(name)
    if path is not None:
        print(f'找到 "{name}" 的子目錄: {path}')
    else:
        print(f'未找到 "{name}" 的子目錄')

    # 取得根目錄的絕對路徑
    absolute_root = record_store.absolute_root_path
    print(f'根目錄的絕對路徑: {absolute_root}')

### 說明

RecordStore class 中的 _find_leaf_folders 方法會遍歷 root 目錄下的所有子目錄，找出葉子目錄（不含子目錄的目錄），並儲存在 leaf_folders 列表中。
 
get_leaf_folders 方法返回 leaf_folders 列表中的資料。
 
find_path_by_name 方法會根據傳入的 name 查找相應的葉子目錄，若找到則回傳該葉子目錄的路徑。
 
absolute_root_path 屬性返回根目錄的絕對路徑。

# ExcelDictReader
=====================
pip install pandas python-docx

## 使用說明

參數：
* `excel_path`: Excel檔案的路徑
* `key`: 欲查詢的字典鍵

方法：
* `load_data()`: 讀取Excel檔案並轉換成字典
* `search_dict(key_value)`: 依據指定的鍵值查詢字典

範例使用：
```python
reader = ExcelDictReader('example.xlsx')
reader.load_data()
result = reader.search_dict('最終訂單編號', '2205-20200102007')
print(result)
