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