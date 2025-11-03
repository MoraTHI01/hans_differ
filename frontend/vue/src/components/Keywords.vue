<template>
  <div class="card-body p-1">
    <div v-if="active" class="keywords-chart-container" ref="chartContainerRef">
      <!-- Show message if no data is available -->
      <div v-if="isEmpty" class="no-data">{{ t("Keywords.unavailable") }}</div>
      <svg v-else ref="chartRef"></svg>
    </div>
  </div>
</template>

<script setup lang="ts">
import {onMounted, ref, watch, computed, nextTick} from "vue";
import type {MediaItem} from "@/data/MediaItem.js";
import {useMediaStore} from "@/stores/media";
import type {Keywords} from "@/data/Keywords";
import {matomo_clicktracking} from "@/common/matomo_utils";
import {useI18n} from "vue-i18n";
import {LoggerService} from "@/common/loggerService";
import * as d3 from "d3";
import cloud from "d3-cloud";

const loggerService = new LoggerService();
const {t, locale} = useI18n({useScope: "global"});
const store = useMediaStore();

const props = defineProps<{
  video: MediaItem;
  active: boolean;
}>();

// Emit search keyword event
const emit = defineEmits(["searchterm-from-keywords"]); // Define the emit event

const keywords: Keywords = ref({});

// Reference to the SVG element
const chartRef = ref(null);
// Surrounding container
const chartContainerRef = ref(null);

// Computed property to check if the keywords object is empty
const isEmpty = computed(() => Object.keys(keywords.value).length === 0);

// Method to start a search based on the clicked keyword
const searchKeyword = (keyword: string) => {
  loggerService.log(`Keywords: Searching for the keyword: ${keyword}`);
  matomo_clicktracking("click_button", `Keyword in word cloud clicked.`);
  emit("searchterm-from-keywords", keyword.split(" "));
};

// Function to draw the chart using D3.js
const drawChart = () => {
  // If no chartRef or empty data, or component is not active, do nothing
  if (!chartRef.value || isEmpty.value || !props.active) return;

  // Get the container's size dynamically
  const containerRect = chartContainerRef.value.getBoundingClientRect();
  const width = containerRect.width - 50;
  const height = containerRect.height - 50;

  // Remove any existing elements in the chart (for re-rendering)
  d3.select(chartRef.value).selectAll("*").remove();

  const keywordsArray = Object.entries(keywords.value).map(([text, value]) => ({text, value}));

  // Create the word cloud layout with rectangular spiral, sqrt scale, and orientations
  cloud()
    .size([width, height]) // Set the word cloud size based on the container
    .words(keywordsArray.map((d) => ({text: d.text, size: Math.sqrt(d.value) * 10}))) // Use sqrt scale for word size
    .padding(5)
    .rotate(() => [0]) // Restrict rotation to -90, 0, or 90 degrees
    .font("Arial") // Use Arial font
    .fontSize((d) => d.size) // Use sqrt(n) scaling for word size
    .spiral("rectangular") // Use rectangular spiral layout
    .on("end", drawWords)
    .start();

  // Function to draw the words
  function drawWords(words: Array<{text: string; size: number; x: number; y: number; rotate: number}>) {
    const svg = d3
      .select(chartRef.value)
      .attr("width", width)
      .attr("height", height)
      .append("g")
      .attr("transform", `translate(${width / 2},${height / 2})`); // Center the word cloud

    const textElements = svg
      .selectAll("text")
      .data(words)
      .join("text")
      .style("font-size", (d) => `${d.size}px`)
      .style("font-family", "Arial")
      .attr("fill", () =>
        d3
          .scaleLinear<string>()
          .domain([0, d3.max(Object.values(keywords.value)) ?? 0])
          .range(["#c8deff", "#5f9ceb", "#2950db"])(Math.random()),
      )
      .attr("text-anchor", "middle")
      .attr("transform", (d) => `translate(${d.x},${d.y})rotate(${d.rotate})`)
      .text((d) => d.text)
      .style("cursor", "pointer") // Makes the text appear clickable
      .style("transition", "fill 0.4s ease, font-size 0.4s ease") // Smooth transition effect
      .on("click", (event, d) => {
        searchKeyword(d.text); // Emit the clicked keyword to the parent
      })
      .on("mouseover", function (event, d) {
        d3.select(this)
          .style("fill", "#2950db") // Change color on hover
          .style("font-size", `${d.size * 1.2}px`); // Slightly enlarge the text on hover
      })
      .on("mouseout", function (event, d) {
        d3.select(this)
          .style("fill", () =>
            d3
              .scaleLinear<string>()
              .domain([0, d3.max(Object.values(keywords.value)) ?? 0])
              .range(["#5f9ceb", "#2950db"])(Math.random()),
          ) // Reset color
          .style("font-size", `${d.size}px`); // Reset font size
      });
    // Ensure CSS class is applied after rendering
    textElements.attr("class", "clickable-word"); // Add class for styling
  }
};

// Watch for component mount or keyword/active changes
onMounted(async () => {
  loggerService.log("Keywords:onMounted");
  await updateKeywords();
  if (props.active) drawChart();
});

// Watch the locale to register for language changes and switch summary dep. on locale
watch(locale, async (newText) => {
  await updateKeywords();
  if (props.active) drawChart();
});

// Watch specifically for the active prop change to show or hide the chart
watch(
  () => props.active,
  (newValue) => {
    loggerService.log("Keywords:activeChanged");
    if (newValue) {
      loggerService.log("Keywords:activeChanged:nextTickDrawChart");
      nextTick(() => {
        drawChart();
      });
    } else {
      loggerService.log("Keywords:activeChanged:ClearChart");
      // If inactive, clear the chart content
      d3.select(chartRef.value).selectAll("*").remove();
    }
  },
);

const updateKeywords = async (): Promise<T> => {
  await store.loadKeywords(props.video?.uuid, true);
  keywords.value = store.getKeywords;
  loggerService.log("Keywords:assigned");
  loggerService.log(keywords.value);
  return;
};
</script>

<style scoped>
.keywords-chart-container {
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 20px;
  width: 100%; /* Allow the container to grow/shrink based on the parent */
  height: 36vh; /* Set a fixed height for the example, or make it dynamic as well */
}

svg {
  font-family: sans-serif;
  font-size: 10px;
}

/* Style for the no data message */
.no-data {
  font-size: 16px;
  color: #888;
}
</style>
