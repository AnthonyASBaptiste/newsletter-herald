import unittest
from unittest.mock import patch, MagicMock
import datetime

from helpers.sanity_editorial import (
    create_sanity_editorial_documents,
    SanityEditorialCreationError,
    derive_deterministic_source_id,
)
from helpers.sanity_mapper import (
    HeraldEditorialResult,
    SanityMappingError,
)


class TestSanityEditorialOperation(unittest.TestCase):
    def setUp(self):
        self.valid_data = {
            "newsletter_id": 77,
            "title": "26th Sunday in Ordinary Time – Community & Charity",
            "summary": "This is the weekly parish reflection.\n\nHere are upcoming community notices.",
            "target_sunday": "2026-09-27",
            "publication_date": "2026-09-25",
            "liturgical_season": "Ordinary Time",
            "liturgical_year": "Year B",
            "primary_theme": "Care for the Poor",
            "supporting_themes": ["Stewardship", "Prayer"],
            "ai_generated": True,
            "ai_model": "llama3.1:8b",
            "source_filename": "holy_trinity_bulletin_2026-09-27.pdf",
            "source_document_url": "https://storage.googleapis.com/bulletins/holy_trinity_2026-09-27.pdf",
        }

    @patch("helpers.sanity_editorial.get_sanity_token", return_value="test-sanity-token")
    @patch("requests.post")
    def test_successful_creation(self, mock_post, mock_token):
        """1. Successful creation: creates edition, workflow, and delivery with correct references and initial state."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "results": [
                {"id": "edition-herald-77", "operation": "createOrReplace"},
                {"id": "workflow-herald-77", "operation": "createOrReplace"},
                {"id": "delivery-herald-77", "operation": "createOrReplace"},
            ]
        }
        mock_post.return_value = mock_response

        result = create_sanity_editorial_documents(self.valid_data)

        # Assert returned contract
        self.assertEqual(
            result,
            {
                "newsletterId": "edition-herald-77",
                "workflowId": "workflow-herald-77",
                "deliveryId": "delivery-herald-77",
            },
        )

        mock_post.assert_called_once()
        _, kwargs = mock_post.call_args
        mutations = kwargs["json"]["mutations"]

        # Find documents in mutations
        edition_mut = next(
            m["createOrReplace"]
            for m in mutations
            if "createOrReplace" in m and m["createOrReplace"]["_type"] == "newsletterEdition"
        )
        workflow_mut = next(
            m["createOrReplace"]
            for m in mutations
            if "createOrReplace" in m and m["createOrReplace"]["_type"] == "editorialWorkflow"
        )
        delivery_mut = next(
            m["createOrReplace"]
            for m in mutations
            if "createOrReplace" in m and m["createOrReplace"]["_type"] == "delivery"
        )

        # Newsletter assertions
        self.assertEqual(edition_mut["_id"], "edition-herald-77")
        self.assertEqual(edition_mut["status"], "awaiting_review")
        self.assertEqual(edition_mut["primaryTheme"]["_ref"], "theme-care-for-the-poor")
        self.assertEqual(edition_mut["workflow"]["_ref"], "workflow-herald-77")
        self.assertEqual(edition_mut["delivery"]["_ref"], "delivery-herald-77")

        # Workflow assertions
        self.assertEqual(workflow_mut["_id"], "workflow-herald-77")
        self.assertEqual(workflow_mut["currentStage"], "awaiting_review")
        self.assertEqual(workflow_mut["assignedAgent"], "herald-ai")
        self.assertEqual(workflow_mut["decision"], "pending")
        self.assertEqual(workflow_mut["newsletter"]["_ref"], "edition-herald-77")

        # History assertions (at least received, processing, draft, awaiting_review)
        history = workflow_mut["history"]
        stages = [entry["stage"] for entry in history]
        self.assertIn("received", stages)
        self.assertIn("processing", stages)
        self.assertIn("draft", stages)
        self.assertIn("awaiting_review", stages)
        for entry in history:
            self.assertIn("stage", entry)
            self.assertIn("actor", entry)
            self.assertIn("timestamp", entry)

        # Delivery assertions
        self.assertEqual(delivery_mut["_id"], "delivery-herald-77")
        self.assertEqual(delivery_mut["status"], "pending")
        self.assertEqual(delivery_mut["newsletter"]["_ref"], "edition-herald-77")
        self.assertTrue(delivery_mut["scheduledFor"].startswith("2026-09-27"))

    @patch("helpers.sanity_editorial.get_sanity_token", return_value="test-sanity-token")
    @patch("requests.post")
    def test_retry_of_the_same_newsletter(self, mock_post, mock_token):
        """2. Idempotency: Retrying the same newsletter produces identical document IDs and replaces existing ones."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"results": []}
        mock_post.return_value = mock_response

        res1 = create_sanity_editorial_documents(self.valid_data)
        res2 = create_sanity_editorial_documents(self.valid_data)

        # Stable deterministic IDs across retries
        self.assertEqual(res1["newsletterId"], res2["newsletterId"])
        self.assertEqual(res1["workflowId"], res2["workflowId"])
        self.assertEqual(res1["deliveryId"], res2["deliveryId"])

        # Also test with HeraldEditorialResult dataclass
        dataclass_item = HeraldEditorialResult(
            title=self.valid_data["title"],
            summary=self.valid_data["summary"],
            target_sunday="2026-09-27",
            primary_theme="Care for the Poor",
            source_filename=self.valid_data["source_filename"],
        )
        res3 = create_sanity_editorial_documents(dataclass_item)
        res4 = create_sanity_editorial_documents(dataclass_item)

        self.assertEqual(res3["newsletterId"], res4["newsletterId"])
        self.assertEqual(res3["workflowId"], res4["workflowId"])
        self.assertEqual(res3["deliveryId"], res4["deliveryId"])

    @patch("helpers.sanity_editorial.get_sanity_token", return_value="test-sanity-token")
    @patch("requests.post")
    def test_sanity_failure(self, mock_post, mock_token):
        """3. Sanity failure: Raises SanityEditorialCreationError on API HTTP errors or network timeouts."""
        # HTTP 500 error from Sanity
        mock_err_response = MagicMock()
        mock_err_response.status_code = 500
        mock_err_response.text = "Internal Server Error in Content Lake"
        mock_post.return_value = mock_err_response

        with self.assertRaises(SanityEditorialCreationError) as ctx:
            create_sanity_editorial_documents(self.valid_data)
        self.assertIn("500", str(ctx.exception))

        # Network error
        mock_post.side_effect = Exception("Connection reset by peer")
        with self.assertRaises(SanityEditorialCreationError) as ctx:
            create_sanity_editorial_documents(self.valid_data)
        self.assertIn("network request failed", str(ctx.exception).lower())

    def test_invalid_input(self):
        """4. Invalid input: Fails fast with SanityMappingError when required data is missing/invalid."""
        # Missing title
        invalid_data = dict(self.valid_data)
        invalid_data["title"] = ""
        with self.assertRaises(SanityMappingError):
            create_sanity_editorial_documents(invalid_data)

        # Missing summary
        invalid_data = dict(self.valid_data)
        invalid_data["summary"] = None
        with self.assertRaises(SanityMappingError):
            create_sanity_editorial_documents(invalid_data)

        # Invalid target Sunday date format
        invalid_data = dict(self.valid_data)
        invalid_data["target_sunday"] = "Sunday-Next"
        with self.assertRaises(SanityMappingError):
            create_sanity_editorial_documents(invalid_data)

    def test_missing_theme_reference(self):
        """5. Missing theme reference: Fails fast when primary theme is None or empty."""
        no_theme_data = dict(self.valid_data)
        no_theme_data["primary_theme"] = None
        no_theme_data["primaryTheme"] = None
        no_theme_data["theme"] = None

        with self.assertRaises(SanityMappingError) as ctx:
            create_sanity_editorial_documents(no_theme_data)
        self.assertIn("theme reference", str(ctx.exception).lower())

        # Empty string theme
        empty_theme_data = dict(self.valid_data)
        empty_theme_data["primary_theme"] = "   "
        with self.assertRaises(SanityMappingError) as ctx:
            create_sanity_editorial_documents(empty_theme_data)
        self.assertIn("theme reference", str(ctx.exception).lower())


if __name__ == "__main__":
    unittest.main()
