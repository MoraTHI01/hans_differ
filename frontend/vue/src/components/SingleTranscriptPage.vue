<template>
  <HeaderRow />
  <LogoAndVideoSearchbarRow
    :placeholder="t('VideoPlayerView.searchplaceholder')"
    :surveys="mediaItem.surveys"
    :surveys_heading="t('VideoPlayerView.surveybanner')"
  />
  <div class="main-container">
    <div class="video-support-content" ref="containerSupport">
      <TranscriptComponent
        :uuid="uuid"
        :video-playing="false"
        @transcriptLoaded="onTranscriptLoaded"
        class="video-transcript"
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
import TranscriptComponent from "@/components/TranscriptComponent.vue";
import {useMediaStore} from "@/stores/media";
import {useAuthStore} from "@/stores/auth";
import type {MediaItem} from "@/data/MediaItem";
import {matomo_trackpageview} from "@/common/matomo_utils";
import {useI18n} from "vue-i18n";
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

const searchTrie = ref();
const searchTrieSlides = ref();
matomo_trackpageview("?uuid=" + uuid);

const store = useMediaStore();
store.loadAsrResults(uuid);
store.loadTranscriptResults(uuid);
store.loadSearchTrie(uuid).then((test) => {
  loggerService.log("search trie loaded");
  loggerService.log(store.getSearchTrie);
  searchTrie.value = store.getSearchTrie;
});
store.loadSearchTrieSlides(uuid).then((test) => {
  loggerService.log("search trie slides loaded");
  loggerService.log(store.getSearchTrieSlides);
  searchTrieSlides.value = store.getSearchTrieSlides;
});

const authRole = useAuthStore().getRole();

// Element refs
//const searchbar = ref();

/**
 * Emitted by TranscriptComponent if transcript is loaded
 */
function onTranscriptLoaded() {
  const lastGlobalSearchTerms = store.getLastGlobalSearchterms;
  if (lastGlobalSearchTerms !== undefined && lastGlobalSearchTerms.length > 0) {
    //loggerService.log("Add Tabs for global search terms");
    //searchbar.value.search(lastGlobalSearchTerms.map((_) => _).join(" "));
  }
}

const container = ref(null);
const containerSupport = ref(null);

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
