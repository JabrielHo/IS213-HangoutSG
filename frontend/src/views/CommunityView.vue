<script setup>
import { ref, watch, onMounted, onUnmounted, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuth0 } from '@auth0/auth0-vue'
import CommunityPost from '../components/CommunityPost.vue'

const route = useRoute()
const router = useRouter()
const { user, isAuthenticated } = useAuth0()

const community = ref({})
const posts = ref([])
const isLoading = ref(true)
const error = ref(null)
const refreshInterval = ref(null)
const refreshRate = ref(30000) // 30 seconds by default
const isRefreshing = ref(false)
const sortOrder = ref('newest')

const isJoined = ref(false)
const isJoinLeaveLoading = ref(false)
const joinLeaveError = ref(null)

const sortedPosts = computed(() => {
  if (!posts.value.length) return []

  // First filter out unpublished posts
  const publishedPosts = posts.value.filter((post) => post.status !== 'unpublished')

  // Then sort the remaining posts
  return publishedPosts.sort((a, b) => {
    const dateA = new Date(a.created_at)
    const dateB = new Date(b.created_at)

    return sortOrder.value === 'newest'
      ? dateB - dateA // Newest first
      : dateA - dateB // Oldest first
  })
})

const changeSortOrder = (order) => {
  sortOrder.value = order
}

const checkMembershipStatus = async () => {
  if (!isAuthenticated.value || !user.value || !community.value.community_id) {
    return
  }

  try {
    const response = await fetch(
      `https://personal-iw6ceuuv.outsystemscloud.com/Community_members/rest/CommunityMemberAPI/getmember/${community.value.community_id}/${user.value.sub}`
    )

    if (response.ok) {
      const data = await response.json()

      if (data.Result && data.Result.ErrorMessage === 'Member Not Found') {
        isJoined.value = false
      } else if (
        data.Result &&
        data.Result.Success === true &&
        data.CommunityMemberAPI.status === 'joined'
      ) {
        isJoined.value = true
      } else {
        isJoined.value = false
      }
    } else {
      isJoined.value = false
    }
  } catch (err) {
    console.error('Error checking membership status:', err)
    isJoined.value = false
  }
}

const toggleJoinLeave = async () => {
  if (!isAuthenticated.value || !user.value || !community.value.community_id) return

  isJoinLeaveLoading.value = true
  joinLeaveError.value = null

  try {
    if (!isJoined.value) {
      // Join the community
      const joinResponse = await fetch(
        `https://personal-iw6ceuuv.outsystemscloud.com/Community_members/rest/CommunityMemberAPI/communityaddmember/${community.value.community_id}/${user.value.sub}`,
        {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
        }
      )

      if (!joinResponse.ok) {
        throw new Error(`Failed to join community: ${joinResponse.status}`)
      }

      isJoined.value = true
    } else {
      const leaveResponse = await fetch(
        `https://personal-iw6ceuuv.outsystemscloud.com/Community_members/rest/CommunityMemberAPI/updatestatus/${community.value.community_id}/${user.value.sub}`,
        {
          method: 'PUT',
          headers: {
            'Content-Type': 'application/json',
          },
        }
      )

      if (!leaveResponse.ok) {
        throw new Error(`Failed to leave community: ${leaveResponse.status}`)
      }

      isJoined.value = false
    }
  } catch (err) {
    console.error('Error toggling community membership:', err)
    joinLeaveError.value = `Failed to ${
      isJoined.value ? 'leave' : 'join'
    } community. Please try again.`
  } finally {
    isJoinLeaveLoading.value = false
  }
}

const createPost = () => {
  router.push(`/c/${route.params.community}/create`)
}

const viewEvents = () => {
  router.push(`/events/${community.value.name}`)
}
const goToPost = (postId) => {
  router.push(`/post/${postId}`)
}

const fetchCommunityData = async () => {
  try {
    error.value = null
    const communityName = route.params.community

    if (!communityName) {
      error.value = 'No community specified'
      isLoading.value = false
      return
    }

    const response = await fetch(`http://localhost:8000/api/community/name/${communityName}`)

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

    // Step 1: Fetch posts and immediately display them
    const response = await fetch(
      `http://localhost:8000/api/posts/community/${community.value.community_id}`
    )

    if (!response.ok) {
      throw new Error(`HTTP error! Status: ${response.status}`)
    }

    const data = await response.json()
    let postsWithUserInfo = data.data.posts.map((post) => ({
      ...post,
      username: 'Loading...',
      commentCount: 0,
    }))

    // Update UI immediately with basic post data
    posts.value = postsWithUserInfo

    // Then fetch additional data in parallel
    const uniqueAuthorIds = [...new Set(postsWithUserInfo.map((post) => post.author_id))]
    const postIds = postsWithUserInfo.map((post) => post.post_id)

    // Fetch user data and comment counts in parallel
    const [userDataMap, commentCountMap] = await Promise.all([
      fetchUserData(uniqueAuthorIds),
      fetchCommentCounts(postIds),
    ])

    // Update posts with additional data
    posts.value = posts.value.map((post) => {
      const userData = userDataMap[post.author_id]
      return {
        ...post,
        username: userData ? userData.username : 'Unknown User',
        commentCount: commentCountMap[post.post_id] || 0,
      }
    })

    isRefreshing.value = false
  } catch (err) {
    console.error('Error fetching posts:', err)
    isRefreshing.value = false
  }
}

// Helper functions to fetch data
const fetchUserData = async (userIds) => {
  const userDataMap = {}
  await Promise.all(
    userIds.map(async (userId) => {
      try {
        const userResponse = await fetch(`http://localhost:8000/api/users/${userId}`)
        if (userResponse.ok) {
          const userData = await userResponse.json()
          userDataMap[userId] = userData.data
        }
      } catch (error) {
        console.error(`Error fetching user data for ${userId}:`, error)
      }
    })
  )
  return userDataMap
}

const fetchCommentCounts = async (postIds) => {
  const commentCountMap = {}
  await Promise.all(
    postIds.map(async (postId) => {
      try {
        const commentResponse = await fetch(`http://localhost:8000/api/comments/post/${postId}`)
        if (commentResponse.ok) {
          const commentData = await commentResponse.json()
          commentCountMap[postId] = commentData.data.comments
            ? commentData.data.comments.filter((comment) => comment.status !== 'unpublished').length
            : 0
        }
      } catch (error) {
        console.error(`Error fetching comment count for post ${postId}:`, error)
        commentCountMap[postId] = 0
      }
    })
  )
  return commentCountMap
}

const startAutoRefresh = () => {
  stopAutoRefresh()
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
  startAutoRefresh()
}

const loadInitialData = async () => {
  isLoading.value = true

  try {
    await fetchCommunityData()

    if (isAuthenticated.value) {
      await Promise.all([fetchPosts(), checkMembershipStatus()])
    } else {
      await fetchPosts()
    }

    startAutoRefresh()
  } catch (err) {
    console.error('Error loading initial data:', err)
  } finally {
    isLoading.value = false
  }
}

watch(
  () => route.params.community,
  (newCommunity) => {
    if (newCommunity) {
      loadInitialData()
    }
  }
)

watch(
  () => isAuthenticated.value,
  (newAuth) => {
    if (newAuth && community.value.community_id) {
      checkMembershipStatus()
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
    <p class="mt-2 text-muted">Loading posts...</p>
  </div>

  <div v-else-if="error" class="alert alert-danger" role="alert">
    {{ error }}
  </div>

  <div v-else>
    <div class="community-header">
      <h1 class="heading mb-3">{{ community.name }}</h1>

      <div class="action-buttons">
        <button @click="viewEvents" class="btn btn-dark me-2 mb-2">
          <i class="bi bi-calendar-event"></i> View Events
        </button>
        <button
          v-if="isAuthenticated && isJoined"
          @click="createPost"
          class="btn btn-dark me-2 mb-2"
        >
          <i class="bi bi-plus-lg"></i> Create Post
        </button>
        <button
          v-if="isAuthenticated"
          @click="toggleJoinLeave"
          class="btn btn-primary mb-2"
          :class="isJoined ? 'btn-danger' : 'btn-primary'"
          :disabled="isJoinLeaveLoading"
        >
          <span
            v-if="isJoinLeaveLoading"
            class="spinner-border spinner-border-sm me-1"
            role="status"
            aria-hidden="true"
          ></span>

          {{ isJoined ? 'Leave' : 'Join' }}
        </button>
      </div>
    </div>

    <p>{{ community.description }}</p>

    <div v-if="joinLeaveError" class="alert alert-danger mb-3" role="alert">
      {{ joinLeaveError }}
    </div>

    <!-- Auto-refresh control -->
    <div class="d-flex justify-content-between align-items-center mb-3">
      <!-- Auto-refresh control -->
      <div class="refresh-controls">
        <div class="d-flex align-items-center">
          <span class="me-2">Auto-refresh:</span>
          <select
            v-model="refreshRate"
            @change="updateRefreshRate(refreshRate / 1000)"
            class="form-select form-select-sm"
            style="width: auto"
          >
            <option :value="10000">10 seconds</option>
            <option :value="30000">30 seconds</option>
            <option :value="60000">1 minute</option>
            <option :value="300000">5 minutes</option>
          </select>
          <button
            @click="fetchPosts"
            class="btn btn-sm btn-outline-secondary ms-2"
            :disabled="isRefreshing"
          >
            <i class="bi bi-arrow-clockwise" :class="{ rotating: isRefreshing }"></i>
          </button>
        </div>
        <div class="text-muted small mt-1" v-if="posts.length > 0">
          Last updated: {{ new Date().toLocaleTimeString() }}
        </div>
      </div>

      <!-- Sort controls -->
      <div class="sort-controls">
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
    </div>

    <hr />

    <!-- Posts section with empty state -->
    <div v-if="posts.length === 0" class="text-center my-4">
      <p class="text-muted">No posts in this community yet.</p>
      <button v-if="isAuthenticated && isJoined" @click="createPost" class="btn btn-primary">
        Create the first post
      </button>
    </div>

    <div v-else class="list-group">
      <CommunityPost
        v-for="post in sortedPosts"
        :key="post.post_id"
        :post="post"
        @click="goToPost(post.post_id)"
      />
    </div>
  </div>
</template>

<style scoped>
.refresh-controls {
  background-color: #f8f9fa;
  padding: 10px;
  border-radius: 8px;
}

@keyframes rotating {
  from {
    transform: rotate(0deg);
  }
  to {
    transform: rotate(360deg);
  }
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

.action-buttons button {
  border-radius: 15px;
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

@media (max-width: 768px) {
  .d-flex.justify-content-between.align-items-center {
    flex-direction: column;
    align-items: flex-start !important;
  }

  .refresh-controls,
  .sort-controls {
    width: 100%;
    margin-bottom: 10px;
  }
}

.sort-controls {
  display: flex;
  align-items: center;
  justify-content: flex-end;
}
</style>