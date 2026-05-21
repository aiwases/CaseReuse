import { createRouter, createWebHistory } from "vue-router";
import type { RouteRecordRaw } from "vue-router";
import { useSidebarStore } from "@/store/sidebarStore";
import { useDetailStore } from "@/store/detailStore";
import { useUserStore } from "@/store/userStore";

import BaseLayout from "@/layouts/BaseLayout.vue";

// 页面组件
import HomePage from "@/views/HomePage.vue";
import UploadPage from "@/views/UploadPage.vue";
import FileManagePage from "@/views/FileManagePage.vue";
import ProjectManagePage from "@/views/ProjectManagePage.vue";
import LoginPage from "@/views/LoginPage.vue";
import RegisterPage from "@/views/RegisterPage.vue";
import CreatProjectPage from "@/views/CreatProjectPage.vue";
import SliceFilterPage from "@/views/ProjectDetail/SliceFilterPage.vue";
import AnnotationPage from "@/views/ProjectDetail/AnnotationPage.vue";
import RuleSynthesisPage from "@/views/ProjectDetail/RuleSynthesisPage.vue";
import CaseGenerationPage from "@/views/ProjectDetail/CaseGenerationPage.vue";
import DocumentDetailPage from "@/views/ProjectDetail/DocumentDetailPage.vue";
import OperationalizeRulesPage from "@/views/ProjectDetail/OperationalizeRulesPage.vue";
import MineRuleRelationsPage from "@/views/ProjectDetail/MineRuleRelationsPage.vue";
// 测试用例重用类型项目页面组件
import IndependentRequirementGeneration from "@/views/reuse/IndependentRequirementGeneration.vue";
import TestScenarioSynthesis from "@/views/reuse/TestScenarioSynthesis.vue";
import ScenarioCaseAlignment from "@/views/reuse/ScenarioCaseAlignment.vue";
import CascadingImpactScopeAnalysis from "@/views/reuse/CascadingImpactScopeAnalysis.vue";
import ReuseDocumentDetailPage from "@/views/reuse/ReuseDocumentDetailPage.vue";
import RegulatoryChangeIdentification from "@/views/reuse/RegulatoryChangeIdentification.vue";
import TestSuiteReuseUpdate from "@/views/reuse/TestSuiteReuseUpdate.vue";
import CascadingDependencyModeling from "@/views/reuse/CascadingDependencyModeling.vue";
import CascadingEffectAwareReuseUpdate from "@/views/reuse/CascadingEffectAwareReuseUpdate.vue";



const routes: RouteRecordRaw[] = [
  // 登录 & 注册（不带导航栏）
  { path: "/login", component: LoginPage },
  { path: "/register", component: RegisterPage },

  // 主业务页面（带导航栏）
  {
    path: "/",
    component: BaseLayout,
    children: [
      { path: "", name: "home", component: HomePage },
      { path: "upload", name: "upload", component: UploadPage },
      { path: "file-manage", name: "file-manage", component: FileManagePage },
      { path: "create-project", name: "create-project", component: CreatProjectPage },

      // ⭐ 项目管理模块（不要再嵌套 BaseLayout）
      {
        path: "projects",
        children: [
          { path: "", name: "ProjectManage", component: ProjectManagePage },
          { path: ":id", name: "DocumentDetail", component: DocumentDetailPage, props: true },
          { path: ":id/reuse-detail", name: "ReuseDocumentDetail", component: ReuseDocumentDetailPage, props: true },
          { path: ":id/filter-rules", name: "FilterRules", component: SliceFilterPage, props: true },
          { path: ":id/extract-rule-elements", name: "ExtractRuleElements", component: AnnotationPage, props: true },
          { path: ":id/assemble-rules", name: "AssembleRules", component: RuleSynthesisPage, props: true },
          { path: ":id/operationalize-rules", name: "OperationalizeRules", component: OperationalizeRulesPage, props: true },
          { path: ":id/mine-rule-relations", name: "MineRuleRelations", component: MineRuleRelationsPage, props: true },
          { path: ":id/test-data-generation", name: "TestDataGeneration", component: CaseGenerationPage, props: true },
          // 测试用例重用类型项目路由
          { path: ":id/independent-requirement-generation", name: "IndependentRequirementGeneration", component: IndependentRequirementGeneration, props: true },
          { path: ":id/test-scenario-synthesis", name: "TestScenarioSynthesis", component: TestScenarioSynthesis, props: true },
          { path: ":id/scenario-case-alignment", name: "ScenarioCaseAlignment", component: ScenarioCaseAlignment, props: true },
          { path: ":id/regulatory-change-identification", name: "RegulatoryChangeIdentification", component: RegulatoryChangeIdentification, props: true },
          { path: ":id/cascading-impact-scope-analysis", name: "CascadingImpactScopeAnalysis", component: CascadingImpactScopeAnalysis, props: true },
          { path: ":id/test-suite-reuse-update", name: "TestSuiteReuseUpdate", component: TestSuiteReuseUpdate, props: true },
          { path: ":id/cascading-dependency-modeling", name: "CascadingDependencyModeling", component: CascadingDependencyModeling, props: true },
          { path: ":id/cascading-effect-aware-reuse-update", name: "CascadingEffectAwareReuseUpdate", component: CascadingEffectAwareReuseUpdate, props: true },
        ],
      },
    ],
  },

  // 捕获所有未匹配的路径
  { path: "/:pathMatch(.*)*", redirect: "/" },
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

// 添加路由导航守卫，实现登录检查和项目菜单的自动加载
router.beforeEach(async (to, from, next) => {
  // 检查用户是否已登录（通过localStorage中的token）
  const isLoggedIn = !!localStorage.getItem('token');
  
  // 不需要登录的页面
  const publicPages = ['/login', '/register'];
  
  // 如果未登录且访问的不是公开页面，则重定向到登录页面
  if (!isLoggedIn && !publicPages.includes(to.path)) {
    return next('/login');
  }
  
  // 如果是项目相关的路由
  if (to.path.startsWith('/projects/')) {
    const sidebarStore = useSidebarStore();
    const detailStore = useDetailStore();
    
    // 提取项目ID
    const projectId = parseInt(to.params.id as string);
    
    if (projectId) {
      // 检查项目是否已在侧边栏中
      const projectExists = sidebarStore.activeProjects.find(p => p.id === projectId);
      
      if (!projectExists) {
        try {
          // 从API获取项目信息
          const projectProgress = await detailStore.fetchProjectProgress(projectId);
          
          // 将项目添加到侧边栏
          sidebarStore.addProjectToSidebar({
            id: projectId,
            name: projectProgress.name, // 假设API返回的项目信息包含名称
            process_type: projectProgress.process_type // 假设API返回的项目信息包含类型
          });
        } catch (error) {
          console.error('获取项目信息失败:', error);
          // 即使获取失败，也继续导航
        }
      }
    }
  }
  
  next();
});

export default router;
