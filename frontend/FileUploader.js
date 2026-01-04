// File Uploader - Handles file upload and parsing
class FileUploader {
  constructor(dataManager) {
    this.dataManager = dataManager
  }

  parseJSON(content) {
    const data = JSON.parse(content)
    return Array.isArray(data) ? data : [data]
  }

  parseCSV(content) {
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

  formatFileSize(bytes) {
    if (bytes < 1024) return bytes + ' B'
    if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB'
    return (bytes / (1024 * 1024)).toFixed(1) + ' MB'
  }

  handleFileUpload(file, onSuccess) {
    const fileName = file.name
    const fileSize = this.formatFileSize(file.size)
    const fileType = fileName.split('.').pop()?.toLowerCase()

    if (!['csv', 'json'].includes(fileType)) {
      alert('Please upload a CSV or JSON file')
      return
    }

    const reader = new FileReader()
    reader.onload = (e) => {
      const content = e.target?.result
      if (typeof content === 'string') {
        try {
          let parsedData
          if (fileType === 'json') {
            parsedData = this.parseJSON(content)
          } else if (fileType === 'csv') {
            parsedData = this.parseCSV(content)
          }

          this.dataManager.setUploadedData(parsedData)
          this.dataManager.addUpload({ name: fileName, size: fileSize, time: 'just now' })

          onSuccess(parsedData.length, fileName)
        } catch (err) {
          alert(`Error parsing file: ${err.message}`)
        }
      }
    }
    reader.readAsText(file)
  }

  attachHandlers(onFileUploaded) {
    const dropzone = document.getElementById('dropzone')
    const fileInput = document.getElementById('fileInput')

    if (!dropzone || !fileInput) return

    dropzone.addEventListener('click', () => fileInput.click())

    fileInput.addEventListener('change', (e) => {
      const file = e.target.files?.[0]
      if (file) this.handleFileUpload(file, onFileUploaded)
    })

    dropzone.addEventListener('dragover', (e) => {
      e.preventDefault()
      dropzone.style.background = '#f0f0f0'
    })

    dropzone.addEventListener('dragleave', () => {
      dropzone.style.background = ''
    })

    dropzone.addEventListener('drop', (e) => {
      e.preventDefault()
      dropzone.style.background = ''
      const file = e.dataTransfer?.files?.[0]
      if (file) this.handleFileUpload(file, onFileUploaded)
    })
  }
}
