# Super Intelligence / AI-use Disclosure

The project team used ChatGPT as an AI-assisted tool during early brainstorming, concept refinement, code assistance, drafting, documentation and preparation of presentation materials. Early concept development did include AI-assisted brainstorming; this is disclosed transparently and is not represented as entirely unaided ideation.

The implementation, data selections, index formulas, candidate definitions and scientific interpretation must be independently reviewed and understood by the registered participant. AI output is not treated as scientific evidence. NASA POWER outputs are fetched from the official API and processed using the documented formulas; numerical claims should be reproducible from source requests and independently checked.

The team reports that its Local Lead was informed and approved proceeding. This does not replace any additional organizer interpretation of the SI rules. Acknowledge AI-assisted/generated elements as required by the official challenge guide.


## Agentic inference layer (added 14 November 2026)

The portal includes a deterministic offline evidence review that runs against published project JSON. It separates environment-tag retrieval, NASA POWER monthly climate, Sentinel-2 spectral-context screening, terrain descriptors and evidence completeness. These signals are not collapsed into an unvalidated universal similarity score.

An optional server-side Cloudflare Worker uses the open-weight `@cf/openai/gpt-oss-20b` model through Cloudflare Workers AI. Four deterministic specialist reports are assembled first; the Mission Director may call a restricted set of evidence tools for candidate inventory, terrain comparison, campaign windows and Sentinel-2 context. The LLM summarizes evidence but does not create measurements. The browser never receives the Cloudflare API token.

Cloud inference is **not active until the project owner** adds `CLOUDFLARE_API_TOKEN` and `CLOUDFLARE_ACCOUNT_ID` as GitHub Actions secrets and manually deploys the Worker. The Workers Free plan currently includes a limited daily inference allocation (10,000 Neurons/day); requests can be throttled or fail when the allocation is exhausted. This is not an unlimited service. AI assistance and the model deployment must be acknowledged as required by the challenge rules. A generated recommendation is not independent scientific validation, an official NASA result or a substitute for domain-expert review.


## Mission-specific decision support and learning UX (updated 14 November 2026)

The Agent Bay's deterministic offline engine now inspects the full ten-site curated catalog when no candidate filter is selected. It matches experiment objectives to each candidate's documented rehearsal tasks and environment tags, checks Moon/Mars eligibility, reports NASA POWER / Sentinel-2 / processed terrain / source-reference availability separately, and separates strict evidence-qualified leads from exploratory contextual references. Its ordering is a transparent triage heuristic and is not a similarity percentage or calibrated probability. The optional LLM receives these specialist results and may inspect allow-listed tools; it does not create measurements.

The mission simulator stores educational XP and quiz completion in the browser. These game points do not enter candidate triage, evidence completeness, planetary terrain comparisons or any scientific calculation.
