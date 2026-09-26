"""
Sanity editorial creation operation.

Atomically creates or idempotently updates:
1. newsletterEdition
2. editorialWorkflow
3. delivery

Uses Sanity references to connect all three documents and guarantees
idempotency via deterministic document IDs.
"""

import os
import json
import logging
import datetime
from typing import Dict, Any, List, Optional, Union

import requests
from helpers.sanity_mapper import (
    map_to_sanity_newsletter_edition,
    HeraldEditorialResult,
    SanityMappingError,
    slugify,
    normalize_date,
    normalize_datetime,
)
from helpers.sanity_client import (
    STANDARD_THEMES,
    get_sanity_token,
)

try:
    from config import get_settings
    settings = get_settings()
except Exception:
    settings = None

logger = logging.getLogger(__name__)


class SanityEditorialCreationError(Exception):
    """Raised when Sanity editorial document creation fails or is rejected."""
    pass


def derive_deterministic_source_id(data: Dict[str, Any]) -> str:
    """
    Derives a stable, deterministic identifier from Herald newsletter data.
    Ensures retrying the same newsletter produces identical Sanity document IDs.
    """
    explicit_id = (
        data.get("newsletter_id")
        or data.get("id")
        or data.get("external_id")
        or data.get("source_id")
    )
    if explicit_id is not None:
        clean_id = str(explicit_id).strip()
        if clean_id:
            return clean_id

    # Fallback to target Sunday + slugified filename or title
    target_sunday_raw = data.get("target_sunday") or data.get("targetSunday")
    target_sunday = normalize_date(target_sunday_raw, "target_sunday")
    filename_or_title = (
        data.get("source_filename")
        or data.get("sourceFilename")
        or data.get("title")
        or "newsletter"
    )
    return f"{target_sunday}-{slugify(str(filename_or_title))}"


def create_sanity_editorial_documents(
    herald_data: Union[HeraldEditorialResult, Dict[str, Any]],
    token: Optional[str] = None,
    project_id: Optional[str] = None,
    dataset: Optional[str] = None,
    api_version: Optional[str] = None,
    session: Optional[Any] = None,
) -> Dict[str, str]:
    """
    Creates the three related Sanity documents (newsletterEdition, editorialWorkflow, delivery)
    in a single atomic Sanity transaction.

    Initial state:
    - newsletterEdition: status = 'awaiting_review'
    - editorialWorkflow: currentStage = 'awaiting_review', assignedAgent = 'herald-ai', decision = 'pending'
      history containing: received, processing, draft, awaiting_review
    - delivery: status = 'pending'

    Returns:
    {
        "newsletterId": "<edition_id>",
        "workflowId": "<workflow_id>",
        "deliveryId": "<delivery_id>"
    }
    """
    # 1. Normalize input dictionary
    if isinstance(herald_data, HeraldEditorialResult):
        raw_data: Dict[str, Any] = {
            "title": herald_data.title,
            "summary": herald_data.summary,
            "target_sunday": herald_data.target_sunday,
            "publication_date": herald_data.publication_date,
            "liturgical_occasion": herald_data.liturgical_occasion,
            "liturgical_season": herald_data.liturgical_season,
            "liturgical_year": herald_data.liturgical_year,
            "primary_theme": herald_data.primary_theme,
            "supporting_themes": herald_data.supporting_themes,
            "ai_generated": herald_data.ai_generated,
            "ai_model": herald_data.ai_model,
            "source_filename": herald_data.source_filename,
            "source_document_url": herald_data.source_document_url,
            "created_at": herald_data.created_at,
            "updated_at": herald_data.updated_at,
            "workflow_id": herald_data.workflow_id,
            "delivery_id": herald_data.delivery_id,
            "edition_id": herald_data.edition_id,
        }
    elif isinstance(herald_data, dict):
        raw_data = dict(herald_data)
    else:
        raise SanityMappingError(f"Expected HeraldEditorialResult or dict, got {type(herald_data).__name__}")

    # 2. Derive stable, deterministic Sanity IDs
    source_id = derive_deterministic_source_id(raw_data)
    newsletter_id = f"edition-herald-{source_id}"
    workflow_id = f"workflow-herald-{source_id}"
    delivery_id = f"delivery-herald-{source_id}"

    # 3. Map newsletterEdition via dedicated mapper (enforcing required primary theme)
    edition_doc = map_to_sanity_newsletter_edition(
        raw_data,
        require_primary_theme=True,
        edition_id=newsletter_id,
        workflow_id=workflow_id,
        delivery_id=delivery_id,
    )

    # Ensure status is strictly awaiting_review per requirements
    edition_doc["status"] = "awaiting_review"

    target_sunday = edition_doc["targetSunday"]
    now_iso = normalize_datetime(raw_data.get("created_at"))
    filename = edition_doc.get("sourceFilename") or "bulletin.pdf"
    uploader = str(raw_data.get("uploader") or "system")

    # 4. Construct editorialWorkflow document
    workflow_doc: Dict[str, Any] = {
        "_id": workflow_id,
        "_type": "editorialWorkflow",
        "newsletter": {
            "_type": "reference",
            "_ref": newsletter_id,
        },
        "currentStage": "awaiting_review",
        "assignedAgent": "herald-ai",
        "decision": "pending",
        "history": [
            {
                "_key": "hist_1",
                "stage": "received",
                "actor": uploader if uploader != "api_user" else "system",
                "timestamp": now_iso,
                "note": f"Newsletter source document '{filename}' received.",
            },
            {
                "_key": "hist_2",
                "stage": "processing",
                "actor": "herald-ai",
                "timestamp": now_iso,
                "note": f"Text extracted; date validation evaluated for target Sunday {target_sunday}.",
            },
            {
                "_key": "hist_3",
                "stage": "draft",
                "actor": "herald-ai",
                "timestamp": now_iso,
                "note": "AI summary synthesized and theme taxonomy assigned.",
            },
            {
                "_key": "hist_4",
                "stage": "awaiting_review",
                "actor": "herald-ai",
                "timestamp": now_iso,
                "note": "Pre-flight validation complete. Handoff to human editorial review.",
            },
        ],
    }

    # 5. Construct delivery document
    # Scheduled for target Sunday at 12:00:00 UTC by default
    scheduled_for = f"{target_sunday}T12:00:00.000Z"
    delivery_doc: Dict[str, Any] = {
        "_id": delivery_id,
        "_type": "delivery",
        "newsletter": {
            "_type": "reference",
            "_ref": newsletter_id,
        },
        "scheduledFor": scheduled_for,
        "status": "pending",
        "deliveryStats": {
            "recipientCount": 0,
            "deliveredCount": 0,
            "failedCount": 0,
            "lastUpdatedAt": now_iso,
        },
    }

    # 6. Assemble atomic mutations array
    # Uses createIfNotExists for themes, and createOrReplace for the three edition docs
    mutations: List[Dict[str, Any]] = []
    for th in STANDARD_THEMES:
        mutations.append({"createIfNotExists": th})

    mutations.append({"createOrReplace": edition_doc})
    mutations.append({"createOrReplace": workflow_doc})
    mutations.append({"createOrReplace": delivery_doc})

    # 7. Execute atomic mutation via Sanity Content Lake REST API
    resolved_token = token or get_sanity_token()
    if not resolved_token:
        raise SanityEditorialCreationError("Missing required Sanity API authentication token.")

    p_id = project_id or getattr(settings, "sanity_project_id", "qbl0snjp")
    d_set = dataset or getattr(settings, "sanity_dataset", "production")
    ver = api_version or getattr(settings, "sanity_api_version", "2025-08-30")

    mutate_url = f"https://{p_id}.api.sanity.io/v{ver}/data/mutate/{d_set}?returnIds=true"
    headers = {
        "Authorization": f"Bearer {resolved_token}",
        "Content-Type": "application/json",
    }

    http_client = session if session is not None else requests

    try:
        response = http_client.post(
            mutate_url,
            headers=headers,
            json={"mutations": mutations},
            timeout=30,
        )
    except Exception as exc:
        raise SanityEditorialCreationError(f"Sanity mutation network request failed: {exc}") from exc

    if response.status_code != 200:
        raise SanityEditorialCreationError(
            f"Sanity atomic mutation failed with HTTP {response.status_code}: {response.text}"
        )

    logger.info(
        f"Sanity editorial documents successfully created: "
        f"newsletterId={newsletter_id}, workflowId={workflow_id}, deliveryId={delivery_id}"
    )

    return {
        "newsletterId": newsletter_id,
        "workflowId": workflow_id,
        "deliveryId": delivery_id,
    }
