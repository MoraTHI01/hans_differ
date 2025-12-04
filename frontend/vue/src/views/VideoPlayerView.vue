<template>
  <NotFoundView v-if="!mediaItem" />
  <ErrorPage
    v-else-if="mediaItem && !authorized"
    :status="t('VideoPlayerView.notauthorizedtitle')"
    :message="t('VideoPlayerView.notauthorizedtext')"
  />
  <VideoPlayerPage v-else-if="mediaItem && authorized && mLayout === 'combined'" :media-item="mediaItem" />
  <SingleTranscriptPage v-else-if="mediaItem && authorized && mLayout === 'transcript'" :media-item="mediaItem" />
  <SingleSlidesPage v-else-if="mediaItem && authorized && mLayout === 'slides'" :media-item="mediaItem" />
  <SinglePlayerPage v-else-if="mediaItem && authorized && mLayout === 'player'" :media-item="mediaItem" />
  <SingleQuestionnaire v-else-if="mediaItem && authorized && mLayout === 'questionnaire'" :media-item="mediaItem" />
  <SingleChatPage
    v-else-if="mediaItem && authorized && mLayout === 'chat'"
    :currItem="mediaItem"
    :channelmode="false"
  />
</template>

<script lang="ts">
import {routeToMedia} from "@/common/loadMedia";
import {useRoute} from "vue-router";
import {useMediaStore} from "@/stores/media";

export default {
  beforeRouteEnter: routeToMedia,
};
</script>

<script setup lang="ts">
import NotFoundView from "./NotFoundView.vue";
import VideoPlayerPage from "@/components/VideoPlayerPage.vue";
import SingleTranscriptPage from "@/components/SingleTranscriptPage.vue";
import SingleChatPage from "@/components/SingleChatPage.vue";
import SingleSlidesPage from "@/components/SingleSlidesPage.vue";
import SinglePlayerPage from "@/components/SinglePlayerPage.vue";
import SingleQuestionnaire from "@/components/SingleQuestionnaire.vue";
import {useAuthStore} from "@/stores/auth";
import {useLayoutStore} from "@/stores/layout";
import ErrorPage from "@/components/ErrorPage.vue";
import {defineProps, ref, watch} from "vue";
import {useI18n} from "vue-i18n";
import {LoggerService} from "@/common/loggerService";

const loggerService = new LoggerService();
const {t} = useI18n({useScope: "global"});

const authorized = ref(false);

const uuid = useRoute().params.uuid as string;
const mediaItem = useMediaStore().getMediaItemByUuid(uuid);

const mLayout = ref("combined");
const layoutStore = useLayoutStore();
layoutStore.setLayout(mLayout.value);

const authStore = useAuthStore();
if (
  ["developer", "admin", "lecturer", "everybody"].includes(authStore.getRole()!) &&
  mediaItem !== null &&
  mediaItem !== undefined &&
  mediaItem.state.published === true
  //||
  //(authStore.getRole()! == "lecturer" && authStore.getUsername() == mediaItem?.description?.lecturer)
) {
  authorized.value = true;
}

watch(layoutStore, async (newText) => {
  loggerService.log("Update layout VideoPlayerView!");
  mLayout.value = layoutStore.getLayout;
});
</script>
