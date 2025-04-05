<script setup>
import { ref, onMounted } from 'vue'
import ReportCard from '@/components/ReportCard.vue'
import ReportDetails from '@/components/ReportDetails.vue'

const errorMessage = ref('')
const flagged_content = ref([])  // Stores flagged content reports
const selectedReport = ref(null)  // Store the selected report
const isLoading = ref(true)

// Simulating fake reports data for testing and styling
const fakeReports = [
  {
    flag_id: 1,
    poster_id: 101,
    comment_id: 201,
    flagged_by: 301,
    reason: 'Offensive language',
    status: 'pending',
    created_at: '2025-04-06T12:00:00Z',
  },
  {
    flag_id: 2,
    poster_id: 102,
    comment_id: 202,
    flagged_by: 302,
    reason: 'Spam',
    status: 'pending',
    created_at: '2025-04-05T15:30:00Z',
  },
  {
    flag_id: 3,
    poster_id: 103,
    comment_id: 203,
    flagged_by: 303,
    reason: 'Hate speech',
    status: 'pending',
    created_at: '2025-04-04T09:15:00Z',
    comment_content: 'i love hitler'
  },
  {
    flag_id: 4,
    post_id: 101,
    poster_id: 1,
    flagged_by: 2,
    reason: 'Offensive language',
    status: 'pending',
    created_at: '2025-04-06T10:00:00',
    post_content: 'fuck u crybaby',
  },
  {
    flag_id: 5,
    post_id: 102,
    poster_id: 3,
    flagged_by: 4,
    reason: 'Spam',
    status: 'pending',
    created_at: '2025-04-06T11:00:00',
    post_content: 'Check out my amazing new product! Only today, 50% off!',
  },
  {
    flag_id: 6,
    post_id: 103,
    poster_id: 5,
    flagged_by: 6,
    reason: 'Harassment',
    status: 'pending',
    created_at: '2025-04-06T12:00:00',
    post_content: 'You are a terrible person, nobody likes you!',
  }
]

const fetchReports = async () => {
  try {
    isLoading.value = true
    // Simulate an API delay
    setTimeout(() => {
      flagged_content.value = fakeReports
      isLoading.value = false
    }, 1000)  // Simulated 1-second delay
  } catch (err) {
    console.error('Error fetching reports:', err)
  }
}

// Handle resolve action for a report
const handleResolve = (flagId) => {
  console.log(`Resolved report with flag_id: ${flagId}`)
  const flagged = flagged_content.value.find(content => content.flag_id === flagId)
  if (flagged) {
    flagged.status = 'resolved' // Update the status to resolved
  }
}

// Handle ignore action for a report
const handleIgnore = (flagId) => {
  console.log(`Ignored report with flag_id: ${flagId}`)
  const flagged = flagged_content.value.find(content => content.flag_id === flagId)
  if (flagged) {
    flagged.status = 'ignored' // Update the status to ignored
  }
}

// Function to handle when a report card is clicked to view details
const viewReport = (content) => {
  selectedReport.value = content  // Set the selected report to the clicked report
}

onMounted(() => {
  // Check for error params
  const urlParams = new URLSearchParams(window.location.search)
  const error = urlParams.get('error')

  if (error === 'unauthorized') {
    errorMessage.value =
      'You need to be an admin to view this page'
  }

  // Fetch reports
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

  <div v-else class="report-grid">
    <ReportCard
      v-for="content in flagged_content"
      :key="content.flag_id"
      :content="content"
      @resolve="handleResolve"
      @ignore="handleIgnore"
      @click="viewReport(content)"
    />
  </div>

  <!-- Display ReportDetails component when a report is selected -->
  <ReportDetails v-if="selectedReport" :report="selectedReport" />

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
