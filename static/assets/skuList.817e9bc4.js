import{_ as G,d as O,r,o as P,M as p,a as l,b as I,c as L,e as u,w as o,u as R,g as k,f as h,t as $,I as v,h as M}from"./index.1f090450.js";import{a as j,b as H,c as J}from"./supplierApis.1301a1e0.js";import{l as Q,s as W}from"./skuUtil.4235bbbd.js";const X=h("br",null,null,-1),Y={class:"table-container"},Z={name:"SkuList"},ee=O({...Z,setup(te){const n=r({skuGroup:"",skuName:"",sku:"",supportDays:""}),g=r({sortBy:"avg_sell_quantity",descending:!0}),D=[{width:60,colKey:"erp_sku_image_url",title:"\u5546\u54C1\u56FE\u7247",align:"center"},{width:120,colKey:"sku_group",title:"sku\u5206\u7EC4",align:"center",edit:{component:v,props:{autofocus:!0},validateTrigger:"change",abortEditOnEvent:["onEnter","onBlur"],onEdited:async e=>{console.log(e),await m(e.newRowData),await s()},rules:[{required:!0,message:"\u4E0D\u80FD\u4E3A\u7A7A"}],defaultEditable:!1}},{width:120,colKey:"sku_name",title:"\u5546\u54C1\u540D",align:"center",edit:{component:v,props:{autofocus:!0},validateTrigger:"change",abortEditOnEvent:["onEnter","onBlur"],onEdited:async e=>{console.log(e),await m(e.newRowData),await s()},rules:[{required:!0,message:"\u4E0D\u80FD\u4E3A\u7A7A"}],defaultEditable:!1}},{width:120,colKey:"sku",title:"\u5546\u54C1SKU",align:"center"},{width:120,colKey:"erp_sku_name",title:"BigSeller\u5546\u54C1\u540D",align:"center"},{width:120,colKey:"sku_unit_name",title:"\u91C7\u8D2D\u5355\u4F4D",align:"center",edit:{component:v,props:{autofocus:!0},validateTrigger:"change",abortEditOnEvent:["onEnter","onBlur"],onEdited:async e=>{console.log(e),await m(e.newRowData),await s()},rules:[{required:!0,message:"\u4E0D\u80FD\u4E3A\u7A7A"}],defaultEditable:!1}},{width:120,colKey:"sku_unit_quantity",title:"\u5355\u4F4D\u7684SKU\u6570",align:"center",sortType:"all",sorter:!0,edit:{component:M,props:{autofocus:!0},validateTrigger:"change",abortEditOnEvent:["onEnter","onBlur"],onEdited:async e=>{console.log(e),await m(e.newRowData),await s()},rules:[{required:!0,message:"\u4E0D\u80FD\u4E3A\u7A7A"}],defaultEditable:!1}},{width:120,colKey:"inventory",sortType:"all",sorter:!0,title:"\u5E93\u5B58",align:"center"},{width:120,colKey:"avg_sell_quantity",title:"\u5E73\u5747\u65E5\u9500\u552E\u91CF",align:"center",sortType:"all",sorter:!0},{width:120,colKey:"inventory_support_days",title:"\u5E93\u5B58\u652F\u6491\u5929\u6570",align:"center",sortType:"all",sorter:!0},{width:120,colKey:"shipping_stock_quantity",title:"\u6D77\u8FD0\u4E2D\u7684SKU",align:"center",sortType:"all",sorter:!0}],y=r([]),i=r(!1),d=r(1),E=r(0),_=r(10),C=[10,20,50,100];P(()=>{s(),Q()});const S=e=>{g.value=e,s()},B=({current:e,pageSize:t})=>{d.value=e,_.value=t,s()},m=async e=>{try{await H(e),await p.success("\u66F4\u65B0sku\u6210\u529F\u3002")}catch(t){console.error(t),await p.error(`\u66F4\u65B0sku\u5F02\u5E38: ${t}`)}},F=async()=>{i.value=!0;try{const{update_count:e}=await J();await p.success(`\u6210\u529F\u540C\u6B65${e}\u4E2Asku`)}catch(e){console.error(e),await p.error(`\u67E5\u8BE2sku\u5F02\u5E38: ${e}`)}i.value=!1},s=async()=>{const e={sku_group:n.value.skuGroup,sku_name:n.value.skuName,sku:n.value.sku,inventory_support_days:n.value.supportDays,current_page:d.value,page_size:_.value,sort:g.value};i.value=!0;try{const t=await j(e);E.value=t.total,y.value=t.list}catch(t){console.error(t),await p.error(`\u67E5\u8BE2sku\u5F02\u5E38: ${t}`)}i.value=!1};return(e,t)=>{const V=l("t-select"),c=l("t-form-item"),f=l("t-input"),K=l("t-input-number"),w=l("t-button"),b=l("t-space"),T=l("t-form"),A=l("t-col"),q=l("t-row"),U=l("t-image"),N=l("t-table"),z=l("t-pagination"),x=l("t-card");return I(),L("div",null,[u(x,null,{default:o(()=>[u(q,null,{default:o(()=>[u(A,{span:12},{default:o(()=>[u(T,{layout:"inline"},{default:o(()=>[u(c,{label:"sku\u5206\u7EC4:",name:"skuGroup"},{default:o(()=>[u(V,{modelValue:n.value.skuGroup,"onUpdate:modelValue":t[0]||(t[0]=a=>n.value.skuGroup=a),options:R(W),clearable:"",filterable:"",placeholder:"-\u8BF7\u9009\u62E9\u5546\u54C1\u5206\u7EC4-",style:{width:"150px",display:"inline-block"}},null,8,["modelValue","options"])]),_:1}),u(c,{label:"\u5546\u54C1\u540D:",name:"skuName"},{default:o(()=>[u(f,{modelValue:n.value.skuName,"onUpdate:modelValue":t[1]||(t[1]=a=>n.value.skuName=a),placeholder:"\u5546\u54C1\u540D"},null,8,["modelValue"])]),_:1}),u(c,{label:"\u5546\u54C1SKU:",name:"sku"},{default:o(()=>[u(f,{modelValue:n.value.sku,"onUpdate:modelValue":t[2]||(t[2]=a=>n.value.sku=a),placeholder:"\u5546\u54C1SKU"},null,8,["modelValue"])]),_:1}),u(c,{label:"\u652F\u6491\u5929\u6570:",name:"supportDays"},{default:o(()=>[u(K,{modelValue:n.value.supportDays,"onUpdate:modelValue":t[3]||(t[3]=a=>n.value.supportDays=a),theme:"column"},null,8,["modelValue"])]),_:1}),u(c,null,{default:o(()=>[u(b,{size:"small",style:{"align-items":"center","margin-left":"30px"}},{default:o(()=>[u(w,{theme:"primary",onClick:s},{default:o(()=>[k("\u67E5\u8BE2")]),_:1})]),_:1}),u(b,{size:"small",style:{"align-items":"center","margin-left":"30px"}},{default:o(()=>[u(w,{theme:"default",variant:"text",onClick:F},{default:o(()=>[k("\u540C\u6B65\u6240\u6709\u5E93\u5B58")]),_:1})]),_:1})]),_:1})]),_:1})]),_:1})]),_:1}),X,h("div",Y,[u(N,{columns:D,data:y.value,loading:i.value,"show-sort-column-bg-color":!0,sort:g.value,bordered:"",hover:"","row-key":"sku",stripe:"",onSortChange:S},{avg_sell_quantity:o(({row:a})=>[k($(a.avg_sell_quantity.toFixed(2)),1)]),erp_sku_image_url:o(({row:a})=>[u(U,{src:a.erp_sku_image_url,style:{width:"60px",height:"60px"}},null,8,["src"])]),_:1},8,["data","loading","sort"]),u(z,{modelValue:d.value,"onUpdate:modelValue":t[4]||(t[4]=a=>d.value=a),pageSize:_.value,"onUpdate:pageSize":t[5]||(t[5]=a=>_.value=a),"page-size-options":C,total:E.value,class:"pagination",onChange:B},null,8,["modelValue","pageSize","total"])])]),_:1})])}}});var le=G(ee,[["__file","/Users/jkguo/workspace/ec-erp-static/src/pages/supply/skuList.vue"]]);export{le as default};