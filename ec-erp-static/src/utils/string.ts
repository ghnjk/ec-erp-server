// 判断字符串是否为空
export function isEmpty(val: string | Array<number>): boolean {
  if (val === null || val === undefined || val.length === 0) {
    return true;
  }
  return false;
}
export function isNotEmpty(val: string | Array<number>): boolean {
  if (val === null || val === undefined || val.length === 0) {
    return false;
  }
  return true;
}

/**
 * 判断一个字符串是否为空或仅包含空格
 * 使用了逻辑非运算符 ! 来判断字符串是否为 null 或 undefined，如果是，则直接返回 true。
 * 如果字符串不为空，则使用正则表达式 /^\s*$/ 来判断字符串是否仅包含空格，如果是，则返回 true，否则返回 false
 * @param str 字符串
 */
export function isBlank(str: string) {
  return !str || /^\s*$/.test(str);
}
