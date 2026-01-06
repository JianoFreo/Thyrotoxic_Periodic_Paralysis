// Data Manager - Handles all data storage and retrieval
class DataManager {
  constructor() {
    this.backendURL = 'http://localhost:3000'
    this.sections = [
      { key: 'overview', label: 'Overview' },
      { key: 'monitoring', label: 'Patient Monitoring' },
      { key: 'upload', label: 'Data Upload' },
      { key: 'insights', label: 'Model Insights' },
      { key: 'settings', label: 'Settings' },
    ]

    this.readings = []
    this.patients = []
    this.uploads = []
    this.uploadedData = []
    this.allData = []
  }

  async fetchDataFromBackend() {
    try {
      const response = await fetch(`${this.backendURL}/api/data`)
      if (response.ok) {
        const result = await response.json()
        this.allData = result.data || []
        this.uploadedData = this.allData
        this.calculateReadings()
        this.generatePatientList()
        return true
      }
    } catch (error) {
      console.error('Failed to fetch data from backend:', error)
    }
    return false
  }

  calculateReadings() {
    if (this.allData.length === 0) {
      this.readings = [
        { label: 'Total Records', value: '0', change: 'Upload data to begin' }
      ]
      return
    }

    const heartRates = this.allData.map(d => d.heartRate).filter(hr => hr)
    const hrvValues = this.allData.map(d => d.hrv).filter(hrv => hrv)
    
    const avgHR = heartRates.length > 0 
      ? Math.round(heartRates.reduce((a, b) => a + b, 0) / heartRates.length)
      : 0
    
    const avgHRV = hrvValues.length > 0
      ? Math.round(hrvValues.reduce((a, b) => a + b, 0) / hrvValues.length)
      : 0

    const highHR = heartRates.filter(hr => hr > 100).length

    this.readings = [
      { label: 'Avg Heart Rate', value: `${avgHR} bpm`, change: `${heartRates.length} readings` },
      { label: 'Avg HRV', value: `${avgHRV} ms`, change: `${hrvValues.length} readings` },
      { label: 'High HR Events', value: `${highHR}`, change: 'HR > 100 bpm' },
      { label: 'Total Records', value: `${this.allData.length}`, change: 'uploaded' },
    ]
  }

  generatePatientList() {
    const deviceGroups = {}
    this.allData.forEach(record => {
      const device = record.device || 'Unknown Device'
      if (!deviceGroups[device]) {
        deviceGroups[device] = []
      }
      deviceGroups[device].push(record.heartRate || 0)
    })

    this.patients = Object.entries(deviceGroups).map(([device, hrs]) => {
      const avgHR = Math.round(hrs.reduce((a, b) => a + b, 0) / hrs.length)
      const maxHR = Math.max(...hrs)
      const status = maxHR > 110 ? 'alert' : maxHR > 90 ? 'watch' : 'stable'
      
      return {
        name: device,
        device: device,
        status: status,
        lastSync: 'from upload',
        hr: avgHR
      }
    })
  }

  getSections() {
    return this.sections
  }

  getReadings() {
    return this.readings
  }

  getPatients() {
    return this.patients
  }

  getUploads() {
    return this.uploads
  }

  getUploadedData() {
    return this.uploadedData
  }

  addUpload(file) {
    this.uploads.unshift(file)
  }

  setUploadedData(data) {
    this.uploadedData = data
  }
}
