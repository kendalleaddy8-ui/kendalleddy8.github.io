import type { EngineInterface, Register } from 'claude-code'

// token-saver: six mods that cut token spend without dumbing the work down.
// 1 Input Router        big tool outputs are condensed by Haiku before the main model reads them
// 2 Effort Optimizer    each turn's effort is lowered to what the prompt needs (never raised)
// 3 Subagent Selector   built-in subagents run on Haiku or Sonnet unless the task is hard
// 4 Cache Clock         status line counts down to when the prompt cache goes cold
// 5 Handoff             /handoff writes HANDOFF.md so a fresh chat can pick up; nudges at 60% context
// 6 Screenshot Shrink   large images are downscaled before Read sends them to the model

const BIG = 24_000 // characters (~6k tokens) before the router steps in
const HAIKU_CAP = 360_000 // characters of raw output Haiku is shown at most
const LEVELS = ['low', 'medium', 'high', 'xhigh', 'max'] as const
type Level = (typeof LEVELS)[number]

const HARD =
  /\b(architect\w*|design|refactor\w*|debug\w*|root cause|why|investigat\w*|plan|strategy|migrat\w*|security|vulnerab\w*|race|deadlock|perf\w*|optimi[sz]\w*|prove|algorithm\w*|trade-?offs?|review|concurren\w*|edge cases?)\b/i
const SIMPLE =
  /^(hi|hey|hello|thanks|thank you|ok|okay|yes|no|yep|nope|sure|cool|great|nice|got it|continue|go|go ahead|do it|proceed|done|commit|push|run (it|the tests?)|try again)\b/i
const KEEP = /\b(ultrathink|think (hard|harder|deeply|carefully)|max effort|full effort)\b/i
const BYPASS = /\b(full output|verbatim|whole file|entire file|no router)\b/i
const QUICK_TASK = /\b(find|search|locate|list|grep|read|summari[sz]e|extract|look ?up|where (is|are)|which files?|count|inventory)\b/i
const IMAGE = /\.(png|jpe?g|webp|gif|bmp|tiff?)$/i

function pickEffort(text: string): Level | undefined {
  const t = text.trim()
  if (!t || KEEP.test(t)) return undefined
  if (HARD.test(t) || t.length > 1500) return undefined // leave hard work at the session's level
  if (t.length < 120 || SIMPLE.test(t)) return 'low'
  return 'medium'
}

function rank(l: unknown): number {
  return typeof l === 'string' ? LEVELS.indexOf(l as Level) : -1
}

function fmt(ms: number): string {
  const s = Math.max(0, Math.round(ms / 1000))
  return `${Math.floor(s / 60)}:${String(s % 60).padStart(2, '0')}`
}

const HANDOFF = `Write a handoff so this work can continue in a fresh chat with no other context. Save it as HANDOFF.md in the working directory (overwrite any old one), then show me its full text.
Sections, short and specific:
1. Goal: what we are trying to achieve and what "done" means.
2. Decisions made, and why (including options rejected).
3. Current state: what works, what is half-done, what is broken.
4. Files touched or important, with paths and line numbers.
5. Commands, branches, environment details needed to continue.
6. Next steps, in order.
7. Open questions and risks.
Leave out anything the next chat does not need. Keep it under 500 words.`

const RULES = `Token-saving rules (token-saver mod):
- Send read-heavy or search-heavy steps (many files, long docs, logs, web pages, big connector results) to the token-saver:scout agent, which runs on Haiku, and work from its summary. Read a file yourself when you are about to edit it.
- When you spawn a subagent, give it the cheapest model that can do the job: haiku for search, reading, extraction and summaries; sonnet for routine coding and reviews; inherit only for hard reasoning.
- Read large files in ranges (offset/limit) once you know where to look.
- In a browser, prefer page text or an accessibility snapshot over screenshots. When you need a screenshot, take only the region you need.
- A tool result marked [token-saver] was condensed by Haiku. Trust it, and re-read exact lines only when you need them to edit or quote.
- Keep reasoning short on simple tasks. When the context gets large, suggest /handoff.`

// The module's own memory for this session (starts over if the mod reloads)
const S = {
  ttlMs: 300_000,
  lastPrompt: '',
  lastTurnEnd: 0,
  warned: false,
  nudged: false,
  effortNote: '',
  effortByTurn: new Map<string, Level>(),
}

function paint($: EngineInterface) {
  const parts: string[] = []
  if (S.effortNote) parts.push(S.effortNote)
  if (S.lastTurnEnd) {
    const left = S.lastTurnEnd + S.ttlMs - Date.now()
    parts.push(left > 0 ? `cache warm ${fmt(left)}` : 'cache cold')
    if (left > 0 && left <= 30_000 && !S.warned) {
      S.warned = true
      $.ui.toast(`Prompt cache goes cold in ${fmt(left)}. Send your next message now to keep it cheap.`)
    }
  }
  $.ui.status(parts.length ? `⛁ ${parts.join(' · ')}` : undefined)
}

export const register: Register = (on, options) => {
  S.ttlMs = (options as { cacheTtl?: string }).cacheTtl === '1h' ? 3_600_000 : 300_000

  on('session.start', async ($, e, next) => {
    await $.command.register({
      name: 'handoff',
      description: 'Write HANDOFF.md so you can continue this work in a fresh, cheap chat.',
    })
    $.clock.every(5_000, () => paint($))
    return next(e)
  })

  on('prompt.compose', async ($, e, next) => {
    const r = await next(e)
    return { sections: [...r.sections, { id: 'token-saver:rules', text: RULES, scope: 'session' as const }] }
  })

  // 5 Handoff
  on('command.run', { command: 'handoff' }, async $ => {
    await $.prompt.submit({ text: HANDOFF })
    return { text: 'Writing HANDOFF.md. Then run /clear (or open a new chat) and paste it in.', isTextDisplayOnly: true }
  })

  // 2 Effort Optimizer: decide once per main turn, apply to each of its requests
  on('turn.start', async ($, e, next) => {
    if (e.agentId !== undefined) return next(e)
    S.lastPrompt = e.text || S.lastPrompt
    const pick = pickEffort(e.text || '')
    if (pick) S.effortByTurn.set(e.turnId, pick)
    else S.effortByTurn.delete(e.turnId)
    return next(e)
  })

  on('turn.step', async function* ($, e, next) {
    if (e.agentId !== undefined) return yield* next(e)
    const pick = S.effortByTurn.get(e.turnId)
    if (pick && rank(e.effort) > rank(pick)) {
      S.effortNote = `effort ${pick}`
      return yield* next({ ...e, effort: pick })
    }
    S.effortNote = typeof e.effort === 'string' ? `effort ${e.effort}` : ''
    return yield* next(e)
  })

  // 4 Cache Clock and the 5 Handoff nudge
  on('turn.complete', async ($, e, next) => {
    const r = await next(e)
    if (e.agentId !== undefined) return r
    S.effortByTurn.delete(e.turnId)
    S.lastTurnEnd = Date.now()
    S.warned = false
    paint($)
    try {
      const { context } = await $.session.usage()
      if (!S.nudged && (context.percent ?? 0) >= 60) {
        S.nudged = true
        $.ui.toast(`Context is ${context.percent}% full. Run /handoff, then continue in a fresh chat to keep each turn cheap.`, { timeoutMs: 12_000 })
      }
    } catch {}
    return r
  })

  // 3 Subagent Model Selector: only built-in agent types, only when no model was asked for
  on('agent.spawn', ($, e, next) => {
    if (e.model !== undefined || e.subagentType === 'fork' || e.subagentType === 'Plan') return next(e)
    if (e.subagentType === 'token-saver:scout') return next(e)
    if (e.provider.plugin !== 'engine') return next(e)
    const head = e.prompt.slice(0, 600)
    let model: string | undefined
    if (e.subagentType === 'Explore' || e.subagentType === 'claude-code-guide' || e.subagentType === 'statusline-setup') model = 'haiku'
    else if (QUICK_TASK.test(head) && !HARD.test(head)) model = 'haiku'
    else if (!HARD.test(head)) model = 'sonnet'
    return model ? next({ ...e, model }) : next(e)
  })

  // 6 Screenshot Shrink and 1 Input Router
  on('tool.call', async ($, e, next) => {
    let call = e
    if (e.tool === 'Read' && IMAGE.test(e.file_path)) {
      try {
        const st = await $.fs.stat(e.file_path)
        if (st.kind === 'file' && st.size > 400_000) {
          const out = `/tmp/token-saver-${st.size}-${Math.round(st.mtimeMs)}.jpg`
          const tries: string[][] = [
            ['magick', e.file_path, '-resize', '1280x1280>', '-quality', '80', out],
            ['convert', e.file_path, '-resize', '1280x1280>', '-quality', '80', out],
            ['sips', '-Z', '1280', '-s', 'format', 'jpeg', e.file_path, '--out', out],
          ]
          for (const argv of tries) {
            try {
              const r = await $.process.run(argv, { timeoutMs: 20_000 })
              if (r.exitCode === 0) {
                call = { ...e, file_path: out }
                break
              }
            } catch {}
          }
        }
      } catch {}
      return next(call)
    }

    const r = await next(call)
    if (e.agentId !== undefined) return r
    const routed = e.tool === 'Read' || e.tool === 'Bash' || e.tool === 'Grep' || e.tool.startsWith('mcp__')
    if (!routed || e.tool.startsWith('mcp__plugin-authoring')) return r
    if (r.deny !== undefined || r.isError || !r.text || r.text.length < BIG) return r
    if (e.tool === 'Read' && (e.offset !== undefined || e.limit !== undefined || /\.(ipynb|pdf)$/i.test(e.file_path))) return r
    if (BYPASS.test(S.lastPrompt)) return r

    const raw = r.text.length > HAIKU_CAP ? r.text.slice(0, HAIKU_CAP * 0.75) + '\n…[middle cut]…\n' + r.text.slice(-HAIKU_CAP * 0.25) : r.text
    const what = e.tool === 'Read' ? `the file ${e.file_path}` : e.tool === 'Bash' ? `the output of: ${String(e.command).slice(0, 300)}` : `the result of ${e.tool}`
    const m = await $.model.complete({
      model: 'haiku',
      effort: 'low',
      maxTokens: 2500,
      timeoutMs: 60_000,
      system:
        'You condense tool output for a more expensive model. Keep only what helps with the task. Copy relevant lines exactly, with their line numbers or locations. Keep error messages, numbers, names and paths exact. Say briefly what kinds of content you left out. Never invent anything.',
      prompt: `The user's current request:\n${S.lastPrompt.slice(0, 3000) || '(unknown)'}\n\nBelow is ${what}. Extract what matters for that request, in under 700 words.\n\n<output>\n${raw}\n</output>`,
    })
    if (!m.isAnswered || !m.text?.trim()) return r
    const lines = r.text.split('\n').length
    const how =
      e.tool === 'Read'
        ? `Read it again with offset/limit for exact lines (it has about ${lines} lines).`
        : e.tool === 'Bash'
          ? 'Re-run the command piped through grep, head or sed for exact text.'
          : 'Call the tool again with a narrower query for exact data.'
    $.ui.status(`⛁ router: ${Math.round(r.text.length / 4).toLocaleString()} → ${Math.round(m.text.length / 4).toLocaleString()} tokens`)
    return {
      deny: `[token-saver] This output was about ${Math.round(r.text.length / 4).toLocaleString()} tokens, so Haiku condensed it to what matters for the current request. ${how}\n\n${m.text.trim()}`,
    }
  })
}
