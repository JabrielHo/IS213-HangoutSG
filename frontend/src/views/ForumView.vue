<script setup>
import { ref } from 'vue'
import { useRoute } from 'vue-router'

const route = useRoute()

const isJoined = ref(false)
const toggleJoinLeave = () => {
  isJoined.value = !isJoined.value
}

const createPost = () => {}

const cards = ref([
  { title: 'Event 1', description: 'Event description 1' },
  { title: 'Event 2', description: 'Event description 2' },
  { title: 'Event 3', description: 'Event description 3' },
  { title: 'Event 4', description: 'Event description 4' },
  { title: 'Event 5', description: 'Event description 5' },
])
</script>

<template>
  <div class="d-flex justify-content-between align-items-center">
    <h1 class="heading">{{ route.params.community }}</h1>
    <div>
      <button @click="createPost" class="btn btn-dark me-2">
        <i class="bi bi-plus-lg"></i>&nbsp;Create Post
      </button>
      <button @click="toggleJoinLeave" class="btn btn-primary">
        {{ isJoined ? 'Leave' : 'Join' }}
      </button>
    </div>
  </div>
  <p>Community Description Here</p>
  <hr />

  <hr />
  <div class="list-group">
    <div class="list-group-item">
      <div class="row">
        <div class="col">
          <h5 class="mb-1">How to fight this monster?</h5>
          <small>u/YuanXing - 13 hr. ago</small>
          <div class="row">
            <div class="col mt-1">
              <a href="#" class="btn btn-sm btn-outline-primary me-2">
                <i class="bi bi-chat-square"></i>&nbsp;10 Comments
              </a>
              <a href="#" class="btn btn-sm btn-outline-secondary me-2">
                <i class="bi bi-share"></i>&nbsp;Share
              </a>
              <a href="#" class="btn btn-sm btn-outline-danger">
                <i class="bi bi-flag"></i>&nbsp;Report
              </a>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style>
.btn {
  border-radius: 15px;
}
</style>