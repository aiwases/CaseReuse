// src/store/userStore.ts
import { defineStore } from "pinia";
import { ref } from "vue";
import { useRouter } from "vue-router";
import { loginApi, registerApi, checkUsernameApi } from "@/api/auth";

export const useUserStore = defineStore("user", () => {
  const isLoggedIn = ref(!!localStorage.getItem("token"));
  const username = ref(localStorage.getItem("username") || "");
  const loading = ref(false);
  const router = useRouter();

  /* ------------------- 登录 ------------------- */
  async function login(formData: { name: string; password: string }) {
    loading.value = true;
    try {
      const res = await loginApi(formData);
      if (res.data.success) {
        localStorage.setItem("token", res.data.token);
        localStorage.setItem("username", formData.name);
        isLoggedIn.value = true;
        username.value = formData.name;
        router.push("/");
      } else {
        alert("登录失败：" + res.data.message);
      }
    } catch (err) {
      console.error("登录错误:", err);
      alert("登录失败，请检查网络");
    } finally {
      loading.value = false;
    }
  }

  /* ------------------- 注册 ------------------- */
  async function register(formData: { name: string; password: string; email?: string }) {
    loading.value = true;
    try {
      const res = await registerApi(formData);

      if (res.data.success) {
        // 注册成功自动登录
        localStorage.setItem("token", res.data.token);
        localStorage.setItem("username", formData.name);

        isLoggedIn.value = true;
        username.value = formData.name;

        alert("注册成功！");
        router.push("/");
      } else {
        alert("注册失败：" + res.data.message);
      }
    } catch (err) {
      console.error("注册错误:", err);
      alert("注册失败，请检查网络");
    } finally {
      loading.value = false;
    }
  }

  /* ------------------- 检查用户名是否存在 ------------------- */
  async function checkUsername(name: string): Promise<boolean> {
    if (!name) return false;

    try {
      const res = await checkUsernameApi({ name });
      // exists = true 表示已存在，不能注册
      return res.data.exists;
    } catch (err) {
      console.error("检查用户名错误:", err);
      return false;
    }
  }

  /* ------------------- 登出 ------------------- */
  function logout() {
    localStorage.removeItem("token");
    localStorage.removeItem("username");
    isLoggedIn.value = false;
    username.value = "";
    router.push("/login");
  }

  return {
    isLoggedIn,
    username,
    loading,
    login,
    register,
    checkUsername,
    logout
  };
});
