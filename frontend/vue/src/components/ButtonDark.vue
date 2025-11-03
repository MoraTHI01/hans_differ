<template>
  <MenuButton class="button-dark" :route="route" :src="src" :btntext="btntext" />
</template>

<script setup lang="ts">
import MenuButton from "./MenuButton.vue";

defineProps<{
  route?: string;
  src: string;
  btntext: string;
}>();
</script>

<style scoped>
.button-dark {
  --button-background-hover: var(--hans-dark-blue);
  --button-color: var(--hans-dark);
  --button-color-hover: var(--hans-light);
  --button-dark-mode: 1;
}
</style>
