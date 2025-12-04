<template>
  <HeaderRow />
  <LogoAndVideoSearchbarRow
    v-if="!props.channelmode"
    :placeholder="t('VideoPlayerView.searchplaceholder')"
    :surveys="currItem.surveys"
    :surveys_heading="t('VideoPlayerView.surveybanner')"
  />
  <LogoAndSearchbarRow
    v-else
    :placeholder="t('ChannelPage.searchplaceholder')"
    :showSearch="true"
    :showProgress="false"
    :showLayoutOptions="true"
    :showLayoutOptionsChannelMode="true"
  />
  <div class="main-container">
    <ChatComponent
      class="chat-comp-container"
      :uuid="props.currItem.uuid"
      :language="props.currItem.language"
      :active="true"
      :channelmode="props.channelmode"
      :singleview="true"
    />
  </div>
  <BottomRow />
</template>

<script setup lang="ts">
import {ref, computed, nextTick, onMounted, onBeforeUnmount, watch} from "vue";
import HeaderRow from "@/components/HeaderRow.vue";
import BottomRow from "@/components/BottomRow.vue";
import LogoAndVideoSearchbarRow from "@/components/LogoAndVideoSearchbarRow.vue";
import LogoAndSearchbarRow from "@/components/LogoAndSearchbarRow.vue";
import ChatComponent from "@/components/ChatComponent.vue";
import type {MediaItem} from "@/data/MediaItem";
import type {ChannelItem} from "@/data/ChannelItem";
import {matomo_trackpageview} from "@/common/matomo_utils";
import {useI18n} from "vue-i18n";
import {matomo_clicktracking} from "@/common/matomo_utils";
import {LoggerService} from "@/common/loggerService";
import {useMessageStore} from "@/stores/message";

const loggerService = new LoggerService();
const {t, locale} = useI18n({useScope: "global"});

const props = defineProps<{
  currItem: MediaItem | ChannelItem;
  channelmode: boolean;
}>();

const messageStore = useMessageStore();
messageStore.setServicesRequired(true);

onMounted(async () => {
  await messageStore.fetchServiceStatus();
});
</script>
<style scoped>
.main-container {
  height: 100%;
}
.chat-comp-container {
  border: 1px solid var(--hans-light-gray);
  border-radius: 0.25rem;
  height: 100%;
}
:deep(.chat-messages-container) {
  min-height: 58vh !important;
  margin-top: 1em;
}
:deep(.chat-messages) {
  max-height: 56vh;
}
</style>
