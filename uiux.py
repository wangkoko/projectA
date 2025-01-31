from util.pdf_parser import PDFParser
from util.record_store_excel import ExcelDictReader
from util.record_store import RecordStore
import os
import json
import logging
import gradio as gr

# 設定日誌檔案名稱和目錄
LOG_FILE = './pdf_parser.log'
# 設定日誌等級
logging.basicConfig(filename=LOG_FILE, level=logging.DEBUG)
# 建立一個記錄器
logger = logging.getLogger(__name__)

# 設定記錄器的格式
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler = logging.FileHandler(LOG_FILE)
handler.setFormatter(formatter)
logger.addHandler(handler)

class FileArchiveAgent:

    def __init__(self, archive_config = "archive_config.json"):
        self.archive_config : dict = None
        self.fileToArchive : list[PDFParser] = []
        self.not_archived_files : list[PDFParser] = []
        self.map_dict = {
            "SN_NUM" : "SN",
            "REPORT_ID_ARCH" : "專案代號",
            "D_DATE" : "校正日",
            "DONE_DATE" : "校正完成日",
            "USER" : "USER",
            "CUSTOMER" : "客戶",
            "P_USER" : "電話",
            "E_USER" : "E-mail",
            "ARCHIVE_TO" : "ARCHIVE_TO",
            "NEW_ARCHIVE" : "NEW_ARCHIVE"
        }

        if archive_config is not None and os.path.exists(archive_config):
            with open(archive_config, 'r', encoding='utf-8') as  f:
                self.archive_config = json.load(f)
        
        if self.archive_config is not None and self.archive_config.get('arch_db'):
            self.arch_db_path = self.archive_config.get('arch_db')
        else:
            self.arch_db_path = "Enter path here..."

        if self.archive_config is not None and self.archive_config.get('folder_db'):
            self.folder_db_path = self.archive_config.get('folder_db')
        else:
            self.folder_db_path = "Enter path here..."

        
        if self.archive_config is not None and self.archive_config.get('arch_db'):
            self.wait_archive_path = self.archive_config.get('arch_files_path')
        else:
            self.wait_archive_path = "Enter path here..."

        self.arch_db : ExcelDictReader = None
        self.folder_db : RecordStore = None

    def able_to_archive(self, pdf : PDFParser) -> bool:
        if pdf.get_data(self.map_dict.get("ARCHIVE_TO")) or pdf.get_data(self.map_dict.get("NEW_ARCHIVE")):
            logger.info(f'able to archive to {pdf.get_data(self.map_dict.get("ARCHIVE_TO"))} or self.map_dict.get("NEW_ARCHIVE")')
            return True
        return False

    def set_archive_db(self, arch_db_path : str):
        self.arch_db_path = arch_db_path

        self.arch_db = ExcelDictReader(self.arch_db_path)
        self.arch_db.load_data()

        logger.info(f'excel with ({self.arch_db.num_pages}) sub pages')
        #print(reader.data_dict)
        self.arch_db.dump_page_keys()
        logger.info(f'excel with data in each page ({self.arch_db.num_data_page()})')

    def set_folder_db(self, folder_db_path : str):
        self.folder_db_path = folder_db_path
        logger.info(f'set and load folder root : {folder_db_path}')
        self.folder_db = RecordStore(folder_db_path)

    def get_folder_db(self):
        if self.folder_db is not None:
            return self.folder_db.get_leaf_folders()
        return None

    def _search_info_in_sheet(self, pdf : PDFParser, key, value) -> str:
        if self.arch_db is None:
            return "please load 工作紀錄表"
        entry = self.arch_db.search_dict(key, value)

        pdf.set_data(self.map_dict.get('SN_NUM'), value)
        REPORT_ID_ARCH = entry.get(self.map_dict.get('REPORT_ID_ARCH')) if entry else None
        CUSTOMER = entry.get(self.map_dict.get('CUSTOMER')) if entry else None

        if REPORT_ID_ARCH:
            logger.info(f'set to pdf {self.map_dict.get("REPORT_ID_ARCH")} : {REPORT_ID_ARCH}')
            pdf.set_data(self.map_dict.get('REPORT_ID_ARCH'), REPORT_ID_ARCH)

        if CUSTOMER:
            logger.info(f'set to pdf {self.map_dict.get("CUSTOMER")} : {CUSTOMER}')
            pdf.set_data(self.map_dict.get('CUSTOMER'), CUSTOMER)
        return f"\t尋找工作紀錄表: ({key}, {value} : {CUSTOMER} {REPORT_ID_ARCH})\n"

    def _search_info_in_folder(self, pdf : PDFParser) -> str:
        path = None
        ret_str = ''
        if self.folder_db is None:
            return 'please load folder database'
        path_company = self.folder_db.traverse_directory(pdf.get_data(self.map_dict.get('CUSTOMER')))

        ret_str = f"\t尋找歸檔路徑 : {pdf.get_data(self.map_dict.get('CUSTOMER'))} :"

        if path_company is not None:
            path = self.folder_db.traverse_directory(pdf.get_data(self.map_dict.get('SN_NUM')), root_folder=path_company)
        else:
            ret_str += f"\n\t\t無公司相關歸檔路徑 {pdf.get_data(self.map_dict.get('CUSTOMER'))}"

        if path is not None:
            pdf.set_data(self.map_dict.get("ARCHIVE_TO"), path)
            ret_str += f"\n\t\t找到歸檔路徑 {path}"

        if path_company is not None and path is None:
            path = os.path.join(path_company, pdf.get_data(self.map_dict.get('SN_NUM')))
            pdf.set_data(self.map_dict.get("NEW_ARCHIVE"), path)
            ret_str += f"\n\t\t需新增歸檔路徑 {path}"

        return ret_str + "\n"

    def archive_pdf(self) -> str:
        parsed_files_str = ''

        for entry in self.fileToArchive:
            save_to = entry.get_data(self.map_dict.get("ARCHIVE_TO"))
            if save_to is None:
                save_to = entry.get_data(self.map_dict.get("NEW_ARCHIVE"))
            parsed_files_str +=  self._show_pdf_info(entry)
            parsed_files_str += entry.save_to(save_to, entry.get_data(self.map_dict.get("REPORT_ID_ARCH")))
            yield parsed_files_str
        parsed_files_str += f'歸檔完畢 ({len(self.fileToArchive)})'
        return parsed_files_str

    def _show_pdf_info(self, entry : PDFParser) -> str:
        parsed_files_str = (f'檔名 : pdf({entry.file_name} \n'
            f'\t 客戶\t: {entry.get_data(self.map_dict.get("CUSTOMER"))} \n'
            f'\t 專案代碼\t: {entry.get_data(self.map_dict.get("REPORT_ID_ARCH"))} \n'
            f'\t 編號\t: {entry.get_data(self.map_dict.get("SN_NUM"))} \n')
        if entry.get_data(self.map_dict.get("ARCHIVE_TO")):
            parsed_files_str += f'\t 可歸檔至\t: {entry.get_data(self.map_dict.get("ARCHIVE_TO"))} \n'
        elif entry.get_data(self.map_dict.get("NEW_ARCHIVE")):
            parsed_files_str += f'\t 需新增歸檔至\t: {entry.get_data(self.map_dict.get("NEW_ARCHIVE"))} \n'
        else:
            parsed_files_str += f'\t 找不到客戶相關路徑 ({entry.get_data(self.map_dict.get("CUSTOMER"))}) \n'
        return parsed_files_str

    def _show_pdfs_info(self, f_list : [PDFParser]) -> str:
        parsed_files_str = ''
        for entry in f_list:
            parsed_files_str += self._show_pdf_info(entry)
        return parsed_files_str

    def show_archived_pdf_info(self) -> str:
        parsed_files_str = '可歸檔\n'
        parsed_files_str += self._show_pdfs_info(self.fileToArchive)
        return parsed_files_str

    def show_man_archived_pdf_info(self) -> str:
        parsed_files_str = '需手動歸檔\n'
        parsed_files_str += self._show_pdfs_info(self.not_archived_files)
        return parsed_files_str

    def extract_pdf(self, folder_path : str) -> str:
        self.not_archived_files = []
        self.fileToArchive = []
        parsed_files_str = ''
        if self.arch_db is None or self.folder_db is None:
            #search_dict
            logger.info(f"如需自動歸檔請先載入 excel 資料庫 {self.arch_db} 或者指定歸檔根目錄 {self.folder_db} \n")
            parsed_files_str += f"如需自動歸檔請先載入 excel 資料庫 {self.arch_db} 或者指定歸檔根目錄 {self.folder_db} \n"
            yield parsed_files_str

        for root, dirs, files in os.walk(folder_path):

            for file in files:
                if file.endswith('.pdf'):
                    logger.info(f"分類 {os.path.join(root, file)}")
                    parsed_files_str += f"分類 : ({os.path.join(root, file)})\n"
                    yield parsed_files_str
                    parser = PDFParser()
                    parser.extract_images_and_perform_ocr(os.path.join(root, file))
                    result = parser.extract_data()
                    logger.info(f'分類 pdf({parser.file_name}) : {result}\n')
                    if result and (result.get("REPORT_ID") or result.get("SN_ENG")):
                        parsed_files_str += f'\t嘗試自動歸檔 pdf({parser.file_name}) : {result}\n'
                        if self.arch_db is not None:
                            sn_search = result.get("SN_ENG") if result.get("SN_ENG") is not None else result.get("SN_ZH")
                            parsed_files_str += self._search_info_in_sheet(parser, self.map_dict.get('SN_NUM'), sn_search)
                            parsed_files_str += self._search_info_in_folder(parser)
                            if self.able_to_archive(parser):
                                self.fileToArchive.append(parser)
                            else:
                                self.not_archived_files.append(parser)
                    else:
                        parsed_files_str += f'需手重歸檔 : pdf({parser.file_name})\n'
                        self.not_archived_files.append(parser)
                    yield parsed_files_str
        parsed_files_str += '總結:\n'
        parsed_files_str += self.show_archived_pdf_info()
        yield parsed_files_str
        parsed_files_str += self.show_man_archived_pdf_info()
        yield parsed_files_str

def create_app():
    archiveAgent = FileArchiveAgent()
    with gr.Blocks() as ui:
        gr.Markdown('### A simple interface for file archive')
        with gr.Row():
            folder_db_path = gr.Textbox(label="歸檔路徑根目錄 (folder_db)", value=archiveAgent.folder_db_path, placeholder=archiveAgent.folder_db_path)
            load_folder_db = gr.Button("讀取歸檔路徑")
        with gr.Row():
            arch_db_path = gr.Textbox(label="工作紀錄表路徑 (arch_db)", value=archiveAgent.arch_db_path, placeholder=archiveAgent.arch_db_path)
            load_arch_db = gr.Button("讀取工作紀錄表路徑")
        with gr.Row():
            fils_to_arch_path = gr.Textbox(label="需歸檔 PDFs 路徑", value=archiveAgent.wait_archive_path, placeholder=archiveAgent.wait_archive_path)
            with gr.Column():
                process_files = gr.Button("確認是否可歸檔")
                archived_files_info = gr.Button("自動歸檔資訊")
                man_archive_files_info = gr.Button("手動歸檔資訊")
                archive_files = gr.Button("歸檔")
        with gr.Row():
            run_status = gr.TextArea(label="執行狀態", interactive=True)

        load_arch_db.click(archiveAgent.set_archive_db, inputs=[arch_db_path], outputs=[run_status])
        load_folder_db.click(archiveAgent.set_folder_db, inputs=[folder_db_path], outputs=[run_status])
        process_files.click(
            archiveAgent.extract_pdf,
            inputs=[fils_to_arch_path], outputs=[run_status]
            )
        archive_files.click(
            archiveAgent.archive_pdf,
            outputs=[run_status]
        )
        archived_files_info.click(
            archiveAgent.show_archived_pdf_info,
            outputs=[run_status]
        )
        man_archive_files_info.click(
            archiveAgent.show_man_archived_pdf_info,
            outputs=[run_status]
        )

    ui.launch(inbrowser=True)


if __name__ == "__main__":
    app = create_app()