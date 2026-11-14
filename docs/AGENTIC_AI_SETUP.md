# ANALOG-X Agent API — Free Cloudflare Workers AI setup

## What this deploys

A server-side Worker that runs the ANALOG-X Mission Director with an open-weight model, `@cf/openai/gpt-oss-20b`, hosted by Cloudflare Workers AI. The Worker calls allow-listed evidence tools for the candidate inventory, NASA POWER monthly climatology, Sentinel-2 spectral context and Earth/Moon/Mars terrain profiles. Four specialist evidence agents run first; the model then uses tool calling to adjudicate the evidence and produce a mission-specific decision brief.

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
6. Open that URL plus `/health` in a browser. It should return `ok: true`.
7. In ANALOG-X's Agent Bay, paste the Worker base URL (without `/analyze`) into **Agent endpoint**, choose **Connect & test**, and save it in that browser.

No Gemini/OpenAI API key is needed. The GitHub Actions secrets are used only to deploy the Worker; the Workers AI binding runs inference inside Cloudflare.

## Local fallback

The public site includes a deterministic, offline evidence mode. It reads the published JSON datasets directly and can compare evidence, campaign months and candidate completeness without any Worker, API key or LLM. The cloud agent adds natural-language synthesis and tool selection; it does not replace the measured-data layer.

## Limitations

- The 10,000-Neuron daily allocation is shared by the Cloudflare account and may not support unrestricted public traffic.
- Cloudflare's built-in rate limit is approximate and enforced per Cloudflare location, not a strict global quota.
- The Worker is a public research endpoint; CORS is not authentication. Do not put private or sensitive information in the prompt.
- Candidate records are a curated screening seed set, not an exhaustive global search.
- The two Chagai playa AOIs are historical leads. Modern remote-sensing screens and field validation are required before making geological or resource claims.
- A model-generated recommendation is not scientific evidence. Every factual claim must trace back to the deterministic specialist reports and linked datasets.
