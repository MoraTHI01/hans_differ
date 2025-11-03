<template>
  <div class="form-check form-switch tgl-container">
    <input
      class="form-check-input tgl-box"
      id="flexSwitchCheckDefault"
      type="checkbox"
      role="switch"
      :checked="value"
      @click="matomo_clicktracking('click_toggle', tgltext)"
      :to="{name: route}"
    />
    <label class="form-check-label tgl-text" for="flexSwitchCheckDefault">{{ tgltext }}</label>
  </div>
</template>

<script setup lang="ts">
import {matomo_clicktracking} from "@/common/matomo_utils";

defineProps<{
  route?: string;
  tgltext: string;
  value: boolean;
}>();
defineEmits(["update:toggleValue"]);
</script>

<style scoped>
/*
 * Style is controllable with CSS variables which default to ButtonLight styles
 */
.tgl-box {
  left: 2em;
  position: relative;
}

.tgl-container {
  display: flex;
  align-items: center;
  float: left;
  color: var(--hans-light);
}

.tgl-container:hover {
  color: var(--button-background-hover, var(--hans-dark));
}

.tgl-container:hover {
  background-color: var(--hans-light);
}

.tgl-text {
  margin-left: 5px;
  color: var(--button-color, var(--hans-light));
  position: relative;
  left: 2em;
}

.tgl-container:hover > .img-btn {
  filter: invert(calc(var(--button-dark-mode, 0) - 0));
}

.tgl-container:hover > .btn-text {
  color: var(--button-color-hover, var(--hans-dark));
}
</style>
