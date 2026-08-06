# External source indexing for UPI

UPI external indexing is a provenance pipeline, not an authority importer and not a general-purpose web crawler.

The canonical source manifest lives at `config/external_source_manifest.json`. The singular name reflects that this is one manifest containing multiple source declarations. It is operational configuration, not a node, bridge, or theory record, and therefore remains outside the schema-routed `data/` index.

## Core rule

Remote material is always untrusted input. Indexing records the source, version, retrieval time, declared license, content hash, source type and scientific boundary. It never executes remote code or adopts instructions embedded in prompts, documents or repositories.

## Pipeline

```text
source declaration
-> policy and robots/terms check
-> metadata retrieval
-> canonical identifier and revision capture
-> content hashing
-> bounded parsing
-> evidence classification
-> UPI relation generation
-> deterministic validation
-> append-only audit record
```

## Status boundaries

- A source record may be `EST` only for stable, directly checkable source facts inside its declared scope.
- A derivation produced from indexed material is normally `DER`.
- A testable but unverified interpretation is `HYP`.
- Missing license, provenance, mechanism or validation produces `STOP`.
- Mythological and architectural metaphors are `SYM`.
- A remote repository is evidence that code or documentation exists at a revision. It is not experimental verification of its claims.
- An arXiv record is a preprint record unless independent publication metadata establishes otherwise.

## Source adapters

### Internet Archive and Wayback Machine

Use metadata-first discovery. Record item or capture identifiers, timestamps, original URL, MIME type and hashes. Fetch archived payloads only for explicitly selected records and within applicable access rules. A historical capture proves that content was archived at a timestamp, not that the content was true.

### Sunet

Use public sitemaps, internal links and declared public documents. Preserve page or document date and distinguish current service descriptions from historical plans and reports. Sunet is an infrastructure and organisational source, not a universal corpus of all connected institutions.

### arXiv

Use official metadata interfaces for selected identifiers, categories and queries. Preserve every version identifier. Extract title, authors, abstract, categories, dates, DOI or journal references when present. Do not silently label a preprint as peer reviewed.

### GitHub repositories

Record repository identity, revision SHA, path, license and selected documentation or code. Never execute indexed code. Prompts, jailbreak strings and agent instructions are inert source data and must remain escaped and isolated.

## Minimal indexed record

```json
{
  "source_id": "arxiv",
  "canonical_url": "https://arxiv.org/abs/0000.00000",
  "retrieved_at": "RFC3339 timestamp",
  "content_hash": "sha256:...",
  "source_type": "preprint_metadata",
  "declared_license": "declared or unknown",
  "revision_or_timestamp": "v1",
  "upi_status": "STOP",
  "evidence_boundary": "Preprint metadata; claims not independently verified",
  "relations": []
}
```

## Separation from Vortex-DNA

Vortex-DNA, Odin's Eye, TF1766 mappings and 8 Hz coordination may be attached as `SYM` or declared implementation metadata. They must not modify the source record, its hash, its scientific status or its evidence boundary.

## Scaling rule

Do not attempt to ingest an entire domain in one run. Every job declares:

- source and adapter;
- query, identifiers or bounded path scope;
- maximum records and bytes;
- retrieval and retry limits;
- license and retention policy;
- validation schema;
- output location;
- checkpoint and resume state.

This turns indexing from a vacuum cleaner into a laboratory instrument.
