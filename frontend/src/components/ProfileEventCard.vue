<template>
  <div class="event-card">
    <div class="card-header">
      <h3>{{ event.title }}</h3>
      <div class="event-details">
        <p><strong>Date:</strong> {{ formatDate(event.event_date) }}</p>
        <p><strong>Location:</strong> {{ event.location }}</p>
        <p><strong>Capacity:</strong> {{ event.capacity }}</p>
      </div>
    </div>
    <div class="card-body">
      <p>{{ event.description }}</p>
    </div>
  </div>
</template>

<script setup>
defineProps({
  event: {
    type: Object,
    required: true,
  },
})

const formatDate = (dateString) => {
  const date = new Date(dateString)
  return date.toLocaleDateString('en-US', {
    weekday: 'short',
    day: 'numeric',
    month: 'short',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  })
}
</script>

<style scoped>
.event-card {
  border: 1px solid #ddd;
  border-radius: 8px;
  padding: 16px;
  margin-bottom: 20px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  background-color: white;
  transition: transform 0.2s;
}

.event-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.15);
}

.card-header h3 {
  margin-top: 0;
  color: #333;
  font-size: 1.5rem;
}

.event-details {
  margin: 10px 0;
}

.event-details p {
  margin: 5px 0;
  color: #555;
}

.card-body {
  margin: 15px 0;
  color: #666;
}

.card-footer {
  display: flex;
  justify-content: flex-end;
  align-items: center;
  gap: 10px;
}

.register-btn,
.delete-btn {
  border: none;
  padding: 8px 16px;
  border-radius: 4px;
  cursor: pointer;
  font-weight: bold;
  transition: background-color 0.3s;
}

.register-btn {
  background-color: #4caf50;
  color: white;
}

.register-btn:hover {
  background-color: #45a049;
}

.delete-btn {
  background-color: #f44336;
  color: white;
}

.delete-btn:hover {
  background-color: #d32f2f;
}

.registered-text {
  display: inline-block;
  padding: 8px 16px;
  background-color: #e8f5e9;
  color: #4caf50;
  border-radius: 4px;
  font-weight: bold;
}
</style>