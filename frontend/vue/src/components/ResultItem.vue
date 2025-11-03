<template>
  <li class="list-group-item d-flex justify-content-between align-items-center">
    {{ resultItem.word }}
    <span class="badge bg-primary badge-pill">{{ resultItem.occurences.length }} </span>
  </li>
</template>

<script setup lang="ts">
const props = defineProps<{
  resultItem;
}>();
</script>

<style>
.badge {
  pointer-events: none;
}
</style>
