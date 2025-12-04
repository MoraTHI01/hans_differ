<template>
  <div class="airflow-status">
    <div v-if="loading" class="loading">
      <LoadingBar />
    </div>
    <div v-else-if="userInfo && userInfo.role !== 'everybody'" class="dag-sections">
      <!-- Running DAGs -->
      <div v-if="runningDAGs && runningDAGs.length > 0" class="dag-section running">
        <div class="section-header" @click="toggleSection('running')">
          <span class="status-icon running"></span>
          Running DAGs ({{ runningDAGs.length }})
          <span class="toggle-icon">{{ expandedSections.running ? '▼' : '▶' }}</span>
          <button class="delete-all-btn" @click.stop="handleDeleteAllDags('running')" title="Delete all running DAGs">
            Delete All
          </button>
        </div>
        <Transition name="slide">
          <div v-show="expandedSections.running" class="dag-grid">
            <DagItem v-for="dag in runningDAGs" :key="dag.dag_run_id" :dag="dag" @delete="handleDeleteDagRun" />
          </div>
        </Transition>
      </div>

      <!-- Queued DAGs -->
      <div v-if="queuedDAGs && queuedDAGs.length > 0" class="dag-section queued">
        <div class="section-header" @click="toggleSection('queued')">
          <span class="status-icon queued"></span>
          Queued DAGs ({{ queuedDAGs.length }})
          <span class="toggle-icon">{{ expandedSections.queued ? '▼' : '▶' }}</span>
          <button class="delete-all-btn" @click.stop="handleDeleteAllDags('queued')" title="Delete all queued DAGs">
            Delete All
          </button>
        </div>
        <Transition name="slide">
          <div v-show="expandedSections.queued" class="dag-grid">
            <DagItem v-for="dag in queuedDAGs" :key="dag.dag_run_id" :dag="dag" @delete="handleDeleteDagRun" />
          </div>
        </Transition>
      </div>

      <!-- Failed DAGs -->
      <div v-if="failedDAGs && failedDAGs.length > 0" class="dag-section failed">
        <div class="section-header" @click="toggleSection('failed')">
          <span class="status-icon failed"></span>
          Failed DAGs ({{ failedDAGs.length }})
          <span class="toggle-icon">{{ expandedSections.failed ? '▼' : '▶' }}</span>
          <button class="delete-all-btn" @click.stop="handleDeleteAllDags('failed')" title="Delete all failed DAGs">
            Delete All
          </button>
        </div>
        <Transition name="slide">
          <div v-show="expandedSections.failed" class="dag-grid">
            <DagItem v-for="dag in failedDAGs" :key="dag.dag_run_id" :dag="dag" @delete="handleDeleteDagRun" />
          </div>
        </Transition>
      </div>

      <!-- Success DAGs -->
      <div v-if="successDAGs && successDAGs.length > 0" class="dag-section success">
        <div class="section-header" @click="toggleSection('success')">
          <span class="status-icon success"></span>
          Success DAGs ({{ successDAGs.length }})
          <span class="toggle-icon">{{ expandedSections.success ? '▼' : '▶' }}</span>
          <button class="delete-all-btn" @click.stop="handleDeleteAllDags('success')" title="Delete all success DAGs">
            Delete All
          </button>
        </div>
        <Transition name="slide">
          <div v-show="expandedSections.success" class="dag-grid">
            <DagItem v-for="dag in successDAGs" :key="dag.dag_run_id" :dag="dag" @delete="handleDeleteDagRun" />
          </div>
        </Transition>
      </div>

      <!-- No DAGs -->
      <div v-if="!loading && (!runningDAGs || runningDAGs.length === 0) && (!queuedDAGs || queuedDAGs.length === 0) && (!failedDAGs || failedDAGs.length === 0) && (!successDAGs || successDAGs.length === 0)" class="no-dags">
        No DAGs found
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import axios from 'axios';
import LoadingBar from '@/components/LoadingBarComponent.vue';
import DagItem from '@/components/DagItem.vue';

interface TaskInstance {
  duration: number | null;
  state: string | null;
  task_id: string;
  start_date: string | null;
  end_date: string | null;
  try_number: number;
  max_tries: number;
  hostname: string;
  operator: string;
}

interface DAGRun {
  dag_run_id: string;
  state: string;
  start_date: string;
  end_date: string | null;
  conf: {
    input: Array<{
      filename: string;
      "hans-type": string;
      locale: string;
      "mime-type": string;
      urn: string;
    }>;
    output: Array<{
      backend: string;
      frontend: string;
    }>;
    metaUrn: string;
  };
  tasks: TaskInstance[];
  metadata?: {
    result: {
      title: string;
      description?: {
        course: string;
        lecturer: string;
      };
      language: string;
    };
  };
}

const loading = ref(true);
const runningDAGs = ref<DAGRun[]>([]);
const queuedDAGs = ref<DAGRun[]>([]);
const failedDAGs = ref<DAGRun[]>([]);
const successDAGs = ref<DAGRun[]>([]);
const userInfo = ref(null);

const expandedSections = ref({
  running: false,
  queued: false,
  failed: false,
  success: false
});

function toggleSection(section: keyof typeof expandedSections.value) {
  expandedSections.value[section] = !expandedSections.value[section];
}

async function fetchUserInfo() {
  try {
    const tokenJson = localStorage.getItem('hans_access_token');
    if (!tokenJson) {
      return;
    }
    const tokenData = JSON.parse(tokenJson);
    const response = await axios.get('/api/user_info', {
      headers: {
        'Authorization': `Bearer ${tokenData.token}`
      }
    });
    userInfo.value = response.data;
  } catch (error) {
    console.error('Error calling user info endpoint:', error);
  }
}

async function fetchAirflowStatus() {
  loading.value = true;
  let allDagsCombined: DAGRun[] = []; // Define here to access in finally block

  try {
    // --- STAGE 1: INITIAL LOAD ---
    const response = await axios.get('/api/status');
    const data = response.data;

    // Assign the lists to your reactive refs
    runningDAGs.value = data?.result?.running_dags || [];
    queuedDAGs.value = data?.result?.queued_dags || [];
    failedDAGs.value = data?.result?.failed_dags || [];
    successDAGs.value = data?.result?.success_dags || [];

    // Combine all DAGs for the background fetching step
    allDagsCombined = [
      ...runningDAGs.value,
      ...queuedDAGs.value,
      ...failedDAGs.value,
      ...successDAGs.value
    ];

  } catch (error) {
    console.error('Error fetching Airflow status:', error);
    if (error.response) {
      console.error('Error response:', error.response);
      console.error('Error response data:', error.response.data);
      console.error('Error response status:', error.response.status);
    }
    // Reset arrays on error
    runningDAGs.value = [];
    queuedDAGs.value = [];
    failedDAGs.value = [];
    successDAGs.value = [];
  } finally {
    // This now runs after the INITIAL load, showing the UI quickly
    loading.value = false;
  }

  // --- STAGE 2: BACKGROUND HYDRATION ---
  // This part runs after the loading screen is gone.
  // We loop through the DAGs and fetch metadata for each one.
  // We don't use Promise.all, as we want each to update independently.
  for (const dag of allDagsCombined) {
    try {
      const metadataResponse = await axios.get(`/api/metadata/${dag.dag_run_id}`);
      // Vue's reactivity will automatically update the DagItem component
      dag.metadata = metadataResponse.data;
    } catch (error) {
      console.error(`Error fetching metadata for DAG ${dag.dag_run_id}:`, error);
      dag.metadata = null; // Or set an error state
    }
  }

  // After metadata is fetched, we must re-filter for the lecturer role
  if (userInfo.value?.role === 'lecturer') {
    const userName = `${userInfo.value.firstName} ${userInfo.value.lastName}`;
    const filterByLecturer = (dags: DAGRun[]) => {
      return dags.filter(dag => {
        const lecturer = dag.metadata?.result?.description?.lecturer;
        return lecturer === userName;
      });
    };
    runningDAGs.value = filterByLecturer(runningDAGs.value);
    queuedDAGs.value = filterByLecturer(queuedDAGs.value);
    failedDAGs.value = filterByLecturer(failedDAGs.value);
    successDAGs.value = filterByLecturer(successDAGs.value);
  }
}

async function handleDeleteDagRun(dagRunId: string) {
  if (!confirm('Are you sure you want to delete this DAG run?')) return;
  try {
    await axios.delete(`/api/airflow_dag_delete/${dagRunId}`);
    await fetchAirflowStatus();
  } catch (error) {
    alert('Failed to delete DAG run.');
    console.error('Delete error:', error);
  }
}

async function handleDeleteAllDags(category: 'running' | 'queued' | 'failed' | 'success') {
  if (!confirm(`Are you sure you want to delete all ${category} DAGs? This action cannot be undone.`)) return;
  try {
    const dagRunIds = category === 'running' ? runningDAGs.value.map(dag => dag.dag_run_id) :
                        category === 'queued' ? queuedDAGs.value.map(dag => dag.dag_run_id) :
                        category === 'failed' ? failedDAGs.value.map(dag => dag.dag_run_id) :
                        successDAGs.value.map(dag => dag.dag_run_id);

    if (dagRunIds.length === 0) {
      alert('No DAGs to delete in this category.');
      return;
    }

    let deletedCount = 0;
    let failedCount = 0;

    for (const dagRunId of dagRunIds) {
      try {
        await axios.delete(`/api/airflow_dag_delete/${dagRunId}`);
        deletedCount++;
      } catch (error) {
        console.error(`Failed to delete DAG run ${dagRunId}:`, error);
        failedCount++;
      }
    }

    await fetchAirflowStatus();

    if (failedCount === 0) {
      alert(`Successfully deleted ${deletedCount} ${category} DAGs.`);
    } else {
      alert(`Deleted ${deletedCount} ${category} DAGs, ${failedCount} failed.`);
    }
  } catch (error) {
    alert('Failed to delete DAGs.');
    console.error('Delete all error:', error);
  }
}

onMounted(async () => {
  await fetchUserInfo(); // Wait for user info to be fetched
  fetchAirflowStatus();
});
</script>

<style scoped>
.airflow-status {
  padding: 1rem;
  background-color: var(--hans-light);
  border-radius: 4px;
  margin-bottom: 1rem;
}

.loading {
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 2rem;
  position: relative;
  min-height: 200px;
  background-color: white;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.dag-sections {
  display: flex;
  flex-direction: column;
  gap: 2rem;
}

.dag-section {
  background-color: white;
  border-radius: 8px;
  padding: 1.5rem;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.section-header {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin-bottom: 1rem;
  padding-bottom: 0.5rem;
  border-bottom: 2px solid var(--hans-light-gray);
  color: var(--hans-dark);
  font-size: 1.2rem;
  cursor: pointer;
  user-select: none;
}

.section-header:hover {
  opacity: 0.8;
}

.toggle-icon {
  margin-left: auto;
  font-size: 0.8em;
  color: var(--hans-dark-gray);
}

.delete-all-btn {
  margin-left: 1rem;
  padding: 0.5rem 1rem;
  background-color: var(--hans-red);
  color: white;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-size: 0.9em;
  transition: background-color 0.2s ease;
}

.delete-all-btn:hover {
  background-color: var(--hans-dark-red);
}

.delete-all-btn:focus {
  outline: none;
}

.status-icon {
  width: 12px;
  height: 12px;
  border-radius: 50%;
}

.status-icon.running {
  background-color: #4CAF50;
  box-shadow: 0 0 8px #4CAF50;
}

.status-icon.queued {
  background-color: #FFC107;
  box-shadow: 0 0 8px #FFC107;
}

.status-icon.failed {
  background-color: #F44336;
  box-shadow: 0 0 8px #F44336;
}

.status-icon.success {
  background-color: #2196F3;
  box-shadow: 0 0 8px #2196F3;
}

.dag-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 1rem;
}

.no-dags {
  text-align: center;
  color: var(--hans-dark-gray);
  padding: 2rem;
  background-color: white;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

/* Responsive Design */
@media (max-width: 768px) {
  .dag-grid {
    grid-template-columns: 1fr;
  }

  .dag-section {
    padding: 1rem;
  }
}

@media (max-width: 480px) {
  .airflow-status {
    padding: 0.5rem;
  }

  .section-header {
    font-size: 1rem;
  }
}

/* Slide transition */
.slide-enter-active,
.slide-leave-active {
  transition: all 0.3s ease;
  max-height: 2000px;
  opacity: 1;
}

.slide-enter-from,
.slide-leave-to {
  max-height: 0;
  opacity: 0;
  overflow: hidden;
}
</style>
