# Spira Lab skills

Agent skills for making and editing short videos with [Spira](https://github.com/spira-lab).

[![skills.sh](https://skills.sh/b/spira-lab/test-skills)](https://skills.sh/spira-lab/test-skills)

## Install

```bash
npx skills add spira-lab/test-skills
```

Install one skill for Claude Code only:

```bash
npx skills add spira-lab/test-skills --skill spira-maxima -a claude-code
```

## Skills

| Skill | What it does |
| --- | --- |
| `spira-maxima` | Turns a script, brief or idea into a finished 9:16 short video. Generation runs through the `spira` CLI; stage, audit and render run locally in Chrome. |
| `spira-vibe-edit` | Opens the Spira local editor on a spira-maxima video, applies each browser comment to the video's editable and re-renders locally. Needs `spira-maxima`. |

## Requirements

- `npm install -g @spira-lab/cli`, then `spira auth login`
- `ffmpeg` (with libvpx), `node`, `python3` with `openai-whisper`, and a local Chrome/Chromium
- `yt-dlp` only when you start from a reference video URL
