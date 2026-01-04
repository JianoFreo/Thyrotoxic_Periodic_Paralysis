// Data Manager - Handles all data storage and retrieval
class DataManager {
  constructor() {
    this.sections = [
      { key: 'overview', label: 'Overview' },
      { key: 'monitoring', label: 'Patient Monitoring' },
      { key: 'upload', label: 'Data Upload' },
      { key: 'insights', label: 'Model Insights' },
      { key: 'settings', label: 'Settings' },
    ]

    this.readings = [
      { label: 'Avg Resting HR', value: '72 bpm', change: '+3 vs last week' },
      { label: 'Nocturnal HRV', value: '58 ms', change: 'stable' },
      { label: 'Episodes Flagged', value: '2 in 24h', change: 'watch' },
      { label: 'Sync Health', value: '96% of devices' },
    ]

    this.patients = [
      { name: 'Sam R.', device: 'Apple Watch', status: 'watch', lastSync: '6 min ago', hr: 102 },
      { name: 'Avery L.', device: 'Fitbit', status: 'stable', lastSync: '18 min ago', hr: 76 },
      { name: 'Dana K.', device: 'Galaxy Watch', status: 'alert', lastSync: '2 min ago', hr: 118 },
    ]

    this.uploads = [
      { name: 'Watch HR JSON', size: '2.4 MB', time: 'just now' },
      { name: 'Clinical lab CSV', size: '640 KB', time: '1h ago' },
      { name: 'Manual note', size: '2 KB', time: 'yesterday' },
    ]

    this.uploadedData = []
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
