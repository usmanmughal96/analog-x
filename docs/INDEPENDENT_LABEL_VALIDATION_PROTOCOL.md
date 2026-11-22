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
- `reviewer` and `review_date_utc`.
- `core_terrain_index`: copied from the exact candidate release being evaluated.

## Labeling rules

1. Define the target-specific physical/process question and positive/negative criteria before inspecting candidate scores.
2. Positives must be supported by independent evidence of the relevant process or terrain property, not merely by a high ANALOG-X score.
3. Negatives should be deliberate hard negatives: plausible lookalikes that fail the predeclared criterion, with the reason documented in the evidence reference or accompanying review record.
4. Keep every neighbouring or geologically related candidate in the same spatial group.
5. Do not use the same DEM-derived descriptors both to assign labels and to claim independent validation of those descriptors.
6. Have a qualified reviewer record the evidence scope, date and limitations. One label validates only the stated target criterion, not all mission processes.

## Evaluation

Run:

```bash
python scripts/validate_analog_labels.py
python scripts/build_quantitative_validation.py
```

The evaluator uses a deterministic 20% spatial-group holdout; all records from a group remain together. It reports ROC-AUC only if the held-out split contains both positive and negative examples and at least five groups exist. This first implementation does not report confidence intervals. Before any performance claim, add a predeclared group bootstrap, inspect class balance and group independence, and seek external expert review.

A ranking-ready global dataset (schema 1.1.0) is a prerequisite for a reproducible score evaluation, but ranking readiness is not model accuracy. If the label file is empty or the held-out classes are incomplete, the report must say that validation is awaiting labels.

## Current status

No independent label records are currently supplied. ANALOG-X must not claim a validated AUC, accuracy, sensitivity, specificity or planetary analog success rate.
