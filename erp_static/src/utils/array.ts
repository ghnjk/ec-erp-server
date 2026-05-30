// 判断对象是否是数组
export function isArray(o) {
  return Object.prototype.toString.call(o) === '[object Array]';
}
