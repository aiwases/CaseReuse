<template>
  <div class="login-page d-flex align-items-center justify-content-center min-vh-100 bg-light">
    <div class="card shadow-lg border-0 login-card p-4" style="max-width: 420px; width: 100%;">
      <div class="card-body">
        <!-- 标题 -->
        <div class="text-center mb-4">
          <i class="fa-solid fa-user-shield fa-3x text-primary mb-3"></i>
          <h3 class="fw-bold mb-1">登录</h3>
          <p class="text-muted small">欢迎回来，请登录您的账户</p>
        </div>

        <!-- 登录表单 -->
        <form @submit.prevent="onSubmit">
          <div class="form-floating mb-3">
            <input
              v-model="form.name"
              type="text"
              class="form-control"
              id="name"
              placeholder="请输入用户名"
              required
            />
            <label for="name">
              <i class="fa-solid fa-user me-2 text-secondary"></i>用户名
            </label>
          </div>

          <div class="form-floating mb-3">
            <input
              v-model="form.password"
              type="password"
              class="form-control"
              id="password"
              placeholder="请输入密码"
              required
            />
            <label for="password">
              <i class="fa-solid fa-lock me-2 text-secondary"></i>密码
            </label>
          </div>

          <div class="d-flex justify-content-between align-items-center mb-3">
            <!-- <div class="form-check">
              <input
                v-model="form.remember"
                type="checkbox"
                class="form-check-input"
                id="remember"
              />
              <label class="form-check-label small text-muted" for="remember">
                记住我
              </label>
            </div> -->
            <!-- <a href="#" class="small text-decoration-none">忘记密码？</a> -->
          </div>

          <button
            type="submit"
            class="btn btn-primary w-100 py-2 fw-semibold"
            :disabled="userStore.loading"
          >
            <i class="fa-solid fa-right-to-bracket me-2"></i>
            {{ userStore.loading ? '登录中...' : '登录' }}
          </button>
        </form>

        <!-- 注册引导 -->
        <div class="text-center mt-4">
          <p class="mb-0 text-muted">
            还没有账号？
            <RouterLink
              to="/register"
              class="text-primary fw-semibold text-decoration-none"
              >立即注册</RouterLink
            >
          </p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from "vue";
import { useUserStore } from "@/store/userStore";

const userStore = useUserStore();

const form = ref({
  name: "",
  password: "",
  remember: false,
});

// 提交登录表单
const onSubmit = async () => {
  await userStore.login({
    name: form.value.name,
    password: form.value.password,
  });
};
</script>

<style scoped>
/* 背景与整体布局 */
.login-page {
  background: linear-gradient(135deg, #f8fafc 0%, #eef2f7 100%);
  padding: 2rem;
}

/* 登录卡片样式 */
.login-card {
  border-radius: 18px;
  background-color: #ffffff;
  box-shadow: 0 12px 30px rgba(0, 0, 0, 0.08);
  transition: all 0.3s ease;
}

.login-card:hover {
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

/* 按钮 */
.btn-primary {
  background: linear-gradient(135deg, #2563eb, #3b82f6);
  border: none;
  border-radius: 10px;
  transition: all 0.3s ease;
}

.btn-primary:hover {
  background: linear-gradient(135deg, #1e40af, #2563eb);
  transform: translateY(-1px);
}

/* 注册链接 */
.text-primary:hover {
  text-decoration: underline;
}

/* 响应式 */
@media (max-width: 576px) {
  .login-card {
    padding: 2rem 1.5rem;
  }
  .form-floating label {
    font-size: 0.9rem;
  }
}
</style>
