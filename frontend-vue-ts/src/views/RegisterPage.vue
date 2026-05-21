<template>
  <div class="register-page d-flex align-items-center justify-content-center min-vh-100 bg-light">
    <div class="card shadow-lg border-0 register-card p-4" style="max-width: 420px; width: 100%;">
      <div class="card-body">
        <div class="text-center mb-4">
          <i class="fa-solid fa-user-plus fa-3x text-primary mb-3"></i>
          <h3 class="fw-bold mb-1">注册</h3>
          <p class="text-muted small">填写以下信息完成注册</p>
        </div>

        <form @submit.prevent="handleSubmit" id="registerForm">
          <!-- 用户名 -->
          <div class="form-floating mb-2">
            <input
              type="text"
              class="form-control"
              id="name"
              v-model="form.name"
              placeholder="请输入用户名"
              required>
            <label for="name"><i class="fa-solid fa-user me-2 text-secondary"></i>用户名</label>
          </div>
          <div v-if="usernameExists" class="text-danger small mb-3">
            <i class="fa-solid fa-circle-exclamation me-1"></i>该用户名已被占用
          </div>

          <!-- 密码 -->
          <div class="form-floating mb-3">
            <input
              type="password"
              class="form-control"
              id="password"
              v-model="form.password"
              placeholder="请输入密码"
              required>
            <label for="password"><i class="fa-solid fa-lock me-2 text-secondary"></i>密码</label>
          </div>

          <!-- 确认密码 -->
          <div class="form-floating mb-2">
            <input
              type="password"
              class="form-control"
              id="confirm_password"
              v-model="form.confirmPassword"
              placeholder="请再次输入密码"
              required>
            <label for="confirm_password"><i class="fa-solid fa-key me-2 text-secondary"></i>确认密码</label>
          </div>
          <div v-if="passwordMismatch" class="text-danger small mb-3">
            <i class="fa-solid fa-circle-exclamation me-1"></i>两次输入的密码不一致
          </div>

          <!-- 注册按钮 -->
          <button type="submit" :disabled="!isFormValid || userStore.loading" class="btn btn-primary w-100 py-2 fw-semibold">
            <span v-if="userStore.loading" class="spinner-border spinner-border-sm me-2" role="status"></span>
            <i v-else class="fa-solid fa-user-check me-2"></i>
            {{ userStore.loading ? '注册中...' : '注册' }}
          </button>
        </form>

        <div class="text-center mt-4">
          <p class="mb-0 text-muted">
            已有账号？
            <router-link to="/login" class="text-primary fw-semibold text-decoration-none">立即登录</router-link>
          </p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import { useUserStore } from '@/store/userStore'

const userStore = useUserStore()

// 表单数据
const form = ref({
  name: '',
  password: '',
  confirmPassword: ''
})

// 验证状态
const usernameExists = ref(false)
const passwordMismatch = ref(false)

// 检查用户名是否已存在
const checkUsername = async (username: string) => {
  if (!username.trim()) return

  usernameExists.value = await userStore.checkUsername(username)
}

// 检查密码匹配
const checkPasswordMatch = () => {
  passwordMismatch.value = form.value.password && form.value.confirmPassword && form.value.password !== form.value.confirmPassword
}

// 表单是否有效
const isFormValid = computed(() => {
  return form.value.name.trim() &&
         form.value.password.trim() &&
         form.value.confirmPassword.trim() &&
         !usernameExists.value &&
         !passwordMismatch.value &&
         !userStore.loading
})

// 监听用户名变化
watch(() => form.value.name, (newName) => {
  checkUsername(newName)
})

// 监听密码和确认密码变化
watch([() => form.value.password, () => form.value.confirmPassword], () => {
  checkPasswordMatch()
})

// 提交表单
const handleSubmit = async () => {
  if (!isFormValid.value) return

  await userStore.register({
    name: form.value.name,
    password: form.value.password
  })
}
</script>

<style scoped>
/* 背景与整体布局 */
.register-page {
  background: linear-gradient(135deg, #f8fafc 0%, #eef2f7 100%);
  padding: 2rem;
}

/* 卡片样式 */
.register-card {
  border-radius: 18px;
  background-color: #ffffff;
  box-shadow: 0 12px 30px rgba(0, 0, 0, 0.08);
  transition: all 0.3s ease;
}

.register-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 18px 45px rgba(0, 0, 0, 0.1);
}

/* 表单输入框 */
.form-floating > .form-control {
  border-radius: 10px;
  border: 1px solid #d1d5db;
  box-shadow: none;
  transition: border-color 0.3s, box-shadow 0.3s;
}

.form-floating > .form-control:focus {
  border-color: #2563eb;
  box-shadow: 0 0 0 0.15rem rgba(37, 99, 235, 0.2);
}

.form-floating label {
  color: #6b7280;
}

/* 按钮样式 */
.btn-primary {
  background: linear-gradient(135deg, #2563eb, #3b82f6);
  border: none;
  border-radius: 10px;
  transition: all 0.3s ease;
}

.btn-primary:hover:not(:disabled) {
  background: linear-gradient(135deg, #1e40af, #2563eb);
  transform: translateY(-1px);
}

.btn-primary:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

/* 链接与提示 */
.text-primary:hover {
  text-decoration: underline;
}

/* 响应式优化 */
@media (max-width: 576px) {
  .register-card {
    padding: 2rem 1.5rem;
  }
  .form-floating label {
    font-size: 0.9rem;
  }
}
</style>
