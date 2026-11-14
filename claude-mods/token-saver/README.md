# token-saver

Six Claude Code mods that cut token spend without lowering the quality of the work:

1. **Input Router**: when a Read, Bash, Grep or connector result is over about 6k tokens, Haiku condenses it to what matters for your current request before the main model sees it. Say "full output" or "whole file" in your prompt to turn it off for that turn.
2. **Effort Optimizer**: short and simple prompts run at low effort and ordinary ones at medium. Hard prompts stay at your session's level. It only lowers effort, never raises it.
3. **Subagent Model Selector**: built-in subagents run on Haiku for search and reading and on Sonnet for routine work, unless the task looks hard or a model was named.
4. **Cache Clock**: the status line counts down to when the prompt cache goes cold, and a toast warns you 30 seconds before.
5. **Handoff**: `/handoff` writes HANDOFF.md for a fresh chat. You get a nudge when context passes 60%.
6. **Screenshot Shrink**: images over 400 KB are downscaled to 1280 px (ImageMagick or sips) before Read sends them.

It also adds a `token-saver:scout` agent on Haiku and short system-prompt rules telling Claude to use it.

Set the cache lifetime (5m or 1h) in the config menu.
