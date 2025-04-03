<script setup>
import { ref, watch, onMounted, onUnmounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import CommunityPost from '../components/CommunityPost.vue'

const route = useRoute()
const router = useRouter()
const community = ref({})
const posts = ref([])
const isLoading = ref(true)
const error = ref(null)
const refreshInterval = ref(null)
const refreshRate = ref(30000) // 30 seconds by default
const isRefreshing = ref(false)

const isJoined = ref(false)
const toggleJoinLeave = () => {
  isJoined.value = !isJoined.value
}

const createPost = () => {
  router.push(`/c/${route.params.community}/create`)
}

const viewEvents = () => {
  // Placeholder for events functionality
  router.push(`/c/${route.params.community}/events`)
}

const goToPost = (postId) => {
  router.push(`/post/${postId}`)
}

const fetchCommunityData = async () => {
  try {
    error.value = null
    const communityName = route.params.community
    
    if (!communityName) {
      error.value = "No community specified"
      isLoading.value = false
      return
    }
    
    const response = await fetch(`http://localhost:5001/api/community/name/${communityName}`)

    if (!response.ok) {
      throw new Error(`HTTP error! Status: ${response.status}`)
    }

    const data = await response.json()
    community.value = data.data
  } catch (err) {
    console.error('Error fetching community data:', err)
    error.value = "Community doesn't exist!"
    isLoading.value = false
  }
}

const fetchPosts = async () => {
  try {
    if (!community.value || !community.value.community_id) return
    
    isRefreshing.value = true
    const response = await fetch(`http://localhost:5002/api/posts/community/${community.value.community_id}`)
    
    if (!response.ok) {
      throw new Error(`HTTP error! Status: ${response.status}`)
    }
    
    const data = await response.json()
    posts.value = data.data.posts
    isLoading.value = false
    isRefreshing.value = false
  } catch (err) {
    console.error('Error fetching posts:', err)
    isRefreshing.value = false
  }
}

const startAutoRefresh = () => {
  stopAutoRefresh() // Clear any existing interval first
  refreshInterval.value = setInterval(fetchPosts, refreshRate.value)
}

const stopAutoRefresh = () => {
  if (refreshInterval.value) {
    clearInterval(refreshInterval.value)
    refreshInterval.value = null
  }
}

const updateRefreshRate = (seconds) => {
  refreshRate.value = seconds * 1000
  startAutoRefresh() // Restart with new rate
}

const loadInitialData = async () => {
  isLoading.value = true
  await fetchCommunityData()
  await fetchPosts()
  startAutoRefresh()
}

watch(
  () => route.params.community,
  (newCommunity) => {
    if (newCommunity) {
      loadInitialData()
    }
  }
)

onMounted(() => {
  loadInitialData()
})

onUnmounted(() => {
  stopAutoRefresh()
})
</script>

<template>
  <div v-if="isLoading" class="text-center my-5">
    <div class="spinner-border" role="status">
      <span class="visually-hidden">Loading...</span>
    </div>
  </div>

  <div v-else-if="error" class="alert alert-danger" role="alert">
    {{ error }}
  </div>

  <div v-else>
    <!-- Mobile-friendly header section -->
    <div class="community-header">
      <h1 class="heading mb-3">{{ community.name }}</h1>

      <!-- Action buttons - stack vertically on mobile -->
      <div class="action-buttons">
        <button @click="viewEvents" class="btn btn-dark me-2 mb-2">
          <i class="bi bi-calendar-event"></i> View Events
        </button>
        <button @click="createPost" class="btn btn-dark me-2 mb-2">
          <i class="bi bi-plus-lg"></i> Create Post
        </button>
        <button @click="toggleJoinLeave" class="btn btn-primary mb-2">
          {{ isJoined ? 'Leave' : 'Join' }}
        </button>
      </div>
    </div>

    <p>{{ community.description }}</p>
    
    <!-- Auto-refresh control -->
    <div class="refresh-controls mb-3">
      <div class="d-flex align-items-center">
        <span class="me-2">Auto-refresh:</span>
        <select v-model="refreshRate" @change="updateRefreshRate(refreshRate/1000)" class="form-select form-select-sm" style="width: auto">
          <option :value="10000">10 seconds</option>
          <option :value="30000">30 seconds</option>
          <option :value="60000">1 minute</option>
          <option :value="300000">5 minutes</option>
        </select>
        <button @click="fetchPosts" class="btn btn-sm btn-outline-secondary ms-2" :disabled="isRefreshing">
          <i class="bi bi-arrow-clockwise" :class="{'rotating': isRefreshing}"></i> 
          {{ isRefreshing ? 'Refreshing...' : 'Refresh Now' }}
        </button>
      </div>
      <div class="text-muted small mt-1" v-if="posts.length > 0">
        Last updated: {{ new Date().toLocaleTimeString() }}
      </div>
    </div>
    
    <hr />
    
    <!-- Posts section with empty state -->
    <div v-if="posts.length === 0" class="text-center my-4">
      <p class="text-muted">No posts in this community yet.</p>
      <button @click="createPost" class="btn btn-primary">Create the first post</button>
    </div>
    
    <div v-else class="list-group">
      <CommunityPost 
        v-for="post in posts"
        :key="post.post_id"
        :post="post"
        @click="goToPost(post.post_id)"
      />
    </div>
  </div>
</template>

<style scoped>
.btn {
  border-radius: 15px;
}

.refresh-controls {
  background-color: #f8f9fa;
  padding: 10px;
  border-radius: 8px;
}

@keyframes rotating {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

.rotating {
  animation: rotating 1s linear infinite;
}

/* Responsive styles */
.community-header {
  display: flex;
  flex-direction: column;
  margin-bottom: 1rem;
}

.action-buttons {
  display: flex;
  flex-wrap: wrap;
}

/* Apply these styles for screens larger than 768px (tablets and up) */
@media (min-width: 768px) {
  .community-header {
    flex-direction: row;
    justify-content: space-between;
    align-items: center;
  }
  
  .action-buttons {
    flex-wrap: nowrap;
  }
  
  .btn {
    margin-bottom: 0 !important;
  }
}

/* Optional: Add a minor adjustment for even smaller screens */
@media (max-width: 480px) {
  .action-buttons {
    width: 100%;
  }
  
  .action-buttons .btn {
    flex-grow: 1;
    font-size: 0.875rem;
    padding: 0.375rem 0.5rem;
  }
}
</style>