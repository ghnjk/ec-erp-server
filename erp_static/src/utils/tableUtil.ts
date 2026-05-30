/**
 * 获取表格的列key
 * @param columns
 */
export const getColumnKeys = (columns) => {
  const list = [];
  columns.forEach((e) => {
    list.push(e.colKey);
    if (e.children) {
      e.children.forEach((i) => {
        list.push(i.colKey);
      });
    }
  });
  return list;
};

/**
 * 获取列key和中文名的映射集合
 * @param columns
 */
export const getColKeyTitleMap = (columns) => {
  const obj = {};
  columns.forEach((e) => {
    obj[e.colKey] = e.title;
    if (e.children) {
      e.children.forEach((i) => {
        obj[i.colKey] = i.title;
      });
    }
  });
  return obj;
};
