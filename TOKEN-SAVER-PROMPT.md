# Token-saver prompt for Claude at work

Paste everything between the lines into Claude. In **Claude Code**, it builds the six mods as a plugin. In a **regular Claude chat** (no Claude Code), Claude follows the same rules by hand for the rest of the conversation.

---

Set up a token-saving system for this workspace. The goal is to cut token spend a lot without lowering the quality of the work. If you're running in Claude Code, build it as a plugin of function hooks using the plugin-authoring skill (or as hooks, a status line, an agent file, a slash command and CLAUDE.md rules if mods aren't available). Validate it, type-check it, test it, and tell me which parts are enforced automatically and which are only instructions. If you're in a normal chat with no tools, follow these rules yourself from now on.

1. **Input Router.** When a file read, shell command, search or connector result is large (over about 6,000 tokens), don't hand the whole thing to the main model. Have Haiku condense it to only what matters for my current request, keeping exact lines, line numbers, numbers, names, paths and error text. Tell the main model how to get exact text if it needs it (re-read a range or narrow the query). Skip this when I say "full output", "verbatim" or "whole file". Also create a `scout` subagent on Haiku (read-only tools: Read, Grep, Glob, WebFetch, WebSearch, Bash) that returns facts with file:line references in under 250 words, and send read-heavy steps to it.

2. **Effort Optimizer.** For each prompt, pick the lowest effort that fits. Use low for short or simple prompts (acknowledgements, "continue", small edits, quick questions) and medium for ordinary work. For hard work (architecture, debugging, root cause, security, performance, plans, reviews) or when I say "think hard", keep my session's level. Only ever lower effort, never raise it. Show the level in the status line.

3. **Subagent Model Selector.** When a subagent is spawned with no model named, run Explore and lookup-style tasks (find, search, read, list, summarize, extract) on Haiku and routine coding or reviews on Sonnet. Keep the main model only for hard reasoning. Never override a model that I or an agent's own definition named.

4. **Cache Clock.** Add a status line that counts down from the end of the last turn to when the prompt cache goes cold (5 minutes by default, with a setting for 1 hour), and pop a warning 30 seconds before it does.

5. **Handoff.** Add a `/handoff` command that writes HANDOFF.md covering the goal and definition of done, decisions made and why, current state, key files with paths and line numbers, commands and branches, ordered next steps, and open questions, all in under 500 words. I'll start a fresh chat from it. Remind me to use it once context passes 60%.

6. **Efficient Browser Use.** Before an image or screenshot over about 400 KB is sent to the model, shrink it to at most 1280 px on the long side as a JPEG (ImageMagick, or sips on a Mac). Fall back to the original if neither is installed. In browsers, prefer page text or an accessibility snapshot over screenshots, and screenshot only the region needed.

Also add short standing rules to the system prompt or CLAUDE.md that say the same things: delegate reading to scout, give subagents the cheapest model that can do the job, read big files in ranges, prefer page text over screenshots, trust condensed results and re-read exact lines only to edit or quote, keep reasoning short on simple tasks, and suggest /handoff when context gets large.

---

## Shortcut if your work machine can reach GitHub

The finished plugin is in this repository. In Claude Code:

```
/plugin marketplace add kendalleaddy8-ui/kendalleddy8.github.io
/plugin install token-saver@kendall-mods
```

(This works once the `claude/festive-turing-mql21f` branch is merged into `main`.)
