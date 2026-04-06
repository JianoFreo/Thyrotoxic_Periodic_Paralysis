import { render, screen, waitFor } from '@testing-library/react'
import { afterEach, describe, expect, it, vi } from 'vitest'
import App from './App'

const makeRecord = (overrides = {}) => ({
  user_id: 'user-1',
  timestamp: '2026-04-07T10:00:00.000Z',
  heart_rate: 138,
  hrv: 18,
  steps: 5,
  ...overrides,
})

afterEach(() => {
  vi.restoreAllMocks()
})

describe('Dashboard frontend behavior without smartwatch hardware', () => {
  it('renders metrics and uses local fallback prediction when prediction API is unavailable', async () => {
    const records = [makeRecord(), makeRecord({ heart_rate: 142, timestamp: '2026-04-07T10:05:00.000Z' })]

    const fetchMock = vi.spyOn(global, 'fetch').mockImplementation(async (url) => {
      if (url === '/api/data') {
        return {
          ok: true,
          json: async () => ({ data: records }),
        }
      }

      if (url === '/api/v1/predict/realtime') {
        return {
          ok: false,
          status: 503,
          json: async () => ({ error: 'offline' }),
        }
      }

      throw new Error(`Unexpected request: ${url}`)
    })

    render(<App />)

    await waitFor(() => {
      const recordsMetricCard = screen.getByText('Records Processed').closest('.metric-card')
      expect(recordsMetricCard).not.toBeNull()
      expect(recordsMetricCard.querySelector('.metric-value')).toHaveTextContent('2')
    })

    expect(screen.getByText('Predicted TPP Risk')).toBeInTheDocument()
    expect(screen.getByText('95%')).toBeInTheDocument()
    expect(screen.getByText('CRITICAL')).toBeInTheDocument()
    expect(screen.getByText('0-3 hours')).toBeInTheDocument()
    expect(screen.getByText('Critical Risk Detected')).toBeInTheDocument()
    expect(fetchMock).toHaveBeenCalled()
  })

  it('shows a readable frontend error when wearable records cannot be fetched', async () => {
    vi.spyOn(global, 'fetch').mockResolvedValue({
      ok: false,
      status: 500,
      json: async () => ({ error: 'backend down' }),
    })

    render(<App />)

    await waitFor(() => {
      expect(screen.getByText('Failed to fetch wearable records from backend')).toBeInTheDocument()
    })
  })
})
