export interface IProjectOption {
  label: string;
  value: string;
}

export const PROJECT_OPTIONS: IProjectOption[] = [
  { label: '菲律宾', value: 'philipine' },
  { label: '马来西亚', value: 'malaysia' },
  { label: '印尼-旧ERP', value: 'indonesia' },
  { label: '印尼-泗水仓', value: 'indonesiaWssh' },
  { label: '印尼-雅加达', value: 'indonesiaWyjd' },
  { label: '泰国', value: 'thailand' },
  { label: '巴西', value: 'brazil' },
];

export function getProjectLabel(projectId: string): string {
  const matched = PROJECT_OPTIONS.find((item) => item.value === projectId);
  if (matched) {
    return matched.label;
  }
  return projectId || '';
}
