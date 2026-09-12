const API_BASE_URL = (import.meta.env.VITE_API_BASE_URL || '/api').replace(/\/$/, '')

function parseResponse(xhr) {
  let data
  try {
    data = xhr.responseText ? JSON.parse(xhr.responseText) : {}
  } catch {
    throw new Error('The backend returned an unreadable response.')
  }

  if (xhr.status < 200 || xhr.status >= 300) {
    throw new Error(data.detail || data.error || `Request failed with status ${xhr.status}.`)
  }
  return data
}

export function uploadPdf(file, onProgress = () => {}) {
  return new Promise((resolve, reject) => {
    const request = new XMLHttpRequest()
    const formData = new FormData()
    formData.append('file', file)

    request.open('POST', `${API_BASE_URL}/upload`)
    request.responseType = 'text'
    request.upload.addEventListener('progress', (event) => {
      if (event.lengthComputable) onProgress(Math.round((event.loaded / event.total) * 100))
    })
    request.addEventListener('load', () => {
      try {
        resolve(parseResponse(request))
      } catch (error) {
        reject(error)
      }
    })
    request.addEventListener('error', () => reject(new Error('Could not reach the FastAPI backend.')))
    request.addEventListener('abort', () => reject(new Error('Upload cancelled.')))
    request.send(formData)
  })
}

export async function scoreDocument(document) {
  const response = await fetch(`${API_BASE_URL}/score`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(document),
  })

  const data = await response.json().catch(() => ({}))
  if (!response.ok) throw new Error(data.detail || data.error || 'The backend could not score this document.')
  return data
}

export async function generateUselessLesson(document, question = 'Teach me something from this PDF.') {
  const response = await fetch(`${API_BASE_URL}/ai/lesson`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ document, question }),
  })

  const data = await response.json().catch(() => ({}))
  if (!response.ok) throw new Error(data.detail || data.error || 'The useless lesson could not be generated.')
  return data
}

export async function generateUselessQuestions(document) {
  const response = await fetch(`${API_BASE_URL}/ai/questions`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ document }),
  })

  const data = await response.json().catch(() => ({}))
  if (!response.ok) throw new Error(data.detail || data.error || 'The exam questions could not be generated.')
  return data
}

export async function generatePanicPlan(document, duration) {
  const response = await fetch(`${API_BASE_URL}/ai/panic`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ document, duration }),
  })

  const data = await response.json().catch(() => ({}))
  if (!response.ok) throw new Error(data.detail || data.error || 'Panic mode could not be activated.')
  return data
}

export async function refuseActualTopic(document, topic = 'the actual topic') {
  const response = await fetch(`${API_BASE_URL}/ai/refusal`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ document, topic }),
  })

  const data = await response.json().catch(() => ({}))
  if (!response.ok) throw new Error(data.detail || data.error || 'Useful information was unavailable.')
  return data
}
