<template>
  <div v-if="loading || !loaded" class="document-loading">
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
    <swiper-slide class="document" v-for="(page, index) in pages" :key="index">
      <canvas :ref="setCanvasRef(index)" class="w-100"></canvas>
    </swiper-slide>
  </swiper>
</template>

<script setup lang="ts">
import LoadingBarComponent from "@/components/LoadingBarComponent.vue";
import type {Emitter, EventType} from "mitt";
import {useI18n} from "vue-i18n";
import * as pdfjsLib from "pdfjs-dist";
import {inject, ref, onBeforeUnmount, onMounted, watch, reactive, defineEmits, nextTick} from "vue";
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
const loading = ref(true);
const isSyncActive = ref(true);

const props = defineProps<{
  pdfUrl: string;
}>();

let slideshow: SwiperType | null = null;
const loaded = ref<boolean>(false);

const emit = defineEmits(["pageChanged"]);

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
  loaded.value = false;
  loading.value = true;
  const loadingTask = pdfjsLib.getDocument({
    url: props.pdfUrl,
  });
  const pdf = await loadingTask.promise;
  pages.value = Array(pdf.numPages).fill(null); // Pre-fill with nulls

  for (let i = 1; i <= pdf.numPages; i++) {
    renderPage(pdf, i);
  }
  curr_page.value = 1;
  emit("pageChanged", curr_page.value);
  loading.value = false;
  loaded.value = true;
}

// Handle slide change
const handleSlideChange = (swiper: any) => {
  if (loaded.value === true && slide_change_ongoing.value === false) {
    slide_change_ongoing.value = true;
    curr_page.value = swiper.activeIndex + 1;
    emit("pageChanged", curr_page.value);
    slide_change_ongoing.value = false;
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
  const prevButton = document.querySelector(".swiper-button-prev");
  prevButton.addEventListener("click", handleClickPrev);
  const nextButton = document.querySelector(".swiper-button-next");
  nextButton.addEventListener("click", handleClickNext);
  await loadPdf();
});

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
//watch(async() => props.dataUrl, loadPdf());
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

.document {
  position: relative;
}

.document-loading {
  text-align: center;
}

.document-loading > .loading-bar {
  position: relative;
}
</style>
