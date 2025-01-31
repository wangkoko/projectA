import PyPDF2
import pytesseract
import io
from PIL import Image
import json
import re
import os
import logging
import shutil

# 設定日誌檔案名稱和目錄
#LOG_FILE = 'pdf_parser.log'

# 設定日誌等級
logging.basicConfig(level=logging.INFO)

# 建立一個記錄器
logger = logging.getLogger(__name__)

# 設定記錄器的格式
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
#handler = logging.FileHandler(LOG_FILE)
#handler.setFormatter(formatter)
#logger.addHandler(handler)

class PDFParser:
    def __init__(self, config_file="config.json"):
        # Load configuration from JSON file
        with open(config_file, 'r', encoding='utf-8') as f:
            self.config = json.load(f)
        # Initialize text variables
        self.pdf_text = ""
        self.lang = ""
        self.file_name = ""
        self.file_path = ""
        self.data = {}
    @property
    def get_text(self):
        return self.pdf_text
    @property
    def get_lang(self):
        return self.lang

    def patterns(self):
        return self.config

    def lang(self):
        return [entry.get("lang") for entry in self.config if entry.get("lang")]

    def extract_text_from_pdf(self, pdf_path):
        # Extract text content from a PDF file using PyPDF2
        pdf_file_obj = open(pdf_path, 'rb')
        pdf_reader = PyPDF2.PdfReader(pdf_file_obj)  
        num_pages = len(pdf_reader.pages) 
        page_text = ''
        for page in range(num_pages):
            page_obj = pdf_reader.pages[page]
            page_text += page_obj.extract_text()
        self.pdf_text = page_text

    def extract_images_and_perform_ocr(self, pdf_path, lang = 'chi_tra'):
        self.lang = lang
        self.file_name = os.path.basename(pdf_path)
        self.file_path = os.path.dirname(pdf_path)
        with open(pdf_path, 'rb') as pdf_file_obj:
            pdf_reader = PyPDF2.PdfReader(pdf_file_obj)

            for page_num, page in enumerate(pdf_reader.pages):
                # 檢查是否包含 XObject
                if '/XObject' in page['/Resources']:
                    x_objects = page['/Resources']['/XObject'].get_object()

                    for obj_name, obj in x_objects.items():
                        obj = obj.get_object()

                        # 確保對象是圖片
                        if obj['/Subtype'] == '/Image':
                            # 提取圖片的基本信息
                            width = obj['/Width']
                            height = obj['/Height']
                            color_space = obj['/ColorSpace']
                            data = obj.get_data()

                            # 處理圖片的壓縮格式
                            if '/Filter' in obj:
                                filters = obj['/Filter']
                                if filters == '/DCTDecode':  # JPEG 圖片
                                    image_data = io.BytesIO(data)
                                    pil_image = Image.open(image_data)
                                elif filters == '/JPXDecode':  # JPEG 2000 圖片
                                    image_data = io.BytesIO(data)
                                    pil_image = Image.open(image_data)
                                else:
                                    logger.warning(f"Unsupported filter {filters} on page {page_num}")
                                    continue
                            else:
                                # 對未壓縮圖片數據進行處理
                                mode = "RGB" if color_space == '/DeviceRGB' else "P"
                                pil_image = Image.frombytes(mode, (width, height), data)

                            # 選擇性保存圖像（如果需要）
                            # output_filename = f"image_{page_num}_1.png"
                            # pil_image.save(output_filename)
                            
                            # 執行 OCR
                            ocr_result = pytesseract.image_to_string(pil_image, lang=lang)
                            self.pdf_text += f"Page {page_num + 1}, Image {obj_name}:\n{ocr_result}\n\n"
        return self.pdf_text

    def merge_pdfs(self, pdf_paths, output_path):
        # ... (Implementation for merging PDFs - you might need a different library)
        pass
    
    def extract_data(self):
        logger.debug(f"to doc is translate by {self.get_lang}")
        patterns = {}
        for entry in self.config:
            if self.get_lang in entry.get('lang'):
                patterns = entry.get("patterns", "")
                logger.debug(f"use following pattern ({type(patterns)}) to parse {patterns}")
        for pattern_name, pattern in patterns.items():
             logger.debug(f'match {pattern_name} by {pattern}')
             match = re.search(pattern, self.pdf_text)
             if match:
                 value = match.group(1)  # or match.group(2), etc.
                 self.data[pattern_name] = value
        logger.debug(self.data)
        return self.data

    def set_data(self, key, data):
        if self.data.get(key):
            logger.info(f'key ({key}) existed - overwrite ({self.data.get(key)})')
        self.data[key] = data

    def save_to(self, path : str, name : str) -> str:
        '''
        save pdf from
        self.file_path = os.path.dirname(pdf_path)
        to
        path with name.pdf
        '''
        archive_path = os.path.join(path, f"{name}.pdf")
        os.makedirs(os.path.dirname(archive_path), exist_ok=True)
        src_path = os.path.join(self.file_path, self.file_name)
        logger.info(f'archive file ({src_path}) to ({archive_path})')
        if os.path.exists(archive_path):
            return f"\t歸檔 PDF 已存在!! 請確認是否已歸過檔\n\t{src_path}\n\t 存在檔案 {archive_path}\n"
        shutil.copy2(src_path, archive_path)  
        return f"\tPDF 已歸檔\n\t 將 {src_path}\n\t歸檔至 {archive_path}\n"
        # try:
        #     with open(self.file_path, 'wb') as f:
        #         f.write(archive_path)  # Assuming self.pdf_data contains the PDF content
        #         return f"PDF saved to {archive_path}/{name}"
        # except Exception as e:
        #     return f"Error saving PDF: {e}"

    def get_data(self, key):
        return self.data.get(key)

    def get_config(self):
        return self.config 



if __name__ == "__main__":
    parser = PDFParser()
    config = parser.get_config()

    print(type(config))
    for patt in config:
        lang = patt.get("lang")
        print(f"pattern entry {lang}")
        
    # pdf_file = "./test_data/20241204082535676.pdf" 
    # pdf_file = "./test_data/20241127081629635.pdf" 
    pdf_file = "./test_data/20241217083105429.pdf"
    parser.extract_images_and_perform_ocr(pdf_file)

    print("Text extracted from PDF:")
    print(parser.pdf_text)

    # print(parser.get_lang)
    # for entry in config:
    #     if parser.get_lang in entry.get('lang'):
    #         pattern = entry.get("patterns", "")
    #         print(f"use following pattern to parse {pattern}")


    print(f'pdf({parser.file_name}) : {parser.extract_data()}')

