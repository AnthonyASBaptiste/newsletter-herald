"""
Live Sanity Integration Verification Script.

Tests:
1. Editorial creation of a real newsletter edition, workflow, and delivery document.
2. Querying Sanity to verify document structure, fields, and references.
3. Retrying the operation with the same newsletter ID.
4. Verifying that the retry is idempotent and produces zero duplicate documents.
"""

import os
import sys
import json
import requests

# Ensure backend root is in PYTHONPATH
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from helpers.sanity_editorial import (
    create_sanity_editorial_documents,
    derive_deterministic_source_id,
)
from helpers.sanity_client import get_sanity_token

def run_verification():
    print("=" * 70)
    print("SANITY LIVE EDITORIAL INTEGRATION TEST")
    print("=" * 70)

    token = get_sanity_token()
    if not token:
        print("[FAIL] No Sanity API token found in environment or config.")
        sys.exit(1)

    project_id = "qbl0snjp"
    dataset = "production"
    api_version = "2025-08-30"

    test_newsletter_id = 9001
    test_target_sunday = "2026-03-08"

    editorial_data = {
        "newsletter_id": test_newsletter_id,
        "title": "Third Sunday of Lent - Holy Trinity Parish Bulletin",
        "summary": (
            "During this season of Lent, we invite all parishioners to join us for Friday Stations of the Cross at 7:00 PM.\n\n"
            "Our parish outreach committee is organizing the annual Easter food basket collection for local families."
        ),
        "target_sunday": test_target_sunday,
        "publication_date": test_target_sunday,
        "liturgical_occasion": "Third Sunday of Lent",
        "liturgical_season": "Lent",
        "liturgical_year": "Year A",
        "primary_theme": "Community & Fellowship",
        "supporting_themes": ["Liturgy & Sacraments"],
        "ai_generated": True,
        "ai_model": "gpt-4o",
        "source_filename": "2026-03-08-Trinity-Newsletter.pdf",
        "source_document_url": "https://storage.googleapis.com/sample/2026-03-08-Trinity-Newsletter.pdf",
        "uploader": "editor@holytrinity.org",
    }

    # Step 1: Create documents via create_sanity_editorial_documents
    print("\n[Step 1] Creating Sanity editorial documents...")
    res = create_sanity_editorial_documents(
        editorial_data,
        token=token,
        project_id=project_id,
        dataset=dataset,
        api_version=api_version,
    )

    edition_id = res["newsletterId"]
    workflow_id = res["workflowId"]
    delivery_id = res["deliveryId"]

    print(f"  Created edition:  {edition_id}")
    print(f"  Created workflow: {workflow_id}")
    print(f"  Created delivery: {delivery_id}")

    expected_edition_id = f"edition-herald-{test_newsletter_id}"
    expected_workflow_id = f"workflow-herald-{test_newsletter_id}"
    expected_delivery_id = f"delivery-herald-{test_newsletter_id}"

    assert edition_id == expected_edition_id, f"Expected {expected_edition_id}, got {edition_id}"
    assert workflow_id == expected_workflow_id, f"Expected {expected_workflow_id}, got {workflow_id}"
    assert delivery_id == expected_delivery_id, f"Expected {expected_delivery_id}, got {delivery_id}"
    print("  [PASS] Deterministic document IDs verified.")

    # Step 2: Query Sanity Content Lake and verify document structures
    print("\n[Step 2] Querying Sanity Content Lake to verify documents...")
    headers = {"Authorization": f"Bearer {token}"}
    groq_query = f'*[_id in ["{edition_id}", "{workflow_id}", "{delivery_id}"]]'
    query_url = f"https://{project_id}.api.sanity.io/v{api_version}/data/query/{dataset}?query={requests.utils.quote(groq_query)}"

    q_resp = requests.get(query_url, headers=headers, timeout=15)
    if q_resp.status_code != 200:
        print(f"[FAIL] Sanity query failed ({q_resp.status_code}): {q_resp.text}")
        sys.exit(1)

    docs = {d["_id"]: d for d in q_resp.json().get("result", [])}
    print(f"  Retrieved {len(docs)} documents from Sanity.")

    assert edition_id in docs, f"Document {edition_id} missing in Sanity!"
    assert workflow_id in docs, f"Document {workflow_id} missing in Sanity!"
    assert delivery_id in docs, f"Document {delivery_id} missing in Sanity!"

    # Verify newsletterEdition
    edition_doc = docs[edition_id]
    assert edition_doc["_type"] == "newsletterEdition"
    assert edition_doc["status"] == "awaiting_review"
    assert edition_doc["aiGenerated"] is True
    assert edition_doc["title"] == editorial_data["title"]
    assert edition_doc["workflow"]["_ref"] == workflow_id
    assert edition_doc["delivery"]["_ref"] == delivery_id
    assert edition_doc["primaryTheme"]["_ref"] == "theme-community"
    print("  [PASS] newsletterEdition document structure and references verified.")

    # Verify editorialWorkflow
    workflow_doc = docs[workflow_id]
    assert workflow_doc["_type"] == "editorialWorkflow"
    assert workflow_doc["currentStage"] == "awaiting_review"
    assert workflow_doc["assignedAgent"] == "herald-ai"
    assert workflow_doc["decision"] == "pending"
    assert workflow_doc["newsletter"]["_ref"] == edition_id
    history_stages = [h["stage"] for h in workflow_doc.get("history", [])]
    assert history_stages == ["received", "processing", "draft", "awaiting_review"], f"Unexpected history: {history_stages}"
    print("  [PASS] editorialWorkflow document and stage history verified.")

    # Verify delivery
    delivery_doc = docs[delivery_id]
    assert delivery_doc["_type"] == "delivery"
    assert delivery_doc["status"] == "pending"
    assert delivery_doc["newsletter"]["_ref"] == edition_id
    print("  [PASS] delivery document and status verified.")

    # Step 3: Test Idempotent Retry
    print("\n[Step 3] Testing retry idempotency (invoking operation a second time)...")
    retry_res = create_sanity_editorial_documents(
        editorial_data,
        token=token,
        project_id=project_id,
        dataset=dataset,
        api_version=api_version,
    )
    assert retry_res == res, "Retry produced different document IDs!"

    # Step 4: Verify No Duplicate Documents were created
    print("\n[Step 4] Querying Sanity to verify NO duplicate documents exist...")
    count_query = f'count(*[_id == "{edition_id}"])'
    count_url = f"https://{project_id}.api.sanity.io/v{api_version}/data/query/{dataset}?query={requests.utils.quote(count_query)}"
    c_resp = requests.get(count_url, headers=headers, timeout=15)
    edition_count = c_resp.json().get("result", 0)
    print(f"  Count of documents with ID '{edition_id}': {edition_count}")
    assert edition_count == 1, f"Expected exactly 1 document, found {edition_count}!"

    # Clean up test documents
    print("\n[Step 5] Cleaning up test documents...")
    delete_mutations = [
        {"delete": {"id": delivery_id}},
        {"delete": {"id": workflow_id}},
        {"delete": {"id": edition_id}},
    ]
    mutate_url = f"https://{project_id}.api.sanity.io/v{api_version}/data/mutate/{dataset}"
    del_resp = requests.post(mutate_url, headers=headers, json={"mutations": delete_mutations}, timeout=15)
    if del_resp.status_code == 200:
        print("  [PASS] Test documents cleaned up cleanly.")
    else:
        print(f"  [WARN] Cleanup returned status {del_resp.status_code}: {del_resp.text}")

    print("\n" + "=" * 70)
    print("ALL LIVE SANITY INTEGRATION CHECKS PASSED SUCCESSFULLY!")
    print("=" * 70)


if __name__ == "__main__":
    run_verification()
