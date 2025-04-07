<script setup>
import { ref, onMounted, onBeforeUnmount } from 'vue';

// Sample data for carousel
const events = ref([
  {
    id: 1,
    title: 'Photography Workshop',
    description: 'Learn the basics of photography in this hands-on workshop',
    location: 'Central Library',
    eventDate: '2025-04-15T14:00',
    capacity: 20,
    image: 'https://placehold.co/600x400/orange/white?text=Photography+Workshop'
  },
  {
    id: 2,
    title: 'Hiking Adventure',
    description: 'Join us for a scenic hike through the nature reserve',
    location: 'MacRitchie Reservoir',
    eventDate: '2025-04-20T08:00',
    capacity: 15,
    image: 'https://placehold.co/600x400/green/white?text=Hiking+Adventure'
  },
  {
    id: 3,
    title: 'Board Game Night',
    description: 'Fun evening of strategy games and new friends',
    location: 'The Mind Café',
    eventDate: '2025-04-12T19:00',
    capacity: 30,
    image: 'https://placehold.co/600x400/purple/white?text=Board+Game+Night'
  }
]);

// Sample communities for dropdown
const communities = ref([
  { id: 'sports-123', name: 'Sports & Fitness' },
  { id: 'tech-456', name: 'Tech Enthusiasts' },
  { id: 'art-789', name: 'Art & Photography' },
  { id: 'food-101', name: 'Food & Cooking' },
  { id: 'music-202', name: 'Music Lovers' }
]);

// Form data
const newEvent = ref({
  communityId: '',
  title: '',
  description: '',
  location: '',
  eventDate: '',
  capacity: null
});

// Carousel controls
const currentSlide = ref(0);

const nextSlide = () => {
  currentSlide.value = (currentSlide.value + 1) % events.value.length;
};

const prevSlide = () => {
  currentSlide.value = (currentSlide.value - 1 + events.value.length) % events.value.length;
};

// Form submission
const submitForm = () => {
  console.log('Event submitted:', newEvent.value);
  // Here you would typically send the data to your backend
  alert('Event created successfully!');
  
  // Reset form
  newEvent.value = {
    communityId: '',
    title: '',
    description: '',
    location: '',
    eventDate: '',
    capacity: null
  };
};

// Automatically rotate carousel every 5 seconds
let carouselInterval;
onMounted(() => {
  carouselInterval = setInterval(() => {
    nextSlide();
  }, 5000);
});

// Clean up interval when component is unmounted
onBeforeUnmount(() => {
  clearInterval(carouselInterval);
});
</script>

<template>
  <h1 class="heading">Events</h1>
  <p>
    Looking for something to do? Discover exciting HangoutSG events happening near you! Explore a
    wide range of hobbies and meet fellow enthusiasts. Find your next adventure today!
  </p>

  <hr />

  <!-- Event Carousel -->
  <div class="carousel-container">
    <h2>Upcoming Events</h2>
    <div class="carousel">
      <button class="carousel-control prev" @click="prevSlide">&#10094;</button>
      
      <div class="carousel-content">
        <div 
          v-for="(event, index) in events" 
          :key="event.id"
          class="carousel-slide"
          :class="{ active: index === currentSlide }"
        >
          <div class="event-card">
            <img :src="event.image" :alt="event.title" class="event-image">
            <div class="event-details">
              <h3>{{ event.title }}</h3>
              <p><strong>Date:</strong> {{ new Date(event.eventDate).toLocaleString() }}</p>
              <p><strong>Location:</strong> {{ event.location }}</p>
              <p>{{ event.description }}</p>
              <p><strong>Capacity:</strong> {{ event.capacity }} people</p>
              <button class="register-btn">Register Now</button>
            </div>
          </div>
        </div>
      </div>
      
      <button class="carousel-control next" @click="nextSlide">&#10095;</button>
    </div>
    
    <div class="carousel-indicators">
      <span 
        v-for="(event, index) in events" 
        :key="`indicator-${index}`"
        class="indicator" 
        :class="{ active: index === currentSlide }"
        @click="currentSlide = index"
      ></span>
    </div>
  </div>

  <hr />

  <!-- Create Event Form -->
  <div class="create-event">
    <h2>Create New Event</h2>
    <form @submit.prevent="submitForm">
      <div class="form-group">
        <label for="communityId">Community*</label>
        <select 
          id="communityId" 
          v-model="newEvent.communityId" 
          required
          class="form-select"
        >
          <option value="" disabled>Select a community</option>
          <option 
            v-for="community in communities" 
            :key="community.id" 
            :value="community.id"
          >
            {{ community.name }} ({{ community.id }})
          </option>
        </select>
      </div>
      
      <div class="form-group">
        <label for="title">Event Title*</label>
        <input 
          type="text" 
          id="title" 
          v-model="newEvent.title" 
          required
          placeholder="Enter a descriptive title"
        >
      </div>
      
      <div class="form-group">
        <label for="description">Description*</label>
        <textarea 
          id="description" 
          v-model="newEvent.description" 
          required
          rows="4"
          placeholder="Describe your event"
        ></textarea>
      </div>
      
      <div class="form-group">
        <label for="location">Location*</label>
        <input 
          type="text" 
          id="location" 
          v-model="newEvent.location" 
          required
          placeholder="Where will the event be held?"
        >
      </div>
      
      <div class="form-group">
        <label for="eventDate">Event Date and Time*</label>
        <input 
          type="datetime-local" 
          id="eventDate" 
          v-model="newEvent.eventDate" 
          required
        >
      </div>
      
      <div class="form-group">
        <label for="capacity">Capacity*</label>
        <input 
          type="number" 
          id="capacity" 
          v-model="newEvent.capacity" 
          required
          min="1"
          placeholder="Maximum number of participants"
        >
      </div>
      
      <button type="submit" class="submit-btn">Create Event</button>
    </form>
  </div>
</template>

<style>
.heading {
  color: #333;
  margin-bottom: 15px;
}

hr {
  margin: 30px 0;
  border: 0;
  border-top: 1px solid #eee;
}

/* Carousel Styles */
.carousel-container {
  margin: 40px 0;
}

.carousel {
  position: relative;
  display: flex;
  align-items: center;
  margin: 20px 0;
}

.carousel-content {
  flex: 1;
  overflow: hidden;
  position: relative;
  height: 400px;
}

.carousel-slide {
  position: absolute;
  width: 100%;
  height: 100%;
  opacity: 0;
  transition: opacity 0.5s ease;
}

.carousel-slide.active {
  opacity: 1;
}

.carousel-control {
  background: rgba(0, 0, 0, 0.3);
  color: white;
  border: none;
  padding: 10px 15px;
  font-size: 18px;
  cursor: pointer;
  z-index: 10;
  border-radius: 50%;
  margin: 0 10px;
}

.carousel-control:hover {
  background: rgba(0, 0, 0, 0.5);
}

.carousel-indicators {
  display: flex;
  justify-content: center;
  margin-top: 15px;
}

.indicator {
  width: 12px;
  height: 12px;
  background: #ccc;
  border-radius: 50%;
  margin: 0 5px;
  cursor: pointer;
}

.indicator.active {
  background: #333;
}

/* Event Card Styles */
.event-card {
  display: flex;
  background: #f8f8f8;
  border-radius: 8px;
  overflow: hidden;
  height: 100%;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
}

.event-image {
  width: 40%;
  object-fit: cover;
}

.event-details {
  padding: 20px;
  flex: 1;
}

.register-btn {
  background: #4CAF50;
  color: white;
  border: none;
  padding: 8px 16px;
  border-radius: 4px;
  cursor: pointer;
  margin-top: 10px;
}

.register-btn:hover {
  background: #45a049;
}

/* Form Styles */
.create-event {
  margin-bottom: 50px;
}

.form-group {
  margin-bottom: 20px;
}

.form-group label {
  display: block;
  margin-bottom: 5px;
  font-weight: bold;
}

.form-group input,
.form-group textarea,
.form-group select {
  width: 100%;
  padding: 10px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 16px;
}

.form-group input[type="number"] {
  width: 200px;
}

.form-select {
  appearance: none;
  background-image: url("data:image/svg+xml;charset=utf-8,%3Csvg xmlns='http://www.w3.org/2000/svg' width='16' height='16' viewBox='0 0 24 24' fill='none' stroke='%23333' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'%3E%3Cpath d='M6 9l6 6 6-6'/%3E%3C/svg%3E");
  background-repeat: no-repeat;
  background-position: right 10px center;
  background-size: 16px;
  padding-right: 30px;
}

.submit-btn {
  background: #2196F3;
  color: white;
  border: none;
  padding: 12px 20px;
  font-size: 16px;
  border-radius: 4px;
  cursor: pointer;
}

.submit-btn:hover {
  background: #0b7dda;
}

/* Responsive Adjustments */
@media (max-width: 768px) {
  .event-card {
    flex-direction: column;
  }
  
  .event-image {
    width: 100%;
    height: 200px;
  }
}
</style>