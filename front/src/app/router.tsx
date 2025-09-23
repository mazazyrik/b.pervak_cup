import { createRootRoute, createRoute, createRouter, Outlet } from '@tanstack/react-router'
import { Home } from '@pages/Home'
import { Camera } from '@pages/Camera'
import { Feed } from '@pages/Feed'
import { ThemeProvider } from '@app/providers/ThemeProvider'
import { QueryProvider } from '@app/providers/QueryProvider'
import { Toaster } from 'sonner'
import { AuthBootstrap } from '@entities/user/model/AuthBootstrap'
import { AppShell } from '@shared/ui/AppShell'
import { Guess } from '@pages/Guess'
import { PostSuccess } from '@pages/PostSuccess'
import { Post } from '@pages/Post'
import { Moderation } from '@pages/Moderation'
import { AppPreloader } from '@shared/ui/AppPreloader'

const Root = () => (
  <ThemeProvider>
    <QueryProvider>
      <AuthBootstrap />
      <AppPreloader />
      <AppShell>
        <Outlet />
      </AppShell>
      <Toaster richColors position='top-center' />
    </QueryProvider>
  </ThemeProvider>
)

const rootRoute = createRootRoute({ component: Root })

const homeRoute = createRoute({ getParentRoute: () => rootRoute, path: '/', component: Home })
const cameraRoute = createRoute({ getParentRoute: () => rootRoute, path: '/camera', component: Camera })
const feedRoute = createRoute({ getParentRoute: () => rootRoute, path: '/feed', component: Feed })

const guessRoute = createRoute({ getParentRoute: () => rootRoute, path: '/guess', component: Guess })
const successRoute = createRoute({ getParentRoute: () => rootRoute, path: '/success', component: PostSuccess })
const postRoute = createRoute({ getParentRoute: () => rootRoute, path: '/post/$postId', component: Post })
const moderationRoute = createRoute({ getParentRoute: () => rootRoute, path: '/moderation', component: Moderation })
const routeTree = rootRoute.addChildren([homeRoute, cameraRoute, feedRoute, guessRoute, successRoute, postRoute, moderationRoute])

export const router = createRouter({ routeTree })
declare module '@tanstack/react-router' {
  interface Register {
    router: typeof router
  }
}

