import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import { RouterProvider } from '@tanstack/react-router'
import { router } from './router'
import '@pages/_init'
import '@styles/globals.css'

createRoot(document.getElementById('root')!)
  .render(
    <StrictMode>
      <RouterProvider router={router} />
    </StrictMode>
  )

