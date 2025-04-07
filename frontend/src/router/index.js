import { createRouter, createWebHistory } from 'vue-router'
import HomeView from '../views/HomeView.vue'
import { useAuth0 } from '@auth0/auth0-vue'

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
  // Check if the route requires authentication
  if (to.matched.some((record) => record.meta.requiresAuth)) {
    const { isAuthenticated, user } = useAuth0()

    // If not authenticated, redirect to home page
    if (!isAuthenticated.value) {
      next({ name: 'home' })
      return
    }

    // If route requires admin role, check if user has admin role
    if (to.matched.some((record) => record.meta.requiresAdmin)) {
      // Wait for user object to be available
      if (!user.value) {
        // This could happen if user info is still loading
        // You might want to show a loading state or handle differently
        next(false)
        return
      }

      const userRoles = user.value['https://hangoutsg.com/roles'] || []
      if (!userRoles.includes('admin')) {
        // If user is not an admin, redirect to home page
        next({ name: 'not-found' })
        return
      }
    }
  }

  // Proceed as normal
  next()
})

export default router
