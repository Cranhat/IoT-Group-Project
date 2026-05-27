<script setup>
import { ref } from 'vue'

import LoginPage from './components/LoginPage.vue'
import DashboardPage from './components/Dashboard.vue'
import AdminPage from './components/AdminPage.vue'

const loggedIn = ref(false)
const currentUser = ref(null)
const currentPage = ref('dashboard')

function handleLoginSuccess(user) {
  currentUser.value = user
  loggedIn.value = true
  currentPage.value = 'dashboard'
}
</script>

<template>
  <LoginPage
    v-if="!loggedIn"
    @login-success="handleLoginSuccess"
  />

  <DashboardPage
    v-else-if="currentPage === 'dashboard'"
    :user="currentUser"
    @go-admin="currentPage = 'admin'"
  />

  <AdminPage
    v-else
    :user="currentUser"
    @go-dashboard="currentPage = 'dashboard'"
  />
</template>