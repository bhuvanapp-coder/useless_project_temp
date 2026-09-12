import unittest

from backend.app.importance_scorer import score_document


class ImportanceScorerTests(unittest.TestCase):
    def setUp(self) -> None:
        self.document = {
            "document_id": "doc-123",
            "title": "The Extremely Serious Notes",
            "author": "Professor Footer",
            "metadata": {"title": "The Extremely Serious Notes", "author": "Professor Footer", "format": "PDF 1.7"},
            "pages": [
                {"page_number": 4, "detected_page_number": 4, "font_sizes": [12, 18], "is_blank": False, "image_count": 0},
            ],
            "structure": {
                "repeated_headers": [{"text": "COURSE NOTES", "page_numbers": [1, 2, 3], "count": 3}],
                "repeated_footers": [{"text": "CONFIDENTIAL", "page_numbers": [1, 2, 3], "count": 3}],
                "repeated_phrases": [{"phrase": "the margin is important", "page_numbers": [1, 2], "count": 2}],
                "headings": [{"text": "3. Margins", "page_number": 3}],
                "table_of_contents": {"detected": True, "page_numbers": [1], "entries": []},
            },
        }

    def test_returns_requested_item_shape(self) -> None:
        result = score_document(self.document)
        self.assertEqual(result["document_id"], "doc-123")
        self.assertIn("fictional comedy rankings", result["disclaimer"])
        self.assertGreater(len(result["items"]), 0)
        for item in result["items"]:
            self.assertEqual(set(item), {"element", "type", "page", "importance_score", "ridiculous_reason"})

    def test_irrelevant_formatting_beats_page_number(self) -> None:
        result = score_document(self.document)
        scores_by_type = {item["type"]: item["importance_score"] for item in result["items"]}
        self.assertGreater(scores_by_type["formatting"], scores_by_type["page_number"])
        self.assertGreater(scores_by_type["page_number"], scores_by_type["title"])

    def test_headers_footers_and_toc_are_scored(self) -> None:
        result = score_document(self.document)
        scored_types = {item["type"] for item in result["items"]}
        self.assertTrue({"header", "footer", "table_of_contents", "repeated_phrase", "section_number"}.issubset(scored_types))

    def test_items_are_ranked_from_most_ridiculous(self) -> None:
        result = score_document(self.document)
        scores = [item["importance_score"] for item in result["items"]]
        self.assertEqual(scores, sorted(scores, reverse=True))


if __name__ == "__main__":
    unittest.main()
