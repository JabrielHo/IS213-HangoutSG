<template>
  <h1 class="heading">Inbox</h1>
  <hr />
  <div class="d-flex flex-column">
    <div v-if="isLoading || !messagesLoaded" class="text-center py-5">
      <div class="spinner-border" role="status">
        <span class="visually-hidden">Loading...</span>
      </div>
      <p class="mt-2 text-muted">Loading your messages...</p>
    </div>
    <div v-else class="accordion" id="messagesAccordion">
      <InboxMessage
        v-for="message in sortedMessages"
        :key="message.message_id"
        :messageId="message.message_id"
        :subject="message.subject"
        :content="message.content"
        :time="formatTime(message.created_at)"
        :unread="message.status === 'unread'"
        @open="openMessage(message)"
        @delete="deleteMessage(message.message_id)"
      />

      <div
        v-if="messages.length === 0 && messagesLoaded == true"
        class="text-center p-4 text-muted"
      >
        Your inbox is empty
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, watch, onUnmounted, computed } from 'vue'
import { io } from 'socket.io-client'
import { useAuth0 } from '@auth0/auth0-vue'
import InboxMessage from '../components/InboxMessage.vue'

const { user, isAuthenticated, isLoading } = useAuth0()
const messages = ref([])
const socket = ref(null)
const isConnected = ref(false)
const messagesLoaded = ref(false)

const sortedMessages = computed(() => {
  return [...messages.value].sort((a, b) => {
    return new Date(b.created_at) - new Date(a.created_at)
  })
})

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

const deleteMessage = async (messageId) => {
  // Find the message index in our local array
  const index = messages.value.findIndex((m) => m.message_id === messageId)
  if (index === -1) {
    console.error('Message not found in local state')
    return
  }

  const originalMessage = { ...messages.value[index] }

  messages.value = messages.value.filter((m) => m.message_id !== messageId)

  try {
    const res = await fetch(`http://localhost:5006/api/inbox/delete/${messageId}`, {
      method: 'POST',
    })

    if (!res.ok) {
      throw new Error(`HTTP error! Status: ${res.status}`)
    }

    console.log(`Message ${messageId} deleted successfully`)
  } catch (err) {
    console.error('Failed to delete message:', err)

    messages.value.push(originalMessage)

    messages.value = [...messages.value].sort((a, b) => {
      return new Date(b.created_at) - new Date(a.created_at)
    })
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
    // Only add the message if it's intended for the current user
    if (message.receiver_id === user.value.sub) {
      messages.value.unshift(message) // Add new messages to the top
      console.log('New message received:', message)
    }
  })

  socket.value.on('update_message_status', (data) => {
    const { message_id, status } = data
    const index = messages.value.findIndex((m) => m.message_id === message_id)

    if (index !== -1) {
      if (status === 'deleted') {
        // Remove the message from UI if it was deleted
        messages.value = messages.value.filter((m) => m.message_id !== message_id)
      } else {
        // Otherwise update its status
        messages.value[index].status = status
      }
      console.log(`Message ${message_id} status updated to ${status}`)
    }
  })

  socket.value.on('disconnect', () => {
    isConnected.value = false
    console.log('Socket disconnected')
  })
}

const openMessage = async (message) => {
  if (message.status === 'unread') {
    const index = messages.value.findIndex((m) => m.message_id === message.message_id)
    if (index !== -1) {
      messages.value[index].status = 'read'
    }

    markAsRead(message.message_id).catch((err) => {
      console.error('Failed to mark message as read:', err)
      if (index !== -1) {
        messages.value[index].status = 'unread'
      }
    })
  }
}

const markAsRead = async (messageId) => {
  try {
    const res = await fetch(`http://localhost:5006/api/inbox/read/${messageId}`, {
      method: 'POST',
    })

    if (!res.ok) {
      throw new Error(`HTTP error! Status: ${res.status}`)
    }

    console.log(`Message ${messageId} marked as read`)
    return true
  } catch (err) {
    console.error('Failed to mark as read:', err)
    throw err // Re-throw to handle in the calling function
  }
}

// Format timestamp into a human-readable format
const formatTime = (timestamp) => {
  if (!timestamp) return 'now'

  const messageDate = new Date(timestamp)
  const now = new Date()
  const diffMs = now - messageDate
  const diffDays = Math.floor(diffMs / (1000 * 60 * 60 * 24))

  // Handle case where message timestamp is newer than current time
  // (happens with timezone issues or slightly future-dated messages)
  if (diffMs < 0) {
    return 'just now'
  }

  if (diffDays === 0) {
    return messageDate.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
  } else if (diffDays === 1) {
    return 'yesterday'
  } else if (diffDays < 7) {
    return `${diffDays}d`
  } else {
    return messageDate.toLocaleDateString()
  }
}

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