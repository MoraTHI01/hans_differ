<template>
  <!-- API button -->
  <router-link @click="matomo_clicktracking('click_button', btntext)" :to="{name: route}" class="btn btn-container">
    <img :src="src" alt="api-btn" class="img-fluid img-btn" />
    <span class="btn-text">{{ btntext }}</span>
  </router-link>
  <!-- API button end -->
</template>

<script setup lang="ts">
import {matomo_clicktracking} from "@/common/matomo_utils";

defineProps<{
  route?: string;
  src: string;
  btntext: string;
}>();
</script>

<style scoped>
/*
 * Style is controllable with CSS variables which default to ButtonLight styles
 */
.btn-container {
  display: flex;
  align-items: center;
  float: left;
  color: var(--hans-light);
}

.btn-container:hover {
  color: var(--button-background-hover, var(--hans-dark));
}

.btn-container:hover {
  background-color: var(--hans-light);
}

.img-btn {
  filter: invert(calc(1 - var(--button-dark-mode, 0)));
}

.btn-text {
  margin-left: 5px;
  color: var(--button-color, var(--hans-light));
}

.btn-container:hover > .img-btn {
  filter: invert(calc(var(--button-dark-mode, 0) - 0));
}

.btn-container:hover > .btn-text {
  color: var(--button-color-hover, var(--hans-dark));
}
</style>
