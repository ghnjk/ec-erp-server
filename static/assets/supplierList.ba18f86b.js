import{_ as h,d as y,r as t,o as S,M as C,a as i,b,c as F,e as u,w as d,f as g,t as z}from"./index.d88f823f.js";import{s as B}from"./supplierApis.9bd7015f.js";const k={class:"table-container"},P={name:"SupplierList"},V=y({...P,setup(x){const _=[{width:120,colKey:"supplier_id",title:"\u4F9B\u5E94\u5546id",align:"center"},{width:120,colKey:"supplier_name",title:"\u4F9B\u5E94\u5546\u540D",align:"center"},{width:120,colKey:"wechat_account",title:"\u5FAE\u4FE1\u53F7",align:"center"},{width:300,colKey:"detail",title:"\u8BE6\u7EC6\u4FE1\u606F"}],r=t([]),s=t(!1),o=t(1),p=t(0),n=t(10),v=[10,20,50,100];S(()=>{c()});const m=async({current:l,pageSize:e})=>{o.value=l,n.value=e,await c()},c=async()=>{const l={current_page:o.value,page_size:n.value};s.value=!0;try{const e=await B(l);p.value=e.total,r.value=e.list}catch(e){console.error(e),await C.error(`\u67E5\u8BE2\u5546\u6237\u5F02\u5E38: ${e}`)}s.value=!1};return(l,e)=>{const f=i("t-table"),w=i("t-pagination"),E=i("t-card");return b(),F("div",null,[u(E,null,{default:d(()=>[g("div",k,[u(f,{columns:_,data:r.value,loading:s.value,bordered:"",hover:"","row-key":"supplier_id",stripe:""},{detail:d(({row:a})=>[g("pre",null,z(a.detail),1)]),_:1},8,["data","loading"]),u(w,{modelValue:o.value,"onUpdate:modelValue":e[0]||(e[0]=a=>o.value=a),pageSize:n.value,"onUpdate:pageSize":e[1]||(e[1]=a=>n.value=a),"page-size-options":v,total:p.value,class:"pagination",onChange:m},null,8,["modelValue","pageSize","total"])])]),_:1})])}}});var T=h(V,[["__file","/Users/jkguo/workspace/ec-erp-static/src/pages/supply/supplierList.vue"]]);export{T as default};
