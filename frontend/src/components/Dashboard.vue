<template>
  <div class="dashboard-page">
    <header class="topbar">
      <div>
        <h1>Dashboard</h1>

        <p>
          Logged in as
          <strong>{{ user?.name }}</strong>

          <span v-if="user?.privilege_type">
            — {{ user.privilege_type }}
          </span>
        </p>
      </div>

      <div class="topbar-actions">
        <button
          v-if="user?.privilege_type === 'administrator'"
          @click="emit('go-admin')"
        >
          Admin Panel
        </button>

        <button @click="refreshAll">
          Refresh
        </button>
      </div>
    </header>

    <section class="new-task-card">
      <h2>Send a new request</h2>

      <form @submit.prevent="submitProblem">
        <textarea
          v-model="problem"
          ref="problemInput"
          placeholder="Example: 'import math; print(math.pi)'"
          rows="1"
          @input="resizeProblemInput"
          required
        ></textarea>

        <select v-model="selectedDeviceId">
          <option value="">Any online device</option>
          <option
            v-for="device in onlineDevices"
            :key="device.device_id"
            :value="String(device.device_id)"
          >
            {{ getDeviceName(device) }}
          </option>
        </select>

        <button type="submit" :disabled="submitting">
          {{ submitting ? 'Sending...' : 'Send to Raspberry Pi' }}
        </button>
      </form>

      <p v-if="message" class="message">{{ message }}</p>
    </section>

    <main class="dashboard-grid">
      <section class="panel">
        <div class="panel-header">
          <h2>Previous Problems</h2>

          <div class="filter-controls">
            <label class="filter-control">
              Status
              <select v-model="requestStatusFilter">
                <option value="">All statuses</option>
                <option
                  v-for="status in requestStatuses"
                  :key="status"
                  :value="status"
                >
                  {{ status }}
                </option>
              </select>
            </label>

            <label class="filter-control">
              Device
              <select v-model="requestDeviceFilter">
                <option value="">All devices</option>
                <option
                  v-for="device in requestDevices"
                  :key="device.value"
                  :value="device.value"
                >
                  {{ device.label }}
                </option>
              </select>
            </label>
          </div>
        </div>

        <table v-if="filteredTasks.length">
          <thead>
            <tr>
              <th>ID</th>
              <th>Problem</th>
              <th>Status</th>
              <th>Device</th>
              <th>Result</th>
              <th>Time</th>
            </tr>
          </thead>

          <tbody>
            <tr v-for="task in filteredTasks" :key="task.task_id">
              <td>{{ task.task_id }}</td>
              <td>{{ task.problem || '—' }}</td>
              <td>
                <span :class="['status', task.status]">
                  {{ task.status || 'unknown' }}
                </span>
              </td>
              <td>{{ getTaskDeviceName(task) }}</td>
              <td>
                <span v-if="task.status === 'done'">
                  {{ task.result ?? '—' }}
                </span>
                <span v-else-if="task.status === 'failed'">
                  {{ task.error_message || 'Error' }}
                </span>
                <span v-else>
                  —
                </span>
              </td>
              <td>{{ formatDate(task.timestamp) }}</td>
            </tr>
          </tbody>
        </table>

        <p v-else class="empty">
          {{ tasks.length ? 'No requests match the selected filters.' : 'No tasks yet.' }}
        </p>
      </section>

      <section class="panel">
        <div class="panel-header">
          <h2>Devices</h2>

          <label class="filter-control">
            Status
            <select v-model="deviceStatusFilter">
              <option value="">All statuses</option>
              <option
                v-for="status in deviceStatuses"
                :key="status"
                :value="status"
              >
                {{ status }}
              </option>
            </select>
          </label>
        </div>

        <table v-if="filteredDevices.length">
          <thead>
            <tr>
              <th>ID</th>
              <th>Name</th>
              <th>Status</th>
            </tr>
          </thead>

          <tbody>
            <tr v-for="device in filteredDevices" :key="device.device_id">
              <td>{{ device.device_id }}</td>
              <td>{{ getDeviceName(device) }}</td>
              <td>
                <span :class="['status', device.status]">
                  {{ device.status }}
                </span>
              </td>
            </tr>
          </tbody>
        </table>

        <p v-else class="empty">
          {{ devices.length ? 'No devices match the selected filter.' : 'No devices connected.' }}
        </p>
      </section>
    </main>
  </div>
</template>

<script setup>
import { computed, nextTick, onMounted, ref } from 'vue'

const props = defineProps({
  user: {
    type: Object,
    required: true,
  },
})

const emit = defineEmits([
  'go-admin'
])

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

const problem = ref('')
const problemInput = ref(null)
const message = ref('')
const submitting = ref(false)
const selectedDeviceId = ref('')

const tasks = ref([])
const devices = ref([])
const requestStatusFilter = ref('')
const requestDeviceFilter = ref('')
const deviceStatusFilter = ref('')

const deviceById = computed(() => {
  return new Map(devices.value.map((device) => [String(device.device_id), device]))
})

const requestStatuses = computed(() => uniqueSorted(tasks.value.map((task) => task.status || 'unknown')))

const deviceStatuses = computed(() => uniqueSorted(devices.value.map((device) => device.status || 'unknown')))

const onlineDevices = computed(() => {
  return devices.value
    .filter((device) => normalizeValue(device.status) === 'online')
    .sort((first, second) => getDeviceName(first).localeCompare(getDeviceName(second), undefined, {
      numeric: true,
      sensitivity: 'base',
    }))
})

const requestDevices = computed(() => {
  const options = new Map()

  for (const task of tasks.value) {
    const value = task.device_id ? String(task.device_id) : 'waiting'
    options.set(value, getTaskDeviceName(task))
  }

  return [...options.entries()]
    .map(([value, label]) => ({ value, label }))
    .sort((first, second) => first.label.localeCompare(second.label, undefined, {
      numeric: true,
      sensitivity: 'base',
    }))
})

const filteredTasks = computed(() => {
  return tasks.value.filter((task) => {
    const statusMatches = !requestStatusFilter.value || normalizeValue(task.status) === requestStatusFilter.value
    const deviceValue = task.device_id ? String(task.device_id) : 'waiting'
    const deviceMatches = !requestDeviceFilter.value || deviceValue === requestDeviceFilter.value

    return statusMatches && deviceMatches
  })
})

const filteredDevices = computed(() => {
  return devices.value.filter((device) => {
    return !deviceStatusFilter.value || normalizeValue(device.status) === deviceStatusFilter.value
  })
})

function getTaskDeviceName(task) {
  if (!task.device_id) return 'Waiting'

  const device = deviceById.value.get(String(task.device_id))
  return getDeviceName(device) || `Device ${task.device_id}`
}

function getDeviceName(device) {
  if (!device) return ''
  return device.device_name || device.container_name || `Device ${device.device_id}`
}

function uniqueSorted(values) {
  return [...new Set(values.map(normalizeValue))].sort((first, second) => {
    return first.localeCompare(second, undefined, {
      numeric: true,
      sensitivity: 'base',
    })
  })
}

function normalizeValue(value) {
  return String(value || 'unknown').toLowerCase()
}

async function submitProblem() {
  submitting.value = true
  message.value = ''

  try {
    const res = await fetch(`${API_URL}/tasks`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        user_id: props.user.user_id,
        problem: problem.value,
        device_id: selectedDeviceId.value ? Number(selectedDeviceId.value) : null,
      }),
    })

    const text = await res.text()
    let data = {}

    try {
      data = JSON.parse(text)
    } catch {
      console.error('Server returned non-JSON:', text)
      message.value = 'Server returned invalid response'
      return
    }

    if (!res.ok) {
      message.value = data.detail || 'Could not send problem'
      return
    }

    message.value = 'Problem sent successfully'
    problem.value = ''
    await nextTick()
    resizeProblemInput()

    await refreshTasks()
  } catch (err) {
    console.error('Request failed:', err)
    message.value = 'Could not connect to server'
  } finally {
    submitting.value = false
  }
}

async function refreshTasks() {
  const res = await fetch(`${API_URL}/tasks?user_id=${props.user.user_id}`)
  const data = await res.json()
  tasks.value = data.tasks || []
}

async function refreshDevices() {
  const res = await fetch(`${API_URL}/devices`)
  const data = await res.json()
  devices.value = data.devices || []
}

async function refreshAll() {
  await Promise.all([
    refreshTasks(),
    refreshDevices(),
  ])
}

function formatDate(value) {
  if (!value) return '—'
  const date = new Date(value)
  const now = new Date()
  const isToday = date.toDateString() === now.toDateString()

  return isToday
    ? date.toLocaleTimeString()
    : date.toLocaleString()
}

function resizeProblemInput() {
  const input = problemInput.value
  if (!input) return

  input.style.height = 'auto'
  input.style.height = `${input.scrollHeight}px`
}

onMounted(() => {
  refreshAll()
  resizeProblemInput()

  setInterval(() => {
    refreshAll()
  }, 5000)
})
</script>

<style scoped>
.dashboard-page {
  min-height: 100vh;
  background: #bfe7cf;
  padding: 28px;
  font-family: Arial, sans-serif;
  color: #0b1f5e;
}

.dashboard-page h1,
.dashboard-page h2,
.dashboard-page p,
.dashboard-page strong,
.dashboard-page span,
.dashboard-page table,
.dashboard-page th,
.dashboard-page td {
  color: #020a26;
}

.topbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  justify-content: center;
  margin-bottom: 24px;
}

.topbar h1 {
  margin: 24px;
}

.topbar p {
  justify-content: center;
  align-items: center;
  margin: 6px 0 0;
}

.topbar-actions {
  display: flex;
  gap: 12px;
}

button {
  padding: 10px 14px;
  background: #1f2937;
  color: white;
  border: none;
  border-radius: 6px;
  cursor: pointer;
}

button:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.new-task-card {
  background: rgb(236, 248, 240);
  padding: 22px;
  border-radius: 12px;
  margin-bottom: 24px;
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.12);
}

.new-task-card textarea::placeholder {
  color: #010512;
}

.new-task-card form {
  display: flex;
  gap: 12px;
  align-items: flex-start;
}

.new-task-card textarea,
.new-task-card select {
  flex: 1;
  padding: 12px;
  border: 1px solid #ccc;
  border-radius: 6px;
  background: rgb(225, 239, 231);
  color: #010512;
}

.new-task-card textarea {
  min-height: 43px;
  max-height: 240px;
  line-height: 1.35;
  overflow-y: auto;
  resize: none;
}

.new-task-card select {
  flex: 0 0 190px;
}

.dashboard-grid {
  display: grid;
  grid-template-columns: 2fr 1fr;
  gap: 24px;
}

.panel {
  background: rgb(236, 248, 240);
  padding: 22px;
  border-radius: 12px;
  box-shadow: 0 6px 18px rgba(0, 0, 0, 0.08);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.12);
}

.panel-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 16px;
}

.panel-header h2 {
  margin: 0;
}

.filter-controls {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
}

.filter-control {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
  font-weight: 700;
  color: #020a26;
}

.filter-control select {
  min-width: 128px;
  padding: 8px 10px;
  border: 1px solid #9ca3af;
  border-radius: 6px;
  background: #f9fafb;
  color: #020a26;
}

table {
  width: 100%;
  border-collapse: collapse;
  margin-top: 12px;
}

th,
td {
  padding: 10px;
  border-bottom: 1px solid #e5e7eb;
  text-align: left;
  font-size: 14px;
}

th {
  background: #f9fafb;
}

.status {
  padding: 4px 8px;
  border-radius: 999px;
  font-size: 12px;
  background: #e5e7eb;
}

.status.completed,
.status.online,
.status.available {
  background: #dcfce7;
  color: #166534;
}

.status.pending,
.status.running,
.status.busy {
  background: #fef3c7;
  color: #92400e;
}

.status.failed,
.status.offline {
  background: #fee2e2;
  color: #991b1b;
}

.message {
  margin-top: 12px;
}

.empty {
  color: #000925;
}

@media (max-width: 900px) {
  .dashboard-grid {
    grid-template-columns: 1fr;
  }

  .new-task-card form {
    flex-direction: column;
  }

  .new-task-card select {
    flex: 1;
  }

  .topbar {
    flex-direction: column;
    align-items: flex-start;
    gap: 12px;
  }

  .panel-header {
    flex-direction: column;
    align-items: flex-start;
  }
}
</style>
