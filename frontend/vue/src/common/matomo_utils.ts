import {useRoute} from "vue-router";
import {useEvalStore} from "@/stores/eval";
import {useAuthStore} from "@/stores/auth";
import {LoggerService} from "@/common/loggerService";

const loggerService = new LoggerService();

function trackEvalId() {
  let evalId = "none";
  if (useEvalStore().evalActive) {
    evalId = useEvalStore().getEvalId();
    loggerService.log("setCustomVariableEvalId");
    _paq.push([
      "setCustomVariable",
      // Index, the number from 1 to 5 where this custom variable name is stored
      1,
      // Name, the name of the variable, for example: Gender, VisitorType
      "evalId",
      // Value, for example: "Male", "Female" or "new", "engaged", "customer"
      evalId,
      // Scope of the custom variable, "visit" means the custom variable applies to the current visit
      "visit",
    ]);
  }
  return evalId;
}

function trackUser() {
  const uName = useAuthStore().getUsername();
  loggerService.log("setCustomVariableUser");
  _paq.push([
    "setCustomVariable",
    // Index, the number from 1 to 5 where this custom variable name is stored
    3,
    // Name, the name of the variable, for example: Gender, VisitorType
    "user",
    // Value, for example: "Male", "Female" or "new", "engaged", "customer"
    uName,
    // Scope of the custom variable, "visit" means the custom variable applies to the current visit
    "visit",
  ]);
  return uName;
}

function trackRole() {
  const uRole = useAuthStore().getRole();
  loggerService.log("setCustomVariableRole");
  _paq.push([
    "setCustomVariable",
    // Index, the number from 1 to 5 where this custom variable name is stored
    2,
    // Name, the name of the variable, for example: Gender, VisitorType
    "role",
    // Value, for example: "Male", "Female" or "new", "engaged", "customer"
    uRole,
    // Scope of the custom variable, "visit" means the custom variable applies to the current visit
    "visit",
  ]);
  return uRole;
}

export function matomo_trackpageview(parameter = "") {
  const evalId = trackEvalId();
  const uName = trackUser();
  const uRole = trackRole();
  let finalParameter = "";
  if (parameter === "") {
    finalParameter = "?evalId=" + evalId + "&user=" + uName + "&role=" + uRole;
  } else {
    finalParameter = parameter + "&evalId=" + evalId + "&user=" + uName + "&role=" + uRole;
  }
  _paq.push(["setCustomUrl", useRoute().path + finalParameter]);
  _paq.push(["trackPageView"]);
}

export function matomo_clicktracking(click_event, form_description) {
  const evalId = trackEvalId();
  const uName = trackUser();
  const uRole = trackRole();
  _paq.push(["trackEvent", click_event, form_description]);
}

export function matomo_searchtracking(searchquery, category_list, result_count) {
  const evalId = trackEvalId();
  const uName = trackUser();
  const uRole = trackRole();
  _paq.push([
    "trackSiteSearch",
    // Search keyword searched for
    searchquery,
    // Search category selected in your search engine. If you do not need this, set to false
    category_list,
    // Number of results on the Search results page. Zero indicates a 'No Result Search Keyword'. Set to false if you don't know
    result_count,
  ]);
}
