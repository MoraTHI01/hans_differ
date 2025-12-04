<template>
  <HeaderRow />
  <LogoAndVideoSearchbarRow
    :placeholder="t('VideoPlayerView.searchplaceholder')"
    @searchterms="addWorkbenchTab"
    ref="searchbar"
    :surveys="mediaItem.surveys"
    :surveys_heading="t('VideoPlayerView.surveybanner')"
    :searchInSlides="currSwitchSlidesAndVideo.value"
  />
  <div class="main-container">
    <div v-if="historyStore.isMediaItemInHistory(mediaItem.uuid)">
      <VideoPlayerQuestion :uuid="mediaItem.uuid" @pause="videoPlaying = false" @play="videoPlaying = true" />
    </div>
    <div class="sub-container video-control-elements">
      <div :class="viewportWidth >= 768 ? 'resizable-container' : 'resizable-container-small'" ref="container">
        <div
          v-if="!currSwitchSlidesAndVideo"
          class="resizable-column left-column"
          :style="{width: leftColumnWidth + 'px', maxWidth: leftColumnWidth + 'px'}"
          id="left-column"
          ref="leftColumn"
        >
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
          <MarkerSequence :video="mediaItem" />
          <VideoDescription :video="mediaItem" />
        </div>
        <div
          v-else
          class="resizable-column left-column"
          :style="{width: leftColumnWidth + 'px', maxWidth: leftColumnWidth + 'px'}"
          id="left-column"
          ref="leftColumn"
        >
          <Slideshow :video="mediaItem" :pdfUrl="useMediaStore().getSlides" ref="slideshowRef" />
        </div>
        <Separator
          ref="separator"
          :viewportWidth="viewportWidth"
          :activeIndex="activeIndex"
          @takeVideoSnapshot="takeSnapshot($event)"
          @startResizeBySeparator="startResize($event)"
          @setSyncActiveSeparator="slideshowSetSyncActive($event)"
        ></Separator>
        <div
          class="resizable-column right-column"
          :style="{width: rightColumnWidth + 'px', maxWidth: maxContainerWidth - leftColumnWidth + 'px'}"
          id="right-column"
          ref="rightColumn"
        >
          <nav class="workbench">
            <!-- Only render workbench tabs when there are items in the tabsmap -->
            <WorkbenchTabs
              v-if="tabsmap.size"
              id="nav-tabs"
              :tabsmap="tabsmap"
              @delete-tab="deleteTab"
              @switch-tab="switchTab"
              ref="workbenchTabs"
            />
            <!-- Only render tab-content div when there are items in tabsmap -->
            <div v-if="tabsmap.size || slidesEnabled || summaryEnabled" class="tab-content" id="pills-tabContent">
              <!-- Render the special slides tab whenever slides are enabled -->
              <WorkbenchTabContent :active="slidesActive" tab-id="pdf-slides">
                <div v-if="currSwitchSlidesAndVideo">
                  <VideoPlayer
                    :url="url"
                    :subtitle_de="subtitle_de"
                    :subtitle_en="subtitle_en"
                    :language="language"
                    :uuid="uuid"
                    @pause="videoPlaying = false"
                    @play="videoPlaying = true"
                  />
                  <MarkerSequence :video="mediaItem" />
                  <VideoDescription :video="mediaItem" />
                </div>
                <div v-else>
                  <Slideshow :video="mediaItem" :pdfUrl="useMediaStore().getSlides" ref="slideshowRef" />
                </div>
              </WorkbenchTabContent>
              <!-- Render the special summary tab whenever summary is enabled -->
              <WorkbenchTabContent :active="summaryActive" tab-id="text-summary">
                <VideoSummary :video="mediaItem" />
              </WorkbenchTabContent>
              <!-- Render the special topics tab whenever topics is enabled -->
              <WorkbenchTabContent :active="topicsActive" tab-id="text-topics">
                <VideoTopics :video="mediaItem" />
              </WorkbenchTabContent>
              <!-- Render the special question tab whenever question is enabled -->
              <WorkbenchTabContent :active="questionActive" tab-id="text-question">
                <DynamicQuestionnaire :video="mediaItem" :active="questionActive" />
              </WorkbenchTabContent>
              <!-- Render the special chat tab whenever chat is enabled -->
              <WorkbenchTabContent :active="chatActive" tab-id="text-chat">
                <ChatComponent
                  :uuid="props.mediaItem.uuid"
                  :language="props.mediaItem.language"
                  :active="chatActive"
                  :channelmode="false"
                />
              </WorkbenchTabContent>
              <!-- Render the special question tab whenever question is enabled -->
              <WorkbenchTabContent :active="linksActive" tab-id="external-links">
                <VideoExternalLinks :video="mediaItem" />
              </WorkbenchTabContent>
              <!-- Render the special question tab whenever question is enabled -->
              <WorkbenchTabContent :active="keywordsActive" tab-id="text-keywords">
                <Keywords :video="mediaItem" :active="keywordsActive" @searchterm-from-keywords="addWorkbenchTab" />
              </WorkbenchTabContent>
              <!-- loop over the tabsmap, the syntax unpacks the map in key and value, the value is a object which is destructured -->
              <WorkbenchIntervalTabContent
                v-for="(element, index) in searchResultsMap.values()"
                :tab-id="element.tabId"
                :intervals="element.intervals"
                :active="index + indexOffset === activeIndex"
                :key="index"
                :data-index="index"
                :data-2="1"
              />
            </div>
          </nav>
        </div>
      </div>
    </div>
    <div class="video-support-content" ref="containerSupport">
      <TranscriptComponent
        :uuid="uuid"
        :video-playing="videoPlaying"
        @transcriptLoaded="onTranscriptLoaded"
        class="video-transcript"
      />
    </div>
  </div>
  <BottomRow />
</template>

<script setup lang="ts">
import type {Ref} from "vue";
import {ref, computed, nextTick, onMounted, onBeforeUnmount, watch} from "vue";
import router from "@/router/index";
import type {WordItem} from "@/data/AsrResults";
import HeaderRow from "@/components/HeaderRow.vue";
import BottomRow from "@/components/BottomRow.vue";
import DynamicQuestionnaire from "@/components/DynamicQuestionnaire.vue";
import LogoAndVideoSearchbarRow from "@/components/LogoAndVideoSearchbarRow.vue";
import VideoPlayer from "@/components/VideoPlayer.vue";
import VideoDescription from "@/components/VideoDescription.vue";
import MarkerSequence from "@/components/MarkerSequence.vue";
import VideoTopics from "@/components/VideoTopics.vue";
import TranscriptComponent from "@/components/TranscriptComponent.vue";
import Separator from "@/components/Separator.vue";
import Slideshow from "@/components/Slideshow.vue";
import Keywords from "@/components/Keywords.vue";
import VideoExternalLinks from "@/components/VideoExternalLinks.vue";
import VideoSummary from "@/components/VideoSummary.vue";
import ChatComponent from "@/components/ChatComponent.vue";
import WorkbenchTabs from "@/components/WorkbenchTabs.vue";
import VideoPlayerQuestion from "./VideoPlayerQuestion.vue";
import {Tab} from "@/components/WorkbenchTabs.vue";
import {useMediaStore} from "@/stores/media";
import {useAuthStore} from "@/stores/auth";
import {useChatStore} from "@/stores/chat";
import type {MediaItem} from "@/data/MediaItem";
import WorkbenchTabContent from "@/components/WorkbenchTabContent.vue";
import WorkbenchIntervalTabContent from "@/components/WorkbenchIntervalTabContent.vue";
import {v4 as uuidv4} from "uuid";
import {matomo_trackpageview} from "@/common/matomo_utils";
import {Search} from "@/data/Search";
import {useI18n} from "vue-i18n";
import {TabHeading} from "@/common/tabHeading";
import {matomo_clicktracking} from "@/common/matomo_utils";
import {LoggerService} from "@/common/loggerService";
import {useMessageStore} from "@/stores/message";
import {useHistoryStore} from "@/stores/history";
import videojs from "video.js";

const loggerService = new LoggerService();
const {t, locale} = useI18n({useScope: "global"});
const viewportWidth = ref(window.innerWidth);
const screenshot = ref("");

const updateViewportWidth = () => {
  viewportWidth.value = window.innerWidth;
};

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

// Subtitle in lecturer language
const subtitle = ref(mediaItem.subtitle);
// Subtitle with language ids
const subtitle_de = ref(mediaItem.subtitle_de);
const subtitle_en = ref(mediaItem.subtitle_en);
const language = ref(mediaItem.language);
const searchTrie = ref();
const searchTrieSlides = ref();

const slideshowRef = ref(null);
const playerRef = ref(null);
matomo_trackpageview("?uuid=" + uuid);

const store = useMediaStore();
store.loadTopics(uuid);
store.loadMarkersFromTopics(uuid, locale.value);
store.loadMarker(uuid);
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

store.loadSlidesImagesMeta(uuid);
store.loadSlides(uuid);

const historyStore = useHistoryStore();
const messageStore = useMessageStore();
const chatStore = useChatStore();

const videoPlaying = ref(false);

const tabsmap: Ref<Map<string, Tab>> = ref(new Map());
const searchResultsMap: Ref<Map<string, {tabId: string; intervals: WordItem[][]}>> = ref(new Map());

const authRole = useAuthStore().getRole();

// Controls whether slides should be rendered in an unclosable tab
const slidesEnabled = authRole !== undefined;
const slidesTabUuid = uuidv4();
const currSwitchSlidesAndVideo = ref(store.getSwitchSlidesAndVideo());

if (slidesEnabled) {
  // Add uncloseable slide tab if slides are enabled
  if (currSwitchSlidesAndVideo.value === true) {
    const headingsV = [
      new TabHeading(t("VideoPlayerView.videotabname", "Video", {locale: "de"}), "de"),
      new TabHeading(t("VideoPlayerView.videotabname", "Video", {locale: "en"}), "en"),
    ];
    tabsmap.value.set(slidesTabUuid, Tab.withType(t("VideoPlayerView.videotabname"), headingsV, "mp4", false));
  } else {
    const headings = [
      new TabHeading(t("VideoPlayerView.slidestabname", "Folien", {locale: "de"}), "de"),
      new TabHeading(t("VideoPlayerView.slidestabname", "Slides", {locale: "en"}), "en"),
    ];
    tabsmap.value.set(slidesTabUuid, Tab.withType(t("VideoPlayerView.slidestabname"), headings, "pdf", false));
  }
}

// Controls whether summary should be rendered in an unclosable tab
const summaryEnabled = authRole !== undefined;
if (summaryEnabled) {
  // Add uncloseable summary tab if slides are enabled
  const headings = [
    new TabHeading(t("VideoPlayerView.summarytabname", "Zusammenfassung", {locale: "de"}), "de"),
    new TabHeading(t("VideoPlayerView.summarytabname", "Summary", {locale: "en"}), "en"),
  ];
  tabsmap.value.set(
    uuidv4(),
    Tab.withType(
      t("VideoPlayerView.summarytabname"),
      headings,
      "text",
      false,
      true,
      t("VideoPlayerView.summarytabhinttext"),
    ),
  );
}

// Controls whether topics should be rendered in an unclosable tab
const topicsEnabled = authRole !== undefined;
if (topicsEnabled) {
  // Add uncloseable summary tab if slides are enabled
  const headings = [
    new TabHeading(t("VideoPlayerView.topicstabname", "Themen", {locale: "de"}), "de"),
    new TabHeading(t("VideoPlayerView.topicstabname", "Topics", {locale: "en"}), "en"),
  ];
  tabsmap.value.set(
    uuidv4(),
    Tab.withType(
      t("VideoPlayerView.topicstabname"),
      headings,
      "text",
      false,
      true,
      t("VideoPlayerView.topicstabhinttext"),
    ),
  );
}

// Controls whether chat should be rendered in an unclosable tab
const questionEnabled = authRole !== undefined; //&& ( authRole === "admin" || authRole === "developer" || authRole === "lecturer");
if (questionEnabled) {
  // Add uncloseable chat tab if slides are enabled
  const headings = [
    new TabHeading(t("VideoPlayerView.questiontabname", "Fragen", {locale: "de"}), "de"),
    new TabHeading(t("VideoPlayerView.questiontabname", "Questions", {locale: "en"}), "en"),
  ];
  tabsmap.value.set(
    uuidv4(),
    Tab.withType(
      t("VideoPlayerView.questiontabname"),
      headings,
      "text",
      false,
      true,
      t("VideoPlayerView.questiontabhinttext"),
    ),
  );
}

// TODO: move to message store? chat available
const chatEnabled = authRole !== undefined; //&& ( authRole === "admin" || authRole === "developer" || authRole === "lecturer");
if (chatEnabled) {
  // Add uncloseable chat tab if slides are enabled
  const headings = [
    new TabHeading(t("VideoPlayerView.chattabname", "Chat", {locale: "de"}), "de"),
    new TabHeading(t("VideoPlayerView.chattabname", "Chat", {locale: "en"}), "en"),
  ];
  tabsmap.value.set(
    uuidv4(),
    Tab.withType(t("VideoPlayerView.chattabname"), headings, "text", false, true, t("VideoPlayerView.chattabhinttext")),
  );
}

// Controls whether external links should be rendered in an unclosable tab
const linksEnabled = authRole !== undefined;
if (linksEnabled) {
  // Add uncloseable summary tab if slides are enabled
  const headings = [
    new TabHeading(t("VideoPlayerView.linkstabname", "Links", {locale: "de"}), "de"),
    new TabHeading(t("VideoPlayerView.linkstabname", "Links", {locale: "en"}), "en"),
  ];
  tabsmap.value.set(
    uuidv4(),
    Tab.withType(t("VideoPlayerView.linktabname"), headings, "text", false, true, t("VideoPlayerView.linktabhinttext")),
  );
}

// Controls whether external links should be rendered in an unclosable tab
const keywordsEnabled = authRole !== undefined;
if (keywordsEnabled) {
  // Add uncloseable summary tab if slides are enabled
  const headings = [
    new TabHeading(t("VideoPlayerView.keywordstabname", "Schlagworte", {locale: "de"}), "de"),
    new TabHeading(t("VideoPlayerView.keywordstabname", "Keywords", {locale: "en"}), "en"),
  ];
  tabsmap.value.set(
    uuidv4(),
    Tab.withType(
      t("VideoPlayerView.keywordstabname"),
      headings,
      "text",
      false,
      true,
      t("VideoPlayerView.keywordstabhinttext"),
    ),
  );
}

// Element refs
const workbenchTabs = ref();
const searchbar = ref();

// Workbench tab content active tracking
const activeIndex = ref(0);
const indexOffset =
  (slidesEnabled ? 1 : 0) +
  (summaryEnabled ? 1 : 0) +
  (topicsEnabled ? 1 : 0) +
  (questionEnabled ? 1 : 0) +
  (chatEnabled ? 1 : 0) +
  (linksEnabled ? 1 : 0) +
  (keywordsEnabled ? 1 : 0);
const slidesActive = computed(() => slidesEnabled && activeIndex.value === 0);
const summaryActive = computed(() => summaryEnabled && activeIndex.value === 1);
const topicsActive = computed(() => topicsEnabled && activeIndex.value === 2);
const questionActive = computed(() => questionEnabled && activeIndex.value === 3);
const chatActive = computed(() => chatEnabled && activeIndex.value === 4);
const linksActive = computed(() => linksEnabled && activeIndex.value === 5);
const keywordsActive = computed(() => keywordsEnabled && activeIndex.value === 6);

/**
 * Emitted by TranscriptComponent if transcript is loaded
 */
function onTranscriptLoaded() {
  const lastGlobalSearchTerms = store.getLastGlobalSearchterms;
  if (lastGlobalSearchTerms !== undefined && lastGlobalSearchTerms.length > 0) {
    loggerService.log("Add Tabs for global search terms");
    searchbar.value.search(lastGlobalSearchTerms.map((_) => _).join(" "));
  }
}

/**
 * Looks up the given search terms and adds a workbench tab populated with the search results if results are found and then switches to the new tab.
 * If results are found, the search bar is also cleared. If no results are found, a message is triggered in the search bar to inform the user.
 *
 * @param {string} searchterms - The search term to look up
 */
function addWorkbenchTab(searchterms: Array<string>) {
  // if user provided searchterms
  if (searchterms && searchterms?.length > 0) {
    // then search in transcript for provided searchterm
    loggerService.log("searchterms", searchterms);
    const transcript = store.getTranscript;
    const search = new Search();
    const intervals = search.search(searchterms, 10, 20, transcript);
    loggerService.log(intervals);
    // Ignore searches with empty results
    if (intervals?.length < 1 && searchterms?.length > 0) {
      loggerService.log("Searches with empty results detected!");
      searchbar.value.setNotFound();
    } else {
      // Clear searchbar if the searchterm was found to allow quickly searching for multiple terms
      searchbar.value.clearSearch();
      // add the new tab-button and tab-pane which is active by default, to the map of tab-buttons which is rendered reactively
      let tabname = searchterms.join(" ");
      const tab = Tab.withType(tabname, "searchterms", true);
      const uuid = uuidv4();
      tabsmap.value.set(uuid, tab);
      searchResultsMap.value.set(uuid, {tabId: tab.tabId, intervals});
      // Switch to newly opened tab
      workbenchTabs.value.switchTo(tabsmap.value.size - 1);
    }
  }
}

/**
 * Handles tab deletion requests (mainly from the tab close button) by deleting both the tab and its content.
 * In cases where the currently active tab is located to the right of the deleted tab, the tab selection is also corrected so the
 * selected tab doesn't switch unexpectedly
 *
 * @param {object} event - The deleteTab event
 * @param {string} event.uuid - The uuid of the deleted Tab
 * @param {number} event.index - The index of the deleted Tab in the tab list
 */
function deleteTab({uuid, index}: {uuid: string; index: number}) {
  // delete the tab-button and tab-content by its UUID from the tabs map
  tabsmap.value.delete(uuid);
  searchResultsMap.value.delete(uuid);
  // Keeps the correct tabs selected if the active tab is to the right of the deleted tab
  if (activeIndex.value > index) {
    workbenchTabs.value.switchTo(activeIndex.value - 1);
  }
}

/**
 * Handles tabs being switched in the tab bar either manually or as a result of, e.g., deletion and also switches to the correct tab content pane
 *
 * @param {number} index - The index of the tab that is now active
 */
const switchTab = async (index: number): Promise<T> => {
  activeIndex.value = index;
  // Load/check chat services status if chat tab is clicked
  if (activeIndex.value === 3 || activeIndex.value === 4) {
    messageStore.setServicesRequired(true);
    await messageStore.fetchServiceStatus();
  } else {
    messageStore.setServicesRequired(false);
  }
};

const container = ref(null);
const containerSupport = ref(null);
const separator = ref(null);

const aspectRatio = 2.5; // Initial aspect ratio 2.5:1
let maxContainerWidth = 0;
const leftColumnWidth = ref(250); // Initial left column width
const rightColumnWidth = ref(100); // Calculate initial right column width based on aspect ratio
let isResizing = false;
let startX = 0;
let startLeftColumnWidth = 0;
let startRightColumnWidth = 0;

onMounted(() => {
  window.addEventListener("resize", updateViewportWidth);
  maxContainerWidth = container.value.clientWidth;
  leftColumnWidth.value = maxContainerWidth - maxContainerWidth / aspectRatio; // Initial left column width
  rightColumnWidth.value = maxContainerWidth / aspectRatio; // Calculate initial right column width based on aspect ratio
  chatStore.loadChatSettings();
});

onBeforeUnmount(() => {
  window.removeEventListener("resize", updateViewportWidth);
  messageStore.setServicesRequired(false);
  chatStore.storeChatSettings();
});

const slideshowSetSyncActive = (value: boolean) => {
  slideshowRef.value.setSyncActive(value);
};

const takeSnapshot = () => {
  const videoElement = document.getElementsByTagName("video")[0];

  // Create a canvas element
  const canvas = document.createElement("canvas");
  canvas.width = videoElement.videoWidth;
  canvas.height = videoElement.videoHeight;

  // Draw the current video frame onto the canvas
  const context = canvas.getContext("2d");
  context.drawImage(videoElement, 0, 0, canvas.width, canvas.height);

  // Convert the canvas to a base64-encoded PNG
  const base64img = canvas.toDataURL("image/png");
  messageStore.setVideoSnapshot(base64img);
};

const startResize = (event: MouseEvent) => {
  if ("touches" in event) {
    startX = event.touches[0].pageX;
    matomo_clicktracking("click_start_resize", "video_and_workbench_view_touch");
  } else {
    startX = (event as MouseEvent).pageX;
    matomo_clicktracking("click_start_resize", "video_and_workbench_view_mouse");
  }

  isResizing = true;
  startLeftColumnWidth = leftColumnWidth.value;
  startRightColumnWidth = rightColumnWidth.value;

  document.addEventListener("mousemove", resize);
  document.addEventListener("mouseup", stopResize);
  document.addEventListener("touchmove", resize);
  document.addEventListener("touchend", stopResize);
};

const stopResize = () => {
  isResizing = false;
  matomo_clicktracking("click_stop_resize", "video_and_workbench_view");
  document.removeEventListener("mousemove", resize);
  document.removeEventListener("mouseup", stopResize);
  document.removeEventListener("touchmove", resize);
  document.removeEventListener("touchend", stopResize);
};

const resize = (event: MouseEvent) => {
  let clientX;
  if ("touches" in event) {
    clientX = event.touches[0].pageX;
  } else {
    clientX = (event as MouseEvent).pageX;
  }

  if (isResizing) {
    let diffX = clientX - startX;
    let newLeftColumnWidth = startLeftColumnWidth + diffX;
    let newRightColumnWidth = startRightColumnWidth - diffX;

    // Ensure minimum width of 100px for each column
    newLeftColumnWidth = Math.max(100, newLeftColumnWidth);
    newRightColumnWidth = Math.max(100, newRightColumnWidth);

    // Ensure total width does not exceed max container width
    if (!isNaN(maxContainerWidth) && newLeftColumnWidth + newRightColumnWidth > maxContainerWidth) {
      const diff = newLeftColumnWidth + newRightColumnWidth - maxContainerWidth;
      if (newLeftColumnWidth >= newRightColumnWidth) {
        newLeftColumnWidth -= diff;
        newRightColumnWidth = newLeftColumnWidth / aspectRatio;
      } else {
        newRightColumnWidth -= diff;
        newLeftColumnWidth = newRightColumnWidth * aspectRatio;
      }
    }

    leftColumnWidth.value = newLeftColumnWidth;
    rightColumnWidth.value = newRightColumnWidth;
  }
};
</script>
<style scoped>
.video-support-content {
  width: min(98vw, max(100ch, 124vh));
}
.resizable-container {
  display: flex;
  flex-direction: row;
  /*height: 60vh; /* Set an initial height */
  height: fit-content;
  border: 1px solid #ccc; /* Add a border for visual separation */
  max-width: min(98vw, max(100ch, 124vh));
  width: min(98vw, max(100ch, 124vh));
}

.resizable-container-small {
  display: block;
  /*height: 60vh; /* Set an initial height */
  height: min-content;
  border: 1px solid #ccc; /* Add a border for visual separation */
  max-width: min(100vw, max(100ch, 124vh));
  width: min(100vw, max(100ch, 124vh));
}

.resizable-column {
  overflow: auto;
  padding: 15px;
  min-width: 365px;
}

.left-column {
  flex: 3; /* Initial ratio: 3 */
  overflow: hidden;
}

.right-column {
  flex: 1; /* Initial ratio: 1 */
  overflow: hidden;
}

.workbench {
  position: sticky;
  display: flex;
  flex-direction: column;
  /* Make the container as tall as the viewport height so everything always stays in view while scrolling */
  max-height: 100vh;
  top: 0;
  z-index: 2;
  grid-row: 1 / 3;
  grid-column: 2;
}

.tab-content {
  overflow: auto;
}

.red-text {
  color: var(--hans-error);
}

/* Hides scroll bar if all workbench tabs are closed */
nav:empty {
  overflow: auto;
}

.video-control-elements {
  display: flex;
}

.video-transcript {
  margin-bottom: 2.5%;
  height: 200px;
}

@media (max-aspect-ratio: 3/4) {
  .video-control-elements {
    grid-template-columns: 100%;
    grid-template-rows: repeat(3, auto);
  }

  .video-transcript {
    grid-row: 3;
    height: 100px;
  }

  .workbench {
    position: static;
    max-height: 40vh;
    grid-column: 1;
    grid-row: 2;
  }
}
</style>
