<template>
  <WorkbenchTabContent :active="props.active" :tab-id="props.tabId">
    <div v-if="props.intervals.length" class="search-summary">
      <span class="search-result-count">{{ props.intervals.length }}</span>
      {{ t("WorkbenchIntervalTabContent.foundtext") }}
    </div>
    <IntervalComponent v-for="item in props.intervals" :interval="item" />
  </WorkbenchTabContent>
</template>

<script setup lang="ts">
import IntervalComponent from "@/components/IntervalComponent.vue";
import WorkbenchTabContent from "@/components/WorkbenchTabContent.vue";
import {matomo_clicktracking} from "@/common/matomo_utils";
import {useI18n} from "vue-i18n";
import type {WordItem} from "@/data/AsrResults";

const {t} = useI18n({useScope: "global"});
const props = defineProps<{
  tabId: string;
  intervals: WordItem[][];
  active: boolean;
}>();

matomo_clicktracking("in_media_search_results", "count: " + props.intervals.length);
</script>

<style scoped>
.search-result-list {
  overflow-y: auto;
  max-height: 20vh;
  transition: max-height linear 0.1s;
}
.search-result-list:empty {
  max-height: 0;
}
/* Adds margin if .search-summary is visible */
.search-result-list:last-child {
  margin-bottom: 1vh;
}
.search-summary {
  color: #777777;
}
.search-result-count {
  font-weight: bold;
}
</style>
