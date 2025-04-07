<template>
  <div class="events-container">
    <div class="header-container">
      <h1>Events</h1>
      <div class="create-event-container-top">
        <router-link to="/events-event" class="create-event-btn">Create Event</router-link>
      </div>
    </div>
    
    <p class="welcome-message">
      Looking to join a Event? Discover exciting HangoutSG events happening near you! Explore a wide range of hobbies and meet fellow enthusiasts. Find your next adventure today!
    </p>

    <div class="filter-container">
      <div class="filter-section">
        <label for="communityFilter">Filter by Community:</label>
        <select id="communityFilter" v-model="selectedCommunity" @change="filterEvents">
          <option value="">All Communities</option>
          <option v-for="community in communities" :key="community.community_id" :value="community.community_id">
            {{ community.name }}
          </option>
        </select>
      </div>
      
      <div class="sort-section">
        <span>Sort by:</span>
        <button 
          @click="sortEvents('newest')" 
          :class="{ 'active': sortOrder === 'newest' }"
          class="sort-btn"
        >
          Newest
        </button>
        <button 
          @click="sortEvents('oldest')" 
          :class="{ 'active': sortOrder === 'oldest' }"
          class="sort-btn"
        >
          Oldest
        </button>
      </div>
    </div>

    <div v-if="loading" class="loading">
      Loading events...
    </div>
    
    <div v-else-if="filteredEvents.length === 0" class="no-events">
      <p>No events found. Why not create one?</p>
    </div>
    
    <div v-else class="events-grid">
      <EventCard 
        v-for="event in filteredEvents" 
        :key="event.event_id" 
        :event="event" 
        :userId="currentUserId"
        :isRegistered="isUserRegisteredForEvent(event.event_id)"
        @register-event="registerForEvent"
        @delete-event="confirmDeleteEvent"
      />
    </div>
    
    <!-- Loading overlay for registration and deletion -->
    <div v-if="isProcessing" class="loading-overlay">
      <div class="loading-content">
        <div class="spinner"></div>
        <p>{{ loadingMessage }}</p>
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios';
import EventCard from '@/components/EventCard.vue';
import { useAuth0 } from '@auth0/auth0-vue';
import { useRoute } from 'vue-router'


export default {
  name: 'EventsView',
  components: {
    EventCard
  },
  setup() {
    const { user, isAuthenticated } = useAuth0()
    const route = useRoute()

    return { user, isAuthenticated, route }
  },
  data() {
    return {
      events: [],
      communities: [],
      selectedCommunity: '',
      loading: true,
      error: null,
      sortOrder: 'newest',
      isProcessing: false,
      loadingMessage: '',
      processingEventId: null,
      communityNameFromUrl: null,
      userRegistrations: [], // New data variable to store user registrations
    };
  },
  computed: {
    currentUserId() {
      return this.isAuthenticated && this.user ? this.user.sub : null
    },
    filteredEvents() {
      // First filter by community if one is selected
      let filtered = this.selectedCommunity 
        ? this.events.filter(event => event.community_id === this.selectedCommunity) 
        : this.events;
      
      // Then sort by date
      return filtered.sort((a, b) => {
        const dateA = new Date(a.created_at);
        const dateB = new Date(b.created_at);
        return this.sortOrder === 'newest' ? dateB - dateA : dateA - dateB;
      });
    }
  },
  methods: {
    async fetchEvents() {
      try {
        const response = await axios.get('http://localhost:5004/api/events');
        this.events = response.data.events;
      } catch (error) {
        console.error('Error fetching events:', error);
        this.error = 'Failed to load events. Please try again later.';
      }
    },
    async fetchCommunities() {
      try {
        const response = await axios.get('http://localhost:5001/api/community');
        this.communities = response.data.data.communities;

        if (this.communityNameFromUrl && this.communities.length > 0) {
          const matchingCommunity = this.communities.find(
            (community) => community.name === this.communityNameFromUrl,
          )

          if (matchingCommunity) {
            this.selectedCommunity = matchingCommunity.community_id
          }
        }
      } catch (error) {
        console.error('Error fetching communities:', error);
        this.error = 'Failed to load communities. Please try again later.';
      }
    },
    // New method to fetch user registrations
    async fetchUserRegistrations() {
      if (!this.currentUserId) return;
      
      try {
        const response = await axios.get(`http://localhost:5005/api/registrations/${this.currentUserId}`);
        this.userRegistrations = response.data.events || [];
      } catch (error) {
        console.error('Error fetching user registrations:', error);
      }
    },
    // New method to check if user is registered for a specific event
    isUserRegisteredForEvent(eventId) {
      return this.userRegistrations.some(registration => registration.event_id === eventId);
    },
    filterEvents() {
      // The filtering happens automatically through the computed property
    },
    sortEvents(order) {
      this.sortOrder = order;
    },
    async loadData() {
      this.loading = true;
      if (this.route.params.community) {
        this.communityNameFromUrl = this.route.params.community
      }
      try {
        await Promise.all([
          this.fetchEvents(), 
          this.fetchCommunities(),
          this.fetchUserRegistrations() // Add this to load user registrations
        ]);
      } catch (error) {
        console.error('Error loading data:', error);
      } finally {
        this.loading = false;
      }
    },
    async registerForEvent(eventId) {
      // Check if already registered
      if (this.isUserRegisteredForEvent(eventId)) {
        alert('You are already registered for this event.');
        return;
      }
      
      if (this.isProcessing) return;
      
      // Set processing state
      this.isProcessing = true;
      this.loadingMessage = 'Registering for event...';
      this.processingEventId = eventId;
      
      try {
        await Promise.all([this.fetchEvents(), this.fetchCommunities()])
        const response = await axios.post('http://127.0.0.1:5010/api/register', {
          event_id: eventId,
          user_id: this.currentUserId
        });
        
        // Check both status code and response data for success
        if (response.data && response.data.success) {
          // Add to local registrations to update UI immediately
          this.userRegistrations.push({
            event_id: eventId,
            user_id: this.currentUserId,
            registered_at: new Date().toISOString(),
            registration_id: response.data.registration_id || 'temp-id'
          });
          
          alert('Successfully registered for event!');
        } else {
          // The request was successful but the operation failed
          alert(response.data.message || 'Registration unsuccessful. Please try again.');
        }
      } catch (error) {
        console.error('Error registering for event:', error);
        // Extract error message from response if available
        const errorMessage = error.response?.data?.message || 'Failed to register for event. Please try again.';
        alert(errorMessage);
      } finally {
        // Clear processing state
        this.isProcessing = false;
        this.loadingMessage = '';
        this.processingEventId = null;
      }
    },
    confirmDeleteEvent(eventId) {
      if (confirm('Are you sure you want to delete this event?')) {
        this.deleteEvent(eventId);
      }
    },
    async deleteEvent(eventId) {
      if (this.isProcessing) return;
      
      // Set processing state
      this.isProcessing = true;
      this.loadingMessage = 'Deleting event...';
      this.processingEventId = eventId;
      
      try {
        await axios.delete(`http://localhost:5009/api/events/${eventId}`);
        
        // Remove the deleted event from the events array
        this.events = this.events.filter(event => event.event_id !== eventId);
        alert('Event deleted successfully');
      } catch (error) {
        console.error('Error deleting event:', error);
        alert('Failed to delete event. Please try again.');
      } finally {
        // Clear processing state
        this.isProcessing = false;
        this.loadingMessage = '';
        this.processingEventId = null;
      }
    }
  },
  created() {
    this.loadData();
  }
}
</script>

<style scoped>
.events-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
  position: relative; /* Important for positioning the overlay */
}

.header-container {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 15px;
}

h1 {
  font-size: 2.5rem;
  color: #333;
  margin: 0;
}

.welcome-message {
  font-size: 1.1rem;
  color: #555;
  line-height: 1.6;
  margin-bottom: 30px;
}

.filter-container {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 30px;
  padding: 15px;
  background-color: #f9f9f9;
  border-radius: 8px;
}

.filter-section select {
  padding: 8px 12px;
  border-radius: 4px;
  border: 1px solid #ddd;
  margin-left: 10px;
  font-size: 1rem;
}

.sort-section {
  display: flex;
  align-items: center;
}

.sort-section span {
  margin-right: 10px;
  color: #555;
}

.sort-btn {
  padding: 8px 16px;
  margin-left: 5px;
  border-radius: 4px;
  border: 1px solid #ddd;
  background-color: white;
  cursor: pointer;
  transition: all 0.3s;
}

.sort-btn.active {
  background-color: #333;
  color: white;
}

.events-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 20px;
}

.no-events {
  text-align: center;
  padding: 50px 0;
  color: #666;
  font-style: italic;
}

.loading {
  text-align: center;
  padding: 50px 0;
  color: #666;
}

.create-event-container-top {
  /* No additional styles needed as it inherits the flex layout from header-container */
}

.create-event-btn {
  background-color: #4CAF50;
  color: white;
  text-decoration: none;
  padding: 12px 24px;
  border-radius: 4px;
  font-weight: bold;
  display: inline-block;
  transition: background-color 0.3s;
}

.create-event-btn:hover {
  background-color: #45a049;
}

/* Loading overlay styles */
.loading-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.7);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}

.loading-content {
  background-color: white;
  padding: 30px;
  border-radius: 8px;
  text-align: center;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
}

.spinner {
  border: 5px solid #f3f3f3;
  border-top: 5px solid #4CAF50;
  border-radius: 50%;
  width: 50px;
  height: 50px;
  animation: spin 1s linear infinite;
  margin: 0 auto 20px;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.loading-content p {
  font-size: 18px;
  color: #333;
  margin: 0;
}
</style>