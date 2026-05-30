import { createApp } from 'vue';
import VNetworkGraph from 'v-network-graph';
import 'v-network-graph/lib/style.css';

import TDesign from 'tdesign-vue-next';
import 'tdesign-vue-next/es/style/index.css';

// 第三方插件导包
import JsonViewer from 'vue-json-viewer';
import 'vue-json-viewer/style.css';

import { store } from './store';
import router from './router';
import '@/style/index.less';
import './permission';
import App from './App.vue';

const app = createApp(App);

app.use(VNetworkGraph);
// 框架自带
app.use(TDesign);
app.use(store);
app.use(router);

// 第三方插件写在这
app.use(JsonViewer);

app.mount('#app');
