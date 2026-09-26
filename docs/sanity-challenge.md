# Sanity Challenge Build Record & Decision Log

> **Note**: This is an active, unpolished engineering build log capturing raw architectural reasoning, design trade-offs, and live decisions during the Sanity Content Operating System implementation for Newsletter Herald.

---

## Why Sanity?

Newsletter Herald originally stored editorial state primarily in PostgreSQL (SQLAlchemy models: `Newsletter`, `Extraction`, alembic migrations).

We introduced Sanity as the content operating system for the editorial layer for several key reasons:

1. **Decoupling Content from Transactional Postgres**:
   - In Postgres, editorial state was tightly coupled to rigid relational tables and raw JSON blobs for AI extraction outputs.
   - Parish church bulletins contain semi-structured liturgical metadata, fluid theme taxonomies, rich summaries, and multi-actor review histories.
   - Adding human-in-the-loop review, visual content previews, real-time draft updates, and revision tracking in Postgres requires building an entire custom CMS from scratch (custom form controls, visual diffing, role management, live preview canvas).

2. **Sanity as Content Lake & Editorial Control Plane**:
   - Sanity Content Lake gives us real-time structured content, schema-as-code in TypeScript, portable text/rich fields, graph-like reference traversal, GROQ queries, real-time mutation subscriptions, and an out-of-the-box Studio UI for parish volunteers and priests.
   - Clean division of responsibility:
     - **Postgres / FastAPI**: Ingestion pipelines, raw document storage, background OCR worker tasks, email delivery queue execution.
     - **Sanity Content Lake**: Editorial source of truth, content staging, review canvas, liturgical taxonomy, validation assertions, and human approval gate.

---

## Why these schemas?

We designed four core schema types in `studio-newsletter-herald/schemaTypes`:

### 1. `newsletterEdition` (`newsletterEdition.ts`)
The central editorial artifact representing a synthesized church bulletin for a target Sunday liturgical cycle.
- **Liturgical calendar grounding**: Dedicated fields for `publicationDate`, `targetSunday`, `liturgicalOccasion`, `liturgicalSeason`, and `liturgicalYear` (e.g., Year B, Ordinary Time). Church communications live and die by Sunday delivery accuracy.
- **Provenance tracking**: `sourceDocumentUrl` and `sourceFilename` link the edition back to the original bulletin PDF received from parish staff via email/Hermes.
- **Editorial digest**: `summary` field formatted as a two-paragraph parishioner-facing reflection and ministry digest.
- **Validation metadata**: An embedded `validation` object containing:
  - `dateValid` (boolean): Did the target Sunday match the extracted liturgical calendar?
  - `confidence` (number): AI extraction and thematic alignment confidence score (0 to 1.0).
  - `checks` (string array): Transparent assertions evaluated by the ingestion agent.
- **AI attribution**: `aiGenerated` and `aiModel` (e.g., `sample-herald-editor`, `claude-3-5-sonnet`) so human reviewers always know what generated the draft.
- **Slug**: Generated intelligently from `targetSunday` and liturgical title (`slug.current = 2026-09-27-26th-sunday-ordinary-time`).

### 2. `theme` (`theme.ts`)
A dedicated taxonomy document rather than a hardcoded string enum.
- Parish ministries, charisms, and liturgical topics (e.g., Stewardship, Care for the Poor, Community, Prayer, Youth Ministry, Liturgy) evolve over time.
- Having a separate `theme` document enables:
  - First-class taxonomy curation by parish staff without code deploys.
  - Categorization into spiritual, community, service, stewardship, vocation, and liturgy buckets.
  - Multi-reference links from `newsletterEdition` via `primaryTheme` (mandatory 1:1 reference) and `supportingThemes` (array of references).
  - GROQ queries across editions by theme (e.g., finding all past editions touching "Care for the Poor").

### 3. `editorialWorkflow` (`editorialWorkflow.ts`)
A dedicated governance document referencing `newsletterEdition`.
- Tracks `currentStage`: `received` ➔ `processing` ➔ `draft` ➔ `awaiting_review` ➔ `approved` ➔ `scheduled` ➔ `sent`.
- Tracks `assignedAgent` (AI worker handling automated steps) and `reviewer` (human editor executing the review gate).
- Explicit `decision` gate (`pending`, `approved`, `rejected`) and `decisionAt` timestamp.
- Structured chronological `history` array capturing each transition: stage, actor (`system`, `herald-ai`, human editor), timestamp, and note.

### 4. `delivery` (`delivery.ts`)
A separate document managing the dispatch lifecycle and analytics.
- References `newsletterEdition`.
- Stores `scheduledFor` datetime and `status` (`pending`, `scheduled`, `sending`, `sent`, `failed`, `cancelled`).
- Embedded `deliveryStats` tracking `recipientCount`, `deliveredCount`, `failedCount`, and `lastUpdatedAt` synced from the Herald delivery engine.

---

## Why Workflow is a document

One of our most deliberate schema choices was making `editorialWorkflow` a distinct document with a reference to `newsletterEdition`, rather than embedding workflow fields directly inside `newsletterEdition`.

### Reasoning:
1. **Decoupled Lifecycle & Permission Boundaries**:
   - Editorial content (headline, reflection text, liturgical season, themes) and editorial governance (state transitions, agent handoffs, reviewer approval, audit entries) change at different frequencies and under different permissions.
   - Separate documents allow Sanity Studio to configure dedicated desk views (e.g., an "Editorial Inbox" or "Awaiting Approval" desk view) without cluttering the content editing interface.
2. **Preventing Write Contention Between AI Agents & Humans**:
   - An automated background worker (like the Hermes ingestion agent or Herald AI) updates stage progress and appends audit logs (`processing` ➔ `draft` ➔ `awaiting_review`).
   - If workflow was embedded inside `newsletterEdition`, an agent writing a status change or validation log while a human editor is tweaking summary text creates concurrent mutation conflicts or noisy content revision diffs.
   - With separate documents, the agent writes to the workflow document while the human polishes the edition document independently.
3. **Clean Event-Driven Subscriptions (GROQ Listening)**:
   - External services, webhooks, or messaging bots (e.g., Hermes WhatsApp/Signal alerting) can listen to mutations strictly on `_type == "editorialWorkflow"`:
     ```groq
     *[_type == "editorialWorkflow" && currentStage == "awaiting_review"]{
       _id,
       decision,
       "newsletter": newsletter->{title, targetSunday, summary}
     }
     ```
   - This keeps notification logic lightweight and decoupled from changes to edition drafts.
4. **Audit Trail Immutability**:
   - The workflow document preserves the full history array of who changed what stage and when. If an edition is rejected and re-processed, we can archive or track distinct workflow cycles without destroying content drafts.

---

## AI-assisted development

How AI pair programming shaped this build in real time:

- **Domain-Specific Schema Synthesis**:
  - Roman Catholic parish communications have distinct liturgical nuances: Sunday dates are non-negotiable anchor points, liturgical cycles (Year A/B/C, Ordinary Time vs. Lent/Advent) dictate themes, and summaries must balance pastoral warmth with factual event details.
  - The AI assistant helped translate these domain requirements into clean Sanity v3 TypeScript schemas with strict custom validation rules (e.g., verifying allowed stage values, Sunday date formatting, confidence ranges).
- **Agent-First Schema Ergonomics**:
  - Rather than treating AI as an external black box that spits text into a CMS, the schema was designed to treat the AI agent as a first-class citizen:
    - Explicit `assignedAgent` field.
    - `history[].actor` field distinguishing `system`, `herald-ai`, and human editors.
    - Embedded `validation` pre-flight checks object (`dateValid`, `confidence`, `checks`) so human reviewers can immediately see *why* the AI made certain extraction decisions.
- **Rapid Scaffold & Seed Loop**:
  - The Sanity Studio, schemas, GROQ preview projections, NDJSON seed dataset (`seeds/sample-seed.ndjson`), and Sanity CLI seeding script (`scripts/seed.ts`) were iterated in tight, fast loops using persistent terminal commands and sanity validation checks.

---

## Decisions we rejected

Capturing discarded alternatives and why they were turned down:

1. **Rejected: Embedding workflow fields directly inside `newsletterEdition`**:
   - *Why rejected*: Pollutes content revision history, causes write-conflict contention during concurrent agent/human edits, and prevents clean webhook subscriptions for workflow events.
2. **Rejected: Storing themes as flat string tags/enums (`string[]`)**:
   - *Why rejected*: Flat strings lead to typos ("stewardship" vs "Stewardship"), lack parish ministry descriptions, cannot be grouped by category (spiritual vs community vs service), and break relational GROQ queries across years of parish archives.
3. **Rejected: Storing raw multi-page bulletin PDF OCR text in Sanity**:
   - *Why rejected*: Parish bulletin PDFs contain 20KB-50KB of uncurated OCR text—advertisements, mass intentions tables, donor lists. Storing all raw OCR text in the Sanity document bloats the content lake, increases payload size, and clutters the editor UI. Raw files belong in Cloud Storage / Postgres; Sanity holds the synthesized editorial layer (`summary`, `themes`, `liturgicalOccasion`) and references the `sourceDocumentUrl`.
4. **Rejected: Bi-directional sync between Postgres and Sanity**:
   - *Why rejected*: Two-way master-master database sync between Postgres and Sanity creates split-brain edge cases and race conditions. Instead, we established clear architectural boundaries:
     - Postgres/FastAPI owns ingestion execution, raw file storage, and email delivery dispatch.
     - Sanity owns the editorial draft, liturgical taxonomy, human-in-the-loop review state, and publication sign-off.
     - The dispatch service queries Sanity for `approved` / `scheduled` editions when it is time to send.
5. **Rejected: Premature multi-tenant workspace complexification**:
   - *Why rejected*: Considered setting up multi-workspace configs for multi-parish clusters right away. Rejected to keep the hackathon/challenge scope laser-focused on a rock-solid single parish workflow with clean, extensible foundations that can easily scale out later.
