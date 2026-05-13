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

      <button @click="refreshAll">Refresh</button>
    </header>

    <section class="new-task-card">
      <h2>Send a new request</h2>

      <form @submit.prevent="submitProblem">
        <input
          v-model="problem"
          type="text"
          placeholder="Example: 'import math; print(math.pi)'"
          required
        />

        <button type="submit" :disabled="submitting">
          {{ submitting ? 'Sending...' : 'Send to Raspberry Pi' }}
        </button>
      </form>

      <p v-if="message" class="message">{{ message }}</p>
    </section>

    <main class="dashboard-grid">
      <section class="panel">
        <h2>Previous Problems</h2>

        <table v-if="tasks.length">
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
            <tr v-for="task in tasks" :key="task.task_id">
              <td>{{ task.task_id }}</td>
              <td>{{ task.problem || '—' }}</td>
              <td>
                <span :class="['status', task.status]">
                  {{ task.status || 'unknown' }}
                </span>
              </td>
              <td>{{ task.device_id || 'Waiting' }}</td>
              <td>
                <span v-if="task.status === 'completed'">
                  {{ task.result }}
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

        <p v-else class="empty">No tasks yet.</p>
      </section>

      <section class="panel">
        <h2>Connected Devices</h2>

        <table v-if="devices.length">
          <thead>
            <tr>
              <th>ID</th>
              <th>IP Address</th>
              <th>Status</th>
            </tr>
          </thead>

          <tbody>
            <tr v-for="device in devices" :key="device.device_id">
              <td>{{ device.device_id }}</td>
              <td>{{ device.ip_address || 'Unknown' }}</td>
              <td>
                <span :class="['status', device.status]">
                  {{ device.status }}
                </span>
              </td>
            </tr>
          </tbody>
        </table>

        <p v-else class="empty">No devices connected.</p>
      </section>
    </main>
  </div>
</template>

<script setup>
import { onMounted, ref } from 'vue'

const props = defineProps({
  user: {
    type: Object,
    required: true,
  },
})

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

const problem = ref('')
const message = ref('')
const submitting = ref(false)

const tasks = ref([])
const devices = ref([])

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
  return new Date(value).toLocaleString()
}

onMounted(() => {
  refreshAll()

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

.new-task-card input::placeholder {
  color: #010512;
}

.new-task-card form {
  display: flex;
  gap: 12px;
}

.new-task-card input {
  flex: 1;
  padding: 12px;
  border: 1px solid #ccc;
  border-radius: 6px;
  background: rgb(225, 239, 231);
  color: #010512;
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

  .topbar {
    flex-direction: column;
    align-items: flex-start;
    gap: 12px;
  }
}
</style>