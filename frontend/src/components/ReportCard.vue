<template>
  <div class="report-card">
    <div class="card-header">
      <span class="report-type">
        {{ content.post_id ? '📮 Post' : '💬 Comment' }}
      </span>
    </div>

    <div class="card-content">
      <p class="reported-content">{{ getContentPreview }}</p>
      <div class="report-meta">
        <div class="meta-item">
          <span class="meta-label">Reported by:</span>
          <span class="meta-value">@{{ content.flagged_by }}</span>
        </div>
        <div class="meta-item">
          <span class="meta-label">Reason:</span>
          <span class="meta-value">{{ content.reason }}</span>
        </div>
        <div class="meta-item">
          <span class="meta-label">Reported on:</span>
          <span class="meta-value">{{ formattedDate }}</span>
        </div>
      </div>
    </div>

    <!-- Action buttons outside the content -->
    <div class="card-actions">
      <button 
        class="action-btn ban-btn"
        @click.stop="$emit('ban', content.flag_id)"
      >
        Ban
      </button>
      <button 
        class="action-btn ignore-btn"
        @click.stop="$emit('ignore', content.flag_id)"
      >
        Ignore
      </button>
    </div>
  </div>
</template>

<script setup>
import { computed, ref, onMounted } from 'vue'

const props = defineProps({
  content: {
    type: Object,
    required: true
  }
})

const getContentPreview = ref('Loading...')  // Initially set to "Loading..."

const formattedDate = computed(() => {
  return new Date(props.content.created_at).toLocaleDateString('en-SG', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  })
})

const fetchContent = async () => {
  try {
    if (props.content.post_id) {
      // Fetch post content if it's a post
      const postResponse = await fetch(`http://localhost:5002/api/post/${props.content.post_id}`);
      if (postResponse.ok) {
        const postData = await postResponse.json();
        getContentPreview.value = postData.data.content || 'No content available for this post.';
      } else {
        getContentPreview.value = 'Failed to load post content.';
      }
    } else if (props.content.comment_id) {
      // Fetch comment content if it's a comment
      const commentResponse = await fetch(`http://localhost:5003/api/comment/${props.content.comment_id}`);
      if (commentResponse.ok) {
        const commentData = await commentResponse.json();
        getContentPreview.value = commentData.data.content || 'No content available for this comment.';
      } else {
        getContentPreview.value = 'Failed to load comment content.';
      }
    }
  } catch (error) {
    console.error('Error fetching content:', error);
    getContentPreview.value = 'Error fetching content.';
  }
}

// Fetch content when the component is mounted
onMounted(() => {
  fetchContent();
});
</script>


<style scoped>
.report-card {
  background: #ffffff;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  overflow: hidden;
  transition: transform 0.2s ease;
}

.report-card:hover {
  transform: translateY(-2px);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem;
  background-color: #f8f9fa;
  border-bottom: 1px solid #e9ecef;
}

.report-type {
  font-weight: 600;
  color: #2c3e50;
}

.report-status {
  font-size: 0.875rem;
  padding: 0.25rem 0.5rem;
  border-radius: 20px;
}

.status-pending {
  background-color: #ffe08a;
  color: #946c00;
}

.status-resolved {
  background-color: #48c774;
  color: #257942;
}

.status-ignored {
  background-color: #f14668;
  color: #b13d3d;
}

.card-content {
  padding: 1.5rem;
}

.reported-content {
  color: #4a4a4a;
  margin-bottom: 1rem;
  line-height: 1.5;
  white-space: normal;  /* Allow text to wrap naturally */
  overflow: visible;    /* Ensure no overflow clipping */
  text-overflow: clip;  /* Ensure no ellipsis at the end */
}

.report-meta {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
  gap: 1rem;
  margin-top: 1rem;
}

.meta-item {
  display: flex;
  flex-direction: column;
}

.meta-label {
  font-size: 0.875rem;
  color: #6c757d;
}

.meta-value {
  font-weight: 500;
  color: #2c3e50;
  margin-top: 0.25rem;
}
.card-actions {
  display: flex;
  gap: 0.75rem;
  padding: 1rem;
  border-top: 1px solid #e9ecef;
}

.action-btn {
  flex: 1;
  padding: 0.75rem 1.5rem;
  border: none;
  border-radius: 6px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease;
}

.ban-btn {
  background-color: #e74c3c;  /* Red for Ban */
  color: white;
}

.ban-btn:hover {
  background-color: #c0392b;  /* Darker red on hover */
}

.ignore-btn {
  background-color: #27ae60;  /* Green for Ignore */
  color: white;
}

.ignore-btn:hover {
  background-color: #2ecc71;  /* Darker green on hover */
}

</style>