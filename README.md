# Spira Skills

This repository stores portable Spira skills for business workflows and developer workflows.

The design goal is:

- human-readable skills
- HTTP-first operational guidance
- compatible with mainstream agents
- easy to mount into a real project

## What Is In This Repo

- `skills/`: the reusable skill library
- `spira-skills.sh`: a lightweight shell CLI for listing, validating, printing env vars, and creating project symlinks
- `.env.example`: shared environment variable baseline for HTTP-oriented skills

## Repository Structure

```text
.
├── README.md
├── .env.example
├── spira-skills.sh
├── skills/
│   ├── _templates/
│   │   └── skill-starter/
│   ├── business/
│   │   ├── brand-space-research/
│   │   └── content-plan-from-trends/
│   └── dev/
│       ├── capability-audit/
│       └── api-route-debugger/
```

## Quick Start

List skills:

```bash
./spira-skills.sh list
```

Print the recommended environment variables:

```bash
./spira-skills.sh env --format dotenv
```

Validate the repository:

```bash
./spira-skills.sh validate
```

Link the whole `skills/` directory into a mainstream agent directory:

```bash
./spira-skills.sh link \
  --project /path/to/your-project \
  --dest .agent/skills
```

Link into a Claude-style skill directory:

```bash
./spira-skills.sh link \
  --project /path/to/your-project \
  --dest .claude/skills
```

## CLI Commands

### `list`

Show all available skills with their descriptions.

```bash
./spira-skills.sh list
```

### `show`

Resolve a skill path or inspect metadata.

```bash
./spira-skills.sh show capability-audit
./spira-skills.sh show dev/capability-audit --format json
```

### `env`

Print the shared environment variable baseline.

```bash
./spira-skills.sh env --format dotenv
./spira-skills.sh env --format shell
```

### `validate`

Validate:

- every skill has `SKILL.md`
- frontmatter includes `name` and `description`
- local markdown links are not broken

```bash
./spira-skills.sh validate
```

### `link`

Create a symlink from this repository into a concrete project.

```bash
./spira-skills.sh link \
  --project /path/to/project \
  --dest .agent/skills
```

Useful flags:

- `--source`: repo-relative path, defaults to `skills`
- `--force`: replace an existing symlink, file, or empty directory

## Project Symlink Strategy

This repo is meant to stay as the source of truth. Consumer projects should usually mount it by symlink into the agent's skill-discovery directory rather than copying files.

Recommended target locations inside a project:

- `.agent/skills`
- `.claude/skills`
- `.cursor/skills`

Recommended patterns:

1. Link the full library when the project should access all shared skills.
2. Link a single skill when the project only needs a narrow workflow.
3. Keep project-specific overrides in the project itself, not back in the shared library unless they should be reused globally.

## Environment Variables

These skills are HTTP-oriented, so a small shared environment baseline helps a lot.

Defined in [.env.example](.env.example):

- `SPIRA_BASE_URL`: base URL of the Spira host or API
- `SPIRA_AUTH_MODE`: `cookie` or `bearer`
- `SPIRA_COOKIE_HEADER`: raw `Cookie` header value when cookie auth is used
- `SPIRA_BEARER_TOKEN`: bearer token when token auth is used
- `SPIRA_TIMEOUT_SECONDS`: default timeout for HTTP requests
- `SPIRA_DEFAULT_PERSONA_ID`: optional default persona for trend-related workflows
- `SPIRA_DEFAULT_PLATFORM`: optional default platform
- `SPIRA_DEFAULT_WORKSPACE_ID`: optional workspace context
- `SPIRA_DEFAULT_TIMEZONE`: optional timezone hint

Suggested local setup:

```bash
cp .env.example .env
source .env
```

Then fill in the values that match your environment.

## Skill Conventions

- Skill directory names use English `kebab-case`.
- Every skill must contain a `SKILL.md` with YAML frontmatter.
- Frontmatter must include `name` and `description`.
- Keep `SKILL.md` concise and procedural.
- Put detailed API notes, route inventories, payload examples, and long operating notes in `references/`.
- Keep each skill self-contained and avoid cross-skill dependencies whenever possible.
- Optional `examples/` or `assets/` folders are allowed when they add real value.

## Recommended Skill Shape

```text
skill-name/
├── SKILL.md
├── references/
├── examples/
└── assets/
```

## Included Skills

- `skills/business/brand-space-research`
- `skills/business/content-plan-from-trends`
- `skills/dev/capability-audit`
- `skills/dev/api-route-debugger`

## Starter Template

Use [skills/_templates/skill-starter/SKILL.md](skills/_templates/skill-starter/SKILL.md) as the base pattern for new skills.

The template is designed for:

- concise metadata
- HTTP-first instructions
- environment-aware assumptions
- references for route details and examples

## Authoring Guidance

When creating a new skill:

1. Start from the template.
2. Keep the description specific enough that a mainstream agent can recognize when to use it.
3. Put the primary workflow in `SKILL.md`.
4. Put route catalogs, payload examples, and large operational notes in `references/`.
5. Call out required auth, base URL, and confirmation boundaries clearly.
