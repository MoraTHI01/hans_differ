<template>
  <HeaderRow />
  <LogoRow />
  <div class="main-container error-container">
    <main class="error-message-wrapper">
      <h1 class="error-status">{{ status }}</h1>
      <h2 class="error-message">{{ message }}</h2>
    </main>
    <SearchBar :placeholder="t('ErrorPage.searchplaceholder')" />
  </div>
  <BottomRow />
</template>

<script setup lang="ts">
import HeaderRow from "@/components/HeaderRow.vue";
import BottomRow from "@/components/BottomRow.vue";
import LogoRow from "@/components/LogoRow.vue";
import SearchBar from "@/components/SearchBar.vue";

import {useI18n} from "vue-i18n";

defineProps<{
  status: string;
  message: string;
}>();

const {t} = useI18n({useScope: "global"});
</script>

<style scoped>
.error-container {
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
}

.error-message-wrapper {
  text-align: center;
  margin-bottom: 4em;
}

.error-status {
  font-weight: bold;
  margin-bottom: 0.5em;
}
</style>
