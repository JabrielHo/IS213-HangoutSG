<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAuth0 } from '@auth0/auth0-vue'
const { user, isAuthenticated, isLoading } = useAuth0()

const router = useRouter()
const route = useRoute()
const communityName = route.params.community
console.log(communityName)
const post = ref({
  title: '',
  content: '',
})

const communityId = ref(null)
const isSubmitting = ref(false)
const errorMessage = ref('')

const canSubmit = computed(() => {
  return communityId.value && isAuthenticated.value && user.value && !isLoading.value
})

onMounted(async () => {
  try {
    const response = await fetch(`http://localhost:5001/api/community/name/${communityName}`)
    if (!response.ok) {
      throw new Error('Failed to fetch community information')
    }
    const data = await response.json()
    communityId.value = data.data.community_id
  } catch (error) {
    console.error('Error fetching community ID:', error)
    errorMessage.value = 'Could not load community information. Please try again later.'
  }
})

const submitForm = async () => {
  isSubmitting.value = true
  errorMessage.value = ''

  if (!communityId.value) {
    errorMessage.value = 'Community information not loaded. Please try again.'
    isSubmitting.value = false
    return
  }

  if (!isAuthenticated.value || !user.value) {
    errorMessage.value = 'You must be logged in to create a post.'
    isSubmitting.value = false
    return
  }

  try {
    const authorId = user.value.sub
    if (!authorId) {
      throw new Error('User ID not available')
    }

    const requestBody = {
      ...post.value,
      community_id: communityId.value,
      author_id: authorId,
    }

    const response = await fetch('http://localhost:5002/api/post', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(requestBody),
    })

    if (!response.ok) {
      const errorData = await response.json()
      throw new Error(errorData.message || 'Failed to create post')
    }

    const result = await response.json()
    console.log('Post created successfully:', result)

    await new Promise((resolve) => setTimeout(resolve, 500))

    router.push(`/c/${communityName}`)
  } catch (error) {
    console.error('Error creating post:', error)
    errorMessage.value = error.message || 'An error occurred while creating the post'
  } finally {
    isSubmitting.value = false
  }
}
</script>

<template>
  <div class="container mt-4">
    <h1 class="heading mb-3">Create Post in {{ communityName }}</h1>
    <hr />

    <div v-if="errorMessage" class="alert alert-danger" role="alert">
      {{ errorMessage }}
    </div>

    <div v-if="isLoading" class="text-center my-5">
        <div class="spinner-border" role="status"></div>
    </div>

    <div v-else-if="!isAuthenticated" class="alert alert-warning">
      You need to be logged in to create a post.
    </div>

    <div class="row" v-else>
      <form @submit.prevent="submitForm">
        <div class="mb-3">
          <label for="postTitle" class="form-label">Title</label>
          <input
            type="text"
            class="form-control"
            id="postTitle"
            v-model="post.title"
            required
            :disabled="isSubmitting || !canSubmit"
          />
        </div>

        <div class="mb-3">
          <label for="postContent" class="form-label">Content</label>
          <textarea
            class="form-control"
            id="postContent"
            v-model="post.content"
            rows="6"
            required
            :disabled="isSubmitting || !canSubmit"
          ></textarea>
        </div>
        <div class="d-grid gap-2 d-md-flex justify-content-md-end">
          <button
            type="button"
            class="btn btn-outline-secondary me-md-2"
            @click="router.back()"
            :disabled="isSubmitting"
          >
            Cancel
          </button>
          <button type="submit" class="btn btn-primary" :disabled="isSubmitting || !canSubmit">
            <span
              v-if="isSubmitting"
              class="spinner-border spinner-border-sm me-1"
              role="status"
              aria-hidden="true"
            ></span>
            {{ isSubmitting ? 'Posting...' : 'Create Post' }}
          </button>
        </div>
      </form>
    </div>
  </div>
</template>

<style>
button:disabled {
  cursor: not-allowed;
}
</style>