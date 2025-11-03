<template>
  <div class="card-body p-1">
    <div class="topics-container">
      <TopicDetail v-for="item in store.getMarker" :marker="item" :thumbnails="props.video.thumbnails" />
    </div>
  </div>
</template>

<script setup lang="ts">
import {ref, watch} from "vue";
import type {MediaItem} from "@/data/MediaItem.js";
import {matomo_clicktracking} from "@/common/matomo_utils";
import {useI18n} from "vue-i18n";
import {useMediaStore} from "@/stores/media";
import TopicDetail from "@/components/TopicDetail.vue";
import ButtonHint from "@/components/ButtonHint.vue";

const {t, locale} = useI18n({useScope: "global"});
const store = useMediaStore();

const props = defineProps<{
  video: MediaItem;
}>();

const showDetails = ref(false);
const finished_loading = ref(true);

const toggleDetails = () => {
  matomo_clicktracking("click_topic_details", props.video.uuid);
  showDetails.value = !showDetails.value;
};

watch(locale, async (newText) => {
  finished_loading.value = false;
  await store.loadMarkersFromTopics(props.video.uuid, locale.value);
  finished_loading.value = true;
});
</script>

<style scoped>
.topics-container {
  overflow-y: auto;
  display: block;
  max-height: 54vh;
}
</style>
