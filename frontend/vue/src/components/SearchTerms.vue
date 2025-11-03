<template>
  <!-- search terms -->
  <div class="col-6 col-md-4">
    <div class="menu p-2 my-1 rounded border" style="display: inline-block">
      <img src="/bootstrap-icons/play-btn.svg" alt="play-btn" />
      {{ t("SearchTerms.text") }}
      <span class="mark rounded p-1" v-for="item in searchterms">{{ item }}</span>
    </div>
  </div>
  <!-- search terms end-->
</template>

<script setup lang="ts">
import {useI18n} from "vue-i18n";

const {t} = useI18n({useScope: "global"});
defineProps<{
  searchterms: string[];
}>();
</script>

<style scoped>
.mark,
mark {
  background-color: rgb(211, 211, 211);
}
</style>
