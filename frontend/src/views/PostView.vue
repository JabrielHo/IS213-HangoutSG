<template>
  <!-- Keeping the existing template code unchanged except for the nested comment structure -->
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
    <!-- Post details section (unchanged) -->
    <div class="post-details">
      <h2>{{ post.title }}</h2>
      <p class="meta">
        <span class="author">By {{ authorUsername }}</span> •
        <span class="date">{{ formatDate(post.created_at) }}</span> •
        <span class="community">
          in community:
          <span v-if="communityLoading">loading...</span>
          <span v-else>{{ communityName }}</span>
        </span>
      </p>
      <div class="content">{{ post.content }}</div>
    </div>

    <hr />

    <!-- Comment form for authenticated users only (unchanged) -->
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

    <!-- Login prompt for non-authenticated users (unchanged) -->
    <div v-else class="login-prompt card p-4 text-center my-4 text-white bg-dark">
      <h4>Please login or sign up to comment</h4>
      <p>Join the conversation by logging in or creating an account</p>
      <div class="d-flex justify-content-center gap-3 mt-3">
        <LoginButton/>
        <SignupButton />
      </div>
    </div>

    <!-- Comments section for all users - authenticated or not -->
    <div class="comments-section">
      <h4>{{ publishedComments.length }} {{ publishedComments.length === 1 ? 'Comment' : 'Comments' }}</h4>

      <div v-if="commentsLoading" class="text-center my-4">
        <div class="spinner-border" role="status">
          <span class="visually-hidden">Loading...</span>
        </div>
        <p class="mt-2 text-muted">Loading Comments...</p>
      </div>

      <div v-else-if="publishedComments.length === 0" class="no-comments">Be the first to comment!</div>

      <div v-else class="comment-items">
        <!-- Top-level comments -->
        <div 
          v-for="comment in topLevelComments" 
          :key="comment.comment_id" 
          class="comment-item"
        >
          <CommentsPost
            :comment="comment"
            :isAuthenticated="isAuthenticated"
            :isHovered="hoveredCommentIds[comment.comment_id]"
            :isActiveReply="activeReplyId === comment.comment_id"
            :activeReplyId="activeReplyId"
            @mouseover="setHoveredComment(comment.comment_id, true)"
            @mouseleave="setHoveredComment(comment.comment_id, false)"
            @toggle-reply="toggleReplyForm"
            @report-comment="reportComment"
          >
            <!-- Reply form slot -->
            <template v-if="isAuthenticated && activeReplyId === comment.comment_id" v-slot:reply-form>
              <div class="reply-form mt-2">
                <div class="form-group">
                  <textarea
                    class="form-control form-control-sm"
                    v-model="replyText"
                    placeholder="Write a reply..."
                    rows="2"
                  ></textarea>
                </div>
                <div class="d-flex mt-2">
                  <button
                    class="btn btn-sm btn-primary me-2"
                    @click="submitComment(comment.comment_id)"
                    :disabled="!replyText.trim() || isSubmittingComment"
                  >
                    <span v-if="isSubmittingComment">Posting...</span>
                    <span v-else>Post Reply</span>
                  </button>
                  <button
                    class="btn btn-sm btn-outline-secondary"
                    @click="cancelReply"
                  >
                    Cancel
                  </button>
                </div>
              </div>
            </template>
            
            <!-- Nested replies slot -->
            <template v-if="getNestedReplies(comment.comment_id).length > 0" v-slot:nested-comments>
              <div class="nested-comments mt-3">
                <div 
                  v-for="reply in getNestedReplies(comment.comment_id)" 
                  :key="reply.comment_id" 
                  class="nested-comment-item"
                >
                  <CommentsPost
                    :comment="reply"
                    :isAuthenticated="isAuthenticated"
                    :isHovered="hoveredCommentIds[reply.comment_id]"
                    :isActiveReply="activeReplyId === reply.comment_id"
                    :activeReplyId="activeReplyId"
                    @mouseover="setHoveredComment(reply.comment_id, true)"
                    @mouseleave="setHoveredComment(reply.comment_id, false)"
                    @toggle-reply="toggleReplyForm"
                    @report-comment="reportComment"
                  >
                    <!-- Reply form slot for nested replies -->
                    <template v-if="isAuthenticated && activeReplyId === reply.comment_id" v-slot:reply-form>
                      <div class="reply-form mt-2">
                        <div class="form-group">
                          <textarea
                            class="form-control form-control-sm"
                            v-model="replyText"
                            placeholder="Write a reply..."
                            rows="2"
                          ></textarea>
                        </div>
                        <div class="d-flex mt-2">
                          <button
                            class="btn btn-sm btn-primary me-2"
                            @click="submitComment(reply.comment_id)"
                            :disabled="!replyText.trim() || isSubmittingComment"
                          >
                            <span v-if="isSubmittingComment">Posting...</span>
                            <span v-else>Post Reply</span>
                          </button>
                          <button
                            class="btn btn-sm btn-outline-secondary"
                            @click="cancelReply"
                          >
                            Cancel
                          </button>
                        </div>
                      </div>
                    </template>
                    
                    <!-- Recursive nested replies - allowing for replies to replies at any level -->
                    <template v-if="getNestedReplies(reply.comment_id).length > 0" v-slot:nested-comments>
                      <div class="nested-comments mt-3">
                        <div 
                          v-for="nestedReply in getNestedReplies(reply.comment_id)" 
                          :key="nestedReply.comment_id" 
                          class="nested-comment-item"
                        >
                          <CommentsPost
                            :comment="nestedReply"
                            :isAuthenticated="isAuthenticated"
                            :isHovered="hoveredCommentIds[nestedReply.comment_id]"
                            :isActiveReply="activeReplyId === nestedReply.comment_id"
                            :activeReplyId="activeReplyId"
                            @mouseover="setHoveredComment(nestedReply.comment_id, true)"
                            @mouseleave="setHoveredComment(nestedReply.comment_id, false)"
                            @toggle-reply="toggleReplyForm"
                            @report-comment="reportComment"
                          >
                            <!-- Reply form for deeply nested replies -->
                            <template v-if="isAuthenticated && activeReplyId === nestedReply.comment_id" v-slot:reply-form>
                              <div class="reply-form mt-2">
                                <div class="form-group">
                                  <textarea
                                    class="form-control form-control-sm"
                                    v-model="replyText"
                                    placeholder="Write a reply..."
                                    rows="2"
                                  ></textarea>
                                </div>
                                <div class="d-flex mt-2">
                                  <button
                                    class="btn btn-sm btn-primary me-2"
                                    @click="submitComment(nestedReply.comment_id)"
                                    :disabled="!replyText.trim() || isSubmittingComment"
                                  >
                                    <span v-if="isSubmittingComment">Posting...</span>
                                    <span v-else>Post Reply</span>
                                  </button>
                                  <button
                                    class="btn btn-sm btn-outline-secondary"
                                    @click="cancelReply"
                                  >
                                    Cancel
                                  </button>
                                </div>
                              </div>
                            </template>
                          </CommentsPost>
                        </div>
                      </div>
                    </template>
                  </CommentsPost>
                </div>
              </div>
            </template>
          </CommentsPost>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, watch, computed, reactive } from 'vue'
import { useRoute } from 'vue-router'
import { useAuth0 } from '@auth0/auth0-vue'
import CommentsPost from '../components/CommentsPost.vue'
import LoginButton from '../components/LoginButton.vue'
import SignupButton from '../components/SignupButton.vue'

const route = useRoute()
const { user, isAuthenticated, isLoading: authLoading } = useAuth0()

const post = ref(null)
const loading = ref(true)
const error = ref(null)
const communityName = ref('')
const communityLoading = ref(false)
const authorUsername = ref('Loading...')

// Comments-related state
const comments = ref([])
const commentsLoading = ref(true)
const commentsError = ref(null)
const newComment = ref('')
const replyText = ref('')
const activeReplyId = ref(null)
const isSubmittingComment = ref(false)
// Replace single hoveredCommentId with a reactive object to track all comment hover states
const hoveredCommentIds = reactive({})

// Helper function to set a comment's hover state
const setHoveredComment = (commentId, isHovered) => {
  hoveredCommentIds[commentId] = isHovered
}

// Computed properties for comments
const publishedComments = computed(() => {
  return comments.value.filter(comment => comment.status === 'published');
})

const topLevelComments = computed(() => {
  return publishedComments.value.filter(comment => !comment.parent_id);
})

// Get all replies for a specific comment, no matter the nesting level
const getNestedReplies = (commentId) => {
  return publishedComments.value.filter(comment => comment.parent_id === commentId)
    .sort((a, b) => new Date(a.created_at) - new Date(b.created_at));
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

// Fetch user data for comments
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

// Fetch comments
const fetchComments = async () => {
  commentsLoading.value = true
  commentsError.value = null

  try {
    const response = await fetch(`http://localhost:5003/api/comments/post/${route.params.postId}`)
    if (response.ok) {
      const data = await response.json()
      let commentsData = data.data.comments || []
      // Extract unique author IDs
      const uniqueAuthorIds = [...new Set(commentsData.map(comment => comment.author_id))]
      
      // Fetch user data for all authors
      const userDataMap = await fetchUserData(uniqueAuthorIds)
      
      // Add username to each comment
      const processedComments = commentsData.map(comment => {
        const userData = userDataMap[comment.author_id]
        return {
          ...comment,
          username: userData ? userData.username : 'Unknown User',
          // If status isn't provided, default to published
          status: comment.status || 'published'
        }
      })

      
      // Only sort top-level comments by newest first
      // Don't change the order of replies as they'll be sorted when retrieved
      processedComments.sort((a, b) => {
        // If both are top-level comments, sort newest first
        if (!a.parent_id && !b.parent_id) {
          return new Date(b.created_at) - new Date(a.created_at);
        }
        return 0; // Don't change the order for replies
      });
      
      comments.value = processedComments;
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

// Submit comment
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

// Report comment
const reportComment = async (comment, event) => {
  event.preventDefault();  // Prevent the default action of the event
  // Prompt user to input a reason for reporting the comment
  const reason = prompt('Please provide a reason for reporting this comment:');
  
  if (!reason) {
    alert('You must provide a reason to report the comment.');
    return;
  }
  try {
    const response = await fetch(`http://localhost:5007/api/moderation/report/comment/${comment.comment_id}`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        poster_id: comment.author_id, 
        user_id: user.value.sub,   
        comment_id: comment.comment_id, 
        content: comment.content,
        reason: reason
      }), 
    });
    if (response.ok) {
      // If the response status is 200-299
      const responseData = await response.json(); // Parse the JSON response
      alert('Comment reported. Thank you for helping keep the community safe.');
    } else {
      const errorData = await response.json();
      throw new Error(errorData.message || 'Failed to report the comment.');
    }
  } catch (error) {
    console.error('Error while reporting the comment:', error);
    alert('There was an error while reporting the comment.');
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

/* Comments section styles */
.comments-section {
  margin-top: 2rem;
}

.no-comments {
  color: #6c757d;
  font-style: italic;
  margin: 1rem 0;
}

.comment-item {
  margin-bottom: 1rem;
}

.reply-form {
  background-color: #f8f9fa;
  padding: 0.75rem;
  border-radius: 6px;
  margin-top: 0.5rem;
}

.nested-comments {
  margin-left: 2rem;
  border-left: 2px solid #dee2e6;
  padding-left: 1rem;
}

.nested-comment-item {
  padding: 0.75rem 0;
  border-bottom: 1px solid #f0f0f0;
}

.nested-comment-item:last-child {
  border-bottom: none;
}
</style>