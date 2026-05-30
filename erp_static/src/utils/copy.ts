import useClipboard from 'vue-clipboard3';
import { MessagePlugin } from 'tdesign-vue-next';

export const copyValue = (value) => {
  const { toClipboard } = useClipboard();
  toClipboard(value)
    .then(() => {
      MessagePlugin.closeAll();
      MessagePlugin.success('复制成功');
    })
    .catch(() => {
      MessagePlugin.closeAll();
      MessagePlugin.error('复制失败');
    });
};
