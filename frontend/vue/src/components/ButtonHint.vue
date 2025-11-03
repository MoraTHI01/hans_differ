<template>
  <!-- API button -->
  <router-link @click="matomo_clicktracking('click_button', '*')" :to="{name: route}" class="btn-container">
    <span v-if="props.hint_after" class="btn-text" :title="hovertext">*</span>
    <span v-else-if="props.hint_before" class="btn-text-before" :title="hovertext">*</span>
  </router-link>
  <!-- API button end -->
</template>

<script setup lang="ts">
import {matomo_clicktracking} from "@/common/matomo_utils";

const props = withDefaults(
  defineProps<{
    route?: string;
    hovertext?: string;
    hint_before?: boolean;
    hint_after?: boolean;
  }>(),
  {
    hint_before: false,
    hint_after: true,
  },
);
</script>

<style scoped>
/*
   * Style is controllable with CSS variables which default to ButtonLight styles
   */
.btn-container {
  position: relative; /* Required for positioning the pseudo-element */
  text-decoration: none;
}
.btn-container:hover::before {
  position: absolute;
  background-color: rgba(0, 0, 0, 0.7); /* Background color for the hover text */
  color: #fff; /* Text color for the hover text */
  padding: 5px; /* Padding for the hover text */
  border-radius: 5px; /* Optional: Rounded corners for the hover text */
  top: -30px; /* Positioning the hover text above the span */
  left: 0; /* Optional: Adjust horizontal position of the hover text */
  z-index: 1; /* Ensure hover text appears above other elements */
  white-space: nowrap; /* Prevent wrapping of hover text */
}
.btn-text {
  margin-left: 0.2em;
  color: var(--hans-error);
  text-decoration: none;
  margin-top: -1.3em;
  display: table-caption;
}
.btn-text-before {
  margin-left: 0em;
  color: var(--hans-error);
  text-decoration: none;
  margin-top: -1.3em;
  display: table-caption;
}
</style>
