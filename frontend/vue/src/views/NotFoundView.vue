<template>
  <ErrorPage :status="t('NotFoundView.status')" :message="t('NotFoundView.message')" />
</template>

<script setup lang="ts">
import ErrorPage from "@/components/ErrorPage.vue";
import {useI18n} from "vue-i18n";
const {t} = useI18n({useScope: "global"});
</script>
