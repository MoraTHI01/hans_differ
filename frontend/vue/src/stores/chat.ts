// store.ts
import {defineStore} from "pinia";
import {LoggerService} from "@/common/loggerService";

const loggerService = new LoggerService();

// Define the store
export const useChatStore = defineStore("chat", {
  state: () => ({
    switchContext: true,
    switchCitation: true,
    switchSelectedContext: false,
    switchVision: false,
    switchVisionSurroundingSlides: false,
    switchVisionSnapshot: false,
    switchTutor: true,
    switchTranslation: false,
    translationEnabled: false,
    settingsOpen: false,
  }),
  // Define getters to access computed values based on the state
  getters: {
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
      const serializedSettings = localStorage.getItem("hans_chatSettings");
      if (serializedSettings) {
        const jsonObject = JSON.parse(serializedSettings);
        this.switchContext = jsonObject.switchContext;
        this.switchCitation = jsonObject.switchCitation;
        this.switchSelectedContext = jsonObject.switchSelectedContext;
        this.switchVision = jsonObject.switchVision;
        this.switchVisionSurroundingSlides = jsonObject.switchVisionSurroundingSlides;
        this.switchVisionSnapshot = jsonObject.switchVisionSnapshot;
        this.switchTutor = jsonObject.switchTutor;
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
        switchTranslation: this.switchTranslation,
        translationEnabled: this.translationEnabled,
      };
      const serializableSettings = JSON.stringify(settings);
      localStorage.setItem("hans_chatSettings", serializableSettings);
      loggerService.log("storeChatSettings:Stored");
    },
  },
});
