<template>
  <div>
    <div class="page-header">
      <h1>
        仓库盘点
        <span style="float: right; font-size: medium">用户: {{ userName }}</span>
      </h1>
    </div>
    <t-card>
      <t-form>
        <t-space direction="vertical">
          <t-radio-group
            v-model="searchType"
            default-value="skuGroup"
            style="margin-bottom: 20px"
            @change="onSearchTypeChange"
          >
            <t-radio-button value="skuGroup">sku分组</t-radio-button>
            <t-radio-button value="saleQuantity">销量TOP30</t-radio-button>
            <t-radio-button value="lackStock">货物紧缺TOP30</t-radio-button>
          </t-radio-group>
        </t-space>
        <t-form-item v-if="searchType === 'skuGroup'" label="sku分组:" name="skuGroup">
          <t-select
            v-model="skuGroup"
            :options="skuGroupNameOptions"
            clearable
            filterable
            placeholder="-请选择商品分组-"
            size="large"
            @change="onSkuGroupChange"
          />
        </t-form-item>
      </t-form>
    </t-card>
    <div class="page-panel">
      <t-loading :loading="skuTableLoading">
        <t-space class="sku-card" direction="vertical" size="large">
          <t-card v-for="sku in skuList" :key="sku.sku" class="sku-card">
            <t-row>
              <t-col :span="2">
                <t-image :src="sku.erp_sku_image_url" :style="{ width: '60px', height: '60px' }" />
              </t-col>
              <t-col :span="10">
                <div>
                  <t-form>
                    <t-form-item label="商品名" name="sku_name">
                      {{ sku.sku_name }}
                    </t-form-item>
                    <t-form-item label="sku" name="sku">
                      {{ sku.sku }}
                    </t-form-item>
                    <t-form-item label="采购单位" name="sku_unit_name">
                      {{ sku.sku_unit_name }} [单位sku数 {{ sku.sku_unit_quantity }}]
                    </t-form-item>
                    <t-form-item label="日均销售量" name="avg_sell_quantity">
                      {{ sku.avg_sell_quantity.toFixed(2) }}
                    </t-form-item>
                    <t-form-item label="erp-库存" name="inventory">
                      {{ sku.inventory }}
                    </t-form-item>
                    <t-form-item label="库存支撑天数" name="inventory_support_days">
                      {{ sku.inventory_support_days }}
                    </t-form-item>
                    <t-form-item label="海运中sku" name="shipping_stock_quantity">
                      {{ sku.shipping_stock_quantity }}
                    </t-form-item>
                    <t-form-item label="操作" name="action">
                      <t-link hover="color" style="margin-left: 16px" theme="primary" @click="popupTakingDrawer(sku)">
                        盘点
                      </t-link>
                    </t-form-item>
                  </t-form>
                </div>
              </t-col>
            </t-row>
          </t-card>
        </t-space>
      </t-loading>
    </div>
    <t-drawer
      v-model:visible="stocktakingDrawer.visible"
      :header="stocktakingDrawer.title"
      :on-overlay-click="() => (stocktakingDrawer.visible = false)"
      placement="bottom"
      size="70%"
      @cancel="stocktakingDrawer.visible = false"
    >
      <t-form>
        <t-form-item label="sku" name="sku">
          {{ stocktakingDrawer.sku.sku }}
        </t-form-item>
        <t-form-item label="实际库存" name="real_quantity">
          <t-input-number v-model="stocktakingDrawer.sku.real_stock_sku" />
          <span style="margin-left: 15px; font-size: medium">{{ stocktakingDrawer.sku.taking_unit }}</span>
        </t-form-item>
        <t-form-item label="盘点单位" name="taking_unit">
          <t-input v-model="stocktakingDrawer.sku.taking_unit" />
        </t-form-item>
        <t-form-item label="盘点单位-sku" name="taking_unit_sku_count">
          <t-input-number v-model="stocktakingDrawer.sku.taking_unit_sku_count" />
        </t-form-item>
        <t-form-item label="未打包sku数" name="shipping_stock_quantity">
          {{ stocktakingDrawer.sku?.shipping_stock_quantity }}
        </t-form-item>
        <t-form-item label="盘点前：库存" name="before-inventory">
          {{ stocktakingDrawer.sku?.inventory }}
        </t-form-item>
        <t-form-item label="盘点后：库存" name="after-inventory">
          {{ stocktakingDrawer.sku?.inventory }}
        </t-form-item>
      </t-form>
    </t-drawer>
  </div>
</template>

<script lang="ts">
export default {
  name: 'Stocktaking',
};
</script>
<script lang="ts" setup>
import { ref, onMounted } from 'vue';
import { useRoute } from 'vue-router';
import { MessagePlugin } from 'tdesign-vue-next';
import { skuGroupNameOptions, skuGroupMap, loadSkuInfo } from '@/utils/skuUtil';
import { loginWithToken } from '@/apis/sysApis';
import { searchSku } from '@/apis/supplierApis';

const userName = ref('未登录');
const skuGroup = ref('');
const skuList = ref([]);
const skuTableLoading = ref(false);
const searchType = ref('skuGroup');
const stocktakingDrawer = ref({
  visible: false,
  title: '货物盘点',
  sku: {
    sku: '',
    real_stock_sku: 0,
    shipping_stock_quantity: 0,
    taking_unit: '',
    taking_unit_sku_count: 0,
    inventory: 0,
  },
});

onMounted(async () => {
  const { query } = useRoute();
  const { token } = query;
  try {
    const userInfo: any = await loginWithToken(token);
    userName.value = userInfo.userName;
    await loadSkuInfo();
  } catch (e) {
    console.error(e);
    await MessagePlugin.error(`登陆异常: ${e}`);
  }
});
// 选择分组
const onSkuGroupChange = () => {
  const req = {
    sku_group: skuGroup.value,
    sku_name: '',
    sku: '',
    inventory_support_days: '',
    current_page: 1,
    page_size: 1000,
    sort: {
      sortBy: 'avg_sell_quantity',
      descending: true,
    },
  };
  onSearchSku(req);
};
const popupTakingDrawer = (sku: any) => {
  stocktakingDrawer.value.title = `货物盘点：${sku.sku_name}`;
  sku.taking_unit = sku.sku_unit_name;
  sku.taking_unit_sku_count = sku.sku_unit_quantity;
  sku.real_stock_sku = Math.floor(sku.inventory / sku.taking_unit_sku_count);
  stocktakingDrawer.value.sku = sku;
  stocktakingDrawer.value.visible = true;
};
const onSearchTypeChange = () => {
  skuList.value = [];
  if (searchType.value === 'skuGroup') {
    skuGroup.value = '';
  } else if (searchType.value === 'lackStock') {
    const req = {
      sku_group: '',
      sku_name: '',
      sku: '',
      inventory_support_days: '14',
      current_page: 1,
      page_size: 30,
      sort: {
        sortBy: 'avg_sell_quantity',
        descending: true,
      },
    };
    onSearchSku(req);
  } else if (searchType.value === 'saleQuantity') {
    const req = {
      sku_group: '',
      sku_name: '',
      sku: '',
      inventory_support_days: '',
      current_page: 1,
      page_size: 30,
      sort: {
        sortBy: 'avg_sell_quantity',
        descending: true,
      },
    };
    onSearchSku(req);
  }
};
const onSearchSku = async (req) => {
  skuTableLoading.value = true;
  try {
    const res = await searchSku(req);
    skuList.value = res.list;
    console.log('skuList', skuList.value);
  } catch (e) {
    console.error(e);
    await MessagePlugin.error(`查询sku异常: ${e}`);
  }
  skuTableLoading.value = false;
};
</script>
<style lang="less">
.page-header {
  margin: 20px;
}

.page-panel {
  width: 100%;
  text-align: center;
  margin-top: 20px;
}

.sku-card {
  width: 100%;
}
</style>
