---
name: "content-plan-from-trends"
description: "Use when you need to combine Brand Space, website intelligence, Trending Radar, and AI Chat into a content plan or multi-platform draft set."
---

# Content Plan From Trends

Use this skill to turn brand context and trend evidence into content plans, draft hooks, and platform variants.

## Workflow

1. Clarify the goal, audience, platform mix, and timeline.
2. Pull grounded brand context from Brand Space.
3. Add website intelligence if the site can strengthen brand or offer understanding.
4. Query Trending Radar for relevant topics, tags, platforms, or persona-aligned opportunities.
5. Reduce retrieved trends into a few usable content angles.
6. Use AI Chat or text endpoints to generate the plan, hooks, titles, tags, scripts, or rewrites.
7. Present recommendations before any high-impact action such as billing, generation, scheduling, or publishing.

## HTTP Capabilities

- Brand context
  - `GET /api/brand-space/toolkit/meta`
  - `GET /api/brand-space/toolkit/files`
  - `POST /api/brand-space/toolkit/search`
  - `GET /api/brand-space/toolkit/resources/[resourceId]`
- Website intelligence
  - `POST /api/internal/website-intelligence/jobs`
  - `GET /api/internal/website-intelligence/jobs/[id]`
- Trending Radar
  - `GET /api/sci/search`
  - `GET /api/sci/content/[id]`
- Generation
  - `POST /api/ai-chat/stream`
  - `POST /api/ai-chat/upload`
  - `POST /api/ai-text/title`
  - `POST /api/ai-text/tags`
  - `POST /api/ai-text/script`
  - `POST /api/ai-text/rewrite`
- Pricing and generation checks
  - `GET /api/pricing`
  - `POST /api/pricing/estimate`

## Guardrails

- Trends are signals, not guarantees.
- Keep source awareness between brand evidence, website evidence, trend evidence, and generated suggestions.
- Estimate cost before expensive media generation.
- Do not claim that scheduling or publishing has happened unless it actually has.

## References

- `references/content-planning-playbook.md`
