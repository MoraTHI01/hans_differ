<template>
  <HeaderRow />
  <LogoAndSearchbarRow :placeholder="t('ContactView.searchplaceholder')" :showSearch="false" :showProgress="false" />
  <div class="main-container">
    <MenuBanner :menutext="t('ContactView.menutext')" />
    <div class="row sub-container">
      <div class="col-md-9 col-md-offset-3">
        <div class="col-content">
          <section class="content content-text">
            <div class="container">
              <div class="content-inner">
                <h2>HAnS</h2>
                <p>
                  <strong
                    >{{ t("ContactView.about") }}<br />
                    {{ t("ContactView.notice") }}</strong
                  >
                </p>
                <h4>{{ t("ContactView.heading") }}</h4>
                <p>
                  <strong>{{ t("ContactView.contact") }}</strong
                  ><br />Verbundprojekt HAnS<br />Technische Hochschule Nürnberg Georg Simon Ohm<br />Kesslerplatz 12<br />90489
                  Nürnberg<br />Tel.: + 49 911/5880-1632<br />Email:
                  <a
                    @click="matomo_clicktracking('click_link', $event.target.href)"
                    href="mailto:verbundprojekt-hans@th-nuernberg.de"
                    >verbundprojekt-hans<span class="fa fa-at"><span class="sr-only">at</span></span
                    >th-nuernberg<span class="fa fa-circle dot-subst"
                      ><span class="sr-only">{{ t("ContactView.dot") }}</span></span
                    >de</a
                  ><strong></strong>
                </p>
                <hr />
              </div>
            </div>
          </section>
          <strong>{{ t("ContactView.report") }}</strong>
          <br /><br />
          <a
            @click="matomo_clicktracking('click_button', 'error_report')"
            href="mailto:tobias.bocklet@th-nuernberg.de, korbinian.riedhammer@th-nuernberg.de,
            thomas.ranzenberger@th-nuernberg.de,fabian.schneider@th-nuernberg.de,
            christopher.simic@th-nuernberg.de?subject=HAnS Error Report"
            class="btn btn-primary btn-md"
          >
            {{ t("ContactView.linkReport") }}</a
          >
        </div>
      </div>
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
import {matomo_trackpageview, matomo_clicktracking} from "@/common/matomo_utils";

matomo_trackpageview();

function alert_link(link) {
  alert(link);
}

const {t} = useI18n({useScope: "global"});
</script>

<style scoped>
.container {
  /* Removes redundant padding and margin from the bootstrap container class */
  padding: 0;
  margin: 0;
}
</style>
