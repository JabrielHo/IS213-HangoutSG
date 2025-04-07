<template>
  <div class="events-container">
    <h1>Events</h1>
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
      />
    </div>

    <div class="create-event-container">
      <router-link to="/create-event" class="create-event-btn">Create Event</router-link>
    </div>
  </div>
</template>

<script>
import axios from 'axios';
import EventCard from '@/components/EventCard.vue';

export default {
  name: 'EventsView',
  components: {
    EventCard
  },
  data() {
    return {
      events: [],
      communities: [],
      selectedCommunity: '',
      loading: true,
      error: null,
      sortOrder: 'newest',
      currentUserId: 'auth0|67cd8623469fee2d24e73bfb' // This would typically come from auth service
    };
  },
  computed: {
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
      } catch (error) {
        console.error('Error fetching communities:', error);
        this.error = 'Failed to load communities. Please try again later.';
      }
    },
    filterEvents() {
      // The filtering happens automatically through the computed property
    },
    sortEvents(order) {
      this.sortOrder = order;
    },
    async loadData() {
      this.loading = true;
      try {
        await Promise.all([this.fetchEvents(), this.fetchCommunities()]);
      } catch (error) {
        console.error('Error loading data:', error);
      } finally {
        this.loading = false;
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
}

h1 {
  font-size: 2.5rem;
  margin-bottom: 15px;
  color: #333;
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

.create-event-container {
  margin-top: 30px;
  text-align: center;
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
</style>