<script setup>
import { RouterView } from 'vue-router'
import SideNavbar from './components/SideNavbar.vue'
</script>

<template>
  <SideNavbar />
  <div class="container mt-3">
    <RouterView />
  </div>
</template>

<style scoped>
</style>
