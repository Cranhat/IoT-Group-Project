<template>
  <div class="login-page">
    <div class="login-card">
      <h1>Welcome!</h1>
        <h2>Please login</h2>

        <form @submit.prevent="login">
          <input v-model="username" type="text" placeholder="Username" required />
          <input v-model="passcode" type="password" placeholder="Passcode" required />
          <button type="submit">Login</button>
        </form>

      <p v-if="message" class="message">{{ message }}</p>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'

const emit = defineEmits(['login-success'])

const username = ref('')
const passcode = ref('')
const message = ref('')

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

async function login() {
  try {
    const res = await fetch(`${API_URL}/login`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        username: username.value,
        passcode: passcode.value,
      }),
    })

    const data = await res.json()

    if (!res.ok) {
      message.value = data.detail || 'Login failed'
      return
    }

    message.value = 'Login successful'

    emit('login-success', {
      user_id: data.user_id,
      name: data.name,
      privilege_type: data.privilege_type
    })
  } catch (err) {
    console.error(err)
    message.value = 'Server error'
  }
}
</script>

<style scoped>
.login-page {
  min-height: 100vh;
  display: flex;
  justify-content: center;
  align-items: center;
  background: #b2e6c7;
}

.login-card {
  width: 360px;
  padding: 28px;
  background: rgb(236, 248, 240);
  border-radius: 12px;
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.12);
}

h1 {
  color: rgb(12, 3, 66);
  text-align: center;
  margin-bottom: 24px;
}

h2 {
  color: rgb(12, 3, 66);
  text-align: center;
  margin-bottom: 16px;
}

input {
  box-sizing: border-box;
  width: 100%;
  padding: 12px;
  margin-bottom: 14px;
  border: 1px solid #cccccc;
  border-radius: 6px;
  background: white;
  color: #010512;
}

button {
  width: 100%;
  padding: 12px;
  background: #1f2937;
  color: white;
  border: none;
  border-radius: 6px;
  cursor: pointer;
}

button:hover {
  background: #111827;
}

.message {
  margin-top: 16px;
  text-align: center;
}
</style>