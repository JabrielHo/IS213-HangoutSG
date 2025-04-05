<template>
  <div class="report-card">
    <div class="card-header">
      <span class="report-type">
        {{ content.post_id ? '📮 Post' : '💬 Comment' }}
      </span>
      <span class="report-status" :class="statusClass">{{ content.status }}</span>
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
          <span class="meta-value reason-badge">{{ content.reason }}</span>
        </div>
        <div class="meta-item">
          <span class="meta-label">Reported on:</span>
          <span class="meta-value">{{ formattedDate }}</span>
        </div>
      </div>
    </div>

    <div class="card-actions">
      <button 
        class="action-btn resolve-btn"
        @click="$emit('resolve', content.flag_id)"
      >
        Resolve
      </button>
      <button 
        class="action-btn ignore-btn"
        @click="$emit('ignore', content.flag_id)"
      >
        Ignore
      </button>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  content: {
    type: Object,
    required: true
  }
})

const getContentPreview = computed(() => {
  const text = content.post_id 
    ? 'Post content preview...' // Replace with actual post content
    : 'Comment content preview...' // Replace with actual comment content
  return text.length > 100 ? text.slice(0, 100) + '...' : text
})

const formattedDate = computed(() => {
  return new Date(props.content.created_at).toLocaleDateString('en-SG', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  })
})

const statusClass = computed(() => {
  return {
    'pending': 'status-pending',
    'resolved': 'status-resolved',
    'ignored': 'status-ignored'
  }[props.content.status.toLowerCase()]
})
</script>

<style scoped>
.report-card {
  background: #ffffff;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
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
  color: #cc0f35;
}

.card-content {
  padding: 1.5rem;
}

.reported-content {
  color: #4a4a4a;
  margin-bottom: 1rem;
  line-height: 1.5;
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

.reason-badge {
  background-color: #f8f9fa;
  padding: 0.25rem 0.5rem;
  border-radius: 4px;
  display: inline-block;
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

.resolve-btn {
  background-color: #27ae60;
  color: white;
}

.resolve-btn:hover {
  background-color: #219653;
}

.ignore-btn {
  background-color: #e74c3c;
  color: white;
}

.ignore-btn:hover {
  background-color: #c0392b;
}
</style>
