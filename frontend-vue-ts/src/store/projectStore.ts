import { defineStore } from "pinia";
import { fetchProjectsApi, deleteProjectApi } from "@/api/project";
import { updateProjectInfoApi } from "@/api/detail";
import type { ProjectItem } from "@/api/project";
interface ProjectState {
  projects: ProjectItem[];
  stats: Record<string, any>;
  pagination: {
    page: number;
    per_page: number;
    total: number;
    pages: number;
    has_prev: boolean;
    has_next: boolean;
    prev_num: number | null;
    next_num: number | null;
    iter_pages: (number | null)[];
  } | null;
  loading: boolean;
}

export const useProjectStore = defineStore("project", {
  state: (): ProjectState => ({
    projects: [],
    stats: {},
    pagination: null,
    loading: false,
  }),

  actions: {
    async fetchProjects(params: {
      page?: number;
      perPage?: number;
      sort?: string;
      keyword?: string;
      searchType?: string;
      status?: string;
      file_id?: string;
    }) {
      this.loading = true;
      try {
        const queryParams: any = {
          page: params.page ?? 1,
          per_page: params.perPage ?? 9,
          sort: params.sort ?? "updated_desc",
          search_type: params.searchType ?? "project",
        };

        if (params.file_id) {
          queryParams.file_id = params.file_id
        }

        if (params.keyword) {
          if (params.searchType === "file") queryParams.filename = params.keyword;
          else queryParams.keyword = params.keyword;
        }

        if (params.status) {
          queryParams.status = params.status;
        }

        const data = await fetchProjectsApi(queryParams);
        this.projects = data.data.projects.items;
        this.stats = data.data.stats;
        this.pagination = {
          page: data.data.projects.page,
          per_page: data.data.projects.per_page,
          total: data.data.projects.total,
          pages: data.data.projects.pages,
          has_prev: data.data.projects.has_prev,
          has_next: data.data.projects.has_next,
          prev_num: data.data.projects.prev_num,
          next_num: data.data.projects.next_num,
          iter_pages: data.data.projects.iter_pages,
        };
      } catch (err) {
        console.error("❌ 获取项目列表失败:", err);
      } finally {
        this.loading = false;
      }
    },

    async updateProjectInfo(projectId: number | string, name: string, description: string) {
      try {
        const response = await updateProjectInfoApi(projectId, name, description);
        // 更新本地项目列表中的项目信息
        const index = this.projects.findIndex(p => p.id === Number(projectId));
        if (index !== -1) {
          this.projects[index].name = name;
          this.projects[index].description = description;
        }
        return response.data;
      } catch (err) {
        console.error("❌ 更新项目信息失败:", err);
        throw err;
      }
    },

    async deleteProject(projectId: number | string) {
      try {
        this.loading = true;
        await deleteProjectApi(projectId);
        // 从本地项目列表中移除被删除的项目
        this.projects = this.projects.filter(p => p.id !== Number(projectId));
        return true;
      } catch (err) {
        console.error("❌ 删除项目失败:", err);
        throw err;
      } finally {
        this.loading = false;
      }
    },
  },
});
