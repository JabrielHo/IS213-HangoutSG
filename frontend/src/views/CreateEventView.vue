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
          <label for="location">Location</label>
          <input 
            type="text" 
            id="location" 
            v-model="event.location" 
            required
            placeholder="Where will the event be held?"
          >
        </div>
        
        <div class="form-group">
          <label for="event_date">Event Date & Time</label>
          <input 
            type="datetime-local" 
            id="event_date" 
            v-model="event.event_date" 
            required
          >
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
          <button type="button" @click="goBack" class="cancel-btn">Cancel</button>
          <button type="submit" class="submit-btn">Create Event</button>
        </div>
      </form>
    </div>
  </template>
  
  <script>
  import axios from 'axios';
  
  export default {
    name: 'CreateEventView',
    data() {
      return {
        event: {
          title: '',
          description: '',
          location: '',
          event_date: '',
          capacity: 1,
          community_id: '',
          organizer_id: 'auth0|67cd8623469fee2d24e73bfb' // This would typically come from auth service
        },
        communities: [],
        loading: false,
        error: null
      };
    },
    methods: {
      async fetchCommunities() {
        try {
          const response = await axios.get('http://localhost:5001/api/community');
          this.communities = response.data.data.communities;
        } catch (error) {
          console.error('Error fetching communities:', error);
          this.error = 'Failed to load communities. Please try again later.';
        }
      },
      async submitEvent() {
        this.loading = true;
        try {
          // Format the date in the format expected by the server if necessary
          const formattedEvent = { ...this.event };
          
          const response = await axios.post('http://localhost:5004/api/events', formattedEvent);
          
          if (response.status === 201 || response.status === 200) {
            alert('Event created successfully!');
            this.$router.push('/events'); // Navigate back to events page
          }
        } catch (error) {
          console.error('Error creating event:', error);
          this.error = 'Failed to create event. Please try again later.';
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
      this.fetchCommunities();
    }
  }
  </script>
  
  <style scoped>
  .create-event-container {
    max-width: 800px;
    margin: 0 auto;
    padding: 30px;
  }
  
  h1 {
    font-size: 2rem;
    margin-bottom: 30px;
    color: #333;
    text-align: center;
  }
  
  .event-form {
    background-color: white;
    padding: 30px;
    border-radius: 8px;
    box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
  }
  
  .form-group {
    margin-bottom: 20px;
  }
  
  label {
    display: block;
    margin-bottom: 8px;
    font-weight: bold;
    color: #444;
  }
  
  input, textarea, select {
    width: 100%;
    padding: 12px;
    border: 1px solid #ddd;
    border-radius: 4px;
    font-size: 1rem;
  }
  
  textarea {
    resize: vertical;
  }
  
  .form-actions {
    display: flex;
    justify-content: space-between;
    margin-top: 30px;
  }
  
  .cancel-btn, .submit-btn {
    padding: 12px 24px;
    border-radius: 4px;
    font-weight: bold;
    cursor: pointer;
    transition: background-color 0.3s;
  }
  
  .cancel-btn {
    background-color: #f2f2f2;
    color: #333;
    border: 1px solid #ddd;
  }
  
  .submit-btn {
    background-color: #4CAF50;
    color: white;
    border: none;
  }
  
  .cancel-btn:hover {
    background-color: #e6e6e6;
  }
  
  .submit-btn:hover {
    background-color: #45a049;
  }
  </style>