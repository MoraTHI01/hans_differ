import {defineStore} from "pinia";
import {v4} from "uuid";
import {matomo_clicktracking} from "@/common/matomo_utils";
import {LoggerService} from "@/common/loggerService";
import {useAuthStore} from "@/stores/auth";

const loggerService = new LoggerService();

export const useEvalStore = defineStore({
  id: "evalStore",
  state: () => ({
    // Is evaluation session active
    evalActive: false,
    // Id used for evaluation session tracking with matomo
    evalId: null as string | null,
  }),
  getters: {
    getEvalActive: (state) => () => {
      return state.evalActive;
    },
    getEvalId: (state) => () => {
      return state.evalId;
    },
  },
  actions: {
    storeEvalActiveInStorage(value: boolean) {
      localStorage.setItem("evalSession", JSON.stringify({active: value}));
    },
    loadEvalActiveFromStorage() {
      const tokenData = localStorage.getItem("evalSession");
      if (tokenData === undefined || tokenData === null) {
        return null;
      }
      const value = JSON.parse(tokenData).active;
      return value;
    },
    storeEvalIdInStorage(value: string) {
      localStorage.setItem("evalId", JSON.stringify({id: value}));
    },
    loadEvalIdFromStorage() {
      const tokenData = localStorage.getItem("evalId");
      if (tokenData === undefined || tokenData === null) {
        return null;
      }
      const value = JSON.parse(tokenData).id;
      return value;
    },
    update() {
      const updEvalActive = this.loadEvalActiveFromStorage();
      const updEvalId = this.loadEvalIdFromStorage();
      if (updEvalActive !== undefined && updEvalActive !== null && updEvalId !== undefined && updEvalId !== null) {
        this.evalActive = updEvalActive;
        this.evalId = updEvalId;
        this.storeEvalActiveInStorage(this.evalActive);
        this.storeEvalIdInStorage(this.evalId);
      }
    },
    setEvalMode(activate: boolean) {
      this.evalActive = activate;
      this.storeEvalActiveInStorage(this.evalActive);
      if (this.evalActive) {
        const auth = useAuthStore();
        auth.update();
        this.evalId = v4();
        matomo_clicktracking("eval", this.evalId);
        matomo_clicktracking("userRole", auth.getRole());
      } else {
        this.evalId = "";
        matomo_clicktracking("eval", "off");
      }
      this.storeEvalIdInStorage(this.evalId);
      this.printStatus();
    },
    printStatus() {
      loggerService.log("evaluationId: " + this.evalId);
    },
  },
});
