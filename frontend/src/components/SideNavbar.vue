<script setup>
import 'bootstrap-icons/font/bootstrap-icons.css'
import LoginButton from '../components/LoginButton.vue'
import LogoutButton from '../components/LogoutButton.vue'
import SignupButton from '../components/SignupButton.vue'
import { useAuth0 } from '@auth0/auth0-vue'
import { ref, watch, onMounted } from 'vue'

const { isAuthenticated, user, isLoading } = useAuth0()
const communities = ref([])
const isLoadingCommunities = ref(false)

// Function to fetch communities for the authenticated user
const fetchUserCommunities = async () => {
  if (!user.value || !user.value.sub) return
  
  isLoadingCommunities.value = true
  try {
    const userId = user.value.sub
    const response = await fetch(`https://personal-iw6ceuuv.outsystemscloud.com/Community_members/rest/CommunityMemberAPI/communitiesbymember/${userId}`)
    const data = await response.json()
    
    if (data.Result.Success && data.CommunityMemberAPI) {
      // Get the community IDs
      const communityIds = data.CommunityMemberAPI.map(membership => membership.community_id)
      
      // For each community ID, fetch details to get the name
      const communityDetailsPromises = communityIds.map(async (id) => {
        try {
          const detailsResponse = await fetch(`http://localhost:5001/api/community/${id}`)
          const detailsData = await detailsResponse.json()
          
          if (detailsData.code === 200 && detailsData.data) {
            return {
              id: detailsData.data.community_id,
              name: detailsData.data.name
            }
          }
          return { id, name: id } // Fallback to ID if response format is unexpected
        } catch (err) {
          console.error(`Failed to fetch details for community ${id}:`, err)
          return { id, name: id } // Fallback to ID if request fails
        }
      })
      
      // Wait for all detail requests to complete
      const communityDetails = await Promise.all(communityDetailsPromises)
      communities.value = communityDetails.filter(Boolean) // Filter out any undefined values
    }
  } catch (error) {
    console.error('Failed to fetch user communities:', error)
  } finally {
    isLoadingCommunities.value = false
  }
}

// Watch for user authentication state changes
watch(() => user.value, (newUser) => {
  if (newUser && isAuthenticated.value) {
    fetchUserCommunities()
  }
}, { immediate: true })

// Also fetch on component mount if user is already authenticated
onMounted(() => {
  if (isAuthenticated.value && user.value) {
    fetchUserCommunities()
  }
})
</script>

<template>
  <nav class="navbar navbar-dark bg-dark">
    <div class="justify-content-start">
      <button
        v-if="!isLoading"
        class="ms-2 navbar-toggler"
        type="button"
        data-bs-toggle="offcanvas"
        data-bs-target="#offcanvasDarkNavbar"
        aria-controls="offcanvasDarkNavbar"
        aria-label="Toggle navigation"
      >
        <span class="navbar-toggler-icon"></span>
      </button>
      <router-link to="/" class="ms-2 navbar-brand">HangoutSG</router-link>

      <div
        class="offcanvas offcanvas-start text-bg-dark"
        tabindex="-1"
        id="offcanvasDarkNavbar"
        aria-labelledby="offcanvasDarkNavbarLabel"
      >
        <div class="offcanvas-header">
          <button
            type="button"
            class="btn-close btn-close-white"
            data-bs-dismiss="offcanvas"
            aria-label="Close"
          ></button>
        </div>
        <hr class="m-0"/>
        <ul class="nav nav-pills flex-column mb-auto" style="padding: 16px;">
          <li class="nav-item">
            <router-link to="/" class="nav-link text-white" active-class="active">
              <i class="bi bi-house-door-fill"></i>&nbsp; Home</router-link
            >
          </li>
          <li class="nav-item">
            <router-link to="/events" class="nav-link text-white" active-class="active">
              <i class="bi bi-calendar-event-fill"></i>&nbsp; Events</router-link
            >
          </li>
          <li v-if="isAuthenticated" class="nav-item">
            <router-link to="/inbox" class="nav-link text-white" active-class="active">
              <i class="bi bi-envelope-fill"></i>&nbsp; Inbox
            </router-link>
          </li>
          <li v-if="isAuthenticated" class="nav-item">
            <router-link to="/communities/create" class="nav-link text-white" active-class="active">
              <i class="bi bi-plus-circle-fill"></i>&nbsp; Create Community
            </router-link>
          </li>
        </ul>
        <hr class="m-0"/>

        <div v-if="isAuthenticated" class="offcanvas-body">
          <h6 class="text-white ms-2 mb-2">My Communities</h6>
          <ul class="nav nav-pills flex-column mb-auto">
            <div v-if="isLoadingCommunities" class="text-center py-3">
              <div class="spinner-border spinner-border-sm text-light" role="status">
                <span class="visually-hidden">Loading communities...</span>
              </div>
            </div>
            <li v-else-if="communities.length === 0" class="text-white-50 text-center py-2">
              No communities joined yet
            </li>
            <li v-else v-for="community in communities" :key="community.id">
              <router-link :to="`/c/${community.name}`" class="nav-link text-white" active-class="active">
                {{ community.name }}
              </router-link>
            </li>
          </ul>
        </div>
        <hr />
      </div>
    </div>
    <div class="justify-content-end">
      <!-- Show loading state -->
      <div v-if="isLoading" class="spinner-border spinner-border-sm text-light me-2" role="status">
        <span class="visually-hidden">Loading...</span>
      </div>

      <!-- Show login/signup when not authenticated -->
      <div v-else-if="!isAuthenticated" class="d-flex gap-2 me-2">
        <LoginButton />
        <SignupButton />
      </div>

      <!-- Show user profile when authenticated -->
      <div v-else class="dropdown me-2">
        <a
          href="#"
          class="d-flex align-items-center text-white text-decoration-none"
          data-bs-toggle="dropdown"
          aria-expanded="false"
        >
          <img :src="user.picture" alt="" width="32" height="32" class="rounded-circle" />
        </a>
        <ul class="dropdown-menu dropdown-menu-dark dropdown-menu-end text-small shadow">
          <li><router-link class="dropdown-item" to="/profile">Profile</router-link></li>
          <li v-if="user['https://hangoutsg.com/roles'].includes('admin')">
            <router-link class="dropdown-item" to="/admin">Content Moderation</router-link>
          </li>
          <li><hr class="dropdown-divider" /></li>
          <li><LogoutButton /></li>
        </ul>
      </div>
    </div>
  </nav>
</template>

<style scoped></style>