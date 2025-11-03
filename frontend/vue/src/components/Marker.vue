<template>
  <div class="slide border" @click="clickImage(props.marker.value, {position: props.marker.interval[0], index: 0})">
    <div class="marker-container grow">
      <img
        class="img-fluid background-image"
        ref="timelineImage"
        src="/bootstrap-icons/box-arrow-up.svg"
        alt="timelineImage"
        @mouseenter="handleMouseEnterTimelineImage"
        @mouseleave="handleMouseLeaveTimelineImage"
      />
      <img class="img-fluid overlay-image" ref="markerImage" src="/bootstrap-icons/box-arrow-up.svg" alt="marker" />
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

const markerImage = ref(null);
const timelineImage = ref(null);
const eventBus = inject("eventBus"); // Inject `eventBus`

const timestamp = formatSecondsToHHMMSS(props.marker.interval[0]);
loggerService.log("Marker timestamp: " + timestamp);
const prefix = props.thumbnails.media
  .split("/")
  .reverse()[0]
  .split("?")[0]
  .replace(".thumb.png", "")
  .replace(/%20/g, " ");
loggerService.log("Marker prefix: " + prefix);

// Handle mouse enter event
const handleMouseEnterTimelineImage = () => {
  // w320-h180, w228-h128, w160-h90, w114-h64 could be changed to dynamic depending on stretching/viewort?
  //timelineImage.value.src = props.thumbnails.timeline[prefix + "-tn-w228-h128-" + timestamp + ".png"];
};

// Handle mouse leave event
const handleMouseLeaveTimelineImage = () => {
  //timelineImage.value.src = props.thumbnails.timeline[prefix + "-tn-w114-h64-" + timestamp + ".png"];
};

onMounted(async () => {
  if (props.marker !== undefined) {
    if (timelineImage.value !== null) {
      // w320-h180, w228-h128, w160-h90, w114-h64 could be changed to dynamic depending on stretching/viewort?
      const uri = encodeURIComponent(props.thumbnails.timeline + "/" + prefix + "-tn-w228-h128-" + timestamp + ".png");
      const {data} = await apiClient.get("/getThumbnail?urn=" + uri);
      if ("data" in data && Object.keys(data.data).length > 0) {
        timelineImage.value.src = data.data;
      } else {
        loggerService.error("Error fetching thumbnail image!");
      }
      if (props.marker.type === "Questionnaire") {
        for (let entry of props.marker.value) {
          timelineImage.value.title = "Question: " + entry.question + " Answer: " + entry.answer + "\n";
        }
      } else {
        timelineImage.value.title = props.marker.value;
      }
    }
    if (markerImage.value !== null) {
      markerImage.value.src = "/marker_" + props.marker.type + ".svg";
      markerImage.value.alt = props.marker.type;
    }
  }
});

function sendPosition(position) {
  eventBus.emit("setPositionEvent", position);
}

function clickImage(value, position) {
  matomo_clicktracking("click_topic_position_using_image", value);
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
.slide {
  min-width: 64px;
  min-height: 64px;
  width: 64px;
  height: 64px;
  max-width: 128px;
  max-height: 64px;
  /* Center vertically and horizontally */
  display: inline-flex;
  justify-content: center;
  align-items: center;
  margin-right: 4px;
  margin-top: 16px;
  margin-bottom: 16px;
  position: relative;
  background-color: rgba(0, 0, 0, 0.8);
}

.slide:hover {
  width: 128px;
  cursor: pointer;
}

.grow {
  transition: all 0.2s ease-in-out;
  position: relative; /* Ensure proper positioning */
  z-index: 1; /* Set a higher z-index to ensure the image stays on top */
}

.grow:hover {
  transform: scale(2);
  z-index: 999; /* Increase the z-index on hover to bring the image to the foreground */
}

.marker-container {
  position: relative;
}

.background-image {
  width: 100%;
  height: auto;
  display: block;
}

.overlay-image {
  position: absolute;
  top: -0.95em;
  left: 0;
  /* You can adjust the position of the overlay image as needed */
  width: 25%; /* Adjust the width of the overlay image */
  height: auto; /* Maintain aspect ratio */
  z-index: 1; /* Ensure the overlay image appears above the background */
  filter: invert(calc(1 - var(--button-dark-mode, 0)));
}
</style>
