<template>
  <div class="dag-item">
    <div class="dag-header">
      <span class="dag-id">DAG Run ID: {{ dag.dag_run_id }}</span>
    </div>
    <div v-if="dag.metadata" class="metadata-section">
      <div class="metadata-item">
        <strong>Title:</strong> {{ dag.metadata.result.title }}
      </div>
      <div class="metadata-item">
        <strong>Course:</strong> {{ dag.metadata.result.description?.course }}
      </div>
      <div class="metadata-item">
        <strong>Lecturer:</strong> {{ dag.metadata.result.description?.lecturer }}
      </div>
      <div class="metadata-item">
        <strong>Language:</strong> {{ dag.metadata.result.language }}
      </div>
    </div>
    <div class="files" v-if="dag.conf?.input">
      <div v-for="file in dag.conf.input" :key="file.urn" class="file-item">
        {{ file.filename }} ({{ file["hans-type"] }})
      </div>
    </div>
    <div class="tasks" v-if="dag.tasks">
      <div v-for="(tasks, state) in groupTasksByState(dag.tasks)" :key="state" class="task-group">
        <div class="task-header">
          {{ state.toUpperCase() }} tasks ({{ tasks.length }})
          <span class="task-count">
            Tasks with N/A duration: {{ countTasksWithNA(tasks) }}
          </span>
        </div>
      </div>
    </div>
    <div>
      <button class="delete-btn" @click="$emit('delete', dag.dag_run_id)">Delete</button>
    </div>

  </div>
</template>

<script setup lang="ts">
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

const props = defineProps<{
  dag: DAGRun;
}>();

function extractUserInfo(metaUrn: string): string {
  return metaUrn.split(":").pop() || "";
}

function groupTasksByState(tasks: TaskInstance[]): Record<string, TaskInstance[]> {
  return tasks.reduce((acc, task) => {
    const state = task.state || "none";
    if (!acc[state]) acc[state] = [];
    acc[state].push(task);
    return acc;
  }, {} as Record<string, TaskInstance[]>);
}

function countTasksWithNA(tasks: TaskInstance[]): number {
  return tasks.filter(task => task.duration === null).length;
}

defineEmits<{
  (e: 'delete', dagRunId: string): void;
}>();
</script>

<style scoped>
.dag-item {
  background-color: var(--hans-light);
  border-radius: 6px;
  padding: 1rem;
  border: 1px solid var(--hans-light-gray);
  transition: transform 0.2s, box-shadow 0.2s;
  position: relative;
}

.dag-item:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
}

.dag-header {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  margin-bottom: 1rem;
  padding-bottom: 0.5rem;
  border-bottom: 1px solid var(--hans-light-gray);
}

.dag-id {
  font-weight: bold;
  color: var(--hans-dark);
  word-break: break-all;
}

.user-info {
  font-size: 0.9em;
  color: var(--hans-dark-gray);
}

.files {
  margin: 0.5rem 0;
}

.file-item {
  margin: 0.5rem 0;
  padding: 0.5rem;
  background-color: white;
  border-radius: 4px;
  font-size: 0.9em;
  color: var(--hans-dark-gray);
}

.tasks {
  margin-top: 1rem;
}

.task-group {
  margin: 0.5rem 0;
}

.task-header {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
  padding: 0.5rem;
  background-color: white;
  border-radius: 4px;
  font-size: 0.9em;
}

.task-count {
  color: var(--hans-dark-gray);
  font-size: 0.9em;
}

.metadata-section {
  margin-top: 10px;
  padding-top: 10px;
  border-top: 1px solid #e0e0e0;
}

.metadata-item {
  margin: 5px 0;
  font-size: 0.9em;
  color: #666;
}

.metadata-item strong {
  color: #333;
  margin-right: 5px;
}

.delete-btn {
  color: #fff;
  background: #d9534f;
  border: none;
  border-radius: 3px;
  padding: 0.5rem 1rem;
  cursor: pointer;
  font-weight: bold;
}
.delete-btn:hover {
  background: #c9302c;
}

@media (max-width: 768px) {
  .dag-header {
    flex-direction: column;
  }

  .task-header {
    flex-direction: column;
  }
}

@media (max-width: 480px) {
  .dag-id, .user-info {
    font-size: 0.9em;
  }
}
</style>
