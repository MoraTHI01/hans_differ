<template>
  <div>
    <div class="progress mt-3">
      <div
        class="progress-bar"
        role="progressbar"
        :style="{width: progress + '%'}"
        aria-valuenow="progress"
        aria-valuemin="0"
        aria-valuemax="100"
      >
        <!-- {{ progress.toFixed(0) }}% -->
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import {defineProps, computed} from "vue";

interface Props {
  duration: number;
  currentTime: number;
}

// Define component props
const props = defineProps<Props>();

// Compute progress based on currentTime and duration
const progress = computed(() => {
  return (props.currentTime / props.duration) * 100;
});
</script>

<style scoped>
.progress {
  height: 10px; /* Adjust height as needed */
}
.progress-bar {
  transition: width 0.6s ease; /* Smooth transition effect */
}
</style>
