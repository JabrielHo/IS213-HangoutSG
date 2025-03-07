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
  <nav class="navbar navbar-dark bg-dark">
    <div class="container" style="justify-content: start">
      <a class="navbar-brand" href="/">HangoutSG</a>
      <button
        class="navbar-toggler"
        type="button"
        data-bs-toggle="offcanvas"
        data-bs-target="#offcanvasDarkNavbar"
        aria-controls="offcanvasDarkNavbar"
        aria-label="Toggle navigation"
      >
        <span class="navbar-toggler-icon"></span>
      </button>
      <div
        class="offcanvas offcanvas-start text-bg-dark"
        tabindex="-1"
        id="offcanvasDarkNavbar"
        aria-labelledby="offcanvasDarkNavbarLabel"
      >
        <div class="offcanvas-header">
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
          <button
            type="button"
            class="btn-close btn-close-white"
            data-bs-dismiss="offcanvas"
            aria-label="Close"
          ></button>
        </div>
        <hr class="m-0"/>
        <ul class="nav nav-pills flex-column mb-auto">
          <li class="nav-item">
            <router-link to="/" class="nav-link text-white" active-class="active">
              <i class="bi bi-calendar-event-fill"></i>&nbsp; Home</router-link
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
              <i class="bi bi-plus-circle-fill"></i>&nbsp; Create Community
            </router-link>
          </li>
        </ul>
        <hr />
        <div class="offcanvas-body">
          <ul class="nav nav-pills flex-column mb-auto">
            <li v-for="hobby in hobbies" :key="hobby">
              <router-link :to="`/c/${hobby}`" class="nav-link text-white" active-class="active">
                {{ hobby }}
              </router-link>
            </li>
          </ul>
        </div>
        <hr />
      </div>
    </div>
  </nav>
</template>

<style scoped>
</style>