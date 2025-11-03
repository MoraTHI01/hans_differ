<template>
  <LogoRow v-if="props.showSearch">
    <SearchBar :placeholder="placeholder" />
  </LogoRow>
  <LogoRow v-else-if="props.showProgress">
    <ProgressBar
      :current="progressLanguage == 'de' ? progressLanguageDeMatchStep : progressLanguageDeNotMatchStep"
      :total="progressTotalSteps"
    ></ProgressBar>
  </LogoRow>
  <LogoRow v-else></LogoRow>
</template>

<script setup lang="ts">
import {ref} from "vue";
import LogoRow from "./LogoRow.vue";
import SearchBar from "./SearchBar.vue";
import ProgressBar from "@/components/ProgressBar.vue";

const props = defineProps<{
  placeholder: string;
  showSearch: boolean;
  showProgress: boolean;
  progressLanguage: string;
  progressLanguageDeMatchStep: number;
  progressLanguageDeNotMatchStep: number;
  progressTotalSteps: number;
}>();
</script>
