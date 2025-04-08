import { createRouter, createWebHistory } from 'vue-router'
import HomeView from '../views/HomeView.vue'
import { useAuth0 } from '@auth0/auth0-vue'
import { watch } from 'vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'home',
      component: HomeView,
    },
    {
      path: '/events',
      name: 'events',
      component: () => import('../views/EventsView.vue'),
    },
    {
      path: '/events/:community',
      name: 'events-community',
      component: () => import('../views/EventsView.vue'),
    },
    {
      path: '/events-event',
      name: 'events-event',
      component: () => import('../views/CreateEventView.vue'),
      meta: {
        requiresAuth: true,
      },
    },
    {
      path: '/profile',
      name: 'profile',
      component: () => import('../views/ProfileView.vue'),
      meta: {
        requiresAuth: true,
      },
    },
    {
      path: '/inbox',
      name: 'inbox',
      component: () => import('../views/InboxView.vue'),
      meta: {
        requiresAuth: true,
      },
    },
    {
      path: '/communities/create',
      name: 'createcommunity',
      component: () => import('../views/CreateCommunityView.vue'),
      meta: {
        requiresAuth: true,
      },
    },
    {
      path: '/admin',
      name: 'admin',
      component: () => import('../views/AdminView.vue'),
      meta: {
        requiresAuth: true,
        requiresAdmin: true,
      },
    },
    {
      path: '/c/:community',
      name: 'community',
      component: () => import('../views/CommunityView.vue'),
    },
    {
      path: '/c/:community/create',
      name: 'createpost',
      component: () => import('../views/CreatePostView.vue'),
      meta: {
        requiresAuth: true,
      },
    },
    {
      path: '/:pathMatch(.*)*',
      name: 'not-found',
      component: () => import('../views/NotFoundView.vue'),
    },
    {
      path: '/post/:postId',
      name: 'PostDetail',
      component: () => import('../views/PostView.vue'),
    },
  ],
})

// Add navigation guard
router.beforeEach(async (to, from, next) => {
  const { user, isAuthenticated, isLoading } = useAuth0()

  // Check if we need authentication for this route
  const requiresAuth = to.matched.some((record) => record.meta.requiresAuth === true)
  const requiresAdmin = to.matched.some((record) => record.meta.requiresAdmin === true)
  
  if (!requiresAuth) {
    return next()
  }
  
  if (isLoading.value) {
    try {
      await new Promise((resolve, reject) => {
        const watchStop = watch(isLoading, (loading) => {
          if (loading === false) {
            watchStop()
            resolve()
          }
        })
        
        // Add timeout to avoid infinite waiting
        setTimeout(() => {
          watchStop()
          reject(new Error('Auth loading timeout'))
        }, 10000)
      })
    } catch (error) {
      console.error('Auth loading error:', error)
      return next('/')
    }
  }
  
  // Now check authentication
  if (!isAuthenticated.value && requiresAuth) {
    return next('/')
  }

  // Check admin role for routes that require it
  if (requiresAdmin) {
    const userRoles = user.value['https://hangoutsg.com/roles'] || []
    if (!userRoles.includes('admin')) {
      console.log('Access denied: Admin role required')
      return next('/')  // Redirect to home or you could create an access denied page
    }
  }
  
  return next()
})

export default router
