'use strict'
const { spawn } = require('node:child_process')
const { EventEmitter } = require('node:events')

const METHODS = new Set([
  'state',
  'history.list',
  'history.detail',
  'history.metadata',
  'proxy.start',
  'proxy.stop',
  'proxy.intercept',
  'proxy.resolve',
  'scope.save',
  'repeater.send',
  'intruder.start',
  'intruder.results',
  'intruder.cancel',
  'audit.toggle',
  'audit.list',
  'decoder.transform',
  'workspace.load',
  'workspace.save',
])

class Backend extends EventEmitter {
  constructor(command, args, options = {}) {
    super()
    this.pending = new Map()
    this.sequence = 0
    this.buffer = ''
    this.diagnostics = ''
    this.child = spawn(command, args, {
      ...options,
      windowsHide: true,
      stdio: ['pipe', 'pipe', 'pipe'],
    })
    this.ready = new Promise((resolve, reject) => {
      const timeout = setTimeout(() => {
        reject(new Error('Python engine startup timed out'))
        this.child.kill()
      }, 30000)
      this.once('ready', (state) => {
        clearTimeout(timeout)
        resolve(state)
      })
      this.once('failure', (error) => {
        clearTimeout(timeout)
        reject(error)
      })
    })
    this.child.stdout.setEncoding('utf8')
    this.child.stdout.on('data', (chunk) => this.consume(chunk))
    this.child.stderr.on('data', (chunk) => {
      this.diagnostics = (this.diagnostics + chunk.toString()).slice(-4000)
    })
    this.child.stdin.on('error', (error) => this.fail(error))
    this.child.on('error', (error) => this.fail(error))
    this.child.on('exit', (code, signal) => {
      this.exited = true
      this.fail(new Error(`Python engine exited (${code ?? signal}). ${this.diagnostics}`))
      this.emit('exit')
    })
  }
  fail(error) {
    for (const entry of this.pending.values()) {
      clearTimeout(entry.timer)
      entry.reject(error)
    }
    this.pending.clear()
    this.emit('failure', error)
  }
  consume(chunk) {
    this.buffer += chunk
    if (this.buffer.length > 16 * 1024 * 1024) {
      this.fail(new Error('Python protocol frame exceeded 16 MiB'))
      this.child.kill()
      return
    }
    let newline
    while ((newline = this.buffer.indexOf('\n')) !== -1) {
      const line = this.buffer.slice(0, newline)
      this.buffer = this.buffer.slice(newline + 1)
      let message
      try {
        message = JSON.parse(line)
      } catch {
        this.fail(new Error('Invalid Python protocol frame'))
        this.child.kill()
        return
      }
      if (message.event) {
        this.emit(message.event, message.data)
        continue
      }
      const entry = this.pending.get(message.id)
      if (!entry) continue
      this.pending.delete(message.id)
      clearTimeout(entry.timer)
      if (message.error) entry.reject(new Error(message.error.message))
      else entry.resolve(message.result)
    }
  }
  request(method, params = {}) {
    if (this.exited || this.child.killed)
      return Promise.reject(new Error('Python engine is offline. Restart the application.'))
    if (this.pending.size >= 32) return Promise.reject(new Error('Too many pending requests'))
    const id = ++this.sequence
    const line = JSON.stringify({ id, method, params }) + '\n'
    if (Buffer.byteLength(line) > 2 * 1024 * 1024)
      return Promise.reject(new Error('Request exceeds 2 MiB'))
    return new Promise((resolve, reject) => {
      const timer = setTimeout(() => {
        this.pending.delete(id)
        reject(new Error(`${method} timed out`))
      }, 60000)
      this.pending.set(id, { resolve, reject, timer })
      this.child.stdin.write(line, (error) => {
        if (error) {
          clearTimeout(timer)
          this.pending.delete(id)
          reject(error)
        }
      })
    })
  }
  async stop() {
    if (this.exited) return
    await new Promise((resolve) => {
      const timer = setTimeout(() => {
        this.child.kill()
        resolve()
      }, 12000)
      this.once('exit', () => {
        clearTimeout(timer)
        resolve()
      })
      this.child.stdin.end()
    })
  }
}
module.exports = { Backend, METHODS }
