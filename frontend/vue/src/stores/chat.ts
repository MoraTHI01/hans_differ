// store.ts
import {defineStore} from "pinia";
import {LoggerService} from "@/common/loggerService";
import {useAuthStore} from "@/stores/auth";

const loggerService = new LoggerService();

// Define the store
export const useChatStore = defineStore("chat", {
  state: () => ({
    // Media chat settings
    switchContext: true,
    switchCitation: true,
    switchSelectedContext: false,
    switchVision: false,
    switchVisionSurroundingSlides: false,
    switchVisionSnapshot: false,
    switchTutor: true,
    switchReasoning: false,
    // Channel chat settings
    switchChannelContext: true,
    switchChannelCitation: true,
    // General chat settings
    switchTranslation: false,
    translationEnabled: false,
    settingsOpen: false,
  }),
  // Define getters to access computed values based on the state
  getters: {
    // Media chat getters
    isSwitchContextEnabled: (state) => {
      return state.switchContext;
    },
    isSwitchCitationEnabled: (state) => {
      return state.switchCitation;
    },
    isSwitchSelectedContextEnabled: (state) => {
      return state.switchSelectedContext;
    },
    isSwitchVisionEnabled: (state) => {
      return state.switchVision;
    },
    isSwitchVisionSurroundingSlidesEnabled: (state) => {
      return state.switchVisionSurroundingSlides;
    },
    isSwitchVisionSnapshotEnabled: (state) => {
      return state.switchVisionSnapshot;
    },
    isSwitchTutorEnabled: (state) => {
      return state.switchTutor;
    },
    isSwitchReasoningEnabled: (state) => {
      return state.switchReasoning;
    },
    // Channel chat getters
    isSwitchChannelContextEnabled: (state) => {
      return state.switchChannelContext;
    },
    isSwitchChannelCitationEnabled: (state) => {
      return state.switchChannelCitation;
    },
    // General chat getters
    isSwitchTranslationEnabled: (state) => {
      return state.switchTranslation;
    },
    isTranslationEnabled: (state) => {
      return state.translationEnabled;
    },
    isSettingsOpen: (state) => {
      return state.settingsOpen;
    },
  },
  // Define actions that can modify the state
  actions: {
    // Media chat actions
    toggleSwitchContext(value: boolean) {
      this.switchContext = value;
      // If the main switch is turned off, also turn off the dependent switch
      if (!value) {
        this.switchCitation = false;
      }
    },
    toggleSwitchCitation(value: boolean) {
      if (this.switchContext) {
        this.switchCitation = value;
      }
    },
    toggleSwitchSelectedContext(value: boolean) {
      this.switchContext = false;
      this.switchSelectedContext = value;
    },
    toggleSwitchVision(value: boolean) {
      this.switchVision = value;
      if (!value) {
        this.switchVisionSurroundingSlides = false;
      }
    },
    toggleSwitchVisionSurroundingSlides(value: boolean) {
      if (this.switchVision) {
        this.switchVisionSurroundingSlides = value;
      }
    },
    toggleSwitchVisionSnapshot(value: boolean) {
      this.switchVisionSnapshot = value;
    },
    toggleSwitchTutor(value: boolean) {
      this.switchTutor = value;
    },
    toggleSwitchReasoning(value: boolean) {
      this.switchVision = false;
      this.switchVisionSnapshot = false;
      this.switchReasoning = value;
    },
    // Channel chat actions
    toggleSwitchChannelContext(value: boolean) {
      this.switchChannelContext = value;
      // If the main switch is turned off, also turn off the dependent switch
      if (!value) {
        this.switchChannelCitation = false;
      }
    },
    toggleSwitchChannelCitation(value: boolean) {
      if (this.switchChannelContext) {
        this.switchChannelCitation = value;
      }
    },
    // General chat actions
    toggleSwitchTranslation(value: boolean) {
      this.switchTranslation = value;
    },
    toggleTranslationEnabled(value: boolean) {
      this.translationEnabled = value;
    },
    toggleSettingsOpen(value: boolean) {
      this.settingsOpen = value;
    },
    loadChatSettings() {
      loggerService.log("loadChatSettings");
      // Store messages with uuid of user
      const authStore = useAuthStore();
      const user_id = authStore.getUserId();
      const serializedSettings = localStorage.getItem("hans_chatSettings_" + user_id);
      if (serializedSettings) {
        const jsonObject = JSON.parse(serializedSettings);
        // Media chat settings
        this.switchContext = jsonObject.switchContext;
        this.switchCitation = jsonObject.switchCitation;
        this.switchSelectedContext = jsonObject.switchSelectedContext;
        this.switchVision = jsonObject.switchVision;
        this.switchVisionSurroundingSlides = jsonObject.switchVisionSurroundingSlides;
        this.switchVisionSnapshot = jsonObject.switchVisionSnapshot;
        this.switchTutor = jsonObject.switchTutor;
        this.switchReasoning = jsonObject.switchReasoning;
        // Channel chat settings
        this.switchChannelContext = jsonObject.switchChannelContext;
        this.switchChannelCitation = jsonObject.switchChannelCitation;
        // General chat settings
        this.switchTranslation = jsonObject.switchTranslation;
        this.translationEnabled = jsonObject.translationEnabled;
        loggerService.log("loadChatSettings:Loaded");
      }
    },
    storeChatSettings() {
      loggerService.log("storeChatSettings");
      const settings = {
        switchContext: this.switchContext,
        switchCitation: this.switchCitation,
        switchSelectedContext: this.switchSelectedContext,
        switchVision: this.switchVision,
        switchVisionSurroundingSlides: this.switchVisionSurroundingSlides,
        switchVisionSnapshot: this.switchVisionSnapshot,
        switchTutor: this.switchTutor,
        switchReasoning: this.switchReasoning,
        switchChannelContext: this.switchChannelContext,
        switchChannelCitation: this.switchChannelCitation,
        switchTranslation: this.switchTranslation,
        translationEnabled: this.translationEnabled,
      };
      const serializableSettings = JSON.stringify(settings);
      // Store messages with uuid of user
      const authStore = useAuthStore();
      const user_id = authStore.getUserId();
      localStorage.setItem("hans_chatSettings_" + user_id, serializableSettings);
      loggerService.log("storeChatSettings:Stored");
    },
  },
});
