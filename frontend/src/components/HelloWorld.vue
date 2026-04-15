<script setup>
import { ref } from 'vue'

const count = ref(0)
</script>

<template>
  <div>
    <h1>Database Table Viewer</h1>
    
    <select v-model="tableName" @change="fetchTable">
      <option disabled value="">Select a table</option>
      <option v-for="t in tables" :key="t" :value="t">{{ t }}</option>
    </select>

    <div v-if="data.length">
      <h2>Table: {{ tableName }}</h2>
      <table border="1">
        <thead>
          <tr>
            <th v-for="key in Object.keys(data[0])" :key="key">{{ key }}</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="row in data" :key="row.id">
            <td v-for="key in Object.keys(row)" :key="key">{{ row[key] }}</td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script>
export default {
  data() {
    return {
      tables: ["users", "passwords", "devices", "task_logs", "task_result_logs", "http_logs"],
      tableName: "",
      data: [],
    };
  },
  methods: {
    async fetchTable() {
      if (!this.tableName) return;
      try {
        const res = await fetch(`http://localhost:8000/${this.tableName}`);
        const json = await res.json();
        this.data = json.data;
      } catch (err) {
        console.error("Error fetching table:", err);
      }
    },
  },
};
</script>
