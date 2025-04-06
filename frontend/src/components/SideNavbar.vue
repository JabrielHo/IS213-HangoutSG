<script setup>
import 'bootstrap-icons/font/bootstrap-icons.css'
import LoginButton from '../components/LoginButton.vue'
import LogoutButton from '../components/LogoutButton.vue'
import SignupButton from '../components/SignupButton.vue'
import { useAuth0 } from '@auth0/auth0-vue'

const { isAuthenticated, user, isLoading } = useAuth0()

const hobbies = ['monsterhunter', 'cycling', 'running', 'pokemon', 'hiking', 'swimming', 'reading']
</script>

<template>
  <nav class="navbar navbar-dark bg-dark">
    <div class="justify-content-start">
      <button
        v-if="!isLoading"
        class="ms-2 navbar-toggler"
        type="button"
        data-bs-toggle="offcanvas"
        data-bs-target="#offcanvasDarkNavbar"
        aria-controls="offcanvasDarkNavbar"
        aria-label="Toggle navigation"
      >
        <span class="navbar-toggler-icon"></span>
      </button>
      <router-link to="/" class="ms-2 navbar-brand">HangoutSG</router-link>

      <div
        class="offcanvas offcanvas-start text-bg-dark"
        tabindex="-1"
        id="offcanvasDarkNavbar"
        aria-labelledby="offcanvasDarkNavbarLabel"
      >
        <div class="offcanvas-header">
          <button
            type="button"
            class="btn-close btn-close-white"
            data-bs-dismiss="offcanvas"
            aria-label="Close"
          ></button>
        </div>
        <hr class="m-0"/>
        <ul class="nav nav-pills flex-column mb-auto" style="padding: 16px;">
          <li class="nav-item">
            <router-link to="/" class="nav-link text-white" active-class="active">
              <i class="bi bi-house-door-fill"></i>&nbsp; Home</router-link
            >
          </li>
          <li class="nav-item">
            <router-link to="/events" class="nav-link text-white" active-class="active">
              <i class="bi bi-calendar-event-fill"></i>&nbsp; Events</router-link
            >
          </li>
          <li v-if="isAuthenticated" class="nav-item">
            <router-link to="/inbox" class="nav-link text-white" active-class="active">
              <i class="bi bi-envelope-fill"></i>&nbsp; Inbox
            </router-link>
          </li>
          <li v-if="isAuthenticated" class="nav-item">
            <router-link to="/communities/create" class="nav-link text-white" active-class="active">
              <i class="bi bi-plus-circle-fill"></i>&nbsp; Create Community
            </router-link>
          </li>
        </ul>
        <hr class="m-0"/>

        <div v-if="isAuthenticated" class="offcanvas-body">
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
    <div class="justify-content-end">
      <!-- Show loading state -->
      <div v-if="isLoading" class="spinner-border spinner-border-sm text-light me-2" role="status">
        <span class="visually-hidden">Loading...</span>
      </div>

      <!-- Show login/signup when not authenticated -->
      <div v-else-if="!isAuthenticated" class="d-flex gap-2 me-2">
        <LoginButton />
        <SignupButton />
      </div>

      <!-- Show user profile when authenticated -->
      <div v-else class="dropdown me-2">
        <a
          href="#"
          class="d-flex align-items-center text-white text-decoration-none"
          data-bs-toggle="dropdown"
          aria-expanded="false"
        >
          <img :src="user.picture" alt="" width="32" height="32" class="rounded-circle" />
        </a>
        <ul class="dropdown-menu dropdown-menu-dark dropdown-menu-end text-small shadow">
          <li><router-link class="dropdown-item" to="/profile">Profile</router-link></li>
          <li v-if="user['https://hangoutsg.com/roles'].includes('admin')">
            <router-link class="dropdown-item" to="/admin">Content Moderation</router-link>
          </li>
          <li><hr class="dropdown-divider" /></li>
          <li><LogoutButton /></li>
        </ul>
      </div>
    </div>
  </nav>
</template>

<style scoped></style>
