<script setup>
import { ref, onMounted } from 'vue'

const errorMessage = ref('')

onMounted(() => {
  const urlParams = new URLSearchParams(window.location.search)
  const error = urlParams.get('error')
  const errorDescription = urlParams.get('error_description')

  if (error === 'unauthorized' && errorDescription?.includes('user is blocked')) {
    errorMessage.value =
      'Your account has been banned. Please check your email for more information!'
  }
})
</script>

<template>
  <div v-if="errorMessage" class="error-alert">
    <span>{{ errorMessage }}</span>
  </div>

  <h1 class="heading">Home</h1>
  <p>
    Looking to join a community? Discover exciting HangoutSG events happening near you! Explore a
    wide range of hobbies and meet fellow enthusiasts. Find your next adventure today!
  </p>

  <hr />
</template>

<style>
.error-alert {
  background-color: #f8d7da;
  color: #721c24;
  padding: 12px;
  border-radius: 4px;
  margin-bottom: 20px;
  border: 1px solid #f5c6cb;
}
</style>