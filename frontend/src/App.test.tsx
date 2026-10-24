import '@testing-library/jest-dom'
import { render, screen } from '@testing-library/react'
import App from './App'
import { vi } from 'vitest'

vi.stubGlobal('fetch', vi.fn(async (url: string) => ({ ok: true, json: async () => url === '/api/demos' ? [] : [] })))
test('shows source document workspace', async () => {
  render(<App />)
  expect(screen.getByText('Regulatory change impact')).toBeInTheDocument()
  expect(screen.getByText('Source documents')).toBeInTheDocument()
  expect(screen.getByRole('button', { name: /create impact report/i })).toBeDisabled()
})
