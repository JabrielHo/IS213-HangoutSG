<template>
  <div class="accordion-item message-item" :class="{ 'unread': unread }">
    <h2 class="accordion-header" :id="headerId">
      <button 
        class="accordion-button collapsed" 
        type="button" 
        data-bs-toggle="collapse" 
        :data-bs-target="'#' + collapseId" 
        aria-expanded="false" 
        :aria-controls="collapseId"
        @click="handleOpen"
      >
        <div class="d-flex w-100 justify-content-between align-items-center">
          <div>{{ subject }}</div>
          <small class="opacity-50 text-nowrap me-2">{{ time }}</small>
        </div>
      </button>
    </h2>
    <div 
      :id="collapseId" 
      class="accordion-collapse collapse" 
      :aria-labelledby="headerId" 
      data-bs-parent="#messagesAccordion"
    >
      <div class="accordion-body">
        <p class="mb-3">{{ content }}</p>
        <div class="d-flex justify-content-end">
          <button class="btn btn-danger btn-sm" @click.stop="$emit('delete')">
            <i class="bi bi-trash"></i> Delete
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue';

const props = defineProps({
  messageId: {
    type: String,
    required: true
  },
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
});

const headerId = computed(() => `heading-${props.messageId}`);
const collapseId = computed(() => `collapse-${props.messageId}`);

const emit = defineEmits(['open', 'delete']);

const handleOpen = () => {
  emit('open');
};
</script>

<style scoped>
.message-item {
  transition: background-color 0.15s ease;
}

.message-item .accordion-button {
  background-color: #f2f2f2; /* Gmail's read message color */
  color: #666;
  padding: 0.75rem 1.25rem;
}

.message-item .accordion-button:not(.collapsed) {
  background-color: #eaf1fb; /* Light blue when expanded */
  color: #1a73e8;
}

.message-item .accordion-button:focus {
  box-shadow: none;
  border-color: rgba(0,0,0,0.125);
}

.message-item:hover .accordion-button {
  background-color: #f0f0f0;
}

.unread .accordion-button {
  background-color: #ffffff; /* Gmail's unread message background (white) */
  color: #202124; /* Gmail's unread message text color (dark) */
  font-weight: 600;
  position: relative;
}

.unread .accordion-button::before {
  content: "";
  position: absolute;
  left: 0;
  top: 0;
  bottom: 0;
  width: 5px;
  background-color: #1a73e8; /* Gmail's unread indicator color */
}

.accordion-body {
  background-color: #ffffff;
  padding: 1rem 1.25rem;
}
</style>