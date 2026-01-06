// UI Helper - Loading states and notifications
class UIHelper {
  static showLoading(message = 'Processing...') {
    const existing = document.getElementById('loading-overlay')
    if (existing) return

    const overlay = document.createElement('div')
    overlay.id = 'loading-overlay'
    overlay.className = 'loading-overlay'
    overlay.innerHTML = `
      <div class="loading-content">
        <div class="loading-spinner"></div>
        <p>${message}</p>
      </div>
    `
    document.body.appendChild(overlay)
  }

  static hideLoading() {
    const overlay = document.getElementById('loading-overlay')
    if (overlay) {
      overlay.remove()
    }
  }

  static showToast(message, type = 'info', duration = 3000) {
    const toast = document.createElement('div')
    toast.className = `toast ${type}`
    
    const icons = {
      success: '✓',
      error: '✕',
      info: 'ℹ'
    }

    toast.innerHTML = `
      <span class="toast-icon">${icons[type] || icons.info}</span>
      <div class="toast-message">${message}</div>
      <button class="toast-close">×</button>
    `

    document.body.appendChild(toast)

    const closeBtn = toast.querySelector('.toast-close')
    const close = () => {
      toast.style.animation = 'slideIn 0.3s ease reverse'
      setTimeout(() => toast.remove(), 300)
    }

    closeBtn.addEventListener('click', close)
    
    if (duration > 0) {
      setTimeout(close, duration)
    }
  }

  static setDropzoneState(uploading) {
    const dropzone = document.getElementById('dropzone')
    if (dropzone) {
      if (uploading) {
        dropzone.classList.add('uploading')
      } else {
        dropzone.classList.remove('uploading')
      }
    }
  }
}
