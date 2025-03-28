<template>
  <h1 class="heading">Inbox</h1>
  <hr />
  <div class="d-flex flex-column">
     <div v-if="isLoading" class="text-center py-5">
      <div class="spinner-border" role="status">
        <span class="visually-hidden">Loading...</span>
      </div>
    </div>
    <div v-else class="list-group">
      <InboxMessage 
        v-for="message in messages" 
        :key="message.message_id"
        :subject="message.subject"
        :content="message.content"
        :time="formatTime(message.created_at)"
        :unread="message.status === 'unread'"
        @open="openMessage(message)"
      />
      
      <div v-if="messages.length === 0 && messagesLoaded == true" class="text-center p-4 text-muted">
        Your inbox is empty
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, watch, onUnmounted } from 'vue'
import { io } from 'socket.io-client'
import { useAuth0 } from '@auth0/auth0-vue'
import InboxMessage from '../components/InboxMessage.vue'

const { user, isAuthenticated, isLoading } = useAuth0()
const messages = ref([])
const socket = ref(null)
const isConnected = ref(false)
const messagesLoaded = ref(false)

const fetchMessages = async () => {
  if (!user.value?.sub) return

  try {
    messagesLoaded.value = false
    const res = await fetch('http://localhost:5006/api/inbox/' + user.value.sub)
    if (!res.ok) {
      throw new Error(`HTTP error! Status: ${res.status}`)
    }
    const data = await res.json()
    messages.value = data
    messagesLoaded.value = true
    console.log('Messages loaded:', data)
  } catch (err) {
    console.error('Failed to fetch messages:', err)
  }
}

const setupSocketConnection = () => {
  if (isConnected.value) return
  
  socket.value = io('http://localhost:5006')
  socket.value.on('connect', () => {
    isConnected.value = true
    console.log('Socket connected')
  })
  
  socket.value.on('new_message', (message) => {
    messages.value.unshift(message) // Add new messages to the top
    console.log('New message received:', message)
  })
  
  socket.value.on('disconnect', () => {
    isConnected.value = false
    console.log('Socket disconnected')
  })
}

const openMessage = async (message) => {
  if (message.status === 'unread') {
    await markAsRead(message.message_id)
    const index = messages.value.findIndex(m => m.message_id === message.message_id)
    if (index !== -1) {
      messages.value[index].status = 'read'
    }
  }
}

const markAsRead = async (messageId) => {
  try {
    const res = await fetch(`http://localhost:5006/api/inbox/read/${messageId}`, {
      method: 'POST',
    })
    if (res.ok) {
      console.log(`Message ${messageId} marked as read`)
    }
  } catch (err) {
    console.error('Failed to mark as read:', err)
  }
}

// Format timestamp into a human-readable format
const formatTime = (timestamp) => {
  if (!timestamp) return 'now';
  
  const messageDate = new Date(timestamp);
  const now = new Date();
  const diffMs = now - messageDate;
  const diffDays = Math.floor(diffMs / (1000 * 60 * 60 * 24));
  
  // Handle case where message timestamp is newer than current time
  // (happens with timezone issues or slightly future-dated messages)
  if (diffMs < 0) {
    return 'just now';
  }
  
  if (diffDays === 0) {
    // Today: show time
    return messageDate.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
  } else if (diffDays === 1) {
    return 'yesterday';
  } else if (diffDays < 7) {
    return `${diffDays}d`;
  } else {
    // More than a week ago: show date
    return messageDate.toLocaleDateString();
  }
};

// Watch for authentication state changes
watch(
  [isAuthenticated, isLoading, user],
  ([newIsAuthenticated, newIsLoading, newUser]) => {
    if (newIsAuthenticated && !newIsLoading && newUser?.sub) {
      console.log('Auth state ready, fetching messages')
      fetchMessages()
      setupSocketConnection()
    }
  },
  { immediate: true }
)

onUnmounted(() => {
  if (socket.value) {
    socket.value.disconnect()
    console.log('Socket disconnected on unmount')
  }
})
</script>