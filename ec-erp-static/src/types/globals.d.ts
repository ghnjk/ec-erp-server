// 通用声明

// Vue
declare module '*.vue' {
  import { DefineComponent } from 'vue';

  const component: DefineComponent<{}, {}, any>;
  export default component;
}

declare interface ImportMeta {
  env: {
    MODE: 'mock' | 'development' | 'test' | 'release';
  };
  // eslint-disable-next-line no-unused-vars
  glob: (url: string) => { url };
}

declare type ClassName = { [className: string]: any } | ClassName[] | string;

declare module '*.svg' {
  const CONTENT: string;
  export default CONTENT;
}

declare type Recordable<T = any> = Record<string, T>;
