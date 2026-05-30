import * as lodash from 'lodash';

export const toMap = (data: any[], keyName: string, valName: string) => {
  return lodash.reduce(
    data,
    (hash, value) => {
      const key = value[keyName];
      hash[key] = value[valName];
      return hash;
    },
    {},
  );
};

export const toList = (data: any[], keyName: string) => {
  return data.map((x) => x[keyName]);
};

export const treeToArray = (tree: any[], key: string) => {
  let res = [];
  for (const item of tree) {
    const { children, ...i } = item;
    if (children && children.length) {
      for (const child of children) {
        toMap;
        if (item[key] && child[key]) {
          child[key] = `${item[key]}/${child[key]}`;
        }
      }
      res = res.concat(treeToArray(children, key));
    }
    res.push(i);
  }
  return res;
};
