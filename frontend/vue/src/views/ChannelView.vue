<template>
  <NotFoundView v-if="!channelItem" />
  <ErrorPage
    v-else-if="!authorized"
    :status="t('ChannelView.notauthorizedtitle')"
    :message="t('ChannelView.notauthorizedtext')"
  />
  <ChannelPage v-else-if="authorized && mLayout === 'combined'" :channelItem="channelItem" />
  <SingleChatPage v-else-if="authorized && mLayout === 'chat'" :currItem="channelItem" :channelmode="true" />
</template>

<script lang="ts">
import {routeToChannel} from "@/common/loadChannel";
import {useRoute} from "vue-router";

export default {
  beforeRouteEnter: routeToChannel,
};
</script>

<script setup lang="ts">
import NotFoundView from "./NotFoundView.vue";
import ChannelPage from "@/components/ChannelPage.vue";
import SingleChatPage from "@/components/SingleChatPage.vue";
import {useAuthStore} from "@/stores/auth";
import {useChannelStore} from "@/stores/channels";
import {useChatStore} from "@/stores/chat";
import {useLayoutStore} from "@/stores/layout";
import {useMessageStore} from "@/stores/message";
import ErrorPage from "@/components/ErrorPage.vue";
import {ref, computed, nextTick, onMounted, onBeforeUnmount, watch} from "vue";
import {useI18n} from "vue-i18n";
import {LoggerService} from "@/common/loggerService";
import {matomo_trackpageview} from "@/common/matomo_utils";

const loggerService = new LoggerService();
const {t} = useI18n({useScope: "global"});

const authorized = ref(false);

const props = defineProps<{
  uuid: string;
}>();

const channelStore = useChannelStore();
const chatStore = useChatStore();
const messageStore = useMessageStore();
const channelItem = channelStore.getChannelItemByUuid(props.uuid);

const authStore = useAuthStore();
if (
  ["developer", "admin", "lecturer", "everybody"].includes(authStore.getRole()!) &&
  channelItem !== undefined
  //||
  //(authStore.getRole()! == "lecturer" && authStore.getUsername() == mediaItem?.description?.lecturer)
) {
  authorized.value = true;
}

const mLayout = ref("combined");
const layoutStore = useLayoutStore();
layoutStore.setLayout(mLayout.value);

matomo_trackpageview();

onMounted(async () => {
  if (authorized.value === true) {
    chatStore.loadChatSettings();
    messageStore.setServicesRequired(true);
    await messageStore.fetchServiceStatus();
  }
});

onBeforeUnmount(() => {
  messageStore.setServicesRequired(false);
  chatStore.storeChatSettings();
});

watch(layoutStore, async (newText) => {
  loggerService.log("Update layout ChannelView!");
  mLayout.value = layoutStore.getLayout;
});
</script>
