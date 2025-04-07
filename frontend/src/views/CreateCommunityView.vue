<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuth0 } from '@auth0/auth0-vue'
const { user } = useAuth0()

const router = useRouter()
const community = ref({
  name: '',
  description: '',
})

const isSubmitting = ref(false)
const errorMessage = ref('')

const submitForm = async () => {
  isSubmitting.value = true
  errorMessage.value = ''

  try {
    const requestBody = {
      ...community.value,
      creator_id: user.value?.sub || '',
    }

    const response = await fetch('http://localhost:5001/api/community', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(requestBody),
    })

    if (!response.ok) {
      const errorData = await response.json()
      throw new Error(errorData.message || 'Failed to create community')
    }

    const result = await response.json()
    // Join the creator to the community automatically
    if (result && result.data && result.data.community_id) {
      const communityId = result.data.community_id
      const userId = user.value?.sub || ''
      
      try {
        // Make API call to join the community
        const joinUrl = `https://personal-iw6ceuuv.outsystemscloud.com/Community_members/rest/CommunityMemberAPI/communityaddmember/${communityId}/${userId}`
        
        const joinResponse = await fetch(joinUrl, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          }
        })

        if (!joinResponse.ok) {
          console.error('Failed to join the community automatically')
        }
      } catch (joinError) {
        console.error('Error joining community:', joinError)
      }

      const communityName = result.data.name || community.value.name
      router.push('/c/' + communityName.toLowerCase())
    } else {
      router.push('/c/' + community.value.name.toLowerCase())
    }
  } catch (error) {
    console.error('Error creating community:', error)
    errorMessage.value = error.message || 'An error occurred while creating the community'
  } finally {
    isSubmitting.value = false
  }
}
</script>

<template>
  <div class="container mt-4">
    <h1 class="heading mb-3">Create Community</h1>
    <hr />

    <div v-if="errorMessage" class="alert alert-danger" role="alert">
      {{ errorMessage }}
    </div>

    <div class="row">
      <form @submit.prevent="submitForm">
        <div class="mb-3">
          <label for="communityName" class="form-label">Community Name</label>
          <input
            type="text"
            class="form-control"
            id="communityName"
            v-model="community.name"
            minlength="3"
            maxlength="21"
            required
            :disabled="isSubmitting"
          />
          <div class="form-text">Minimum 3 characters & Maximum 21 characters</div>
        </div>

        <div class="mb-3">
          <label for="communityDescription" class="form-label">Description</label>
          <textarea
            class="form-control"
            id="communityDescription"
            v-model="community.description"
            rows="4"
            required
            :disabled="isSubmitting"
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
          <button type="submit" class="btn btn-primary" :disabled="isSubmitting">
            <span
              v-if="isSubmitting"
              class="spinner-border spinner-border-sm me-1"
              role="status"
              aria-hidden="true"
            ></span>
            {{ isSubmitting ? 'Creating...' : 'Create Community' }}
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