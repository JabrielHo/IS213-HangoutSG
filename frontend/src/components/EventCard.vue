<template>
    <div class="event-card">
      <div class="card-header">
        <h3>{{ event.title }}</h3>
        <div class="event-details">
          <p><strong>Date:</strong> {{ formatDate(event.event_date) }}</p>
          <p><strong>Location:</strong> {{ event.location }}</p>
          <p><strong>Capacity:</strong> {{ event.capacity }}</p>
        </div>
      </div>
      <div class="card-body">
        <p>{{ event.description }}</p>
      </div>
      <div class="card-footer">
        <button @click="registerForEvent" class="register-btn">Register</button>
      </div>
    </div>
  </template>
  
  <script>
  import axios from 'axios';
  
  export default {
    name: 'EventCard',
    props: {
      event: {
        type: Object,
        required: true
      },
      userId: {
        type: String,
        required: true
      }
    },
    methods: {
      formatDate(dateString) {
        const date = new Date(dateString);
        return date.toLocaleDateString('en-US', {
          weekday: 'short',
          day: 'numeric',
          month: 'short',
          year: 'numeric',
          hour: '2-digit',
          minute: '2-digit'
        });
      },
      async registerForEvent() {
        try {
          const response = await axios.post('http://127.0.0.1:5010/api/register', {
            event_id: this.event.event_id,
            user_id: this.userId
          });
          
          if (response.status === 200) {
            alert('Successfully registered for event!');
          }
        } catch (error) {
          console.error('Error registering for event:', error);
          alert('Failed to register for event. Please try again.');
        }
      }
    }
  }
  </script>
  
  <style scoped>
  .event-card {
    border: 1px solid #ddd;
    border-radius: 8px;
    padding: 16px;
    margin-bottom: 20px;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
    background-color: white;
    transition: transform 0.2s;
  }
  
  .event-card:hover {
    transform: translateY(-5px);
    box-shadow: 0 4px 8px rgba(0, 0, 0, 0.15);
  }
  
  .card-header h3 {
    margin-top: 0;
    color: #333;
    font-size: 1.5rem;
  }
  
  .event-details {
    margin: 10px 0;
  }
  
  .event-details p {
    margin: 5px 0;
    color: #555;
  }
  
  .card-body {
    margin: 15px 0;
    color: #666;
  }
  
  .card-footer {
    display: flex;
    justify-content: flex-end;
  }
  
  .register-btn {
    background-color: #4CAF50;
    color: white;
    border: none;
    padding: 8px 16px;
    border-radius: 4px;
    cursor: pointer;
    font-weight: bold;
    transition: background-color 0.3s;
  }
  
  .register-btn:hover {
    background-color: #45a049;
  }
  </style>