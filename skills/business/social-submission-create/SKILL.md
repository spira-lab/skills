---
name: social-submission-create
description: Use when the user wants to create a TikTok, Twitter/X, or LinkedIn submission. This skill guides the user from rough intent to final publish-ready content, checks the user's connected accounts, asks the user to choose an account when multiple are available, and creates the submission through the HTTP API.
---

# Social Submission Creation

Use this skill when the user wants to create a social submission for:

- `tiktok`
- `twitter`
- `linkedin`

This skill is API-driven and should use the authenticated web session.

This skill is responsible for:

- framing that the current stage is content finalization plus submission creation
- guiding the user to shape the final post content
- identifying what is still missing before the post is ready
- checking available connected accounts
- asking the user to choose an account when multiple accounts exist
- guiding the user to bind an account when none exists
- creating the social submission through HTTP

This skill does not publish the submission.
Publishing should be handled by a separate skill.

## Stage framing

At the start of the turn, explicitly say:

- which skill is being used
- that the current goal is to finalize content and create a draft submission
- that publishing is a separate next step

Suggested wording:

```text
Using skill: social-submission-create
Current stage: finalize the post content, then create a submission draft.
Publishing is a separate next step after the content is ready.
```

Do not skip this framing.

## Core goal

This skill should help the user arrive at the final content that is intended to be published.

It should not just collect fields mechanically.
It should guide the user until the post is ready enough to become a submission.

Do not create an empty or obviously incomplete submission unless the user explicitly asks for a placeholder draft.

## Working style

Start from the user's intent, rough draft, notes, mood, or media.

Help the user clarify only what is needed:

- target platform
- main message
- final post copy
- media set
- CTA if relevant

Ask only for missing information that blocks a publish-ready draft.

If the user is vague, help shape the post first before creating the submission.
If the user gives feelings, fragments, or tone guidance instead of final copy, convert that into a candidate final post and confirm by proceeding with that content unless there is material ambiguity.

Prefer this rhythm:

1. infer what is already clear
2. identify the one or two missing pieces
3. help produce a final post draft
4. create the submission only after the content is ready

## When to ask follow-up questions

Ask follow-up questions only when the missing information changes the submission meaningfully.

Good reasons to ask:

- platform is not known and cannot be inferred
- the user has not provided enough information to write any final post copy
- the user referenced media or links that are required but not provided
- multiple accounts exist for the chosen platform

Do not ask avoidable questions when a reasonable assumption is safe.

Examples of safe assumptions:

- if the user says "发 twitter" or clearly discusses tweets, use `twitter`
- if the user provides only text and no media, assume `mediaUrls: []`
- if exactly one account exists for the platform, use it and say so
- if no CTA preference is provided, omit CTA rather than inventing one

## Platform guidance

### TikTok

Usually guide the user toward:

- a clear hook
- caption or description
- media assets
- post type such as video or photo

Typical submission mapping:

- `title`
- `description`
- `mediaUrls`
- `contentKind: "video"` or `contentKind: "photo"` or `contentKind: "mixed"`

### Twitter/X

Usually guide the user toward:

- one clear final text draft
- optional media

Typical submission mapping:

- `description`
- `mediaUrls`
- `contentKind: "text"` or `contentKind: "mixed"`

### LinkedIn

Usually guide the user toward:

- a polished final post draft
- optional supporting asset

Typical submission mapping:

- `description`
- `mediaUrls`
- `contentKind: "text"` or `contentKind: "mixed"`

## Required APIs

### 1. Check connected accounts

```http
GET /api/accounts/context
```

Use only:

- `linkedAccounts.tiktok`
- `linkedAccounts.twitter`
- `linkedAccounts.linkedin`

Ignore:

- `cloudDeviceAccounts`
- `operation_account`

### 2. Create submission

```http
POST /api/social-submissions
Content-Type: application/json
```

Request body:

```json
{
  "platform": "twitter",
  "accountId": "account_123",
  "accountSource": "oauth_account",
  "contentKind": "text",
  "source": { "sourceType": "manual" },
  "title": null,
  "description": "Launch update",
  "mediaUrls": [],
  "platformOptions": {}
}
```

## Account selection rules

If no account exists for the chosen platform, tell the user to bind one in:

```text
/dashboard/accounts
```

Suggested wording:

```text
No <platform> account is connected for the current user. Please bind an account in /dashboard/accounts before creating the submission.
```

If exactly one account exists:

1. use it automatically
2. tell the user which account will be used
3. do not ask an unnecessary account-selection question

Suggested wording:

```text
I found one <platform> account for the current user, so I will use <displayName or username> (<id>).
```

If multiple accounts exist:

1. do not auto-pick
2. show the available accounts
3. ask the user to choose one

For each account, show useful fields when available:

- `id`
- `displayName`
- `username`
- `avatarUrl`
- `profileUrl`

Suggested interaction:

```text
I found multiple <platform> accounts for the current user. Please choose one account for this submission:
1. <displayName or username> (<id>)
2. <displayName or username> (<id>)
3. <displayName or username> (<id>)
```

## Submission creation rules

Always create submissions with:

- `accountSource: "oauth_account"`

Supported `platform` values for this skill:

- `tiktok`
- `twitter`
- `linkedin`

Supported `contentKind` values:

- `video`
- `photo`
- `text`
- `mixed`

Use `source` like this unless another upstream flow requires something else:

```json
{
  "source": { "sourceType": "manual" }
}
```

## Content mapping guidance

Map content conservatively:

- TikTok usually uses `title`, `description`, and `mediaUrls`
- Twitter/X usually uses `description` as the main text and `mediaUrls` when needed
- LinkedIn usually uses `description` as the main post text and may later use `linkUrl` at publish time

Do not invent hidden field mappings.

Before creating the submission, make sure the content is already in its final intended form for publishing.

If the content is still obviously incomplete, keep guiding the user instead of creating the submission too early.

Signs the content is not ready yet:

- placeholders such as "xxx", "later", or "待补"
- unresolved references to missing links or missing files
- the user is still deciding among multiple substantially different directions
- there is no usable final post copy yet

## Handoff to publish

After creating the submission:

1. clearly say the draft has been created
2. show the final content that was used
3. include the `submissionId`
4. say that the next step is `social-publish-http` if the user wants to publish now

Suggested wording:

```text
The submission draft is ready. If you want, I can switch to social-publish-http next and publish this exact content.
```

## Output expectations

When using this skill, return:

1. which skill is being used
2. which stage is being handled now
3. which platform was selected
4. the final content that will be used
5. which account was selected
6. the API route used
7. the created submission result
8. the returned `submissionId`
9. the recommended next step

## Example

### Create one Twitter submission

1. say that `social-submission-create` is being used and that the current stage is content finalization plus draft creation
2. help the user finalize the Twitter post text and media
3. `GET /api/accounts/context`
4. read `linkedAccounts.twitter`
5. if multiple accounts exist, ask the user to choose
6. if exactly one account exists, say it will be used
7. `POST /api/social-submissions`
8. body:

```json
{
  "platform": "twitter",
  "accountId": "account_123",
  "accountSource": "oauth_account",
  "contentKind": "mixed",
  "source": { "sourceType": "manual" },
  "description": "Launch update",
  "mediaUrls": ["https://cdn.example.com/post-image.png"],
  "platformOptions": {}
}
```

9. return the final content, selected account, created result, and `submissionId`
