
<p style="display:flex; justify-content: center">

</p>
<p align="center">
  <a href="https://tdesign.tencent.com/starter/vue-next/#/dashboard/base" target="_blank">
    <img alt="TDesign Logo" width="200" src="https://tdesign.gtimg.com/starter/brand-logo.svg">
  </a>
</p>

<p align="center">
  <a href="https://nodejs.org/en/about/releases/"><img src="https://img.shields.io/node/v/vite.svg" alt="node compatility"></a>
  <a href="https://github.com/Tencent/tdesign-vue-next/blob/develop/LICENSE">
    <img src="https://img.shields.io/npm/l/tdesign-vue-next.svg?sanitize=true" alt="License">
  </a>
</p>

### 项目简介

TDesign Vue Next Starter 是一个基于 TDesign。使用 `Vue3`、`Vite2`、`Pinia`、`TypeScript` 开发，可进行个性化主题配置，旨在提供项目开箱即用的、配置式的中后台项目。

<p>
  <a href="http://tdesign.tencent.com/starter/vue-next/">在线预览</a>
  .
  <a href="https://tdesign.tencent.com/starter/">使用文档</a>

</p>

<img src="docs/starter.png">

### 特性

- 内置多种常用的中后台页面
- 完善的目录结构
- 完善的代码规范配置
- 支持暗黑模式
- 自定义主题颜色
- 多种空间布局
- 内置 Mock 数据方案

### 开发

``` bash
## 安装依赖
pnpm install

## 启动项目
npm run dev

## 启动mock环境
npm run dev:mock
```

### 构建

```bash
## 构建正式环境
npm run build

## 构建测试环境
npm run build:test
```

### 其他

```bash
## 预览构建产物
npm run preview

## 代码格式检查
npm run lint

## 代码格式检查与自动修复
npm run lint:fix

## style格式检查
npm run stylelint

## style格式检查与自动修复
npm run stylelint:fix

```
建议搭配`webstorm` - `save action`插件来完成保存自动eslint


## 代码编写规范
### 文件
1、文件夹名: 统一采用`下划线命名法`

2、文件名: 统一采用`小驼峰`

### 类、接口
1、类名全部使用大写驼峰，同时命名跟回文件命名。

2、接口命名以大写 I 开头，代表 `interface`。如`IOption`。


#### 贡献提交规范

- [Angular Convention](https://github.com/conventional-changelog/conventional-changelog/tree/master/packages/conventional-changelog-angular)
- [Vue Style Guide](https://v3.vuejs.org/style-guide/#rule-categories)

### 兼容性

| [<img src="https://raw.githubusercontent.com/alrra/browser-logos/master/src/edge/edge_48x48.png" alt="IE / Edge" width="24px" height="24px" />](http://godban.github.io/browsers-support-badges/)</br> IE / Edge | [<img src="https://raw.githubusercontent.com/alrra/browser-logos/master/src/firefox/firefox_48x48.png" alt="Firefox" width="24px" height="24px" />](http://godban.github.io/browsers-support-badges/)</br>Firefox | [<img src="https://raw.githubusercontent.com/alrra/browser-logos/master/src/chrome/chrome_48x48.png" alt="Chrome" width="24px" height="24px" />](http://godban.github.io/browsers-support-badges/)</br>Chrome | [<img src="https://raw.githubusercontent.com/alrra/browser-logos/master/src/safari/safari_48x48.png" alt="Safari" width="24px" height="24px" />](http://godban.github.io/browsers-support-badges/)</br>Safari |
| ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Edge >=84                                                                                                                                                                                                        | Firefox >=83                                                                                                                                                                                                      | Chrome >=84                                                                                                                                                                                                   | Safari >=14.1                                                                                                                                                                                                  |

### License

[MIT](./LICENSE)
