<template>
  <!-- logo and searchbar row -->
  <div class="row logo-row-container justify-content-center">
    <div class="row align-items-center logo-row">
      <LogoBig class="main-logo" />
      <!-- Additional logo row content-->
      <slot></slot>
    </div>
  </div>
</template>

<script setup lang="ts">
import LogoBig from "./LogoBig.vue";
</script>

<style scoped>
.logo-row-container {
  width: 100%;
  margin: 0;
}

.logo-row {
  width: var(--container-width);
}

.main-logo {
  padding-left: 0;
  display: flex;
}
</style>
