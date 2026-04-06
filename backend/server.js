import express from 'express'
import cors from 'cors'
import multer from 'multer'
import fs from 'fs/promises'
import path from 'path'
import { fileURLToPath } from 'url'

const __filename = fileURLToPath(import.meta.url)
const __dirname = path.dirname(__filename)

const app = express()
const PORT = process.env.PORT || 3000
const DATA_DIR = path.resolve(process.env.DATA_DIR || path.join(__dirname, 'data'))
const UPLOADS_DIR = path.resolve(process.env.UPLOADS_DIR || path.join(__dirname, 'uploads'))

// Middleware
app.use(cors())
app.use(express.json())
app.use(express.urlencoded({ extended: true }))

// File upload configuration
const upload = multer({ 
  dest: 'uploads/',
  limits: { fileSize: 10 * 1024 * 1024 } // 10MB limit
})

// Ensure directories exist
await fs.mkdir(DATA_DIR, { recursive: true })
await fs.mkdir(UPLOADS_DIR, { recursive: true })

// Routes
app.get('/health', (req, res) => {
  res.json({ status: 'ok', timestamp: new Date().toISOString() })
})

app.post('/api/ingest', upload.single('file'), async (req, res) => {
  try {
    if (!req.file) {
      return res.status(400).json({ error: 'No file uploaded' })
    }

    const fileContent = await fs.readFile(req.file.path, 'utf-8')
    const fileType = req.file.originalname.split('.').pop().toLowerCase()

    let parsedData
    
    if (fileType === 'json') {
      parsedData = JSON.parse(fileContent)
      if (!Array.isArray(parsedData)) {
        parsedData = [parsedData]
      }
    } else if (fileType === 'csv') {
      parsedData = parseCSV(fileContent)
    } else {
      await fs.unlink(req.file.path)
      return res.status(400).json({ error: 'Unsupported file type. Use CSV or JSON.' })
    }

    // Save to data storage
    const timestamp = Date.now()
    const dataFile = path.join(DATA_DIR, `upload_${timestamp}.json`)
    await fs.writeFile(dataFile, JSON.stringify(parsedData, null, 2))

    // Clean up temp upload
    await fs.unlink(req.file.path)

    res.json({
      success: true,
      message: `Uploaded ${parsedData.length} records`,
      records: parsedData.length,
      timestamp: new Date(timestamp).toISOString(),
      preview: parsedData.slice(0, 5)
    })
  } catch (error) {
    console.error('Upload error:', error)
    res.status(500).json({ error: 'Failed to process upload', details: error.message })
  }
})

app.get('/api/data', async (req, res) => {
  try {
    const files = await fs.readdir(DATA_DIR)
    const jsonFiles = files.filter(f => f.endsWith('.json'))
    
    const allData = []
    for (const file of jsonFiles) {
      const content = await fs.readFile(path.join(DATA_DIR, file), 'utf-8')
      const data = JSON.parse(content)
      allData.push(...data)
    }

    res.json({
      totalRecords: allData.length,
      files: jsonFiles.length,
      data: allData
    })
  } catch (error) {
    console.error('Data retrieval error:', error)
    res.status(500).json({ error: 'Failed to retrieve data' })
  }
})

// Helper: Parse CSV
function parseCSV(content) {
  const lines = content.trim().split('\n')
  if (lines.length === 0) return []

  const headers = lines[0].split(',').map(h => h.trim())
  const rows = []

  for (let i = 1; i < lines.length; i++) {
    const values = lines[i].split(',').map(v => v.trim())
    const row = {}
    headers.forEach((header, idx) => {
      row[header] = values[idx] || ''
    })
    rows.push(row)
  }

  return rows
}

app.listen(PORT, () => {
  console.log(`🚀 TPP Backend running on http://localhost:${PORT}`)
  console.log(`📁 Data directory: ${DATA_DIR}`)
  console.log(`📤 Upload endpoint: POST http://localhost:${PORT}/api/ingest`)
})
