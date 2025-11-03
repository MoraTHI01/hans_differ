<template>
  <HeaderRow />
  <LogoAndSearchbarRow :placeholder="t('UploadView.searchplaceholder')" :showSearch="false" :showProgress="false" />
  <div class="main-container">
    <MenuBanner :menutext="t('UploadView.menutext')" />
    <div class="row justify-content-left sub-container">
      <div class="left col-8 border">
        <form class="d-grid gap-2" method="POST" id="uploadForm" enctype="multipart/form-data" accept-charset="utf-8">
          <div class="form-group row">
            <label for="inputMediaFile" class="col-sm-2 col-form-label">Media file</label>
            <div class="col-sm-3">
              <input
                name="media"
                v-on:change="handleMediaFileUpload()"
                ref="inputMediaFile"
                type="file"
                class="form-control-file"
                id="inputMediaFile"
                accept=".mp4, .mp3"
              />
            </div>
          </div>
          <div class="form-group row">
            <label for="inputMediaFileLanguageSelect" class="col-sm-2 col-form-label">Language</label>
            <div class="col-sm-3">
              <select
                name="language"
                v-on:change="handleMediaFileLanguageSelect()"
                v-model="inputMediaFileLanguageSelect"
                class="custom-select"
                id="inputMediaFileLanguageSelect"
              >
                <option value="en" selected>English</option>
                <option value="de">German</option>
              </select>
            </div>
          </div>
          <div class="form-group row">
            <label for="inputSlidesFile" class="col-sm-2 col-form-label">Slides file</label>
            <div class="col-sm-3">
              <input
                name="slides"
                v-on:change="handleSlidesFileUpload()"
                ref="inputSlidesFile"
                type="file"
                class="form-control-file"
                id="inputSlidesFile"
                accept=".pdf"
              />
            </div>
          </div>
          <div class="form-group row">
            <label for="inputTitle" class="col-sm-2 col-form-label">Title</label>
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
            <div class="col-sm-2">Permissions</div>
            <div class="col-sm-10">
              <div class="form-check">
                <input
                  name="permission_public"
                  v-model="gridPermissionPublic"
                  class="form-check-input"
                  type="checkbox"
                  id="gridPermissionPublic"
                />
                <label class="form-check-label" for="gridPermissionPublic"> Public </label>
              </div>
              <div class="form-check">
                <input
                  name="permission_university_only"
                  v-model="gridPermissionUniversityOnly"
                  class="form-check-input"
                  type="checkbox"
                  id="gridPermissionUniversityOnly"
                />
                <label class="form-check-label" for="gridPermissionUniversityOnly"> University only </label>
              </div>
              <div class="form-check">
                <input
                  name="permission_faculty_only"
                  v-model="gridPermissionFacultyOnly"
                  class="form-check-input"
                  type="checkbox"
                  id="gridPermissionFacultyOnly"
                />
                <label class="form-check-label" for="gridPermissionFacultyOnly"> Faculty only </label>
              </div>
              <div class="form-check">
                <input
                  name="permission_study_topic_only"
                  v-model="gridPermissionStudyTopicOnly"
                  class="form-check-input"
                  type="checkbox"
                  id="gridPermissionStudyTopicOnly"
                />
                <label class="form-check-label" for="gridPermissionStudyTopicOnly"> Topic of study only </label>
              </div>
              <div class="form-check">
                <input
                  name="permission_students_only"
                  v-model="gridPermissionStudentsOnly"
                  class="form-check-input"
                  type="checkbox"
                  id="gridPermissionStudentsOnly"
                />
                <label class="form-check-label" for="gridPermissionStudentsOnly"> Students only </label>
              </div>
            </div>
          </div>
          <div class="form-group row">
            <div class="col-sm-2">Licenses</div>
            <div class="col-sm-10">
              <div class="form-check">
                <input
                  name="license_cc_0"
                  v-model="gridLicenseCC0"
                  class="form-check-input"
                  type="checkbox"
                  id="gridLicenseCC0"
                />
                <label class="form-check-label" for="gridLicenseCC0">
                  CC0 1.0 Universal (CC0 1.0) Public Domain Dedication
                </label>
                <div class="col-sm-3">
                  <a href="https://creativecommons.org/publicdomain/zero/1.0/" target="_blank">
                    <img
                      src="/creativecommons-icons/cc-zero.svg"
                      alt="cc-zero-license-icon"
                      class="img-fluid img-btn"
                    />
                  </a>
                </div>
              </div>
              <div class="form-check">
                <input
                  name="license_cc_by_4"
                  v-model="gridLicenseCCBY4"
                  class="form-check-input"
                  type="checkbox"
                  id="gridLicenseCCBY4"
                />
                <label class="form-check-label" for="gridLicenseCCBY4">
                  Attribution 4.0 International (CC BY 4.0)
                </label>
                <div class="col-sm-3">
                  <a href="https://creativecommons.org/licenses/by/4.0/" target="_blank">
                    <img src="/creativecommons-icons/by.svg" alt="cc-by-4.0-license-icon" class="img-fluid img-btn" />
                  </a>
                </div>
              </div>
              <div class="form-check">
                <input
                  name="license_cc_by_sa_4"
                  v-model="gridLicenseCCBYSA4"
                  class="form-check-input"
                  type="checkbox"
                  id="gridLicenseCCBYSA4"
                />
                <label class="form-check-label" for="gridLicenseCCBYSA4">
                  Attribution-ShareAlike 4.0 International (CC BY-SA 4.0)
                </label>
                <div class="col-sm-3">
                  <a href="https://creativecommons.org/licenses/by-sa/4.0/" target="_blank">
                    <img
                      src="/creativecommons-icons/by-sa.svg"
                      alt="cc-by-sa-4.0-license-icon"
                      class="img-fluid img-btn"
                    />
                  </a>
                </div>
              </div>
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
            <div class="col-sm-10">
              <button type="button" v-on:click="uploadMedia()" class="btn btn-primary mb-2">Upload</button>
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
const avatarPictures: string[] = [];
const urlOrigin = window.location.origin;
const zeroPad = (num, places) => String(num).padStart(places, "0");
for (let i = 1; i <= 29; i++) {
  avatarPictures.push(
    `${urlOrigin}/avatars/avatar-m-${zeroPad(i, 5)}.png`,
    `${urlOrigin}/avatars/avatar-w-${zeroPad(i, 5)}.png`,
  );
}

// Important file data
const inputMediaFile: Ref<HTMLLabelElement | null> = ref("");
const inputMediaFileLanguageSelect: Ref<HTMLLabelElement | null> = ref("en");
const inputSlidesFile: Ref<HTMLLabelElement | null> = ref("");
// Meta data
const inputTitle: Ref<HTMLLabelElement | null> = ref(null);
const inputCourse: Ref<HTMLLabelElement | null> = ref(null);
const inputCourseAcronym: Ref<HTMLLabelElement | null> = ref(null);
const inputSemester: Ref<HTMLLabelElement | null> = ref(null);
const inputLecturer: Ref<HTMLLabelElement | null> = ref(null);
const inputFaculty: Ref<HTMLLabelElement | null> = ref(null);
const inputFacultyAcronym: Ref<HTMLLabelElement | null> = ref(null);
const inputFacultyColor: Ref<HTMLLabelElement | null> = ref("#2F9B92");
const inputUniversity: Ref<HTMLLabelElement | null> = ref(null);
const inputUniversityAcronym: Ref<HTMLLabelElement | null> = ref(null);
// Permissions
const gridPermissionPublic: Ref<HTMLLabelElement | null> = ref(null);
const gridPermissionUniversityOnly: Ref<HTMLLabelElement | null> = ref(null);
const gridPermissionFacultyOnly: Ref<HTMLLabelElement | null> = ref(null);
const gridPermissionStudyTopicOnly: Ref<HTMLLabelElement | null> = ref(null);
const gridPermissionStudentsOnly: Ref<HTMLLabelElement | null> = ref(null);
// Licenses
const gridLicenseCC0: Ref<HTMLLabelElement | null> = ref(null);
const gridLicenseCCBY4: Ref<HTMLLabelElement | null> = ref(null);
const gridLicenseCCBYSA4: Ref<HTMLLabelElement | null> = ref(null);
// Tags for the media item, e.g. channel tags
const inputTags: Ref<HTMLLabelElement | null> = ref(null);
const inputAvatar: Ref<HTMLElement | null> = ref(null);

const handleMediaFileUpload = () => {
  loggerService.log("Media file added!");
};

const handleMediaFileLanguageSelect = () => {
  loggerService.log("Media file language selected!");
};

const handleSlidesFileUpload = () => {
  loggerService.log("Slides file added!");
};

onMounted(() => {
  inputTitle.value?.focus();
});

function wrapBooleanValue(element) {
  if (element.value === undefined || element.value === null) {
    return "false";
  } else {
    return element.value;
  }
}

function uploadMedia() {
  var bodyFormData = new FormData();
  bodyFormData.append("media", inputMediaFile.value.files[0]);
  bodyFormData.append("language", inputMediaFileLanguageSelect.value);
  bodyFormData.append("slides", inputSlidesFile.value.files[0]);
  bodyFormData.append("title", inputTitle.value);
  bodyFormData.append("course", inputCourse.value);
  bodyFormData.append("course_acronym", inputCourseAcronym.value);
  bodyFormData.append("semester", inputSemester.value);
  bodyFormData.append("lecturer", inputLecturer.value);
  bodyFormData.append("faculty", inputFaculty.value);
  bodyFormData.append("faculty_acronym", inputFacultyAcronym.value);
  bodyFormData.append("faculty_color", inputFacultyColor.value);
  bodyFormData.append("university", inputUniversity.value);
  bodyFormData.append("university_acronym", inputUniversityAcronym.value);

  bodyFormData.append("permission_public", wrapBooleanValue(gridPermissionPublic));
  bodyFormData.append("permission_university_only", wrapBooleanValue(gridPermissionUniversityOnly));
  bodyFormData.append("permission_faculty_only", wrapBooleanValue(gridPermissionFacultyOnly));
  bodyFormData.append("permission_study_topic_only", wrapBooleanValue(gridPermissionStudyTopicOnly));
  bodyFormData.append("permission_students_only", wrapBooleanValue(gridPermissionStudentsOnly));

  bodyFormData.append("license_cc_0", wrapBooleanValue(gridLicenseCC0));
  bodyFormData.append("license_cc_by_4", wrapBooleanValue(gridLicenseCCBY4));
  bodyFormData.append("license_cc_by_sa_4", wrapBooleanValue(gridLicenseCCBYSA4));

  bodyFormData.append("tags", inputTags.value);
  bodyFormData.append("thumbnails_lecturer", inputAvatar.value);

  loggerService.log(bodyFormData);
  return apiClient
    .post("/upload", bodyFormData, {
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
      loggerService.error("Error uploading media!");
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
</style>
