<template>
  <HeaderRow />
  <LogoAndVideoSearchbarRow
    :placeholder="t('VideoPlayerView.searchplaceholder')"
    :surveys="mediaItem.surveys"
    :surveys_heading="t('VideoPlayerView.surveybanner')"
  />
  <div class="main-container">
    <div class="video-support-content" ref="containerSupport">
      <div v-if="historyStore.isMediaItemInHistory(mediaItem.uuid)">
        <VideoPlayerQuestion :uuid="mediaItem.uuid" @pause="videoPlaying = false" @play="videoPlaying = true" />
      </div>
      <VideoPlayer
        ref="playerRef"
        :url="url"
        :subtitle_de="subtitle_de"
        :subtitle_en="subtitle_en"
        :language="language"
        :uuid="uuid"
        @pause="videoPlaying = false"
        @play="videoPlaying = true"
      />
    </div>
  </div>
  <BottomRow />
</template>

<script setup lang="ts">
import {ref, computed, nextTick, onMounted, onBeforeUnmount, watch} from "vue";
import HeaderRow from "@/components/HeaderRow.vue";
import BottomRow from "@/components/BottomRow.vue";
import LogoAndVideoSearchbarRow from "@/components/LogoAndVideoSearchbarRow.vue";
import VideoPlayerQuestion from "./VideoPlayerQuestion.vue";
import {useHistoryStore} from "@/stores/history";
import type {MediaItem} from "@/data/MediaItem";
import {matomo_trackpageview} from "@/common/matomo_utils";
import {useI18n} from "vue-i18n";
import {matomo_clicktracking} from "@/common/matomo_utils";
import {LoggerService} from "@/common/loggerService";
import VideoPlayer from "@/components/VideoPlayer.vue";
import videojs from "video.js";

const loggerService = new LoggerService();
const {t, locale} = useI18n({useScope: "global"});

const props = defineProps<{
  mediaItem: MediaItem;
}>();

const mediaItem = props.mediaItem;
const uuid = mediaItem.uuid!;

const video = ref(mediaItem);
const url = ref(mediaItem.media);
const use_hls = videojs.browser.IS_ANY_SAFARI && videojs.browser.IS_IOS;
if (use_hls && mediaItem.media_hls !== "none") {
  url.value = mediaItem.media_hls;
}

const playerRef = ref(null);

// Subtitle in lecturer language
const subtitle = ref(mediaItem.subtitle);
// Subtitle with language ids
const subtitle_de = ref(mediaItem.subtitle_de);
const subtitle_en = ref(mediaItem.subtitle_en);
const language = ref(mediaItem.language);

matomo_trackpageview("?uuid=" + uuid);
const historyStore = useHistoryStore();
const containerSupport = ref(null);

const videoPlaying = ref(false);

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

.video-transcript {
  margin-bottom: 2.5%;
  height: 100%;
}

@media (max-aspect-ratio: 3/4) {
  .video-transcript {
    grid-row: 3;
  }
}
</style>
