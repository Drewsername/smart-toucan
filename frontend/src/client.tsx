// src/client.tsx
/// <reference types="vinxi/types/client" />
import './styles/app.css'
import { hydrateRoot } from 'react-dom/client'
import { StartClient } from '@tanstack/react-start'
import { createRouter } from './router'

const router = createRouter()

/**
 * Hydrates the React application on the client side
 */
function hydrateApplication() {
  hydrateRoot(document, <StartClient router={router} />)
}

// Initialize hydration
hydrateApplication()

/**
 * Default export function that matches the existing hydration logic
 * Can be imported and used in other files if needed
 */
export default function hydrate() {
  return <StartClient router={router} />
}
