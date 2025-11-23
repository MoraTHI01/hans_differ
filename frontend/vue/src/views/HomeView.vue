<template>
  <HeaderRow />
  <LogoAndSearchbarRow :placeholder="t('HomeView.searchplaceholder')" :showSearch="true" :showProgress="false" />
  <div class="main-container">
    <MenuBanner :menutext="t('HomeView.menutext')" />
    <div class="row sub-container recent-media">
      <LoadingBar class="media-loading" v-if="store.getRecentMediaLoading" />
      <VideoCard class="col-3" v-for="item in store.getRecentMedia" :video="item" />
    </div>
    <AirflowStatus />
  </div>
  <BottomRow />
</template>

<script setup lang="ts">
import LoadingBar from "@/components/LoadingBarComponent.vue";
import HeaderRow from "@/components/HeaderRow.vue";
import BottomRow from "@/components/BottomRow.vue";
import LogoAndSearchbarRow from "@/components/LogoAndSearchbarRow.vue";
import VideoCard from "@/components/VideoCard.vue";
import MenuBanner from "@/components/MenuBanner.vue";
import AirflowStatus from '@/components/AirflowStatus.vue';

import {useMediaStore} from "@/stores/media";
import {matomo_trackpageview} from "@/common/matomo_utils";
import {useI18n} from "vue-i18n";

matomo_trackpageview();

const {t} = useI18n({useScope: "global"});
const store = useMediaStore();

store.loadRecentMedia();
// No automatic local search should be done if on home view
store.setLastGlobalSearchterms([]);
</script>

<style scoped>
.media-loading {
  --bar-height: 0.4em;
}

.recent-media {
  position: relative;
}

@media (max-aspect-ratio: 3/4) {
  .recent-media {
    justify-content: center;
  }
}
</style>
