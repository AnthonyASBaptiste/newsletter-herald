import unittest
import datetime
from helpers.sanity_mapper import (
    map_to_sanity_newsletter_edition,
    HeraldEditorialResult,
    SanityMappingError,
    KNOWN_THEME_IDS,
)


class TestSanityMapper(unittest.TestCase):
    def test_1_normal_newsletter(self):
        """1. Normal newsletter: All required and optional fields correctly mapped."""
        pub_date = datetime.date(2026, 9, 25)
        target_sun = datetime.date(2026, 9, 27)
        created_time = datetime.datetime(2026, 9, 25, 14, 30, tzinfo=datetime.timezone.utc)
        updated_time = datetime.datetime(2026, 9, 25, 14, 32, tzinfo=datetime.timezone.utc)

        herald_data = HeraldEditorialResult(
            title="26th Sunday in Ordinary Time – Community & Care",
            summary="A warm reflection for our parish.\n\nUpcoming events and Mass intentions.",
            publication_date=pub_date,
            target_sunday=target_sun,
            liturgical_occasion="26th Sunday in Ordinary Time",
            liturgical_season="Ordinary Time",
            liturgical_year="Year B",
            primary_theme="Care for the Poor",
            supporting_themes=["Stewardship", "Prayer"],
            ai_generated=True,
            ai_model="llama3.1:8b",
            source_filename="holy_trinity_bulletin_2026-09-27.pdf",
            source_document_url="https://drive.google.com/file/d/sample123/view",
            created_at=created_time,
            updated_at=updated_time,
            workflow_id="workflow-herald-101",
            delivery_id="delivery-herald-101",
            edition_id="edition-herald-101",
        )

        edition = map_to_sanity_newsletter_edition(herald_data)

        self.assertEqual(edition["_type"], "newsletterEdition")
        self.assertEqual(edition["_id"], "edition-herald-101")
        self.assertEqual(edition["title"], "26th Sunday in Ordinary Time – Community & Care")
        self.assertEqual(edition["slug"]["_type"], "slug")
        self.assertEqual(
            edition["slug"]["current"],
            "2026-09-27-26th-sunday-in-ordinary-time-community-care",
        )
        self.assertEqual(edition["publicationDate"], "2026-09-25")
        self.assertEqual(edition["targetSunday"], "2026-09-27")
        self.assertEqual(edition["liturgicalOccasion"], "26th Sunday in Ordinary Time")
        self.assertEqual(edition["liturgicalSeason"], "Ordinary Time")
        self.assertEqual(edition["liturgicalYear"], "Year B")
        self.assertEqual(edition["sourceFilename"], "holy_trinity_bulletin_2026-09-27.pdf")
        self.assertEqual(
            edition["sourceDocumentUrl"],
            "https://drive.google.com/file/d/sample123/view",
        )
        self.assertEqual(
            edition["primaryTheme"],
            {"_type": "reference", "_ref": "theme-care-for-the-poor"},
        )
        self.assertEqual(edition["status"], "awaiting_review")
        self.assertTrue(edition["aiGenerated"])
        self.assertEqual(edition["aiModel"], "llama3.1:8b")
        self.assertEqual(edition["createdAt"], created_time.isoformat())
        self.assertEqual(edition["updatedAt"], updated_time.isoformat())

        # Workflow and delivery references
        self.assertEqual(
            edition["workflow"],
            {"_type": "reference", "_ref": "workflow-herald-101"},
        )
        self.assertEqual(
            edition["delivery"],
            {"_type": "reference", "_ref": "delivery-herald-101"},
        )

        # Supporting themes references
        self.assertEqual(len(edition["supportingThemes"]), 2)
        refs = [st["_ref"] for st in edition["supportingThemes"]]
        self.assertIn("theme-stewardship", refs)
        self.assertIn("theme-prayer", refs)

        # Each supporting theme must have a unique _key
        keys = [st["_key"] for st in edition["supportingThemes"]]
        self.assertEqual(len(keys), len(set(keys)))

    def test_2_missing_optional_liturgical_metadata(self):
        """2. Missing optional liturgical metadata: occasion, season, year omitted."""
        herald_dict = {
            "title": "Parish Bulletin Announcement",
            "summary": "This is a simple digest.",
            "target_sunday": "2026-10-04",
            "publication_date": "2026-10-02",
            "source_filename": "bulletin.pdf",
            "primary_theme": "Community",
        }

        edition = map_to_sanity_newsletter_edition(herald_dict)

        self.assertEqual(edition["_type"], "newsletterEdition")
        self.assertEqual(edition["status"], "awaiting_review")
        self.assertEqual(edition["targetSunday"], "2026-10-04")
        self.assertEqual(edition["publicationDate"], "2026-10-02")
        self.assertTrue(edition["aiGenerated"])

        # Optional liturgical fields should not be present
        self.assertNotIn("liturgicalOccasion", edition)
        self.assertNotIn("liturgicalSeason", edition)
        self.assertNotIn("liturgicalYear", edition)
        self.assertNotIn("sourceDocumentUrl", edition)
        self.assertNotIn("workflow", edition)
        self.assertNotIn("delivery", edition)

    def test_3_missing_source_url(self):
        """3. Missing source URL: document URL is None or omitted without error."""
        herald_dict = {
            "title": "27th Sunday Bulletin",
            "summary": "Welcome to our parish.\n\nHere are this week's activities.",
            "target_sunday": datetime.date(2026, 10, 4),
            "source_filename": "offline_bulletin.pdf",
            "source_document_url": None,
            "primary_theme": "Service",
        }

        edition = map_to_sanity_newsletter_edition(herald_dict)

        self.assertNotIn("sourceDocumentUrl", edition)
        self.assertEqual(edition["sourceFilename"], "offline_bulletin.pdf")
        self.assertEqual(edition["status"], "awaiting_review")
        self.assertEqual(
            edition["primaryTheme"],
            {"_type": "reference", "_ref": "theme-service"},
        )

    def test_4_multiple_supporting_themes(self):
        """4. Multiple supporting themes: mapped to existing canonical themes with unique keys."""
        herald_dict = {
            "title": "Parish Stewardship & Outreach Sunday",
            "summary": "Join us in stewardship, prayer, and service to those in need.",
            "target_sunday": "2026-10-11",
            "primary_theme": "theme-stewardship",
            "supporting_themes": [
                "Care for the Poor",
                "theme-prayer",
                "Service",
                "Community",
                "theme-stewardship",  # Duplicate of primary theme; should be deduplicated
            ],
            "ai_model": "claude-3-5-sonnet",
        }

        edition = map_to_sanity_newsletter_edition(herald_dict)

        self.assertEqual(edition["primaryTheme"]["_ref"], "theme-stewardship")
        supporting = edition["supportingThemes"]

        # Should contain the 4 distinct non-primary themes
        self.assertEqual(len(supporting), 4)

        refs = [st["_ref"] for st in supporting]
        self.assertEqual(
            set(refs),
            {
                "theme-care-for-the-poor",
                "theme-prayer",
                "theme-service",
                "theme-community",
            },
        )

        # Primary theme must not be in supporting themes
        self.assertNotIn("theme-stewardship", refs)

        # Every ref must be in KNOWN_THEME_IDS (no dynamically invented theme documents)
        for r in refs:
            self.assertIn(r, KNOWN_THEME_IDS)

        # All keys must be unique strings
        keys = [st["_key"] for st in supporting]
        self.assertEqual(len(keys), 4)
        self.assertEqual(len(set(keys)), 4)
        for k in keys:
            self.assertTrue(k.startswith("st_"))

    def test_5_invalid_missing_required_fields(self):
        """5. Invalid/missing required fields: raises SanityMappingError with descriptive messages."""
        base_valid = {
            "title": "Valid Title",
            "summary": "Valid Summary",
            "target_sunday": "2026-10-18",
        }

        # Missing or empty title
        invalid_title_cases = [
            {**base_valid, "title": ""},
            {**base_valid, "title": "   "},
            {**base_valid, "title": None},
        ]
        for c in invalid_title_cases:
            with self.assertRaises(SanityMappingError) as ctx:
                map_to_sanity_newsletter_edition(c)
            self.assertIn("title", str(ctx.exception).lower())

        # Missing or empty summary
        invalid_summary_cases = [
            {**base_valid, "summary": ""},
            {**base_valid, "summary": "   "},
            {**base_valid, "summary": None},
        ]
        for c in invalid_summary_cases:
            with self.assertRaises(SanityMappingError) as ctx:
                map_to_sanity_newsletter_edition(c)
            self.assertIn("summary", str(ctx.exception).lower())

        # Missing target_sunday
        with self.assertRaises(SanityMappingError) as ctx:
            map_to_sanity_newsletter_edition({"title": "A", "summary": "B"})
        self.assertIn("target_sunday", str(ctx.exception).lower())

        # Invalid date format
        invalid_date_cases = ["18-10-2026", "2026/10/18", "next sunday", "2026-02-30"]
        for bad_date in invalid_date_cases:
            with self.assertRaises(SanityMappingError) as ctx:
                map_to_sanity_newsletter_edition(
                    {**base_valid, "target_sunday": bad_date}
                )
            self.assertIn("target_sunday", str(ctx.exception).lower())

        # Invalid input type
        with self.assertRaises(SanityMappingError):
            map_to_sanity_newsletter_edition("not-a-dict")  # type: ignore


if __name__ == "__main__":
    unittest.main()
