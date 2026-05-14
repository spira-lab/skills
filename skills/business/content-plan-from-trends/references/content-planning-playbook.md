# Content Planning Playbook

## Suggested Sequence

1. Gather brand tone, offer, audience, and no-go areas.
2. Retrieve 3 to 5 trend candidates from `GET /api/sci/search`.
3. Read details for the strongest candidates with `GET /api/sci/content/[id]`.
4. Reduce them into 1 to 3 opportunity angles.
5. Draft:
   - content themes
   - platform hooks
   - CTA ideas
   - optional titles, tags, and scripts

## Useful Query Dimensions

- `personaId`
- keywords
- tags
- platform
- sorting
- pagination

## High-Impact Actions

Require explicit confirmation before:

- `POST /api/ai/jobs`
- `DELETE /api/ai/jobs/[id]`
- `POST /api/social-submissions`
- `POST /api/social-submissions/[submissionId]/publish`
- `POST /api/schedules`
- billing or subscription routes
