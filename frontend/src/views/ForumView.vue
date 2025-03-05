<script setup>
import { ref } from 'vue'
import { useRoute } from 'vue-router'

const route = useRoute()

const isJoined = ref(false)

const toggleJoinLeave = () => {
  isJoined.value = !isJoined.value
}

const createPost = () => {
}

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
  <div id="cardCarousel" class="carousel slide" data-bs-ride="carousel">
    <div class="carousel-inner">
      <div
        v-for="(cardGroup, groupIndex) in Array(Math.ceil(cards.length / 3))
          .fill()
          .map((_, i) => cards.slice(i * 4, (i + 1) * 4))"
        :key="groupIndex"
        class="carousel-item"
        :class="{ active: groupIndex === 0 }"
      >
        <div class="d-flex justify-content-around">
          <div
            v-for="(card, cardIndex) in cardGroup"
            :key="cardIndex"
            class="card"
            style="width: 18rem"
          >
            <img src="../assets/logo.svg" class="card-img-top" alt="Card image" />
            <div class="card-body">
              <h5 class="card-title">{{ card.title }}</h5>
              <p class="card-text">{{ card.description }}</p>
            </div>
          </div>
        </div>
      </div>
    </div>
    <button
      class="carousel-control-prev"
      type="button"
      data-bs-target="#cardCarousel"
      data-bs-slide="prev"
    >
      <span class="carousel-control-prev-icon" aria-hidden="true"></span>
      <span class="visually-hidden">Previous</span>
    </button>
    <button
      class="carousel-control-next"
      type="button"
      data-bs-target="#cardCarousel"
      data-bs-slide="next"
    >
      <span class="carousel-control-next-icon" aria-hidden="true"></span>
      <span class="visually-hidden">Next</span>
    </button>
  </div>
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
/* Add any additional styles here */
.btn {
  border-radius: 15px;
}

.carousel-control-prev-icon,
.carousel-control-next-icon {
  background-color: rgba(0, 0, 0, 0.5);
  border-radius: 50%;
}

/* Make carousel controls appear outside the cards */
.carousel-control-prev {
  left: -10%;
}

.carousel-control-next {
  right: -10%;
}
</style>