<!--
 * @Author: frankfyang
 * @Date: 2022/10/11 15:40
 * @Email: frankfyang@tencent.com
-->
<template>
  <div class="no-data-page">
    <div>
      <no-data></no-data>
    </div>
    <span>暂无数据</span>
  </div>
</template>

<script lang="ts">
export default {
  name: 'NoDataPage',
};
</script>
<script lang="ts" setup>
import noData from '@/assets/no_data.svg?component';
</script>

<style scoped>
.no-data-page {
  position: relative;
  display: flex;
  justify-content: center;
  flex-direction: column;
  align-items: center;
  top: 30%;
}
</style>
