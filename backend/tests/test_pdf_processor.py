import unittest

import fitz

from backend.app.pdf_processor import process_pdf


class PdfProcessorTests(unittest.TestCase):
    def test_extracts_document_structure_from_sample_pdf(self) -> None:
        pdf = fitz.open()
        pdf.set_metadata({"title": "The Margins", "author": "Dr. Footer"})
        for page_number in range(1, 4):
            page = pdf.new_page()
            page.insert_text((60, 45), "COURSE NOTES 101", fontsize=10)
            page.insert_text((60, 100), "Contents" if page_number == 1 else f"Chapter {page_number}", fontsize=18)
            if page_number == 1:
                page.insert_text((60, 135), "Chapter 2........2", fontsize=11)
            page.insert_text((60, 180), "The margin is important and the margin is important.", fontsize=12)
            page.insert_text((60, 790), f"Page {page_number}", fontsize=10)

        result = process_pdf(pdf.tobytes(), "sample-notes.pdf", "sample-id")
        pdf.close()

        self.assertEqual(result["page_count"], 3)
        self.assertEqual(result["title"], "The Margins")
        self.assertEqual(result["author"], "Dr. Footer")
        self.assertIn("The margin is important", result["pages"][1]["text"])
        self.assertEqual(result["pages"][1]["detected_page_number"], 2)
        self.assertTrue(result["structure"]["repeated_headers"])
        self.assertTrue(result["structure"]["repeated_footers"])
        self.assertTrue(result["structure"]["repeated_phrases"])
        self.assertTrue(result["structure"]["headings"])
        self.assertTrue(result["structure"]["table_of_contents"]["detected"])
        self.assertFalse(result["ocr"]["recommended"])

    def test_marks_image_only_document_for_future_ocr(self) -> None:
        pdf = fitz.open()
        page = pdf.new_page()
        page.draw_rect(fitz.Rect(30, 30, 200, 200), color=(1, 0, 0))

        result = process_pdf(pdf.tobytes(), "scan.pdf", "scan-id")
        pdf.close()

        self.assertTrue(result["ocr"]["recommended"])
        self.assertEqual(result["ocr"]["status"], "not_configured")


if __name__ == "__main__":
    unittest.main()
