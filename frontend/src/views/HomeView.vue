<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()
const errorMessage = ref('')
const communities = ref([])
const isLoading = ref(true)

// Navigate to community page
const navigateToCommunity = (communityName) => {
  router.push(`/c/${communityName}`)
}

// Fetch all communities
const fetchCommunities = async () => {
  try {
    isLoading.value = true
    const response = await fetch('http://localhost:5001/api/community')

    if (!response.ok) {
      throw new Error(`HTTP error! Status: ${response.status}`)
    }

    const data = await response.json()
    communities.value = data.data.communities
  } catch (err) {
    console.error('Error fetching communities:', err)
  } finally {
    isLoading.value = false
  }
}

onMounted(() => {
  // Check for error params
  const urlParams = new URLSearchParams(window.location.search)
  const error = urlParams.get('error')
  const errorDescription = urlParams.get('error_description')

  if (error === 'unauthorized' && errorDescription?.includes('user is blocked')) {
    errorMessage.value =
      'Your account has been banned. Please check your email for more information!'
  }

  // Fetch communities
  fetchCommunities()
})
</script>

<template>
  <div v-if="errorMessage" class="error-alert">
    <span>{{ errorMessage }}</span>
  </div>

  <h1 class="heading">Home</h1>
  <p>
    Looking to join a community? Discover exciting HangoutSG events happening near you! Explore a
    wide range of hobbies and meet fellow enthusiasts. Find your next adventure today!
  </p>

  <hr />

  <div v-if="isLoading" class="text-center my-5">
    <div class="spinner-border" role="status">
      <span class="visually-hidden">Loading communities...</span>
    </div>
  </div>

  <!-- Communities grid -->
  <div v-else class="communities-grid">
    <div
      v-for="community in communities"
      :key="community.id"
      class="community-card"
      @click="navigateToCommunity(community.name)"
    >
      <div class="card-img-top" :style="{ backgroundColor: getRandomColor(community.name) }">
        <span class="community-initial">{{ community.name.charAt(0) }}</span>
      </div>
      <div class="card-body">
        <h3 class="card-title">{{ community.name }}</h3>
        <p class="card-text">{{ truncateDescription(community.description, 100) }}</p>
        <div class="community-stats">
          <span><i class="bi bi-people-fill"></i> {{ community.members_count || 0 }} members</span>
          <span><i class="bi bi-calendar-event"></i> {{ community.events_count || 0 }} events</span>
        </div>
      </div>
    </div>
  </div>
  <div v-if="communities.length === 0 && !isLoading" class="text-center p-4 text-muted">
    No communities found. Why not create one?
  </div>
</template>

<style scoped>
.communities-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 1.5rem;
  margin-top: 2rem;
}

.community-card {
  border-radius: 8px;
  overflow: hidden;
  box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
  transition: transform 0.3s ease, box-shadow 0.3s ease;
  cursor: pointer;
  background-color: white;
  height: 100%;
}

.community-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 5px 15px rgba(0, 0, 0, 0.1);
}

.card-img-top {
  height: 120px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.community-initial {
  font-size: 3rem;
  font-weight: bold;
  color: white;
}

.card-body {
  padding: 1.25rem;
}

.card-title {
  font-size: 1.25rem;
  margin-bottom: 0.75rem;
  font-weight: 600;
}

.card-text {
  color: #6c757d;
  margin-bottom: 1rem;
}

.community-stats {
  display: flex;
  justify-content: space-between;
  font-size: 0.875rem;
  color: #6c757d;
}

.lead {
  font-size: 1.1rem;
  margin-bottom: 1.5rem;
}
</style>

<script>
// Helper functions
export function getRandomColor(seed) {
  // Generate a consistent color based on the community name
  let hash = 0
  for (let i = 0; i < seed.length; i++) {
    hash = seed.charCodeAt(i) + ((hash << 5) - hash)
  }

  const colors = [
    '#4285f4',
    '#ea4335',
    '#fbbc05',
    '#34a853',
    '#673ab7',
    '#3f51b5',
    '#2196f3',
    '#009688',
    '#ff5722',
  ]

  return colors[Math.abs(hash) % colors.length]
}

export function truncateDescription(text, maxLength) {
  if (!text) return ''
  return text.length > maxLength ? text.substring(0, maxLength) + '...' : text
}
</script>