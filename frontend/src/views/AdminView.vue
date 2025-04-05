<script setup>
import { ref, onMounted } from 'vue'
import ReportCard from '@/components/ReportCard.vue'

const errorMessage = ref('')
const flagged_content = ref([])
const isLoading = ref(true)

// Fetch all communities
const fetchReports = async () => {
  try {
    isLoading.value = true
    const response = await fetch('http://localhost:5007/api/moderation/get/')

    if (!response.ok) {
      throw new Error(`HTTP error! Status: ${response.status}`)
    }

    const data = await response.json()
    flagged_content.value = data.data.flagged_content
  } catch (err) {
    console.error('Error fetching reports:', err)
  } finally {
    isLoading.value = false
  }
}

onMounted(() => {
  // Check for error params
  const urlParams = new URLSearchParams(window.location.search)
  const error = urlParams.get('error')

  if (error === 'unauthorized') {
    errorMessage.value =
      'You need to be an admin to view this page'
  }

  // Fetch communities
  fetchReports()
})
</script>

<template>
  <div v-if="errorMessage" class="error-alert">
    <span>{{ errorMessage }}</span>
  </div>

  <h1 class="heading">Reported Content</h1>
  <p>
    Please review the following content.
  </p>

  <hr />

  <div v-if="isLoading" class="text-center my-5">
    <div class="spinner-border" role="status">
      <span class="visually-hidden"></span>
    </div>
    <p class="mt-2 text-muted">Loading Reports...</p>
  </div>

  <!-- Communities grid -->
  <div v-else class="report-grid">
    <ReportCard
      v-for="content in flagged_content"
      :key="content.flag_id"
      :content="content"
      @resolve="handleResolve"
      @ignore="handleIgnore"
    />
  </div>
  <div v-if="flagged_content.length === 0 && !isLoading" class="text-center p-4 text-muted">
    No reported content found.
  </div>
</template>

<style scoped>
.report-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 1.5rem;
  margin-top: 2rem;
}

.lead {
  font-size: 1.1rem;
  margin-bottom: 1.5rem;
}
</style>