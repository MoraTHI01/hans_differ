<template>
  <!-- video Highlights -->
  <div class="card-body p-1" v-if="'de' === locale && video.search_highlights?.asr_result_de">
    <h6 class="search-highlights-header">
      {{ t("VideoSummarySearchHighlights.headline")
      }}<ButtonHint route="generalnotes" :hovertext="t('VideoSummarySearchHighlights.hint')" :hint_after="true" />
    </h6>
    <div class="search-highlights" v-for="item of video.search_highlights?.asr_result_de">
      <div v-html="item"></div>
    </div>
  </div>
  <div class="card-body p-1" v-else-if="'en' === locale && video.search_highlights?.asr_result_en">
    <h6 class="search-highlights-header">
      {{ t("VideoSummarySearchHighlights.headline")
      }}<ButtonHint route="generalnotes" :hovertext="t('VideoSummarySearchHighlights.hint')" :hint_after="true" />
    </h6>
    <div class="search-highlights" v-for="item of video.search_highlights?.asr_result_en">
      <div v-html="item"></div>
    </div>
  </div>
  <!-- video Highlights end -->
</template>

<script setup lang="ts">
import {useRoute} from "vue-router";
import {ref} from "vue";
import type {MediaItem} from "@/data/MediaItem.js";
import {matomo_clicktracking} from "@/common/matomo_utils";
import ButtonHint from "@/components/ButtonHint.vue";
import {useI18n} from "vue-i18n";

const {t, locale} = useI18n({useScope: "global"});

const route = ref(useRoute().name);
defineProps<{
  video: MediaItem;
}>();
</script>

<style scoped>
.search-highlights-header {
  /*font-size: 0.7em;*/
}
.search-highlights {
  /*font-size: 0.6em;*/
}
</style>
