<template>
  <router-link :to="{name: 'home'}" class="col-3 my-3" @click="matomo_clicktracking('click_button', 'logo')"
    ><img src="/logo_full.svg" alt="logo" class="logo"
  /></router-link>
</template>

<script setup lang="ts">
import {matomo_clicktracking} from "@/common/matomo_utils";
</script>

<style scoped>
.logo {
  width: auto;
  max-height: 4em;
}
</style>
