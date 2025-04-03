<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import CommunityCard from '@/components/CommunityCard.vue'

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
      <span class="visually-hidden"></span>
    </div>
    <p class="mt-2 text-muted">Loading Communities...</p>
  </div>

  <!-- Communities grid -->
  <div v-else class="communities-grid">
    <CommunityCard
      v-for="community in communities"
      :key="community.id"
      :community="community"
      @click="navigateToCommunity(community.name)"
    />
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

.lead {
  font-size: 1.1rem;
  margin-bottom: 1.5rem;
}
</style>