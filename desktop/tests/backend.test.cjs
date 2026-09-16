const { test } = require('node:test')
const assert = require('node:assert/strict')
const { mkdtemp, rm } = require('node:fs/promises')
const { existsSync } = require('node:fs')
const { join, resolve } = require('node:path')
const { tmpdir } = require('node:os')
const { Backend, METHODS } = require('../electron/backend.cjs')

test('stdio backend handshake, concurrent RPC, validation and clean EOF shutdown', async () => {
  const dir = await mkdtemp(join(tmpdir(), 'bidoytu-ipc-'))
  const root = resolve(__dirname, '../..')
  const candidate = join(
    root,
    'venv',
    process.platform === 'win32' ? 'Scripts/python.exe' : 'bin/python',
  )
  const python = process.env.BIDOYTU_PYTHON || (existsSync(candidate) ? candidate : 'python')
  const backend = new Backend(python, ['-u', '-m', 'bidoytu.backend', '--data-dir', dir], {
    env: { ...process.env, PYTHONPATH: join(root, 'src'), PYTHONUTF8: '1' },
  })
  try {
    const state = await backend.ready
    assert.equal(state.protocol, 1)
    const values = await Promise.all([
      backend.request('decoder.transform', { operation: 'base64.decode', text: 'Ymlkb3l0dQ==' }),
      backend.request('history.list'),
      backend.request('state'),
    ])
    assert.equal(values[0], 'bidoytu')
    assert.equal(values[1].total, 0)
    assert.equal(values[2].running, true)
    await assert.rejects(backend.request('shell.exec'), /Unknown method/)
    assert.equal(METHODS.has('certificate.read'), false)
    assert.equal(METHODS.has('shell.exec'), false)
    await assert.rejects(
      backend.request('decoder.transform', { text: 'x'.repeat(2 * 1024 * 1024) }),
      /exceeds/,
    )
  } finally {
    await backend.stop()
    assert.equal(backend.child.exitCode, 0, backend.diagnostics)
    await rm(dir, { recursive: true, force: true })
  }
})
