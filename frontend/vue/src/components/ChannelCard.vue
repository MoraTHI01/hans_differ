<template>
  <!-- channel card -->
  <div class="channel-card col-3">
    <div class="card border-0 mb-3">
      <!-- channel thumbnail -->
      <router-link
        :to="{name: 'SearchResults', query: {q: channel.tags, f: ['tags']}}"
        @click="matomo_clicktracking('click_channelcard', channel.tags?.toString())"
        style="text-decoration: none"
      >
        <div class="channel-container">
          <span class="course-acronym">{{ channel.course_acronym }}</span>
        </div>
      </router-link>
      <!-- channel thumbnail end -->
      <!-- channel description -->
      <div class="card-body p-1">
        <!-- description -->
        <h6 class="my-2">
          <router-link
            class="link"
            :to="{name: 'SearchResults', query: {q: [channel.faculty_acronym], f: ['orgaunit_acronym']}}"
            @click="matomo_clicktracking('click_channelcard_search_faculty_acronym', channel.faculty_acronym)"
          >
            {{ channel.faculty }}
          </router-link>
          -
          <router-link
            class="link"
            :to="{name: 'SearchResults', query: {q: [channel.course_acronym], f: ['course_acronym']}}"
            @click="matomo_clicktracking('click_channelcard_search_course_acronym', channel.course_acronym)"
          >
            {{ channel.course }}
          </router-link>
        </h6>
        <h6 class="my-2">
          <router-link
            class="link"
            :to="{name: 'SearchResults', query: {q: [channel.semester], f: ['semester']}}"
            @click="matomo_clicktracking('click_channelcard_search_semester', channel.semester)"
          >
            {{ channel.semester }}
          </router-link>
        </h6>
        <div class="my-2" style="display: flex; align-items: center">
          <!-- avatar -->
          <router-link
            class="link"
            :to="{name: 'SearchResults', query: {q: [channel.lecturer], f: ['lecturer']}}"
            @click="matomo_clicktracking('click_channelcard_search_lecturer', channel.lecturer)"
          >
            <img :src="channel.thumbnails?.lecturer" alt="avatar" class="avatar rounded-circle" />
          </router-link>
          <!-- channel details -->
          <router-link
            class="link"
            :to="{name: 'SearchResults', query: {q: [channel.lecturer], f: ['lecturer']}}"
            @click="matomo_clicktracking('click_channelcard_search_lecturer', channel.lecturer)"
          >
            <span class="name">{{ channel.lecturer }}</span>
          </router-link>
          <!-- channel details end -->
        </div>
      </div>
      <!-- channel description end -->
    </div>
    <!-- channel description end -->
  </div>
  <!-- channel card end -->
</template>

<script setup lang="ts">
import type {ChannelItem} from "@/data/ChannelItem.js";
import {matomo_clicktracking} from "@/common/matomo_utils";
import {LoggerService} from "@/common/loggerService";

const props = defineProps<{
  channel: ChannelItem;
}>();

const loggerService = new LoggerService();
loggerService.log("channel:");
loggerService.log(props.channel);
</script>

<style scoped>
.avatar {
  width: 50px;
  height: auto;
  float: left;
}

.name {
  display: inline;
  margin-left: 5px;
}

.channel-container {
  width: 100%;
  aspect-ratio: 16 / 9;
  background-color: var(--hans-dark-gray);
  opacity: 0.5;
  display: flex;
  justify-content: center;
  align-items: center;
  transition: all 0.2s ease-in-out;
}

.channel-container:hover {
  background-color: v-bind("props.channel.faculty_color");
  opacity: 0.7;
  transform: scale(1.1);
}

.course-acronym {
  color: var(--hans-dark);
  font-size: 20px;
}

.link {
  color: var(--hans-dark);
  text-decoration: none;
  transition: all 0.2s ease-in-out;
}

.link:hover {
  opacity: 0.5;
}

@media (max-aspect-ratio: 3/4) {
  .channel-card {
    display: flex;
    justify-content: center;
    flex-wrap: wrap;
    width: 100%;
  }

  .card,
  .video-description {
    width: 90%;
  }
}
</style>
