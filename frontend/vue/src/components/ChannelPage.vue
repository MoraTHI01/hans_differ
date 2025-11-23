<template>
  <HeaderRow />
  <LogoAndSearchbarRow
    :placeholder="t('ChannelPage.searchplaceholder')"
    :showSearch="true"
    :showProgress="false"
    :showLayoutOptions="true"
    :showLayoutOptionsChannelMode="true"
  />
  <div class="main-container">
    <MenuBanner
      :menutext="t('ChannelsView.menutext')"
      :submenu="true"
      :submenutext="props.channelItem.course_acronym"
      :menuroute="'channels'"
    />
    <div class="sub-container channel-elements">
      <div :class="viewportWidth >= 768 ? 'resizable-container' : 'resizable-container-small'" ref="container">
        <div
          class="resizable-column left-column"
          :style="viewportWidth > 810 ? {width: leftColumnWidth + 'px', maxWidth: leftColumnWidth + 'px'} : {}"
          id="left-column"
          ref="leftColumn"
        >
          <!-- Bootstrap Tabs for switching between contextList and contextListtranslation -->
          <ul class="nav nav-tabs" id="myChannelTab" role="tablist">
            <li class="nav-item" role="presentation">
              <button
                class="nav-link active"
                id="channel-media-tab"
                data-bs-toggle="tab"
                data-bs-target="#channel-media"
                type="button"
                role="tab"
                aria-controls="channel-media"
                aria-selected="true"
                @click="searchNow()"
              >
                {{ t("ChannelPage.media") }}
              </button>
            </li>
            <li v-if="documentManEnabled" class="nav-item" role="presentation">
              <button
                class="nav-link"
                id="channel-documents-tab"
                data-bs-toggle="tab"
                data-bs-target="#channel-documents"
                type="button"
                role="tab"
                aria-controls="channel-documents"
                aria-selected="false"
              >
                {{ t("ChannelPage.documents") }}
              </button>
            </li>
          </ul>
          <!-- Tab Content -->
          <div class="tab-content mt-3" id="myChannelTabContent">
            <!-- First Tab: Context List -->
            <div
              class="tab-pane fade show active"
              id="channel-media"
              role="tabpanel"
              aria-labelledby="channel-media-tab"
            >
              <div class="row search-results" :style="viewportWidth >= 768 ? 'height: 64vh;' : 'height: 33vh;'">
                <div class="found-media">
                  <LoadingBar class="media-loading" v-if="mediaStore.getFoundMediaLoading" />
                  <router-link
                    class="media-item-link"
                    :to="{name: 'VideoPlayer', query: {uuid: item.uuid}}"
                    @click="matomo_clicktracking('click_mediaitem', item.title)"
                    v-for="(item, index) in mediaStore.getFoundMedia"
                    :key="index"
                  >
                    <VideoCard
                      :class="[
                        'row',
                        'rounded',
                        'channel-media',
                        {'selected-media': selectedMediaItem === item, 'padded-item': index > 0},
                      ]"
                      video-classes="col-4"
                      :video="item"
                      @click="selectedMediaItem = item"
                    />
                  </router-link>
                </div>
              </div>
            </div>
            <div
              v-if="documentManEnabled"
              class="tab-pane fade"
              id="channel-documents"
              role="tabpanel"
              aria-labelledby="channel-documents-tab"
            >
              <div class="row doc-man-view" :style="viewportWidth >= 768 ? 'height: fit-content;' : 'height: 33vh;'">
                <div class="doc-man-view-inner">
                  <DocumentManager :channelItem="props.channelItem"></DocumentManager>
                </div>
              </div>
            </div>
          </div>
        </div>
        <Separator
          ref="separator"
          :viewportWidth="viewportWidth"
          :activeIndex="-1"
          @startResizeBySeparator="startResize($event)"
        >
        </Separator>
        <div
          class="resizable-column right-column"
          :style="
            viewportWidth > 810
              ? {width: rightColumnWidth + 'px', maxWidth: maxContainerWidth - leftColumnWidth + 'px'}
              : {}
          "
          id="right-column"
          ref="rightColumn"
        >
          <!-- Bootstrap Tabs for switching between contextList and contextListtranslation -->
          <ul class="nav nav-tabs" id="myChannelWorkbenchTabs" role="tablist">
            <li class="nav-item" role="presentation">
              <button
                class="nav-link active"
                id="channel-chat-tab"
                data-bs-toggle="tab"
                data-bs-target="#channel-chat"
                type="button"
                role="tab"
                aria-controls="channel-chat"
                aria-selected="true"
              >
                {{ t("ChannelPage.chat") }}
              </button>
            </li>
          </ul>
          <!-- Tab Content -->
          <div class="tab-content mt-3" id="myChannelWorkbenchTabsContent">
            <div class="tab-pane fade show active" id="channel-chat" role="tabpanel" aria-labelledby="channel-chat-tab">
              <ChatComponent
                :uuid="props.channelItem.uuid"
                :language="props.channelItem.language"
                :active="true"
                :channelmode="true"
              />
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
  <BottomRow />
</template>

<script setup lang="ts">
import MenuBanner from "@/components/MenuBanner.vue";
import LoadingBar from "@/components/LoadingBarComponent.vue";
import HeaderRow from "@/components/HeaderRow.vue";
import BottomRow from "@/components/BottomRow.vue";
import LogoAndSearchbarRow from "@/components/LogoAndSearchbarRow.vue";
import VideoCard from "@/components/VideoCard.vue";
import Separator from "@/components/Separator.vue";
import ChatComponent from "@/components/ChatComponent.vue";
import DocumentManager from "@/components/DocumentManager.vue";
import {useMediaStore} from "@/stores/media";
import {useChannelStore} from "@/stores/channels";
import {useAuthStore} from "@/stores/auth";
import {inject, onMounted, ref, watch} from "vue";
import {matomo_clicktracking} from "@/common/matomo_utils";
import {useI18n} from "vue-i18n";
import {LoggerService} from "@/common/loggerService";
import type {ChannelItem} from "@/data/ChannelItem";
import type {MediaItem} from "@/data/MediaItem";
import type {Emitter, EventType} from "mitt";
import {SelectMediaItemEvent} from "@/common/events";

const loggerService = new LoggerService();
const {t, locale} = useI18n({useScope: "global"});

const props = defineProps<{
  channelItem: ChannelItem;
}>();

const mediaStore = useMediaStore();
const channelStore = useChannelStore();
const authStore = useAuthStore();
const documentManEnabled = ref(false);
documentManEnabled.value = ["developer", "admin"].includes(authStore.getRole());

const eventBus: Emitter<Record<EventType, unknown>> = inject("eventBus")!;

const selectedMediaItem = ref<MediaItem | null>(null);

const searchNow = () => {
  loggerService.log("Search channel items for channel");
  loggerService.log(props.channelItem.course_acronym);
  // TODO: parse query parameter to obtain sort by values, currently static:
  mediaStore.searchMedia(
    [props.channelItem.course_acronym],
    ["course_acronym"],
    ["description.course", "description.lecturer", "title"],
  );
  // Do not automatic local search if channels view was used
  mediaStore.setLastGlobalSearchterms([]);
};

const viewportWidth = ref(window.innerWidth);
const viewportHeight = ref(window.innerHeight * 0.75);

const updateViewportWidth = () => {
  viewportWidth.value = window.innerWidth;
};

onMounted(() => {
  window.addEventListener("resize", updateViewportWidth);
  maxContainerWidth = container.value.clientWidth;
  leftColumnWidth.value = maxContainerWidth - maxContainerWidth / aspectRatio; // Initial left column width
  rightColumnWidth.value = maxContainerWidth / aspectRatio; // Calculate initial right column width based on aspect ratio
  searchNow();
  eventBus.on("selectMediaItemEvent", (event: SelectMediaItemEvent) => {
    if (event !== undefined && event.uuid !== undefined) {
      selectedMediaItem.value = mediaStore.getMediaItemByUuid(event.uuid);
    }
  });
});

// Watch the locale to register for language changes and switch summary dep. on locale
watch(locale, async (newText) => {
  searchNow();
});

const container = ref(null);
const separator = ref(null);

const aspectRatio = 3; // Initial aspect ratio 3:1
let maxContainerWidth = 0;
const leftColumnWidth = ref(300); // Initial left column width
const rightColumnWidth = ref(100); // Calculate initial right column width based on aspect ratio
let isResizing = false;
let startX = 0;
let startLeftColumnWidth = 0;
let startRightColumnWidth = 0;

const startResize = (event: MouseEvent) => {
  if ("touches" in event) {
    startX = event.touches[0].pageX;
    matomo_clicktracking("click_start_resize", "channel_page_view_touch");
  } else {
    startX = (event as MouseEvent).pageX;
    matomo_clicktracking("click_start_resize", "channel_page_view_mouse");
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
  matomo_clicktracking("click_stop_resize", "channel_page_view");
  document.removeEventListener("mousemove", resize);
  document.removeEventListener("mouseup", stopResize);
  document.removeEventListener("touchmove", resize);
  document.removeEventListener("touchend", stopResize);
  searchNow();
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
.media-loading {
  position: relative;
}

.channel-elements {
  display: flex;
}

.video-card.row {
  display: flex;
  overflow: hidden;
  /*height: 30%;*/
  padding-top: 0.5em;
}

.search-results {
  overflow-y: hidden;
  display: flex;
}

.doc-man-view {
  overflow: hidden;
  display: flex;
}

.padded-item {
  margin-top: 1em;
}
.channel-media {
  cursor: pointer;
  /*pointer-events: none;*/
  /*border-bottom: 0.2em solid var(--hans-light-blue);*/
}
.channel-media:hover {
  background-color: var(--hans-light-blue);
}

.resizable-container {
  display: flex;
  flex-direction: row;
  min-height: 52vh; /* Set an initial height */
  height: fit-content;
  border: 1px solid #ccc;
  /* Add a border for visual separation */
  max-width: min(98vw, max(100ch, 124vh));
  width: min(98vw, max(100ch, 124vh));
}

.resizable-container-small {
  display: block;
  /*height: 60vh; /* Set an initial height */
  height: min-content;
  border: 1px solid #ccc;
  /* Add a border for visual separation */
  max-width: min(98vw, max(100ch, 124vh));
  width: min(98vw, max(100ch, 124vh));
}

.resizable-column {
  overflow: auto;
  padding: 15px;
  min-width: 365px;
}

.left-column {
  flex: 3;
  /* Initial ratio: 3 */
  overflow: hidden;
}

.right-column {
  flex: 1;
  /* Initial ratio: 1 */
  overflow: hidden;
}

@media (max-aspect-ratio: 3/4) {
  .search-results {
    flex-direction: column;
    justify-content: center;
  }
}

.found-media {
  overflow-y: auto;
  height: inherit;
}

.doc-man-view-inner {
  overflow-y: auto;
  height: inherit;
}

.selected-media {
  background-color: var(--hans-light-blue) !important;
}

.media-item-link {
  color: var(--hans-dark);
  text-decoration: none;
}

.chat-messages-container-outer {
  height: 50vh;
}
</style>
