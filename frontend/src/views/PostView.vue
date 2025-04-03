<template>
  <div class="container">
    <div v-if="authLoading || loading" class="text-center my-5">
      <div class="spinner-border text-primary" role="status">
        <span class="visually-hidden">Loading...</span>
      </div>
      <p class="mt-2">Loading post...</p>
    </div>
    
    <div v-else-if="error" class="alert alert-danger my-5">
      {{ error }}
    </div>
    
    <div class="post-view" v-else-if="post">
      <div class="post-details">
        <h2>{{ post.title }}</h2>
        <p class="meta">
          <span class="author">By {{ user.username}}</span> • 
          <span class="date">{{ formatDate(post.created_at) }}</span> • 
          <span class="community">in community: 
            <span v-if="communityLoading">loading...</span>
            <span v-else>{{ communityName }}</span>
          </span>
        </p>
        <div class="content">{{ post.content }}</div>
      </div>

      <hr />

      <!-- Pass actual user data to CommentsPost component -->
      <CommentsPost 
        :postId="$route.params.postId"
        :currentUser="isAuthenticated ? user.sub : 'anonymous'"
      />
    </div>
    
    <div v-else class="alert alert-warning my-5">
      Post not found
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue';
import { useRoute } from 'vue-router';
import { useAuth0 } from '@auth0/auth0-vue';
import CommentsPost from '../components/CommentsPost.vue';

const route = useRoute();
const { user, isAuthenticated, isLoading: authLoading } = useAuth0();

const post = ref(null);
const loading = ref(true);
const error = ref(null);
const communityName = ref('');
const communityLoading = ref(false);

const formatDate = (dateString) => {
  if (!dateString) return '';
  
  const options = { 
    year: 'numeric', 
    month: 'long', 
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  };
  
  return new Date(dateString).toLocaleString(undefined, options);
};

const fetchCommunityInfo = async (communityId) => {
  communityLoading.value = true;
  try {
    const response = await fetch(`http://localhost:5001/api/community/${communityId}`);
    
    if (response.ok) {
      const data = await response.json(); 
      console.log(data.data.name)
      
      if (data.code === 200 ) {
        communityName.value = data.data.name;
      } else {
        communityName.value = 'Unknown Community';
        console.error('Error fetching community:', data.message);
      }
    } else {
      communityName.value = 'Unknown Community';
      console.error('HTTP error fetching community:', response.status);
    }
  } catch (err) {
    communityName.value = 'Unknown Community';
    console.error('Failed to fetch community info:', err);
  } finally {
    communityLoading.value = false;
  }
};

const fetchPost = async () => {
  loading.value = true;
  error.value = null;
  
  const postId = route.params.postId;
  
  try {
    const response = await fetch(`http://localhost:5002/api/post/${postId}`);
    
    if (response.ok) {
      const data = await response.json();
      
      if (data.code === 200 && data.data) {
        post.value = data.data;
        
        // Fetch community information once we have the post
        if (post.value.community_id) {
          await fetchCommunityInfo(post.value.community_id);
        }
      } else {
        error.value = data.message || 'Failed to fetch post';
      }
    } else if (response.status === 404) {
      post.value = null; // Post not found
    } else {
      const errorData = await response.json();
      error.value = errorData.message || `Error ${response.status}: Failed to load post`;
    }
  } catch (err) {
    console.error('Failed to fetch post:', err);
    error.value = 'Network error when fetching post data';
  } finally {
    loading.value = false;
  }
};

// Watch for changes in the route params to reload the post if necessary
watch(() => route.params.postId, (newId, oldId) => {
  if (newId !== oldId) {
    fetchPost();
  }
});

onMounted(() => {
  fetchPost();
});
</script>

<style scoped>
.post-view {
  max-width: 800px;
  margin: auto;
  padding: 1.5rem;
}

.post-details {
  margin-bottom: 2rem;
}

.meta {
  font-size: 0.9rem;
  color: #666;
  margin-bottom: 1rem;
}

.author {
  font-weight: 500;
}

.community {
  font-style: italic;
}

.content {
  font-size: 1.1rem;
  color: #333;
  white-space: pre-line;
  margin-top: 1.5rem;
}

hr {
  margin: 2rem 0;
  border-top: 1px solid rgba(0, 0, 0, 0.1);
}
</style>