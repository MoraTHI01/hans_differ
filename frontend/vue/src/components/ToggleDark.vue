<template>
  <ToggleSwitch class="toggle-dark" :route="route" :tgltext="tgltext" :value="value" />
</template>

<script setup lang="ts">
import ToggleSwitch from "./ToggleSwitch.vue";

defineProps<{
  route?: string;
  tgltext: string;
  value: boolean;
}>();
</script>

<style scoped>
.toggle-dark {
  --button-background-hover: var(--hans-dark-blue);
  --button-color: var(--hans-dark);
  --button-color-hover: var(--hans-light);
  --button-dark-mode: 1;
}
</style>
