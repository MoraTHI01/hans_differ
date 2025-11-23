<template>
  <!-- AnnouncementBanner -->
  <div class="col announcements-container">
    <template v-for="item in announcements" :key="item.uuid">
      <div class="row announcement-heading" :id="item.uuid">
        <div v-if="locale === 'de'">
          <h5 class="rotating-text">{{ item.title_de }}: {{ item.text_de }}</h5>
        </div>
        <div v-else-if="locale === 'en'">
          <h5 class="rotating-text">{{ item.title_en }}: {{ item.text_en }}</h5>
        </div>
      </div>
    </template>
  </div>
  <!-- AnnouncementBanner end -->
</template>

<script setup lang="ts">
import {ref, watch, onMounted} from "vue";
import {matomo_clicktracking} from "@/common/matomo_utils";
import {useAuthStore} from "@/stores/auth";
import {useI18n} from "vue-i18n";
import {LoggerService} from "@/common/loggerService";
import {apiClient} from "@/common/apiClient";

const loggerService = new LoggerService();
const {t, locale} = useI18n({useScope: "global"});

const authStore = useAuthStore();
const announcements = ref([]);

onMounted(async () => {
  if (authStore.getLoggedIn() === true) {
    const {data} = await apiClient.get("/announcement");
    if ("result" in data && Object.keys(data.result).length > 0) {
      announcements.value = data.result;
    }
  }
});
</script>

<style scoped>
.announcements-container {
  display: inline-block;
}

.announcement-heading {
  margin-top: 0.5em;
  overflow: hidden;
  text-align: center;
  position: relative;
  left: 0.7em;
  color: var(--hans-dark-blue);
}

.rotating-text {
  font-weight: bold;
  white-space: nowrap;
  animation: scrollText 15s linear infinite;
}

@keyframes scrollText {
  0% {
    transform: translateX(100%);
  }
  100% {
    transform: translateX(-100%);
  }
}
</style>
