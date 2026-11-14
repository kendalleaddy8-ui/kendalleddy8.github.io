import { expect, test } from 'claude-code/testing'

const BIG = 'line of log output that nobody needs\n'.repeat(2000)

test('a big Bash result is condensed by Haiku', async ($, on) => {
  let asked = ''
  on('tool.call', () => ({ result: { stdout: BIG, stderr: '', interrupted: false }, text: BIG }))
  on('model.complete', (_, e) => {
    asked = e.model
    return { value: { isAnswered: true, text: 'Only the error on line 12 matters.', usage: { input_tokens: 1, output_tokens: 1, cache_creation_input_tokens: 0, cache_read_input_tokens: 0 } } }
  })
  const r = await $.tool.call({ tool: 'Bash', command: 'npm test' })
  expect(asked).toBe('haiku')
  expect(String(r.deny)).toContain('[token-saver]')
  expect(String(r.deny)).toContain('Only the error on line 12 matters.')
})

test('a small result passes untouched', async ($, on) => {
  on('tool.call', () => ({ result: { stdout: 'ok', stderr: '', interrupted: false }, text: 'ok' }))
  const r = await $.tool.call({ tool: 'Bash', command: 'ls' })
  expect(r.deny).toBe(undefined)
})

test('Explore runs on Haiku; a hard general task keeps its model', async ($, on) => {
  const seen: (string | undefined)[] = []
  on('agent.spawn', (_, e) => {
    seen.push(e.model)
    return { model: e.model ?? 'inherit' } as never
  })
  const base = { tool_use_id: 't1', description: 'x', provider: { plugin: 'engine', tier: 'core' }, parentModel: 'opus' }
  await $.agent.spawn({ ...base, subagentType: 'Explore', prompt: 'find the config files' } as never)
  await $.agent.spawn({ ...base, subagentType: 'general-purpose', prompt: 'debug the race condition in the scheduler' } as never)
  await $.agent.spawn({ ...base, subagentType: 'general-purpose', prompt: 'add a docstring to utils.py' } as never)
  expect(seen).toEqual(['haiku', undefined, 'sonnet'])
})
