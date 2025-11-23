<template>
  <!-- footer row -->
  <br /><br />
  <footer class="row justify-content-center bottom-sticky">
    <div class="footer-content">
      <!-- column for left buttons -->
      <nav>
        <router-link
          class="btn"
          @click="matomo_clicktracking('click_button', 'How to contact us')"
          :to="{name: 'contact'}"
        >
          <span class="btn-text">{{ t("BottomRow.linkContact") }}</span>
        </router-link>
        <router-link class="btn" @click="matomo_clicktracking('click_button', 'Legal notice')" :to="{name: 'legal'}">
          <span class="btn-text">{{ t("BottomRow.linkLegal") }}</span>
        </router-link>
        <router-link
          class="btn"
          @click="matomo_clicktracking('click_button', 'Data protection')"
          :to="{name: 'dataprotection'}"
        >
          <span class="btn-text">{{ t("BottomRow.linkDataProtection") }}</span>
        </router-link>
        <router-link
          class="btn"
          @click="matomo_clicktracking('click_button', 'General notes')"
          :to="{name: 'generalnotes'}"
        >
          <span class="btn-text">{{ t("BottomRow.generalNotes") }}</span>
        </router-link>
        <span v-if="ev.getEvalActive() === true" class="eval-text">Evaluation Id: {{ ev.getEvalId() }}</span>
      </nav>
    </div>
    <ConsentBanner />
  </footer>
  <!-- header row end -->
</template>

<script setup lang="ts">
import {matomo_clicktracking} from "@/common/matomo_utils";
import {useI18n} from "vue-i18n";
import {useEvalStore} from "@/stores/eval";
import ConsentBanner from "@/components/ConsentBannerMatomo.vue";

const ev = useEvalStore();

const {t} = useI18n({useScope: "global"});
</script>

<style scoped>
footer {
  background-color: var(--hans-dark-blue);
  width: 100%;
  margin: 0;
  bottom: 0 !important;
  position: sticky !important;
  z-index: 99999;
}

@media (max-width: 600px) {
  footer {
    position: relative !important;
    top: 64vh;
  }
}

.footer-content {
  width: var(--container-width);
}

.eval-text {
  margin-left: 5px;
  color: var(--hans-light);
  font-size: 10pt;
  text-align: center;
  position: fixed;
  margin-top: 95px;
  bottom: 8px;
}

.btn-text {
  margin-left: 5px;
  color: var(--hans-light);
  font-size: 12px;
  text-align: center;
}

.btn-text:hover {
  color: var(--hans-light);
  font-weight: bolder;
}
</style>
