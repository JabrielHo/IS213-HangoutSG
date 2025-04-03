<template>
  <div class="list-group-item post-card">
    <h5 class="mb-1">{{ post.title }}</h5>
    <small>u/{{ post.author_id }} - {{ formatTimeAgo(post.created_at) }}</small>
    <p v-if="showPreview" class="post-preview mt-2">{{ contentPreview }}</p>
    <div class="row">
      <div class="col mt-1">
        <a href="#" class="btn btn-sm btn-outline-primary me-2" @click.stop="viewComments">
          <i class="bi bi-chat-square"></i>&nbsp;{{ commentCount }} {{ commentCount === 1 ? 'Comment' : 'Comments' }}
        </a>
        <a href="#" class="btn btn-sm btn-outline-secondary me-2" @click.stop="sharePost">
          <i class="bi bi-share"></i>&nbsp;Share
        </a>
        <a href="#" class="btn btn-sm btn-outline-danger" @click.stop="reportPost">
          <i class="bi bi-flag"></i>&nbsp;Report
        </a>
      </div>
    </div>
  </div>
</template>

<script>

import { useAuth0 } from '@auth0/auth0-vue';

const user = useAuth0();


export default {
  name: 'CommunityPost',
  props: {
    post: {
      type: Object,
      required: true
    },
    showPreview: {
      type: Boolean,
      default: true
    }
  },
  data() {
    return {
      commentCount: 0
    }
  },
  computed: {
    contentPreview() {
      if (!this.post.content) return '';
      return this.post.content.length > 150 
        ? this.post.content.substring(0, 150) + '...' 
        : this.post.content;
    }
  },
  methods: {
    formatTimeAgo(timestamp) {
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
    },
    async fetchCommentCount() {
      try {
        const response = await fetch(`http://localhost:5003/api/comments/post/${this.post.post_id}`);
        if (response.ok) {
          const data = await response.json();
          this.commentCount = data.data.comments ? data.data.comments.length : 0;
        }
      } catch (error) {
        console.error('Error fetching comment count:', error);
        this.commentCount = 0;
      }
    },
    viewComments(event) {
      event.preventDefault();
      this.$router.push(`/post/${this.post.post_id}`);
    },
    sharePost(event) {
      event.preventDefault();
      // Share functionality - could use navigator.share if available
      const shareUrl = `${window.location.origin}/post/${this.post.post_id}`;
      
      if (navigator.share) {
        navigator.share({
          title: this.post.title,
          text: 'Check out this post',
          url: shareUrl
        });
      } else {
        // Fallback - copy to clipboard
        navigator.clipboard.writeText(shareUrl)
          .then(() => alert('Link copied to clipboard!'))
          .catch(err => console.error('Could not copy text: ', err));
      }
    },
    reportPost(event) {
      event.preventDefault();
      // Simple confirmation for reporting
      if (confirm('Are you sure you want to report this post?')) {
        // Here you would make an API call to report the post
        alert('Post reported. Thank you for helping keep the community safe.');
      }
    }
  },
  mounted() {
    this.fetchCommentCount();
  }
}
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