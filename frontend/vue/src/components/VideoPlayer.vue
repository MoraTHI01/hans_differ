<template>
  <video
    id="videoPlayer"
    ref="videoPlayer"
    class="video-js vjs-16-9 vjs-fluid"
    controls
    preload="auto"
    width="640"
    height="360"
    data-setup='{ "playbackRates": [0.25, 0.5, 0.75, 1, 1.25, 1.5, 1.75, 2] }'
  >
    <p class="vjs-no-js">
      {{ t("VideoPlayer.text") }}
      <a href="https://videojs.com/html5-video-support/" target="_blank">{{ t("VideoPlayer.link") }}</a>
    </p>
  </video>
  <VideoPlayerInfo ref="videoPlayerInfo"></VideoPlayerInfo>
</template>

<script setup lang="ts">
import {PlayEvent, PauseEvent, SetPositionEvent} from "@/common/events";
import type {Emitter, EventType} from "mitt";
import videojs from "video.js";
import {h, onBeforeUnmount, inject, ref, render, onMounted, onUnmounted, watch} from "vue";
import {matomo_clicktracking} from "@/common/matomo_utils";
import {useI18n} from "vue-i18n";
import {LoggerService} from "@/common/loggerService";
import {useHistoryStore} from "@/stores/history";
import VideoPlayerInfo from "@/components/VideoPlayerInfo.vue";
import VideoPlayerSettings from "@/components/VideoPlayerSettings.vue";

const loggerService = new LoggerService();
const {t, locale} = useI18n({useScope: "global"});
const props = defineProps(["url", "subtitle_de", "subtitle_en", "language", "uuid"]);

const videoPlayer = ref();
const videoPlayerInfo = ref(null);
const eventBus: Emitter<Record<EventType, unknown>> = inject("eventBus")!;

let eventSeek = false;
let seeking = false;
let settingsMenuShown = false;
let streamType = "dash";

const historyStore = useHistoryStore();

onMounted(() => {
  loadVideo();
  eventBus.on("setPositionEvent", (event: SetPositionEvent) => {
    matomo_clicktracking("videoplayer_click", "set_position: " + event.position);
    if (event.origin !== "video") {
      eventSeek = true;
      videojs("videoPlayer").currentTime(event.position);
    }
  });
  eventBus.on("play", (event: PlayEvent) => {
    if (event.origin !== "video") {
      videojs("videoPlayer").play();
    }
  });
  eventBus.on("pause", (event: PauseEvent) => {
    if (event.origin !== "video") {
      videojs("videoPlayer").pause();
    }
  });
});

onBeforeUnmount(() => {
  historyStore.addHistory(props.uuid, videojs("videoPlayer").currentTime(), videojs("videoPlayer").duration());
});

onUnmounted(() => videojs("videoPlayer").dispose());

const emit = defineEmits<{
  (e: "videometadata", data: {duration: number}): void;
  (e: "pause"): void;
  (e: "play"): void;
}>();

/**
 * Configure the video player UI for the muted button
 */
function handleMuted(player) {
  if (player.muted()) {
    const muteButton = player.controlBar.volumePanel.muteToggle;
    muteButton.controlText(t("VideoPlayer.controlBarUnmute") + " (m)");
  } else {
    const muteButton = player.controlBar.volumePanel.muteToggle;
    muteButton.controlText(t("VideoPlayer.controlBarMute") + " (m)");
  }
}

/**
 * Add custom controls to the video player UI
 */
function addCustomControlsToPlayerUI(player) {
  // Modify controlBar
  // Add the custom buttons before the fullscreen button
  const fullscreenButton = player.controlBar.fullscreenToggle;
  let fullscreenButtonIndex = player.controlBar.children().indexOf(fullscreenButton);

  // Add Settings menu
  const settingsMenu = player.controlBar.addChild(
    "Menu",
    {
      id: "settingsMenu",
      className: "vjs-settings-menu vjs-menu-button vjs-menu-button-popup vjs-control vjs-button",
    },
    fullscreenButtonIndex,
  );
  fullscreenButtonIndex = player.controlBar.children().indexOf(fullscreenButton);
  loggerService.log("addCustomControlsToPlayerUI:SettingsMenuDiv added!");

  // Create our button's DOM Component
  const settingsMenuDom = settingsMenu.el();
  settingsMenuDom.innerHTML =
    `
    <button id="playerSettingsMenuBtn" class="vjs-settings-menu vjs-menu-button vjs-menu-button-popup vjs-button" type="button" aria-disabled="false" title="` +
    t("VideoPlayer.controlBarSettingsMenu") +
    `" aria-haspopup="true" aria-expanded="false">
      <span class="vjs-icon-placeholder" aria-hidden="true">
      <img src="/bootstrap-icons/gear-fill.svg" alt="info" class="img-fluid img-settings" style="filter: invert(1)" />
      </span>
      <span id="playerSettingsMenuBtnSpan" class="vjs-control-text" aria-live="polite">` +
    t("VideoPlayer.controlBarSettingsMenu") +
    `</span>
    </button>
  `;

  const toggleSettingsMenu = (show: boolean) => {
    settingsMenuShown = show;
    const playerSettingsMenuBtn = document.getElementById("playerSettingsMenuBtn");
    const videoPlayerSettingsContainer = document.getElementById("videoPlayerSettingsContainer");
    if (show === true) {
      if (playerSettingsMenuBtn) {
        playerSettingsMenuBtn.setAttribute("aria-expanded", "true");
      }
      if (videoPlayerSettingsContainer) {
        videoPlayerSettingsContainer.classList.add("vjs-lock-showing");
        videoPlayerSettingsContainer.classList.remove("vjs-hidden");
      }
    } else {
      if (playerSettingsMenuBtn) {
        playerSettingsMenuBtn.setAttribute("aria-expanded", "false");
      }
      if (videoPlayerSettingsContainer) {
        videoPlayerSettingsContainer.classList.add("vjs-hidden");
        videoPlayerSettingsContainer.classList.remove("vjs-lock-showing");
      }
    }
  };

  // Show/hide custom menu on mouse enter/leave
  settingsMenu.on("mouseenter", () => {
    loggerService.log("SettingsMenuMouseEnter");
    toggleSettingsMenu(true);
    settingsMenu.addClass("vjs-hover");
  });

  settingsMenu.on("mouseleave", () => {
    loggerService.log("SettingsMenuMouseLeave");
    toggleSettingsMenu(false);
    settingsMenu.removeClass("vjs-hover");
  });

  // Create VNode from VideoPlayerSettings component
  const settingsMenuVNode = h(VideoPlayerSettings, {
    playerInstance: player,
    playerInfoInstanceRef: videoPlayerInfo,
    t: t,
    locale: locale,
    streamType: streamType,
  });
  // Render the component into the container
  render(settingsMenuVNode, settingsMenuDom);
  // Toggle custom menu on mouse down
  document.getElementById("playerSettingsMenuBtn")?.addEventListener("mousedown", () => {
    loggerService.log("SettingsMenuMouseDown");
    if (settingsMenuShown === false) {
      toggleSettingsMenu(true);
    } else {
      toggleSettingsMenu(false);
    }
  });
}

/**
 * Configure the video player UI
 */
function configurePlayerUI(player) {
  // Modify controlBar button hover text
  loggerService.log("configurePlayerUI");

  // Get the settingsMenu button
  const playerSettingsMenuBtn = document.getElementById("playerSettingsMenuBtn");
  if (playerSettingsMenuBtn) playerSettingsMenuBtn.title = t("VideoPlayer.controlBarSettingsMenu");
  const playerSettingsMenuBtnSpan = document.getElementById("playerSettingsMenuBtnSpan");
  if (playerSettingsMenuBtnSpan) playerSettingsMenuBtnSpan.innerHTML = t("VideoPlayer.controlBarSettingsMenu");

  // Get the Fullscreen button component
  const fullscreenButton = player.controlBar.fullscreenToggle;
  // Set the new hover title
  fullscreenButton.controlText(t("VideoPlayer.controlBarFullscreenToggle") + " (f)");

  // Get the CC button component
  const ccButton = player.controlBar.subsCapsButton;
  // Set the new hover title for CC button
  ccButton.controlText(t("VideoPlayer.controlBarClosedCaptionsButton") + " (c)");

  // Get the skip forward button component
  const fwdButton = player.controlBar.skipForward;
  // Set the new hover title for skip forward button
  fwdButton.controlText(t("VideoPlayer.controlBarSkipForward"));

  // Get the skip backward button component
  const bckButton = player.controlBar.skipBackward;
  // Set the new hover title for skip backward button
  bckButton.controlText(t("VideoPlayer.controlBarSkipBackward"));

  // Handle muted button
  handleMuted(player);

  // https://github.com/ctd1500/videojs-hotkeys
  // https://github.com/ctd1500/videojs-hotkeys/blob/master/example.html
  player.hotkeys({
    volumeStep: 0.1,
    // VLC seek behavior would be seeking default to 5.
    // Now seeking to 10 as other streaming services
    seekStep: function (e) {
      if (e.ctrlKey && e.altKey) {
        return 10 * 60;
      } else if (e.ctrlKey) {
        return 60;
      } else if (e.altKey) {
        return 10;
      } else {
        return 10;
      }
    },
    enableMute: true,
    enableVolumeScroll: true,
    enableHoverScroll: false,
    enableFullscreen: true,
    enableNumbers: true,
    enableJogStyle: false,
    alwaysCaptureHotkeys: false,
    captureDocumentHotkeys: false,
    documentHotkeysFocusElementFilter: (e) => {
      loggerService.log("documentHotkeysFocusElementFilter");
      loggerService.log(e.tagName);
      return e.tagName.toLowerCase() === "video";
    },
    enableModifiersForNumbers: false,
    enableInactiveFocus: false,
    skipInitialFocus: false,
    // https://gist.github.com/kyranjamie/b9fca0c2cb82588bd492b6ee59ed239b
    // https://developer.mozilla.org/en-US/docs/Web/API/UI_Events
    playPauseKey: function (e) {
      // Space bar or K or MediaPlayPause
      return e.which === 32 || e.which === 75 || e.which === 179;
    },
    rewindKey: function (e) {
      // Left Arrow or MediaRewind
      return e.which === 37 || e.which === 177;
    },
    forwardKey: function (e) {
      // Right Arrow or MediaForward
      return e.which === 39 || e.which === 176;
    },
    volumeUpKey: function (e) {
      // Up Arrow
      return e.which === 38;
    },
    volumeDownKey: function (e) {
      // Down Arrow
      return e.which === 40;
    },
    muteKey: function (e) {
      // M key
      return e.which === 77;
    },
    // Enhance existing simple hotkey with a complex hotkey
    fullscreenKey: function (e) {
      // fullscreen with the F key or Ctrl+Enter
      return e.which === 70 || (e.ctrlKey && e.which === 13);
    },
    // Custom Keys
    customKeys: {
      // Add new simple hotkey
      simpleKey: {
        key: function (e) {
          // Toggle something with S Key
          return e.which === 83;
        },
        handler: function (player, options, e) {
          // Example
          if (player.paused()) {
            player.play();
          } else {
            player.pause();
          }
        },
      },
      // Add new complex hotkey
      complexKey: {
        key: function (e) {
          // Toggle something with CTRL + D Key
          return e.ctrlKey && e.which === 68;
        },
        handler: function (player, options, event) {
          // Example
          if (options.enableMute) {
            player.muted(!player.muted());
          }
        },
      },
      // Override number keys example from https://github.com/ctd1500/videojs-hotkeys/pull/36
      numbersKey: {
        key: function (event) {
          // Override number keys
          return (event.which > 47 && event.which < 59) || (event.which > 95 && event.which < 106);
        },
        handler: function (player, options, event) {
          // Do not handle if enableModifiersForNumbers set to false and keys are Ctrl, Cmd or Alt
          if (options.enableModifiersForNumbers || !(event.metaKey || event.ctrlKey || event.altKey)) {
            var sub = 48;
            if (event.which > 95) {
              sub = 96;
            }
            var number = event.which - sub;
            player.currentTime(player.duration() * number * 0.1);
          }
        },
      },
    },
  });
}

// Watch the locale to register for language changes and switch player UI
watch(locale, async (newText) => {
  configurePlayerUI(videoPlayer.value);
});

/**
 * Loads the video player and registers event hooks for:
 * - metadata loading to provide the total duration to other components
 * - seeking and timeupdate events for providing separate events for when a video is playing and
 *   when it is seeked either automatically via events or manually by the user
 * - Play and pause events for tracking video play states
 */
function loadVideo() {
  // See https://videojs.com/guides/options/#nativeaudiotracks
  // and https://github.com/videojs/http-streaming#overridenative
  const player = (videoPlayer.value = videojs("videoPlayer", {
    html5: {
      vhs: {
        overrideNative: !videojs.browser.IS_SAFARI,
      },
      nativeAudioTracks: false,
      nativeVideoTracks: false,
    },
    enableSmoothSeeking: true,
    liveui: true,
    responsive: true,
    controlBar: {
      skipButtons: {
        forward: 10,
        backward: 10,
      },
    },
  }));
  videoPlayer.value.one("loadedmetadata", () =>
    emit("videometadata", {
      duration: videoPlayer.value.duration(),
    }),
  );
  player.ready(function () {
    let vtype = "application/dash+xml";
    if (props.url.includes(".m3u8") === true) {
      vtype = "application/x-mpegURL";
      streamType = "hls";
    }
    player.src({
      src: props.url,
      type: vtype,
    });

    // Add subtitles, currently only available for the spoken language
    // see https://videojs.com/guides/text-tracks
    player.addRemoteTextTrack(
      {
        src: props.subtitle_de,
        srclang: "de",
      },
      false,
    );

    player.addRemoteTextTrack(
      {
        src: props.subtitle_en,
        srclang: "en",
      },
      false,
    );

    // Add custom controls to the video player UI
    addCustomControlsToPlayerUI(player);

    // Configure player UI translations, hotkeys and tooltips
    configurePlayerUI(player);

    // Handle and register events
    player.on("seeking", () => (seeking = true));
    player.on("seeked", () => {
      seeking = false;
      // Only disables eventSeek when the current seek is complete since an
      // event may cause more than one seeking event
      // Since event seeks are very short this shouldn't interfere with manual seeking
      eventSeek = false;
    });
    player.on("timeupdate", () => {
      if (seeking) {
        // Prevents sending time updates caused by the video seeking due to an event from another component
        if (eventSeek) {
          return;
        }

        // Send regular position change events on manual seeking
        eventBus.emit("setPositionEvent", new SetPositionEvent(player.currentTime(), "video"));
      } else if (!player.paused()) {
        // If the video was not seeked manually through user interaction or event emit a playing event
        eventBus.emit("videoPlaying", player.currentTime());
        // Update stats only if the modal stats info window is displayed
        if (videoPlayerInfo.value && videoPlayerInfo.value.isPlayerInfoDisplayed()) {
          videoPlayerInfo.value.updateStats(player.tech().vhs.stats);
        }
      }
    });
    player.on("play", () => {
      matomo_clicktracking("videoplayer_click", "play");
      // Get the Play/Pause button component
      const playPauseButton = player.controlBar.playToggle;
      // Set the new hover title for Play/Pause button
      playPauseButton.controlText(t("VideoPlayer.controlBarPause") + " (k)");
      emit("play");
    });
    player.on("pause", () => {
      matomo_clicktracking("videoplayer_click", "pause");
      // Get the Play/Pause button component
      const playPauseButton = player.controlBar.playToggle;
      // Set the new hover title for Play/Pause button
      playPauseButton.controlText(t("VideoPlayer.controlBarPlay") + " (k)");
      emit("pause");
    });
    player.on("volumechange", () => {
      matomo_clicktracking("videoplayer_click", "volumechange");
      handleMuted(player);
    });
    player.on("click", () => {
      handleMuted(player);
    });
    //videoPlayer.value.play();
  });
}
</script>

<style scoped></style>
