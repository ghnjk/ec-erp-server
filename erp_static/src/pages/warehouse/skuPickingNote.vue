<template>
  <div>
    <t-card>
      <div class="search-container" style="margin-bottom: 16px;">
        <t-form layout="inline">
          <t-form-item label="SKU搜索">
            <t-input 
              v-model="searchSku" 
              placeholder="请输入SKU进行搜索"
              style="width: 200px;"
              @enter="onSearch"
              clearable
            />
          </t-form-item>
          <t-form-item>
            <t-button theme="primary" @click="onSearch">搜索</t-button>
            <t-button theme="default" @click="onShowAddDialog">
          新增拣货备注
        </t-button>
          </t-form-item>
        </t-form>
      </div>
      
      <div class="table-container">
        <t-table
          :columns="noteTableColumns"
          :data="noteTableData"
          :loading="noteTableLoading"
          bordered
          hover
          row-key="sku"
          stripe
        >
          <template #erp_sku_image_url="{ row }">
            <t-image :src="row.erp_sku_image_url" :style="{ width: '60px', height: '60px' }" />
          </template>
        </t-table>
        <t-pagination
          v-model="paginationCurrentPage"
          v-model:pageSize="paginationPageSize"
          :page-size-options="paginationPageSizeOptions"
          :total="paginationTotalCount"
          class="pagination"
          @change="onPaginationChange"
        />
      </div>
    </t-card>

    <t-dialog
      v-model:visible="addDialogVisible"
      header="新增拣货备注"
      width="600px"
      :confirm-btn="{ content: '保存', loading: addDialogLoading }"
      @confirm="onConfirmAdd"
      @cancel="onCancelAdd"
    >
      <t-form
        ref="addFormRef"
        :data="addFormData"
        :rules="addFormRules"
        label-align="left"
        label-width="120px"
      >
        <t-form-item label="SKU" name="sku">
          <t-input v-model="addFormData.sku" placeholder="请输入SKU" />
        </t-form-item>
        
        <t-form-item label="拣货单位数量" name="picking_unit">
          <t-input-number 
            v-model="addFormData.picking_unit" 
            :min="1"
            placeholder="请输入1拣货单位=多少sku"
          />
        </t-form-item>
        
        <t-form-item label="拣货单位名" name="picking_unit_name">
          <t-input v-model="addFormData.picking_unit_name" placeholder="请输入拣货单位名" />
        </t-form-item>
        
        <t-form-item label="拣货SKU名" name="picking_sku_name">
          <t-input v-model="addFormData.picking_sku_name" placeholder="请输入拣货SKU名" />
        </t-form-item>
        
        <t-form-item label="是否支持PKG打包" name="support_pkg_picking">
          <t-select 
            v-model="addFormData.support_pkg_picking" 
            placeholder="请选择是否支持PKG打包"
            :options="[
              { label: '否', value: false },
              { label: '是', value: true }
            ]"
          />
        </t-form-item>
        
        <t-form-item 
          v-if="addFormData.support_pkg_picking" 
          label="PKG打包单位数量" 
          name="pkg_picking_unit"
          :rules="addFormData.support_pkg_picking ? [{ required: true, message: 'PKG打包单位数量不能为空' }] : []"
        >
          <t-input-number 
            v-model="addFormData.pkg_picking_unit" 
            :min="1"
            placeholder="请输入1 PKG=多少SKU"
          />
        </t-form-item>
        
        <t-form-item 
          v-if="addFormData.support_pkg_picking" 
          label="PKG打包单位名" 
          name="pkg_picking_unit_name"
          :rules="addFormData.support_pkg_picking ? [{ required: true, message: 'PKG打包单位名不能为空' }] : []"
        >
          <t-input v-model="addFormData.pkg_picking_unit_name" placeholder="请输入PKG打包单位名" />
        </t-form-item>
      </t-form>
    </t-dialog>
  </div>
</template>

<script lang="ts">
export default {
  name: 'SkuPickingNote',
};
</script>
<script lang="ts" setup>
import { ref, onMounted } from 'vue';
import { InputNumber, Select, Input, MessagePlugin, Dialog, Form, FormItem, Button } from 'tdesign-vue-next';
import { savePurchaseOrder, searchPurchaseOrder } from '@/apis/supplierApis';
import { searchManualMarkSkuPickingNote, submitManualMarkSkuPickingNote } from '@/apis/warehouseApis';

const noteTableColumns = [
  {
    width: 60,
    colKey: 'erp_sku_image_url',
    title: '商品图片',
    align: 'center',
  },
  {
    width: 60,
    colKey: 'erp_sku_name',
    title: 'sku',
    align: 'center',
  },
  {
    width: 80,
    colKey: 'sku',
    title: 'sku',
    align: 'center',
  },
  {
    width: 80,
    colKey: 'picking_unit',
    title: '1拣货单位=多少sku?',
    // 编辑状态相关配置，全部集中在 edit
    edit: {
      // 1. 支持任意组件。需保证组件包含 `value` 和 `onChange` 两个属性，且 onChange 的第一个参数值为 new value。
      // 2. 如果希望支持校验，组件还需包含 `status` 和 `tips` 属性。具体 API 含义参考 Input 组件
      component: InputNumber,
      // props, 透传全部属性到 Input 组件。可以是一个函数，不同行有不同的 props 属性 时，使用 Function）
      props: {
        autofocus: true,
      },
      // 触发校验的时机（when to validate)
      validateTrigger: 'change',
      // 除了点击非自身元素退出编辑态之外，还有哪些事件退出编辑态
      abortEditOnEvent: ['onEnter', 'onBlur'],
      // 编辑完成，退出编辑态后触发
      onEdited: async (context) => {
        console.log(context);
        await onSavePickingNote(context.newRowData);
      },
      // 校验规则，此处同 Form 表单。https://tdesign.tencent.com/vue-next/components/form
      rules: [
        {
          required: true,
          message: '不能为空',
        },
      ],
      // 默认是否为编辑状态
      defaultEditable: false,
    },
    align: 'center',
  },
  {
    width: 60,
    colKey: 'picking_unit_name',
    title: '拣货单位名',
    // 编辑状态相关配置，全部集中在 edit
    edit: {
      // 1. 支持任意组件。需保证组件包含 `value` 和 `onChange` 两个属性，且 onChange 的第一个参数值为 new value。
      // 2. 如果希望支持校验，组件还需包含 `status` 和 `tips` 属性。具体 API 含义参考 Input 组件
      component: Input,
      // props, 透传全部属性到 Input 组件。可以是一个函数，不同行有不同的 props 属性 时，使用 Function）
      props: {
        autofocus: true,
      },
      // 触发校验的时机（when to validate)
      validateTrigger: 'change',
      // 除了点击非自身元素退出编辑态之外，还有哪些事件退出编辑态
      abortEditOnEvent: ['onEnter', 'onBlur'],
      // 编辑完成，退出编辑态后触发
      onEdited: async (context) => {
        console.log(context);
        await onSavePickingNote(context.newRowData);
      },
      // 校验规则，此处同 Form 表单。https://tdesign.tencent.com/vue-next/components/form
      rules: [
        {
          required: true,
          message: '不能为空',
        },
      ],
      // 默认是否为编辑状态
      defaultEditable: false,
    },
    align: 'center',
  },
  {
    width: 80,
    colKey: 'picking_sku_name',
    title: '拣货SKU名',
    // 编辑状态相关配置，全部集中在 edit
    edit: {
      // 1. 支持任意组件。需保证组件包含 `value` 和 `onChange` 两个属性，且 onChange 的第一个参数值为 new value。
      // 2. 如果希望支持校验，组件还需包含 `status` 和 `tips` 属性。具体 API 含义参考 Input 组件
      component: Input,
      // props, 透传全部属性到 Input 组件。可以是一个函数，不同行有不同的 props 属性 时，使用 Function）
      props: {
        autofocus: true,
      },
      // 触发校验的时机（when to validate)
      validateTrigger: 'change',
      // 除了点击非自身元素退出编辑态之外，还有哪些事件退出编辑态
      abortEditOnEvent: ['onEnter', 'onBlur'],
      // 编辑完成，退出编辑态后触发
      onEdited: async (context) => {
        console.log(context);
        await onSavePickingNote(context.newRowData);
      },
      // 校验规则，此处同 Form 表单。https://tdesign.tencent.com/vue-next/components/form
      rules: [
        {
          required: true,
          message: '不能为空',
        },
      ],
      // 默认是否为编辑状态
      defaultEditable: false,
    },
    align: 'center',
  },
  {
    width: 80,
    colKey: 'support_pkg_picking',
    title: '是否支持PKG打包',
    // 编辑状态相关配置，全部集中在 edit
    edit: {
      // 1. 支持任意组件。需保证组件包含 `value` 和 `onChange` 两个属性，且 onChange 的第一个参数值为 new value。
      // 2. 如果希望支持校验，组件还需包含 `status` 和 `tips` 属性。具体 API 含义参考 Input 组件
      component: Select,
      // props, 透传全部属性到 Input 组件。可以是一个函数，不同行有不同的 props 属性 时，使用 Function）
      props: {
        options: [
          { label: '否', value: false },
          { label: '是', value: true },
        ],
      },
      // 除了点击非自身元素退出编辑态之外，还有哪些事件退出编辑态
      abortEditOnEvent: ['onEnter', 'onBlur', 'onChange'],
      on: (editContext) => ({
        onChange: (params) => {
          console.log('status changed', editContext, params);
        },
      }),
      // 除了点击非自身元素退出编辑态之外，还有哪些事件退出编辑态
      // abortEditOnEvent: ['onChange'],
      // 编辑完成，退出编辑态后触发
      onEdited: async (context) => {
        console.log(context);
        await onSavePickingNote(context.newRowData);
      },
      defaultEditable: true,
    },
    align: 'center',
  },
  {
    width: 80,
    colKey: 'pkg_picking_unit',
    title: '1 PKG=多少SKU',
    // 编辑状态相关配置，全部集中在 edit
    edit: {
      // 1. 支持任意组件。需保证组件包含 `value` 和 `onChange` 两个属性，且 onChange 的第一个参数值为 new value。
      // 2. 如果希望支持校验，组件还需包含 `status` 和 `tips` 属性。具体 API 含义参考 Input 组件
      component: InputNumber,
      // props, 透传全部属性到 Input 组件。可以是一个函数，不同行有不同的 props 属性 时，使用 Function）
      props: {
        autofocus: true,
      },
      // 触发校验的时机（when to validate)
      validateTrigger: 'change',
      // 除了点击非自身元素退出编辑态之外，还有哪些事件退出编辑态
      abortEditOnEvent: ['onEnter', 'onBlur'],
      // 编辑完成，退出编辑态后触发
      onEdited: async (context) => {
        console.log(context);
        await onSavePickingNote(context.newRowData);
      },
      // 校验规则，此处同 Form 表单。https://tdesign.tencent.com/vue-next/components/form
      rules: [],
      // 默认是否为编辑状态
      defaultEditable: false,
    },
    align: 'center',
  },
  {
    width: 60,
    colKey: 'pkg_picking_unit_name',
    title: 'PKG打包单位名',
    // 编辑状态相关配置，全部集中在 edit
    edit: {
      // 1. 支持任意组件。需保证组件包含 `value` 和 `onChange` 两个属性，且 onChange 的第一个参数值为 new value。
      // 2. 如果希望支持校验，组件还需包含 `status` 和 `tips` 属性。具体 API 含义参考 Input 组件
      component: Input,
      // props, 透传全部属性到 Input 组件。可以是一个函数，不同行有不同的 props 属性 时，使用 Function）
      props: {
        autofocus: true,
      },
      // 触发校验的时机（when to validate)
      validateTrigger: 'change',
      // 除了点击非自身元素退出编辑态之外，还有哪些事件退出编辑态
      abortEditOnEvent: ['onEnter', 'onBlur'],
      // 编辑完成，退出编辑态后触发
      onEdited: async (context) => {
        console.log(context);
        await onSavePickingNote(context.newRowData);
      },
      // 校验规则，此处同 Form 表单。https://tdesign.tencent.com/vue-next/components/form
      rules: [],
      // 默认是否为编辑状态
      defaultEditable: false,
    },
    align: 'center',
  },
];
const noteTableData = ref([]);
const noteTableLoading = ref(false);

const paginationCurrentPage = ref(1);
const paginationTotalCount = ref(0);
const paginationPageSize = ref(10);
const paginationPageSizeOptions = [10, 20, 50, 100];

const addDialogVisible = ref(false);
const addDialogLoading = ref(false);
const addFormRef = ref(null);
const addFormData = ref({
  sku: '',
  picking_unit: 1,
  picking_unit_name: '',
  picking_sku_name: '',
  support_pkg_picking: false,
  pkg_picking_unit: 1,
  pkg_picking_unit_name: '',
});
const addFormRules = ref({
  sku: [{ required: true, message: 'SKU不能为空' }],
  picking_unit: [{ required: true, message: '拣货单位数量不能为空' }],
  picking_unit_name: [{ required: true, message: '拣货单位名不能为空' }],
  picking_sku_name: [{ required: true, message: '拣货SKU名不能为空' }],
  support_pkg_picking: [{ required: true, message: '请选择是否支持PKG打包' }],
});

const searchSku = ref('');

onMounted(async () => {
  await onSearchPickingNote();
});
const onPaginationChange = async ({ current, pageSize }) => {
  paginationCurrentPage.value = current;
  paginationPageSize.value = pageSize;
  await onSearchPickingNote();
};
const onSearch = async () => {
  paginationCurrentPage.value = 1;
  await onSearchPickingNote();
};
const onSearchPickingNote = async () => {
  const req = {
    current_page: paginationCurrentPage.value,
    page_size: paginationPageSize.value,
    search_sku: searchSku.value,
  };
  noteTableLoading.value = true;
  try {
    const res = await searchManualMarkSkuPickingNote(req);
    paginationTotalCount.value = res.total;
    noteTableData.value = res.list;
  } catch (e) {
    console.error(e);
    await MessagePlugin.error(`查询备注异常: ${e}`);
  }
  noteTableLoading.value = false;
};
const onSavePickingNote = async (pickingNote) => {
  let isValid = true;
  if (pickingNote.picking_unit <= 0) {
    MessagePlugin.info(`${pickingNote.sku} picking_unit 未填`);
    isValid = false;
  }
  if (pickingNote.picking_unit_name === '') {
    MessagePlugin.info(`${pickingNote.sku} picking_unit_name 未填`);
    isValid = false;
  }
  if (pickingNote.picking_sku_name === '') {
    MessagePlugin.info(`${pickingNote.sku} picking_sku_name 未填`);
    isValid = false;
  }

  if (!isValid) {
    return false;
  }
  try {
    const req = {
      manual_mark_sku_list: [pickingNote],
    };
    await submitManualMarkSkuPickingNote(req);
    await onSearchPickingNote();
    return true;
  } catch (e) {
    console.error(e);
    await MessagePlugin.error(`保存sku拣货备注失败: ${e}`);
    return false;
  }
};
const onShowAddDialog = () => {
  // 重置表单数据
  addFormData.value = {
    sku: '',
    picking_unit: 1,
    picking_unit_name: '',
    picking_sku_name: '',
    support_pkg_picking: false,
    pkg_picking_unit: 1,
    pkg_picking_unit_name: '',
  };
  addDialogVisible.value = true;
};
const onConfirmAdd = async () => {
  try {
    addDialogLoading.value = true;
    
    // 表单验证
    if (addFormRef.value) {
      const validateResult = await addFormRef.value.validate();
      if (validateResult !== true) {
        addDialogLoading.value = false;
        return;
      }
    }

    // 创建要保存的数据
    const pickingNoteData: any = {
      sku: addFormData.value.sku,
      picking_unit: addFormData.value.picking_unit,
      picking_unit_name: addFormData.value.picking_unit_name,
      picking_sku_name: addFormData.value.picking_sku_name,
      support_pkg_picking: addFormData.value.support_pkg_picking,
    };

    // 如果支持PKG打包，添加相关字段
    if (addFormData.value.support_pkg_picking) {
      pickingNoteData.pkg_picking_unit = addFormData.value.pkg_picking_unit;
      pickingNoteData.pkg_picking_unit_name = addFormData.value.pkg_picking_unit_name;
    } else {
      pickingNoteData.pkg_picking_unit = 0;
      pickingNoteData.pkg_picking_unit_name = 'pk';
    }

    const isValid = await onSavePickingNote(pickingNoteData);
    if (isValid) {
      addDialogVisible.value = false;
      MessagePlugin.success('新增拣货备注成功');
    }
  } catch (error) {
    console.error('新增拣货备注失败:', error);
    MessagePlugin.error('新增拣货备注失败');
  } finally {
    addDialogLoading.value = false;
  }
};
const onCancelAdd = () => {
  addDialogVisible.value = false;
  // 清空表单错误状态
  if (addFormRef.value) {
    addFormRef.value.clearValidate();
  }
};
const onResetSearch = async () => {
  searchSku.value = '';
  paginationCurrentPage.value = 1; // 重置到第一页
  await onSearchPickingNote();
};
</script>
<style scoped></style>
