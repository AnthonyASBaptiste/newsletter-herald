import {getCliClient} from 'sanity/cli'
import * as fs from 'fs'
import * as path from 'path'

async function seed() {
  const client = getCliClient({apiVersion: '2025-08-30'})
  console.log('Seeding dataset using Sanity CLI client...')

  const ndjsonPath = path.resolve(__dirname, '../seeds/sample-seed.ndjson')
  const content = fs.readFileSync(ndjsonPath, 'utf8')
  const lines = content.trim().split('\n').filter(Boolean)

  const transaction = client.transaction()
  for (const line of lines) {
    const doc = JSON.parse(line)
    console.log(`Queuing document: ${doc._type} (${doc._id})`)
    transaction.createOrReplace(doc)
  }

  console.log('Committing transaction to Sanity Content Lake...')
  const result = await transaction.commit()
  console.log(`Successfully committed ${result.documentIds.length} documents!`)
  for (const id of result.documentIds) {
    console.log(` - ${id}`)
  }
}

seed().catch((err) => {
  console.error('Failed to seed dataset:', err)
  process.exit(1)
})
