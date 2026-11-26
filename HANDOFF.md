# HANDOFF: token-saver system and Road to 30 HQ (as of Nov 26, 2026)

Read this whole file before doing anything. It is the complete state of the work from one long session, so a new session or system can continue without that chat. Personal details are kept out on purpose (this repo is public); they live in the HQ artifact itself.

---

## 1. Goal

Make every Claude session cheaper without lowering quality ("hardwire" the token-saving system), and keep the owner's personal operating system, **Road to 30 HQ** (a private claude.ai artifact), on the same system.

---

## 2. The token-saver plugin (the hardwire)

**Where it is:** `claude-mods/token-saver/` in this repo, on `main`. That folder is the single source of truth. Never rebuild it from a description; copy it.

| File | What it does |
|---|---|
| `.claude-plugin/plugin.json` | Manifest. `userConfig.cacheTtl` = `5m` or `1h` |
| `hooks/hooks.json` | Points at `./register.ts` |
| `hooks/register.ts` | All six mods (function hooks) |
| `hooks/token-saver.test.ts` | 3 tests (`claude plugin test`) |
| `agents/scout.md` | `token-saver:scout`, a read-only pre-reader on Haiku |
| `README.md` | Short user guide |

**The six mods:**
1. **Input Router.** Read, Bash, Grep and `mcp__*` results over ~24,000 characters (~6k tokens) in the main loop are condensed by Haiku against the user's current prompt. The model gets them as `[token-saver] ...` with instructions for getting exact text (re-read with offset/limit, narrow the command or query). Read with offset/limit and .ipynb/.pdf files are exempt. The prompt words "full output", "verbatim", "whole file", "entire file" and "no router" skip it for that turn.
2. **Effort Optimizer.** Sets effort per main turn (`turn.start` + `turn.step`): low for short or simple prompts, medium for ordinary ones, unchanged for hard ones (debug, design, strategy, review, optimize...) or "think hard"/"ultrathink". It only lowers effort, never raises it.
3. **Subagent Model Selector.** `agent.spawn`: only engine built-in agents with no model named. Explore and lookup-style tasks go to `haiku`, routine tasks to `sonnet`, hard tasks are left alone. Plan, fork and the scout are untouched.
4. **Cache Clock.** Status line `⛁ effort low · cache warm 3:12`. A toast warns 30 seconds before the cache goes cold.
5. **Handoff.** The `/handoff` command makes Claude write HANDOFF.md. A toast nudge appears at 60% context.
6. **Screenshot Shrink.** Read on an image over 400 KB is downscaled to 1280 px JPEG via `magick`, then `convert`, then `sips`. If none is installed, the original image is used.

It also appends a short "Token-saving rules" section to the system prompt (delegate reading to the scout, cheapest model for subagents, ranged reads, page text over screenshots).

**Install (pick one):**
- Any machine with GitHub access (user scope means every session there):
  ```
  /plugin marketplace add kendalleaddy8-ui/kendalleddy8.github.io
  /plugin install token-saver@kendall-mods
  ```
- Cloud sessions in this repo: automatic. `.claude/settings.json` declares the `kendall-mods` marketplace and enables `token-saver@kendall-mods`.
- Cloud session in another repo: `git fetch` this repo's `main`, load the plugin-authoring skill, and copy `claude-mods/token-saver` unchanged into that session's mods folder (the skill gives the path). Then run `claude plugin validate <folder>` and `claude plugin test <folder>`.
- Local without the marketplace: `claude --plugin-dir <path>/claude-mods/token-saver`, or add the path to `CLAUDE_CODE_PLUGIN_DIRS`.

**Verified:** validate passes and 3 of 3 tests pass. Loaded and running in the original session (the router condensed ~10k-token listings to ~600 tokens). **Not verified:** the marketplace install and the `--plugin-dir` load on another machine.

**Known limits:** scheduled tasks cannot attach plugins (no API for it), so the plugin does not run inside them. Browser screenshots returned inline by MCP tools cannot be resized; only image files on disk can.

**Plain-text version** for Claude chats with no plugins: `TOKEN-SAVER-PROMPT.md` in this repo.

---

## 3. Road to 30 HQ (private artifact)

A single-page app (~1.5 MB HTML) published as a private claude.ai artifact titled "Road to 30 HQ" (find it with the Artifact tool, action `list`). The source is **not** in this repo because it holds personal data. It is built in layers: each version appends a `// ---------- vNN: ...` block before the final `(async()=>{ if(!window.claude)return; ...` init IIFE, and wraps existing functions (`renderRun`, `runBlocks`, `speak`, `go`, `mcPromptLine` ...) instead of editing them. Keep that pattern. Changelog through v26 is on branch `claude/road-to-30-hq-enhance-g3i5lj` (`road-to-30-hq/CHANGELOG.md`).

**Capabilities declared:** `assets, db, downloads, mcp (Google Calendar: list_calendars, list_events, create_event; Claude Docs: batch), sample (images), user, dictation`. A republish without `capabilities` keeps them. Passing `capabilities` replaces the whole set, so restate everything.

**Versions shipped in this session (live = v32, artifact version 65):**
| Version | Change |
|---|---|
| v27 / 27.1 | **Lean engine** (always on): wraps `ultWrap` so in-page Claude calls route by task. Simple chat goes to `modelTier` default at low effort, explicit `quick`/`default` tiers are honored, and hard topics go to Opus (`ULT.model`) at medium effort in chat or high for one-shot jobs. Chats of 18+ messages get older turns summarized on the quick tier. Photos are shrunk to 1024 px. Stats show on the Crew health card. |
| v28 / 28.1 | **Fight Night**: a full-screen, round-by-round view of `runBlocks()` (bell sound, swipe and arrow keys, a scorecard and a knockout screen). A corner "next round" bar on every tab. Opens per day are logged to `log.<date>.ringOpens`; `mcPromptLine` compares days with and without it. Also fixed: the header camp clock now starts Nov 11 (`CAMP_START`), matching `CAMP_DAY1`. |
| v29 | **Workout player** (`wpOpen`): today's `DATA.days` session as steps, one per set, with rest timers parsed from the plan text, conditioning clocks and spoken calls. It keeps the screen awake, resumes from `r30-wp-<date>` and logs `workout:'done', wpMin`. **On Ice**: Work, Ventures, Booth and PLV are hidden until 2027-01-04 (`iceCard`; note `vaultCard` is the unrelated Rewards vault). **Talk to close**: a microphone button in the debrief, using the `dictation` capability with a `webkitSpeechRecognition` fallback. |
| v30 | **Head of AI, anywhere**: the one-company interview content was removed, and its job and study records were deleted from the db. A standing camp lives in db `jobs/hoai` (`standing:true`, `status:'standing'`, deliberately not `active`). It has six monthly moves (`moves[YYYY-MM]`), six decoded pillars, and a study guide rotating two chapters a day. A real opportunity added via "Add an opportunity" takes over while open. The crew profile text was updated to match. |
| v31 | **iPhone voices**: `voiceFor` ranks Premium above Enhanced above everything else, ignores voice names saved on other devices, and gives each crew member a distinct voice (`VCREW` gender and profile map). A "Crew voices on this phone" panel on the Voice card. Crew replies speak as the agent who answered. |
| v32 | **HQ 2.0 for iPhone**: Home is now a hero card (greeting, camp day, days to 30, Deacon's line, next round, next calendar event, context buttons) plus the run, family and mode cards, with the other ~23 cards behind "Everything else on Home". Ignite no longer auto-opens. The dock button Business is replaced by Us. Text fields are 16 px on touch screens (no zoom). Bottom padding clears the fixed bars. The corner bar hides while the hero's button is visible. |

**How to change HQ safely:** read it with the Artifact tool (it saves the full HTML locally), patch with exact-match Python replacements (assert count==1), insert new blocks before the init IIFE, test in Playwright with a mocked `window.claude` (iPhone 13 profile; hide `#ignite`; watch `pageerror`), then republish to the same URL. Use the scout to search the file instead of reading 1.5 MB.

---

## 4. Scheduled tasks changed

- Switched to `claude-sonnet-5-5`: Deacon 5 AM brief, Deacon after-work handoff (5:03 PM weekdays), Deacon nightly debrief nudge (9:07 PM), Hart Thursday family note. Everything else stays on Opus 5.5.
- `HQ · Interview prep brief` (daily) became **`HQ · Head of AI weekly brief`** (Mondays 6:33 AM New York). It reads `jobs` (standing camp and any real opportunity), does light web research, and writes `inbox/hoai-YYYYMMDD`.
- The Watchtower only expects an interview brief while a job's status is `active`, so the standing camp never triggers it.
- Not done (the owner chose to skip it): adding token rules to all 25+ scheduled prompts. Each prompt would have to be rewritten in full, which costs more than it saves.

---

## 5. Decisions and lessons

- Never paste long code from a phone. Point sessions at files in this repo instead (the phone cut off two earlier attempts).
- Pushing straight to `main` is blocked for the agent. Open a PR and merge it through GitHub (this worked).
- HQ's evening modes (`html[data-mode=family|wind|sleep]`) hide Home cards that lack the `.nowcard` class. Anything new on Home needs `.nowcard` or it disappears at night.
- A body stylesheet beats head-injected CSS at equal specificity. Use higher specificity (for example `body main{...}`).
- `position:fixed` elements have `offsetParent === null`. Use `getClientRects().length`.
- The `dictation` capability is not offered in the Claude mobile apps, so Talk to close relies on the browser fallback there.
- The Google Calendar connector in HQ has never been called in a session, so the hero's calendar line is unverified.

---

## 6. Next steps

1. On the new system: install token-saver (section 2) and confirm the cache clock appears in the status line after one turn.
2. Open HQ on the iPhone: tap "Use the best voices on this phone" after downloading Premium voices (Settings → Accessibility → Spoken Content → Voices). Then check the hero card, Fight Night, the workout player and Talk to close.
3. After a week, read the `ringOpens` data via `mcPromptLine` to see whether Fight Night raises completed pillars.
4. On 2027-01-04, On Ice reopens the business tabs automatically. Re-check that the paused Markets and Flow agents resume.
5. Optional later: a 5-tab navigation consolidation (Today, Body, Mind, Life, Crew), a launch-fund meter on Money, and a single morning briefing feed for all agents.
