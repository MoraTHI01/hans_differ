<template>
  <HeaderRow />
  <LogoAndSearchbarRow
    :placeholder="t('SearchResultsView.searchplaceholder')"
    :showSearch="true"
    :showProgress="false"
  />
  <div class="main-container">
    <div class="row search-results">
      <LoadingBar class="media-loading" v-if="store.getFoundMediaLoading" />
      <SearchTerms class="search-terms" :searchterms="queryTerms" />
      <div class="sub-container found-media">
        <VideoCard
          class="row"
          video-classes="col-4"
          :video="item"
          v-for="(item, index) in store.getFoundMedia"
          :key="index"
          :class="{'padded-item': index > 0}"
        />
      </div>
    </div>
  </div>
  <BottomRow />
</template>

<script setup lang="ts">
import LoadingBar from "@/components/LoadingBarComponent.vue";
import HeaderRow from "@/components/HeaderRow.vue";
import BottomRow from "@/components/BottomRow.vue";
import LogoAndSearchbarRow from "@/components/LogoAndSearchbarRow.vue";
import SearchTerms from "@/components/SearchTerms.vue";
import VideoCard from "@/components/VideoCard.vue";
import {useMediaStore} from "@/stores/media";
import {onMounted, ref, watch} from "vue";
import {matomo_trackpageview, matomo_searchtracking} from "@/common/matomo_utils";
import {useI18n} from "vue-i18n";
import {LoggerService} from "@/common/loggerService";

const loggerService = new LoggerService();
const {t, locale} = useI18n({useScope: "global"});

const props = defineProps<{
  query: string[] | string;
  fields: string[] | string;
}>();

// If reload happens query param q is not an array anymore
const queryTerms = ref(typeof props.query === "string" ? props.query.split(" ") : props.query);
const fieldTerms = ref(typeof props.fields === "string" ? props.fields.split(" ") : props.fields);
const store = useMediaStore();

const searchNow = () => {
  loggerService.log("Search term");
  loggerService.log(props.query);
  loggerService.log("Search fields");
  loggerService.log(props.fields);
  // TODO: parse query parameter to obtain sort by values, currently static:
  store.searchMedia(queryTerms.value, fieldTerms.value, ["description.course", "description.lecturer", "title"]);
  if (fieldTerms.value && fieldTerms.value.includes("tags")) {
    // Do not automatic local search if channels view was used
    store.setLastGlobalSearchterms([]);
  } else {
    // Do automatic local search
    store.setLastGlobalSearchterms(queryTerms.value);
  }
};

onMounted(() => {
  searchNow();
});

matomo_trackpageview();
// Second parameter: search category selected in your search engine. If you do not need this, set to false
matomo_searchtracking(queryTerms.value, false, store.foundMedia.data.size);

// Watch the locale to register for language changes and switch summary dep. on locale
watch(locale, async (newText) => {
  searchNow();
});
</script>

<style scoped>
.search-results {
  position: relative;
}
.padded-item {
  padding-top: 2em; /* Adjust the padding value as needed */
}
@media (max-aspect-ratio: 3/4) {
  .search-results {
    flex-direction: column;
    justify-content: center;
  }

  .search-terms {
    width: auto;
  }
}
</style>
