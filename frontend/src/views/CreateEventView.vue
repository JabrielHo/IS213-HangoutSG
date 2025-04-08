<template>
  <div class="create-event-container">
    <h1>Create a New Event</h1>
    
    <form @submit.prevent="submitEvent" class="event-form">
      <div class="form-group">
        <label for="title">Event Title</label>
        <input 
          type="text" 
          id="title" 
          v-model="event.title" 
          required
          placeholder="Enter event title"
        >
      </div>
      
      <div class="form-group">
        <label for="description">Description</label>
        <textarea 
          id="description" 
          v-model="event.description" 
          required
          placeholder="Describe your event"
          rows="4"
        ></textarea>
      </div>
      
      <div class="form-group">
        <label for="location">Postal Code</label>
        <input 
          type="text" 
          id="location" 
          v-model="event.location" 
          required
          placeholder="Postal Code of Event Venue"
        >
      </div>
      
      <div class="form-group">
        <label for="event_date">Event Date & Time</label>
        <input 
          type="datetime-local" 
          id="event_date" 
          v-model="event.event_date" 
          :min="getCurrentDateTime()"
          required
          @change="validateEventDate"
        >
        <small v-if="dateError" class="text-danger">{{ dateError }}</small>
      </div>
      
      <div class="form-group">
        <label for="capacity">Capacity</label>
        <input 
          type="number" 
          id="capacity" 
          v-model="event.capacity" 
          required
          min="1"
          placeholder="How many people can attend?"
        >
      </div>
      
      <div class="form-group">
        <label for="community">Community</label>
        <select 
          id="community" 
          v-model="event.community_id" 
          required
        >
          <option value="" disabled>Select a community</option>
          <option 
            v-for="community in communities" 
            :key="community.community_id" 
            :value="community.community_id"
          >
            {{ community.name }}
          </option>
        </select>
      </div>
      
      <div class="form-actions">
        <button type="button" @click="goBack" class="cancel-btn" :disabled="loading">Cancel</button>
        <button type="submit" class="submit-btn" :disabled="loading">Create Event</button>
      </div>
    </form>
    
    <!-- Loading overlay -->
    <div v-if="loading" class="loading-overlay">
      <div class="loading-content">
        <div class="spinner"></div>
        <p>Creating your event...</p>
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios';
import { useAuth0 } from '@auth0/auth0-vue';

export default {
  name: 'CreateEventView',
  setup() {
    const { user, isAuthenticated } = useAuth0();
    return { user, isAuthenticated };
  },
  data() {
    return {
      event: {
        title: '',
        description: '',
        location: '',
        event_date: '',
        capacity: 1,
        community_id: '',
        organizer_id: null
      },
      communities: [],
      loading: false,
      error: null,
      dateError: ''
    };
  },
  computed: {
    currentUserId() {
      return this.isAuthenticated && this.user ? this.user.sub : null;
    }
  },
  methods: {
    getCurrentDateTime() {
      // Format current date and time in YYYY-MM-DDThh:mm format for datetime-local input
      const now = new Date();
      const year = now.getFullYear();
      const month = String(now.getMonth() + 1).padStart(2, '0');
      const day = String(now.getDate()).padStart(2, '0');
      const hours = String(now.getHours()).padStart(2, '0');
      const minutes = String(now.getMinutes()).padStart(2, '0');
      
      return `${year}-${month}-${day}T${hours}:${minutes}`;
    },
    validateEventDate() {
      const selectedDate = new Date(this.event.event_date);
      const currentDate = new Date();
      
      if (selectedDate <= currentDate) {
        this.dateError = 'Please select a future date and time';
        return false;
      } else {
        this.dateError = ''; 
        return true;
      }
    },
    async fetchCommunities() {
      try {
        const response = await axios.get('http://localhost:8000/api/community');
        this.communities = response.data.data.communities;
      } catch (error) {
        console.error('Error fetching communities:', error);
        this.error = 'Failed to load communities. Please try again later.';
      }
    },
    async submitEvent() {
      console.log('Submitting event:', this.event);
      this.loading = true;
      
      try {
        // Ensure organizer_id is set to current user
        this.event.organizer_id = this.currentUserId;
        
        // Format the date in the format expected by the server if necessary
        const formattedEvent = { ...this.event };
        
        console.log('Sending request to create event:', formattedEvent);
        const response = await axios.post('http://localhost:8000/api/events', formattedEvent);
        
        console.log('Create event response:', response);
        
        if (response.status === 201 || response.status === 200) {
          alert('Event created successfully!');
          this.$router.push('/events'); // Navigate back to events page
        }
      } catch (error) {
        console.error('Error creating event:', error);
        this.error = 'Failed to create event. Check your fields again';
        alert(this.error);
      } finally {
        this.loading = false;
      }
    },
    goBack() {
      this.$router.go(-1); // Go back to previous page
    }
  },
  created() {
    console.log('CreateEventView component created');
    this.fetchCommunities();
    // Set the organizer_id from the computed property
    this.event.organizer_id = this.currentUserId;
  }
};
</script>

<style scoped>
.create-event-container {
  max-width: 800px;
  margin: 0 auto;
  padding: 2rem;
  position: relative; /* Important for the loading overlay */
}

h1 {
  text-align: center;
  margin-bottom: 2rem;
  color: #333;
}

.event-form {
  background-color: #f9f9f9;
  padding: 2rem;
  border-radius: 8px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
}

.form-group {
  margin-bottom: 1.5rem;
}

label {
  display: block;
  margin-bottom: 0.5rem;
  font-weight: 600;
  color: #555;
}

input,
textarea,
select {
  width: 100%;
  padding: 0.75rem;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 1rem;
}

input:focus,
textarea:focus,
select:focus {
  outline: none;
  border-color: #4a90e2;
  box-shadow: 0 0 0 2px rgba(74, 144, 226, 0.2);
}

.form-actions {
  display: flex;
  justify-content: space-between;
  margin-top: 2rem;
}

button {
  padding: 0.75rem 1.5rem;
  border-radius: 4px;
  font-size: 1rem;
  cursor: pointer;
  transition: all 0.2s;
}

button:disabled {
  opacity: 0.7;
  cursor: not-allowed;
}

.cancel-btn {
  background-color: #f5f5f5;
  border: 1px solid #ddd;
  color: #666;
}

.cancel-btn:hover:not(:disabled) {
  background-color: #e5e5e5;
}

.submit-btn {
  background-color: #4a90e2;
  border: none;
  color: white;
  font-weight: 600;
}

.submit-btn:hover:not(:disabled) {
  background-color: #3a80d2;
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
  border-top: 5px solid #4a90e2;
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