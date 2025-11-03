<template>
  <ToggleSwitch class="toggle-light" :route="route" :tgltext="tgltext" :value="value" />
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
.toggle-light {
  --button-background-hover: var(--hans-dark);
  --button-color: var(--hans-light);
  --button-color-hover: var(--hans-dark);
  --button-dark-mode: 0;
}
</style>
