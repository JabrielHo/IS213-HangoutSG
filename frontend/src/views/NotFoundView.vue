<template>
  <div class="not-found-container">
    <h1 class="heading">404</h1>
    <p class="subheading">Page Not Found</p>
    <p>The page you are looking for doesn't exist or has been moved.</p>
    <router-link to="/" class="btn btn-primary mt-3"> Return to Home </router-link>
  </div>
</template>

<style scoped>
.not-found-container {
  text-align: center;
  padding: 3rem 1rem;
}

.heading {
  font-size: 6rem;
  font-weight: bold;
  margin-bottom: 0;
  color: #343a40;
}

.subheading {
  font-size: 1.8rem;
  margin-bottom: 1.5rem;
  color: #6c757d;
}
</style>