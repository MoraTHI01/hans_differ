<template>
  <div class="container my-1 mx-0 marker-container" ref="markerSequenceContainer">
    <!-- Left arrow indicator -->
    <div
      v-show="showLeftArrow"
      class="arrow-indicator left"
      @mousedown="scrollMarkerSeqLeft"
      @touchstart="scrollMarkerSeqLeft"
    >
      <img class="img-fluid left-arrow-image" src="/bootstrap-icons/arrow-left-circle.svg" alt="left arrow" />
    </div>
    <div ref="markerSequence" class="marker-sequence my-1 mx-0">
      <Marker
        v-if="finished_loading"
        v-for="item in store.getMarker"
        :marker="item"
        :thumbnails="props.video.thumbnails"
      />
    </div>
    <!-- Right arrow indicator -->
    <div
      v-show="showRightArrow"
      class="arrow-indicator right"
      @mousedown="scrollMarkerSeqRight"
      @touchstart="scrollMarkerSeqRight"
    >
      <img class="img-fluid right-arrow-image" src="/bootstrap-icons/arrow-right-circle.svg" alt="left arrow" />
    </div>
  </div>
</template>

<script setup lang="ts">
import {ref, watch, onMounted, onUnmounted} from "vue";
import Marker from "./Marker.vue";
import {useMediaStore} from "@/stores/media";
import {useI18n} from "vue-i18n";
const {t, locale} = useI18n({useScope: "global"});
import {LoggerService} from "@/common/loggerService";

const loggerService = new LoggerService();
const props = defineProps<{
  video: MediaItem;
}>();

const store = useMediaStore();
const finished_loading = ref(true);
const markerSequence = ref(null);
const markerSequenceContainer = ref(null);

// Watch the locale to register for language changes and switch markers dep. on locale
watch(locale, async (newText) => {
  finished_loading.value = false;
  await store.loadMarkersFromTopics(props.video.uuid, locale.value);
  finished_loading.value = true;
});

// Refs for tracking arrow visibility
const showLeftArrow = ref(false);
const showRightArrow = ref(false);

const adjustScrollPosition = () => {
  if (markerSequence.value) {
    const containerScrollLeft = markerSequence.value.scrollLeft;
    const containerScrollWidth = markerSequence.value.scrollWidth;
    const containerClientWidth = markerSequence.value.clientWidth;
    showLeftArrow.value = containerScrollLeft > 0;
    showRightArrow.value =
      containerScrollLeft < containerScrollWidth - containerClientWidth &&
      markerSequence.value.children.length * 68 > containerClientWidth;
  }
};

const resizeObserver = new ResizeObserver(adjustScrollPosition);

const handleWheel = (event) => {
  if (event.deltaY !== 0) {
    if (markerSequence.value) {
      // Adjust the scroll position based on the deltaY value
      markerSequence.value.scrollLeft += event.deltaY;
      adjustScrollPosition();
    }
  }
};

let touchStartX = 0;

const handleTouchMove = (event) => {
  if (markerSequence.value) {
    const touch = event.touches[0];
    const deltaX = touch.clientX - touchStartX;

    // Adjust the scroll position based on the deltaX value
    markerSequence.value.scrollLeft -= deltaX;
    adjustScrollPosition();
    touchStartX = touch.clientX;
  }
};

const scrollOffset = ref(32);

const scrollMarkerSeqLeft = () => {
  if (markerSequence.value) {
    let containerScrollWidth = markerSequence.value.scrollWidth;
    let containerClientWidth = markerSequence.value.clientWidth;
    // Adjust the scroll position based on the deltaY value
    if (markerSequence.value.scrollLeft - scrollOffset.value >= 0) {
      markerSequence.value.scrollLeft -= scrollOffset.value;
    } else {
      markerSequence.value.scrollLeft = 0;
    }
    containerScrollWidth = markerSequence.value.scrollWidth;
    containerClientWidth = markerSequence.value.clientWidth;
    const containerScrollLeft = markerSequence.value.scrollLeft;
    showLeftArrow.value = containerScrollLeft > 0;
    showRightArrow.value = containerScrollLeft < containerScrollWidth - containerClientWidth;
  }
};

const scrollMarkerSeqRight = () => {
  if (markerSequence.value) {
    let containerScrollWidth = markerSequence.value.scrollWidth;
    let containerClientWidth = markerSequence.value.clientWidth;
    // Adjust the scroll position based on the deltaY value
    if (markerSequence.value.scrollLeft + scrollOffset.value <= containerScrollWidth - containerClientWidth) {
      markerSequence.value.scrollLeft += scrollOffset.value;
    }
    containerScrollWidth = markerSequence.value.scrollWidth;
    containerClientWidth = markerSequence.value.clientWidth;
    const containerScrollLeft = markerSequence.value.scrollLeft;
    showLeftArrow.value = containerScrollLeft > 0;
    showRightArrow.value = containerScrollLeft < containerScrollWidth - containerClientWidth;
  }
};

onMounted(() => {
  if (markerSequenceContainer.value) {
    resizeObserver.observe(markerSequenceContainer.value);
  }
  if (markerSequence.value) {
    loggerService.log("scrollOffset: " + scrollOffset.value);
    markerSequence.value.addEventListener("wheel", handleWheel);
    markerSequence.value.addEventListener("touchstart", (event) => {
      touchStartX = event.touches[0].clientX;
    });
    markerSequence.value.addEventListener("touchmove", handleTouchMove);
    adjustScrollPosition();
  }
});

onUnmounted(() => {
  resizeObserver.disconnect();
});
</script>

<style scoped>
.marker-container {
  height: 80px;
  align-content: center;
  display: flex;
}
.marker-sequence {
  height: 80px;
  overflow-x: hidden;
  overflow-y: clip;
  white-space: nowrap;
  z-index: 1;
  position: relative;
  align-content: center;
  display: flex;
}
.arrow-indicator {
  position: relative;
  top: 50%;
  transform: translateY(-50%);
  z-index: 2;
  cursor: pointer;
  width: 32px;
  height: 64px;
  margin-top: 12px;
}
.arrow-indicator.left {
  left: 0;
}
.arrow-indicator.right {
  right: 0;
}
.left-arrow-image {
  height: 64px;
  width: 32px;
  margin-right: 2em;
}
.right-arrow-image {
  height: 64px;
  width: 32px;
  margin-right: 2em;
}
</style>
