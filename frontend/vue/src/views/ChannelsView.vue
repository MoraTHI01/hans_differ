<template>
  <HeaderRow />
  <LogoAndSearchbarRow :placeholder="t('ChannelsView.searchplaceholder')" :showSearch="true" :showProgress="false" />
  <div class="main-container">
    <MenuBanner :menutext="t('ChannelsView.menutext')" />
    <div class="row sub-container channels">
      <LoadingBar class="media-loading" v-if="store.getChannelsLoading" />
      <ChannelCard v-for="item in store.getChannels" :key="item.uuid" :channel="item" />
    </div>
  </div>
  <BottomRow />
</template>

<script setup lang="ts">
import LoadingBar from "@/components/LoadingBarComponent.vue";
import HeaderRow from "@/components/HeaderRow.vue";
import BottomRow from "@/components/BottomRow.vue";
import LogoAndSearchbarRow from "@/components/LogoAndSearchbarRow.vue";
import MenuBanner from "@/components/MenuBanner.vue";
import ChannelCard from "@/components/ChannelCard.vue";
import {useChannelStore} from "@/stores/channels";
import {useMediaStore} from "@/stores/media";

import {matomo_trackpageview} from "@/common/matomo_utils";
import {useI18n} from "vue-i18n";

matomo_trackpageview();

const {t} = useI18n({useScope: "global"});
const store = useChannelStore();

store.loadChannels();
const mediaStore = useMediaStore();
// No automatic local search should be done if on channels view
mediaStore.setLastGlobalSearchterms([]);
</script>

<style scoped>
.channels {
  position: relative;
}
</style>
