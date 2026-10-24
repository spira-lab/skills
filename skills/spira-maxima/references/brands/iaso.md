# IASO

Preferences the user set for every IASO project, and for no other brand.
Read this file when the brand is IASO; they apply without being asked
again.

- Never use a talking head.
- Produce the VO with this job, the text being the approved script
  (write the payload to `jobs/vo.json`, create it with `spira ai jobs create`
  as `elevenlabs-text-to-speech`, then wait on it and download the result
  to `<materials>/<name>/vo.mp3`, toolkit section 1):

  ```json
  {"text":"…","voiceId":"cgSgspJ2msm6clMCkdW9","providerModelId":"eleven_v3"}
  ```
- Transitions are always effortful and purposeful, and elements enter
  and exit dynamically. No element simply appears or simply disappears.
- Do not add the IASO logo or the word IASO as text on screen. Avoid
  redundancy between caption subtitles and on-screen text: IF the
  on-screen text already covers the script word per word, use no
  caption subtitle.
- WHEN generating background music, the tone is scientific, not sad.
- WHEN asked to translate a video into another language, translate the
  script, generate a new VO from the translated script with the IASO VO
  job, apply it to the video, and adjust the timing of every element to
  the new VO. Captions and any on-screen text that carries the script
  follow the translated script. Save it as a new editable, with its own
  materials and render, named with the language as a prefix
  on the title and the same video number as the original:
  `NN-<lang>-name-MM-DD`, so `03-iaso-09-21` in Spanish becomes
  `03-es-iaso-09-21`. The number is kept, not incremented; the language
  is what tells the two apart.
