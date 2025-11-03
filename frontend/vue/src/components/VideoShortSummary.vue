<template>
  <!-- video Highlights -->
  <div v-if="route === 'SearchResults'">
    <div class="card-body p-1">
      <h6 class="short-summary-header">
        {{ t("VideoShortSummary.headline")
        }}<ButtonHint route="generalnotes" :hovertext="t('VideoShortSummary.hint')" :hint_after="true" />
      </h6>
      <div class="short-summary">
        <p>{{ summary }}</p>
      </div>
    </div>
  </div>
  <!-- video Highlights end -->
</template>

<script setup lang="ts">
import {ref, watch} from "vue";
import type {MediaItem} from "@/data/MediaItem.js";
import {matomo_clicktracking} from "@/common/matomo_utils";
import {useI18n} from "vue-i18n";
import {useMediaStore} from "@/stores/media";
import {useRoute} from "vue-router";
import ButtonHint from "@/components/ButtonHint.vue";
import type {Summary, SummaryItem} from "@/data/Summary";

const {t, locale} = useI18n({useScope: "global"});
const route = ref(useRoute().name);
const store = useMediaStore();

const props = defineProps<{
  video: MediaItem;
}>();

const text = ref();
const summary = ref("Loading");

watch(text, async (newText) => {
  if (summary.value === "Loading") {
    const summaryResult = await store.loadShortSummary(props.video?.uuid);
    for (const item in summaryResult.data) {
      const summaryData = summaryResult.data[item] as Summary;
      if (summaryData.language === locale.value) {
        for (const result in summaryData.result) {
          const summaryItem = summaryData.result[result] as SummaryItem;
          summary.value = summaryItem.summary;
          return;
        }
      }
    }
  }
});
text.value = "Load";
</script>

<style scoped>
.red-text {
  color: var(--hans-error);
}
.short-summary-header {
  /*font-size: 0.8em;*/
}
.short-summary {
  /*font-size: 0.7em;*/
}
</style>
