<template>
  <div class="comments-section">
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
          
          <!-- Reply button - only shown to authenticated users -->
          <div v-if="isAuthenticated" class="comment-actions mt-2">
            <button 
              class="btn btn-sm btn-outline-secondary" 
              @click="$emit('toggle-reply', comment.comment_id)"
            >
              Reply
            </button>
          </div>
          
          <!-- Reply form -->
          <div v-if="isAuthenticated && activeReplyId === comment.comment_id" class="reply-form mt-2">
            <div class="form-group">
              <textarea
                class="form-control form-control-sm"
                :value="replyText"
                @input="$emit('update:replyText', $event.target.value)"
                placeholder="Write a reply..."
                rows="2"
              ></textarea>
            </div>
            <div class="d-flex mt-2">
              <button
                class="btn btn-sm btn-primary me-2"
                @click="$emit('submit-comment', comment.comment_id)"
                :disabled="!replyText.trim() || isSubmitting"
              >
                <span v-if="isSubmitting">Posting...</span>
                <span v-else>Post Reply</span>
              </button>
              <button
                class="btn btn-sm btn-outline-secondary"
                @click="$emit('cancel-reply')"
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
        </div>
      </div>
    </div>
  </div>
</template>
  
<script>
export default {
  name: 'CommentsPost',
  props: {
    comments: {
      type: Array,
      required: true
    },
    loading: {
      type: Boolean,
      default: false
    },
    isSubmitting: {
      type: Boolean,
      default: false
    },
    replyText: {
      type: String,
      default: ''
    },
    activeReplyId: {
      type: String,
      default: null
    },
    currentUser: {
      type: Object,
      required: false,
      default: null
    },
    isAuthenticated: {
      type: Boolean,
      default: false
    }
  },
  emits: [
    'update:replyText',
    'submit-comment',
    'toggle-reply',
    'cancel-reply'
  ],
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
    }
  }
}
</script>
  
<style scoped>
.comments-section {
  margin-top: 2rem;
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