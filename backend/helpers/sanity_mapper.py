"""
Dedicated mapping layer between Herald's existing editorial result
and the Sanity newsletterEdition content model.

Pure transformation boundary:
- No database access
- No AI invocations
- No Sanity API network calls
- No mutation of existing Herald records
"""

import re
import datetime
from typing import Dict, Any, List, Optional, Union
from dataclasses import dataclass, field


class SanityMappingError(ValueError):
    """Raised when Herald editorial result cannot be mapped to Sanity content model."""
    pass


# Known canonical theme IDs in Sanity Studio
KNOWN_THEME_IDS = {
    "theme-care-for-the-poor",
    "theme-stewardship",
    "theme-community",
    "theme-service",
    "theme-prayer",
}

# Theme name/alias to canonical Sanity document ID mapping
THEME_NAME_TO_ID = {
    "care for the poor": "theme-care-for-the-poor",
    "care-for-the-poor": "theme-care-for-the-poor",
    "care_for_the_poor": "theme-care-for-the-poor",
    "poor": "theme-care-for-the-poor",
    "charity": "theme-care-for-the-poor",
    "stewardship": "theme-stewardship",
    "community": "theme-community",
    "fellowship": "theme-community",
    "parish": "theme-community",
    "service": "theme-service",
    "outreach": "theme-service",
    "ministry": "theme-service",
    "prayer": "theme-prayer",
    "spiritual": "theme-prayer",
    "liturgy": "theme-prayer",
    "worship": "theme-prayer",
}


@dataclass
class HeraldEditorialResult:
    """Strongly typed container for Herald's editorial processing result."""
    title: str
    summary: str
    target_sunday: Union[datetime.date, str]
    publication_date: Optional[Union[datetime.date, str]] = None
    liturgical_occasion: Optional[str] = None
    liturgical_season: Optional[str] = None
    liturgical_year: Optional[str] = None
    primary_theme: Optional[str] = None
    supporting_themes: List[str] = field(default_factory=list)
    ai_generated: bool = True
    ai_model: Optional[str] = None
    source_filename: Optional[str] = None
    source_document_url: Optional[str] = None
    created_at: Optional[Union[datetime.datetime, str]] = None
    updated_at: Optional[Union[datetime.datetime, str]] = None
    workflow_id: Optional[str] = None
    delivery_id: Optional[str] = None
    edition_id: Optional[str] = None


def slugify(text: str) -> str:
    """Convert text into a URL-friendly slug."""
    text = text.lower().strip()
    text = re.sub(r"[^\w\s-]", "", text)
    text = re.sub(r"[\s_-]+", "-", text)
    return text.strip("-")


def normalize_date(val: Any, field_name: str) -> str:
    """Normalize a date or datetime object/string into 'YYYY-MM-DD'."""
    if not val:
        raise SanityMappingError(f"Missing required date field: '{field_name}'")
    if isinstance(val, datetime.datetime):
        return val.date().isoformat()
    if isinstance(val, datetime.date):
        return val.isoformat()
    if isinstance(val, str):
        val_str = val.strip()
        # Handle full ISO format e.g. 2026-09-27T00:00:00
        if "T" in val_str:
            val_str = val_str.split("T")[0]
        match = re.match(r"^\d{4}-\d{2}-\d{2}$", val_str)
        if not match:
            raise SanityMappingError(
                f"Invalid date format for '{field_name}': '{val}'. Expected 'YYYY-MM-DD'."
            )
        try:
            datetime.date.fromisoformat(val_str)
        except ValueError as err:
            raise SanityMappingError(
                f"Invalid date value for '{field_name}': '{val}'. {err}"
            )
        return val_str
    raise SanityMappingError(
        f"Unsupported date type for '{field_name}': {type(val).__name__}"
    )


def normalize_datetime(val: Any) -> str:
    """Normalize a timestamp to ISO-8601 UTC string."""
    if isinstance(val, datetime.datetime):
        if val.tzinfo is None:
            val = val.replace(tzinfo=datetime.timezone.utc)
        return val.isoformat()
    if isinstance(val, datetime.date):
        dt = datetime.datetime.combine(val, datetime.time.min, tzinfo=datetime.timezone.utc)
        return dt.isoformat()
    if isinstance(val, str) and val.strip():
        return val.strip()
    return datetime.datetime.now(datetime.timezone.utc).isoformat()


def resolve_theme_reference(theme_input: Optional[Union[str, Dict[str, Any]]]) -> str:
    """
    Resolve theme input to an existing canonical Sanity theme ID without
    dynamically inventing arbitrary theme documents.
    """
    if not theme_input:
        return "theme-community"

    if isinstance(theme_input, dict):
        ref = theme_input.get("_ref") or theme_input.get("id")
        if ref:
            return resolve_theme_reference(ref)
        name = theme_input.get("name")
        if name:
            return resolve_theme_reference(name)
        return "theme-community"

    raw_theme = str(theme_input).strip().lower()

    # Exact match in known Sanity theme IDs
    if raw_theme in KNOWN_THEME_IDS:
        return raw_theme

    # Direct name/alias match
    if raw_theme in THEME_NAME_TO_ID:
        return THEME_NAME_TO_ID[raw_theme]

    # Partial/keyword match
    for alias, tid in THEME_NAME_TO_ID.items():
        if alias in raw_theme:
            return tid

    # Fallback to existing community theme rather than inventing a document
    return "theme-community"


def map_to_sanity_newsletter_edition(
    data: Union[HeraldEditorialResult, Dict[str, Any]],
    require_primary_theme: bool = False,
    **overrides: Any,
) -> Dict[str, Any]:
    """
    Pure deterministic mapping from Herald editorial result to Sanity newsletterEdition.

    Rules applied:
    - status must be 'awaiting_review'
    - aiGenerated must be boolean (True if from AI pipeline)
    - aiModel reflects the actual model used
    - supportingThemes are mapped to canonical existing theme references with unique _key
    - does not invent dynamic theme documents
    - validates all required fields
    """
    # 1. Normalize input dictionary
    if isinstance(data, HeraldEditorialResult):
        raw: Dict[str, Any] = {
            "title": data.title,
            "summary": data.summary,
            "target_sunday": data.target_sunday,
            "publication_date": data.publication_date,
            "liturgical_occasion": data.liturgical_occasion,
            "liturgical_season": data.liturgical_season,
            "liturgical_year": data.liturgical_year,
            "primary_theme": data.primary_theme,
            "supporting_themes": data.supporting_themes,
            "ai_generated": data.ai_generated,
            "ai_model": data.ai_model,
            "source_filename": data.source_filename,
            "source_document_url": data.source_document_url,
            "created_at": data.created_at,
            "updated_at": data.updated_at,
            "workflow_id": data.workflow_id,
            "delivery_id": data.delivery_id,
            "edition_id": data.edition_id,
        }
    elif isinstance(data, dict):
        raw = dict(data)
    else:
        raise SanityMappingError(f"Expected HeraldEditorialResult or dict, got {type(data).__name__}")

    raw.update(overrides)

    # 2. Extract and validate required fields
    title = raw.get("title")
    if not title or not isinstance(title, str) or not title.strip():
        raise SanityMappingError("Missing or empty required field: 'title'")
    title = title.strip()

    summary = raw.get("summary")
    if not summary or not isinstance(summary, str) or not summary.strip():
        raise SanityMappingError("Missing or empty required field: 'summary'")
    summary = summary.strip()

    target_sunday_raw = raw.get("target_sunday") or raw.get("targetSunday")
    target_sunday = normalize_date(target_sunday_raw, "target_sunday")

    publication_date_raw = (
        raw.get("publication_date")
        or raw.get("publicationDate")
        or raw.get("schedule_date")
        or target_sunday
    )
    publication_date = normalize_date(publication_date_raw, "publication_date")

    # 3. Resolve themes to existing Sanity theme references
    primary_theme_input = (
        raw.get("primary_theme")
        or raw.get("primaryTheme")
        or raw.get("theme")
    )
    if require_primary_theme:
        if primary_theme_input is None or (isinstance(primary_theme_input, str) and not primary_theme_input.strip()):
            raise SanityMappingError("Missing required theme reference: 'primary_theme' must be provided.")

    primary_theme_id = resolve_theme_reference(primary_theme_input)

    raw_supporting = raw.get("supporting_themes") or raw.get("supportingThemes") or []
    if isinstance(raw_supporting, (str, dict)):
        raw_supporting = [raw_supporting]

    supporting_theme_ids: List[str] = []
    for item in raw_supporting:
        tid = resolve_theme_reference(item)
        if tid != primary_theme_id and tid not in supporting_theme_ids:
            supporting_theme_ids.append(tid)

    # 4. Generate deterministic slug
    slug_base = f"{target_sunday}-{slugify(title)}"
    slug_current = slug_base[:96].rstrip("-")

    # 5. Extract AI metadata
    ai_generated = raw.get("ai_generated")
    if ai_generated is None:
        ai_generated = raw.get("aiGenerated", True)
    ai_generated = bool(ai_generated)

    ai_model = raw.get("ai_model") or raw.get("aiModel") or raw.get("model")
    if ai_model and not isinstance(ai_model, str):
        ai_model = str(ai_model)

    # 6. Extract timestamps
    created_at = normalize_datetime(raw.get("created_at") or raw.get("createdAt"))
    updated_at = normalize_datetime(raw.get("updated_at") or raw.get("updatedAt") or created_at)

    # 7. Construct Sanity newsletterEdition document
    edition: Dict[str, Any] = {
        "_type": "newsletterEdition",
        "title": title,
        "slug": {
            "_type": "slug",
            "current": slug_current,
        },
        "publicationDate": publication_date,
        "targetSunday": target_sunday,
        "primaryTheme": {
            "_type": "reference",
            "_ref": primary_theme_id,
        },
        "supportingThemes": [
            {
                "_key": f"st_{idx}",
                "_type": "reference",
                "_ref": tid,
            }
            for idx, tid in enumerate(supporting_theme_ids)
        ],
        "summary": summary,
        "status": "awaiting_review",
        "aiGenerated": ai_generated,
        "createdAt": created_at,
        "updatedAt": updated_at,
    }

    # Optional deterministic document ID
    edition_id = raw.get("edition_id") or raw.get("_id")
    if edition_id:
        edition["_id"] = str(edition_id)

    # Optional AI Model
    if ai_model:
        edition["aiModel"] = ai_model

    # Optional source filename
    source_filename = raw.get("source_filename") or raw.get("sourceFilename") or raw.get("filename")
    if source_filename and str(source_filename).strip():
        edition["sourceFilename"] = str(source_filename).strip()

    # Optional source document URL
    source_url = raw.get("source_document_url") or raw.get("sourceDocumentUrl") or raw.get("drive_web_view_link")
    if source_url and isinstance(source_url, str) and source_url.strip().startswith(("http://", "https://")):
        edition["sourceDocumentUrl"] = source_url.strip()

    # Optional liturgical occasion
    occasion = raw.get("liturgical_occasion") or raw.get("liturgicalOccasion")
    if occasion and str(occasion).strip():
        edition["liturgicalOccasion"] = str(occasion).strip()

    # Optional liturgical season
    season = raw.get("liturgical_season") or raw.get("liturgicalSeason")
    if season and str(season).strip():
        edition["liturgicalSeason"] = str(season).strip()

    # Optional liturgical year
    year = raw.get("liturgical_year") or raw.get("liturgicalYear")
    if year and str(year).strip():
        edition["liturgicalYear"] = str(year).strip()

    # Optional workflow reference
    workflow_id = raw.get("workflow_id") or raw.get("workflowId") or raw.get("workflow")
    if workflow_id:
        ref_id = workflow_id if isinstance(workflow_id, str) else workflow_id.get("_ref")
        if ref_id:
            edition["workflow"] = {
                "_type": "reference",
                "_ref": str(ref_id),
            }

    # Optional delivery reference
    delivery_id = raw.get("delivery_id") or raw.get("deliveryId") or raw.get("delivery")
    if delivery_id:
        ref_id = delivery_id if isinstance(delivery_id, str) else delivery_id.get("_ref")
        if ref_id:
            edition["delivery"] = {
                "_type": "reference",
                "_ref": str(ref_id),
            }

    return edition
