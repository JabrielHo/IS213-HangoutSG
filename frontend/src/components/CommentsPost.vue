<template>
  <div class="comments-section">
    <!-- Comment Submission Form -->
    <div class="comment-form mb-4">
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
        :disabled="!newComment.trim() || isSubmitting"
      >
        <span v-if="isSubmitting">Posting...</span>
        <span v-else>Post Comment</span>
      </button>
    </div>

    <!-- Comments List -->
    <div class="comments-list">
      <h4>{{ publishedComments.length }} {{ publishedComments.length === 1 ? 'Comment' : 'Comments' }}</h4>

      <div v-if="loading" class="text-center my-4">
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
          <div class="comment-header">
            <strong>{{ comment.username || 'Unknown User' }}</strong>
            <span class="comment-time">{{ formatTimeAgo(comment.created_at) }}</span>
          </div>
          <div class="comment-content">
            {{ comment.content }}
          </div>
          
          <!-- Reply button -->
          <div class="comment-actions mt-2">
            <button 
              class="btn btn-sm btn-outline-secondary" 
              @click="toggleReplyForm(comment.comment_id)"
            >
              Reply
            </button>
          </div>
          
          <!-- Reply form -->
          <div v-if="activeReplyId === comment.comment_id" class="reply-form mt-2">
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
                :disabled="!replyText.trim() || isSubmitting"
              >
                <span v-if="isSubmitting">Posting...</span>
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
          
          <!-- Nested replies -->
          <div 
            v-if="getRepliesForComment(comment.comment_id).length > 0" 
            class="nested-comments ml-4 mt-3"
          >
            <div 
              v-for="reply in getRepliesForComment(comment.comment_id)" 
              :key="reply.comment_id" 
              class="nested-comment-item"
            >
              <div class="comment-header">
                <strong>{{ reply.username || 'Unknown User' }}</strong>
                <span class="comment-time">{{ formatTimeAgo(reply.created_at) }}</span>
              </div>
              <div class="comment-content">
                {{ reply.content }}
              </div>
            </div>
          </div>
          <div>
            <a href="#" class="btn btn-sm btn-outline-danger" @click.stop="reportPost(comment, $event)">
              <i class="bi bi-flag"></i>&nbsp;Report
            </a>
          </div>

        </div>
      </div>
    </div>
  </div>
</template>
  
<script>
export default {
  name: 'CommentsPost',
  props: {
    postId: {
      type: String,
      required: true,
    },
    currentUser: {
      type: Object,
      required: true,
    },
  },
  data() {
    return {
      comments: [],
      newComment: '',
      replyText: '',
      activeReplyId: null,
      isSubmitting: false,
      loading: true,
      error: null,
    }
  },
  computed: {
    // Filter only published comments
    publishedComments() {
      return this.comments.filter(comment => comment.status === 'published');
    },
    // Get only top-level comments (no parent_id)
    topLevelComments() {
      return this.publishedComments.filter(comment => !comment.parent_id);
    }
  },
  methods: {
    // Get replies for a specific comment
    getRepliesForComment(commentId) {
      return this.publishedComments.filter(comment => comment.parent_id === commentId);
    },
    // Toggle reply form visibility
    toggleReplyForm(commentId) {
      if (this.activeReplyId === commentId) {
        this.activeReplyId = null;
        this.replyText = '';
      } else {
        this.activeReplyId = commentId;
        this.replyText = '';
      }
    },
    // Cancel reply
    cancelReply() {
      this.activeReplyId = null;
      this.replyText = '';
    },
    formatTimeAgo(timestamp) {
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
    },
    async fetchUserData(userIds) {
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
    },
    async fetchComments() {
      this.loading = true
      this.error = null

      try {
        const response = await fetch(`http://localhost:5003/api/comments/post/${this.postId}`)
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
          const userDataMap = await this.fetchUserData(uniqueAuthorIds)
          
          // Add username to each comment
          this.comments = commentsData.map(comment => {
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
          this.error = errorData.message || 'Failed to load comments'
          console.error('Error fetching comments:', this.error)
        }
      } catch (error) {
        this.error = 'Network error when fetching comments'
        console.error('Error fetching comments:', error)
      } finally {
        this.loading = false
      }
    },
    async submitComment(parentId) {
      // Use replyText if it's a reply, otherwise use newComment
      const commentContent = parentId ? this.replyText.trim() : this.newComment.trim();
      
      if (!commentContent) return

      this.isSubmitting = true

      try {
        const response = await fetch('http://localhost:5003/api/comment', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            post_id: this.postId,
            author_id: this.currentUser.id,
            content: commentContent,
            parent_id: parentId, // Include parent_id for replies
            status: 'published' // Set status to published by default
          }),
        })

        if (response.ok) {
          // Clear the form
          if (parentId) {
            this.replyText = '';
            this.activeReplyId = null;
          } else {
            this.newComment = '';
          }
          // Refresh comments
          await this.fetchComments()
        } else {
          const errorData = await response.json()
          alert(`Error posting comment: ${errorData.message}`)
        }
      } catch (error) {
        console.error('Error submitting comment:', error)
        alert('Failed to submit comment. Please try again.')
      } finally {
        this.isSubmitting = false
      }
    },
  async reportPost(comment, event) {
    event.preventDefault();  // Prevent the default action of the event

    // Simple confirmation for reporting
    const confirmed = confirm('Are you sure you want to report this Comment?');
    if (!confirmed) return;

    try {
      const response = await fetch('http://localhost:5007/api/moderation/report/comment/' + comment.comment_id, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          poster_id: comment.author_id, 
          user_id: this.currentUser,   
          comment_id: comment.comment_id, 
          content:comment.content,
          reason: 'No reason provided'
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
  },
  },
  mounted() {
    this.fetchComments()
  },
}
</script>
  
<style scoped>
.comments-section {
  margin-top: 2rem;
}

.comment-form {
  background-color: #f8f9fa;
  padding: 1.5rem;
  border-radius: 8px;
}

.comments-list {
  margin-top: 2rem;
}

.no-comments {
  color: #6c757d;
  font-style: italic;
  margin: 1rem 0;
}

.comment-item {
  padding: 1rem;
  border-bottom: 1px solid #dee2e6;
  margin-bottom: 1rem;
}

.comment-header {
  display: flex;
  justify-content: space-between;
  margin-bottom: 0.5rem;
}

.comment-time {
  color: #6c757d;
  font-size: 0.85rem;
}

.comment-content {
  white-space: pre-line;
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

.comment-actions {
  margin-top: 0.5rem;
}

.reply-form {
  background-color: #f8f9fa;
  padding: 0.75rem;
  border-radius: 6px;
  margin-top: 0.5rem;
}
</style>