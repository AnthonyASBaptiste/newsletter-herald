"""
End-to-end integration test of real newsletter ingestion with Sanity editorial creation,
failure resilience, and idempotent retry.
"""

import os
import io
import json
import unittest
from unittest.mock import patch, MagicMock, AsyncMock
from fastapi.testclient import TestClient

from main import app
from config import get_settings

PDF_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "test_newsletters", "test.pdf")

class TestEndToEndRealNewsletterIngestion(unittest.TestCase):

    def setUp(self):
        self.client = TestClient(app)
        self.settings = get_settings()
        self.headers = {"X-API-Key": self.settings.api_key}

    @patch("main.upload_to_drive")
    @patch("main.choose_llm_and_summarize")
    @patch("helpers.sanity_editorial.create_sanity_editorial_documents")
    @patch("main.notify_agent", new_callable=AsyncMock)
    @patch("main.database.execute", new_callable=AsyncMock)
    def test_real_newsletter_ingestion_success_flow(
        self,
        mock_db_execute,
        mock_notify_agent,
        mock_sanity_create,
        mock_summarize,
        mock_upload_drive,
    ):
        """
        Tests desired flow:
        upload -> validate -> extract -> summarize -> persist Herald data ->
        map editorial result -> create Sanity docs -> notify agent -> return success
        """
        self.assertTrue(os.path.exists(PDF_PATH), f"Real test PDF not found at {PDF_PATH}")
        with open(PDF_PATH, "rb") as f:
            pdf_bytes = f.read()

        from helpers.validation import get_target_sunday
        target_sunday = get_target_sunday()
        target_sunday_str = target_sunday.isoformat()
        target_sunday_file_fmt = target_sunday.strftime("%d%b%Y")

        # Mock storage
        mock_upload_drive.return_value = ("drive_file_123", "https://storage.example.com/test.pdf")

        # Mock LLM summarizer returning church editorial result
        mock_summarize.return_value = {
            "title": "25th Sunday in Ordinary Time - Servant Leadership",
            "summary": (
                "Jesus teaches that true greatness in the Kingdom of God is found in humility and selfless service.\n\n"
                "Join us for our parish outreach programs and ministry meetings this week."
            ),
            "schedule_date": target_sunday_str,
            "liturgical_season": "Ordinary Time",
            "calendar_year": 2024,
            "liturgical_year": "Year B",
            "model": "gpt-4o",
            "tokens": 320,
            "cost_usd_estimate": 0.0032,
            "primary_theme": "Service & Outreach",
            "supporting_themes": ["Community & Fellowship"],
        }

        # Mock DB execute returning auto-increment IDs
        # 1st call: update older newsletters to superseded
        # 2nd call: insert newsletters -> newsletter_id = 1001
        # 3rd call: insert summaries -> summary_id = 2001
        # 4th call: insert model_usage
        # 5th call: insert upload_logs
        mock_db_execute.side_effect = [0, 1001, 2001, 1, 1]

        # Mock Sanity editorial creation
        mock_sanity_create.return_value = {
            "newsletterId": "edition-herald-1001",
            "workflowId": "workflow-herald-1001",
            "deliveryId": "delivery-herald-1001",
        }

        # Send request
        response = self.client.post(
            "/upload-document",
            headers=self.headers,
            files={"file": (f"{target_sunday_file_fmt}-Newsletter.pdf", io.BytesIO(pdf_bytes), "application/pdf")},
            data={"uploader": "pastor@church.org"},
        )

        self.assertEqual(response.status_code, 200)
        data = response.json()

        # 1. Verify response payload
        self.assertIn("summary", data)
        self.assertIn("validation", data)
        self.assertTrue(data["validation"]["is_valid"])
        self.assertEqual(data["validation"]["target_sunday"], target_sunday_str)

        # 2. Verify Sanity document info
        self.assertIn("sanity", data)
        sanity_info = data["sanity"]
        self.assertTrue(sanity_info["synced"])
        self.assertEqual(sanity_info["status"], "awaiting_review")
        self.assertEqual(sanity_info["newsletterId"], "edition-herald-1001")
        self.assertEqual(sanity_info["workflowId"], "workflow-herald-1001")
        self.assertEqual(sanity_info["deliveryId"], "delivery-herald-1001")

        # 3. Verify Sanity creation was called with mapped editorial payload
        self.assertTrue(mock_sanity_create.called)
        editorial_call_arg = mock_sanity_create.call_args[0][0]
        self.assertEqual(editorial_call_arg["newsletter_id"], 1001)
        self.assertEqual(editorial_call_arg["title"], "25th Sunday in Ordinary Time - Servant Leadership")
        self.assertEqual(editorial_call_arg["primary_theme"], "Service & Outreach")
        self.assertEqual(editorial_call_arg["source_filename"], f"{target_sunday_str}-Trinity-Newsletter.pdf")

        # 4. Verify agent notification dispatched with review_request and sanity IDs
        self.assertTrue(mock_notify_agent.called)
        agent_event_type, agent_payload = mock_notify_agent.call_args_list[-1][0]
        self.assertEqual(agent_event_type, "review_request")
        self.assertEqual(agent_payload["newsletter_id"], 1001)
        self.assertEqual(agent_payload["sanity_edition_id"], "edition-herald-1001")

    @patch("main.upload_to_drive")
    @patch("main.choose_llm_and_summarize")
    @patch("helpers.sanity_editorial.create_sanity_editorial_documents")
    @patch("main.notify_agent", new_callable=AsyncMock)
    @patch("main.database.execute", new_callable=AsyncMock)
    def test_real_newsletter_ingestion_sanity_failure_resilience(
        self,
        mock_db_execute,
        mock_notify_agent,
        mock_sanity_create,
        mock_summarize,
        mock_upload_drive,
    ):
        """
        Failure handling requirement:
        If Sanity is temporarily unavailable:
        - do NOT silently report success
        - existing Herald record must remain available (no deletion or rollback)
        - record clear integration failure that can be retried later
        - observable through logging & agent notification
        - do not make a second AI call
        """
        with open(PDF_PATH, "rb") as f:
            pdf_bytes = f.read()

        from helpers.validation import get_target_sunday
        target_sunday_str = get_target_sunday().isoformat()

        mock_upload_drive.return_value = ("drive_file_1002", "https://storage.example.com/test.pdf")
        mock_summarize.return_value = {
            "title": "25th Sunday in Ordinary Time",
            "summary": "Sunday reflections on servant leadership.",
            "schedule_date": target_sunday_str,
            "liturgical_season": "Ordinary Time",
            "calendar_year": 2024,
            "liturgical_year": "Year B",
            "model": "gpt-4o",
            "tokens": 200,
            "cost_usd_estimate": 0.002,
        }

        mock_db_execute.side_effect = [0, 1002, 2002, 1, 1]

        # Simulate Sanity network timeout or 503 outage
        from helpers.sanity_editorial import SanityEditorialCreationError
        mock_sanity_create.side_effect = SanityEditorialCreationError("Sanity API timeout: connection refused (503)")

        response = self.client.post(
            "/upload-document",
            headers=self.headers,
            files={"file": ("22Sept2024-Newsletter.pdf", io.BytesIO(pdf_bytes), "application/pdf")},
            data={"uploader": "pastor@church.org"},
        )

        self.assertEqual(response.status_code, 200)
        data = response.json()

        # 1. Verify NOT silently reported as synced
        sanity_info = data["sanity"]
        self.assertFalse(sanity_info["synced"])
        self.assertEqual(sanity_info["status"], "sync_failed")
        self.assertIn("Sanity API timeout", sanity_info["error"])
        self.assertEqual(sanity_info["retry_url"], "/newsletters/1002/sync-sanity")

        # 2. Verify Herald record still exists and returned
        self.assertEqual(data["summary"]["newsletter_id"], 1002)

        # 3. Verify agent notification dispatched with sanity_sync_failed
        self.assertTrue(mock_notify_agent.called)
        agent_event_type, agent_payload = mock_notify_agent.call_args_list[-1][0]
        self.assertEqual(agent_event_type, "sanity_sync_failed")
        self.assertEqual(agent_payload["newsletter_id"], 1002)
        self.assertIn("Sanity API timeout", agent_payload["error_message"])

    @patch("helpers.sanity_editorial.create_sanity_editorial_documents")
    @patch("main.notify_agent", new_callable=AsyncMock)
    @patch("main.choose_llm_and_summarize")
    @patch("main.database.fetch_one", new_callable=AsyncMock)
    def test_retry_sanity_sync_endpoint_without_second_ai_call(
        self,
        mock_db_fetch_one,
        mock_summarize,
        mock_notify_agent,
        mock_sanity_create,
    ):
        """
        Verifies retry flow:
        - POST /newsletters/{newsletter_id}/sync-sanity
        - Reuses existing Herald records from DB
        - Does NOT call AI summarization again
        - Idempotently creates/replaces Sanity documents
        """
        newsletter_id = 1002

        # 1st fetch: newsletters table
        mock_newsletter_row = {
            "id": newsletter_id,
            "filename": "2024-09-22-Trinity-Newsletter.pdf",
            "drive_file_id": "drive_file_1002",
            "drive_web_view_link": "https://storage.example.com/test.pdf",
            "target_sunday": "2024-09-22",
            "schedule_date": "2024-09-22",
            "tags": "ordinary-time, 2024, Year B",
            "status": "draft",
            "uploader": "pastor@church.org",
        }
        # 2nd fetch: summaries table
        mock_summary_row = {
            "id": 2002,
            "newsletter_id": newsletter_id,
            "title": "25th Sunday in Ordinary Time",
            "summary": "Existing summary retrieved from PostgreSQL without re-calling LLM.",
        }
        mock_db_fetch_one.side_effect = [mock_newsletter_row, mock_summary_row]

        mock_sanity_create.return_value = {
            "newsletterId": f"edition-herald-{newsletter_id}",
            "workflowId": f"workflow-herald-{newsletter_id}",
            "deliveryId": f"delivery-herald-{newsletter_id}",
        }

        # Invoke retry endpoint
        response = self.client.post(
            f"/newsletters/{newsletter_id}/sync-sanity",
            headers=self.headers,
        )

        self.assertEqual(response.status_code, 200)
        data = response.json()

        # Verify NO second AI call was made
        mock_summarize.assert_not_called()

        # Verify Sanity sync succeeded
        self.assertTrue(data["sanity"]["synced"])
        self.assertEqual(data["sanity"]["newsletterId"], f"edition-herald-{newsletter_id}")
        self.assertEqual(data["sanity"]["workflowId"], f"workflow-herald-{newsletter_id}")
        self.assertEqual(data["sanity"]["deliveryId"], f"delivery-herald-{newsletter_id}")

        # Verify review_request was dispatched
        self.assertTrue(mock_notify_agent.called)
        agent_event_type, agent_payload = mock_notify_agent.call_args[0]
        self.assertEqual(agent_event_type, "review_request")
        self.assertEqual(agent_payload["newsletter_id"], newsletter_id)


if __name__ == "__main__":
    unittest.main()
