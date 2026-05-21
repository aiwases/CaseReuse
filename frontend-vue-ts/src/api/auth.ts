// src/api/auth.ts
import service from "./index";

// 登录
export function loginApi(data: { name: string; password: string }) {
  return service.post("/login", data);
}

// 注册
export function registerApi(data: { name: string; password: string; email?: string }) {
  return service.post("/register", data);
}

// 检查用户名是否已存在
export function checkUsernameApi(data: { name: string }) {
  return service.post("/check_username", data);
}
