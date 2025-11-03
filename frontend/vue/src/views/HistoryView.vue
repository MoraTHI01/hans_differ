<template>
  <HeaderRow />
  <LogoAndSearchbarRow :placeholder="t('HistoryView.searchplaceholder')" :showSearch="true" :showProgress="false" />
  <div class="main-container">
    <MenuBanner :menutext="t('HistoryView.menutext')" />
    <div class="row sub-container history-media">
      <LoadingBar class="media-loading" v-if="historyStore.getHistoryLoading || itemsLoading" />
      <VideoCard class="col-3" v-for="item in currentHistoryMediaItems" :video="item" :show_position="true" />
    </div>
  </div>
  <BottomRow />
</template>

<script setup lang="ts">
import LoadingBar from "@/components/LoadingBarComponent.vue";
import HeaderRow from "@/components/HeaderRow.vue";
import BottomRow from "@/components/BottomRow.vue";
import LogoAndSearchbarRow from "@/components/LogoAndSearchbarRow.vue";
import VideoCard from "@/components/VideoCard.vue";
import MenuBanner from "@/components/MenuBanner.vue";

import {ref, onBeforeUnmount, onMounted, watch} from "vue";
import {useMediaStore} from "@/stores/media";
import {useHistoryStore} from "@/stores/history";
import {matomo_trackpageview} from "@/common/matomo_utils";
import {useI18n} from "vue-i18n";
import {LoggerService} from "@/common/loggerService";

matomo_trackpageview();

const loggerService = new LoggerService();
const {t, locale} = useI18n({useScope: "global"});

const mediaStore = useMediaStore();
const historyStore = useHistoryStore();

const currentHistoryMediaItems = ref([]);
const currentHistory = ref(null);
const itemsLoading = ref(false);

// No automatic local search should be done if on home view
mediaStore.setLastGlobalSearchterms([]);

onMounted(async () => {
  itemsLoading.value = true;
  historyStore.loadHistory().then(async () => {
    currentHistory.value = historyStore.getMediaHistory;
    const sortedArray = Array.from(currentHistory.value.entries());
    // Sort the array by the 'access' date in descending order (most recent first)
    sortedArray.sort((a, b) => {
      const dateA = new Date(a[1].access).getTime(); // Convert to Date and get time in ms
      const dateB = new Date(b[1].access).getTime();
      return dateB - dateA; // Sort descending (most recent first)
    });
    for (const [key] of sortedArray) {
      loggerService.log(`HistoryView:LoadMediaItem: ${key}`);
      currentHistoryMediaItems.value.push(await mediaStore.getMedia(key, true));
    }
    itemsLoading.value = false;
  });
});

onBeforeUnmount(() => {
  historyStore.storeHistory();
});
</script>

<style scoped>
.media-loading {
  --bar-height: 0.4em;
}

.history-media {
  position: relative;
}

@media (max-aspect-ratio: 3/4) {
  .history-media {
    justify-content: center;
  }
}
</style>
