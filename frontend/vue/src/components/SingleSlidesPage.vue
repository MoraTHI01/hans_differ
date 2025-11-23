<template>
  <HeaderRow />
  <LogoAndVideoSearchbarRow
    :placeholder="t('VideoPlayerView.searchplaceholder')"
    :surveys="mediaItem.surveys"
    :surveys_heading="t('VideoPlayerView.surveybanner')"
  />
  <div class="main-container">
    <div class="video-support-content" ref="containerSupport">
      <Slideshow :video="mediaItem" :pdfUrl="useMediaStore().getSlides" ref="slideshowRef" />
    </div>
  </div>
  <BottomRow />
</template>

<script setup lang="ts">
import {ref, computed, nextTick, onMounted, onBeforeUnmount, watch} from "vue";
import HeaderRow from "@/components/HeaderRow.vue";
import BottomRow from "@/components/BottomRow.vue";
import LogoAndVideoSearchbarRow from "@/components/LogoAndVideoSearchbarRow.vue";
import Slideshow from "@/components/Slideshow.vue";
import {useMediaStore} from "@/stores/media";
import {useAuthStore} from "@/stores/auth";
import type {MediaItem} from "@/data/MediaItem";
import {matomo_trackpageview} from "@/common/matomo_utils";
import {useI18n} from "vue-i18n";
import {matomo_clicktracking} from "@/common/matomo_utils";
import {LoggerService} from "@/common/loggerService";

const loggerService = new LoggerService();
const {t, locale} = useI18n({useScope: "global"});
const viewportWidth = ref(window.innerWidth);

const updateViewportWidth = () => {
  viewportWidth.value = window.innerWidth;
};

const props = defineProps<{
  mediaItem: MediaItem;
}>();
const mediaItem = props.mediaItem;
const uuid = mediaItem.uuid!;

const authRole = useAuthStore().getRole();

// Element refs
//const searchbar = ref();

const slideshowRef = ref(null);
const container = ref(null);

onMounted(() => {});

onBeforeUnmount(() => {});
</script>
<style scoped>
.main-container {
  height: 100%;
}

.video-support-content {
  height: 100%;
}

:deep(.swiper-autoheight) {
  margin-top: 1em;
}
</style>
