<template>
  <LogoRow>
    <VideoSearchBar @searchterms="$emit('searchterms', $event)" ref="searchbar" />
    <SurveyBanner :heading="surveys_heading" :surveys="surveys" />
  </LogoRow>
</template>

<script setup lang="ts">
import {ref} from "vue";
import LogoRow from "./LogoRow.vue";
import SearchBar from "./SearchBar.vue";
import VideoSearchBar from "./VideoSearchBar.vue";
import SurveyBanner from "./SurveyBanner.vue";
import type {SurveyItem} from "@/data/SurveyItem";

const searchbar = ref();

defineProps<{
  placeholder: string;
  surveys_heading: string;
  surveys: Array<SurveyItem>;
}>();

defineEmits<{
  (e: "searchterms", terms: string[]): void;
}>();

defineExpose({
  /**
   * Clears the search bar text
   */
  clearSearch() {
    searchbar.value.clearSearch();
  },
  /**
   * Enables a message near the search bar indicating that no search result was found for the given query.
   * The message will disappear on any further input.
   */
  setNotFound() {
    searchbar.value.setNotFound();
  },
  /**
   * Search
   */
  search(searchterms: string) {
    searchbar.value.search(searchterms);
  },
});
</script>
