---
name: "brand-space-research"
description: "Use when you need to inspect Brand Space metadata, files, search results, and resource content to support grounded brand research or content generation."
---

# Brand Space Research

Use this skill for Brand Space retrieval, evidence review, and brand-context synthesis. Prefer confirmed source material over assumption.

## Workflow

1. Start with metadata or file listing to understand the available knowledge surface.
2. Search Brand Space with task-specific terms before opening full resources.
3. Read only the resources needed for the current task.
4. Separate confirmed brand facts, reusable language, and open questions.
5. Keep source awareness in the final answer so it is clear what came from Brand Space versus user input or synthesis.

## HTTP Capabilities

- `GET /api/brand-space/toolkit/meta`
  - Use to understand overall Brand Space coverage and top-level context.
- `GET /api/brand-space/toolkit/files`
  - Use to inspect available files before deeper retrieval.
- `POST /api/brand-space/toolkit/search`
  - Use to narrow the candidate set by keywords or task intent.
- `GET /api/brand-space/toolkit/resources/[resourceId]`
  - Use when you need the content of a specific resource.
- `GET /api/brand-space/toolkit/gaps`
  - Use when the task needs missing-material detection or a follow-up list.

## Guardrails

- Do not present Brand Space material as absolute truth if it may be outdated, partial, or contradictory.
- Distinguish user-provided facts from Brand Space evidence.
- Prefer retrieval before summarization.
- Explain impact before upload, delete, or folder-management actions.

## References

- `references/brand-space-workflow.md`
