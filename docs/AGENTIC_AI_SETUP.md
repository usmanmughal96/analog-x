# ANALOG-X Agent API — Free Cloudflare Workers AI setup

## What this deploys

A server-side Worker that runs the ANALOG-X Mission Director with an open-weight model, `@cf/openai/gpt-oss-20b`, hosted by Cloudflare Workers AI. The Worker exposes two separate paths: `POST /scout` performs a no-LLM global coordinate scan using the public NASA POWER climatology endpoint plus Microsoft Planetary Computer STAC searches for Sentinel-2 L2A and Copernicus DEM GLO-30; `POST /analyze` runs the tool-using Mission Director over specialist evidence and can repeat a supplied coordinate scan. The AI tool list includes candidate inventory, terrain comparison, campaign windows, Sentinel-2 context and coordinate scouting. Four specialist evidence agents run first; the model then uses tool calling to adjudicate the evidence and produce a mission-specific decision brief.

The browser never receives an AI provider secret. Requests are restricted by CORS to the published ANALOG-X site, limited by a per-IP rate-limit binding, and constrained to a small JSON payload. The Worker does not store chat history or write prompt text to project files.

## Cost and provider

Cloudflare Workers AI currently includes 10,000 Neurons per day at no charge on the Workers Free plan. The free allocation resets daily at 00:00 UTC; once exhausted, requests on the Workers Free plan fail until reset. A paid plan can bill above the free allocation, so **use the Workers Free plan and do not upgrade or enable paid usage** if you need a hard no-charge boundary. The model is open-weight and supports function calling. Check the account's model availability and current quota before use.

Official references:
- Workers AI pricing: https://developers.cloudflare.com/workers-ai/platform/pricing/
- gpt-oss-20b model/function calling: https://developers.cloudflare.com/workers-ai/models/gpt-oss-20b/
- Worker rate-limiting binding: https://developers.cloudflare.com/workers/runtime-apis/bindings/rate-limit/
- Workers AI data usage: https://developers.cloudflare.com/workers-ai/platform/data-usage/

Cloudflare states that standard Workers AI inference uses zero data retention and does not use customer content to train models. Operational metadata may still be retained. Review the current terms before sending sensitive material.

## One-time deployment

1. Create or sign in to a Cloudflare account and enable Workers AI on the Free plan.
2. In Cloudflare, create an API token with permission to edit Workers scripts and access Workers AI. Copy the token once.
3. In the GitHub repository, open **Settings → Secrets and variables → Actions**. Add:
   - `CLOUDFLARE_API_TOKEN` (secret)
   - `CLOUDFLARE_ACCOUNT_ID` (secret; the account identifier from Cloudflare)
4. Open **Actions → Deploy ANALOG-X Agent API (Cloudflare Workers AI) → Run workflow**.
5. Open the successful workflow log. Wrangler prints the deployed `workers.dev` URL, typically `https://analog-x-agent.<your-subdomain>.workers.dev`.
6. Open that URL plus `/health` in a browser. It should return `ok: true` and show `scout_enabled: true`. If the AI binding is configured, `ai_enabled` is true; it is safe for the endpoint to return `ai_enabled: false` while the live `/scout` service is still available. In that case, the UI enables Coordinate Scout but keeps cloud Mission Director disabled.
7. In ANALOG-X's Agent Bay, paste the Worker base URL (without `/analyze`) into **Agent endpoint**, choose **Connect & test**, and save it in that browser.

No Gemini/OpenAI API key is needed. The GitHub Actions secrets are used only to deploy the Worker; the Workers AI binding runs inference inside Cloudflare.

## Local fallback

The public site includes a deterministic, offline evidence mode. It reads the published JSON datasets directly and can compare evidence, campaign months, terrain profiles and candidate completeness without any Worker, API key or LLM. Global Coordinate Scout requires the deployed Worker proxy, but does not require the AI binding or model inference; it can be used without spending Workers AI Neurons. The cloud agent adds natural-language synthesis and tool selection; it does not replace the measured-data layer.

## Limitations

- The 10,000-Neuron daily allocation is shared by the Cloudflare account and may not support unrestricted public traffic. Current model pricing lists gpt-oss-20b at 18,182 input Neurons and 27,273 output Neurons per million tokens; the free 10,000-Neuron daily allowance is account-wide and requests fail when exhausted rather than automatically becoming paid usage on the Workers Free plan.
- Cloudflare's built-in rate limit is approximate and enforced per Cloudflare location, not a strict global quota.
- The Worker is a public research endpoint; CORS is not authentication. Do not put private or sensitive information in the prompt. Its simple rate limit is approximate and per Cloudflare location; it is not a strict global abuse-control system.
- Candidate records are a curated screening seed set, not an exhaustive global search.
- The two Chagai playa AOIs are historical leads. Modern remote-sensing screens and field validation are required before making geological or resource claims.
- A model-generated recommendation is not scientific evidence. Every factual claim must trace back to the deterministic specialist reports and linked datasets.


## Decision logic and target handling

The deterministic specialist reports run before the Mission Director. The candidate decision rule is documented in [DECISION_ENGINE.md](DECISION_ENGINE.md). The model is instructed to treat the reports and allow-listed tool results as the evidence base, distinguish measurement from inference, and never invent mineralogy, brine, ice access, dust flux, safety or a similarity percentage.

When **Moon + Mars** is selected, the terrain tool returns two independent comparisons (Shackleton Rim and Nili Patera); it must not blend them into a single score. Tool calling is limited to one explicit retrieval round (up to three allow-listed calls) followed by a synthesis pass. The Worker returns the tool trace and model usage metadata with the brief.


## gpt-oss tool-call reliability

The Mission Director handles both Workers AI's structured tool-call response and the documented gpt-oss edge case where a function call may be returned as JSON text with an empty structured tool-call array. Text recovery is deliberately narrow: it accepts JSON objects/arrays only, rejects any name outside the five-tool allow-list, and passes the recovered arguments through the same server-side tool executor. This is not an unrestricted code-execution path.
