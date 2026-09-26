import os
import re
import json
import logging
import datetime
from typing import Dict, Any, List, Optional, Tuple

import requests
try:
    from config import get_settings
    settings = get_settings()
except Exception:
    settings = None

logger = logging.getLogger(__name__)

# Standard themes corresponding to studio-newsletter-herald/seeds/sample-seed.ndjson
STANDARD_THEMES = [
    {
        "_id": "theme-care-for-the-poor",
        "_type": "theme",
        "name": "Care for the Poor",
        "description": "Charitable outreach, St. Vincent de Paul pantry support, and direct aid to vulnerable families.",
        "category": "service",
    },
    {
        "_id": "theme-stewardship",
        "_type": "theme",
        "name": "Stewardship",
        "description": "Responsible care, sharing of time, talent, and parish financial resources for God's kingdom.",
        "category": "stewardship",
    },
    {
        "_id": "theme-community",
        "_type": "theme",
        "name": "Community",
        "description": "Fostering parish fellowship, unity, and shared fraternal life across parish ministries.",
        "category": "community",
    },
    {
        "_id": "theme-service",
        "_type": "theme",
        "name": "Service",
        "description": "Active Christian ministry, outreach, and assistance to parishioners and the wider community.",
        "category": "service",
    },
    {
        "_id": "theme-prayer",
        "_type": "theme",
        "name": "Prayer",
        "description": "Personal and communal devotions, Eucharistic adoration, Scripture study, and liturgical prayer.",
        "category": "spiritual",
    },
]


def slugify(text: str) -> str:
    """Convert text into a URL-friendly slug."""
    text = text.lower().strip()
    text = re.sub(r"[^\w\s-]", "", text)
    text = re.sub(r"[\s_-]+", "-", text)
    return text.strip("-")


def get_sanity_token() -> Optional[str]:
    """
    Resolve Sanity auth token:
    1. settings.sanity_api_token
    2. SANITY_API_TOKEN environment variable
    3. ~/.config/sanity/config.json (local Sanity CLI auth)
    """
    if getattr(settings, "sanity_api_token", None):
        return settings.sanity_api_token

    env_token = os.environ.get("SANITY_API_TOKEN")
    if env_token:
        return env_token

    # Check Sanity CLI config file fallback
    cli_config_path = os.path.expanduser("~/.config/sanity/config.json")
    if os.path.exists(cli_config_path):
        try:
            with open(cli_config_path, "r", encoding="utf-8") as f:
                config_data = json.load(f)
                token = config_data.get("authToken")
                if token:
                    return token
        except Exception as e:
            logger.debug(f"Could not read Sanity CLI config: {e}")

    return None


def resolve_themes(text: str, liturgical_season: Optional[str] = None) -> Tuple[str, List[str]]:
    """
    Classify content into a primary theme reference ID and supporting theme IDs.
    """
    text_lower = (text or "").lower()
    season_lower = (liturgical_season or "").lower()

    # Keyword scoring for pastoral themes
    scores: Dict[str, int] = {
        "theme-care-for-the-poor": 0,
        "theme-stewardship": 0,
        "theme-community": 0,
        "theme-service": 0,
        "theme-prayer": 0,
    }

    if any(k in text_lower for k in ["poor", "pantry", "vincent", "needy", "homeless", "hunger", "food drive"]):
        scores["theme-care-for-the-poor"] += 3
    if any(k in text_lower for k in ["stewardship", "offertory", "collection", "pledge", "fund", "donation", "generosity", "tithing"]):
        scores["theme-stewardship"] += 3
    if any(k in text_lower for k in ["prayer", "adoration", "rosary", "mass", "scripture", "worship", "spiritual", "retreat", "reconciliation"]):
        scores["theme-prayer"] += 3
    if any(k in text_lower for k in ["volunteer", "ministry", "service", "outreach", "help", "visit", "hospital"]):
        scores["theme-service"] += 3
    if any(k in text_lower for k in ["fellowship", "gathering", "fair", "coffee", "community", "welcome", "parish family", "cluster"]):
        scores["theme-community"] += 2

    if "lent" in season_lower or "advent" in season_lower:
        scores["theme-prayer"] += 1
        scores["theme-care-for-the-poor"] += 1

    # Sort themes by score descending
    sorted_themes = sorted(scores.items(), key=lambda item: item[1], reverse=True)

    # Pick top as primary
    primary = sorted_themes[0][0] if sorted_themes[0][1] > 0 else "theme-community"

    # Supporting themes (themes with non-zero scores other than primary)
    supporting = [tid for tid, score in sorted_themes[1:] if score > 0 and tid != primary]
    if not supporting:
        # Default supporting themes for pastoral balance
        defaults = ["theme-service", "theme-prayer", "theme-stewardship"]
        supporting = [t for t in defaults if t != primary][:2]

    return primary, supporting


def sync_to_sanity(
    newsletter_id: int,
    filename: str,
    drive_web_view_link: Optional[str],
    target_sunday: datetime.date,
    schedule_date_val: Optional[datetime.date],
    summary_data: Dict[str, Any],
    is_valid: bool,
    error_msg: str = "",
    uploader: str = "system",
) -> Dict[str, Any]:
    """
    Creates or updates the Sanity Newsletter Edition and Editorial Workflow documents,
    placing the edition in stage 'awaiting_review'.
    
    Returns details of the created Sanity documents or error diagnostics.
    """
    token = get_sanity_token()
    project_id = getattr(settings, "sanity_project_id", "qbl0snjp")
    dataset = getattr(settings, "sanity_dataset", "production")
    api_version = getattr(settings, "sanity_api_version", "2025-08-30")

    edition_id = f"edition-herald-{newsletter_id}"
    workflow_id = f"workflow-herald-{newsletter_id}"
    now_iso = datetime.datetime.now(datetime.timezone.utc).isoformat()
    publication_date_iso = (
        schedule_date_val.isoformat()
        if schedule_date_val
        else target_sunday.isoformat()
    )

    title = summary_data.get("title") or f"Newsletter for {target_sunday}"
    summary_text = summary_data.get("summary") or ""
    liturgical_season = summary_data.get("liturgical_season")
    liturgical_year = summary_data.get("liturgical_year")
    ai_model = summary_data.get("model", "herald-ai")

    # Generate slug (max length 96 per schema)
    raw_slug = f"{target_sunday.isoformat()}-{slugify(title)}"
    slug_current = raw_slug[:96].rstrip("-")

    # Resolve theme taxonomy references
    primary_theme, supporting_themes = resolve_themes(
        f"{title}\n{summary_text}", liturgical_season
    )

    # Format validation checklist
    validation_checks = [
        "PDF text successfully extracted and sanitized for PII"
    ]
    if is_valid:
        validation_checks.append(f"Target Sunday {target_sunday} validated against liturgical calendar")
    else:
        validation_checks.append(f"Date validation alert: {error_msg or 'Target Sunday mismatch'}")
    if liturgical_season:
        validation_checks.append(f"Liturgical season identified: {liturgical_season}")
    if liturgical_year:
        validation_checks.append(f"Liturgical cycle identified: {liturgical_year}")
    validation_checks.append("Two-paragraph pastoral digest prepared for parishioners")

    # Build newsletterEdition document via dedicated mapping layer
    from helpers.sanity_mapper import map_to_sanity_newsletter_edition

    edition_doc = map_to_sanity_newsletter_edition({
        "edition_id": edition_id,
        "title": title,
        "summary": summary_text,
        "target_sunday": target_sunday,
        "publication_date": publication_date_iso,
        "liturgical_season": liturgical_season,
        "liturgical_year": liturgical_year,
        "liturgical_occasion": f"{target_sunday.strftime('%B %d')} in {liturgical_season}" if liturgical_season else None,
        "primary_theme": primary_theme,
        "supporting_themes": supporting_themes,
        "ai_generated": True,
        "ai_model": ai_model,
        "source_filename": filename,
        "source_document_url": drive_web_view_link,
        "created_at": now_iso,
        "updated_at": now_iso,
        "workflow_id": workflow_id,
    })

    # Attach pre-flight validation checklist assessed by Herald
    edition_doc["validation"] = {
        "dateValid": is_valid,
        "confidence": 0.95 if is_valid else 0.40,
        "checks": validation_checks,
    }

    # Build editorialWorkflow document
    workflow_doc: Dict[str, Any] = {
        "_id": workflow_id,
        "_type": "editorialWorkflow",
        "newsletter": {"_type": "reference", "_ref": edition_id},
        "currentStage": "awaiting_review",
        "assignedAgent": ai_model,
        "decision": "pending",
        "history": [
            {
                "_key": "h_recv",
                "stage": "received",
                "actor": uploader if uploader != "api_user" else "system",
                "note": f"Bulletin '{filename}' received via Herald upload.",
                "timestamp": now_iso,
            },
            {
                "_key": "h_proc",
                "stage": "processing",
                "actor": "herald-ai",
                "note": f"Extracted text and evaluated date validation (target Sunday: {target_sunday}).",
                "timestamp": now_iso,
            },
            {
                "_key": "h_draft",
                "stage": "draft",
                "actor": "herald-ai",
                "note": f"Synthesized two-paragraph summary with primary theme: {primary_theme}.",
                "timestamp": now_iso,
            },
            {
                "_key": "h_rev",
                "stage": "awaiting_review",
                "actor": "herald-ai",
                "note": "Pre-flight checks evaluated. Edition submitted to Sanity Studio awaiting human editorial review.",
                "timestamp": now_iso,
            },
        ],
    }

    # Assemble mutations array:
    # 1. createIfNotExists for all standard themes (guarantees references resolve)
    # 2. createOrReplace newsletterEdition
    # 3. createOrReplace editorialWorkflow
    mutations: List[Dict[str, Any]] = []
    for th in STANDARD_THEMES:
        mutations.append({"createIfNotExists": th})

    mutations.append({"createOrReplace": edition_doc})
    mutations.append({"createOrReplace": workflow_doc})

    result_payload = {
        "edition_id": edition_id,
        "workflow_id": workflow_id,
        "status": "awaiting_review",
        "stage": "awaiting_review",
        "primary_theme": primary_theme,
        "target_sunday": target_sunday.isoformat(),
        "synced": False,
        "error": None,
    }

    if not token:
        logger.warning(
            "SANITY_API_TOKEN is not configured and could not be discovered. "
            "Sanity documents were prepared locally but mutation was skipped."
        )
        result_payload["error"] = "Missing Sanity API token"
        return result_payload

    # Execute atomic mutation request to Sanity Content Lake
    mutate_url = f"https://{project_id}.api.sanity.io/v{api_version}/data/mutate/{dataset}?returnIds=true"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }

    try:
        response = requests.post(
            mutate_url,
            headers=headers,
            json={"mutations": mutations},
            timeout=30,
        )
        if response.status_code == 200:
            resp_data = response.json()
            logger.info(
                f"Successfully committed Sanity documents (edition={edition_id}, workflow={workflow_id}): "
                f"{resp_data.get('results', [])}"
            )
            result_payload["synced"] = True
            result_payload["results"] = resp_data.get("results")
        else:
            err_msg = f"Sanity mutation returned HTTP {response.status_code}: {response.text}"
            logger.error(err_msg)
            result_payload["error"] = err_msg
    except Exception as e:
        err_msg = f"Sanity mutation request failed: {str(e)}"
        logger.error(err_msg)
        result_payload["error"] = err_msg

    return result_payload
