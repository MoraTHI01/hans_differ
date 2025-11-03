<template>
  <HeaderRow />
  <LogoAndSearchbarRow :placeholder="t('SurveysView.searchplaceholder')" :showSearch="false" :showProgress="false" />
  <div class="main-container">
    <MenuBanner :menutext="t('SurveysView.menutext')" />
    <div class="row sub-container">
      <div class="left col-8 border">
        <form class="d-grid gap-2" method="POST" id="uploadForm" enctype="multipart/form-data" accept-charset="utf-8">
          <div class="form-group row">
            <label for="inputCourseAcronym" class="col-sm-2 col-form-label">Course Acronym</label>
            <div class="col-sm-4">
              <input
                name="course_acronym"
                v-model="inputCourseAcronym"
                type="text"
                class="form-control"
                id="inputCourseAcronym"
                placeholder="Acronym"
              />
            </div>
          </div>
          <div class="form-group row">
            <label for="inputTitle" class="col-sm-2 col-form-label">Survey Title</label>
            <div class="col-sm-4">
              <input
                name="title"
                v-model="inputTitle"
                type="text"
                class="form-control"
                id="inputTitle"
                placeholder="Title"
              />
            </div>
          </div>
          <div class="form-group row">
            <label for="inputSurveyLanguageSelect" class="col-sm-2 col-form-label">Survey Language</label>
            <div class="col-sm-3">
              <select
                name="language"
                v-on:change="handleSurveyLanguageSelect()"
                v-model="inputSurveyLanguageSelect"
                class="custom-select"
                id="inputSurveyLanguageSelect"
              >
                <option value="en" selected>English</option>
                <option value="de">German</option>
              </select>
            </div>
          </div>
          <div class="form-group row">
            <label for="inputUrl" class="col-sm-2 col-form-label">Survey Url</label>
            <div class="col-sm-6">
              <input
                name="semester"
                v-model="inputUrl"
                type="text"
                class="form-control"
                id="inputUrl"
                placeholder="https://somewhere.org/xyz"
              />
            </div>
          </div>
          <div class="form-group row">
            <label for="inputSurveyStatusSelect" class="col-sm-2 col-form-label">Survey Status</label>
            <div class="col-sm-3">
              <select
                name="language"
                v-on:change="handleSurveyStatusSelect()"
                v-model="inputSurveyStatusSelect"
                class="custom-select"
                id="inputSurveyStatusSelect"
              >
                <option value="active" selected>Active</option>
                <option value="inactive">Inactive</option>
              </select>
            </div>
          </div>
          <div class="form-group row">
            <div class="col-sm-10">
              <button type="button" v-on:click="uploadSurvey()" class="btn btn-primary mb-2">Upload</button>
            </div>
          </div>
        </form>
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
import {apiClient} from "@/common/apiClient";
import router from "@/router/index";

import type {Ref} from "vue";
import {ref, onMounted} from "vue";
import {useI18n} from "vue-i18n";
import {LoggerService} from "@/common/loggerService";

const loggerService = new LoggerService();
const {t} = useI18n({useScope: "global"});

// Data
const inputCourseAcronym: Ref<HTMLLabelElement | null> = ref(null);
const inputTitle: Ref<HTMLLabelElement | null> = ref(null);
const inputSurveyLanguageSelect: Ref<HTMLLabelElement | null> = ref("en");
const inputUrl: Ref<HTMLLabelElement | null> = ref(null);
const inputSurveyStatusSelect: Ref<HTMLLabelElement | null> = ref("active");

const handleSurveyLanguageSelect = () => {
  loggerService.log("Survey language selected!");
};

const handleSurveyStatusSelect = () => {
  loggerService.log("Survey status changed!");
};

onMounted(() => {
  inputCourseAcronym.value?.focus();
});

function uploadSurvey() {
  var bodyFormData = new FormData();
  bodyFormData.append("course_acronym", inputCourseAcronym.value);
  bodyFormData.append("survey_title", inputTitle.value);
  bodyFormData.append("survey_language", inputSurveyLanguageSelect.value);
  bodyFormData.append("survey_url", inputUrl.value);
  bodyFormData.append("survey_status", inputSurveyStatusSelect.value);
  loggerService.log(bodyFormData);
  return apiClient
    .post("/survey", bodyFormData, {
      headers: {
        "Content-type": "multipart/form-data",
        "Access-Control-Allow-Origin": "*",
      },
    })
    .then((response) => {
      if (response.status === 200) {
        //redirect to default to home page
        router.push("/");
      }
    })
    .catch((error) => {
      loggerService.error("Error uploading survey!");
      loggerService.error(error);
    });
}
</script>
<style scoped>
.sub-container {
  display: flex;
  flex-direction: column;
  gap: 1rem;
  width: 100%;
  margin-right: auto;
  margin-left: auto;
}
</style>
