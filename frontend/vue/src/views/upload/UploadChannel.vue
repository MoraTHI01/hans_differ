<template>
  <HeaderRow />
  <LogoAndSearchbarRow :placeholder="t('HomeView.searchplaceholder')" :showSearch="false" :showProgress="false" />
  <div class="main-container">
    <MenuBanner :menutext="t('UploadChannelView.menutext')" />
    <div v-if="isLoading" class="row sub-container channels-load-container">
      <LoadingBar class="channels-loading" />
    </div>
    <div v-else class="row sub-container channels">
      <ChannelCard
        v-for="item in channelItems"
        :key="item.uuid"
        :channel="item"
        @click="openMediaItemOverviewForChannel(item)"
      />
    </div>
  </div>
  <BottomRow />
</template>

<script setup lang="ts">
import LoadingBar from "@/components/LoadingBarComponent.vue";
import HeaderRow from "@/components/HeaderRow.vue";
import BottomRow from "@/components/BottomRow.vue";
import ChannelCard from "@/components/ChannelCard.vue";
import LogoAndSearchbarRow from "@/components/LogoAndSearchbarRow.vue";
import MenuBanner from "@/components/MenuBanner.vue";
import router from "@/router/index";
import {useMessageStore} from "@/stores/message";
import {useChannelStore} from "@/stores/channels";
import type {ChannelItem} from "@/data/ChannelItem";
import {useI18n} from "vue-i18n";
import {onBeforeUnmount, ref, watch} from "vue";
import {matomo_trackpageview} from "@/common/matomo_utils";

matomo_trackpageview();

const {t, locale} = useI18n({useScope: "global"});
const channelItems = ref<ChannelItem[]>([]);

const store = useChannelStore();
const messageStore = useMessageStore();
const isLoading = ref(true);
messageStore.setServicesRequired(true);
loadChannels(true);

watch(locale, loadChannels(true));

function loadChannels(first_load: boolean = false) {
  if (first_load === true) {
    isLoading.value = true;
  }
  messageStore.fetchServiceStatus();
  store.loadUserChannels().then(() => {
    channelItems.value = Array.from(store.getUserChannels);
    isLoading.value = false;
  });
}

onBeforeUnmount(() => {
  messageStore.setServicesRequired(false);
});

function openMediaItemOverviewForChannel(channel: ChannelItem) {
  store.setCurrentUserChannel(channel);
  router.push("/upload/overview");
}
</script>

<style scoped>
.channels-loading {
  --bar-height: 0.4em;
}

.channels-overview-container {
  width: 100%;
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  align-items: center;
  position: relative;
}

.channels-load-container {
  position: relative;
}

@media (max-aspect-ratio: 3/4) {
  .channels-overview-container {
    justify-content: center;
  }
  .channels-load-container {
    justify-content: center;
  }
}
.channels {
  position: relative;
}
</style>
