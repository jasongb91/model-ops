---
date: 2026-07-27
type: provider-review
---

# Provider Expansion & Architecture
 
Goal: Unified OpenRouter BYOK provider architecture to eliminate direct provider lock-in, bypass DeepInfra/direct provider latency issues, and optimize for cost and speed across Hermes and OpenCode.
 
## Active State (July 28, 2026)
- **Primary Provider:** `openrouter` (BYOK)
- **Hermes Profile Auth:** `OPENROUTER_API_KEY` configured across `ops` and `ops-light`. Direct keys (`OPENAI_API_KEY`, `ANTHROPIC_API_KEY`, `DEEPINFRA_API_KEY`, `GEMINI_API_KEY`) cleaned up.
- **OpenCode Provider Auth:** OpenRouter BYOK set in `~/.config/opencode/opencode.json`.
 
## Provider Benefits
1. **Multi-Provider Fallback:** Seamlessly failover between OpenAI, Anthropic, Google Gemini, and Qwen without managing 5 separate API keys.
2. **Bypasses Local MCP Tool Conflicts:** OpenCode MCP keys sanitized (`onepassword`, `google_calendar`, `aws_pricing`) to ensure Gemini function-calling works natively.
3. **No Credit Expiration:** OpenRouter BYOK routes billing directly to your provider enterprise accounts (e.g. Google Cloud Vertex AI / AI Studio, OpenAI, Anthropic) while keeping a $5 gateway buffer.

## Highest-priority additions

### 1. OpenRouter or Nous Portal with provider routing
Why:
- enables provider routing across multiple underlying providers
- can optimize for `latency`, `price`, or `throughput`
- supports provider allow/ignore/order controls
- gives a cleaner way to avoid over-committing to a single direct provider such as DeepInfra

Why this matters here:
- if DeepInfra is slow, routing through OpenRouter/Portal can try a faster provider path for the same model family
- this is the most practical way to evaluate many open-weight providers without wiring a dozen separate direct integrations

Suggested uses:
- interactive internal ops/CS drafts: route for `latency`
- large-volume internal extraction/classification: route for `price`
- maintain `require_parameters: true` to avoid silent parameter loss
- maintain `data_collection: deny` unless a specific exception is acceptable

### 2. Google Gemini direct
Why:
- likely strong candidate for fast, low-cost internal summarization/extraction
- useful additional non-DeepInfra lane
- can be wired through Gemini API / AI Studio or Vertex AI

Suggested use class:
- internal first-pass synthesis
- extraction and categorization
- bounded drafting

Caution:
- tool-calling compatibility through generic OpenAI-compatible paths needs its own validation
- do not promote into tool-heavy workflows until verified

### 3. Additional direct low-cost inference provider for open-weight models
Candidates supported by Hermes docs:
- `fireworks`
- `novita`
- `gmi`
- `arcee`
- `minimax`
- `zai`
- `alibaba`

Practical recommendation:
- do not add many at once
- pick **one** additional open-weight provider after OpenRouter/Portal and Gemini
- evaluate based on latency and stability for ops/CS benchmarks, not benchmark-leaderboard hype

## Lower-priority / optional additions

### xAI
Potential value:
- additional premium/fast reasoning lane
- different model family for comparison

Priority:
- below OpenRouter/Portal and Gemini for current ops/CS goals

### Local models
Current machine:
- Apple M5
- 16 GB RAM

Recommendation:
- acceptable for narrow local experiments
- not the first expansion priority for ops/CS production routing

## Config ideas to consider later

### Hermes
- add model aliases for reliability, fast-open-weight, and coder-open-weight lanes
- use provider routing only on OpenRouter/Portal-backed aliases
- revisit the fallback chain so it is not only reliability-first, but also intentionally cross-provider

### OpenCode
- prefer explicit per-run model selection while benchmarks are still in motion
- once a few winners emerge, wrap them behind stable task-family defaults in the dispatch helper / routing notes

## Recommended sequence
1. add OpenRouter or Nous Portal
2. add Gemini direct
3. run ops/CS benchmark suite on both
4. if DeepInfra still underperforms, add one more direct low-cost inference provider
5. only then reconsider local-first experiments
