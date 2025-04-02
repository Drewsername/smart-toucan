import { createFileRoute } from '@tanstack/react-router'
import '../styles/app.css'
import { ColorTest } from '../components/ColorTest'

export const Route = createFileRoute('/')({
  component: Home,
})

function Home() {
  return (
    <div className="p-2">
      <h3>Welcome Home!!!</h3>
      <ColorTest />
    </div>
  )
}
