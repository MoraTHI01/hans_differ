<template>
  <!-- video description -->
  <div class="card-body p-1">
    <!-- description -->
    <h6 class="my-2 video-description-overflow">{{ video.title.split("_").join(" ") }}</h6>
    <div v-if="route === 'SearchResults'">
      <div class="my-2">
        <router-link
          class="link"
          @click="matomo_clicktracking('click_videocard_search_course_acronym', video.description.course_acronym)"
          :to="{
            name: 'SearchResults',
            query: {q: [video.description?.course_acronym], f: ['course_acronym']},
          }"
        >
          {{ video.description?.course }}
        </router-link>
      </div>
      <div class="my-2">
        <router-link
          class="link"
          @click="matomo_clicktracking('click_videocard_search_semester', video.description.semester)"
          :to="{
            name: 'SearchResults',
            query: {q: [video.description?.semester], f: ['semester']},
          }"
        >
          {{ video.description?.semester }}
        </router-link>
      </div>
    </div>
    <div v-else class="my-2">
      <router-link
        class="link"
        @click="matomo_clicktracking('click_videocard_search_course_acronym', video.description.course_acronym)"
        :to="{
          name: 'SearchResults',
          query: {q: [video.description?.course_acronym], f: ['course_acronym']},
        }"
      >
        {{ video.description?.course }}
      </router-link>
      -
      <router-link
        class="link"
        @click="matomo_clicktracking('click_videocard_search_semester', video.description.semester)"
        :to="{
          name: 'SearchResults',
          query: {q: [video.description?.semester], f: ['semester']},
        }"
      >
        {{ video.description?.semester }}
      </router-link>
    </div>
    <!-- video details -->
    <router-link
      class="my-2 lecturer"
      @click="matomo_clicktracking('click_videocard_search_lecturer', video.description.lecturer)"
      :to="{
        name: 'SearchResults',
        query: {q: [video.description?.lecturer], f: ['lecturer']},
      }"
    >
      <!-- avatar -->
      <img :src="video.thumbnails?.lecturer" alt="avatar" class="avatar rounded-circle" />
      <span class="link name">{{ video.description?.lecturer }}</span>
    </router-link>
    <!-- video details end -->
    <!-- license -->
    <div
      v-if="(route === 'VideoPlayer' || route === 'SearchResults') && showLicense === true"
      class="my-2 license-content"
    >
      <div v-for="(license, index) in video.licenses" :key="index">
        <!-- license show only demo licenses with CC-BY-SA -->
        <div v-if="license.value === true && license.type === 'CC-BY-SA-4.0'">
          <a class="license-link link" :href="license.url" target="_blank">
            <img src="/creativecommons-icons/by-sa.svg" alt="api-btn" class="img-fluid img-btn" />
            <span class="link name">{{ license.name }}</span>
          </a>
        </div>
        <div v-else-if="license.value === true && license.type === 'CC-BY-4.0'">
          <a class="license-link link" :href="license.url" target="_blank">
            <img src="/creativecommons-icons/by.svg" alt="api-btn" class="img-fluid img-btn" />
            <span class="link name">{{ license.name }}</span>
          </a>
        </div>
        <!--
        <div v-else-if="license.value === true && license.type === 'CC0-1.0'">
          <a class="license-link link" :href="license.url" target="_blank">
            <img src="/creativecommons-icons/cc-zero.svg" alt="api-btn" class="img-fluid img-btn"/>
            <span class="link name">{{ license.name }}</span>
          </a>
        </div>
        -->
      </div>
    </div>
  </div>
  <!-- video description end -->
</template>

<script setup lang="ts">
import {useRoute} from "vue-router";
import {ref} from "vue";
import type {MediaItem} from "@/data/MediaItem.js";
import {matomo_clicktracking} from "@/common/matomo_utils";

const route = ref(useRoute().name);
const props = defineProps<{
  video: MediaItem;
}>();

const showLicense = ref(false);
if (props.video && props.video.licenses) {
  props.video.licenses.forEach((license) => {
    if (license.value === true && (license.type === "CC-BY-SA-4.0" || license.type === "CC-BY-4.0")) {
      showLicense.value = true;
    }
  });
}
</script>

<style scoped>
.avatar {
  width: 50px;
  height: auto;
  float: left;
  transition: all 0.2s ease-in-out;
}

.name {
  display: inline;
  margin-left: 5px;
}

.link {
  color: var(--hans-dark);
  text-decoration: none;
  transition: all 0.2s ease-in-out;
  pointer-events: auto;
}

.link:hover {
  opacity: 0.5;
}

.lecturer {
  display: flex;
  align-items: center;
  text-decoration: none;
  height: 3em;
}

.avatar:hover {
  opacity: 0.5;
}

.video-description-overflow {
  text-overflow: ellipsis;
  overflow: hidden;
}

.license-content {
  position: relative;
  height: 1.5em;
  top: 0.5em;
}

.license-link {
  position: relative;
  height: 1.5em;
  display: inline-flex;
}
</style>
