import{_ as L,d as q,r as s,a,b,c as K,h as V,w as u,e,g as A,j as T,f as x,t as z,M as g,F as M,n as j,o as Y,p as Z,q as ee,s as te,v as ue}from"./index.fe0d001b.js";import{q as ae,p as le,s as ne,a as oe,g as ie,b as se}from"./warehouseApis.cb60006e.js";const re={style:{width:"80%"}},ce={name:"OrderPrintProgressDialog"},_e=q({...ce,setup(S,{expose:U}){const D=s(""),m=s(!1),r=s(null),_=s(null),E=s(!1),f=async()=>{_.value!==null&&clearTimeout(_.value),await F()||(_.value=setTimeout(f,1e3))},P=()=>r.value===null?!1:r.value.pdf_file_url!==null&&r.value.pdf_file_url!==void 0&&r.value.pdf_file_url!=="",F=async()=>{try{const v={task_id:D.value},o=await ae(v);return r.value=o.task,P()?(E.value=!0,console.log("url",r.value.pdf_file_url),window.open(r.value.pdf_file_url,"_blank"),!0):!1}catch(v){return console.error(v),await g.error(`\u67E5\u8BE2\u6253\u5370\u8FDB\u5EA6\u5F02\u5E38: ${v}`),!1}},$=async v=>{D.value=v,E.value=!1,m.value=!0,await f()},w=()=>{_.value!==null&&clearTimeout(_.value),m.value=!1};return U({popupDialog:$}),(v,o)=>{const t=a("t-input"),d=a("t-form-item"),h=a("link-icon"),B=a("t-link"),C=a("t-progress"),l=a("t-collapse-panel"),n=a("t-collapse"),p=a("t-form"),O=a("t-dialog");return b(),K("div",null,[m.value?(b(),V(O,{key:0,visible:m.value,"onUpdate:visible":o[0]||(o[0]=c=>m.value=c),"close-on-esc-keydown":!1,"close-on-overlay-click":!1,"confirm-btn":null,header:"\u6253\u5370\u8BA2\u5355\u4E2D...","show-overlay":"",width:"80%",onCancel:w},{default:u(()=>[e(p,null,{default:u(()=>[e(d,{label:"\u4EFB\u52A1id"},{default:u(()=>{var c;return[e(t,{value:(c=r.value)==null?void 0:c.task_id,disabled:""},null,8,["value"])]}),_:1}),e(d,{label:"\u5F53\u524D\u6B65\u9AA4"},{default:u(()=>{var c;return[e(t,{value:(c=r.value)==null?void 0:c.current_step,current_step:"",disabled:""},null,8,["value"])]}),_:1}),E.value?(b(),V(d,{key:0,label:"\u6253\u5370\u94FE\u63A5"},{default:u(()=>{var c;return[e(B,{href:(c=r.value)==null?void 0:c.pdf_file_url,target:"_blank",theme:"primary",underline:""},{"prefix-icon":u(()=>[e(h)]),default:u(()=>[A(" \u6253\u5370PDF ")]),_:1},8,["href"])]}),_:1})):T("v-if",!0),e(d,{label:"\u8FDB\u5EA6"},{default:u(()=>{var c;return[x("div",re,[e(C,{percentage:(c=r.value)==null?void 0:c.progress,theme:"plump"},null,8,["percentage"])])]}),_:1}),e(n,{"default-value":[]},{default:u(()=>[e(l,{header:"\u5904\u7406\u65E5\u5FD7"},{default:u(()=>{var c;return[x("pre",null,z((c=r.value)==null?void 0:c.logs.join(`
`)),1)]}),_:1})]),_:1})]),_:1})]),_:1},8,["visible"])):T("v-if",!0)])}}});var R=L(_e,[["__file","/Users/jkguo/workspace/ec-erp-static/src/pages/warehouse/components/orderPrintProgressDialog.vue"]]);const pe={name:"OrderPrintConfirmDialog",components:{OrderPrintProgressDialog:R}},de=q({...pe,setup(S,{expose:U}){const D=s(null),m=s(!1),r=s(""),_=s([]),E=s([]),f=s(!1),P=async(o,t)=>{E.value=t,r.value=`\u672C\u6B21\u6253\u5370 ${t.length} \u5355 / \u5171 ${o} \u5355`,m.value=!0,f.value=!1,await F()},F=async()=>{try{_.value=[],f.value=!0;const o={order_list:E.value},t=await le(o);return t.need_manual_mark_sku_list.forEach(d=>{_.value.push({sku:d.sku,image_url:d.image_url,desc:d.desc,picking_unit:0,picking_unit_name:"pcs",picking_sku_name:d.sku,support_pkg_picking:!1,pkg_picking_unit:0,pkg_picking_unit_name:"pk"})}),console.log("manualMarkSkuList",_.value),f.value=!1,_.value.length>0?(await g.info("\u9700\u8981\u8865\u5145sku\u62E3\u8D27\u5907\u6CE8."),null):(console.log("\u63D0\u4EA4\u6253\u5370\u8BA2\u5355\u6210\u529F\uFF0C\u9762\u5355id",t.task_id),t.task_id)}catch(o){console.error(o),await g.error(`\u6253\u5370\u8BA2\u5355\u5931\u8D25: ${o}`),f.value=!1}return null},$=async()=>{if(_.value.length===0)return!0;let o=!0;if(_.value.forEach(t=>{t.picking_unit<=0&&(g.info(`${t.sku} picking_unit \u672A\u586B`),o=!1),t.picking_unit_name===""&&(g.info(`${t.sku} picking_unit_name \u672A\u586B`),o=!1),t.picking_sku_name===""&&(g.info(`${t.sku} picking_sku_name \u672A\u586B`),o=!1),t.support_pkg_picking&&(t.pkg_picking_unit<=0&&(g.info(`${t.sku} pkg_picking_unit \u672A\u586B`),o=!1),t.pkg_picking_unit_name===""&&(g.info(`${t.sku} pkg_picking_unit_name \u672A\u586B`),o=!1))}),!o)return!1;try{const t={manual_mark_sku_list:_.value};return await ne(t),!0}catch(t){return console.error(t),await g.error(`\u6DFB\u52A0sku\u62E3\u8D27\u5907\u6CE8\u5931\u8D25: ${t}`),!1}},w=async o=>{try{const t={task_id:o};m.value=!1;const d=await oe(t);console.log("task",d),D.value.popupDialog(o)}catch(t){console.error(t),await g.error(`\u542F\u52A8\u540E\u53F0\u4EFB\u52A1\u5931\u8D25: ${t}`),f.value=!1}},v=async()=>{if(!await $()||f.value)return;f.value=!0;const t=await F();t!=null?await w(t):f.value=!1};return U({popupDialog:P}),(o,t)=>{const d=a("t-input"),h=a("t-form-item"),B=a("t-list-item-meta"),C=a("t-input-number"),l=a("t-checkbox"),n=a("t-space"),p=a("t-list-item"),O=a("t-list"),c=a("t-form"),I=a("t-loading"),N=a("t-dialog");return b(),K("div",null,[m.value?(b(),V(N,{key:0,visible:m.value,"onUpdate:visible":t[0]||(t[0]=i=>m.value=i),"close-on-esc-keydown":!1,"close-on-overlay-click":!1,"confirm-btn":"\u786E\u8BA4 & \u63D0\u4EA4\u6253\u5370",header:"\u8BA2\u5355\u6253\u5370\u4FE1\u606F\u786E\u8BA4","show-overlay":"",width:"80%",onConfirm:v},{default:u(()=>[e(I,{loading:f.value},{default:u(()=>[e(c,null,{default:u(()=>[e(h,{label:"\u8BA2\u5355\u6570"},{default:u(()=>[e(d,{value:r.value,disabled:""},null,8,["value"])]),_:1}),e(h,{label:"sku\u62E3\u8D27\u5907\u6CE8"},{default:u(()=>[e(n,{direction:"vertical"},{default:u(()=>[e(O,{split:!0,stripe:""},{default:u(()=>[(b(!0),K(M,null,j(_.value,i=>(b(),V(p,{key:i==null?void 0:i.sku},{default:u(()=>[e(B,{description:i.desc,image:i.image_url,title:i==null?void 0:i.sku},null,8,["description","image","title"]),e(n,{direction:"vertical"},{default:u(()=>[e(h,{label:"1\u62E3\u8D27\u5355\u4F4D="},{default:u(()=>[e(C,{modelValue:i.picking_unit,"onUpdate:modelValue":k=>i.picking_unit=k},null,8,["modelValue","onUpdate:modelValue"]),A(" SKU ")]),_:2},1024),e(h,{label:"\u62E3\u8D27\u5355\u4F4D\u540D"},{default:u(()=>[e(d,{modelValue:i.picking_unit_name,"onUpdate:modelValue":k=>i.picking_unit_name=k},null,8,["modelValue","onUpdate:modelValue"])]),_:2},1024),e(h,{label:"\u6DFB\u52A0pkg\u6253\u5305"},{default:u(()=>[e(l,{modelValue:i.support_pkg_picking,"onUpdate:modelValue":k=>i.support_pkg_picking=k},null,8,["modelValue","onUpdate:modelValue"])]),_:2},1024),i.support_pkg_picking?(b(),V(h,{key:0,label:"1 PKG ="},{default:u(()=>[e(C,{modelValue:i.pkg_picking_unit,"onUpdate:modelValue":k=>i.pkg_picking_unit=k},null,8,["modelValue","onUpdate:modelValue"]),A(" SKU ")]),_:2},1024)):T("v-if",!0),i.support_pkg_picking?(b(),V(h,{key:1,label:"PKG\u6253\u5305\u5355\u4F4D"},{default:u(()=>[e(d,{modelValue:i.pkg_picking_unit_name,"onUpdate:modelValue":k=>i.pkg_picking_unit_name=k},null,8,["modelValue","onUpdate:modelValue"])]),_:2},1024)):T("v-if",!0),e(h,{label:"\u62E3\u8D27sku\u540D"},{default:u(()=>[e(d,{modelValue:i.picking_sku_name,"onUpdate:modelValue":k=>i.picking_sku_name=k},null,8,["modelValue","onUpdate:modelValue"])]),_:2},1024)]),_:2},1024)]),_:2},1024))),128))]),_:1})]),_:1})]),_:1})]),_:1})]),_:1},8,["loading"])]),_:1},8,["visible"])):T("v-if",!0),e(R,{ref_key:"orderPrintProgressDialog",ref:D},null,512)])}}});var W=L(de,[["__file","/Users/jkguo/workspace/ec-erp-static/src/pages/warehouse/components/orderPrintConfirmDialog.vue"]]);const G=S=>(te("data-v-cf49c91e"),S=S(),ue(),S),fe=G(()=>x("br",null,null,-1)),ge=G(()=>x("br",null,null,-1)),me={class:"table-container"},ve={name:"PrintOrder",components:{OrderPrintConfirmDialog:W}},ke=q({...ve,setup(S){const U=s("\u672A\u767B\u5F55"),D=s(null),m=[{width:50,colKey:"row-select",type:"multiple",checkProps:{allowUncheck:!0},align:"center"},{width:120,colKey:"id",title:"id",align:"center"},{width:60,colKey:"platformOrderId",title:"\u8BA2\u5355\u53F7",align:"center"},{width:120,colKey:"packageNo",title:"\u5305\u88F9\u53F7",align:"center"},{width:120,colKey:"shippingCarrierName",title:"\u7269\u6D41",align:"center"},{width:120,colKey:"trackingNo",title:"\u8FD0\u5355\u53F7",align:"center"},{width:120,colKey:"multilingualViewStatus",title:"\u72B6\u6001",align:"center"},{width:120,colKey:"amount",title:"\u91D1\u989D",align:"center"},{width:120,colKey:"platform",title:"\u5E73\u53F0",align:"center"}],r=s([]),_=s(!1),E=s([]),f=s(1),P=s(0),F=s(500),$=[10,20,50,100,200,500,1e3],w=s([]),v=s(null);Y(async()=>{const{query:l}=Z(),{token:n}=l;try{const p=await ee(n);U.value=p.userName,await o()}catch(p){console.error(p),await g.error(`\u767B\u9646\u5F02\u5E38: ${p}`)}});const o=async()=>{try{const n=(await ie()).ship_provider_list;console.log("shipProviderList",n),w.value=[],n.forEach(p=>{w.value.push({label:`${p.name}(${p.count})`,value:p.id})})}catch(l){console.error(l),await g.error(`\u67E5\u8BE2\u8BA2\u5355\u7EDF\u8BA1\u4FE1\u606F\u5F02\u5E38: ${l}`)}},t=(l,n)=>{D.value=l,B()},d=(l,{selectedRowData:n})=>{E.value=l},h=({current:l,pageSize:n})=>{f.value=l,F.value=n,B()},B=async()=>{if(_.value=!0,await o(),D.value===null){_.value=!1;return}try{const l={shipping_provider_id:D.value,current_page:f.value,page_size:F.value};E.value=[];const n=await se(l);P.value=n.total,r.value=n.list,console.log("waitOrder",P.value,r.value)}catch(l){console.error(l),await g.error(`\u67E5\u8BE2\u8BA2\u5355\u4FE1\u606F\u5F02\u5E38: ${l}`)}_.value=!1},C=async()=>{const l=new Set;if(E.value.forEach(p=>{l.add(p)}),console.log("selected: ",l),l.size<=0){g.info("\u8BF7\u5148\u9009\u4E2D\u9700\u8981\u6253\u5370\u7684\u8BA2\u5355.");return}const n=[];if(r.value.forEach(p=>{l.has(p.id)&&n.push(p)}),n.length!=l.size){g.error("\u9009\u4E2D\u7684\u8BA2\u5355\u4FE1\u606F\u7F3A\u5931\u3002.");return}v.value.popupDialog(P.value,n)};return(l,n)=>{const p=a("t-radio"),O=a("t-space"),c=a("t-radio-group"),I=a("t-form-item"),N=a("t-button"),i=a("t-form"),k=a("t-col"),Q=a("t-row"),H=a("t-table"),J=a("t-pagination"),X=a("t-card");return b(),K("div",null,[e(X,null,{default:u(()=>[fe,e(Q,null,{default:u(()=>[e(k,{span:12},{default:u(()=>[e(i,{layout:"inline"},{default:u(()=>[e(I,{label:"\u7269\u6D41\u65B9\u5F0F"},{default:u(()=>[e(c,{modelValue:D.value,"onUpdate:modelValue":n[0]||(n[0]=y=>D.value=y),name:"shipping",variant:"default-filled",onChange:t},{default:u(()=>[e(O,{direction:"vertical"},{default:u(()=>[(b(!0),K(M,null,j(w.value,y=>(b(),V(p,{value:y.value},{default:u(()=>[A(z(y.label),1)]),_:2},1032,["value"]))),256))]),_:1})]),_:1},8,["modelValue"])]),_:1}),e(I,null,{default:u(()=>[e(O,{size:"small",style:{"align-items":"center","margin-left":"30px"}},{default:u(()=>[e(N,{theme:"default",onClick:B},{default:u(()=>[A("\u5237 \u65B0")]),_:1}),e(N,{theme:"primary",onClick:C},{default:u(()=>[A("\u6253 \u5370")]),_:1})]),_:1})]),_:1})]),_:1})]),_:1})]),_:1}),ge,x("div",me,[e(H,{columns:m,data:r.value,loading:_.value,"select-on-row-click":!0,"selected-row-keys":E.value,bordered:"",hover:"","row-key":"id",stripe:"",onSelectChange:d},{multilingualViewStatus:u(({row:y})=>[A(z(y.printLabelMark>0?"[\u5DF2\u6253\u5370]"+y.multilingualViewStatus:y.multilingualViewStatus),1)]),_:1},8,["data","loading","selected-row-keys"]),e(J,{modelValue:f.value,"onUpdate:modelValue":n[1]||(n[1]=y=>f.value=y),pageSize:F.value,"onUpdate:pageSize":n[2]||(n[2]=y=>F.value=y),"page-size-options":$,total:P.value,class:"pagination",onChange:h},null,8,["modelValue","pageSize","total"])])]),_:1}),e(W,{ref_key:"orderPrintConfirmDialog",ref:v},null,512)])}}});var be=L(ke,[["__scopeId","data-v-cf49c91e"],["__file","/Users/jkguo/workspace/ec-erp-static/src/pages/warehouse/printOrder.vue"]]);export{be as default};
