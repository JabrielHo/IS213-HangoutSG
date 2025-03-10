<!-- <script setup>
</script>

<template>
  <h1 class="heading">Inbox</h1>
  <hr />
  <div class="d-flex flex-column">
    <div class="list-group">
      <div class="list-group-item d-flex gap-3 py-3">
        <div class="d-flex gap-2 w-100 justify-content-between">
          <div>
            <h6 class="mb-0">List group item heading</h6>
            <p class="mb-0 opacity-75">Some placeholder content in a paragraph.</p>
          </div>
          <small class="opacity-50 text-nowrap">now</small>
        </div>
      </div>
      <div class="list-group-item d-flex gap-3 py-3">
        <div class="d-flex gap-2 w-100 justify-content-between">
          <div>
            <h6 class="mb-0">Another title here</h6>
            <p class="mb-0 opacity-75">
              Some placeholder content in a paragraph that goes a little longer so it wraps to a new
              line.
            </p>
          </div>
          <small class="opacity-50 text-nowrap">3d</small>
        </div>
      </div>
    </div>
  </div>
</template>

<style>
</style> -->

<template>
  <div>
    <h2>Inbox</h2>
    <ul>
      <li
        v-for="message in messages"
        :key="message.message_id"
        :class="{ unread: message.status === 'unread' }"
        @click="openMessage(message)"
      >
        {{ message.content }}
      </li>
    </ul>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { io } from 'socket.io-client'

const messages = ref([])
const socket = io('http://localhost:5002')

const fetchMessages = async () => {
  const res = await fetch('http://localhost:5002/get-messages/' + 'auth0|67cd8623469fee2d24e73bfb')
  const data = await res.json()
  messages.value = data
}

const openMessage = async (message) => {
  if (message.status === 'unread') {
    await markAsRead(message.message_id)
  }
}

const markAsRead = async (messageId) => {
  try {
    const res = await fetch(`http://localhost:5002/mark-as-read/${messageId}`, {
      method: 'POST',
    })
    if (res.ok) {
      console.log(`Message ${messageId} marked as read`)
    }
  } catch (err) {
    console.error('Failed to mark as read:', err)
  }
}

onMounted(() => {
  fetchMessages()

  socket.on('new_message', (message) => {
    messages.value.push(message)
    console.log('New message received:', message)
  })

  socket.on('update_message_status', (data) => {
    const msg = messages.value.find((m) => m.message_id === data.message_id)
    if (msg) {
      msg.status = data.status
      console.log(`Message ${data.message_id} status updated to: ${data.status}`)
    }
  })
})
</script>

<style scoped>
.unread {
  font-weight: bold;
  color: red;
  cursor: pointer;
}
</style>
