<template>
  <div class="list-group-item post-card">
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
</template>

<style scoped>
.post-card {
  cursor: pointer;
  border-radius: 8px;
  margin-bottom: 0.5rem;
  transition: transform 0.3s ease, box-shadow 0.3s ease;
  border: 1px solid rgba(0, 0, 0, 0.125);
}

.post-card:hover {
  box-shadow: 0 8px 15px rgba(0, 0, 0, 0.1);
}
</style>