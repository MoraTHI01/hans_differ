import {defineStore} from "pinia";
import {apiClient} from "@/common/apiClient";
import type {ChannelItem} from "@/data/ChannelItem";
import {RemoteData} from "@/data/RemoteData";
import {LoggerService} from "@/common/loggerService";

const loggerService = new LoggerService();
export const useLayoutStore = defineStore({
  id: "layoutStore",
  state: () => ({
    // Key is the uuid of the meta data
    currentLayout: "combined",
  }),
  getters: {
    getLayout: (state) => state.currentLayout,
  },
  actions: {
    setLayout(value: string[]) {
      this.currentLayout = value;
    },
  },
});
