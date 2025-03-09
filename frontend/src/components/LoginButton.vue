<template>
  <div>
    <button type="button" class="btn btn-outline-secondary text-white" @click="login">
      Log in
    </button>
  </div>
</template>
<script>
import { useAuth0 } from '@auth0/auth0-vue'

export default {
  setup() {
    const { loginWithRedirect } = useAuth0()

    return {
      login: () => {
        loginWithRedirect()
      },
    }
  },
}
</script>