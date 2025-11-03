<template>
  <div class="consent-banner-background">
    <div class="consent-banner">
      <div class="row">
        <div class="col-6 disclaimer-text-column">
          <p class="disclaimer-text">
            {{ t("ConsentBannerMatomo.text") }}
            <a class="link-text" href="https://matomo.org/faq/general/faq_18254/" target="_blank">{{
              t("ConsentBannerMatomo.link")
            }}</a
            >.
          </p>
        </div>
        <div class="col-3 consent-buttons">
          <div class="btn btn-container">
            <span class="btn-text" @click="userConsentTracking()">{{ t("ConsentBannerMatomo.accept") }}</span>
          </div>
          <div class="btn btn-container">
            <span class="btn-text" @click="disableTracking()">{{ t("ConsentBannerMatomo.decline") }}</span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import type {Ref} from "vue";
import {ref, onMounted} from "vue";
import {useI18n} from "vue-i18n";

const {t} = useI18n({useScope: "global"});

function userConsentTracking() {
  _paq.push(["forgetUserOptOut"]);
  _paq.push(["rememberConsentGiven"]);
  _paq.push(["rememberCookieConsentGiven"]);
  checkUserConsent();
}

function disableTracking() {
  _paq.push(["optUserOut"]);
  _paq.push(["disableCookies"]);
  checkUserConsent();
}

function checkUserConsent() {
  var visitorConsent;
  var visitorOptedOut;
  _paq.push([
    function () {
      visitorConsent = this.getRememberedConsent();
    },
  ]);
  _paq.push([
    function () {
      visitorOptedOut = this.isUserOptedOut();
    },
  ]);
  if (visitorOptedOut === false) {
    if (visitorConsent !== null) {
      var el = document.getElementsByClassName("consent-banner-background");
      if (el.length > 0) {
        el[0].style.display = "none";
      }
    }
  } else {
    var el = document.getElementsByClassName("consent-banner-background");
    if (el.length > 0) {
      el[0].style.display = "none";
    }
  }
}

onMounted(() => {
  _paq.push(["forgetUserOptOut"]);
  checkUserConsent();
});
</script>

<style scoped>
.consent-banner-background {
  position: fixed;
  top: 0;
  bottom: 0;
  left: 0;
  right: 0;
  background: rgba(0, 0, 0, 0.7);
  transition: opacity 500ms;
  visibility: visible;
  opacity: 1;
}

.consent-banner {
  margin: auto;
  width: 100%;
  background-color: #6d8edf;
  font-size: 100%;
  padding: 2em;
  padding-left: 2em;
  padding-right: 4em;
  position: absolute;
  top: 25%;
  left: 0;
}

.disclaimer-text {
  color: var(--hans-light);
}

.link-text {
  color: var(--hans-light);
  text-decoration: underline;
}

.link-text:hover {
  color: var(--hans-light);
  font-weight: bolder;
}

.btn-container {
  display: flex;
  align-items: center;
  float: left;
  color: var(--hans-light);
}

.btn-container:hover {
  color: var(--hans-dark);
}

.btn-container:hover {
  background-color: var(--hans-light);
}

.img-btn {
  filter: invert(1);
}

.btn-text {
  margin-left: 5px;
  color: var(--hans-light);
}

.btn-container:hover > .img-btn {
  filter: invert(0);
}

.btn-container:hover > .btn-text {
  color: var(--hans-dark);
}

.consent-buttons {
  width: auto;
}

.disclaimer-text-column {
  max-width: 80ch;
  flex-shrink: 1;
  width: auto;
}
</style>
