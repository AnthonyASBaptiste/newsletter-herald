"""
Unit and integration tests for Sanity Editorial creation connected to
the Herald newsletter ingestion flow.
"""

import unittest
from unittest.mock import patch, MagicMock, AsyncMock
import datetime

from helpers.sanity_editorial import (
    create_sanity_editorial_documents,
    SanityEditorialCreationError,
    derive_deterministic_source_id,
)
from helpers.sanity_mapper import (
    map_to_sanity_newsletter_edition,
    HeraldEditorialResult,
)


class TestSanityIngestionFlow(unittest.TestCase):

    def setUp(self):
        self.sample_herald_summary = {
            "title": "Third Sunday of Lent - Parish Community Bulletin",
            "summary": (
                "Welcome to our Lenten journey. Stations of the Cross are scheduled every Friday evening at 7:00 PM in the main sanctuary.\n\n"
                "Our parish food pantry continues to collect canned goods and non-perishables for local families in need this season."
            ),
            "schedule_date": "2026-03-08",
            "liturgical_season": "Lent",
            "calendar_year": 2026,
            "liturgical_year": "Year A",
            "model": "gpt-4o",
            "tokens": 450,
            "cost_usd_estimate": 0.0045,
            "primary_theme": "Community & Fellowship",
            "supporting_themes": ["Liturgy & Sacraments"],
        }
        self.newsletter_id = 42
        self.target_sunday = datetime.date(2026, 3, 8)
        self.standard_filename = "2026-03-08-Trinity-Newsletter.pdf"
        self.web_view_link = "https://drive.google.com/file/d/sample-view-link/view"
        self.uploader = "editor@parish.org"

    def test_editorial_payload_mapping_and_deterministic_ids(self):
        """Verifies that Herald editorial data maps to deterministic Sanity IDs."""
        editorial_payload = {
            "newsletter_id": self.newsletter_id,
            "title": self.sample_herald_summary["title"],
            "summary": self.sample_herald_summary["summary"],
            "target_sunday": self.target_sunday,
            "publication_date": self.target_sunday,
            "liturgical_occasion": "Third Sunday of Lent",
            "liturgical_season": self.sample_herald_summary["liturgical_season"],
            "liturgical_year": self.sample_herald_summary["liturgical_year"],
            "primary_theme": self.sample_herald_summary["primary_theme"],
            "supporting_themes": self.sample_herald_summary["supporting_themes"],
            "ai_generated": True,
            "ai_model": self.sample_herald_summary["model"],
            "source_filename": self.standard_filename,
            "source_document_url": self.web_view_link,
            "uploader": self.uploader,
        }

        source_id = derive_deterministic_source_id(editorial_payload)
        self.assertEqual(source_id, "42")

        mock_session = MagicMock()
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "results": [
                {"id": "edition-herald-42"},
                {"id": "workflow-herald-42"},
                {"id": "delivery-herald-42"},
            ]
        }
        mock_session.post.return_value = mock_response

        res = create_sanity_editorial_documents(
            editorial_payload,
            token="test-token",
            project_id="test-proj",
            dataset="production",
            session=mock_session,
        )

        self.assertEqual(res["newsletterId"], "edition-herald-42")
        self.assertEqual(res["workflowId"], "workflow-herald-42")
        self.assertEqual(res["deliveryId"], "delivery-herald-42")

        # Verify mutation structure
        call_kwargs = mock_session.post.call_args[1]
        mutations = call_kwargs["json"]["mutations"]
        mutation_types = [list(m.keys())[0] for m in mutations]
        self.assertIn("createOrReplace", mutation_types)

        # Inspect newsletterEdition
        edition_mutations = [m["createOrReplace"] for m in mutations if "createOrReplace" in m and m["createOrReplace"].get("_type") == "newsletterEdition"]
        self.assertEqual(len(edition_mutations), 1)
        edition = edition_mutations[0]
        self.assertEqual(edition["_id"], "edition-herald-42")
        self.assertEqual(edition["status"], "awaiting_review")
        self.assertEqual(edition["primaryTheme"]["_ref"], "theme-community")

        # Inspect editorialWorkflow
        wf_mutations = [m["createOrReplace"] for m in mutations if "createOrReplace" in m and m["createOrReplace"].get("_type") == "editorialWorkflow"]
        self.assertEqual(len(wf_mutations), 1)
        wf = wf_mutations[0]
        self.assertEqual(wf["_id"], "workflow-herald-42")
        self.assertEqual(wf["currentStage"], "awaiting_review")
        self.assertEqual(wf["assignedAgent"], "herald-ai")
        self.assertEqual(wf["decision"], "pending")
        stages = [h["stage"] for h in wf["history"]]
        self.assertEqual(stages, ["received", "processing", "draft", "awaiting_review"])

        # Inspect delivery
        del_mutations = [m["createOrReplace"] for m in mutations if "createOrReplace" in m and m["createOrReplace"].get("_type") == "delivery"]
        self.assertEqual(len(del_mutations), 1)
        delivery = del_mutations[0]
        self.assertEqual(delivery["_id"], "delivery-herald-42")
        self.assertEqual(delivery["status"], "pending")

    def test_retry_idempotency_produces_identical_documents(self):
        """Verifies that calling the operation twice for the same newsletter produces identical mutation IDs."""
        editorial_payload = {
            "newsletter_id": 99,
            "title": "Feast of Corpus Christi",
            "summary": "Parish feast celebration summary.",
            "target_sunday": "2026-06-07",
            "primary_theme": "Eucharist & Worship",
            "source_filename": "corpus-christi.pdf",
        }

        mock_session = MagicMock()
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_session.post.return_value = mock_response

        first_call = create_sanity_editorial_documents(
            editorial_payload,
            token="test-token",
            session=mock_session,
        )
        second_call = create_sanity_editorial_documents(
            editorial_payload,
            token="test-token",
            session=mock_session,
        )

        self.assertEqual(first_call, second_call)
        self.assertEqual(first_call["newsletterId"], "edition-herald-99")
        self.assertEqual(first_call["workflowId"], "workflow-herald-99")
        self.assertEqual(first_call["deliveryId"], "delivery-herald-99")

    def test_sanity_failure_raises_actionable_error(self):
        """Verifies that temporary Sanity outage raises SanityEditorialCreationError without silent swallowing."""
        editorial_payload = {
            "newsletter_id": 101,
            "title": "Easter Vigil",
            "summary": "Holy Saturday vigil announcements.",
            "target_sunday": "2026-04-05",
            "primary_theme": "Liturgy & Sacraments",
        }

        mock_session = MagicMock()
        mock_response = MagicMock()
        mock_response.status_code = 503
        mock_response.text = "Service Unavailable"
        mock_session.post.return_value = mock_response

        with self.assertRaises(SanityEditorialCreationError) as ctx:
            create_sanity_editorial_documents(
                editorial_payload,
                token="test-token",
                session=mock_session,
            )
        self.assertIn("503", str(ctx.exception))


class TestIngestionEndpointLogic(unittest.IsolatedAsyncioTestCase):

    async def test_notify_agent_formats_sanity_sync_failed(self):
        """Verifies that sanity_sync_failed notifications are structured with retry links."""
        mock_db = MagicMock()
        mock_db.execute = AsyncMock(return_value=1)
        mock_table = MagicMock()
        captured_values = {}

        def fake_values(**kwargs):
            captured_values.update(kwargs)
            return MagicMock()

        mock_table.insert.return_value.values = fake_values

        with patch.dict("sys.modules", {
            "db.setup": MagicMock(database=mock_db),
            "db.models": MagicMock(agent_notifications=mock_table),
        }):
            from helpers.agent_bridge import notify_agent

            success = await notify_agent(
                "sanity_sync_failed",
                {
                    "newsletter_id": 55,
                    "title": "Palm Sunday Newsletter",
                    "target_sunday": "2026-03-29",
                    "status": "draft",
                    "error_message": "Sanity API timed out connecting to dataset 'production'",
                    "filename": "2026-03-29-Palm-Sunday.pdf",
                },
            )

            self.assertTrue(success)
            self.assertTrue(mock_db.execute.called)
            self.assertEqual(captured_values["event_type"], "sanity_sync_failed")
            payload_str = captured_values["payload"]
            self.assertIn("Sanity Editorial Sync Failed", payload_str)
            self.assertIn("Retry Sanity Sync", payload_str)
            self.assertIn("/newsletters/55/sync-sanity", payload_str)

    async def test_notify_agent_review_request_includes_sanity_url(self):
        """Verifies review_request notification includes direct Sanity Studio link."""
        mock_db = MagicMock()
        mock_db.execute = AsyncMock(return_value=1)
        mock_table = MagicMock()
        captured_values = {}

        def fake_values(**kwargs):
            captured_values.update(kwargs)
            return MagicMock()

        mock_table.insert.return_value.values = fake_values

        with patch.dict("sys.modules", {
            "db.setup": MagicMock(database=mock_db),
            "db.models": MagicMock(agent_notifications=mock_table),
        }):
            from helpers.agent_bridge import notify_agent

            await notify_agent(
                "review_request",
                {
                    "newsletter_id": 77,
                    "title": "Good Friday Bulletin",
                    "summary": "Solemn liturgies and veneration schedule.",
                    "target_sunday": "2026-04-03",
                    "status": "draft",
                    "sanity_edition_id": "edition-herald-77",
                    "sanity_workflow_id": "workflow-herald-77",
                    "sanity_delivery_id": "delivery-herald-77",
                },
            )

            self.assertTrue(mock_db.execute.called)
            payload_str = captured_values["payload"]
            self.assertIn("structure/newsletterEdition;edition-herald-77", payload_str)
            self.assertIn("Sanity Studio", payload_str)


if __name__ == "__main__":
    unittest.main()
