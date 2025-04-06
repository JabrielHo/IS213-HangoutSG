<template>
  <div class="list-group-item post-card">
    <h5 class="mb-1">{{ post.title }}</h5>
    <small>u/{{ post.username }} - {{ formatTimeAgo(post.created_at) }}</small>
    <div class="row">
      <div class="col mt-1">
        <a class="btn btn-sm btn-outline-primary disabled me-2">
          <i class="bi bi-chat-square"></i>&nbsp;{{ post.commentCount }} {{ post.commentCount === 1 ? 'Comment' : 'Comments' }}
        </a>
        <a v-if="isAuthenticated" href="#" class="btn btn-sm btn-outline-danger" @click.stop="reportPost">
          <i class="bi bi-flag"></i>&nbsp;Report
        </a>
      </div>
    </div>
  </div>
</template>

<script setup>
import { useAuth0 } from '@auth0/auth0-vue'
const { isAuthenticated } = useAuth0()

defineProps({
  post: {
    type: Object,
    required: true
  },
});

const formatTimeAgo = (timestamp) => {
  if (!timestamp) return 'unknown time';
  
  const now = new Date();
  const postDate = new Date(timestamp);
  const diffInSeconds = Math.floor((now - postDate) / 1000);
  
  if (diffInSeconds < 60) {
    return 'just now';
  } else if (diffInSeconds < 3600) {
    const minutes = Math.floor(diffInSeconds / 60);
    return `${minutes} ${minutes === 1 ? 'minute' : 'minutes'} ago`;
  } else if (diffInSeconds < 86400) {
    const hours = Math.floor(diffInSeconds / 3600);
    return `${hours} ${hours === 1 ? 'hour' : 'hours'} ago`;
  } else {
    const days = Math.floor(diffInSeconds / 86400);
    return `${days} ${days === 1 ? 'day' : 'days'} ago`;
  }
};

const reportPost = (event) => {
  event.preventDefault();
  // Simple confirmation for reporting
  if (confirm('Are you sure you want to report this post?')) {
    // Here you would make an API call to report the post
    alert('Post reported. Thank you for helping keep the community safe.');
  }
};

</script>

<style scoped>
.post-card {
  cursor: pointer;
  border-radius: 8px;
  margin-bottom: 0.5rem;
  transition: transform 0.3s ease, box-shadow 0.3s ease;
  border: 1px solid rgba(0, 0, 0, 0.125);
}

.post-card:hover {
  box-shadow: 0 8px 15px rgba(0, 0, 0, 0.1);
}

.post-preview {
  color: #666;
  font-size: 0.9rem;
  white-space: pre-line;
}
</style>