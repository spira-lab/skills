# Brand Space Workflow

## Recommended Retrieval Order

1. `GET /api/brand-space/toolkit/meta`
2. `GET /api/brand-space/toolkit/files`
3. `POST /api/brand-space/toolkit/search`
4. `GET /api/brand-space/toolkit/resources/[resourceId]`
5. `GET /api/brand-space/toolkit/gaps` when the task needs completeness checking

## When To Use Each Route

- `meta`
  - Quick understanding of the available knowledge surface
- `files`
  - File-oriented inventory browsing
- `search`
  - Task-driven narrowing by keywords or topic
- `resources/[resourceId]`
  - Full content retrieval for citation, extraction, or summarization
- `gaps`
  - Detect missing assets or incomplete brand memory

## Related Write Routes

Use only when the task explicitly requires them:

- `POST /api/brand-space/uploads`
- `PUT /api/brand-space/uploads/[uploadId]/parts/[partNumber]`
- `POST /api/brand-space/uploads/[uploadId]/complete`
- `DELETE /api/brand-space/uploads/[uploadId]`
- `POST /api/brand-space/folders`
- `PATCH /api/brand-space/folders/[folderId]`
- `DELETE /api/brand-space/folders/[folderId]`
- `DELETE /api/brand-space/resources/[resourceId]`

## Output Pattern

- List the materials reviewed
- Separate confirmed facts from open questions
- Call out missing evidence explicitly
