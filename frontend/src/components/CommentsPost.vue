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
        @click="submitComment"
        :disabled="!newComment.trim() || isSubmitting"
      >
        <span v-if="isSubmitting">Posting...</span>
        <span v-else>Post Comment</span>
      </button>
    </div>

    <!-- Comments List -->
    <div class="comments-list">
      <h4>{{ comments.length }} {{ comments.length === 1 ? 'Comment' : 'Comments' }}</h4>

      <div v-if="loading" class="text-center my-4">
        <div class="spinner-border" role="status">
          <span class="visually-hidden">Loading...</span>
        </div>
        <p class="mt-2 text-muted">Loading Comments...</p>
      </div>

      <div v-else-if="comments.length === 0" class="no-comments">Be the first to comment!</div>

      <div v-else class="comment-items">
        <div v-for="comment in comments" :key="comment.comment_id" class="comment-item">
          <div class="comment-header">
            <strong>{{ comment.author_id }}</strong>
            <span class="comment-time">{{ formatTimeAgo(comment.created_at) }}</span>
          </div>
          <div class="comment-content">
            {{ comment.content }}
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
      type: String,
      required: true,
    },
  },
  data() {
    return {
      comments: [],
      newComment: '',
      isSubmitting: false,
      loading: true,
      error: null,
    }
  },
  methods: {
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
    async fetchComments() {
      this.loading = true
      this.error = null

      try {
        const response = await fetch(`http://localhost:5003/api/comments/post/${this.postId}`)
        if (response.ok) {
          const data = await response.json()
          this.comments = data.data.comments || []
          // Sort comments with newest first
          this.comments.sort((a, b) => new Date(b.created_at) - new Date(a.created_at))
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
    async submitComment() {
      if (!this.newComment.trim()) return

      this.isSubmitting = true

      try {
        const response = await fetch('http://localhost:5003/api/comment', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            post_id: this.postId,
            author_id: this.currentUser,
            content: this.newComment.trim(),
          }),
        })

        if (response.ok) {
          // Clear the form
          this.newComment = ''
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
</style>