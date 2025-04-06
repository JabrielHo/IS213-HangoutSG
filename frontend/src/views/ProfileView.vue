<script setup>
import { ref, onMounted, watch } from 'vue'
import { useAuth0 } from '@auth0/auth0-vue'
import { useRouter } from 'vue-router'
import CommunityPost from '../components/CommunityPost.vue'
import CommunityCard from '@/components/CommunityCard.vue'

const router = useRouter()
const { user, isAuthenticated, isLoading: authLoading } = useAuth0()
const currentTab = ref('community')
const communities = ref([])
const posts = ref([])
const comments = ref([])
const isLoading = ref(false)

const tabs = [
  { id: 'community', name: 'Communities' },
  { id: 'posts', name: 'Posts' },
  { id: 'comments', name: 'Comments' },
  { id: 'hostedevents', name: 'Created Events' },
  { id: 'joinedevents', name: 'Joined Events' },
]

const goToPost = (postId) => {
  router.push(`/post/${postId}`)
}

const navigateToCommunity = (communityName) => {
  router.push(`/c/${communityName}`)
}

const loadUserData = async () => {
  if (isAuthenticated.value && user.value) {
    try {
      await fetchUserCommunities()
      await fetchUserPosts()
      await fetchUserComments()
      await fetchHostedEvents()
      await fetchJoinedEvents()
    } catch (error) {
      console.error('Error fetching user data:', error)
    }
  }
}

watch(isAuthenticated, (newValue) => {
  if (newValue) {
    loadUserData()
  }
})

watch(user, (newValue) => {
  if (newValue && isAuthenticated.value) {
    loadUserData()
  }
})

onMounted(() => {
  // If already authenticated, load data right away
  if (isAuthenticated.value && user.value && !authLoading.value) {
    loadUserData()
  }
})

const fetchUserCommunities = async () => {
  try {
    isLoading.value = true

    const creatorId = user.value.sub

    const response = await fetch(`http://localhost:5001/api/community/creator/${creatorId}`)

    if (!response.ok) {
      throw new Error(`HTTP error! Status: ${response.status}`)
    }

    const data = await response.json()

    if (data.code === 200) {
      communities.value = data.data.communities
    } else {
      console.error('Error fetching communities:', data.message)
    }
  } catch (err) {
    console.error('Error fetching communities:', err)
  } finally {
    isLoading.value = false
  }
}

const fetchUserPosts = async () => {
  try {
    isLoading.value = true
    const creatorId = user.value.sub

    // Step 1: Fetch posts and immediately display them
    const response = await fetch(`http://localhost:5002/api/posts/author/${creatorId}`)

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
    isLoading.value = false

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
  } catch (err) {
    console.error('Error fetching posts:', err)
  }
}

// Helper functions to fetch data
const fetchUserData = async (userIds) => {
  const userDataMap = {}
  await Promise.all(
    userIds.map(async (userId) => {
      try {
        const userResponse = await fetch(`http://localhost:5000/api/users/${userId}`)
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
        const commentResponse = await fetch(`http://localhost:5003/api/comments/post/${postId}`)
        if (commentResponse.ok) {
          const commentData = await commentResponse.json()
          commentCountMap[postId] = commentData.data.comments ? commentData.data.comments.length : 0
        }
      } catch (error) {
        console.error(`Error fetching comment count for post ${postId}:`, error)
        commentCountMap[postId] = 0
      }
    })
  )
  return commentCountMap
}

const fetchUserComments = async () => {
  comments.value = []
}

const fetchHostedEvents = async () => {
  comments.value = []
}

const fetchJoinedEvents = async () => {
  comments.value = []
}
</script>

<template>
  <div v-if="authLoading" class="text-center my-5">
    <div class="spinner-border" role="status"></div>
    <p class="mt-2 text-muted">Loading Profile...</p>
  </div>

  <div v-else>
    <div class="profile-header">
      <div class="profile-avatar">
        <img :src="user.picture" :alt="user.name" />
      </div>
      <div class="profile-info">
        <h2>{{ user.username }}</h2>
        <p class="email">{{ user.email }}</p>
      </div>
    </div>

    <div class="profile-tabs">
      <div class="tabs">
        <button
          v-for="tab in tabs"
          :key="tab.id"
          @click="currentTab = tab.id"
          :class="{ active: currentTab === tab.id }"
        >
          {{ tab.name }}
        </button>
      </div>

      <div class="tab-content">
        <!-- Community Tab -->
        <div v-if="currentTab === 'community'" class="tab-panel">
          <h3>My Created Communities</h3>
          <div v-if="isLoading" class="text-center my-5">
            <div class="spinner-border" role="status"></div>
            <p class="mt-2 text-muted">Loading Communities...</p>
          </div>
          <div v-else-if="communities.length === 0" class="empty-state">
            You haven't created any communities yet.
          </div>
          <div v-else class="communities-grid">
            <CommunityCard
              v-for="community in communities"
              :key="community.id"
              :community="community"
              :showStats="false"
              @click="navigateToCommunity(community.name)"
            />
          </div>
        </div>

        <!-- Posts Tab -->
        <div v-if="currentTab === 'posts'" class="tab-panel">
          <h3>My Posts</h3>
          <div v-if="isLoading" class="text-center my-5">
            <div class="spinner-border" role="status"></div>
            <p class="mt-2 text-muted">Loading Posts...</p>
          </div>
          <div v-else-if="posts.length === 0" class="empty-state">
            You haven't created any posts yet.
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

        <!-- Comments Tab -->
        <div v-if="currentTab === 'comments'" class="tab-panel">
          <h3>My Comments</h3>
          <div v-if="comments.length === 0" class="empty-state">
            You haven't made any comments yet.
          </div>
          <div v-else class="comments-list">
            <div v-for="comment in comments" :key="comment.id">
              <p>{{ comment.content }}</p>
            </div>
          </div>
        </div>

        <!-- Created Events Tab -->
        <div v-if="currentTab === 'hostedevents'" class="tab-panel">
          <h3>My Hosted Events</h3>
          <div v-if="comments.length === 0" class="empty-state">
            You haven't created any events yet.
          </div>
          <div v-else></div>
        </div>

        <!-- Joined Events Tab -->
        <div v-if="currentTab === 'joinedevents'" class="tab-panel">
          <h3>My Joined Events</h3>
          <div v-if="comments.length === 0" class="empty-state">
            You haven't joined any events yet.
          </div>
          <div v-else></div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.profile-header {
  display: flex;
  align-items: center;
  margin-bottom: 30px;
  padding-bottom: 20px;
  border-bottom: 1px solid #eee;
  flex-wrap: wrap; /* Allow wrapping on small screens */
}

.profile-avatar img {
  width: 100px;
  height: 100px;
  border-radius: 50%;
  object-fit: cover;
}

.profile-info {
  margin-left: 20px;
}

.profile-info h2 {
  margin-bottom: 5px;
}

.email {
  color: #666;
  margin: 5px 0;
}

.tabs {
  display: flex;
  border-bottom: 1px solid #ddd;
  margin-bottom: 20px;
  flex-wrap: wrap; /* Allow tabs to wrap on smaller screens */
  gap: 5px; /* Add gap between wrapped tabs */
}

.tabs button {
  padding: 10px 20px;
  background: none;
  border: none;
  cursor: pointer;
  font-size: 16px;
  position: relative;
  white-space: nowrap; /* Prevent tab text from wrapping */
}

.tabs button.active {
  font-weight: bold;
  color: #4a90e2;
}

.tabs button.active::after {
  content: '';
  position: absolute;
  bottom: -1px;
  left: 0;
  right: 0;
  height: 3px;
  background-color: #4a90e2;
}

.tab-panel {
  min-height: 200px;
}

.tab-panel h3 {
  margin-bottom: 15px;
}

.empty-state {
  color: #888;
  font-style: italic;
  text-align: center;
  padding: 30px;
  background: #f9f9f9;
  border-radius: 5px;
}

.communities-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 1.5rem;
  margin-top: 2rem;
}

.spinner-border {
  width: 3rem;
  height: 3rem;
}

/* Add these media queries for mobile responsiveness */
@media (max-width: 768px) {
  .profile-header {
    flex-direction: column;
    align-items: center;
    text-align: center;
  }
  
  .profile-info {
    margin-left: 0;
    margin-top: 15px;
  }
  
  .tabs {
    justify-content: center;
  }
  
  .tabs button {
    padding: 8px 15px;
    font-size: 14px;
    flex: 1;
    text-align: center;
    min-width: 100px;
  }
  
  .communities-grid {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 480px) {
  .tabs button {
    padding: 8px 10px;
    font-size: 13px;
    min-width: auto;
  }
  
  .profile-avatar img {
    width: 80px;
    height: 80px;
  }
}
</style>