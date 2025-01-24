import unittest
from pathlib import Path
import os
import optparse
from util.pdf_parser import PDFParser  # Import from your 'util' folder

class TestPDFParser(unittest.TestCase):

    def setUp(self):
        self.parser = PDFParser("config.json")  # Assuming you have a config file

    def test_extract_pdf(self):
        # Traverse ./test_data and extract each PDF file
        parsed_files = []
        for root, dirs, files in os.walk('./test_data'):
            for file in files:
                if file.endswith('.pdf'):
                    print(f"extract {os.path.join(root, file)}")
                    parser = PDFParser()
                    parser.extract_images_and_perform_ocr(os.path.join(root, file))
                    result = parser.extract_data()
                    assert result is not None
                    print(f'pdf({parser.file_name}) : {result}')
                    parsed_files.append(parser)
    # def test_extract_text_from_pdf_case1(self):
    #     """Test text extraction from a sample PDF."""
    #     test_pdf_path = Path("./test_data/20241127081629635.pdf") 
    #     self.parser.extract_text_from_pdf(test_pdf_path)
    #     # Assert if the extracted text is not empty or contains expected keywords
    #     assert self.parser.pdf_text, "Extracted text is empty."

    # def test_extract_text_from_pdf_case2(self):
    #     """Test text extraction from a sample PDF."""
    #     test_pdf_path = Path("./test_data/20241217083105429.pdf") 
    #     self.parser.extract_text_from_pdf(test_pdf_path)
    #     # Assert if the extracted text is not empty or contains expected keywords
    #     assert self.parser.pdf_text, "Extracted text is empty."
    
    def test_images_and_perform_ocr(self):
        pdf_file = "./test_data/20241127081629635.pdf" 
        self.parser.extract_images_and_perform_ocr(pdf_file)
        # You'd want to assert that the expected number of images are extracted here
        assert self.parser.pdf_text, "Extracted text is empty."

if __name__ == "__main__":
    unittest.main()