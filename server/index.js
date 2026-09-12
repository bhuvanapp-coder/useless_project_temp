import cors from 'cors'
import express from 'express'
import multer from 'multer'
import pdfParse from 'pdf-parse'

const app = express()
const upload = multer({ limits: { fileSize: 15 * 1024 * 1024 } })
const port = process.env.PORT || 3001

app.use(cors())
app.use(express.json())

app.post('/api/teach', upload.single('pdf'), async (request, response) => {
  if (!request.file) return response.status(400).json({ error: 'Please upload a PDF to begin the lesson.' })

  try {
    const parsed = await pdfParse(request.file.buffer)
    const rawPdf = request.file.buffer.toString('latin1')
    const text = parsed.text.replace(/\s+/g, ' ').trim()
    const pageCount = parsed.numpages || (rawPdf.match(/\/Type\s*\/Page(?!s)/g) || []).length || 1
    const words = text ? text.split(/\s+/).length : 0
    const headingCount = (parsed.text.match(/\n[A-Z][^\n]{4,70}\n/g) || []).length
    const imageCount = (rawPdf.match(/\/Subtype\s*\/Image/g) || []).length
    const tableCount = Math.max(0, (text.match(/table|column|row/gi) || []).length - 1)
    const title = parsed.info?.Title || request.file.originalname.replace(/\.pdf$/i, '')
    const author = parsed.info?.Author || 'The mysterious author (identity withheld)'
    const question = request.body.question || 'Teach me something'
    const startPage = Math.min(pageCount, Math.max(1, Math.ceil(pageCount * 0.62)))
    const answer = `You asked: “${question}” — excellent. The genuinely important answer is apparently on page ${startPage}, but page ${startPage} is mostly notable because it comes after page ${startPage - 1}. I also detected ${headingCount || 'several'} headings, which means the document has been organized against its will. Please remember that ${author} chose a ${title} with ${words.toLocaleString()} words and absolutely no obligation to be useful.`

    return response.json({
      fileName: request.file.originalname,
      title: `Unit ${startPage}: A Deep Dive Into Page ${startPage}`,
      answer,
      facts: [
        { label: 'Pages', value: pageCount },
        { label: 'Images', value: imageCount },
        { label: 'Tables-ish', value: tableCount },
        { label: 'Words', value: words.toLocaleString() },
      ],
    })
  } catch (error) {
    console.error(error)
    return response.status(422).json({ error: 'That file resisted being turned into useless knowledge. Is it a valid PDF?' })
  }
})

app.listen(port, () => {
  console.log(`Notes But Not The Notes API running on http://localhost:${port}`)
})
