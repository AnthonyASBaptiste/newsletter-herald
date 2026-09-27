import unittest
import datetime
from unittest.mock import patch, MagicMock
from helpers.sanity_client import slugify, resolve_themes, sync_to_sanity, STANDARD_THEMES


class TestSanitySync(unittest.TestCase):
    def test_slugify(self):
        self.assertEqual(slugify("26th Sunday in Ordinary Time – Living in Community"), "26th-sunday-in-ordinary-time-living-in-community")
        self.assertEqual(slugify("St. Patrick's Bulletin & Announcements!"), "st-patricks-bulletin-announcements")

    def test_resolve_themes_care_for_poor(self):
        text = "The St. Vincent de Paul Society is hosting a food drive for poor and hungry families."
        primary, supporting = resolve_themes(text, "Ordinary Time")
        self.assertEqual(primary, "theme-care-for-the-poor")
        self.assertIsInstance(supporting, list)

    def test_resolve_themes_stewardship(self):
        text = "We thank parishioners for their ongoing financial stewardship and weekly offertory pledge."
        primary, supporting = resolve_themes(text, "Ordinary Time")
        self.assertEqual(primary, "theme-stewardship")

    def test_resolve_themes_default(self):
        text = "General parish updates and Sunday schedule."
        primary, supporting = resolve_themes(text, None)
        self.assertEqual(primary, "theme-community")
        self.assertGreater(len(supporting), 0)


    @patch("helpers.sanity_client.get_sanity_token", return_value="mock-token-xyz")
    @patch("requests.post")
    def test_sync_to_sanity_success(self, mock_post, mock_token):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "results": [
                {"id": "edition-herald-42", "operation": "createOrReplace"},
                {"id": "workflow-herald-42", "operation": "createOrReplace"}
            ]
        }
        mock_post.return_value = mock_response

        summary_data = {
            "title": "26th Sunday in Ordinary Time",
            "summary": "This is a warm reflection.\n\nHere are the announcements.",
            "schedule_date": "2026-09-27",
            "liturgical_season": "Ordinary Time",
            "liturgical_year": "Year B",
            "model": "llama-3.3-70b-versatile (Groq)",
            "tokens": 450,
            "cost_usd_estimate": 0.0,
        }

        result = sync_to_sanity(
            newsletter_id=42,
            filename="bulletin-2026-09-27.pdf",
            drive_web_view_link="https://drive.google.com/file/d/xyz/view",
            target_sunday=datetime.date(2026, 9, 27),
            schedule_date_val=datetime.date(2026, 9, 27),
            summary_data=summary_data,
            is_valid=True,
            error_msg="",
            uploader="fr_john@parish.org",
        )

        self.assertTrue(result["synced"])
        self.assertEqual(result["edition_id"], "edition-herald-42")
        self.assertEqual(result["workflow_id"], "workflow-herald-42")
        self.assertEqual(result["status"], "awaiting_review")
        self.assertEqual(result["stage"], "awaiting_review")

        # Verify mutation payload sent to Sanity
        mock_post.assert_called_once()
        args, kwargs = mock_post.call_args
        self.assertIn("https://qbl0snjp.api.sanity.io/v2025-08-30/data/mutate/production", args[0])
        payload = kwargs["json"]
        self.assertIn("mutations", payload)
        mutations = payload["mutations"]

        # Must contain standard themes createIfNotExists
        theme_mutations = [m for m in mutations if "createIfNotExists" in m]
        self.assertEqual(len(theme_mutations), len(STANDARD_THEMES))

        # Must contain edition createOrReplace
        edition_mutations = [m for m in mutations if "createOrReplace" in m and m["createOrReplace"]["_type"] == "newsletterEdition"]
        self.assertEqual(len(edition_mutations), 1)
        edition_doc = edition_mutations[0]["createOrReplace"]
        self.assertEqual(edition_doc["_id"], "edition-herald-42")
        self.assertEqual(edition_doc["status"], "awaiting_review")
        self.assertEqual(edition_doc["targetSunday"], "2026-09-27")
        self.assertTrue(edition_doc["primaryTheme"]["_ref"].startswith("theme-"))
        self.assertTrue(edition_doc["validation"]["dateValid"])
        self.assertTrue(edition_doc["aiGenerated"])

        # Must contain workflow createOrReplace
        workflow_mutations = [m for m in mutations if "createOrReplace" in m and m["createOrReplace"]["_type"] == "editorialWorkflow"]
        self.assertEqual(len(workflow_mutations), 1)
        workflow_doc = workflow_mutations[0]["createOrReplace"]
        self.assertEqual(workflow_doc["_id"], "workflow-herald-42")
        self.assertEqual(workflow_doc["currentStage"], "awaiting_review")
        self.assertEqual(workflow_doc["decision"], "pending")
        self.assertEqual(workflow_doc["newsletter"]["_ref"], "edition-herald-42")
        self.assertEqual(len(workflow_doc["history"]), 4)

    @patch("helpers.sanity_client.get_sanity_token", return_value="mock-token-xyz")
    @patch("requests.post", side_effect=Exception("Connection timeout"))
    def test_sync_to_sanity_handles_network_error_gracefully(self, mock_post, mock_token):
        summary_data = {
            "title": "26th Sunday in Ordinary Time",
            "summary": "Reflection text.",
        }

        result = sync_to_sanity(
            newsletter_id=99,
            filename="bulletin.pdf",
            drive_web_view_link=None,
            target_sunday=datetime.date(2026, 9, 27),
            schedule_date_val=None,
            summary_data=summary_data,
            is_valid=False,
            error_msg="Target date mismatch",
            uploader="system",
        )

        # Should not raise exception, but return error status
        self.assertFalse(result["synced"])
        self.assertIn("Connection timeout", result["error"])
        self.assertEqual(result["edition_id"], "edition-herald-99")


if __name__ == "__main__":
    unittest.main()
