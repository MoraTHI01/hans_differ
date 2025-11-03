import {defineStore} from "pinia";
import {apiClient} from "@/common/apiClient";
import type {ChannelItem} from "@/data/ChannelItem";
import {RemoteData} from "@/data/RemoteData";
import {LoggerService} from "@/common/loggerService";

const loggerService = new LoggerService();
export const useQuestionStore = defineStore({
  id: "questionStore",
  state: () => ({
    // Key is the uuid of the meta data
    currentDifficulty: "easy",
  }),
  getters: {
    getDifficulty: (state) => state.currentDifficulty,
  },
  actions: {
    setDifficulty(value: string[]) {
      this.currentDifficulty = value;
    },
  },
});
