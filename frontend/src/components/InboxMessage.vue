<template>
  <div 
    class="list-group-item d-flex gap-3 py-3 message-item" 
    :class="{ 'unread': unread }" 
    @click="$emit('open')"
  >
    <div class="d-flex gap-2 w-100 justify-content-between">
      <div>
        <h6 class="mb-0">{{ subject }}</h6>
        <p class="mb-0 opacity-75">{{ content }}</p>
      </div>
      <small class="opacity-50 text-nowrap">{{ time }}</small>
    </div>
  </div>
</template>

<script setup>
defineProps({
  subject: {
    type: String,
    required: true
  },
  content: {
    type: String,
    required: true
  },
  time: {
    type: String,
    required: true
  },
  unread: {
    type: Boolean,
    default: false
  }
})

defineEmits(['open'])
</script>

<style scoped>
.message-item {
  cursor: pointer;
  transition: background-color 0.15s ease;
  background-color: #f2f2f2; /* Gmail's read message color */
  color: #666;
}

.message-item:hover {
  background-color: #f0f0f0;
}

.unread {
  background-color: #ffffff; /* Gmail's unread message background (white) */
  color: #202124; /* Gmail's unread message text color (dark) */
  font-weight: 600;
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.05);
  position: relative;
}

.unread:before {
  content: "";
  position: absolute;
  left: 0;
  top: 0;
  bottom: 0;
  width: 5px;
  background-color: #1a73e8; /* Gmail's unread indicator color */
  border-top-left-radius: 4px;
  border-bottom-left-radius: 4px;
}
</style>