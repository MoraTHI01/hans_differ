<template>
  <MenuButton class="button-light" :route="route" :src="src" :btntext="btntext" />
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
.button-light {
  --button-background-hover: var(--hans-dark);
  --button-color: var(--hans-light);
  --button-color-hover: var(--hans-dark);
  --button-dark-mode: 0;
}
</style>
