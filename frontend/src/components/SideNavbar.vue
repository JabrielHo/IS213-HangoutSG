<script setup>
import 'bootstrap-icons/font/bootstrap-icons.css'

const hobbies = [
  'MonsterHunter',
  'Cycling',
  'Running',
  'Pokemon',
  'Hiking',
  'Swimming',
  'Reading',
  'Gaming1',
  'Gaming2',
  'Gaming3',
  'Gaming4',
  'Gaming5',
  'Gaming6',
  'Gaming7',
  'Gaming8',
  'Gaming9',
  'Gaming10',
]
</script>

<template>
  <div class="d-flex flex-column flex-shrink-0 p-3 text-bg-dark vh-100" style="width: 280px">
    <a
      href="/"
      class="d-flex align-items-center mb-3 mb-md-0 me-md-auto text-white text-decoration-none"
    >
      <span class="fs-4">HangoutSG</span>
    </a>
    <hr />
    <ul class="nav nav-pills flex-column mb-auto">
      <li class="nav-item">
        <router-link to="/" class="nav-link text-white" active-class="active">
          <i class="bi bi-house-door-fill"></i>&nbsp; Home</router-link
        >
      </li>
      <li class="nav-item">
        <router-link to="/events" class="nav-link text-white" active-class="active">
          <i class="bi bi-house-door-fill"></i>&nbsp; Events</router-link
        >
      </li>
      <li class="nav-item">
        <router-link to="/inbox" class="nav-link text-white" active-class="active">
          <i class="bi bi-envelope-fill"></i>&nbsp; Inbox
        </router-link>
      </li>
      <li class="nav-item">
        <router-link to="/communities/create" class="nav-link text-white" active-class="active">
          <i class="bi bi-plus-circle"></i>&nbsp; Create Community
        </router-link>
      </li>
    </ul>
    <hr />
    <div class="hobbies-wrapper flex-grow-1 overflow-auto">
      <ul class="nav nav-pills flex-column mb-auto">
        <li v-for="hobby in hobbies" :key="hobby">
          <router-link
            :to="`/c/${hobby}`"
            class="nav-link text-white"
            active-class="active"
          >
            {{ hobby }}
          </router-link>
        </li>
      </ul>
    </div>

    <hr />
    <div class="dropdown">
      <a
        href="#"
        class="d-flex align-items-center text-white text-decoration-none dropdown-toggle"
        data-bs-toggle="dropdown"
        aria-expanded="false"
      >
        <img
          src="https://static.vecteezy.com/system/resources/previews/020/765/399/non_2x/default-profile-account-unknown-icon-black-silhouette-free-vector.jpg"
          alt=""
          width="32"
          height="32"
          class="rounded-circle me-2"
        />
        <strong>YuanXing</strong>
      </a>
      <ul class="dropdown-menu dropdown-menu-dark text-small shadow">
        <li><a class="dropdown-item" href="#">Reported Posts</a></li>
        <li><hr class="dropdown-divider" /></li>
        <li><a class="dropdown-item" href="#">Sign out</a></li>
      </ul>
    </div>
  </div>
</template>

<style scoped>
.hobbies-wrapper {
  max-height: calc(100vh - 100px);
  overflow-y: auto;
}

/* Custom scrollbar styles */
.hobbies-wrapper::-webkit-scrollbar {
  width: 8px;
}

.hobbies-wrapper::-webkit-scrollbar-track {
  background: #343a40;
}

.hobbies-wrapper::-webkit-scrollbar-thumb {
  background-color: #6c757d;
  border-radius: 4px;
  border: 2px solid #343a40;
}

.hobbies-wrapper::-webkit-scrollbar-thumb:hover {
  background-color: #adb5bd;
}
</style>
