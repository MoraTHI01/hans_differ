const host_url = import.meta.env.VITE_HANS_BACKEND_HOST_URL;

var _paq = (window._paq = window._paq || []);
/* tracker methods like "setCustomDimension" should be called before "trackPageView" */
// _paq.push(['trackPageView']);
_paq.push(["enableLinkTracking"]);
_paq.push(["requireConsent"]);
_paq.push(["requireCookieConsent"]);
(function () {
  // var u="//localhost:8001/";
  // var u="//hans-backend-webserver:8089/matomo-analytics/";
  var u = "//" + host_url + "/matomo-analytics/";
  _paq.push(["setTrackerUrl", u + "matomo.php"]);
  _paq.push(["setSiteId", "1"]);
  var d = document,
    g = d.createElement("script"),
    s = d.getElementsByTagName("script")[0];
  g.async = true;
  g.src = u + "matomo.js";
  s.parentNode.insertBefore(g, s);
})();
