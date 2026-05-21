// src/api/index.ts
import axios from "axios";

const service = axios.create({
  baseURL: "http://localhost:5000", // 可通过环境变量配置
  timeout: 10000,
  withCredentials: true,
});

// 请求拦截器
service.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem("token");
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// 响应拦截器
service.interceptors.response.use(
  (response) => response,
  (error) => {
    console.error("API Error:", error);
    
    // 处理认证失败情况（401状态码）
    if (error.response && error.response.status === 401) {
      // 清除本地存储的登录信息
      localStorage.removeItem('token');
      localStorage.removeItem('username');
      
      // 重定向到登录页面
      window.location.href = '/login';
    }
    
    return Promise.reject(error);
  }
);

export default service;
