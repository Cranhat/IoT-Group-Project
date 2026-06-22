<script setup>
import { ref } from 'vue'

import LoginPage from './components/LoginPage.vue'
import DashboardPage from './components/Dashboard.vue'
import AdminPage from './components/AdminPage.vue'
import SnifferLogsPage from './components/SnifferLogs.vue'
import SnifferLogDetailPage from './components/SnifferLogDetail.vue'

const loggedIn = ref(false)
const currentUser = ref(null)
const currentPage = ref('dashboard')
const selectedLog = ref(null)
const snifferFilters = ref({
  limit: 10,
  sort: 'desc',
  port: '',
})

function handleLoginSuccess(user) {
  currentUser.value = user
  loggedIn.value = true
  currentPage.value = 'dashboard'
}

function openLog(log) {
  selectedLog.value = log
  currentPage.value = 'log-detail'
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
    v-else-if="currentPage === 'admin'"
    :user="currentUser"
    @go-dashboard="currentPage = 'dashboard'"
    @go-sniffer="currentPage = 'sniffer'"
  />

  <SnifferLogsPage
    v-else-if="currentPage === 'sniffer'"
    :user="currentUser"
    :filters="snifferFilters"
    @go-admin="currentPage = 'admin'"
    @view-log="openLog"
    @update-filters="snifferFilters = $event"
  />

  <SnifferLogDetailPage
  v-else-if="currentPage === 'log-detail'"
  :log="selectedLog"
  @go-back="currentPage = 'sniffer'"
  />
</template>
