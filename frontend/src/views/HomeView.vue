<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import CommunityCard from '@/components/CommunityCard.vue'

const router = useRouter()
const errorMessage = ref('')
const communities = ref([])
const isLoading = ref(true)
const sortOrder = ref('newest')

const sortedCommunities = computed(() => {
  if (!communities.value.length) return []

  return [...communities.value].sort((a, b) => {
    const dateA = new Date(a.created_at)
    const dateB = new Date(b.created_at)

    return sortOrder.value === 'newest'
      ? dateB - dateA // Newest first
      : dateA - dateB // Oldest first
  })
})

// Function to change sort order
const changeSortOrder = (order) => {
  sortOrder.value = order
}

// Navigate to community page
const navigateToCommunity = (communityName) => {
  router.push(`/c/${communityName}`)
}

// Fetch member count for a specific community
const fetchMemberCount = async (communityId) => {
  try {
    const response = await fetch(
      `https://personal-iw6ceuuv.outsystemscloud.com/Community_members/rest/CommunityMemberAPI/membersbycommunity/${communityId}`
    )

    if (!response.ok) {
      throw new Error(`HTTP error! Status: ${response.status}`)
    }

    const data = await response.json()

    // Check if there's an error message indicating no members
    if (data.Result && data.Result.ErrorMessage === 'No Members Found') {
      return 0
    }

    // Otherwise count the members in the array
    return data.CommunityMemberAPI ? data.CommunityMemberAPI.length : 0
  } catch (err) {
    console.error(`Error fetching member count for community ${communityId}:`, err)
    return 0
  }
}

// Fetch event count for a specific community
const fetchEventCount = async (communityId) => {
  try {
    const response = await fetch(`http://localhost:5004/events/community/${communityId}`)

    if (!response.ok) {
      throw new Error(`HTTP error! Status: ${response.status}`)
    }

    const data = await response.json()
    return Array.isArray(data) ? data.length : 0
  } catch (err) {
    console.error(`Error fetching event count for community ${communityId}:`, err)
    return 0
  }
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
    const communitiesData = data.data.communities
    // Fetch member counts and event counts for each community
    const communitiesWithCounts = await Promise.all(
      communitiesData.map(async (community) => {
        const memberCount = await fetchMemberCount(community.community_id)
        const eventCount = await fetchEventCount(community.community_id)
        return {
          ...community,
          memberCount,
          eventCount,
        }
      })
    )

    communities.value = communitiesWithCounts
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

  <div class="sort-controls mb-3">
    <span class="me-2">Sort by:</span>
    <div class="btn-group">
      <button
        @click="changeSortOrder('newest')"
        :class="['btn', 'btn-sm', sortOrder === 'newest' ? 'btn-dark' : 'btn-outline-dark']"
      >
        Newest
      </button>
      <button
        @click="changeSortOrder('oldest')"
        :class="['btn', 'btn-sm', sortOrder === 'oldest' ? 'btn-dark' : 'btn-outline-dark']"
      >
        Oldest
      </button>
    </div>
  </div>

  <div v-if="isLoading" class="text-center my-5">
    <div class="spinner-border" role="status">
      <span class="visually-hidden"></span>
    </div>
    <p class="mt-2 text-muted">Loading Communities...</p>
  </div>

  <!-- Communities grid -->
  <div v-else class="communities-grid">
    <CommunityCard
      v-for="community in sortedCommunities"
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

.sort-controls {
  display: flex;
  align-items: center;
  justify-content: flex-end;
}
</style>