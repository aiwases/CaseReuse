<template>
  <div class="project-info-section">
    <el-form-item label="项目名称" prop="name">
      <el-input
        v-model.trim="store.formData.name"
        placeholder="请输入项目名称"
        maxlength="255"
        show-word-limit
        :class="{ 'is-invalid': !store.nameAvailable }"
        class="ruoyi-input"
      />
      <div class="form-text" :class="{ 'text-danger': !store.nameAvailable }">
        {{ store.nameAvailable ? '项目名称在同一用户下必须唯一' : '该项目名称已存在，请更换名称' }}
      </div>
    </el-form-item>

    <el-form-item label="项目描述">
      <el-input
        v-model="store.formData.description"
        type="textarea"
        :rows="3"
        placeholder="请输入项目描述（可选）"
        maxlength="500"
        show-word-limit
        class="ruoyi-input"
      />
      <div class="form-text">简要描述项目的目标和用途</div>
    </el-form-item>

    <el-form-item label="项目类型" required>
      <div class="form-text">选择项目的主要功能类型</div>
      <el-radio-group v-model="store.formData.process_type" class="project-type-radio">
        <el-radio label="generation">测试用例生成</el-radio>
        <el-radio label="reuse">测试用例重用</el-radio>
      </el-radio-group>
    </el-form-item>
  </div>
</template>

<script setup lang="ts">
import { useCreatProjectStore } from '@/store/creatProjectStore';

// 获取store实例
const store = useCreatProjectStore();
</script>

<style scoped>
.project-info-section {
  width: 100%;
}
</style>