<template>
  <HeaderRow />
  <LogoAndSearchbarRow :placeholder="t('HomeView.searchplaceholder')" :showSearch="false" :showProgress="false" />
  <div class="main-container">
    <MenuBanner :menutext="t('UploadOverviewView.menutext')" />
    <div v-if="isLoading" class="row sub-container media-load-container">
      <LoadingBar class="media-loading" />
    </div>
    <div v-else class="col sub-container media-overview-container">
      <UploadOverviewItem v-for="item in mediaItems" :media="item" />
    </div>
  </div>
  <BottomRow />
</template>

<script setup lang="ts">
import LoadingBar from "@/components/LoadingBarComponent.vue";
import HeaderRow from "@/components/HeaderRow.vue";
import BottomRow from "@/components/BottomRow.vue";
import UploadOverviewItem from "@/components/UploadOverviewItem.vue";
import LogoAndSearchbarRow from "@/components/LogoAndSearchbarRow.vue";
import MenuBanner from "@/components/MenuBanner.vue";

import {useI18n} from "vue-i18n";
import {useMediaStore} from "@/stores/media";
import {useMessageStore} from "@/stores/message";
import {onBeforeUnmount, ref, watch} from "vue";
import type {MediaItem} from "@/data/MediaItem";
import {matomo_trackpageview} from "@/common/matomo_utils";

matomo_trackpageview();

const {t, locale} = useI18n({useScope: "global"});
const mediaItems = ref<MediaItem[]>([]);

const store = useMediaStore();
const messageStore = useMessageStore();
const isLoading = ref(true);
messageStore.setServicesRequired(true);
loadMedia(true);

watch(locale, loadMedia(true));

let timeout: number;
function loadMedia(first_load: boolean = false) {
  if (first_load === true) {
    isLoading.value = true;
  }
  messageStore.fetchServiceStatus();
  store.loadUploadedMedia().then(() => {
    mediaItems.value = Array.from(store.getUploadedMedia);
    isLoading.value = false;

    if (mediaItems.value.some((item) => item.state?.overall_step === "PROCESSING")) {
      clearTimeout(timeout);
      timeout = setTimeout(loadMedia, 30 * 1000);
    }
  });
}

onBeforeUnmount(() => {
  messageStore.setServicesRequired(false);
});
</script>

<style scoped>
.media-loading {
  --bar-height: 0.4em;
}

.media-overview-container {
  width: 100%;
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  align-items: center;
  position: relative;
}

.media-load-container {
  position: relative;
}

@media (max-aspect-ratio: 3/4) {
  .media-overview-container {
    justify-content: center;
  }
  .media-load-container {
    justify-content: center;
  }
}
</style>
