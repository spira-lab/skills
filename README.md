# Spira Skills

This repository is a pure source repository for portable Spira skills.

It is designed to be consumed from GitHub by external installers and agent ecosystems such as:

- `npx skills add owner/repo`
- `npx skills add owner/repo --skill <slug>`
- Claude-style plugin or marketplace flows

This repo does not provide a local installer, local maintainer CLI, or CI workflow. It is intentionally just a source repository for skills.

## How This Repo Is Consumed

- Source of truth: this repository
- Distribution source: GitHub repository URL or `owner/repo`
- Installation target: decided by the external CLI or agent runtime
- Runtime configuration: `.env.example` documents optional HTTP execution context only

Typical consumer flows:

```bash
npx skills add owner/repo
npx skills add owner/repo --skill brand-space-research
```

The install destination is determined by the consuming tool, not by this repository.

## Repository Structure

```text
.
├── README.md
├── AGENTS.md
├── .env.example
├── .claude-plugin/
└── skills/
    ├── business/
    │   ├── brand-space-research/
    │   └── content-plan-from-trends/
    ├── dev/
    │   └── api-route-debugger/
```

## Included Skills

- `skills/business/brand-space-research`
- `skills/business/content-plan-from-trends`
- `skills/dev/api-route-debugger`

## Static Entry Files

- `AGENTS.md`
  - repo-level index and navigation entry for agent-facing consumers
- `.claude-plugin/`
  - Claude-style static metadata so the repository can participate in plugin-style discovery flows

## Environment Variables

Defined in [.env.example](.env.example):

- `SPIRA_BASE_URL`
- `SPIRA_AUTH_MODE`
- `SPIRA_COOKIE_HEADER`
- `SPIRA_BEARER_TOKEN`
- `SPIRA_TIMEOUT_SECONDS`
- `SPIRA_DEFAULT_PERSONA_ID`
- `SPIRA_DEFAULT_PLATFORM`
- `SPIRA_DEFAULT_WORKSPACE_ID`
- `SPIRA_DEFAULT_TIMEZONE`

These variables are optional runtime documentation for wrappers or tool layers that actually execute HTTP calls.

They do not become active merely because a skill is installed or copied by an external CLI.

## Skill Conventions

- every skill must contain `SKILL.md`
- frontmatter must include `name` and `description`
- no absolute paths
- no vendor-specific installation assumptions inside the skill body
- use `references/` for route lists and detailed operational notes
- prefer symbolic configuration such as `SPIRA_BASE_URL` over fixed hosts or ports
