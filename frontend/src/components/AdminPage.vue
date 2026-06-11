<script setup>
import { ref, onMounted, computed } from 'vue'

defineProps({
  user: {
    type: Object,
    required: true,
  },
})

defineEmits(['go-dashboard', 'go-sniffer'])

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

const users = ref([])
const devices = ref([])
const requests = ref([])

const showUsers = ref(false)
const showDevices = ref(true)
const showRequests = ref(false)

const showUserModal = ref(false)
const showDeviceModal = ref(false)
const showProvisionModal = ref(false)
const provisioning = ref(false)

const message = ref('')
const provisionName = ref('')

const newUser = ref({
  name: '',
  password: '',
  privilege_type: 'user',
})

const newDevice = ref({
  ip_address: '',
  status: 'online',
})


const requestsPerDay = computed(() => {
  const days = []

  for (let i = 6; i >= 0; i--) {
    const date = new Date()
    date.setDate(date.getDate() - i)

    const key = date.toISOString().slice(0, 10)

    days.push({
      key,
      label: date.toLocaleDateString(undefined, {
        weekday: 'short',
      }),
      count: 0,
    })
  }

  for (const request of requests.value) {
    if (!request.timestamp) continue

    const key = new Date(request.timestamp).toISOString().slice(0, 10)
    const day = days.find((d) => d.key === key)

    if (day) {
      day.count++
    }
  }

  return days
})

const maxRequests = computed(() => {
  return Math.max(
    1,
    ...requestsPerDay.value.map((day) => day.count)
  )
})


async function refreshAll() {
  await Promise.all([
    fetchUsers(),
    fetchDevices(),
    fetchRequests(),
  ])
}

async function fetchUsers() {
  const res = await fetch(`${API_URL}/tables/users`)
  const data = await res.json()
  users.value = data.data || []
}

async function fetchDevices() {
  const res = await fetch(`${API_URL}/devices`)
  const data = await res.json()
  devices.value = data.devices || []
}

async function fetchRequests() {
  const res = await fetch(`${API_URL}/tables/task_logs`)
  const data = await res.json()
  requests.value = data.data || []
}

async function addUser() {
  message.value = ''

  try {
    const res = await fetch(`${API_URL}/add/users`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(newUser.value),
    })

    const data = await res.json()

    if (!res.ok) {
      message.value = data.detail || 'Could not add user'
      return
    }

    newUser.value = {
      name: '',
      password: '',
      privilege_type: 'user',
    }

    showUserModal.value = false
    message.value = 'User added successfully'
    await fetchUsers()
  } catch (err) {
    console.error(err)
    message.value = 'Server error'
  }
}

async function provisionDockerDevice() {
  message.value = ''
  provisioning.value = true

  try {
    const res = await fetch(`${API_URL}/devices/provision`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        device_name: provisionName.value || null,
      }),
    })

    const data = await res.json()

    if (!res.ok) {
      message.value = data.detail || 'Could not provision device'
      return
    }

    provisionName.value = ''
    showProvisionModal.value = false
    message.value = `Docker device provisioned: ${data.device_name || data.device_id}`
    await fetchDevices()
  } catch (err) {
    console.error(err)
    message.value = 'Agent or server error'
  } finally {
    provisioning.value = false
  }
}

async function addDevice() {
  message.value = ''

  try {
    const res = await fetch(`${API_URL}/add/devices`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(newDevice.value),
    })

    const data = await res.json()

    if (!res.ok) {
      message.value = data.detail || 'Could not add device'
      return
    }

    newDevice.value = {
      ip_address: '',
      status: 'online',
    }

    showDeviceModal.value = false
    message.value = 'Device added successfully'
    await fetchDevices()
  } catch (err) {
    console.error(err)
    message.value = 'Server error'
  }
}

async function updateDevice(device) {
  message.value = ''

  try {
    const res = await fetch(`${API_URL}/update/devices/${device.device_id}`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        ip_address: device.ip_address,
        status: device.status,
        container_name: device.container_name || null,
        device_name: device.device_name || null,
      }),
    })

    const data = await res.json()

    if (!res.ok) {
      message.value = data.detail || 'Could not update device'
      return
    }

    message.value = 'Device updated successfully'
    await fetchDevices()
  } catch (err) {
    console.error(err)
    message.value = 'Server error'
  }
}

async function deleteDevice(deviceId) {
  if (!confirm('Delete this device?')) return

  const res = await fetch(`${API_URL}/delete/devices/${deviceId}`, {
    method: 'DELETE',
  })

  const data = await res.json()

  if (!res.ok) {
    message.value = data.detail || 'Could not delete device'
    return
  }

  message.value = 'Device deleted successfully'
  await fetchDevices()
}

async function deleteUser(userId) {
  if (!confirm('Delete this user?')) return

  const res = await fetch(`${API_URL}/delete/users/${userId}`, {
    method: 'DELETE',
  })

  const data = await res.json()

  if (!res.ok) {
    message.value = data.detail || 'Could not delete user'
    return
  }

  message.value = 'User deleted successfully'
  await fetchUsers()
}

function formatDate(value) {
  if (!value) return '—'
  return new Date(value).toLocaleString()
}

onMounted(refreshAll)
</script>

<template>
  <div class="admin-page">
    <header class="topbar">
      <div>
        <h1>Admin Panel</h1>
        <p>Logged in as <strong>{{ user?.name }}</strong></p>
      </div>

      <button @click="$emit('go-dashboard')">
        Back to Dashboard
      </button>
    </header>

    <section class="actions-card">
      <button @click="showUserModal = true">
        Add User
      </button>

      <button @click="showDeviceModal = true">
        Add Device
      </button>

      <button @click="showProvisionModal = true">
        Provision Docker Device
      </button>

      <button @click="refreshAll">
        Refresh All
      </button>

      <button @click="$emit('go-sniffer')">
        Packet Sniffer Logs
      </button>
    </section>

    <p v-if="message" class="message">
      {{ message }}
    </p>

    <section class="fold-card">
      <button class="fold-header" @click="showDevices = !showDevices">
        <span>Devices</span>
        <span>{{ showDevices ? '▲' : '▼' }}</span>
      </button>

      <div v-if="showDevices" class="fold-content">
        <table v-if="devices.length">
          <thead>
            <tr>
              <th>ID</th>
              <th>Name</th>
              <th>Container</th>
              <th>IP / Device ID</th>
              <th>Status</th>
              <th>Save</th>
              <th>Delete</th>
            </tr>
          </thead>

          <tbody>
            <tr v-for="device in devices" :key="device.device_id">
              <td>{{ device.device_id }}</td>

              <td>{{ device.device_name || '—' }}</td>

              <td>{{ device.container_name || '—' }}</td>

              <td>
                <input v-model="device.ip_address" />
              </td>

              <td>
                <select v-model="device.status">
                  <option value="online">online</option>
                  <option value="busy">busy</option>
                  <option value="offline">offline</option>
                </select>
              </td>

            <td>
                <button @click="updateDevice(device)">
                    Save
                </button>
                </td>

                <td>
                <button
                    class="delete-btn"
                    @click="deleteDevice(device.device_id)"
                >
                    Delete
                </button>
                </td>
            </tr>
          </tbody>
        </table>

        <p v-else>No devices found.</p>
      </div>
    </section>

    <section class="fold-card">
    <button class="fold-header" @click="showUsers = !showUsers">
        <span>Users</span>
        <span>{{ showUsers ? '▲' : '▼' }}</span>
    </button>

    <div v-if="showUsers" class="fold-content">
        <table v-if="users.length">
        <thead>
            <tr>
            <th>ID</th>
            <th>Name</th>
            <th>Privilege</th>
            <th>Delete</th>
            </tr>
        </thead>

        <tbody>
            <tr v-for="u in users" :key="u.user_id">
            <td>{{ u.user_id }}</td>

            <td>{{ u.name }}</td>

            <td>{{ u.privilege_type }}</td>

            <td>
                <button
                class="delete-btn"
                @click="deleteUser(u.user_id)"
                >
                Delete
                </button>
            </td>
            </tr>
        </tbody>
        </table>

        <p v-else>No users found.</p>
    </div>
    </section>


    <section class="fold-card">
      <button class="fold-header" @click="showRequests = !showRequests">
        <span>Requests</span>
        <span>{{ showRequests ? '▲' : '▼' }}</span>
      </button>

      <div v-if="showRequests" class="fold-content">
        <table v-if="requests.length">
          <thead>
            <tr>
              <th>Task ID</th>
              <th>User ID</th>
              <th>Device ID</th>
              <th>Request</th>
              <th>Status</th>
              <th>Time</th>
            </tr>
          </thead>

          <tbody>
            <tr v-for="task in requests" :key="task.task_id">
              <td>{{ task.task_id }}</td>
              <td>{{ task.user_id }}</td>
              <td>{{ task.device_id || '—' }}</td>
              <td>{{ task.problem || '—' }}</td>
              <td>{{ task.status || 'unknown' }}</td>
              <td>{{ formatDate(task.timestamp) }}</td>
            </tr>
          </tbody>
        </table>

        <p v-else>No requests found.</p>
      </div>
    </section>

    <div v-if="showUserModal" class="modal-backdrop">
      <div class="modal">
        <h2>Add User</h2>

        <form @submit.prevent="addUser">
          <input
            v-model="newUser.name"
            placeholder="Username"
            required
          />

          <input
            v-model="newUser.password"
            type="password"
            placeholder="Password"
            required
          />

          <select v-model="newUser.privilege_type">
            <option value="user">user</option>
            <option value="administrator">administrator</option>
          </select>

          <div class="modal-actions">
            <button type="button" @click="showUserModal = false">
              Cancel
            </button>

            <button type="submit">
              Create User
            </button>
          </div>
        </form>
      </div>
    </div>

    <div v-if="showProvisionModal" class="modal-backdrop">
      <div class="modal">
        <h2>Provision Docker Device</h2>
        <p class="modal-hint">
          Creates a new peripheral container, copies TLS certificates with docker cp,
          and registers the device in the system.
        </p>

        <form @submit.prevent="provisionDockerDevice">
          <input
            v-model="provisionName"
            placeholder="Device name (optional), e.g. sensor-01"
          />

          <div class="modal-actions">
            <button type="button" @click="showProvisionModal = false">
              Cancel
            </button>

            <button type="submit" :disabled="provisioning">
              {{ provisioning ? 'Provisioning...' : 'Create Device' }}
            </button>
          </div>
        </form>
      </div>
    </div>

    <div v-if="showDeviceModal" class="modal-backdrop">
      <div class="modal">
        <h2>Add Device</h2>

        <form @submit.prevent="addDevice">
          <input
            v-model="newDevice.ip_address"
            placeholder="IP address"
            required
          />

          <select v-model="newDevice.status">
            <option value="online">online</option>
            <option value="busy">busy</option>
            <option value="offline">offline</option>
          </select>

          <div class="modal-actions">
            <button type="button" @click="showDeviceModal = false">
              Cancel
            </button>

            <button type="submit">
              Create Device
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>

<section class="fold-card chart-card">
  <h2>Number of requests in the last week</h2>

  <div class="bar-chart">
    <div
      v-for="day in requestsPerDay"
      :key="day.key"
      class="bar-item"
    >
      <div class="bar-wrapper">
        <div
          class="bar"
          :style="{
            height: `${(day.count / maxRequests) * 160}px`
          }"
        >
          <span>{{ day.count }}</span>
        </div>
      </div>

      <p>{{ day.label }}</p>
    </div>
  </div>
</section>

</template>

<style scoped>
.admin-page {
  min-height: 100vh;
  background: #bfe7cf;
  padding: 28px;
  font-family: Arial, sans-serif;
  color: #010512;
}

.topbar,
.actions-card,
.fold-card {
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

.topbar p {
  margin: 6px 0 0;
}

.actions-card {
  display: flex;
  gap: 12px;
  padding: 18px;
  margin-bottom: 20px;
}

.fold-card {
  margin-bottom: 18px;
  overflow: hidden;
}

.fold-header {
  width: 100%;
  display: flex;
  justify-content: space-between;
  background: rgb(236, 248, 240);
  color: #020a26;
  font-weight: bold;
  font-size: 18px;
  text-align: left;
}

.fold-content {
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

button:not(.fold-header):hover {
  background: #111827;
}

.fold-header:hover {
  background: rgb(236, 248, 240);
  color: #020a26;
}

.delete-btn {
  background: #991b1b;
}

.delete-btn:hover {
  background: #7f1d1d;
}

input,
select {
  padding: 10px;
  border: 1px solid #ccc;
  border-radius: 6px;
  background: rgb(225, 239, 231);
  color: #010512;
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
  margin-bottom: 16px;
  font-weight: bold;
}

.modal-backdrop {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.45);
  display: flex;
  align-items: center;
  justify-content: center;
}

.modal {
  width: 360px;
  background: rgb(236, 248, 240);
  padding: 24px;
  border-radius: 14px;
  box-shadow: 0 14px 40px rgba(0, 0, 0, 0.3);
}

.modal h2 {
  margin-top: 0;
  color: #020a26;
}

.modal-hint {
  margin-top: 0;
  color: #374151;
  font-size: 14px;
  line-height: 1.4;
}

.modal form {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.modal-actions {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
}

.chart-card {
  padding: 22px;
  margin-top: 20px;
}

.chart-card h2 {
  margin-top: 0;
  color: #020a26;
}

.bar-chart {
  height: 220px;
  display: flex;
  align-items: end;
  gap: 18px;
  padding-top: 20px;
}

.bar-item {
  flex: 1;
  text-align: center;
}

.bar-wrapper {
  height: 170px;
  display: flex;
  align-items: end;
  justify-content: center;
}

.bar {
  width: 100%;
  max-width: 48px;
  min-height: 8px;
  background: #1f2937;
  border-radius: 8px 8px 0 0;
  display: flex;
  align-items: start;
  justify-content: center;
  padding-top: 6px;
}

.bar span {
  color: white;
  font-size: 12px;
}

.bar-item p {
  margin-top: 8px;
  color: #020a26;
  font-weight: bold;
}

@media (max-width: 900px) {
  .topbar,
  .actions-card {
    flex-direction: column;
    align-items: flex-start;
  }

  .modal {
    width: 90%;
  }
}
</style>