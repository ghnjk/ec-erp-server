// 判断字符串是否为空

export const confKeyTypeOptions = [
  {
    label: 'SERVER',
    value: '1',
  },
  {
    label: 'CKV',
    value: '2',
  },
  {
    label: 'DB',
    value: '3',
  },
  {
    label: 'SERVER',
    value: '4',
  },
  {
    label: 'SWITCH',
    value: '5',
  },
  {
    label: 'COREDB',
    value: '6',
  },
  {
    label: 'SEG',
    value: '7',
  },
];

export function convertCcConfKeyType(confKeyType: string): string {
  for (let i = 0; i < confKeyTypeOptions.length; i++) {
    if (confKeyType === confKeyTypeOptions[i].value) {
      return confKeyTypeOptions[i].label;
    }
  }
  return `UNKNOWN-${confKeyType}`;
}
