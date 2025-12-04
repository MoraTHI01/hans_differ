<template>
  <HeaderRow />
  <LogoAndSearchbarRow :placeholder="t('StatisticsView.searchplaceholder')" :showSearch="false" :showProgress="false" />
  <div class="main-container">
    <MenuBanner :menutext="t('StatisticsView.menutext')" />
    <div class="row sub-container statistics-container">
      <LoadingBar v-if="statLoading" class="statistics-loading" />
      <div class="col statistics">
        <h3 class="scope">{{ headerText }}</h3>
        <div v-if="!statLoading" class="row d-flex justify-content-center numbers">
          <div class="col-md-3 numbers-item" v-for="(value, key) in stats" :key="key">
            <div class="card text-center">
              <div class="card-body">
                <img :src="iconMap[key]" alt="icon" class="mb-2" width="40" height="40" />
                <h5 class="card-title">{{ t("StatisticsView." + key) }}</h5>
                <p class="card-text">{{ value }}</p>
              </div>
            </div>
          </div>
        </div>
        <div class="row charts">
          <div class="col-md-6 text-center">
            <canvas id="mediaTotalPieChart" class="mt-2"></canvas>
          </div>
          <div class="col-md-6 text-center">
            <canvas id="mediaPublishedPieChart" class="mt-2"></canvas>
          </div>
        </div>
      </div>
    </div>
  </div>
  <BottomRow />
</template>

<script setup lang="ts">
import LoadingBar from "@/components/LoadingBarComponent.vue";
import HeaderRow from "@/components/HeaderRow.vue";
import BottomRow from "@/components/BottomRow.vue";
import LogoAndSearchbarRow from "@/components/LogoAndSearchbarRow.vue";
import MenuBanner from "@/components/MenuBanner.vue";
import {ref, watch, onMounted} from "vue";
import {useI18n} from "vue-i18n";
import {LoggerService} from "@/common/loggerService";
import {apiClient} from "@/common/apiClient";
import {useAuthStore} from "@/stores/auth";
import {Chart, registerables} from "chart.js";

const loggerService = new LoggerService();

const {t, locale} = useI18n({useScope: "global"});
const authStore = useAuthStore();
const headerText = ref("");
const statLoading = ref(true);

Chart.register(...registerables);

const stats = ref({
  count_channels: 0,
  count_media: 0,
  count_media_published: 0,
  count_media_listed: 0,
});

const iconMap: Record<string, string> = {
  count_channels: "/bootstrap-icons/layers.svg",
  count_media: "/bootstrap-icons/play-btn.svg",
  count_media_published: "/bootstrap-icons/eye.svg",
  count_media_listed: "/bootstrap-icons/list-task.svg",
};

const fetchData = async () => {
  try {
    const response = await apiClient.get("/stats");
    stats.value = response.data.result;
    renderChart();
    statLoading.value = false;
  } catch (error) {
    console.error("Error fetching statistics:", error);
  }
};

const renderChart = () => {
  if (["admin"].includes(authStore.getRole())) {
    headerText.value = t("StatisticsView.global");
  } else if (["developer"].includes(authStore.getRole())) {
    headerText.value = t("StatisticsView.institute") + ": " + decodeURIComponent(authStore.getInstitute());
  } else {
    headerText.value = t("StatisticsView.account");
  }
  const mediaTotalCtx = document.getElementById("mediaTotalPieChart") as HTMLCanvasElement;
  if (mediaTotalCtx) {
    new Chart(mediaTotalCtx, {
      type: "pie",
      data: {
        labels: [t("StatisticsView.media_published"), t("StatisticsView.media_unpublished")],
        datasets: [
          {
            data: [
              (stats.value.count_media_published / stats.value.count_media) * 100,
              100 - (stats.value.count_media_published / stats.value.count_media) * 100,
            ],
            backgroundColor: ["#28a745", "#dc3545"],
          },
        ],
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          tooltip: {
            callbacks: {
              label: (tooltipItem: any) => `${tooltipItem.raw.toFixed(2)}%`,
            },
          },
        },
      },
    });
  }

  const mediaPublishedCtx = document.getElementById("mediaPublishedPieChart") as HTMLCanvasElement;
  if (mediaPublishedCtx) {
    new Chart(mediaPublishedCtx, {
      type: "pie",
      data: {
        labels: [t("StatisticsView.media_listed"), t("StatisticsView.media_published")],
        datasets: [
          {
            data: [
              (stats.value.count_media_listed / stats.value.count_media_published) * 100,
              100 - (stats.value.count_media_listed / stats.value.count_media_published) * 100,
            ],
            backgroundColor: ["#28a745", "#0d6efd"],
          },
        ],
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          tooltip: {
            callbacks: {
              label: (tooltipItem: any) => `${tooltipItem.raw.toFixed(2)}%`,
            },
          },
        },
      },
    });
  }
};

onMounted(fetchData);

watch(locale, async (newText) => {
  renderChart();
});
</script>

<style>
.statistics-loading {
  --bar-height: 0.4em;
}
.statistics {
  max-height: 56vh;
  margin-top: 1em;
}
.numbers {
  display: flex;
}
.numbers-item {
}
.scope {
  text-align: center;
}
.card-title {
  word-wrap: break-word;
}

.statistics-container {
  position: relative;
}

@media (max-aspect-ratio: 3/4) {
  .statistics-container {
    justify-content: center;
  }
}

@media (max-width: 600px) {
  .numbers-item {
  }
  .numbers {
    display: flex;
    /*
    display: grid !important;
    grid-template-columns: 50% 50%;
    grid-template-rows: 100% 100%;*/
  }
  .charts {
    display: flex;
    /*
    display: grid;
    grid-template-columns: 50% 50%;
    */
  }
}
</style>
