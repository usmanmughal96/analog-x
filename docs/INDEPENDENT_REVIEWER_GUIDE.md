# ANALOG-X — Independent Reviewer Guide

## Invitation and scope

ANALOG-X is seeking independent, evidence-based assessments of a limited terrain-morphology screening criterion. This is an invitation template, not evidence that any expert has been contacted or agreed to review.

Reviewers should have relevant experience in planetary geology, geomorphology, remote sensing, field geology, terrain analysis or planetary surface operations. Please disclose your qualifications, affiliation, potential conflicts and any prior involvement with ANALOG-X.

The first review packet contains 96 blinded cases: 48 Moon-related and 48 Mars-related terrain-morphology cases. Candidate identifiers, ANALOG-X ranks, terrain scores and shortlist position are withheld in the reviewer interface. Public case codes are keyed with an owner-private salt, and area coordinates are rounded to the nearest 0.1 degree to reduce reverse matching against the public shortlist. The location is approximate, not the exact 5.55 km window centre.

## What the reviewer is being asked

For each supplied candidate window:

> Does independent evidence support a terrain-morphology match relevant to the stated planetary reference and its target process, at the stated spatial scale?

This criterion is deliberately narrow. It is not a request to decide whether a place is a complete Moon/Mars analog or whether a landing site, rover route, resource or base is safe or feasible.

### Permitted responses

- **Positive:** independent evidence supports the stated terrain-morphology criterion.
- **Negative:** the candidate is a plausible lookalike but independent evidence shows it fails the criterion.
- **Inconclusive:** evidence is mixed, not decisive or not sufficient for a binary judgment.
- **Insufficient evidence:** available public sources do not support a defensible judgment.

Do not force a positive or negative label merely to complete the form.

## How to use the reviewer desk

1. Open [independent-review.html](../independent-review.html).
2. Enter your name, affiliation, relevant qualification and review date.
3. Confirm that you are assessing the cases independently of ANALOG-X scores and ranks.
4. Review the stated reference target, approximate area locator and spatial support. Use independent sources, not an ANALOG-X rank or score. The area locator is deliberately coarse; when the available evidence cannot isolate the stated candidate area well enough, use “insufficient evidence” rather than guessing.
5. Select a response, cite evidence references and explain the task-specific rationale and limitations.
6. Save each case. The page stores the draft only in the current browser's local storage; it does not transmit the response.
7. Export the response JSON and return it through an agreed, approved private channel.

The interface can import a previously exported response JSON into the same browser. Clearing local drafts permanently deletes that browser's saved response.

## Evidence and provenance requirements

For positive and negative labels, cite at least one independent reference: a DOI, official dataset/product ID, published map, stable URL or documented first-hand expertise. Explain what the cited source establishes and what it does not establish.

Each binary label requires:
- reviewer name, affiliation and relevant qualification;
- review date in UTC;
- a target-specific rationale and criterion version;
- confidence from 1 to 5;
- an explicit attestation of independence from ANALOG-X scores;
- one or more independent evidence references;
- limitations or reasons the evidence may be incomplete.

Inconclusive and insufficient-evidence responses remain useful and should include a rationale. The importer does not convert these responses into binary labels or AUC observations.

## Spatial and methodological safeguards

- Do not ask for or use candidate IDs, ranks or scores.
- Do not copy an ANALOG-X interpretation into the rationale as independent evidence.
- Do not label using the same score or DEM-derived feature being evaluated as if it were an independent ground truth.
- Consider whether adjacent cases belong to the same geological province. The project's 10-degree geographic grouping is a predeclared proxy, not a guaranteed geological boundary.
- One case assesses only the specified terrain criterion. It does not prove mineralogy, ice, volatiles, biological potential, process equivalence, trafficability or safety.
- Disclose uncertainties, incomplete coverage and source limitations.

## How responses are processed

The project owner must use the exact matching packet version and the private case key produced by scripts/build_independent_review_pack.py. The private key maps blind case codes back to candidate IDs, scores and spatial groups. It must never be given to reviewers or committed to the public repository.

The repository owner then uses the following commands from the repository root:

    python scripts/import_independent_review_labels.py --key "$HOME/analogx-private/independent-review-case-key.json" --dry-run
    python scripts/import_independent_review_labels.py --key "$HOME/analogx-private/independent-review-case-key.json"
    python scripts/validate_analog_labels.py
    python scripts/build_quantitative_validation.py

The analysis uses spatial groups rather than randomly splitting neighboring windows. ROC-AUC is withheld unless the held-out groups contain both positive and negative labels and meet the validator's minimum group requirements. Any resulting metric is exploratory and specific to the declared criterion and label set—not universal model accuracy.

## Reviewer invitation text

**Subject:** Independent blind review request — ANALOG-X planetary terrain-morphology cases

ANALOG-X is an independent research prototype exploring how terrestrial terrain evidence can support mission-relevant analog research for the Moon and Mars. We have prepared a 96-case blinded review packet (48 Moon, 48 Mars) to assess one narrow criterion: terrain-morphology relevance at a stated spatial support.

We are seeking a qualified reviewer with experience in planetary geology, geomorphology, remote sensing, terrain analysis or planetary surface operations. The review interface withholds our candidate IDs, ranks and scores. We ask reviewers to provide evidence-backed positive, negative, inconclusive or insufficient-evidence judgments, along with a short rationale, confidence and relevant source references.

This is not a request to endorse ANALOG-X, validate an entire planetary analog, or assess landing/rover safety. Reviewers should disclose their qualification, affiliation and conflicts. Responses can be returned as a JSON export through an agreed private channel. The protocol and data limitations are available in the repository.

Would you be willing to discuss whether this review falls within your expertise and, if appropriate, review a subset of the cases?
