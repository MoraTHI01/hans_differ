<template>
  <HeaderRow />
  <LogoAndSearchbarRow :placeholder="API" :showSearch="false" :showProgress="false" />
  <div class="main-container">
    <MenuBanner :menutext="t('OpenApiView.menutext')" />
    <div class="openapi">
      <iframe class="openapi-iframe" src="http://localhost/api/openapi/" allowfullscreen></iframe>
    </div>
  </div>
  <BottomRow />
</template>

<script setup lang="ts">
import HeaderRow from "@/components/HeaderRow.vue";
import BottomRow from "@/components/BottomRow.vue";
import LogoAndSearchbarRow from "@/components/LogoAndSearchbarRow.vue";
import MenuBanner from "@/components/MenuBanner.vue";
import {useI18n} from "vue-i18n";

const {t} = useI18n({useScope: "global"});
</script>

<style>
@media (min-width: 1024px) {
  .openapi {
    position: relative;
    overflow: hidden;
    width: 100%;
    height: 100vh;
    padding-top: 56.25%; /* 16:9 Aspect Ratio (divide 9 by 16 = 0.5625) */
    display: flex;
    align-items: center;
  }
  .openapi-iframe {
    position: absolute;
    top: 0;
    left: 0;
    bottom: 0;
    right: 0;
    width: 100%;
    height: 100%;
    border: none;
  }
}
</style>
