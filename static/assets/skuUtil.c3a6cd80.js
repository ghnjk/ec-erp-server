import{r as u,M as t}from"./index.d88f823f.js";import{a as c}from"./supplierApis.9bd7015f.js";const r=u([]),l=u([]),e=u(new Map),n=u(new Map);async function f(){r.value=[],l.value=[],e.value=new Map,n.value=new Map;const p={current_page:1,page_size:1e4};try{const s=await c(p);r.value=s.list,new Set(s.list.map(a=>a.sku_group)).forEach(a=>{l.value.push({label:a,value:a})}),s.list.forEach(a=>{n.value.set(a.sku,a);const o=a.sku_group;e.value.has(o)?e.value.get(o).push(a):e.value.set(o,[a])})}catch(s){console.error(s),await t.error(`\u67E5\u8BE2sku\u5F02\u5E38: ${s}`)}}export{e as a,n as b,f as l,l as s};
