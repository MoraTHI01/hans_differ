<template>
  <div class="row g-0 bg-light position-relative topic-detail-container border-bottom">
    <div class="col-md-6 mb-md-0 p-md-4 position-relative grow">
      <img
        class="img-fluid w-100 max-image-size"
        ref="topicImage"
        src="/bootstrap-icons/box-arrow-up.svg"
        alt="topicImage"
      />
    </div>
    <div class="col-md-6 p-4 ps-md-0">
      <h5 class="mt-0 topic-detail-heading">{{ props.marker.title }}</h5>
      <p>{{ props.marker.summary }}</p>
      <a
        @click="clickLink(props.marker.title, {position: props.marker.interval[0], index: 0})"
        class="stretched-link time"
        >{{ props.marker.time }}</a
      >
    </div>
  </div>
</template>

<script setup>
import {ref, inject, onMounted} from "vue";
import {matomo_clicktracking} from "@/common/matomo_utils";
import {LoggerService} from "@/common/loggerService";
import {apiClient} from "@/common/apiClient";

const loggerService = new LoggerService();
const props = defineProps(["marker", "thumbnails"]);
const eventBus = inject("eventBus"); // Inject `eventBus`
const topicImage = ref(null);

onMounted(async () => {
  if (props.marker !== undefined) {
    if (topicImage.value !== null) {
      const timestamp = formatSecondsToHHMMSS(props.marker.interval[0]);
      loggerService.log("Topic timestamp: " + timestamp);
      const prefix = props.thumbnails.media
        .split("/")
        .reverse()[0]
        .split("?")[0]
        .replace(".thumb.png", "")
        .replace(/%20/g, " ");
      loggerService.log("Topic thumbnail prefix: " + prefix);
      // w320-h180, w228-h128, w160-h90, w114-h64 could be changed to dynamic depending on stretching/viewort?
      const uri = encodeURIComponent(props.thumbnails.timeline + "/" + prefix + "-tn-w320-h180-" + timestamp + ".png");
      const {data} = await apiClient.get("/getThumbnail?urn=" + uri);
      if ("data" in data && Object.keys(data.data).length > 0) {
        topicImage.value.src = data.data;
      } else {
        loggerService.error("Error fetching thumbnail image!");
      }
      if (props.marker.type === "Questionnaire") {
        for (let entry of props.marker.value) {
          topicImage.value.title = "Question: " + entry.question + " Answer: " + entry.answer + "\n";
        }
      } else {
        topicImage.value.title = props.marker.value;
      }
    }
  }
});

function sendPosition(position) {
  eventBus.emit("setPositionEvent", position);
}

function clickLink(title, position) {
  matomo_clicktracking("click_topic_position_using_link", title);
  sendPosition(position);
}

function formatSecondsToHHMMSS(totalSeconds) {
  const roundedSeconds = Math.round(totalSeconds / 10) * 10;
  const hours = Math.floor(roundedSeconds / 3600);
  const minutes = Math.floor((roundedSeconds % 3600) / 60);
  const seconds = Math.floor(roundedSeconds % 60);

  const formattedHours = hours < 10 ? `0${hours}` : `${hours}`;
  const formattedMinutes = minutes < 10 ? `0${minutes}` : `${minutes}`;
  const formattedSeconds = seconds < 10 ? `0${seconds}` : `${seconds}`;

  return `${formattedHours}#${formattedMinutes}#${formattedSeconds}`;
}
</script>

<style scoped>
.topic-detail-heading-text {
  cursor: default;
}
.topic-detail-heading {
  padding: 0px;
}
.topic-detail-summary {
  padding-left: 2em;
}
.topic-detail-container {
  padding: 0px;
  cursor: pointer;
}
.time {
  color: var(--hans-dark-blue);
}
.time:hover {
  color: var(--hans-medium-blue);
}
.max-image-size {
  max-width: 320px;
  max-height: 180px;
}
.grow {
  transition: all 0.2s ease-in-out;
  position: relative; /* Ensure proper positioning */
  z-index: 1; /* Set a higher z-index to ensure the image stays on top */
}

.grow:hover {
  transform: scale(1.2);
  z-index: 2; /* Increase the z-index on hover to bring the image to the foreground */
}
</style>
