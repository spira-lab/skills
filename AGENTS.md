# Spira Skills Index

This repository provides portable Spira skills for external agent installers and agent runtimes.

## Available Skills

- `brand-space-research`
  - Category: `business`
  - Path: `skills/business/brand-space-research`
  - Purpose: grounded Brand Space retrieval, evidence review, and brand-context synthesis
- `content-plan-from-trends`
  - Category: `business`
  - Path: `skills/business/content-plan-from-trends`
  - Purpose: combine Brand Space, website intelligence, Trending Radar, and AI text generation into content planning
- `api-route-debugger`
  - Category: `dev`
  - Path: `skills/dev/api-route-debugger`
  - Purpose: inspect authenticated Spira API routes and debug request or response contract issues

## Notes

- `skills/` is the canonical content layer.
- Each installable skill is discovered from its `SKILL.md`.
- This repo does not decide install destinations.
- External installers such as `skills` CLI or Claude-style plugin tooling decide where downloaded skills are placed.
