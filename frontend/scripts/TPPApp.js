// Main App Class - Orchestrates everything
class TPPApp {
  constructor(rootElement) {
    this.root = rootElement //this = javascript, self = python
    this.activeSection = 'overview'
    this.dataManager = new DataManager()
    this.renderer = new Renderer(this.dataManager)
    this.fileUploader = new FileUploader(this.dataManager)
  }

  attachTabHandlers() { // These are the methods that make the buttons work
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

    this.fileUploader.attachHandlers(async (count, fileName) => {
      await this.dataManager.fetchDataFromBackend()
      this.render()
    })
  }

  render() { // This method draws the page based on the active section
    this.renderer.render(this.root, this.activeSection)
    this.attachTabHandlers()
  }

  async init() { // This method starts the app, it calls render to draw the initial page
    await this.dataManager.fetchDataFromBackend()
    this.render()
  }
}
