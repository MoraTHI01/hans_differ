<template>
  <div
    class="interval"
    @click="sendPosition(searchResult.interval, props.interval[0].index, null)"
    v-html="searchResult.content"
  ></div>
</template>

<script setup lang="ts">
import {SetPositionEvent} from "@/common/events";
import {computed, inject} from "vue";
import type {Emitter, EventType} from "mitt";
import {matomo_clicktracking} from "@/common/matomo_utils";
import type {WordItem} from "@/data/AsrResults";

const props = defineProps<{
  interval: Array<WordItem>;
}>();

const searchResult = computed(() => {
  let content = "";
  for (const wordElement of props.interval) {
    content += wordElement.html;
  }
  if (props.interval[0]) {
    return {interval: props.interval[0].interval[0], content: content};
  } else {
    return {interval: 0, content: content};
  }
});
const eventBus: Emitter<Record<EventType, unknown>> = inject("eventBus")!;

function sendPosition(position: number, index: number, searchterm: string | null) {
  matomo_clicktracking(
    "click_in_media_search_results",
    "word: " + searchterm + " - pos: " + position + " - index: " + index,
  );
  eventBus.emit("setPositionEvent", new SetPositionEvent(position, "transcript", index));
}
</script>

<style scoped>
.interval {
  width: auto;
  min-height: 55px;
  background-color: var(--hans-light-gray);
  opacity: 0.5;
  margin-bottom: 5px;
  padding: 5px;
}

.interval:hover {
  background-color: var(--hans-light-gray);
  opacity: 1;
  cursor: pointer;
}

.searchtearm {
  font-weight: bold;
}
</style>
