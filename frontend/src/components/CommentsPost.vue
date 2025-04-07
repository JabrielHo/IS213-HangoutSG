<template>
  <div class="comment-container" @mouseover="$emit('mouseover')" @mouseleave="$emit('mouseleave')">
    <div class="comment-header">
      <strong>{{ comment.username || 'Unknown User' }}</strong>
      <span class="comment-time">{{ formatTimeAgo(comment.created_at) }}</span>
    </div>
    <div class="comment-content">
      {{ comment.content }}
    </div>
    
    <!-- Comment actions - only shown when hovering and authenticated -->
    <div v-if="isAuthenticated && isHovered" class="comment-actions mt-2">
      <button 
        class="btn btn-sm btn-outline-secondary me-2" 
        @click="$emit('toggle-reply', comment.comment_id)"
      >
        Reply
      </button>
      <button 
        class="btn btn-sm btn-outline-danger" 
        @click="$emit('report-comment', comment, $event)"
      >
        <i class="bi bi-flag"></i>&nbsp;Report
      </button>
    </div>
    
    <!-- Reply form slot -->
    <slot name="reply-form"></slot>
    
    <!-- Nested comments slot -->
    <slot name="nested-comments"></slot>
  </div>
</template>
  
<script setup>
import { defineEmits } from 'vue';

const props = defineProps({
  // Individual comment object
  comment: {
    type: Object,
    required: true
  },
  isAuthenticated: {
    type: Boolean,
    default: false
  },
  isHovered: {
    type: Boolean,
    default: false
  },
  isActiveReply: {
    type: Boolean,
    default: false
  },
  activeReplyId: {
    type: String,
    default: null
  }
});

const emit = defineEmits([
  'toggle-reply',
  'report-comment',
  'mouseover',
  'mouseleave'
]);

// Format relative time for comments
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
</script>
  
<style scoped>
.comment-container {
  padding: 1rem;
  border-bottom: 1px solid #dee2e6;
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

.comment-actions {
  margin-top: 0.5rem;
  transition: opacity 0.2s ease;
}
</style>