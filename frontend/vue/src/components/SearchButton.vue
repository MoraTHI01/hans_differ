<template>
  <button class="search-button" tabindex="-1" aria-hidden="true" @click="search">
    <div v-if="props.localSearch" class="local-search-container">
      <img class="img-search-file" src="/bootstrap-icons/file-earmark-text.svg" alt="search" />
      <img class="img-search" src="/bootstrap-icons/search.svg" alt="search" />
    </div>
    <div v-else>
      <img src="/bootstrap-icons/search.svg" alt="search" />
    </div>
  </button>
</template>

<script setup lang="ts">
const props = defineProps<{
  search: () => void;
  localSearch: boolean;
}>();
</script>

<style scoped>
.search-button {
  all: unset;
  position: absolute;
  right: 20px;
  cursor: pointer;
  /* TODO: Better workaround sizing issue? */
  display: flex;
  transition: opacity 0.2s ease-in-out;
}

.search-button:hover {
  opacity: 0.5;
}

.local-search-container {
  scale: 1.5;
}

.img-search {
  display: flex;
  position: relative;
  top: -9px;
  left: 1px;
  scale: 0.6;
}

.img-search-file {
  display: flex;
  position: relative;
  top: 8px;
}
</style>
