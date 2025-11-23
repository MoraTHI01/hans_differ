<template>
  <!-- header row -->
  <header class="row justify-content-center header-sticky">
    <div class="header-content d-flex">
      <!-- column for left buttons -->
      <div class="header-section d-flex">
        <!-- videos button -->
        <ButtonLight src="/bootstrap-icons/play-btn.svg" route="home" :btntext="t('HeaderRow.media')" invert="0" />
        <!-- videos button end -->

        <!-- channels button -->
        <ButtonLight src="/bootstrap-icons/layers.svg" route="channels" :btntext="t('HeaderRow.channels')" invert="1" />
        <!-- channels button end-->

        <!-- channels button -->
        <ButtonLight
          src="/bootstrap-icons/clock-history.svg"
          route="history"
          :btntext="t('HeaderRow.history')"
          invert="1"
        />
        <!-- channels button end-->
      </div>
      <!-- column for left buttons end -->

      <!-- column for right buttons -->
      <div class="header-section right-section">
        <div class="d-flex">
          <!-- language select -->
          <LanguageSelector />
          <!-- language select end -->
          <!-- login button -->
          <DropdownLogin />
          <!-- login button end -->
        </div>
      </div>
      <!-- column for right buttons end -->
    </div>
  </header>
  <!-- header row end -->
</template>

<script setup lang="ts">
import DropdownLogin from "./DropdownLogin.vue";
import ButtonLight from "./ButtonLight.vue";
import LanguageSelector from "@/components/LanguageSelector.vue";
import {useI18n} from "vue-i18n";

const {t} = useI18n({useScope: "global"});
</script>

<style scoped>
header {
  background-color: var(--hans-dark-blue);
  width: 100%;
  margin: 0;
}

.header-content {
  display: flex;
  width: var(--container-width);
}

.header-section {
  width: auto;
  padding: 0;
}

.right-section {
  margin-left: auto;
}
</style>
