<script setup>
import { ref, onMounted } from 'vue'

const message = ref('Loading...')
const backendStatus = ref('')

onMounted(async () => {
  try {
    const res = await fetch('/api/status')
    const data = await res.json()
    backendStatus.value = `Backend Status: ${data.status} (Cameras: ${data.cameras})`
    message.value = 'Welcome to CCTV MFU (Vue + FastAPI)'
  } catch (err) {
    console.error(err)
    backendStatus.value = 'Error connecting to backend.'
    message.value = 'Welcome to CCTV MFU'
  }
})
</script>

<template>
  <header>
    <div class="wrapper">
      <h1>{{ message }}</h1>
      <p class="status">{{ backendStatus }}</p>
    </div>
  </header>

  <main>
    <!-- Camera grid will go here -->
    <div class="camera-grid">
      <div class="camera-placeholder">Camera 1</div>
      <div class="camera-placeholder">Camera 2</div>
      <div class="camera-placeholder">Camera 3</div>
    </div>
  </main>
</template>

<style scoped>
header {
  line-height: 1.5;
  text-align: center;
  margin-bottom: 2rem;
}

h1 {
  font-weight: 500;
  font-size: 2.6rem;
  top: -10px;
}

.status {
  font-size: 1.2rem;
  color: #42b883;
}

.camera-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 1rem;
}

.camera-placeholder {
  background: #333;
  color: #fff;
  height: 200px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 8px;
}
</style>
