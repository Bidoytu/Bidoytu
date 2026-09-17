import { _electron as electron, expect } from '@playwright/test'
import { mkdtemp, rm, writeFile, mkdir } from 'node:fs/promises'
import { tmpdir } from 'node:os'
import { join } from 'node:path'

const dir = await mkdtemp(join(tmpdir(), 'bidoytu-editor-'))
const env = { ...process.env, BIDOYTU_DATA_DIR: dir, BIDOYTU_TEST: '1' }
delete env.ELECTRON_RUN_AS_NODE
const app = await electron.launch({ args: ['.'], env })
try {
  const page = await app.firstWindow()
  await expect(page.getByText('Engine connected', { exact: true })).toBeVisible()
  await page.getByRole('button', { name: 'Decoder', exact: true }).click()
  await page.getByRole('combobox').selectOption('base64.encode')
  await page.getByRole('textbox', { name: 'Input editor' }).evaluate((element) => {
    Object.getOwnPropertyDescriptor(HTMLTextAreaElement.prototype, 'value').set.call(
      element,
      'line\n'.repeat(20000),
    )
    element.dispatchEvent(new Event('input', { bubbles: true }))
  })
  const start = Date.now()
  await page.getByRole('button', { name: 'Pretty', exact: false }).first().click()
  await expect(page.getByRole('region', { name: 'Input message' })).toBeVisible()
  const report = {
    lines: 20000,
    rendered_lines: await page.locator('.code-line').count(),
    switch_ms: Date.now() - start,
  }
  console.log(JSON.stringify(report))
  await mkdir('test-results', { recursive: true })
  await writeFile(
    `test-results/editor-${process.env.BENCHMARK_LABEL || 'current'}.json`,
    JSON.stringify(report, null, 2),
  )
} finally {
  await app.close()
  await rm(dir, { recursive: true, force: true })
}
