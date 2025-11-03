<template>
  <!-- video Highlights -->
  <div class="card-body p-1">
    <!-- <h6 class="summary-header">{{ title }}</h6> -->
    <div class="summary">
      <p>{{ summary }}</p>
    </div>
  </div>
  <!-- video Highlights end -->
</template>

<script setup lang="ts">
import {ref, watch} from "vue";
import type {Summary, SummaryItem} from "@/data/Summary";
import type {MediaItem} from "@/data/MediaItem.js";
import {matomo_clicktracking} from "@/common/matomo_utils";
import {useI18n} from "vue-i18n";
import {useMediaStore} from "@/stores/media";

const {t, locale} = useI18n({useScope: "global"});
const store = useMediaStore();

const props = defineProps<{
  video: MediaItem;
}>();

const title = ref("Loading");
const text = ref();
const summary = ref();
// TODO: FIX LLM Handling here (should be not needed if proper resopnses are coming)
const updateSummary = async (): Promise<T> => {
  const summaryResult = await store.loadSummary(props.video?.uuid);
  for (const item in summaryResult.data) {
    const summaryData = summaryResult.data[item] as Summary;
    if (summaryData.language === locale.value) {
      for (const result in summaryData.result) {
        const summaryItem = summaryData.result[result] as SummaryItem;
        if (summaryItem.title !== undefined && summaryItem.title.length > summaryItem.summary.length) {
          if (summaryItem.title?.indexOf("HAnSi") > -1) {
            summary.value = summaryItem.title
              ?.replace("\\", "")
              .replace(
                "HAnSi, as an AI, I am unable to view the video transcript you provided. However, I can still help you with the text summary.",
                "",
              )
              .replace("HAnSi, I have generated a text summary for you.", "")
              .replace(".\\ n * ", ". ")
              .replace(" _ ", "_");
          } else {
            summary.value = summaryItem.title?.replace("\\", "").replace(".\\ n * ", ". ").replace(" _ ", "_");
          }
        } else {
          summary.value = summaryItem.summary
            ?.replace("\\", "")
            .replace(". n * ", ". ")
            .replace("The text summary is as follows: ", "")
            .replace("Der Text fasst folgendermaßen zusammen: ", "")
            .replace(" _ ", "_");
        }
        title.value = summaryItem.title;
        return;
      }
    }
  }
  return;
};

// Watch the locale to register for language changes and switch summary dep. on locale
watch(locale, async (newText) => {
  title.value = "Loading";
  updateSummary();
});

watch(text, async (newText) => {
  if (title.value === "Loading") {
    updateSummary();
  }
});
text.value = "Load";
</script>

<style scoped>
.summary {
  overflow-y: auto;
}
</style>
