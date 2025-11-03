<template>
  <HeaderRow />
  <LogoAndSearchbarRow
    :placeholder="t('CreateChannelView.searchplaceholder')"
    :showSearch="false"
    :showProgress="false"
  />
  <div class="main-container">
    <MenuBanner :menutext="t('CreateChannelView.menutext')" />
    <div class="row border sub-container form-container">
      <form
        class="d-grid gap-2"
        method="POST"
        id="createChannelForm"
        enctype="multipart/form-data"
        accept-charset="utf-8"
      >
        <div class="form-group row">
          <label for="inputChannelLanguageSelect" class="col-sm-2 col-form-label">Language</label>
          <div class="col-sm-3">
            <select
              name="language"
              v-on:change="handleChannelLanguageSelect()"
              v-model="inputChannelLanguageSelect"
              class="custom-select"
              id="inputChannelLanguageSelect"
            >
              <option value="en" selected>English</option>
              <option value="de">German</option>
            </select>
          </div>
        </div>
        <div class="form-group row">
          <label for="inputCourse" class="col-sm-2 col-form-label">Course</label>
          <div class="col-sm-4">
            <input
              name="course"
              v-model="inputCourse"
              type="text"
              class="form-control"
              id="inputCourse"
              placeholder="Course"
            />
          </div>
          <label for="inputCourseAcronym" class="col-sm-1 col-form-label">Acronym</label>
          <div class="col-sm-2">
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
          <label for="inputSemester" class="col-sm-2 col-form-label">Semester</label>
          <div class="col-sm-4">
            <input
              name="semester"
              v-model="inputSemester"
              type="text"
              class="form-control"
              id="inputSemester"
              placeholder="summer semester 2022"
            />
          </div>
        </div>
        <div class="form-group row">
          <label for="inputLecturer" class="col-sm-2 col-form-label">Lecturer</label>
          <div class="col-sm-4">
            <input
              name="lecturer"
              v-model="inputLecturer"
              type="text"
              class="form-control"
              id="inputLecturer"
              placeholder="Prof. Dr. Max Mustermann"
            />
          </div>
        </div>
        <div class="form-group row">
          <label for="inputFaculty" class="col-sm-2 col-form-label">Faculty</label>
          <div class="col-sm-5">
            <input
              name="faculty"
              v-model="inputFaculty"
              type="text"
              class="form-control"
              id="inputFaculty"
              placeholder="Faculty"
            />
          </div>
          <label for="inputFacultyAcronym" class="col-sm-1 col-form-label">Acronym</label>
          <div class="col-sm-2">
            <input
              name="faculty_acronym"
              v-model="inputFacultyAcronym"
              type="text"
              class="form-control"
              id="inputFacultyAcronym"
              placeholder="Acronym"
            />
          </div>
          <label for="inputFacultyColor" class="col-sm-1 col-form-label">Color</label>
          <div class="col-sm-1">
            <input
              name="faculty_color"
              v-model="inputFacultyColor"
              type="color"
              class="form-control form-control-color"
              id="inputFacultyColor"
              title="Color"
            />
          </div>
        </div>
        <div class="form-group row">
          <label for="inputUniversity" class="col-sm-2 col-form-label">University</label>
          <div class="col-sm-6">
            <input
              name="university"
              v-model="inputUniversity"
              type="text"
              class="form-control"
              id="inputUniversity"
              placeholder="University"
            />
          </div>
          <label for="inputUniversityAcronym" class="col-sm-1 col-form-label">Acronym</label>
          <div class="col-sm-2">
            <input
              name="university_acronym"
              v-model="inputUniversityAcronym"
              type="text"
              class="form-control"
              id="inputUniversityAcronym"
              placeholder="Acronym"
            />
          </div>
        </div>
        <div class="form-group row">
          <label for="inputLicense" class="col-sm-2 col-form-label">License</label>
          <div class="col-sm-3">
            <input
              name="license"
              v-model="inputLicense"
              type="text"
              class="form-control"
              id="inputLicense"
              placeholder="License, e.g. OER"
            />
          </div>
          <label for="inputLicenseUrl" class="col-sm-1 col-form-label">Url</label>
          <div class="col-sm-5">
            <input
              name="license_url"
              v-model="inputLicenseUrl"
              type="text"
              pattern="https?://.+"
              class="form-control"
              id="inputLicenseUrl"
              placeholder="url, e.g. https://open-educational-resources.de"
            />
          </div>
        </div>
        <div class="form-group row">
          <label for="inputTags" class="col-sm-2 col-form-label">Tags</label>
          <div class="col-sm-8">
            <input
              name="tags"
              v-model="inputTags"
              type="text"
              pattern="^[\w]+(,[\w]+)*$"
              class="form-control"
              id="inputTags"
              placeholder="comma seperated list of tags, without whitespaces"
            />
          </div>
        </div>
        <div class="form-group row">
          <div class="col-sm-2">Lecturer Avatar</div>
          <div class="col-sm-10">
            <div class="input-group">
              <div class="row input-group-prepend">
                <template v-for="(picture, index) in avatarPictures">
                  <input
                    v-model="inputAvatar"
                    class="avatar"
                    type="radio"
                    name="thumbnails_lecturer"
                    :value="picture"
                    :id="`avatar-${index}`"
                  />
                  <label :for="`avatar-${index}`" class="input-group-text avatar-picture">
                    <img :src="picture" :alt="picture" class="img-fluid img-btn" />
                  </label>
                </template>
              </div>
            </div>
          </div>
        </div>
        <div class="form-group row">
          <div class="col-sm-2">Optional</div>
          <div class="col-sm-10">
            <div class="form-check">
              <input
                name="archive_channel_content"
                v-model="archiveChannelContents"
                class="form-check-input"
                type="checkbox"
                id="archiveChannelContents"
              />
              <label class="form-check-label" for="archiveChannelContents"> Create Channel Package </label>
            </div>
          </div>
        </div>
        <div class="form-group row">
          <div class="col-sm-10">
            <button type="button" v-on:click="createChannel()" class="btn btn-primary mb-2">Create</button>
          </div>
        </div>
      </form>
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

const avatarPictures: string[] = [];
const urlOrigin = window.location.origin;
const zeroPad = (num, places) => String(num).padStart(places, "0");
for (let i = 1; i <= 29; i++) {
  avatarPictures.push(
    `${urlOrigin}/avatars/avatar-m-${zeroPad(i, 5)}.png`,
    `${urlOrigin}/avatars/avatar-w-${zeroPad(i, 5)}.png`,
  );
}

const inputChannelLanguageSelect: Ref<HTMLElement | null> = ref("en");
const inputCourse: Ref<HTMLElement | null> = ref(null);
const inputCourseAcronym: Ref<HTMLElement | null> = ref(null);
const inputSemester: Ref<HTMLElement | null> = ref(null);
const inputLecturer: Ref<HTMLElement | null> = ref(null);
const inputFaculty: Ref<HTMLElement | null> = ref(null);
const inputFacultyAcronym: Ref<HTMLElement | null> = ref(null);
const inputFacultyColor: Ref<HTMLElement | null> = ref("#2F9B92");
const inputUniversity: Ref<HTMLElement | null> = ref(null);
const inputUniversityAcronym: Ref<HTMLElement | null> = ref(null);
const inputLicense: Ref<HTMLElement | null> = ref(null);
const inputLicenseUrl: Ref<HTMLElement | null> = ref(null);
// Tags for the channel item
const inputTags: Ref<HTMLElement | null> = ref(null);
const inputAvatar: Ref<HTMLElement | null> = ref(null);
// Optional
const archiveChannelContents: Ref<HTMLElement | null> = ref(null);

const handleChannelLanguageSelect = () => {
  loggerService.log("Channel language selected!");
};

onMounted(() => {
  inputCourse.value?.focus();
});

function createChannel() {
  var bodyFormData = new FormData();
  bodyFormData.append("language", inputChannelLanguageSelect.value);
  bodyFormData.append("course", inputCourse.value);
  bodyFormData.append("course_acronym", inputCourseAcronym.value);
  bodyFormData.append("semester", inputSemester.value);
  bodyFormData.append("lecturer", inputLecturer.value);
  bodyFormData.append("faculty", inputFaculty.value);
  bodyFormData.append("faculty_acronym", inputFacultyAcronym.value);
  bodyFormData.append("faculty_color", inputFacultyColor.value);
  bodyFormData.append("university", inputUniversity.value);
  bodyFormData.append("university_acronym", inputUniversityAcronym.value);
  bodyFormData.append("license", inputLicense.value);
  bodyFormData.append("license_url", inputLicenseUrl.value);
  bodyFormData.append("tags", inputTags.value);
  bodyFormData.append("thumbnails_lecturer", inputAvatar.value);
  if (archiveChannelContents.value === undefined || archiveChannelContents.value === null) {
    bodyFormData.append("archive_channel_content", "false");
  } else {
    bodyFormData.append("archive_channel_content", archiveChannelContents.value);
  }
  loggerService.log(bodyFormData);
  return apiClient
    .post("/createChannel", bodyFormData, {
      headers: {
        "Content-type": "multipart/form-data",
        "Access-Control-Allow-Origin": "*",
      },
    })
    .then((response) => {
      if (response.status === 200) {
        //redirect to default to channels page
        router.push("/channels");
      }
    })
    .catch((error) => {
      loggerService.error("Error creating channel!");
      loggerService.error(error);
    });
}
</script>

<style scoped>
.avatar {
  display: none;
}

.avatar-picture {
  width: auto;
  cursor: pointer;
}

.avatar:hover + .avatar-picture {
  background: var(--hans-light-blue);
  transition: background 0.2s;
}

.avatar:checked + .avatar-picture {
  background: var(--hans-dark-blue);
}

.form-container {
  padding: 1rem 0;
}
</style>
