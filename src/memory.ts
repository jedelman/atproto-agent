/**
 * Writes content to Scout-Two's Letta core memory blocks.
 * Core memory is always in context and never compressed — use for permanent directives.
 *
 * Usage:
 *   BLOCK_LABEL=human BLOCK_VALUE="..." node dist/memory.js      # replace entire block
 *   BLOCK_LABEL=human BLOCK_APPEND="..." node dist/memory.js     # append to existing block
 *   node dist/memory.js                                          # list all blocks
 */

const LETTA_BASE_URL = process.env.LETTA_BASE_URL
const LETTA_AGENT_ID = process.env.LETTA_AGENT_ID
const LETTA_API_KEY = process.env.LETTA_API_KEY
const BLOCK_LABEL = process.env.BLOCK_LABEL   // e.g. 'human', 'persona'
const BLOCK_VALUE = process.env.BLOCK_VALUE   // replace entire value
const BLOCK_APPEND = process.env.BLOCK_APPEND // append to existing value
const DRY_RUN = process.env.DRY_RUN === 'true'

if (!LETTA_BASE_URL || !LETTA_AGENT_ID) {
  console.error('LETTA_BASE_URL and LETTA_AGENT_ID are required')
  process.exit(1)
}

const headers: Record<string, string> = { 'Content-Type': 'application/json' }
if (LETTA_API_KEY) headers['Authorization'] = `Bearer ${LETTA_API_KEY}`

// ---------------------------------------------------------------------------
// API helpers
// ---------------------------------------------------------------------------

interface MemoryBlock {
  id: string
  label: string
  value: string
  limit: number
  template_name?: string
  description?: string
}

async function listBlocks(): Promise<MemoryBlock[]> {
  const res = await fetch(
    `${LETTA_BASE_URL}/v1/agents/${LETTA_AGENT_ID}/core-memory/blocks`,
    { headers }
  )
  if (!res.ok) throw new Error(`List blocks failed: ${res.status} ${await res.text()}`)
  return res.json() as Promise<MemoryBlock[]>
}

async function updateBlock(label: string, value: string): Promise<MemoryBlock> {
  const res = await fetch(
    `${LETTA_BASE_URL}/v1/agents/${LETTA_AGENT_ID}/core-memory/blocks/${label}`,
    { method: 'PATCH', headers, body: JSON.stringify({ value }) }
  )
  if (!res.ok) throw new Error(`Update block failed: ${res.status} ${await res.text()}`)
  return res.json() as Promise<MemoryBlock>
}

// ---------------------------------------------------------------------------
// Main
// ---------------------------------------------------------------------------

async function main() {
  const blocks = await listBlocks()

  if (!BLOCK_LABEL) {
    // List mode
    console.log(`\nCore memory blocks for agent ${LETTA_AGENT_ID}:\n`)
    for (const b of blocks) {
      console.log(`── [${b.label}] (${b.value.length}/${b.limit} chars)`)
      console.log(b.value)
      console.log()
    }
    return
  }

  const existing = blocks.find(b => b.label === BLOCK_LABEL)
  if (!existing) {
    console.error(`Block '${BLOCK_LABEL}' not found. Available: ${blocks.map(b => b.label).join(', ')}`)
    process.exit(1)
  }

  let newValue: string
  if (BLOCK_VALUE !== undefined) {
    newValue = BLOCK_VALUE
  } else if (BLOCK_APPEND !== undefined) {
    newValue = existing.value.trimEnd() + '\n\n' + BLOCK_APPEND
  } else {
    console.error('Set BLOCK_VALUE (replace) or BLOCK_APPEND (append)')
    process.exit(1)
  }

  if (newValue.length > existing.limit) {
    console.error(`Value too long: ${newValue.length} chars, limit is ${existing.limit}`)
    process.exit(1)
  }

  console.log(`Block: ${BLOCK_LABEL}`)
  console.log(`Current length: ${existing.value.length}`)
  console.log(`New length: ${newValue.length} / ${existing.limit}`)
  console.log(`\nNew value:\n${newValue}\n`)

  if (DRY_RUN) {
    console.log('[DRY RUN] Would write above to core memory.')
    return
  }

  const updated = await updateBlock(BLOCK_LABEL, newValue)
  console.log(`Updated block '${updated.label}' (${updated.value.length} chars)`)
}

main().catch((err: unknown) => {
  console.error('Unhandled error:', err)
  process.exit(1)
})
