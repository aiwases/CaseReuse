// src/api/project.ts
import axios from "@/api";

export interface ProjectParams {
  page?: number;
  per_page?: number;
  sort?: string;
  search_type?: string;
  keyword?: string;
  filename?: string;
  status?: string;
  file_id?: string;
}

export interface ProjectItem {
  id: number;
  description: string;
  name: string;
  status: string;
  process_type: string;
  created_at: string;
  updated_at: string;
  [key: string]: any;
}

export interface Pagination {
  items: ProjectItem[];
  page: number;
  per_page: number;
  total: number;
  pages: number;
  has_prev: boolean;
  has_next: boolean;
  prev_num: number | null;
  next_num: number | null;
  iter_pages: (number | null)[];
}

export interface ProjectResponse {
  projects: Pagination;
  stats: Record<string, number>;
}

export const fetchProjectsApi = (params: ProjectParams) =>{
  return axios.get("/projects", { params });
}

export const fetchProjectDetailApi = (id: number | string) =>
  axios.get(`/projects/${id}`);

export const deleteProjectApi = (id: number | string) =>
  axios.delete(`/delete_project/${id}`);
