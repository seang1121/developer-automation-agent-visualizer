import { readdirSync, copyFileSync, existsSync } from 'node:fs'
import { join } from 'node:path'

const dataDir = join(import.meta.dirname, '..', 'src', 'data')
const files = readdirSync(dataDir)

for (const file of files) {
  if (!file.endsWith('.example.json')) continue
  const target = file.replace('.example.json', '.json')
  const targetPath = join(dataDir, target)
  if (!existsSync(targetPath)) {
    copyFileSync(join(dataDir, file), targetPath)
    console.log(`Created ${target} from ${file}`)
  }
}

console.log('Data files initialized.')
