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

    <!-- Comment form for authenticated users only -->
    <div v-if="isAuthenticated" class="comment-form mb-4">
      <h4>Add a comment</h4>
      <div class="form-group">
        <textarea
          class="form-control"
          v-model="newComment"
          placeholder="What are your thoughts?"
          rows="3"
        ></textarea>
      </div>
      <button
        class="btn btn-primary mt-2"
        @click="submitComment(null)"
        :disabled="!newComment.trim() || isSubmittingComment"
      >
        <span v-if="isSubmittingComment">Posting...</span>
        <span v-else>Post Comment</span>
      </button>
    </div>

    <!-- Login prompt for non-authenticated users -->
    <div v-else class="login-prompt card p-4 text-center my-4 text-white bg-dark">
      <h4>Please login or sign up to comment</h4>
      <p>Join the conversation by logging in or creating an account</p>
      <div class="d-flex justify-content-center gap-3 mt-3">
        <LoginButton/>
        <SignupButton />
      </div>
    </div>

    <!-- Comments section for all users - authenticated or not -->
    <CommentsPost
      :comments="comments"
      :loading="commentsLoading"
      :isSubmitting="isSubmittingComment"
      :replyText="replyText"
      :activeReplyId="activeReplyId"
      :currentUser="isAuthenticated ? { id: user.sub, username: user.username } : null"
      :isAuthenticated="isAuthenticated"
      @update:replyText="replyText = $event"
      @submit-comment="submitComment"
      @toggle-reply="toggleReplyForm"
      @cancel-reply="cancelReply"
    />
  </div>
</template>

<script setup>
import { ref, onMounted, watch, computed } from 'vue'
import { useRoute } from 'vue-router'
import { useAuth0 } from '@auth0/auth0-vue'
import CommentsPost from '../components/CommentsPost.vue'
import LoginButton from '../components/LoginButton.vue'
import SignupButton from '../components/SignupButton.vue'

const route = useRoute()
const { user, isAuthenticated, isLoading: authLoading, loginWithRedirect } = useAuth0()

const post = ref(null)
const loading = ref(true)
const error = ref(null)
const communityName = ref('')
const communityLoading = ref(false)
const authorUsername = ref('Loading...')

// Comments-related state moved from CommentsPost
const comments = ref([])
const commentsLoading = ref(true)
const commentsError = ref(null)
const newComment = ref('')
const replyText = ref('')
const activeReplyId = ref(null)
const isSubmittingComment = ref(false)

// Comments computed properties
const publishedComments = computed(() => {
  return comments.value.filter(comment => comment.status === 'published');
})

const topLevelComments = computed(() => {
  return publishedComments.value.filter(comment => !comment.parent_id);
})

const getRepliesForComment = (commentId) => {
  return publishedComments.value.filter(comment => comment.parent_id === commentId);
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

const formatTimeAgo = (timestamp) => {
  if (!timestamp) return 'unknown time'

  const now = new Date()
  const commentDate = new Date(timestamp)
  const diffInSeconds = Math.floor((now - commentDate) / 1000)

  if (diffInSeconds < 60) {
    return 'just now'
  } else if (diffInSeconds < 3600) {
    const minutes = Math.floor(diffInSeconds / 60)
    return `${minutes} ${minutes === 1 ? 'minute' : 'minutes'} ago`
  } else if (diffInSeconds < 86400) {
    const hours = Math.floor(diffInSeconds / 3600)
    return `${hours} ${hours === 1 ? 'hour' : 'hours'} ago`
  } else {
    const days = Math.floor(diffInSeconds / 86400)
    return `${days} ${days === 1 ? 'day' : 'days'} ago`
  }
}

// Toggle reply form visibility
const toggleReplyForm = (commentId) => {
  if (!isAuthenticated.value) {
    // Don't allow toggling replies if not authenticated
    return;
  }
  
  if (activeReplyId.value === commentId) {
    activeReplyId.value = null;
    replyText.value = '';
  } else {
    activeReplyId.value = commentId;
    replyText.value = '';
  }
}

// Cancel reply
const cancelReply = () => {
  activeReplyId.value = null;
  replyText.value = '';
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

// Moved from CommentsPost
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

// Fetch comments - moved from CommentsPost
const fetchComments = async () => {
  commentsLoading.value = true
  commentsError.value = null

  try {
    const response = await fetch(`http://localhost:5003/api/comments/post/${route.params.postId}`)
    if (response.ok) {
      const data = await response.json()
      let commentsData = data.data.comments || []
      
      // Sort comments with newest first for top-level comments
      // but keep replies in chronological order
      commentsData.sort((a, b) => {
        // If both are top-level or both are replies, sort by time (newest first for top-level)
        if ((!a.parent_id && !b.parent_id) || (a.parent_id && b.parent_id)) {
          return !a.parent_id ? 
            new Date(b.created_at) - new Date(a.created_at) : // Top level: newest first
            new Date(a.created_at) - new Date(b.created_at);  // Replies: oldest first
        }
        // Put top-level comments before replies
        return a.parent_id ? 1 : -1;
      });
      
      // Extract unique author IDs
      const uniqueAuthorIds = [...new Set(commentsData.map(comment => comment.author_id))]
      
      // Fetch user data for all authors
      const userDataMap = await fetchUserData(uniqueAuthorIds)
      
      // Add username to each comment
      comments.value = commentsData.map(comment => {
        const userData = userDataMap[comment.author_id]
        return {
          ...comment,
          username: userData ? userData.username : 'Unknown User',
          // If status isn't provided, default to published
          status: comment.status || 'published'
        }
      })
    } else {
      const errorData = await response.json()
      commentsError.value = errorData.message || 'Failed to load comments'
      console.error('Error fetching comments:', commentsError.value)
    }
  } catch (error) {
    commentsError.value = 'Network error when fetching comments'
    console.error('Error fetching comments:', error)
  } finally {
    commentsLoading.value = false
  }
}

// Submit comment - moved from CommentsPost
const submitComment = async (parentId) => {
  // Ensure user is authenticated before submitting
  if (!isAuthenticated.value) {
    return;
  }
  
  // Use replyText if it's a reply, otherwise use newComment
  const commentContent = parentId ? replyText.value.trim() : newComment.value.trim();
  
  if (!commentContent) return

  isSubmittingComment.value = true

  try {
    const response = await fetch('http://localhost:5003/api/comment', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        post_id: route.params.postId,
        author_id: user.value.sub,
        content: commentContent,
        parent_id: parentId, // Include parent_id for replies
        status: 'published' // Set status to published by default
      }),
    })

    if (response.ok) {
      // Clear the form
      if (parentId) {
        replyText.value = '';
        activeReplyId.value = null;
      } else {
        newComment.value = '';
      }
      // Refresh comments
      await fetchComments()
    } else {
      const errorData = await response.json()
      alert(`Error posting comment: ${errorData.message}`)
    }
  } catch (error) {
    console.error('Error submitting comment:', error)
    alert('Failed to submit comment. Please try again.')
  } finally {
    isSubmittingComment.value = false
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
        
        // Fetch comments for the post
        await fetchComments()
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

/* Added styles for comment form */
.comment-form {
  background-color: #f8f9fa;
  padding: 1.5rem;
  border-radius: 8px;
}
</style>