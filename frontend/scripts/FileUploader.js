// File Uploader - Handles file upload and parsing
class FileUploader {
  constructor(dataManager) {
    this.dataManager = dataManager
    this.backendURL = 'http://localhost:3000'
  }

  formatFileSize(bytes) {
    if (bytes < 1024) return bytes + ' B'
    if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB'
    return (bytes / (1024 * 1024)).toFixed(1) + ' MB'
  }

  async handleFileUpload(file, onSuccess, onError) {
    const fileName = file.name
    const fileSize = this.formatFileSize(file.size)
    const fileType = fileName.split('.').pop()?.toLowerCase()

    if (!['csv', 'json'].includes(fileType)) {
      UIHelper.showToast('Please upload a CSV or JSON file', 'error')
      return
    }

    try {
      UIHelper.showLoading('Uploading file...')
      UIHelper.setDropzoneState(true)

      // Send file to backend
      const formData = new FormData()
      formData.append('file', file)

      const response = await fetch(`${this.backendURL}/api/ingest`, {
        method: 'POST',
        body: formData
      })

      if (!response.ok) {
        const error = await response.json()
        throw new Error(error.error || 'Upload failed')
      }

      const result = await response.json()

      // Update local state
      this.dataManager.setUploadedData(result.preview || [])
      this.dataManager.addUpload({ name: fileName, size: fileSize, time: 'just now' })

      UIHelper.hideLoading()
      UIHelper.setDropzoneState(false)
      UIHelper.showToast(`Successfully uploaded ${result.records} records`, 'success')

      onSuccess(result.records, fileName)
    } catch (err) {
      console.error('Upload error:', err)
      UIHelper.hideLoading()
      UIHelper.setDropzoneState(false)
      UIHelper.showToast(`Upload failed: ${err.message}`, 'error', 5000)
      if (onError) onError(err)
    }
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
