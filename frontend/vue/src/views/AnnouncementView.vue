<template>
  <HeaderRow />
  <LogoAndSearchbarRow
    :placeholder="t('AnnouncementView.searchplaceholder')"
    :showSearch="false"
    :showProgress="false"
  />
  <div class="main-container">
    <MenuBanner :menutext="t('AnnouncementView.menutext')" />
    <div class="row sub-container">
      <div class="left col-8 border">
        <form
          @submit.prevent="submitForm"
          class="d-grid gap-2 needs-validation"
          method="POST"
          id="uploadForm"
          enctype="multipart/form-data"
          accept-charset="utf-8"
          novalidate
        >
          <!-- Start Date -->
          <div class="mb-3">
            <label for="startDate" class="form-label">Start Date</label>
            <input type="date" class="form-control" id="startDate" v-model="form.start_date" required />
            <div class="invalid-feedback">Please provide a valid start date.</div>
          </div>

          <!-- End Date -->
          <div class="mb-3">
            <label for="endDate" class="form-label">End Date</label>
            <input type="date" class="form-control" id="endDate" v-model="form.end_date" required />
            <div class="invalid-feedback">Please provide a valid end date.</div>
          </div>

          <!-- UUID (auto-generated and readonly) -->
          <div class="mb-3">
            <label for="uuid" class="form-label">UUID</label>
            <input type="text" class="form-control" id="uuid" v-model="form.uuid" />
          </div>

          <!-- Status -->
          <div class="mb-3">
            <label for="status" class="form-label">Status</label>
            <select class="form-select" id="status" v-model="form.status" required>
              <option value="">Select status</option>
              <option value="active">Active</option>
              <option value="inactive">Inactive</option>
            </select>
          </div>

          <!-- English Announcement -->
          <div class="mb-3">
            <h4>English Announcement</h4>
            <div class="mb-3">
              <label for="enTitle" class="form-label">Title</label>
              <input type="text" class="form-control" id="enTitle" v-model="form.title_en" required />
            </div>

            <div class="mb-3">
              <label for="enText" class="form-label">Text</label>
              <textarea class="form-control" id="enText" v-model="form.text_en" rows="2" required></textarea>
            </div>
          </div>

          <!-- German Announcement -->
          <div class="mb-3">
            <h4>German Announcement</h4>
            <div class="mb-3">
              <label for="deTitle" class="form-label">Title</label>
              <input type="text" class="form-control" id="deTitle" v-model="form.title_de" required />
            </div>

            <div class="mb-3">
              <label for="deText" class="form-label">Text</label>
              <textarea class="form-control" id="deText" v-model="form.text_de" rows="2" required></textarea>
            </div>
          </div>

          <!-- Submit Button -->
          <button type="submit" class="btn btn-success mt-4" :disabled="submitDisabled">Submit</button>
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
import {reactive, ref, onMounted} from "vue";
import {useI18n} from "vue-i18n";
import {LoggerService} from "@/common/loggerService";

const loggerService = new LoggerService();
const {t} = useI18n({useScope: "global"});

// Define the types for our form data
interface CustomFormData extends FormData {
  start_date: string; // The start date as string (in format YYYY-MM-DD)
  end_date: string; // The end date as string (in format YYYY-MM-DD)
  uuid: string; // Unique identifier for the form (UUID format)
  status: string; // Announcement status (e.g., 'active', 'inactive')
  title_de: string;
  text_de: string;
  title_en: string;
  text_en: string;
}

// Generate UUID using crypto.randomUUID
const generateUUID = () => crypto.randomUUID();

// Initialize form with reactive state and TypeScript types
const form = ref<CustomFormData>({
  start_date: "",
  end_date: "",
  uuid: "", // Will be auto-generated on page load
  status: "",
  title_de: "",
  text_de: "",
  title_en: "",
  text_en: "",
});

const submitDisabled = ref(false);

// Submit form to backend
const submitForm = () => {
  submitDisabled.value = true;
  return apiClient
    .post("/announcement", form.value, {
      headers: {
        "Content-type": "multipart/form-data",
        "Access-Control-Allow-Origin": "*",
      },
    })
    .then((response) => {
      submitDisabled.value = false;
      if (response.status === 200) {
        //redirect to default to home page
        router.push("/");
      }
    })
    .catch((error) => {
      submitDisabled.value = false;
      loggerService.error("Error uploading survey!");
      loggerService.error(error);
    });
};

onMounted(() => {
  form.value.uuid = generateUUID();
});
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
