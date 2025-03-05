<script setup>
import { RouterView } from 'vue-router'
import SideNavbar from './components/SideNavbar.vue'
</script>

<template>
  <div class="d-flex">
    <SideNavbar />
    <div class="container mt-3">
      <RouterView />
    </div>
  </div>
</template>

<style scoped>
</style>
