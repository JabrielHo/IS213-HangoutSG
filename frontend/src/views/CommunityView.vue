<script setup>
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import CommunityPost from '../components/CommunityPost.vue'

const route = useRoute()
const community = ref({})
const isLoading = ref(true)
const error = ref(null)

const isJoined = ref(false)
const toggleJoinLeave = () => {
  isJoined.value = !isJoined.value
}

const createPost = () => {}

const fetchCommunityData = async () => {
  try {
    isLoading.value = true
    error.value = null
    const communityName = route.params.community
    const response = await fetch(`http://localhost:8000/api/community/name/${communityName}`)

    if (!response.ok) {
      throw new Error(`HTTP error! Status: ${response.status}`)
    }

    const data = await response.json()
    community.value = data.data
    isLoading.value = false
  } catch (err) {
    console.error('Error fetching community data:', err)
    error.value = "Community doesn't exist!"
    isLoading.value = false
  }
}

onMounted(() => {
  fetchCommunityData()
})
</script>

<template>
  <div v-if="isLoading" class="text-center my-5">
    <div class="spinner-border" role="status">
      <span class="visually-hidden">Loading...</span>
    </div>
  </div>

  <div v-else-if="error" class="alert alert-danger" role="alert">
    {{ error }}
  </div>
  
  <div v-else>
    <div class="d-flex justify-content-between align-items-center">
      <h1 class="heading">{{ community.name }}</h1>
      <div>
        <button @click="createPost" class="btn btn-dark me-2">
          <i class="bi bi-plus-lg"></i>&nbsp;Create Post
        </button>
        <button @click="toggleJoinLeave" class="btn btn-primary">
          {{ isJoined ? 'Leave' : 'Join' }}
        </button>
      </div>
    </div>
    <p>{{ community.description }}</p>
    <hr />

    <div class="list-group">
      <CommunityPost />
    </div>
  </div>
</template>

<style>
.btn {
  border-radius: 15px;
}
</style>