import { createRouter, createWebHistory } from 'vue-router'
import HomeView from '../views/HomeView.vue'
import ReportDetails from '../components/ReportDetails.vue' 

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
      path: '/profile',
      name: 'profile',
      component: () => import('../views/ProfileView.vue'),
    },
    {
      path: '/inbox',
      name: 'inbox',
      component: () => import('../views/InboxView.vue'),
    },
    {
      path: '/communities/create',
      name: 'createcommunity',
      component: () => import('../views/CreateCommunityView.vue'),
    },
    {
      path: '/admin',
      name: 'admin',
      component: () => import('../views/AdminView.vue'),
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
    // Add the report-details route and use the imported ReportDetails component
    {
      path: '/report/:reportId',
      name: 'report-details',
      component: () => import('../components/ReportDetails.vue'),  // Reference the imported component
      props: true,  // Pass the route params as props to the component
    },
  ],
})

export default router
