import{_ as w,d as C,r as t,o as P,M as y,a as u,b as S,c as b,e as l,w as r,f as E,g as x,t as z}from"./index.4c4f720c.js";import{e as K}from"./supplierApis.b61036a2.js";const B={class:"table-container"},V={name:"SkuPurchasePriceList"},D=C({...V,setup(T){const g=[{width:120,colKey:"supplier_name",title:"\u4F9B\u5E94\u5546",align:"center"},{width:60,colKey:"erp_sku_image_url",title:"\u5546\u54C1\u56FE\u7247",align:"center"},{width:120,colKey:"sku_group",title:"sku\u5206\u7EC4",align:"center"},{width:120,colKey:"sku_name",title:"\u5546\u54C1\u540D",align:"center"},{width:120,colKey:"sku",title:"\u5546\u54C1SKU",align:"center"},{width:120,colKey:"purchase_price",title:"\u91C7\u8D2D\u4EF7(RMB)",align:"center"}],c=t([]),i=t(!1),n=t(1),p=t(0),s=t(10),d=[10,20,50,100];P(()=>{_()});const m=({current:o,pageSize:e})=>{n.value=o,s.value=e,_()},_=async()=>{const o={current_page:n.value,page_size:s.value};i.value=!0;try{const e=await K(o);p.value=e.total,c.value=e.list}catch(e){console.error(e),await y.error(`\u67E5\u8BE2sku\u5F02\u5E38: ${e}`)}i.value=!1};return(o,e)=>{const k=u("t-image"),h=u("t-table"),v=u("t-pagination"),f=u("t-card");return S(),b("div",null,[l(f,null,{default:r(()=>[E("div",B,[l(h,{columns:g,data:c.value,loading:i.value,bordered:"",hover:"","row-key":"sku",stripe:""},{erp_sku_image_url:r(({row:a})=>[l(k,{src:a.erp_sku_image_url,style:{width:"60px",height:"60px"}},null,8,["src"])]),purchase_price:r(({row:a})=>[x(z(a.purchase_price/100),1)]),_:1},8,["data","loading"]),l(v,{modelValue:n.value,"onUpdate:modelValue":e[0]||(e[0]=a=>n.value=a),pageSize:s.value,"onUpdate:pageSize":e[1]||(e[1]=a=>s.value=a),"page-size-options":d,total:p.value,class:"pagination",onChange:m},null,8,["modelValue","pageSize","total"])])]),_:1})])}}});var M=w(D,[["__file","/Users/jkguo/workspace/ec-erp-static/src/pages/supply/skuPurchasePriceList.vue"]]);export{M as default};
