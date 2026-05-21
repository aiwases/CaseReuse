<template>
  <div class="progress-bar-container">
    <div class="progress-steps">
      <div class="ready-section">
        <div class="progress-step" :class="{ active: isStepActive(0), completed: isStepCompleted(0) }">
          <span class="step-number">0</span>
          <span class="step-text">Ready</span>
        </div>
      </div>

      <div class="connector"></div>

      <div class="branches-section">
        <div class="branch branch-1" :class="branch1Status">
          <div class="progress-step" :class="{ active: isStepActive(1), completed: isStepCompleted(1) }">
            <span class="step-number">1-1</span>
            <span class="step-text">Independent Requirement (old)</span>
          </div>
          <div class="connector"></div>
          <div class="progress-step" :class="{ active: isStepActive(3), completed: isStepCompleted(3) }">
            <span class="step-number">2</span>
            <span class="step-text">Test Scenario Synthesis</span>
          </div>
          <div class="connector"></div>
          <div class="progress-step" :class="{ active: isStepActive(4), completed: isStepCompleted(4) }">
            <span class="step-number">3</span>
            <span class="step-text">Scenario-Case Alignment</span>
          </div>
        </div>

        <div class="branch branch-2" :class="branch2Status">
          <div class="progress-step" :class="{ active: isStepActive(1), completed: isStepCompleted(1) }">
            <span class="step-number">1-1</span>
            <span class="step-text">Independent Requirement (old)</span>
          </div>
          <div class="connector"></div>
          <div class="progress-step" :class="{ active: isStepActive(2), completed: isStepCompleted(2) }">
            <span class="step-number">1-2</span>
            <span class="step-text">Independent Requirement (new)</span>
          </div>
          <div class="connector"></div>
          <div class="progress-step" :class="{ active: isStepActive(5), completed: isStepCompleted(5) }">
            <span class="step-number">4</span>
            <span class="step-text">Regulatory Change ID</span>
          </div>
        </div>
      </div>

      <div class="connector"></div>

      <div class="right-section">
        <div class="branch branch-merge" :class="branchMergeStatus">
          <div class="progress-step" :class="{ active: isStepActive(6), completed: isStepCompleted(6) }">
            <span class="step-number">5</span>
            <span class="step-text">Cascading Impact Scope</span>
          </div>
          <div class="connector"></div>
          <div class="progress-step" :class="{ active: isStepActive(7), completed: isStepCompleted(7) }">
            <span class="step-number">6</span>
            <span class="step-text">Test Suite Reuse Update</span>
          </div>
        </div>
      </div>
    </div>

    <div v-if="loading" class="progress-loading">Loading progress...</div>
    <div v-if="error" class="progress-error">{{ error }}</div>
  </div>
</template>

<script setup lang="ts">
import { computed, onBeforeUnmount, onMounted, ref, watch } from "vue";
import { type ProjectStatus, fetchProjectProgressApi, type ProjectProgress } from "@/api/reuse";

interface Props {
  status?: ProjectStatus;
  projectId: number | string;
  autoFetch?: boolean;
}

const props = withDefaults(defineProps<Props>(), {
  status: "Ready",
  autoFetch: true,
});

const loading = ref(false);
const error = ref<string | null>(null);
const progressData = ref<ProjectProgress | null>(null);
const pollTimer = ref<number | null>(null);

const currentStatus = computed<ProjectStatus>(() => progressData.value?.reuse_status || props.status);
const branchAStatus = computed<ProjectStatus>(() => progressData.value?.branch_a_status || "Ready");
const branchBStatus = computed<ProjectStatus>(() => progressData.value?.branch_b_status || "Ready");
const running = computed(() => progressData.value?.is_running || false);

const completedSteps = computed<Set<number>>(() => {
  const done = new Set<number>();
  const a = branchAStatus.value;
  const b = branchBStatus.value;
  const reuse = currentStatus.value;

  if (a !== "Ready" || b !== "Ready" || reuse !== "Ready") {
    done.add(0);
  }

  if (a === "Step1_old_ready" || a === "Step2_Done" || a === "Step3_Done") done.add(1);
  if (a === "Step2_Done" || a === "Step3_Done") done.add(3);
  if (a === "Step3_Done") done.add(4);

  if (b === "Step1_old_ready" || b === "Step1_all_ready" || b === "Step4_Done") done.add(1);
  if (b === "Step1_all_ready" || b === "Step4_Done") done.add(2);
  if (b === "Step4_Done") done.add(5);

  if (reuse === "Step5_Done" || reuse === "Completed") done.add(6);
  if (reuse === "Completed") done.add(7);

  return done;
});

const activeSteps = computed<Set<number>>(() => {
  const active = new Set<number>();
  const done = completedSteps.value;
  const reuse = currentStatus.value;

  if (reuse === "Completed" || reuse === "failed") {
    return active;
  }

  if (reuse === "Step5_Done") {
    active.add(7);
    return active;
  }

  if (reuse === "Merge_Ready") {
    active.add(6);
    return active;
  }

  // Branch A next target: 1-1 -> 2 -> 3
  if (!done.has(1)) active.add(1);
  else if (!done.has(3)) active.add(3);
  else if (!done.has(4)) active.add(4);

  // Branch B next target: 1-1 -> 1-2 -> 4
  if (!done.has(1)) active.add(1);
  else if (!done.has(2)) active.add(2);
  else if (!done.has(5)) active.add(5);

  if (active.size === 0 && !done.has(0)) {
    active.add(0);
  }

  return active;
});

const branch1Status = computed(() => {
  const done = completedSteps.value;
  const active = activeSteps.value;
  if (done.has(1) && done.has(3) && done.has(4)) return "completed";
  if (active.has(1) || active.has(3) || active.has(4) || done.has(1) || done.has(3) || done.has(4)) return "active";
  return "";
});

const branch2Status = computed(() => {
  const done = completedSteps.value;
  const active = activeSteps.value;
  if (done.has(1) && done.has(2) && done.has(5)) return "completed";
  if (active.has(1) || active.has(2) || active.has(5) || done.has(1) || done.has(2) || done.has(5)) return "active";
  return "";
});

const branchMergeStatus = computed(() => {
  const done = completedSteps.value;
  const active = activeSteps.value;
  if (done.has(6) && done.has(7)) return "completed";
  if (active.has(6) || active.has(7) || done.has(6)) return "active";
  return "";
});

const isStepActive = (stepId: number): boolean => activeSteps.value.has(stepId);
const isStepCompleted = (stepId: number): boolean => completedSteps.value.has(stepId);

const fetchProgress = async () => {
  if (!props.projectId) return;

  loading.value = true;
  error.value = null;
  try {
    const response = await fetchProjectProgressApi(props.projectId);
    progressData.value = response.data;
  } catch (err: any) {
    error.value = err?.response?.data?.message || "Failed to fetch progress";
  } finally {
    loading.value = false;
  }
};

const clearPollTimer = () => {
  if (pollTimer.value !== null) {
    window.clearInterval(pollTimer.value);
    pollTimer.value = null;
  }
};

const resetPolling = () => {
  clearPollTimer();
  if (!props.autoFetch || !props.projectId || !running.value) return;
  pollTimer.value = window.setInterval(() => {
    fetchProgress();
  }, 5000);
};

watch(
  () => props.projectId,
  (newId) => {
    if (newId && props.autoFetch) {
      fetchProgress();
    }
  }
);

watch(running, () => {
  resetPolling();
});

onMounted(() => {
  if (props.autoFetch) {
    fetchProgress();
  }
});

onBeforeUnmount(() => {
  clearPollTimer();
});

defineExpose({
  fetchProgress,
});
</script>

<style scoped>
.progress-bar-container {
  width: 100%;
  margin: 20px 0;
  padding: 15px;
  background-color: #fafafa;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
}

.progress-steps {
  display: flex;
  align-items: center;
  gap: 20px;
  margin-bottom: 10px;
}

.ready-section {
  display: flex;
  align-items: center;
}

.branches-section {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 40px;
}

.right-section {
  display: flex;
  align-items: center;
}

.branch {
  display: flex;
  align-items: center;
  position: relative;
  width: 100%;
}

.branch .connector {
  flex: 1;
  height: 2px;
  background-color: #e6e6e6;
  margin: 0 10px;
  position: relative;
}

.branch.completed .connector {
  background-color: #67c23a;
}

.branch.active .connector {
  background-color: #409eff;
}

.branch-1,
.branch-2,
.branch-merge {
  justify-content: flex-start;
}

.progress-step {
  display: flex;
  flex-direction: column;
  align-items: center;
  position: relative;
  width: 120px;
  z-index: 1;
}

.connector {
  width: 80px;
  height: 2px;
  background-color: #e6e6e6;
  margin: 0 10px;
  position: relative;
}

.step-number {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  background-color: #e6e6e6;
  color: #909399;
  font-size: 12px;
  display: flex;
  justify-content: center;
  align-items: center;
  margin-bottom: 6px;
  transition: all 0.3s ease;
  position: relative;
  z-index: 2;
}

.step-text {
  font-size: 12px;
  color: #909399;
  transition: color 0.3s ease;
  text-align: center;
  line-height: 1.2;
}

.progress-step.active .step-number {
  background-color: #409eff;
  color: #fff;
  box-shadow: 0 0 0 3px rgba(64, 158, 255, 0.2);
}

.progress-step.active .step-text {
  color: #409eff;
  font-weight: 500;
}

.progress-step.completed .step-number {
  background-color: #67c23a;
  color: #fff;
}

.progress-step.completed .step-text {
  color: #67c23a;
  font-weight: 500;
}

.progress-loading {
  text-align: center;
  font-size: 12px;
  color: #909399;
  margin-top: 10px;
}

.progress-error {
  text-align: center;
  font-size: 12px;
  color: #f56c6c;
  margin-top: 10px;
}
</style>
