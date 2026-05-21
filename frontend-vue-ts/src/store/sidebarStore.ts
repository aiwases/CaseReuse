import { defineStore } from "pinia";
import type { RouteRecordRaw } from "vue-router";

interface MenuItem {
  name: string;
  path: string;
  label: string;
  children?: MenuItem[];
}

interface ProjectMenuItem {
  id: number;
  name: string;
  process_type: string;
  path: string;
  children: MenuItem[];
}

interface SidebarState {
  activeProjects: ProjectMenuItem[];
  openMenus: string[];
}

export const useSidebarStore = defineStore("sidebar", {
  state: (): SidebarState => {
    // 从localStorage加载持久化数据
    const savedActiveProjects = localStorage.getItem("sidebarActiveProjects");
    const savedOpenMenus = localStorage.getItem("sidebarOpenMenus");
    
    return {
      activeProjects: savedActiveProjects ? JSON.parse(savedActiveProjects) : [],
      openMenus: savedOpenMenus ? JSON.parse(savedOpenMenus) : ["file", "project"]
    };
  },

  actions: {
    // 持久化状态到localStorage
    persistState() {
      localStorage.setItem("sidebarActiveProjects", JSON.stringify(this.activeProjects));
      localStorage.setItem("sidebarOpenMenus", JSON.stringify(this.openMenus));
    },

    // 添加项目到侧边栏
    addProjectToSidebar(project: { id: number; name: string; process_type: string }) {
      // 检查项目是否已存在
      const existingProject = this.activeProjects.find(item => item.id === project.id);
      if (existingProject) {
        return;
      }

      // 创建项目菜单项
      const projectPath = `/projects/${project.id}`;
      
      // 根据项目类型生成不同的子菜单
      let children = [];
      
      // 基础菜单
      children.push(
        { name: "document-detail", path: projectPath, label: "文档详情" }
      );
      
      // 如果是测试用例生成类型
      if (project.process_type === 'generation' || project.process_type === '测试用例生成') {
        children = children.concat([
          { name: "filter-rules", path: `${projectPath}/filter-rules`, label: "Filter rules" },
          { name: "extract-rule-elements", path: `${projectPath}/extract-rule-elements`, label: "Extract rule elements" },
          { name: "assemble-rules", path: `${projectPath}/assemble-rules`, label: "Assemble rules" },
          { name: "operationalize-rules", path: `${projectPath}/operationalize-rules`, label: "Operationalize rules" },
          { name: "mine-rule-relations", path: `${projectPath}/mine-rule-relations`, label: "Mine rule relations" },
          { name: "test-data-generation", path: `${projectPath}/test-data-generation`, label: "Test Data Generation" }
        ]);
      }
      // 如果是测试用例重用类型
      else if (project.process_type === 'reuse' || project.process_type === '测试用例重用') {
        children = [
          { name: "document-detail", path: `${projectPath}/reuse-detail`, label: "文档详情" },
          { name: "cascading-dependency-modeling", path: `${projectPath}/cascading-dependency-modeling`, label: "阶段I:Cascading Dependency Modeling" },
          { name: "cascading-effect-aware-reuse-update", path: `${projectPath}/cascading-effect-aware-reuse-update`, label: "阶段II:Cascading Effect-Aware Reuse and Update" },
          {
            name: "individual-steps",
            path: "#",
            label: "所有步骤",
            children: [
              { name: "independent-requirement-generation", path: `${projectPath}/independent-requirement-generation`, label: "Independent Requirement Generation" },
              { name: "test-scenario-synthesis", path: `${projectPath}/test-scenario-synthesis`, label: "Test Scenario Synthesis" },
              { name: "scenario-case-alignment", path: `${projectPath}/scenario-case-alignment`, label: "Scenario-Test Case Alignment" },
              { name: "regulatory-change-identification", path: `${projectPath}/regulatory-change-identification`, label: "Regulatory Change Identification" },
              { name: "cascading-impact-scope-analysis", path: `${projectPath}/cascading-impact-scope-analysis`, label: "Cascading Impact Scope Analysis" },
              { name: "test-suite-reuse-update", path: `${projectPath}/test-suite-reuse-update`, label: "Test Suite Reuse and Update" }
            ]
          }
        ];
      }
      
      const projectItem: ProjectMenuItem = {
        id: project.id,
        name: project.name,
        process_type: project.process_type,
        path: projectPath,
        children: children
      };

      // 添加到侧边栏
      this.activeProjects.push(projectItem);
      // 自动展开新添加的项目菜单
      this.openMenus.push(`project-${project.id}`);
      
      // 持久化状态
      this.persistState();
    },

    // 从侧边栏移除项目
    removeProjectFromSidebar(projectId: number) {
      const index = this.activeProjects.findIndex(item => item.id === projectId);
      if (index !== -1) {
        this.activeProjects.splice(index, 1);
        // 同时移除展开状态
        const menuKey = `project-${projectId}`;
        const menuIndex = this.openMenus.indexOf(menuKey);
        if (menuIndex !== -1) {
          this.openMenus.splice(menuIndex, 1);
        }
        
        // 持久化状态
        this.persistState();
      }
    },

    // 切换菜单展开/收起状态
    toggleMenu(menuName: string) {
      const index = this.openMenus.indexOf(menuName);
      if (index === -1) {
        this.openMenus.push(menuName);
      } else {
        this.openMenus.splice(index, 1);
      }
      
      // 持久化状态
      this.persistState();
    },

    // 清除所有激活项目
    clearActiveProjects() {
      this.activeProjects = [];
      
      // 持久化状态
      this.persistState();
    }
  }
});