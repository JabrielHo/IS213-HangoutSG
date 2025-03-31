<script setup>
import { defineProps } from 'vue';

const props = defineProps({
  community: {
    type: Object,
    required: true
  }
});

// Helper functions
function getRandomColor(seed) {
  // Generate a consistent color based on the community name
  let hash = 0
  for (let i = 0; i < seed.length; i++) {
    hash = seed.charCodeAt(i) + ((hash << 5) - hash)
  }

  const colors = [
    '#4285f4',
    '#ea4335',
    '#fbbc05',
    '#34a853',
    '#673ab7',
    '#3f51b5',
    '#2196f3',
    '#009688',
    '#ff5722',
  ]

  return colors[Math.abs(hash) % colors.length]
}

function truncateDescription(text, maxLength) {
  if (!text) return ''
  return text.length > maxLength ? text.substring(0, maxLength) + '...' : text
}
</script>

<template>
  <div class="community-card">
    <div class="card-img-top" :style="{ backgroundColor: getRandomColor(props.community.name) }">
      <span class="community-initial">{{ props.community.name.charAt(0) }}</span>
    </div>
    <div class="card-body">
      <h3 class="card-title">{{ props.community.name }}</h3>
      <p class="card-text">{{ truncateDescription(props.community.description, 100) }}</p>
      <div class="community-stats">
        <span><i class="bi bi-people-fill"></i> {{ props.community.members_count || 0 }} members</span>
        <span><i class="bi bi-calendar-event"></i> {{ props.community.events_count || 0 }} events</span>
      </div>
    </div>
  </div>
</template>

<style scoped>
.community-card {
  border-radius: 8px;
  overflow: hidden;
  box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
  transition: transform 0.3s ease, box-shadow 0.3s ease;
  cursor: pointer;
  background-color: white;
  height: 100%;
}

.community-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 5px 15px rgba(0, 0, 0, 0.1);
}

.card-img-top {
  height: 120px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.community-initial {
  font-size: 3rem;
  font-weight: bold;
  color: white;
}

.card-body {
  padding: 1.25rem;
}

.card-title {
  font-size: 1.25rem;
  margin-bottom: 0.75rem;
  font-weight: 600;
}

.card-text {
  color: #6c757d;
  margin-bottom: 1rem;
}

.community-stats {
  display: flex;
  justify-content: space-between;
  font-size: 0.875rem;
  color: #6c757d;
}
</style>