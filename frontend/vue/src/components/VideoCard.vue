<template>
  <div :class="viewportWidth >= 768 ? 'video-card' : 'video-card-mobile'">
    <div :class="'card border-0 mb-3 video-thumb-container ' + videoClasses">
      <!-- video thumbnail if we are in SearchResultsView-->
      <router-link
        class="video-thumb"
        :to="{name: 'VideoPlayer', query: {uuid: props.video.uuid}}"
        @click="matomo_clicktracking('click_videocard', props.video.title)"
      >
        <img class="img-fluid card-image-top grow" :src="video.thumbnails?.media" alt="thumbnail" height="221px" />
        <div v-if="props.show_position === true">
          <p class="video-position">{{ position_str }}</p>
          <VideoProgressBar class="video-progress" :currentTime="position" :duration="duration"></VideoProgressBar>
        </div>
      </router-link>
      <!-- video thumbnail end -->
    </div>
    <div class="col video-description">
      <!-- video description if we are in SearchResultsView-->
      <VideoDescription :video="props.video" />
      <!-- video description end -->
    </div>
    <div :class="viewportWidth > 810 ? ['col-4', 'video-info'] : ['row', 'video-info-mobile']">
      <!-- short summary if we are in SearchResultsView-->
      <VideoShortSummary :video="props.video" />
      <!-- short summary end -->
      <!-- search highlights if we are in SearchResultsView-->
      <VideoSummarySearchHighlights :video="props.video" />
      <!-- search highlights end -->
    </div>
  </div>
</template>

<script setup lang="ts">
import {ref} from "vue";
import VideoDescription from "@/components/VideoDescription.vue";
import VideoShortSummary from "@/components/VideoShortSummary.vue";
import VideoSummarySearchHighlights from "@/components/VideoSummarySearchHighlights.vue";
import VideoProgressBar from "@/components/VideoProgressBar.vue";
import type {MediaItem} from "@/data/MediaItem";
import {matomo_clicktracking} from "@/common/matomo_utils";
import {useHistoryStore} from "@/stores/history";

const historyStore = useHistoryStore();

// The video media item and optional CSS classes for styling the video element
const props = withDefaults(
  defineProps<{
    video: MediaItem;
    videoClasses?: string;
    show_position?: boolean;
  }>(),
  {
    videoClasses: "",
    show_position: false,
  },
);
const viewportWidth = ref(window.innerWidth);

const position_str = ref("");
const position = ref(0);
const duration = ref(0);

const formatPosition = (seconds: number) => {
  const hrs = Math.floor(seconds / 3600); // Get the number of hours
  const mins = Math.floor((seconds % 3600) / 60); // Get the number of minutes
  const secs = Math.floor(seconds % 60); // Get the remaining seconds

  // Pad with zeros if necessary to ensure two digits for hours, minutes, and seconds
  const formattedHrs = String(hrs).padStart(2, "0");
  const formattedMins = String(mins).padStart(2, "0");
  const formattedSecs = String(secs).padStart(2, "0");

  return `${formattedHrs}:${formattedMins}:${formattedSecs}`;
};

if (props.show_position === true) {
  const itemHistory = historyStore.getHistoryForMediaItem(props.video.uuid);
  position.value = itemHistory.position;
  position_str.value = formatPosition(position.value);
  duration.value = itemHistory.duration;
}
</script>

<style scoped>
.video-progress {
  position: absolute;
  width: 100%;
  bottom: -5px;
}

.video-position {
  position: absolute;
  color: #fff;
  border-radius: 15px;
  padding-left: 5px;
  padding-right: 5px;
  right: 0.5em;
  bottom: -5px;
  height: 1.5em;
  background-color: rgba(0, 0, 0, 0.6);
}

.video-thumb-container {
  background-color: transparent;
}

.video-thumb {
  text-decoration: none !important;
  pointer-events: auto;
}

.avatar {
  width: 50px;
  height: auto;
  float: left;
}

.name {
  display: inline;
  margin-left: 5px;
}

.grow {
  transition: all 0.2s ease-in-out;
}

.grow:hover {
  transform: scale(1.1);
}

@media (max-aspect-ratio: 3/4) {
  .video-card {
    display: flex;
    justify-content: center;
    flex-wrap: wrap;
    width: auto;
  }

  .video-card-mobile {
    display: flex;
    justify-content: center;
    flex-wrap: wrap;
    width: auto;
    margin-top: -2em;
  }

  .card,
  .video-description {
    width: 90%;
  }

  .video-description {
    flex: 0 0 auto;
  }

  .card,
  .video-info-mobile {
    width: 90%;
    overflow-y: auto;
    position: relative;
    margin-top: 2em;
    margin-bottom: 2em;
  }

  .video-info {
    flex: 0 0 auto;
  }

  .video-info-mobile {
    flex: 0 0 auto;
  }
}
</style>
