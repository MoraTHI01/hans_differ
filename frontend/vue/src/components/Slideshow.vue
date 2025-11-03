<template>
  <div v-if="loading || !loaded" class="slide-loading">
    <LoadingBarComponent />
  </div>
  <!-- auto height is enabled since only the active sl</div>ide is resized, touch move is disabled to allow slide text to be selected -->
  <swiper
    :auto-height="true"
    :navigation="true"
    :centered-slides="true"
    :keyboard="{enabled: true}"
    :mousewheel="true"
    :scrollbar="{draggable: true}"
    :modules="[Navigation, Scrollbar, Keyboard, Mousewheel]"
    :allow-touch-move="false"
    @swiper="getSwiper"
    @slide-change="handleSlideChange"
  >
    <swiper-slide class="slide" v-for="(page, index) in pages" :key="index">
      <canvas :ref="setCanvasRef(index)" class="w-100"></canvas>
    </swiper-slide>
  </swiper>
  <div v-if="!loading && loaded" class="slide-number">
    <p>{{ t("Slideshow.slide") }} {{ curr_page }}</p>
  </div>
</template>

<script setup lang="ts">
import LoadingBarComponent from "@/components/LoadingBarComponent.vue";
import type {Emitter, EventType} from "mitt";
import {PauseEvent, PlayEvent, SetPageEvent, SetPositionEvent} from "@/common/events";
import type {MediaItem} from "@/data/MediaItem.js";
import {useI18n} from "vue-i18n";
import {useMediaStore} from "@/stores/media";
import * as pdfjsLib from "pdfjs-dist";
import {inject, ref, onBeforeUnmount, onMounted, watch, reactive, defineExpose, nextTick} from "vue";
import {Swiper, SwiperSlide} from "swiper/vue";
import type {Swiper as SwiperType} from "swiper";
import {Navigation, Scrollbar, Keyboard, Mousewheel} from "swiper/modules";
import {matomo_clicktracking} from "@/common/matomo_utils";
import {LoggerService} from "@/common/loggerService";

import "swiper/css";
import "swiper/css/pagination";
import "swiper/css/navigation";
import "swiper/css/scrollbar";

// Set the workerSrc using a relative path
// Set workerSrc to the path of pdf.worker.min.mjs
pdfjsLib.GlobalWorkerOptions.workerSrc = new URL("pdfjs-dist/build/pdf.worker.min.mjs", import.meta.url).toString();

const loggerService = new LoggerService();
const {t, locale} = useI18n({useScope: "global"});
const store = useMediaStore();
const loading = ref(true);
const isSyncActive = ref(true);

const props = defineProps<{
  pdfUrl: string;
  video: MediaItem;
}>();

const eventBus: Emitter<Record<EventType, unknown>> = inject("eventBus")!;

let slideshow: SwiperType | null = null;
const loaded = ref<boolean>(false);

// Alignment
const timestamps = ref<number[]>([]);
const timestampsSlideNumbers = ref<number[]>([]);

const prev_position = ref<number>(0.0);
const curr_page = ref<number>(1);
const do_set_position = ref(false);
const slide_change_ongoing = ref(false);

/**
 * Callback to retrieve the swiper object from the swiper element for interaction with its internals
 *
 * @param {SwiperType} swiper - The newly initialized swiper instance to be assigned
 */
function getSwiper(swiper: SwiperType) {
  slideshow = swiper;
}

const pages = ref<null[] | string[]>([]);
const canvases = ref<(HTMLCanvasElement | null)[]>([]);
const slideWidths = ref<string[]>([]);

function setCanvasRef(index: number) {
  return (el: HTMLCanvasElement) => {
    canvases.value[index] = el;
  };
}

async function renderPage(pdf: pdfjsLib.PDFDocumentProxy, pageNum: number) {
  const page = await pdf.getPage(pageNum);
  const viewport = page.getViewport({scale: 1.5});
  pages.value[pageNum - 1] = ""; // Store page rendering

  if (canvases.value[pageNum - 1]) {
    const canvas = canvases.value[pageNum - 1]!;
    const context = canvas.getContext("2d");
    if (context) {
      canvas.height = viewport.height;
      canvas.width = viewport.width;

      const renderContext = {
        canvasContext: context,
        viewport: viewport,
      };
      await page.render(renderContext).promise;
    }
  }
}

async function loadPdf() {
  loading.value = true;
  const loadingTask = pdfjsLib.getDocument({
    url: props.pdfUrl,
  });
  const pdf = await loadingTask.promise;
  pages.value = Array(pdf.numPages).fill(null); // Pre-fill with nulls

  for (let i = 1; i <= pdf.numPages; i++) {
    renderPage(pdf, i);
  }
  loading.value = false;
}

// Handle slide change
const handleSlideChange = (swiper: any) => {
  if (loaded.value === true && slide_change_ongoing.value === false) {
    slide_change_ongoing.value = true;
    curr_page.value = swiper.activeIndex + 1;
    nextTick(() => {
      eventBus.emit("setPageEvent", new SetPageEvent(curr_page.value, "slideshow", swiper.activeIndex));
    });
    if (do_set_position.value === true && isSyncActive.value === true) {
      const time_index = timestampsSlideNumbers.value.findIndex((num) => num === curr_page.value);
      nextTick(() => {
        eventBus.emit("setPositionEvent", new SetPositionEvent(timestamps.value[time_index], "slideshow", 0));
      });
      do_set_position.value = false;
    }
    slide_change_ongoing.value = false;
  }
};

const getSlideNumberFromAlignment = (posInSec: number): number => {
  if (loaded.value === true) {
    if (!timestamps.value || !timestampsSlideNumbers.value) {
      loggerService.error("Slideshow:getSlideNumberFromAlignment: Alignment invalid!");
      return 1; // Return default slide if alignment is undefined
    }
    loggerService.log("Slideshow:Alignment");

    let prev_page = 1;
    // slide change happens 3 seconds before:
    const comp_sec = posInSec + 3.0;
    for (let i = 0; i < timestamps.value.length; i++) {
      if (comp_sec >= timestamps.value[i]) {
        //loggerService.log(`Slideshow:CurrTime: ${posInSec}`);
        //loggerService.log(`Slideshow:SlideStartTime: ${timestamps.value[i]}`);
        //loggerService.log(`Slideshow:SlidePage: ${timestampsSlideNumbers.value[i]}`);
        prev_page = timestampsSlideNumbers.value[i];
      }
    }
    loggerService.log(`Slideshow:Alignment:SlideToPage: ${prev_page}`);
    //loggerService.log(`Slideshow:getSlideNumberFromAlignment: Page found: ${prev_page}`);
    return prev_page;
  }
};

const handleInterval = async (positionInSec: number) => {
  //loggerService.log("Slideshow:handleInterval");
  // slides can change every second abs +- 1
  if (
    loaded.value === true &&
    isSyncActive.value === true &&
    loading.value === false &&
    Math.abs(positionInSec - prev_position.value) >= 1.0
  ) {
    prev_position.value = positionInSec;
    //loggerService.log("Slideshow:getPageFromAlignment");
    curr_page.value = getSlideNumberFromAlignment(positionInSec);
    //loggerService.log("Slideshow:setSlide");
    //loggerService.log(`Slideshow:previousSlide: ${slideshow.activeIndex.toString()}`);
    const to_index = curr_page.value - 1;
    loggerService.log(`Slideshow:toSlide: ${to_index.toString()}`);
    eventBus.emit("setPageEvent", new SetPageEvent(curr_page.value, "slideshow", to_index));
    //loggerService.log("Slideshow:setSlideFinished");
  }
};

const handleClickPrev = () => {
  if (loaded.value === true) {
    matomo_clicktracking("click_button", "Previous slide");
    do_set_position.value = true;
  }
};

const handleClickNext = () => {
  if (loaded.value === true) {
    matomo_clicktracking("click_button", "Next slide");
    do_set_position.value = true;
  }
};

onMounted(async () => {
  await loadPdf();

  eventBus.on("setPositionEvent", (event: SetPositionEvent) => {
    if (event !== undefined && event.position !== undefined) {
      handleInterval(event.position);
    }
  });

  eventBus.on("setPageEvent", (event: SetPageEvent) => {
    if (event !== undefined && event.page !== undefined && event.index !== undefined) {
      nextTick(() => {
        slideshow.slideTo(event.index, 150, true);
      });
    }
  });

  eventBus.on("videoPlaying", (position: number) => {
    if (position !== undefined) {
      handleInterval(position);
    }
  });

  await store.loadSlidesImagesMeta(props.video.uuid, true);

  // Convert object to an array of entries and sort by timestamp
  const sortedEntries = Object.entries(store.getAlignment)
    .map(([key, value]) => [parseFloat(key), value]) // Convert the timestamp string to a float
    .sort((a, b) => a[0] - b[0]); // Sort by timestamp (first element of the pair)

  // Separate the sorted entries into two arrays: timestamps and slide numbers
  timestamps.value = sortedEntries.map((entry) => entry[0] as number);
  timestampsSlideNumbers.value = sortedEntries.map((entry) => entry[1] as number);

  loggerService.log(`Slideshow:Timestamps: ${timestamps.value}`);
  loggerService.log(`Slideshow:TimestampsSlideNumbers: ${timestampsSlideNumbers.value}`);

  loading.value = false;
  const prevButton = document.querySelector(".swiper-button-prev");
  prevButton.addEventListener("click", handleClickPrev);
  const nextButton = document.querySelector(".swiper-button-next");
  nextButton.addEventListener("click", handleClickNext);
  loaded.value = true;
});

const setSyncActive = (value: boolean) => {
  if (loaded.value === true) {
    loggerService.log("Slideshow:setSyncActive");
    isSyncActive.value = value;
  }
};

const doRerender = () => {
  if (loaded.value === true) {
    loggerService.log("Slideshow:doRerender");
  }
};

// Clean up the event listener before the component is unmounted
onBeforeUnmount(() => {
  const prevButton = document.querySelector(".swiper-button-prev");
  if (prevButton) {
    prevButton.removeEventListener("click", handleClickPrev);
  }
  const nextButton = document.querySelector(".swiper-button-next");
  if (nextButton) {
    nextButton.removeEventListener("click", handleClickNext);
  }
});

defineExpose({setSyncActive, doRerender});
</script>

<style scoped>
.swiper-slide {
  /*
   * Ensures the scrollbar doesn't overlap the slide so text on the bottom of
   * each slide is easily selectable (2 x 3px scrollbar padding + 5 px scrollbar)
   */
  padding-bottom: 11px;
}

.swiper > :deep(.swiper-button-disabled) {
  display: none;
}

.swiper.auto-hide > :deep(.swiper-button-next),
.swiper.auto-hide > :deep(.swiper-button-prev),
.swiper.auto-hide > :deep(.swiper-scrollbar) {
  opacity: 0;
  transition: opacity 0.25s ease-in;
}

.swiper.auto-hide:hover > :deep(.swiper-button-next),
.swiper.auto-hide:hover > :deep(.swiper-button-prev),
.swiper.auto-hide:hover > :deep(.swiper-scrollbar) {
  opacity: 1;
}

.slide {
  position: relative;
}

.slide-number {
  text-align: center;
}

.slide-loading {
  text-align: center;
}

.slide-loading > .loading-bar {
  position: relative;
}
</style>
