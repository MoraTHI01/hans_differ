<template>
  <LogoRow v-if="props.showSearch">
    <SearchBar :placeholder="placeholder" />
    <div v-if="props.showLayoutOptions" class="col d-flex layout-container">
      <LayoutOptions :channelmode="props.showLayoutOptionsChannelMode"></LayoutOptions>
    </div>
  </LogoRow>
  <LogoRow v-else-if="props.showProgress">
    <ProgressBar
      :current="progressLanguage == 'de' ? progressLanguageDeMatchStep : progressLanguageDeNotMatchStep"
      :total="progressTotalSteps"
    ></ProgressBar>
  </LogoRow>
  <LogoRow v-else>
    <div v-if="props.showLayoutOptions" class="col d-flex layout-container">
      <LayoutOptions :channelmode="props.showLayoutOptionsChannelMode"></LayoutOptions>
    </div>
  </LogoRow>
</template>

<script setup lang="ts">
import {ref} from "vue";
import LogoRow from "./LogoRow.vue";
import SearchBar from "./SearchBar.vue";
import ProgressBar from "@/components/ProgressBar.vue";
import LayoutOptions from "./LayoutOptions.vue";

const props = defineProps<{
  placeholder: string;
  showSearch: boolean;
  showProgress: boolean;
  progressLanguage: string;
  progressLanguageDeMatchStep: number;
  progressLanguageDeNotMatchStep: number;
  progressTotalSteps: number;
  showLayoutOptions: boolean;
  showLayoutOptionsChannelMode: boolean;
}>();
</script>
<style lang="css" scoped>
.layout-container {
  margin-right: -1.3rem;
}
</style>
