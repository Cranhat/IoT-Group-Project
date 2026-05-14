<script setup>
import { ref } from 'vue'

import LoginPage from './components/LoginPage.vue'
import Dashboard from './components/Dashboard.vue'

const loggedIn = ref(false)
const currentUser = ref(null)

function handleLoginSuccess(user) {
  currentUser.value = user
  loggedIn.value = true
}
</script>

<template>
  <LoginPage
    v-if="!loggedIn"
    @login-success="handleLoginSuccess"
  />

  <Dashboard
    v-else
    :user="currentUser"
  />
</template>