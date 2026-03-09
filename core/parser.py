import fitz  # PyMuPDF
import docx2txt

class ResumeParser:
    @staticmethod
    def extract_text(file_path):
        """Extracts text from PDF, DOCX, or TXT files."""
        ext = file_path.split('.')[-1].lower()
        
        try:
            if ext == 'pdf':
                return ResumeParser._extract_from_pdf(file_path)
            elif ext == 'docx':
                return ResumeParser._extract_from_docx(file_path)
            elif ext == 'txt':
                return ResumeParser._extract_from_txt(file_path)
            else:
                raise ValueError("Unsupported file format. Please upload PDF, DOCX, or TXT.")
        except Exception as e:
            print(f"Error parsing file {file_path}: {e}")
            return ""

    @staticmethod
    def _extract_from_pdf(file_path):
        text = ""
        with fitz.open(file_path) as doc:
            for page in doc:
                text += page.get_text() + "\n"
        return text

    @staticmethod
    def _extract_from_docx(file_path):
        return docx2txt.process(file_path)

    @staticmethod
    def _extract_from_txt(file_path):
        with open(file_path, 'r', encoding='utf-8') as file:
            return file.read()
