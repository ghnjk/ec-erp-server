import{_ as F,d as B,r as p,o as w,n as x,p as q,M as N,a as n,b as m,c as y,f as _,g as o,t as s,e,w as t,u as V,F as G,q as M,h as S}from"./index.c31d7726.js";import{l as z,s as L,a as I}from"./skuUtil.d422fa11.js";import"./supplierApis.aad0d7e8.js";const T={class:"page-header"},U={style:{float:"right","font-size":"medium"}},j={class:"page-panel"},A={name:"Stocktaking"},O=B({...A,setup(P){const d=p("\u672A\u767B\u5F55"),c=p(""),i=p([]);w(async()=>{const{query:f}=x(),{token:r}=f;try{const l=await q(r);d.value=l.userName,await z()}catch(l){console.error(l),await N.error(`\u767B\u9646\u5F02\u5E38: ${l}`)}});const h=()=>{i.value=I.value.get(c.value),console.log("skuList",i.value)};return(f,r)=>{const l=n("t-select"),u=n("t-form-item"),k=n("t-form"),g=n("t-card"),C=n("t-image"),v=n("t-col"),D=n("t-link"),b=n("t-row"),E=n("t-space");return m(),y("div",null,[_("div",T,[_("h1",null,[o(" \u4ED3\u5E93\u76D8\u70B9 "),_("span",U,"\u7528\u6237: "+s(d.value),1)])]),e(g,null,{default:t(()=>[e(k,null,{default:t(()=>[e(u,{label:"sku\u5206\u7EC4:",name:"skuGroup"},{default:t(()=>[e(l,{modelValue:c.value,"onUpdate:modelValue":r[0]||(r[0]=a=>c.value=a),options:V(L),clearable:"",filterable:"",placeholder:"-\u8BF7\u9009\u62E9\u5546\u54C1\u5206\u7EC4-",size:"large",onChange:h},null,8,["modelValue","options"])]),_:1})]),_:1})]),_:1}),_("div",j,[e(E,{class:"sku-card",direction:"vertical",size:"large"},{default:t(()=>[(m(!0),y(G,null,M(i.value,a=>(m(),S(g,{key:a.sku,class:"sku-card"},{default:t(()=>[e(b,null,{default:t(()=>[e(v,{span:2},{default:t(()=>[e(C,{src:a.erp_sku_image_url,style:{width:"60px",height:"60px"}},null,8,["src"])]),_:2},1024),e(v,{span:10},{default:t(()=>[_("div",null,[e(k,null,{default:t(()=>[e(u,{label:"\u5546\u54C1\u540D",name:"sku_name"},{default:t(()=>[o(s(a.sku_name),1)]),_:2},1024),e(u,{label:"sku",name:"sku"},{default:t(()=>[o(s(a.sku),1)]),_:2},1024),e(u,{label:"\u91C7\u8D2D\u5355\u4F4D",name:"sku_unit_name"},{default:t(()=>[o(s(a.sku_unit_name)+" [\u5355\u4F4Dsku\u6570 "+s(a.sku_unit_quantity)+"] ",1)]),_:2},1024),e(u,{label:"\u65E5\u5747\u9500\u552E\u91CF",name:"avg_sell_quantity"},{default:t(()=>[o(s(a.avg_sell_quantity.toFixed(2)),1)]),_:2},1024),e(u,{label:"erp-\u5E93\u5B58",name:"inventory"},{default:t(()=>[o(s(a.inventory),1)]),_:2},1024),e(u,{label:"\u5E93\u5B58\u652F\u6491\u5929\u6570",name:"inventory_support_days"},{default:t(()=>[o(s(a.inventory_support_days),1)]),_:2},1024),e(u,{label:"\u6D77\u8FD0\u4E2Dsku",name:"shipping_stock_quantity"},{default:t(()=>[o(s(a.shipping_stock_quantity),1)]),_:2},1024),e(u,{label:"\u64CD\u4F5C",name:"action"},{default:t(()=>[e(D,{hover:"color",style:{"margin-left":"16px"},theme:"primary"},{default:t(()=>[o("\u76D8\u70B9")]),_:1})]),_:1})]),_:2},1024)])]),_:2},1024)]),_:2},1024)]),_:2},1024))),128))]),_:1})])])}}});var H=F(O,[["__file","/Users/jkguo/workspace/ec-erp-static/src/pages/warehouse/stocktaking.vue"]]);export{H as default};
