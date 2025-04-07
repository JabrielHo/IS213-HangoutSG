<script setup>
import { ref, onMounted } from 'vue'
import ReportCard from '@/components/ReportCard.vue'
import { useAuth0 } from '@auth0/auth0-vue'

const { isAuthenticated, user } = useAuth0()

const errorMessage = ref('')
const flagged_content = ref([])  // Stores flagged content reports
const isLoading = ref(true)

const checkLogin = async () => {
  if (!isAuthenticated.value || !user.value || !user['https://hangoutsg.com/roles']?.includes('admin')) {
    errorMessage.value = 'You need to be an admin to view this page'
  }
}

const fetchReports = async () => {
  try {
    isLoading.value = true;

    // Send the fetch request to the API
    const response = await fetch('http://localhost:8000/api/moderation/get/', {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
    });

    if (response.ok) {
      // Parse the response JSON
      const data = await response.json();
      if (data.code === 200) {
        // Update flagged_content with the list of flagged content
        flagged_content.value = data.flagged_content;
      } else {
        console.log('No reported content found:', data.message);
      }
    } else {
      console.error('Error fetching reports:', response.status, response.statusText);
    }
  } catch (err) {
    console.error('Error fetching reports:', err);
  } finally {
    // Set loading to false once the request completes
    isLoading.value = false;
  }
};

// Handle resolve action for a report
const handleBan = async (flagId) => {
  console.log(`Ban report with flag_id: ${flagId}`)
  
  try {
    // Send POST request to /api/ban/content
    const response = await fetch('http://localhost:8000/api/ban/content', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ flagId }), // Send flagId in the request body
    });

    if (response.ok) {
      console.log(`Successfully banned content with flag_id: ${flagId}`)
      
      // Optionally, update the status in the local state (e.g., set as 'resolved')
      const flagged = flagged_content.value.find(content => content.flag_id === flagId);
      if (flagged) {
        flagged.status = 'banned'; // Update status to 'banned' or 'resolved' as needed
      }
      alert('The report has been successfully banned.');

      location.reload();

    } else {
      const errorData = await response.json();
      console.error(`Failed to ban content. Error: ${errorData.message}`);
    }
  } catch (error) {
    console.error(`Error while banning content: ${error.message}`);
    alert('An error occurred while trying to ban the content. Please try again later.');

    location.reload();
  }
}

const handleIgnore = async (flagId) => {
  console.log(`Ignore report with flag_id: ${flagId}`)
  try {
    // Send an empty POST request to the appropriate API URL
    const response = await fetch(`http://localhost:8000/api/moderation/delete/flag/${flagId}`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
    });

    if (response.ok) {
      console.log(`Successfully ignored and deleted report with flag_id: ${flagId}`);
    } else {
      const errorData = await response.json();
      console.error(`Failed to ignore the content. Error: ${errorData.message}`);
    }
    alert('The report has been successfully ignored.');

    location.reload();
  } catch (error) {
    console.error(`Error while ignoring content: ${error.message}`);
    alert('An error occurred while trying to ignore the content. Please try again later.');

    location.reload();
  }

}

onMounted(() => {
  // Check for error params
  () => isAuthenticated.value,
  (newAuth) => {
    if (newAuth) {
      checkLogin()
    }
  }
  
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
      @ban="handleBan"
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
