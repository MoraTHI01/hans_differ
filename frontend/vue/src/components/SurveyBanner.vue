<template>
  <!-- SurveyBanner -->
  <div class="col-3 d-flex justify-content-center survey-container" v-if="hasSurveys">
    <div class="col-5 survey-heading">
      <div>
        <h5>{{ heading }}</h5>
      </div>
    </div>
    <div class="col-13 survey-content">
      <div class="list-container">
        <ul>
          <template v-for="item in surveys" :key="item.survey_title">
            <template v-if="item.survey_status === 'active' && item.survey_language === locale">
              <li>
                <p class="survey-link-text">
                  <a
                    class="survey-link-text"
                    @click="
                      matomo_clicktracking('click_survey', 'title: ' + item.survey_title + ' - url: ' + item.survey_url)
                    "
                    :href="item.survey_url"
                    target="_blank"
                    >{{ item.survey_title }}</a
                  >
                </p>
              </li>
            </template>
          </template>
        </ul>
      </div>
    </div>
  </div>
  <!-- SurveyBanner end -->
</template>

<script setup lang="ts">
import {computed, watch, onMounted} from "vue";
import {matomo_clicktracking} from "@/common/matomo_utils";
import type {SurveyItem} from "@/data/SurveyItem";
import {useI18n} from "vue-i18n";
import {LoggerService} from "@/common/loggerService";

const loggerService = new LoggerService();
const {t, locale} = useI18n({useScope: "global"});

const props = defineProps<{
  heading: string;
  surveys: Array<SurveyItem>;
}>();

function checkHasSurveys() {
  loggerService.log("hasSurveys");
  for (const survey of props.surveys) {
    loggerService.log(survey);
    if (survey.survey_status === "active" && survey.survey_language === locale.value) {
      loggerService.log("hasSurveys:true");
      return true;
    }
  }
  loggerService.log("hasSurveys:false");
  return false;
}

const hasSurveys = computed(() => checkHasSurveys());
onMounted(() => {
  hasSurveys.value = checkHasSurveys();
});

// Watch the locale to register for language changes and switch summary dep. on locale
watch(locale, async (newText) => {
  hasSurveys.value = checkHasSurveys();
});
</script>

<style scoped>
.survey-container {
  left: 4em;
  position: relative;
}
.survey-content {
}
.survey-heading {
  margin-top: 0.5em;
  overflow: hidden;
}

.list-container {
  max-height: 2.375em;
  max-width: 16em;
  position: relative;
  display: flex;
  overflow-y: auto;
  border: var(--bs-border-width) solid var(--bs-border-color);
  border-radius: var(--bs-border-radius);
  margin-left: auto;
  min-width: 14em;
}

.list-container li {
  text-align: left;
  height: 1.5em;
}

.survey-text {
  color: var(--hans-dark-blue);
}

.survey-link-text {
  color: var(--hans-dark-blue);
  text-decoration: underline;
  font-size: small;
}

.survey-link-text:hover {
  color: var(--hans-dark-blue);
  font-weight: bolder;
}

.survey-text-column {
  max-width: 80ch;
  flex-shrink: 1;
  width: auto;
}
</style>
