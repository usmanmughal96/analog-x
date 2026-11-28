# Independent Analog-Label Validation Protocol

## Purpose

This protocol defines the evidence needed before ANALOG-X reports a held-out ROC-AUC or another model-performance metric. The current label file is intentionally empty. No labels are inferred from the terrain score, a competitor's ranking, a map preview or an unreviewed opinion.

## Required record

Each row in `data/validation/independent_analog_labels.json` must contain:

- `target`: `moon` or `mars`.
- `candidate_id`: exact candidate ID from the released global shortlist.
- `label`: `positive` or `negative`.
- `spatial_group`: a predeclared region/geologic block used to prevent neighbouring windows leaking across train/test.
- `evidence_ref`: DOI, official dataset/product ID, published map reference or controlled expert-review record.
- `reviewer` and `review_date_utc` (an explicit ISO 8601 UTC date-time ending in `Z` or `+00:00`).
- `criterion_version`: exactly `terrain_morphology_transfer_v1` for this release.
- `review_scope`: criterion version and task-specific rationale.
- `reviewer_confidence_1_to_5`: integer 1–5, not a boolean.
- `reviewer_independence_attested`: explicit boolean `true`.
- `core_terrain_index`: copied from the exact candidate release being evaluated.

## Labeling rules

1. Define the target-specific physical/process question and positive/negative criteria before inspecting candidate scores.
2. Positives must be supported by independent evidence of the relevant process or terrain property, not merely by a high ANALOG-X score.
3. Negatives should be deliberate hard negatives: plausible lookalikes that fail the predeclared criterion, with the reason documented in the evidence reference or accompanying review record.
4. Keep every neighbouring or geologically related candidate in the same spatial group.
5. Do not use the same DEM-derived descriptors both to assign labels and to claim independent validation of those descriptors.
6. Have a qualified reviewer record the evidence scope, date and limitations. One label validates only the stated target criterion, not all mission processes.

## Blind reviewer packet and sampling design

The repository now generates `data/validation/independent_analog_review_packet.json` from the released schema 1.1.0 shortlist. It samples eight candidates in each of six predeclared rank strata per target (48 Moon + 48 Mars), preferring distinct 10-degree geographic cells within each stratum. The packet exposes a keyed opaque case code, target, a rounded approximate area locator (0.1-degree precision), window size and required review fields. The exact candidate centre is held only in the private case key. Case codes use a private salt and cannot be dictionary-matched against public candidate IDs. Candidate IDs, scores, ranks and terrain metrics are not exposed.

The matching private case key contains candidate IDs, ranks, scores and geographic-group IDs. Generate it locally and keep it outside the repository:

```bash
python scripts/build_independent_review_pack.py --key-output "$HOME/analogx-private/independent-review-case-key.json"
```

Never send the key to reviewers or commit it. The key file contains the private salt and exact candidate mapping; protect it like credentials and keep a secure owner backup. The automated ranking-release workflow intentionally does not regenerate the review packet because an ephemeral CI runner cannot safely retain the owner's private case key. Regenerate the packet locally when the candidate release changes, using the same existing key-output file to preserve the salt. Reviewers should complete the `independent_review` block in the packet and return the packet only. Import binary labels locally:

```bash
python scripts/import_independent_review_labels.py --key "$HOME/analogx-private/independent-review-case-key.json" --dry-run
python scripts/import_independent_review_labels.py --key "$HOME/analogx-private/independent-review-case-key.json"
python scripts/validate_analog_labels.py
python scripts/build_quantitative_validation.py
```

The importer requires the exact `terrain_morphology_transfer_v1` criterion, an independent-of-score attestation, reviewer qualification/affiliation, an explicit ISO 8601 UTC date-time ending in `Z` or `+00:00`, one or more non-empty string evidence references, confidence and rationale. It ignores only inconclusive/insufficient-evidence responses for AUC; unknown label values are rejected. Boolean confidence values, date-only values, timezone-naive values and non-UTC offsets are rejected. Duplicate candidate labels are rejected pending explicit adjudication. The private key must match the exact review packet revision.

The 10-degree grid cell is a predeclared geographic blocking proxy, not a guaranteed geological boundary. A qualified reviewer should merge cells belonging to one geologic province before evaluation when necessary. Do not split neighbouring or genetically related terrain across train/test.

## Evaluation

Run:

```bash
python scripts/validate_analog_labels.py
python scripts/build_quantitative_validation.py
```

The evaluator uses a deterministic 20% spatial-group holdout; all records from a group remain together. It reports ROC-AUC only if the held-out split contains at least **five distinct spatial groups**, with positive labels represented in at least **two held-out groups** and negative labels represented in at least **two held-out groups**. Having five groups across the full dataset is not sufficient if only one or two groups land in the held-out partition. A deterministic 2,000-resample group bootstrap estimates a 95% interval only when at least 200 valid group resamples can be produced. The output remains exploratory and must be interpreted with class balance, group independence, label scope and reviewer quality; it is not a universal accuracy estimate.

A ranking-ready global dataset (schema 1.1.0) is a prerequisite for a reproducible score evaluation, but ranking readiness is not model accuracy. If the label file is empty or the held-out classes are incomplete, the report must say that validation is awaiting labels.

## Current status

The first blind review packet is a sampling instrument only; no independent label records are currently supplied. ANALOG-X must not claim a validated AUC, accuracy, sensitivity, specificity or planetary analog success rate.
