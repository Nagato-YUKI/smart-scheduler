import { readFileSync, writeFileSync } from 'fs'
import { join, dirname } from 'path'
import { fileURLToPath } from 'url'

const __dirname = dirname(fileURLToPath(import.meta.url))
const distDir = join(__dirname, 'dist')

;['index.html', '404.html'].forEach(file => {
  const filePath = join(distDir, file)
  try {
    let html = readFileSync(filePath, 'utf-8')
    // Remove crossorigin attribute from script and link tags
    html = html.replace(/\s+crossorigin(?=\s|>)/g, '')
    writeFileSync(filePath, html)
    console.log(`Fixed: ${file}`)
  } catch (e) {
    if (e.code !== 'ENOENT') throw e
  }
})
console.log('Done: crossorigin attributes removed from HTML')
