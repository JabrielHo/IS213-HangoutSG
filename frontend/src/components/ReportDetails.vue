<template>
  <div v-if="report">
    <h1>Report Details</h1>

    <div class="report-card-details">
      <div class="card-header">
        <span class="report-type">
          {{ report.post_id ? '📮 Post' : '💬 Comment' }}
        </span>
        <span class="report-status" :class="statusClass">{{ report.status }}</span>
      </div>

      <div class="card-content">
        <p class="full-content-text">{{ report.post_content || report.comment_content }}</p>

        <div class="report-meta">
          <div class="meta-item">
            <span class="meta-label">Reported by:</span>
            <span class="meta-value">@{{ report.flagged_by }}</span>
          </div>
          <div class="meta-item">
            <span class="meta-label">Reason:</span>
            <span class="meta-value">{{ report.reason }}</span>
          </div>
          <div class="meta-item">
            <span class="meta-label">Reported on:</span>
            <span class="meta-value">{{ formattedDate }}</span>
          </div>
        </div>
      </div>

      <div class="card-actions">
        <button class="action-btn resolve-btn" @click="resolveReport">
          Resolve
        </button>
        <button class="action-btn ignore-btn" @click="ignoreReport">
          Ignore
        </button>
      </div>
    </div>
  </div>

  <div v-else>
    <p>Loading report details...</p>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  report: Object  // Receiving the report prop
})

const formattedDate = computed(() => {
  return new Date(props.report.created_at).toLocaleDateString('en-SG', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  })
})

const statusClass = computed(() => {
  const status = props.report.status?.toLowerCase() || 'pending';  // Default to 'pending' if undefined
  return {
    'pending': 'status-pending',
    'resolved': 'status-resolved',
    'ignored': 'status-ignored'
  }[status] || 'status-pending'; // Fallback to 'pending' if status is unknown
})

const resolveReport = () => {
  // Handle resolving the report
}

const ignoreReport = () => {
  // Handle ignoring the report
}
</script>

<style scoped>
.report-details {
  background: #f8f9fa;
  padding: 2rem;
  display: flex;
  justify-content: center;
}

.report-card-details {
  background: #ffffff;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  overflow: hidden;
  max-width: 800px;
  width: 100%;
  transition: transform 0.2s ease;
  padding: 1.5rem;
}

.report-card-details:hover {
  transform: translateY(-2px);
}

.page-title {
  text-align: center;
  font-size: 2rem;
  font-weight: 600;
  margin-bottom: 2rem;
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

.full-content-text {
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