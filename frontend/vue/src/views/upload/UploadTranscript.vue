<template>
  <HeaderRow />
  <LogoAndSearchbarRow
    :placeholder="t('HomeView.searchplaceholder')"
    :showSearch="false"
    :showProgress="true"
    :progressLanguage="'de'"
    :progressLanguageDeMatchStep="3"
    :progressLanguageDeNotMatchStep="3"
    :progressTotalSteps="5"
  />
  <div class="main-container">
    <div class="sub-container management-view">
      <TranscriptChapterSelection v-model="content" />
    </div>
    <UploadNavigation :step="3" :uuid="uuid" @save="generateChapters" v-model:loading="generatingChapters" />
  </div>
  <BottomRow />
</template>

<script lang="ts">
import {routeToRefreshMedia} from "@/common/loadMedia";
export default {
  beforeRouteEnter: routeToRefreshMedia,
};
</script>

<script setup lang="ts">
import HeaderRow from "@/components/HeaderRow.vue";
import BottomRow from "@/components/BottomRow.vue";
import ProgressBar from "@/components/ProgressBar.vue";
import TranscriptChapterSelection from "@/components/TranscriptChapterSelection.vue";
import LogoAndSearchbarRow from "@/components/LogoAndSearchbarRow.vue";
import UploadNavigation from "@/components/UploadNavigation.vue";

import {useI18n} from "vue-i18n";
import {ref} from "vue";
import {useRoute} from "vue-router";
import {useMediaStore} from "@/stores/media";
import router from "@/router";
import {apiClient} from "@/common/apiClient";
import {useAuthStore} from "@/stores/auth";
import {matomo_trackpageview, matomo_clicktracking} from "@/common/matomo_utils";
import {LoggerService} from "@/common/loggerService";

matomo_trackpageview();
const loggerService = new LoggerService();
const {t, locale} = useI18n({useScope: "global"});

const uuid = useRoute().params.uuid as string;

const content = ref<Block[]>([]);
const generatingChapters = ref(false);

const store = useMediaStore();
const authStore = useAuthStore();
const mediaItem = store.getMediaItemByUuid(uuid);
if (!mediaItem || mediaItem.state?.overall_step !== "EDITING" || authStore.getRole() == "everybody") {
  router.push("/upload/overview");
} else {
  Promise.all([store.loadTranscript(uuid), store.loadTopics(uuid)]).then(() => {
    const blocks = [];

    const topicResult = store.topic.data?.find((topic) => topic.language == locale.value);
    if (topicResult?.result) {
      blocks.push({
        start: 0,
        stop: 0,
        chapter: true,
        chapterId: crypto.randomUUID(),
        draggable: false,
      } as Block);
      blocks.push(
        ...topicResult.result.map(
          (entry) =>
            ({
              start: entry.interval[0],
              stop: entry.interval[1],
              chapter: true,
              chapterId: crypto.randomUUID(),
              draggable: true,
            }) as Block,
        ),
      );
    }
    loggerService.log(`Chapter length: ${blocks.length}`);
    // remove index 1 as it has the same start interval as the none draggable first chapter
    if (blocks.length > 1) {
      loggerService.log("Chapter 0");
      loggerService.log(blocks[0]);
      loggerService.log("Chapter 1");
      loggerService.log(blocks[1]);
      const seg_start = store.transcript.segments[0].start;
      loggerService.log(`First sentence start: ${seg_start}`);
      if (blocks[1].start < blocks[0].start + seg_start + 1) {
        loggerService.log("Merge default chapter and first chapter");
        blocks[0].end = blocks[1].end;
        blocks.splice(1, 1);
        if (blocks.length > 1) {
          blocks[0].end = blocks[1].start;
        }
      }
    }
    blocks.push(
      ...store.transcript.segments.map(
        (segment) =>
          ({
            text: segment.transcript,
            start: segment.start,
            stop: segment.stop,
            chapter: false,
            draggable: false,
          }) as Block,
      ),
    );
    content.value = blocks.sort((a, b) => a.start! - b.start!);
  });
}

async function generateChapters(nextUrl: string) {
  generatingChapters.value = true;
  loggerService.log("generateChapters");

  const segments = content.value.reduce((pv, cv) => {
    if (pv.length > 0 && pv[pv.length - 1].chapter && cv.chapter) {
      return pv;
    }
    return [...pv, cv];
  }, [] as Block[]);
  loggerService.log("generateChapters: Segements created");

  //if (segments[0].chapter) {
  //  segments.splice(0, 1);
  //}

  if (segments[segments.length - 1].chapter) {
    segments.splice(-1, 1);
  }

  loggerService.log("generateChapters: Segements cleaned");
  const data: {start: number; stop?: number}[] = [];

  const addStart = (timestamp: number) => data.push({start: timestamp});
  const addStop = (timestamp: number) => (data[data.length - 1].stop = timestamp);
  loggerService.log("generateChapters: Segements start stop");

  addStart(segments[0].start ?? 0);
  loggerService.log("generateChapters: Segements initial start added");

  for (let i = 1; i < segments.length - 1; i++) {
    if (segments[i].chapter && segments[i - 1].stop && segments[i + 1].start) {
      addStop(segments[i - 1].stop!);
      addStart(segments[i + 1].start!);
    }
  }
  loggerService.log("generateChapters: Segements start stop iterated");

  addStop(segments[segments.length - 1].stop!);
  loggerService.log("generateChapters: Segements final stop added");

  const bodyData = {
    uuid,
    data,
  };
  loggerService.log("UploadTranscript: New segmentation");
  loggerService.log(bodyData);

  try {
    await apiClient.put("/chapter-fragmentation", bodyData, {
      headers: {
        "Content-type": "application/json",
        "Access-Control-Allow-Origin": "*",
      },
      // Adjust timeout as needed, currently 360 seconds
      timeout: 360000,
    });
    matomo_clicktracking("click_button", `Upload chapter segmentation for media item: ${uuid}`);
    await router.push(nextUrl);
    generatingChapters.value = false;
  } catch (e) {
    console.error(`Error uploading chapter segmentation for media item: ${uuid}`);
    await router.push("/upload/overview");
  }
}

export interface Block {
  text?: string;
  start?: number;
  stop?: number;
  chapter: boolean;
  chapterId?: string;
  draggable: boolean;
}
</script>

<style scoped>
.main-container {
  width: 100%;
  display: flex;
  flex-direction: column;
  align-items: center;
}

.sub-container {
  width: 100%;
  border: 1px solid var(--hans-light-gray);
  border-radius: 0.25rem;
}

button {
  border: none;
  border-radius: 25%;
  background-color: transparent;
}

button:hover {
  background-color: var(--hans-light-gray);
}

.management-view {
  height: 74vh;
  position: relative;
  overflow-y: scroll;
}
</style>
