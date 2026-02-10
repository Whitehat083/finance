import { render, screen } from '@testing-library/react'
import App from './App'

test('renders title and modules', () => {
  render(<App />)
  expect(screen.getByText('Educa Finance')).toBeInTheDocument()
  expect(screen.getByText('Trilha de aprendizado')).toBeInTheDocument()
  expect(screen.getByText(/Conceito de orçamento/)).toBeInTheDocument()
})
