<template>
  <div
    class="tab-pane fade show content"
    :class="{active: props.active ? 'active' : ''}"
    :id="id"
    role="tabpanel"
    :aria-labelledby="id"
  >
    <slot />
  </div>
</template>

<script setup lang="ts">
import {computed} from "vue";

const props = defineProps<{
  tabId: string;
  active: boolean;
}>();
const id = computed(() => `pills-${props.tabId}`);
</script>

<style scoped></style>
