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
        self.images = []
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

    def extract_images_and_perform_ocr(self, pdf_path, lang='chi_tra', crop_box=None):
        """
        從 PDF 提取圖片並對指定範圍進行 OCR。
        
        :param pdf_path: PDF 文件的路徑
        :param lang: OCR 語言（預設為繁體中文 'chi_tra'）
        :param crop_box: 要 OCR 的特定區域 (left, upper, right, lower)，如果為 None 則處理整張圖片
        :return: OCR 提取的文本
        """
        self.lang = lang
        self.file_name = os.path.basename(pdf_path)
        self.file_path = os.path.dirname(pdf_path)

        with open(pdf_path, 'rb') as pdf_file_obj:
            pdf_reader = PyPDF2.PdfReader(pdf_file_obj)

            for page_num, page in enumerate(pdf_reader.pages):
                if '/XObject' in page['/Resources']:
                    x_objects = page['/Resources']['/XObject'].get_object()

                    for obj_name, obj in x_objects.items():
                        obj = obj.get_object()

                        if obj['/Subtype'] == '/Image':  # 確保是圖片
                            data = obj.get_data()
                            width, height = obj['/Width'], obj['/Height']
                            color_space = obj['/ColorSpace']

                            # 處理圖片格式
                            if '/Filter' in obj:
                                filters = obj['/Filter']
                                if filters == '/DCTDecode':  # JPEG
                                    image_data = io.BytesIO(data)
                                    pil_image = Image.open(image_data)
                                elif filters == '/JPXDecode':  # JPEG 2000
                                    image_data = io.BytesIO(data)
                                    pil_image = Image.open(image_data)
                                else:
                                    print(f"Unsupported filter {filters} on page {page_num}")
                                    continue
                            else:
                                mode = "RGB" if color_space == '/DeviceRGB' else "P"
                                pil_image = Image.frombytes(mode, (width, height), data)

                            # **裁剪圖像特定範圍**
                            if crop_box:
                                cropped_image = pil_image.crop(crop_box)
                            else:
                                cropped_image = pil_image  # 不裁剪，使用整張圖

                            # **執行 OCR**
                            ocr_result = pytesseract.image_to_string(cropped_image, lang=lang)
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

    def extract_images(self, pdf_path, target_page=None):
        """
        從 PDF 提取圖片。
        :param pdf_path: PDF 文件的路徑
        :param target_page: 只提取特定頁面的圖片（從 0 開始計數），如果為 None 則提取所有頁面
        :return: 包含 (page_num, obj_name, pil_image) 的列表
        """
        self.lang = lang
        self.file_name = os.path.basename(pdf_path)
        self.file_path = os.path.dirname(pdf_path)
        self.images = []
        with open(pdf_path, 'rb') as pdf_file_obj:
            pdf_reader = PyPDF2.PdfReader(pdf_file_obj)

            for page_num, page in enumerate(pdf_reader.pages):
                if target_page is not None and page_num != target_page:
                    continue
                
                if '/XObject' in page['/Resources']:
                    x_objects = page['/Resources']['/XObject'].get_object()

                    for obj_name, obj in x_objects.items():
                        obj = obj.get_object()

                        if obj['/Subtype'] == '/Image':  # 確保是圖片
                            data = obj.get_data()
                            width, height = obj['/Width'], obj['/Height']
                            color_space = obj['/ColorSpace']

                            if '/Filter' in obj:
                                filters = obj['/Filter']
                                if filters == '/DCTDecode':  # JPEG
                                    image_data = io.BytesIO(data)
                                    pil_image = Image.open(image_data)
                                elif filters == '/JPXDecode':  # JPEG 2000
                                    image_data = io.BytesIO(data)
                                    pil_image = Image.open(image_data)
                                else:
                                    print(f"Unsupported filter {filters} on page {page_num}")
                                    continue
                            else:
                                mode = "RGB" if color_space == '/DeviceRGB' else "P"
                                pil_image = Image.frombytes(mode, (width, height), data)

                            self.images.append((page_num, obj_name, pil_image, width, height))
        return self.images

    def perform_ocr(self, lang='chi_tra', crop_box=None, save_cropped=True):
        """
        對提取的圖片執行 OCR。
        :param images: (page_num, obj_name, pil_image) 的列表
        :param lang: OCR 語言
        :param crop_box: 要 OCR 的特定區域 (left, upper, right, lower)，如果為 None 則處理整張圖片
            crop_box=(100, 50, 500, 300) 代表 從左上角 (100, 50) 到右下角 (500, 300)
        :return: OCR 提取的文本
        """
        if len(self.images) == 0:
            self.pdf_text = ''
            return self.pdf_text

        images = self.images

        for page_num, obj_name, pil_image, pil_width, pil_height in images:
            print(f'image width {pil_width} height {pil_height}\n')
            if crop_box:
                left, upper, right, lower = crop_box
                width, height = pil_image.size
                left = max(0, min(left, width))
                upper = max(0, min(upper, height))
                right = max(left + 1, min(right, width))
                lower = max(upper + 1, min(lower, height))
                cropped_image = pil_image.crop((left, upper, right, lower))
                cropped_image.rotate(90, expand=True)
                # 保存裁剪後的圖片
                if save_cropped:
                    clean_obj_name = obj_name.replace("/", "_")  # 移除 `/`
                    cropped_image_path = f"cropped_page{page_num + 1}_{clean_obj_name}.png"
                    cropped_image.save(cropped_image_path)
                    print(f"Saved cropped image: {cropped_image_path}")
            else:
                #pil_image.rotate(90, expand=True)
                cropped_image = pil_image

            ocr_result = pytesseract.image_to_string(cropped_image, lang=lang)
            self.pdf_text += f"Page {page_num + 1}, Image {obj_name}: {ocr_result}\n\n"
        return self.pdf_text

if __name__ == "__main__":
    import argparse
    # 設定 argparse
    parser = argparse.ArgumentParser(description="Process a PDF file for OCR.")
    parser.add_argument("pdf_file", type=str, help="Path to the PDF file to be processed")
    args = parser.parse_args()

    pdf_parser = PDFParser()
    config = pdf_parser.get_config()

    print(type(config))
    for patt in config:
        lang = patt.get("lang")
        print(f"pattern entry {lang}")

    # 使用命令列傳入的 PDF 文件路徑
    #pdf_parser.extract_images_and_perform_ocr(args.pdf_file)

    pdf_parser.extract_images(args.pdf_file, target_page=0)
    pdf_parser.perform_ocr(lang = 'eng',crop_box=(1650, 700, 1850, 1350))
    #pdf_parser.perform_ocr(crop_box=(1650, 700, 1850, 1350))
    #pdf_parser.perform_ocr(lang = 'eng')

    print(f'pdf parsed text:\n{pdf_parser.pdf_text}\n\n')
    print(f'pdf({pdf_parser.file_name}) : {pdf_parser.extract_data()}')

