import{_ as E,d as y,r as t,o as C,M as S,a as i,b,c as F,e as u,w as r,f as z,g as _}from"./index.c0285eea.js";import{s as B}from"./supplierApis.beeefb90.js";const V={class:"table-container"},k={name:"SupplierList"},x=y({...k,setup(P){const g=[{width:120,colKey:"supplier_id",title:"\u4F9B\u5E94\u5546id",align:"center"},{width:120,colKey:"supplier_name",title:"\u4F9B\u5E94\u5546\u540D",align:"center"},{width:120,colKey:"wechat_account",title:"\u5FAE\u4FE1\u53F7",align:"center"},{width:300,colKey:"detail",title:"\u8BE6\u7EC6\u4FE1\u606F"}],p=t([]),s=t(!1),o=t(1),c=t(0),n=t(10),v=[10,20,50,100];C(()=>{d()});const m=async({current:l,pageSize:e})=>{o.value=l,n.value=e,await d()},d=async()=>{const l={current_page:o.value,page_size:n.value};s.value=!0;try{const e=await B(l);c.value=e.total,p.value=e.list}catch(e){console.error(e),await S.error(`\u67E5\u8BE2\u5546\u6237\u5F02\u5E38: ${e}`)}s.value=!1};return(l,e)=>{const w=i("t-table"),f=i("t-pagination"),h=i("t-card");return b(),F("div",null,[u(h,null,{default:r(()=>[z("div",V,[u(w,{columns:g,data:p.value,loading:s.value,bordered:"",hover:"","row-key":"supplier_id",stripe:""},{wechat_account:r(({row:a})=>[_(" *** ")]),detail:r(({row:a})=>[_(" *** ")]),_:1},8,["data","loading"]),u(f,{modelValue:o.value,"onUpdate:modelValue":e[0]||(e[0]=a=>o.value=a),pageSize:n.value,"onUpdate:pageSize":e[1]||(e[1]=a=>n.value=a),"page-size-options":v,total:c.value,class:"pagination",onChange:m},null,8,["modelValue","pageSize","total"])])]),_:1})])}}});var L=E(x,[["__file","/Users/jkguo/workspace/ec-erp-static/src/pages/supply/supplierList.vue"]]);export{L as default};
