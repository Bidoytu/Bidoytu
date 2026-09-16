import { spawn } from 'node:child_process'
import { createServer } from 'vite'
import electron from 'electron'
const server = await createServer({ configFile: 'desktop/vite.config.ts' })
await server.listen()
const child = spawn(electron, ['.'], { stdio: 'inherit', env: { ...process.env, BIDOYTU_DEV: '1' }, windowsHide: true })
child.on('exit', async code => { await server.close(); process.exit(code ?? 0) })
process.on('SIGINT', () => child.kill())
