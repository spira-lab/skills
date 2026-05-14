---
name: social-publish-http
description: Use when the user wants to publish an existing TikTok, Twitter/X, or LinkedIn submission. This skill frames that the workflow has moved into the publish stage, checks the user's connected accounts, asks the user to choose an account when multiple are available, and publishes the submission through the HTTP API.
---

# Social Submission Publish

Use this skill when the user wants to publish an existing social submission for:

- `tiktok`
- `twitter`
- `linkedin`

This skill is API-driven and should use the authenticated web session.

This skill is responsible for:

- framing that the current stage is publishing an existing submission
- checking available connected accounts
- asking the user to choose an account when multiple accounts exist
- guiding the user to bind an account when none exists
- publishing an existing submission through HTTP

This skill does not create the submission.
Submission creation should be handled by a separate skill.

## Stage framing

At the start of the publish turn, explicitly say:

- which skill is being used
- that the current stage is publishing an existing submission
- which submission will be published if that is already known

Suggested wording:

```text
Using skill: social-publish-http
Current stage: publish the existing submission.
I will publish submission <submissionId> if everything is ready.
```

Do not skip this framing.

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

### 2. Publish submission

```http
POST /api/social-submissions/<submissionId>/publish
Content-Type: application/json
```

Publishing always requires:

```json
{
  "confirm": true
}
```

## Submission readiness checks

Before publishing, make sure:

- a `submissionId` exists
- the platform is known
- the connected account situation is valid
- the content being published is clear enough to describe back to the user

If the submission came from the immediately previous `social-submission-create` step, reuse that `submissionId` and content unless the user asked to change something.

If the user says only "发布" right after a create step, assume they mean:

- publish the most recently created submission from the current flow
- use the exact finalized content that was just created

Do not ask redundant questions in that case.

## Account selection rules

If no account exists for the chosen platform, tell the user to bind one in:

```text
/dashboard/accounts
```

Suggested wording:

```text
No <platform> account is connected for the current user. Please bind an account in /dashboard/accounts before publishing.
```

If exactly one account exists:

1. use it
2. tell the user which account is being used
3. do not ask an unnecessary account-selection question

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
I found multiple <platform> accounts for the current user. Please choose one account to publish with:
1. <displayName or username> (<id>)
2. <displayName or username> (<id>)
3. <displayName or username> (<id>)
```

## Publish rules

This skill must publish through the submission flow.

It expects an existing `submissionId`.

Before calling the publish API, briefly restate:

- platform
- selected account
- the content that will be published
- the `submissionId`

If the user previously gave explicit approval to publish, proceed with `confirm: true`.

If the request returns:

```json
{
  "error": "Publishing requires explicit confirmation.",
  "confirmationRequired": true
}
```

resend only after explicit user approval.

## Platform-specific request body additions

### TikTok

```json
{
  "confirm": true,
  "title": "Title",
  "description": "Caption",
  "mediaUrls": ["https://..."],
  "privacyLevel": "PUBLIC_TO_EVERYONE",
  "allowComment": true,
  "allowDuet": true,
  "allowStitch": true,
  "brandContentToggle": false,
  "brandOrganicToggle": true,
  "autoAddMusic": false,
  "isAigc": false
}
```

### Twitter/X

```json
{
  "confirm": true,
  "text": "Hello world",
  "mediaUrls": ["https://..."]
}
```

### LinkedIn

```json
{
  "confirm": true,
  "text": "Hello LinkedIn",
  "linkUrl": "https://example.com"
}
```

## Output expectations

When using this skill, return:

1. which skill is being used
2. which stage is being handled now
3. which platform was selected
4. which content was published
5. which account was selected
6. the API route used
7. the `submissionId` that was published
8. the publish result

## Example

### Publish one Twitter submission

1. say that `social-publish-http` is being used and that the current stage is publishing an existing submission
2. if this follows a just-created draft, reuse that `submissionId` and content
3. `GET /api/accounts/context`
4. read `linkedAccounts.twitter`
5. if multiple accounts exist, ask the user to choose
6. if exactly one account exists, say it will be used
7. restate the text and `submissionId`
8. `POST /api/social-submissions/<submissionId>/publish`
9. body:

```json
{
  "confirm": true,
  "text": "Launch update",
  "mediaUrls": ["https://cdn.example.com/post-image.png"]
}
```

10. return the selected account, `submissionId`, and publish result
