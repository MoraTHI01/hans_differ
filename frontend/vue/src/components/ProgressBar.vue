<template>
  <div class="progress-container">
    <template v-for="idx in total">
      <div v-if="idx !== 1" class="line" :class="{current: idx <= current}"></div>
      <div class="circle" :class="{current: idx <= current}">
        <span>{{ idx }}</span>
      </div>
      <div v-if="idx !== total" class="line" :class="{current: idx < current}"></div>
    </template>
  </div>
</template>

<script setup lang="ts">
defineProps<{
  current: number;
  total: number;
}>();
</script>

<style scoped>
.progress-container {
  display: flex;
  align-items: center;
  width: 50%;
  margin: 1rem;
}

@media (max-width: 768px) {
  .progress-container {
    width: 90%;
  }
}

.line {
  height: 5px;
  flex: 1;
  background-color: var(--hans-light-gray);
}

.circle {
  width: 3rem;
  height: 3rem;
  background-color: var(--hans-light-gray);
  border-radius: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
}

.circle > span {
  font-size: 1.25rem;
}

.current {
  background-color: var(--hans-dark-blue);
  color: var(--hans-light);
}
</style>
