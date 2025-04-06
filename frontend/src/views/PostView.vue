<template>
  <div v-if="authLoading || loading" class="text-center my-5">
    <div class="spinner-border" role="status">
      <span class="visually-hidden">Loading...</span>
    </div>
    <p class="mt-2">Loading post...</p>
  </div>

  <div v-else-if="error" class="alert alert-danger my-5">
    {{ error }}
  </div>

  <div v-else class="post-view">
    <div class="post-details">
      <h2>{{ post.title }}</h2>
      <p class="meta">
        <span class="author">By {{ authorUsername }}</span> •
        <span class="date">{{ formatDate(post.created_at) }}</span> •
        <span class="community"
          >in community:
          <span v-if="communityLoading">loading...</span>
          <span v-else>{{ communityName }}</span>
        </span>
      </p>
      <div class="content">{{ post.content }}</div>
    </div>

    <hr />

    <!-- Comments section for authenticated users -->
    <CommentsPost
      v-if="isAuthenticated"
      :postId="$route.params.postId"
      :currentUser="{ id: user.sub, username: user.username }"
    />
    
    <!-- Login prompt for non-authenticated users -->
    <div v-else class="login-prompt card p-4 text-center my-4">
      <h4>Please login or sign up to comment</h4>
      <p class="text-muted">Join the conversation by logging in or creating an account</p>
      <div class="d-flex justify-content-center gap-3 mt-3">
        <LoginButton />
        <button @click="signUp" class="btn btn-outline-primary">Sign Up</button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue'
import { useRoute } from 'vue-router'
import { useAuth0 } from '@auth0/auth0-vue'
import CommentsPost from '../components/CommentsPost.vue'
import LoginButton from '../components/LoginButton.vue'

const route = useRoute()
const { user, isAuthenticated, isLoading: authLoading, loginWithRedirect } = useAuth0()

const post = ref(null)
const loading = ref(true)
const error = ref(null)
const communityName = ref('')
const communityLoading = ref(false)
const authorUsername = ref('Loading...')

// Sign up function with screen_hint for Auth0
const signUp = () => {
  loginWithRedirect({
    appState: { 
      returnTo: window.location.pathname 
    },
    screen_hint: 'signup'
  })
}

const formatDate = (dateString) => {
  if (!dateString) return ''

  const options = {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  }

  return new Date(dateString).toLocaleString(undefined, options)
}

const fetchAuthorInfo = async (authorId) => {
  try {
    const response = await fetch(`http://localhost:5000/api/users/${authorId}`)
    
    if (response.ok) {
      const userData = await response.json()
      if (userData.data && userData.data.username) {
        authorUsername.value = userData.data.username
      } else {
        authorUsername.value = 'Unknown User'
      }
    } else {
      authorUsername.value = 'Unknown User'
      console.error('HTTP error fetching author:', response.status)
    }
  } catch (err) {
    authorUsername.value = 'Unknown User'
    console.error('Failed to fetch author info:', err)
  }
}

const fetchCommunityInfo = async (communityId) => {
  communityLoading.value = true
  try {
    const response = await fetch(`http://localhost:5001/api/community/${communityId}`)

    if (response.ok) {
      const data = await response.json()
      console.log(data.data.name)

      if (data.code === 200) {
        communityName.value = data.data.name
      } else {
        communityName.value = 'Unknown Community'
        console.error('Error fetching community:', data.message)
      }
    } else {
      communityName.value = 'Unknown Community'
      console.error('HTTP error fetching community:', response.status)
    }
  } catch (err) {
    communityName.value = 'Unknown Community'
    console.error('Failed to fetch community info:', err)
  } finally {
    communityLoading.value = false
  }
}

const fetchPost = async () => {
  loading.value = true
  error.value = null
  authorUsername.value = 'Loading...'

  const postId = route.params.postId

  try {
    const response = await fetch(`http://localhost:5002/api/post/${postId}`)

    if (response.ok) {
      const data = await response.json()

      if (data.code === 200 && data.data) {
        post.value = data.data

        // Fetch author information
        if (post.value.author_id) {
          await fetchAuthorInfo(post.value.author_id)
        }

        // Fetch community information
        if (post.value.community_id) {
          await fetchCommunityInfo(post.value.community_id)
        }
      } else {
        error.value = data.message || 'Failed to fetch post'
      }
    } else if (response.status === 404) {
      post.value = null // Post not found
    } else {
      const errorData = await response.json()
      error.value = errorData.message || `Error ${response.status}: Failed to load post`
    }
  } catch (err) {
    console.error('Failed to fetch post:', err)
    error.value = 'Network error when fetching post data'
  } finally {
    loading.value = false
  }
}

// Watch for changes in the route params to reload the post if necessary
watch(
  () => route.params.postId,
  (newId, oldId) => {
    if (newId !== oldId) {
      fetchPost()
    }
  }
)

onMounted(() => {
  fetchPost()
})
</script>

<style scoped>
.post-view {
  padding: 1.5rem;
}

.post-details {
  margin-bottom: 2rem;
}

.meta {
  font-size: 0.9rem;
  color: #666;
  margin-bottom: 1rem;
}

.author {
  font-weight: 500;
}

.community {
  font-style: italic;
}

.content {
  font-size: 1.1rem;
  color: #333;
  white-space: pre-line;
  margin-top: 1.5rem;
}

.login-prompt {
  background-color: #f8f9fa;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}
</style>