// Main App Class - Orchestrates everything
class TPPApp {
  constructor(rootElement) {
    this.root = rootElement
    this.activeSection = 'overview'
    this.dataManager = new DataManager()
    this.renderer = new Renderer(this.dataManager)
    this.fileUploader = new FileUploader(this.dataManager)
  }

  attachTabHandlers() {
    const buttons = this.root.querySelectorAll('[data-section]')
    buttons.forEach((btn) => {
      btn.addEventListener('click', () => {
        const target = btn.getAttribute('data-section')
        if (target) {
          this.activeSection = target
          this.render()
        }
      })
    })

    this.fileUploader.attachHandlers((count, fileName) => {
      this.render()
      alert(`Successfully uploaded ${count} records from ${fileName}`)
    })
  }

  render() {
    this.renderer.render(this.root, this.activeSection)
    this.attachTabHandlers()
  }

  init() {
    this.render()
  }
}
