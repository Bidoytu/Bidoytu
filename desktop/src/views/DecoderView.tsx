import { ArrowLeftRight, WandSparkles } from 'lucide-react'
import { api } from '../api'
import { Button, Editor } from '../components'

import type { WorkspaceController } from '../hooks/useWorkspace'

export function DecoderView({ workspace }: { workspace: WorkspaceController }) {
  const {
    online,
    decoderInput,
    setDecoderInput,
    decoderOutput,
    setDecoderOutput,
    operation,
    setOperation,
    split,
    run,
  } = workspace
  return (
    <div className="tool-workspace">
      <div className="tool-toolbar">
        <label className="inline muted">
          Transformation{' '}
          <select
            value={operation}
            onChange={(e) => setOperation(e.target.value)}
            aria-label="Decoder transformation"
          >
            {[
              'base64.decode',
              'base64.encode',
              'url.decode',
              'url.encode',
              'json.format',
              'hex.decode',
              'hex.encode',
            ].map((op) => (
              <option key={op} value={op}>
                {op.replace('.', ' · ')}
              </option>
            ))}
          </select>
        </label>
        <Button
          className="primary"
          disabled={!online}
          onClick={() =>
            void run(async () =>
              setDecoderOutput(
                await api.request<string>('decoder.transform', {
                  operation,
                  text: decoderInput,
                }),
              ),
            )
          }
        >
          <WandSparkles size={14} />
          Transform
        </Button>
        <span className="grow" />
        <Button
          className="subtle"
          onClick={() => {
            setDecoderInput(decoderOutput)
            setDecoderOutput(decoderInput)
          }}
        >
          <ArrowLeftRight size={13} />
          Swap
        </Button>
      </div>
      <div className="editor-split full">
        <Editor title="Input" value={decoderInput} onChange={setDecoderInput} />
        <Editor title="Output" value={decoderOutput} />
      </div>
    </div>
  )
}
