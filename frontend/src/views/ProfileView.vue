<template>
  <div>
    <h2>User Profile</h2>
    <pre v-if="isAuthenticated">
      {{ user }}
    </pre>
  </div>
</template>

<script setup>
import { useAuth0 } from '@auth0/auth0-vue'

const { user, isAuthenticated } = useAuth0()

</script>