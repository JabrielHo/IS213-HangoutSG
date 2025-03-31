<script setup>
import { ref, watch, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import CommunityPost from '../components/CommunityPost.vue'

const route = useRoute()
const router = useRouter()
const community = ref({})
const isLoading = ref(true)
const error = ref(null)

const isJoined = ref(false)
const toggleJoinLeave = () => {
  isJoined.value = !isJoined.value
}

const createPost = () => {
  router.push(`/c/${route.params.community}/create`)
}

const fetchCommunityData = async () => {
  try {
    isLoading.value = true
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
    isLoading.value = false
  } catch (err) {
    console.error('Error fetching community data:', err)
    error.value = "Community doesn't exist!"
    isLoading.value = false
  }
}

watch(
  () => route.params.community,
  (newCommunity) => {
    if (newCommunity) {
      fetchCommunityData()
    }
  }
)

onMounted(() => {
  fetchCommunityData()
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
    <hr />

    <div class="list-group">
      <CommunityPost />
    </div>
  </div>
</template>

<style scoped>
.btn {
  border-radius: 15px;
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