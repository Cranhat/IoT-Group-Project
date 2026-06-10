<script setup>
defineProps({
  log: {
    type: Object,
    required: true,
  },
})

defineEmits(['go-back'])

function formatDate(value) {
  if (!value) return '—'
  return new Date(value).toLocaleString()
}
</script>

<template>
  <div class="page">
    <header class="topbar">
      <h1>Packet Log</h1>

      <button @click="$emit('go-back')">
        Back
      </button>
    </header>

    <section class="card">
      <p>
        <strong>Sniffer:</strong>
        {{ log.sniffer_name }}
      </p>

      <p>
        <strong>Port:</strong>
        {{ log.port }}
      </p>

      <p>
        <strong>Timestamp:</strong>
        {{ formatDate(log.timestamp) }}
      </p>
    </section>

    <section class="log-card">
      <pre>{{ log.log }}</pre>
    </section>
  </div>
</template>

<style scoped>
.page {
  min-height: 100vh;
  background: #bfe7cf;
  padding: 28px;
}

.topbar {
  display: flex;
  justify-content: space-between;
  margin-bottom: 20px;
}

.topbar h1 {
  margin: 20px;
  color: #020a26;
}

.card,
.log-card {
  background: rgb(236, 248, 240);
  padding: 20px;
  border-radius: 12px;
  box-shadow: 0 8px 24px rgba(0,0,0,0.12);
  margin-bottom: 20px;
}

pre {
  text-align: left;
  white-space: pre-wrap;
  word-break: break-word;
  font-family: Consolas, monospace;
  color: #020a26;
  margin: 0;
}

button {
  padding: 10px 14px;
  background: #1f2937;
  color: white;
  border: none;
  border-radius: 6px;
  cursor: pointer;
}
</style>