<template>
  <div class="test-scenario-synthesis-edit">
    <!-- 编辑对话框 -->
    <el-dialog
      v-model="dialogVisible"
      title="编辑场景块"
      width="80%"
      destroy-on-close
    >
      <div class="edit-container">
        <!-- 场景块编辑区域 -->
        <div class="edit-section">
          <h4>场景块详情</h4>
          <el-form :model="editingBlock" label-width="60px">
            <el-form-item label="场景块ID">
              <el-input v-model="editingBlock.id" placeholder="场景块ID" />
            </el-form-item>
            <el-form-item label="规则">
              <el-input v-model="editingBlock.rule" placeholder="规则" />
            </el-form-item>
            <el-form-item label="来源ID">
              <el-input v-model="editingBlock.sourceId" placeholder="来源ID" />
            </el-form-item>
            <el-form-item label="场景块文本">
              <el-input v-model="editingBlock.text" placeholder="场景块文本" />
            </el-form-item>
            
            <!-- 规则块编辑区域 -->
            <el-form-item label="规则块">
              <div class="block-list">
                <div
                  v-for="(ruleBlock, ruleBlockIndex) in editingBlock.blocks"
                  :key="ruleBlock.name || ruleBlockIndex"
                  class="block-item"
                >
                  <el-form :model="ruleBlock" label-width="60px">
                    <el-form-item label="块名称">
                      <el-input v-model="ruleBlock.name" placeholder="块名称" />
                    </el-form-item>
                    
                    <!-- IF 条件编辑 -->
                    <el-form-item label="IF条件">
                      <div class="condition-list">
                        <div
                          v-for="(condition, condIndex) in ruleBlock.if"
                          :key="`if-${condIndex}`"
                          class="condition-item"
                        >
                          <el-form :model="condition" label-width="50px">
                            <el-form-item label="字段">
                              <el-input v-model="condition.field" placeholder="字段" />
                            </el-form-item>
                            <el-form-item label="值">
                              <el-input v-model="condition.value" placeholder="值" />
                            </el-form-item>
                            <el-button
                              type="danger"
                              size="small"
                              @click="removeCondition(ruleBlockIndex, 'if', condIndex)"
                            >
                              删除条件
                            </el-button>
                          </el-form>
                        </div>
                        <el-button
                          type="primary"
                          size="small"
                          @click="addCondition(ruleBlockIndex, 'if')"
                        >
                          添加IF条件
                        </el-button>
                      </div>
                    </el-form-item>
                    
                    <!-- THEN 条件编辑 -->
                    <el-form-item label="THEN条件">
                      <div class="condition-list">
                        <div
                          v-for="(condition, condIndex) in ruleBlock.then"
                          :key="`then-${condIndex}`"
                          class="condition-item"
                        >
                          <el-form :model="condition" label-width="50px">
                            <el-form-item label="字段">
                              <el-input v-model="condition.field" placeholder="字段" />
                            </el-form-item>
                            <el-form-item label="值">
                              <el-input v-model="condition.value" placeholder="值" />
                            </el-form-item>
                            <el-button
                              type="danger"
                              size="small"
                              @click="removeCondition(ruleBlockIndex, 'then', condIndex)"
                            >
                              删除条件
                            </el-button>
                          </el-form>
                        </div>
                        <el-button
                          type="primary"
                          size="small"
                          @click="addCondition(ruleBlockIndex, 'then')"
                        >
                          添加THEN条件
                        </el-button>
                      </div>
                    </el-form-item>
                    
                    <el-button
                      type="danger"
                      size="small"
                      @click="removeBlock(ruleBlockIndex)"
                    >
                      删除规则块
                    </el-button>
                  </el-form>
                </div>
                <el-button
                  type="primary"
                  size="small"
                  @click="addBlock"
                >
                  添加规则块
                </el-button>
              </div>
            </el-form-item>
          </el-form>
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
import { ref, watch } from 'vue'
import { useReuseStore } from '@/store/reuseStore'

const reuseStore = useReuseStore()

// 定义props
const props = defineProps<{
  editingBlockData?: any
  blockIndex?: number
}>()

// 定义emit事件
const emit = defineEmits<{
  (e: 'update:block', data: any, index: number): void
}>()

// 对话框状态
const dialogVisible = ref(false)

const currentBlockIndex = ref<number | null>(null)

const originalBlockSnapshot = ref<any>(null)

// 编辑中的数据
const editingBlock = ref<any>({
  id: '',
  rule: '',
  sourceId: '',
  text: '',
  blocks: []
})

// 监听props变化，更新编辑数据
watch(() => props.editingBlockData, (newData) => {
  if (newData) {
    editingBlock.value = JSON.parse(JSON.stringify(newData))
  }
}, { deep: true })

// 打开编辑对话框
const openEdit = (block: any, index: number) => {
  editingBlock.value = JSON.parse(JSON.stringify(block))
  originalBlockSnapshot.value = JSON.parse(JSON.stringify(block))
  currentBlockIndex.value = index
  dialogVisible.value = true
}

const buildTextFromBlocks = (blocks: any[]) => {
  if (!Array.isArray(blocks) || blocks.length === 0) {
    return ''
  }

  return blocks
    .map((block) => {
      const ifText = Array.isArray(block.if) && block.if.length > 0
        ? `if ${block.if.map((condition: any) => `${condition.field} is ${condition.value}`).join(' and ')}`
        : 'if'
      const thenText = Array.isArray(block.then) && block.then.length > 0
        ? `then ${block.then.map((condition: any) => `${condition.field} is ${condition.value}`).join(' and ')}`
        : 'then'
      return `${ifText}\n${thenText}`
    })
    .join('\n') + '\n'
}

// 添加规则块
const addBlock = () => {
  editingBlock.value.blocks.push({
    name: '',
    if: [],
    then: []
  })
}

// 删除规则块
const removeBlock = (ruleBlockIndex: number) => {
  editingBlock.value.blocks.splice(ruleBlockIndex, 1)
}

// 添加条件
const addCondition = (ruleBlockIndex: number, type: 'if' | 'then') => {
  editingBlock.value.blocks[ruleBlockIndex][type].push({
    field: '',
    value: ''
  })
}

// 删除条件
const removeCondition = (ruleBlockIndex: number, type: 'if' | 'then', condIndex: number) => {
  editingBlock.value.blocks[ruleBlockIndex][type].splice(condIndex, 1)
}

// 保存更改
const saveChanges = () => {
  const payload = JSON.parse(JSON.stringify(editingBlock.value))
  const original = originalBlockSnapshot.value

  const originalText = original?.text ?? ''
  const currentText = payload.text ?? ''
  const originalBlocks = JSON.stringify(original?.blocks ?? [])
  const currentBlocks = JSON.stringify(payload.blocks ?? [])
  const blocksChanged = originalBlocks !== currentBlocks
  const textChanged = currentText !== originalText

  if (blocksChanged && !textChanged) {
    payload.text = buildTextFromBlocks(payload.blocks || [])
  }

  const targetIndex = currentBlockIndex.value ?? props.blockIndex ?? -1
  emit('update:block', payload, targetIndex)
  dialogVisible.value = false
}

// 暴露方法给父组件
defineExpose({
  openEdit
})
</script>

<style scoped>
.test-scenario-synthesis-edit {
  width: 100%;
}

.edit-container {
  display: flex;
  flex-direction: column;
  gap: 24px;
  width: 100%;
}

.edit-section {
  border: 1px solid #ebeef5;
  border-radius: 8px;
  padding: 16px;
  background-color: #fafafa;
  width: 100%;
}

.edit-section h4 {
  margin: 0 0 16px 0;
  font-size: 14px;
  font-weight: 500;
  color: #303133;
  padding-bottom: 8px;
  border-bottom: 1px solid #e4e7ed;
}

.block-list,
.condition-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
  margin-bottom: 16px;
  width: 100%;
}

.block-item,
.condition-item {
  border: 1px solid #e4e7ed;
  border-radius: 6px;
  padding: 12px;
  background-color: #ffffff;
  width: 100%;
}

.dialog-footer {
  width: 100%;
  display: flex;
  justify-content: flex-end;
  gap: 8px;
}

/* 修复Element-UI表单label对齐和宽度问题 */
:deep(.el-form-item) {
  margin-bottom: 16px;
  width: 100%;
}

:deep(.el-form-item__label) {
  text-align: right;
  padding-right: 12px;
}

:deep(.el-form-item__content) {
  width: calc(100% - 60px);
}

:deep(.el-input__inner) {
  width: 100%;
}
</style>
