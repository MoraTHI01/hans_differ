<template>
  <div>
    <!-- Switch Input -->
    <div class="form-check form-switch">
      <input
        class="form-check-input"
        type="checkbox"
        :checked="modelValue && isEnabled"
        :disabled="!isEnabled"
        @change="updateStatus($event.target.checked)"
        :id="switchId"
      />
      <label class="form-check-label" :for="switchId" @click="toggleSwitch">
        {{ label }}
      </label>
    </div>

    <!-- Description Text Area (4 lines) -->
    <div class="mt-3">
      <textarea
        :id="descriptionId"
        class="form-control switch-description"
        rows="4"
        :value="description"
        disabled
        readonly
      ></textarea>
    </div>
  </div>
</template>

<script setup lang="ts">
import {defineProps, defineEmits, watch} from "vue";
import {matomo_clicktracking} from "@/common/matomo_utils";

// Define props with TypeScript types
const props = defineProps<{
  modelValue: boolean; // Prop for the switch state
  label: string; // Label for the switch
  id?: string; // Optional ID for the switch
  isEnabled: boolean; // Control whether the switch is enabled
  description: string; // Description text for the switch
  trackingMessageOn?: string; // The tracking message when ON
  trackingMessageOff?: string; // The tracking message when OFF
}>();

// Emits for two-way binding
const emit = defineEmits<{
  (event: "update:modelValue", value: boolean): void; // Define the emit event
}>();

const toggleSwitch = () => {
  // Trigger checkbox click
  props.modelValue = !props.modelValue;
  updateStatus(props.modelValue);
};

// Watch for changes in `isEnabled` and set status to false if disabled
watch(
  () => props.isEnabled,
  (newValue) => {
    if (!newValue) {
      emit("update:modelValue", false); // Disable switch if `isEnabled` is false
    }
  },
);

// Method to update the status and emit the event
const updateStatus = (newValue: boolean) => {
  emit("update:modelValue", newValue); // Emit the updated value to the parent
  if (newValue) {
    performAction(props.trackingMessageOn); // Call internal method if switch is turned ON
  } else {
    performAction(props.trackingMessageOff); // Call internal method if switch is turned OFF
  }
};

// Internal method to perform an action with the tracking message
const performAction = (message: string) => {
  matomo_clicktracking("click_button", message);
};
</script>
<style scoped>
.switch-description {
  width: 34vh;
  height: auto;
  resize: none;
  background-color: var(--hans-light-blue);
}
</style>
