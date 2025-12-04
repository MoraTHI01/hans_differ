import {createRouter, createWebHistory} from "vue-router";
import {useAuthStore} from "@/stores/auth";
import {useEvalStore} from "@/stores/eval";

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: "/",
      name: "home",
      component: () => import("@/views/HomeView.vue"),
    },
    {
      path: "/channels",
      name: "channels",
      component: () => import("@/views/ChannelsView.vue"),
    },
    {
      path: "/history",
      name: "history",
      component: () => import("@/views/HistoryView.vue"),
    },
    {
      path: "/search-results",
      name: "SearchResults",
      component: () => import("@/views/SearchResultsView.vue"),
      props: (route) => ({query: route.query.q, fields: route.query.f}),
    },
    {
      path: "/channel",
      name: "Channel",
      component: () => import("@/views/ChannelView.vue"),
      props: (route) => ({uuid: route.query.uuid}),
    },
    {
      path: "/video-player",
      name: "VideoPlayer",
      component: () => import("@/views/VideoPlayerView.vue"),
      props: (route) => ({uuid: route.query.uuid}),
    },
    {
      path: "/contact",
      name: "contact",
      component: () => import("@/views/ContactView.vue"),
    },
    {
      path: "/legal",
      name: "legal",
      component: () => import("@/views/LegalView.vue"),
    },
    {
      path: "/dataprotection",
      name: "dataprotection",
      component: () => import("@/views/DataProtectionView.vue"),
    },
    {
      path: "/generalnotes",
      name: "generalnotes",
      component: () => import("@/views/GeneralNotesView.vue"),
    },
    {
      path: "/upload",
      name: "upload",
      component: () => import("@/views/UploadView.vue"),
    },
    {
      path: "/survey",
      name: "survey",
      component: () => import("@/views/SurveysView.vue"),
    },
    {
      path: "/announcement",
      name: "announcement",
      component: () => import("@/views/AnnouncementView.vue"),
    },
    {
      path: "/create",
      name: "create",
      component: () => import("@/views/CreateChannelView.vue"),
    },
    {
      path: "/login",
      name: "login",
      component: () => import("@/views/LoginView.vue"),
      props: (route) => ({username: route.query.username, password: route.query.password}),
    },
    {
      path: "/openapi",
      name: "openapi",
      // route level code-splitting
      // this generates a separate chunk (About.[hash].js) for this route
      // which is lazy-loaded when the route is visited.
      component: () => import("@/views/OpenApiView.vue"),
    },
    {
      path: "/airflow",
      name: "airflow",
      // route level code-splitting
      // this generates a separate chunk (About.[hash].js) for this route
      // which is lazy-loaded when the route is visited.
      component: () => import("@/views/AirflowView.vue"),
    },
    {
      path: "/upload/channel",
      name: "upload-channel",
      component: () => import("@/views/upload/UploadChannel.vue"),
    },
    {
      path: "/upload/overview",
      name: "upload-overview",
      component: () => import("@/views/upload/UploadOverview.vue"),
    },
    {
      path: "/upload/1",
      name: "upload-general",
      props: {
        language: "de",
      },
      component: () => import("@/views/upload/UploadGeneral.vue"),
    },
    {
      path: "/upload/2",
      name: "upload-general-secondary",
      props: {
        language: "en",
      },
      component: () => import("@/views/upload/UploadGeneral.vue"),
    },
    {
      path: "/upload/3",
      name: "upload-transcript",
      component: () => import("@/views/upload/UploadTranscript.vue"),
    },
    {
      path: "/upload/4",
      name: "upload-chapters",
      props: {
        language: "de",
      },
      component: () => import("@/views/upload/UploadChapters.vue"),
    },
    {
      path: "/upload/5",
      name: "upload-chapters-secondary",
      props: {
        language: "en",
      },
      component: () => import("@/views/upload/UploadChapters.vue"),
    },
    {
      path: "/statistics",
      name: "statistics",
      component: () => import("@/views/StatisticsView.vue"),
    },
    {
      path: "/:pathMatch(.*)*",
      name: "notfound",
      component: () => import("@/views/NotFoundView.vue"),
    },
  ],
});

router.beforeEach(async (to) => {
  // redirect to login page if not logged in and trying to access a restricted page
  const publicPages = ["/login", "/contact", "/legal", "/dataprotection"];
  const authRequired = !publicPages.includes(to.path);
  const auth = useAuthStore();
  auth.update();
  const ev = useEvalStore();
  ev.update();

  //console.log("Route to path: " + to.fullPath);
  if (to.fullPath.includes("login-oidc-success")) {
    //console.log("Router: OIDC login successful");
    return auth.handleOidc(to.fullPath);
  }

  if (to.fullPath.includes("logout-oidc-success")) {
    //console.log("Router: OIDC logout successful");
    auth.localLogout();
    return;
  }

  if (authRequired && !auth.getLoggedIn()) {
    auth.returnUrl = to.fullPath;
    //console.log("Router: Redirect to login");
    return "/login";
  }

  const lecturerPages = [
    "/openapi",
    "/airflow",
    "/create",
    "/upload",
    "/survey",
    "/upload/channel",
    "/upload/overview",
    "/upload/1",
    "/upload/2",
    "/upload/3",
    "/upload/4",
    "/upload/5",
  ];
  if (auth.role === "everybody" && lecturerPages.includes(to.path)) {
    auth.returnUrl = to.fullPath;
    //console.log("Router: Logout and redirect to login");
    auth.logout();
    return "/login";
  }
});

export default router;
