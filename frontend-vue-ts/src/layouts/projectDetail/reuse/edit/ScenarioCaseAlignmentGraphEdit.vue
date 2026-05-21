<template>
  <div class="scenario-case-alignment-graph-edit">
    <!-- 编辑对话框 -->
    <el-dialog
      v-model="dialogVisible"
      title="编辑场景-测试用例对齐关系"
      width="80%"
      destroy-on-close
    >
      <div class="edit-container">
        <!-- 节点编辑区域 -->
        <div class="edit-section">
          <h4>节点管理</h4>
          <div class="node-list">
            <div
              v-for="(node, index) in editingNodes"
              :key="node.id"
              class="node-item"
            >
              <el-form :model="node" label-width="80px">
                <el-form-item label="节点ID">
                  <el-input v-model="node.id" disabled />
                </el-form-item>
                <el-form-item label="节点名称">
                  <el-input v-model="node.name" placeholder="节点名称" />
                </el-form-item>
                <el-form-item label="节点类型">
                  <el-select v-model="node.category" placeholder="选择节点类型">
                    <el-option label="规则" value="rule" />
                    <el-option label="需求" value="requirement" />
                    <el-option label="场景" value="scenario" />
                    <el-option label="测试用例" value="test case" />
                  </el-select>
                </el-form-item>
                <el-button
                  type="danger"
                  size="small"
                  @click="removeNode(index)"
                >
                  删除节点
                </el-button>
              </el-form>
            </div>
          </div>
          <el-button type="primary" size="small" @click="addNode">
            添加节点
          </el-button>
        </div>

        <!-- 链接编辑区域 -->
        <div class="edit-section">
          <h4>链接管理</h4>
          <div class="link-list">
            <div
              v-for="(link, index) in editingLinks"
              :key="index"
              class="link-item"
            >
              <el-form :model="link" label-width="80px">
                <el-form-item label="源节点">
                  <el-select v-model="link.source" placeholder="选择源节点">
                    <el-option
                      v-for="node in editingNodes"
                      :key="node.id"
                      :label="node.name"
                      :value="node.id"
                    />
                  </el-select>
                </el-form-item>
                <el-form-item label="目标节点">
                  <el-select v-model="link.target" placeholder="选择目标节点">
                    <el-option
                      v-for="node in editingNodes"
                      :key="node.id"
                      :label="node.name"
                      :value="node.id"
                    />
                  </el-select>
                </el-form-item>
                <el-button
                  type="danger"
                  size="small"
                  @click="removeLink(index)"
                >
                  删除链接
                </el-button>
              </el-form>
            </div>
          </div>
          <el-button type="primary" size="small" @click="addLink">
            添加链接
          </el-button>
        </div>
      </div>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="dialogVisible = false">取消</el-button>
          <el-button type="primary" @click="saveChanges">保存</el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed } from 'vue'
import { useReuseStore } from '@/store/reuseStore'

const reuseStore = useReuseStore()

// 对话框状态
const dialogVisible = ref(false)

// 编辑中的数据
const editingNodes = ref<any[]>([])
const editingLinks = ref<any[]>([])

// 打开编辑对话框
const openEdit = () => {
  const alignmentData = reuseStore.getScenarioCaseAlignments
  if (!alignmentData) return
  
  // 深拷贝数据
  editingNodes.value = JSON.parse(JSON.stringify(alignmentData.nodes || []))
  editingLinks.value = JSON.parse(JSON.stringify(alignmentData.links || []))
  
  dialogVisible.value = true
}

// 添加节点
const addNode = () => {
  editingNodes.value.push({
    id: `node_${Date.now()}`,
    name: '新节点',
    category: 'rule'
  })
}

// 删除节点
const removeNode = (index: number) => {
  const nodeId = editingNodes.value[index].id
  editingNodes.value.splice(index, 1)
  
  // 同时删除与该节点相关的链接
  editingLinks.value = editingLinks.value.filter(link => 
    link.source !== nodeId && link.target !== nodeId
  )
}

// 添加链接
const addLink = () => {
  editingLinks.value.push({
    source: '',
    target: ''
  })
}

// 删除链接
const removeLink = (index: number) => {
  editingLinks.value.splice(index, 1)
}

// 保存更改
const saveChanges = () => {
  const alignmentData = {
    nodes: editingNodes.value,
    links: editingLinks.value
  }
  
  // 更新store中的数据
  reuseStore.updateScenarioCaseAlignments(alignmentData)
  dialogVisible.value = false
}

// 暴露方法给父组件
defineExpose({
  openEdit
})
</script>

<style scoped>
.scenario-case-alignment-graph-edit {
  width: 100%;
}

.edit-container {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.edit-section {
  border: 1px solid #ebeef5;
  border-radius: 8px;
  padding: 16px;
  background-color: #fafafa;
}

.edit-section h4 {
  margin: 0 0 16px 0;
  font-size: 14px;
  font-weight: 500;
  color: #303133;
  padding-bottom: 8px;
  border-bottom: 1px solid #e4e7ed;
}

.node-list,
.link-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
  margin-bottom: 16px;
}

.node-item,
.link-item {
  border: 1px solid #e4e7ed;
  border-radius: 6px;
  padding: 12px;
  background-color: #ffffff;
}

.node-item .el-form,
.link-item .el-form {
  margin-bottom: 0;
}

.dialog-footer {
  width: 100%;
  display: flex;
  justify-content: flex-end;
  gap: 8px;
}
</style>