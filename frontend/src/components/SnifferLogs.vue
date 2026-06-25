<script setup>
import { ref, onMounted, watch } from 'vue'

const props = defineProps({
  user: {
    type: Object,
    required: true,
  },
  filters: {
    type: Object,
    required: true,
  },
})

const emit = defineEmits(['go-admin', 'view-log', 'update-filters'])

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

const logs = ref([])
const limit = ref(props.filters.limit ?? 10)
const sort = ref(props.filters.sort ?? 'desc')
const portFilter = ref(props.filters.port ?? '')
const message = ref('')

watch([limit, sort, portFilter], () => {
  emit('update-filters', {
    limit: limit.value,
    sort: sort.value,
    port: portFilter.value,
  })
})

async function fetchLogs() {
  message.value = ''

  try {
    const params = new URLSearchParams({
      limit: limit.value,
      sort: sort.value,
    })

    const normalizedPort = String(portFilter.value).trim()

    if (normalizedPort) {
      params.set('port', normalizedPort)
    }

    const res = await fetch(`${API_URL}/sniffer/logs?${params.toString()}`)

    const data = await res.json()

    if (!res.ok) {
      message.value = data.detail || 'Could not fetch logs'
      return
    }

    logs.value = data.logs || []
  } catch (err) {
    console.error(err)
    message.value = 'Server error'
  }
}

function formatDate(value) {
  if (!value) return '—'
  return new Date(value).toLocaleString()
}

onMounted(fetchLogs)
</script>

<template>
  <div class="logs-page">
    <header class="topbar">
      <div>
        <h1>Packet Sniffer Logs</h1>
        <p>Logged in as <strong>{{ user?.name }}</strong></p>
      </div>

      <button @click="$emit('go-admin')">
        Back to Admin Panel
      </button>
    </header>

    <section class="controls-card">
      <label>
        Show
        <select v-model="limit" @change="fetchLogs">
          <option :value="5">5 packets</option>
          <option :value="10">10 packets</option>
          <option :value="25">25 packets</option>
          <option :value="50">50 packets</option>
          <option :value="100">100 packets</option>
        </select>
      </label>

      <label>
        Sort
        <select v-model="sort" @change="fetchLogs">
          <option value="desc">Newest first</option>
          <option value="asc">Oldest first</option>
        </select>
      </label>

      <label>
        Port
        <input
          v-model="portFilter"
          type="number"
          min="1"
          max="65535"
          placeholder="Any"
          @keyup.enter="fetchLogs"
        />
      </label>

      <button @click="fetchLogs">
        Apply
      </button>

      <button
        v-if="portFilter"
        class="secondary-button"
        @click="portFilter = ''; fetchLogs()"
      >
        Clear
      </button>
    </section>

    <p v-if="message" class="message">
      {{ message }}
    </p>

    <section class="logs-card">
      <table v-if="logs.length">
        <thead>
          <tr>
            <th>Sniffer</th>
            <th>Port</th>
            <th>Log</th>
            <th>Time</th>
          </tr>
        </thead>

        <tbody>
          <tr v-for="log in logs" :key="`${log.timestamp}-${log.port}`">
            <td>{{ log.sniffer_name }}</td>
            <td>{{ log.port }}</td>
            <td>
              <button
                @click="emit('view-log', log)"
              >
                View Log
              </button>
            </td>
            <td>{{ formatDate(log.timestamp) }}</td>
          </tr>
        </tbody>
      </table>

      <p v-else>No packet logs found.</p>
    </section>
  </div>
</template>

<style scoped>
.logs-page {
  min-height: 100vh;
  background: #bfe7cf;
  padding: 28px;
  font-family: Arial, sans-serif;
  color: #010512;
}

.topbar,
.controls-card,
.logs-card {
  background: rgb(236, 248, 240);
  border-radius: 12px;
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.12);
}

.topbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 22px;
  margin-bottom: 20px;
}

.topbar h1 {
  margin: 20px;
  color: #020a26;
}

.controls-card {
  display: flex;
  flex-wrap: wrap;
  gap: 16px;
  align-items: center;
  padding: 18px;
  margin-bottom: 20px;
}

.controls-card label {
  display: flex;
  align-items: center;
  gap: 8px;
}

.logs-card {
  padding: 18px;
}

button {
  padding: 10px 14px;
  background: #1f2937;
  color: white;
  border: none;
  border-radius: 6px;
  cursor: pointer;
}

.secondary-button {
  background: #4b5563;
}

select,
input {
  padding: 8px;
  border-radius: 6px;
  border: 1px solid #9ca3af;
  background: rgb(225, 239, 231);
  color: #010512;
}

input {
  width: 96px;
}

table {
  width: 100%;
  border-collapse: collapse;
}

th,
td {
  padding: 10px;
  border-bottom: 1px solid #d1d5db;
  text-align: left;
  color: #020a26;
}

th {
  background: #f3f4f6;
}

.message {
  font-weight: bold;
}
</style>
