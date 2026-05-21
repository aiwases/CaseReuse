Vue 3 + Vite + Pinia + Vue Router + Axios

npm install bootstrap
npm install vue-router pinia
npm install element-plus --save
npm install @element-plus/icons-vue

npm install marked
npm install dompurify
npm install pdfjs-dist（没用）
npm install jsmind（没用）
npm install mind-elixir --save（没用）
npm install echarts（没用）
npm install vue3-tree-org（没用）

frontend-vue-ts/
├── .gitignore
├── index.html
├── package-lock.json
├── package.json
├── README.md
├── tsconfig.app.json
├── tsconfig.json
├── tsconfig.node.json
├── vite.config.ts
├── public/
│   └── vite.svg
└── src/
    ├── App.vue
    ├── main.ts
    ├── style.css
    ├── api/
    │   ├── auth.ts
    │   ├── detail.ts
    │   ├── file.ts
    │   ├── index.ts
    │   ├── project.ts
    │   └── upload.ts
    ├── assets/
    │   └── css/
    │       ├── detail.css
    │       ├── project.css
    │       └── upload.css
    ├── components/
    │   └── NavBar.vue
    ├── layouts/
    │   ├── BaseLayout.vue
    │   ├── fileManage/
    │   │   ├── FileDeleteModal.vue
    │   │   └── FilePreviewModal.vue
    │   ├── projectDetail/
    │   │   ├── FileProcess.vue
    │   │   └── ProjectInfo.vue
    │   └── upload/
    │       └── FileUpload.vue
    ├── router/
    │   └── index.ts
    ├── store/
    │   ├── detailStore.ts
    │   ├── fileStore.ts
    │   ├── projectStore.ts
    │   ├── uploadStore.ts
    │   └── userStore.ts
    └── views/
        ├── CreatProjectPage.vue
        ├── FileManagePage.vue
        ├── HomePage.vue
        ├── LoginPage.vue
        ├── ProjectDetailPage.vue
        ├── ProjectManagePage.vue
        ├── RegisterPage.vue
        └── UploadPage.vue




