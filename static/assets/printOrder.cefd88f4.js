import{i as A,_ as N,d as q,r as s,a as n,b as y,c as T,h as U,w as u,e,g as S,j as I,f as x,t as K,M as m,F as z,n as L,o as Z,p as ee,q as te,s as ue,v as ae}from"./index.900814fc.js";const ne=()=>A.post("/erp_api/warehouse/get_wait_print_order_ship_provider_list",{}),le=p=>A.post("/erp_api/warehouse/search_wait_print_order",p),oe=p=>A.post("/erp_api/warehouse/pre_submit_print_order",p),re=p=>A.post("/erp_api/warehouse/start_run_print_order_task",p),ie=p=>A.post("/erp_api/warehouse/submit_manual_mark_sku_picking_note",p),se=p=>A.post("/erp_api/warehouse/query_print_order_task",p),ce={style:{width:"80%"}},_e={name:"OrderPrintProgressDialog"},pe=q({..._e,setup(p,{expose:C}){const k=s(""),f=s(!1),i=s(null),c=s(null),h=s(!1),w=async()=>{c.value!==null&&clearTimeout(c.value),await D()||(c.value=setTimeout(w,1e3))},b=()=>i.value===null?!1:i.value.pdf_file_url!==null&&i.value.pdf_file_url!==void 0&&i.value.pdf_file_url!=="",D=async()=>{try{const l={task_id:k.value},t=await se(l);return i.value=t.task,b()?(h.value=!0,console.log("url",i.value.pdf_file_url),window.open(i.value.pdf_file_url,"_blank"),!0):!1}catch(l){return console.error(l),await m.error(`\u67E5\u8BE2\u6253\u5370\u8FDB\u5EA6\u5F02\u5E38: ${l}`),!1}},O=async l=>{k.value=l,h.value=!1,f.value=!0,await w()},F=()=>{c.value!==null&&clearTimeout(c.value),f.value=!1};return C({popupDialog:O}),(l,t)=>{const d=n("t-input"),v=n("t-form-item"),V=n("link-icon"),P=n("t-link"),B=n("t-progress"),o=n("t-collapse-panel"),r=n("t-collapse"),_=n("t-form"),$=n("t-dialog");return y(),T("div",null,[f.value?(y(),U($,{key:0,visible:f.value,"onUpdate:visible":t[0]||(t[0]=a=>f.value=a),"close-on-esc-keydown":!1,"close-on-overlay-click":!1,"confirm-btn":null,header:"\u6253\u5370\u8BA2\u5355\u4E2D...","show-overlay":"",width:"80%",onCancel:F},{default:u(()=>[e(_,null,{default:u(()=>[e(v,{label:"\u4EFB\u52A1id"},{default:u(()=>{var a;return[e(d,{value:(a=i.value)==null?void 0:a.task_id,disabled:""},null,8,["value"])]}),_:1}),e(v,{label:"\u5F53\u524D\u6B65\u9AA4"},{default:u(()=>{var a;return[e(d,{value:(a=i.value)==null?void 0:a.current_step,current_step:"",disabled:""},null,8,["value"])]}),_:1}),h.value?(y(),U(v,{key:0,label:"\u6253\u5370\u94FE\u63A5"},{default:u(()=>{var a;return[e(P,{href:(a=i.value)==null?void 0:a.pdf_file_url,target:"_blank",theme:"primary",underline:""},{"prefix-icon":u(()=>[e(V)]),default:u(()=>[S(" \u6253\u5370PDF ")]),_:1},8,["href"])]}),_:1})):I("v-if",!0),e(v,{label:"\u8FDB\u5EA6"},{default:u(()=>[x("div",ce,[e(B,{percentage:i.value.progress,theme:"plump"},null,8,["percentage"])])]),_:1}),e(r,{"default-value":[]},{default:u(()=>[e(o,{header:"\u5904\u7406\u65E5\u5FD7"},{default:u(()=>{var a;return[x("pre",null,K((a=i.value)==null?void 0:a.logs.join(`
`)),1)]}),_:1})]),_:1})]),_:1})]),_:1},8,["visible"])):I("v-if",!0)])}}});var M=N(pe,[["__file","/Users/jkguo/workspace/ec-erp-static/src/pages/warehouse/components/orderPrintProgressDialog.vue"]]);const de={name:"OrderPrintConfirmDialog",components:{OrderPrintProgressDialog:M}},fe=q({...de,setup(p,{expose:C}){const k=s(null),f=s(!1),i=s(""),c=s([]),h=s([]),w=async(l,t)=>{h.value=t,i.value=`\u672C\u6B21\u6253\u5370 ${t.length} \u5355 / \u5171 ${l} \u5355`,f.value=!0,await b()},b=async()=>{try{const l={order_list:h.value},t=await oe(l);return c.value=[],t.need_manual_mark_sku_list.forEach(d=>{c.value.push({sku:d.sku,image_url:d.image_url,picking_unit:0,picking_unit_name:"pcs",picking_sku_name:d.sku})}),console.log("manualMarkSkuList",c.value),c.value.length>0?(await m.info("\u9700\u8981\u8865\u5145sku\u62E3\u8D27\u5907\u6CE8."),null):(console.log("\u63D0\u4EA4\u6253\u5370\u8BA2\u5355\u6210\u529F\uFF0C\u9762\u5355id",t.task_id),t.task_id)}catch(l){console.error(l),await m.error(`\u6253\u5370\u8BA2\u5355\u5931\u8D25: ${l}`)}return null},D=async()=>{if(c.value.length===0)return!0;let l=!0;if(c.value.forEach(t=>{t.picking_unit<=0&&(m.info(`${t.sku} picking_unit \u672A\u586B`),l=!1),t.picking_unit_name===""&&(m.info(`${t.sku} picking_unit_name \u672A\u586B`),l=!1),t.picking_sku_name===""&&(m.info(`${t.sku} picking_sku_name \u672A\u586B`),l=!1)}),!l)return!1;try{const t={manual_mark_sku_list:c.value};return await ie(t),!0}catch(t){return console.error(t),await m.error(`\u6DFB\u52A0sku\u62E3\u8D27\u5907\u6CE8\u5931\u8D25: ${t}`),!1}},O=async l=>{try{const d=await re({task_id:l});console.log("task",d),f.value=!1,k.value.popupDialog(l)}catch(t){console.error(t),await m.error(`\u542F\u52A8\u540E\u53F0\u4EFB\u52A1\u5931\u8D25: ${t}`)}},F=async()=>{if(!await D())return;const t=await b();t!=null&&await O(t)};return C({popupDialog:w}),(l,t)=>{const d=n("t-input"),v=n("t-form-item"),V=n("t-list-item-meta"),P=n("t-input-number"),B=n("t-space"),o=n("t-list-item"),r=n("t-list"),_=n("t-form"),$=n("t-dialog");return y(),T("div",null,[f.value?(y(),U($,{key:0,visible:f.value,"onUpdate:visible":t[0]||(t[0]=a=>f.value=a),"close-on-esc-keydown":!1,"close-on-overlay-click":!1,"confirm-btn":"\u786E\u8BA4 & \u63D0\u4EA4\u6253\u5370",header:"\u8BA2\u5355\u6253\u5370\u4FE1\u606F\u786E\u8BA4","show-overlay":"",width:"80%",onConfirm:F},{default:u(()=>[e(_,null,{default:u(()=>[e(v,{label:"\u8BA2\u5355\u6570"},{default:u(()=>[e(d,{value:i.value,disabled:""},null,8,["value"])]),_:1}),e(v,{label:"sku\u62E3\u8D27\u5907\u6CE8"},{default:u(()=>[e(B,{direction:"vertical"},{default:u(()=>[e(r,{split:!0,stripe:""},{default:u(()=>[(y(!0),T(z,null,L(c.value,a=>(y(),U(o,{key:a==null?void 0:a.sku},{default:u(()=>[e(V,{image:a.image_url,title:a==null?void 0:a.sku,description:"sku\u62E3\u8D27\u5907\u6CE8"},null,8,["image","title"]),e(B,{direction:"vertical"},{default:u(()=>[e(v,{label:"1\u62E3\u8D27\u5355\u4F4D="},{default:u(()=>[e(P,{modelValue:a.picking_unit,"onUpdate:modelValue":E=>a.picking_unit=E},null,8,["modelValue","onUpdate:modelValue"]),S(" SKU ")]),_:2},1024),e(v,{label:"\u62E3\u8D27\u5355\u4F4D\u540D"},{default:u(()=>[e(d,{modelValue:a.picking_unit_name,"onUpdate:modelValue":E=>a.picking_unit_name=E},null,8,["modelValue","onUpdate:modelValue"])]),_:2},1024),e(v,{label:"\u62E3\u8D27sku\u540D"},{default:u(()=>[e(d,{modelValue:a.picking_sku_name,"onUpdate:modelValue":E=>a.picking_sku_name=E},null,8,["modelValue","onUpdate:modelValue"])]),_:2},1024)]),_:2},1024)]),_:2},1024))),128))]),_:1})]),_:1})]),_:1})]),_:1})]),_:1},8,["visible"])):I("v-if",!0),e(M,{ref_key:"orderPrintProgressDialog",ref:k},null,512)])}}});var j=N(fe,[["__file","/Users/jkguo/workspace/ec-erp-static/src/pages/warehouse/components/orderPrintConfirmDialog.vue"]]);const R=p=>(ue("data-v-cf49c91e"),p=p(),ae(),p),me=R(()=>x("br",null,null,-1)),ve=R(()=>x("br",null,null,-1)),ge={class:"table-container"},ke={name:"PrintOrder",components:{OrderPrintConfirmDialog:j}},he=q({...ke,setup(p){const C=s("\u672A\u767B\u5F55"),k=s(null),f=[{width:50,colKey:"row-select",type:"multiple",checkProps:{allowUncheck:!0},align:"center"},{width:120,colKey:"id",title:"id",align:"center"},{width:60,colKey:"platformOrderId",title:"\u8BA2\u5355\u53F7",align:"center"},{width:120,colKey:"packageNo",title:"\u5305\u88F9\u53F7",align:"center"},{width:120,colKey:"shippingCarrierName",title:"\u7269\u6D41",align:"center"},{width:120,colKey:"trackingNo",title:"\u8FD0\u5355\u53F7",align:"center"},{width:120,colKey:"multilingualViewStatus",title:"\u72B6\u6001",align:"center"},{width:120,colKey:"amount",title:"\u91D1\u989D",align:"center"},{width:120,colKey:"platform",title:"\u5E73\u53F0",align:"center"}],i=s([]),c=s(!1),h=s([]),w=s(1),b=s(0),D=s(500),O=[10,20,50,100,200,500,1e3],F=s([]),l=s(null);Z(async()=>{const{query:o}=ee(),{token:r}=o;try{const _=await te(r);C.value=_.userName,await t()}catch(_){console.error(_),await m.error(`\u767B\u9646\u5F02\u5E38: ${_}`)}});const t=async()=>{try{const r=(await ne()).ship_provider_list;console.log("shipProviderList",r),F.value=[],r.forEach(_=>{F.value.push({label:`${_.name}(${_.count})`,value:_.id})})}catch(o){console.error(o),await m.error(`\u67E5\u8BE2\u8BA2\u5355\u7EDF\u8BA1\u4FE1\u606F\u5F02\u5E38: ${o}`)}},d=(o,r)=>{k.value=o,P()},v=(o,{selectedRowData:r})=>{h.value=o},V=({current:o,pageSize:r})=>{w.value=o,D.value=r,P()},P=async()=>{if(c.value=!0,await t(),k.value===null){c.value=!1;return}try{const o={shipping_provider_id:k.value,current_page:w.value,page_size:D.value},r=await le(o);b.value=r.total,i.value=r.list,console.log("waitOrder",b.value,i.value)}catch(o){console.error(o),await m.error(`\u67E5\u8BE2\u8BA2\u5355\u4FE1\u606F\u5F02\u5E38: ${o}`)}c.value=!1},B=async()=>{const o=new Set;if(h.value.forEach(_=>{o.add(_)}),console.log("selected: ",o),o.size<=0){m.info("\u8BF7\u5148\u9009\u4E2D\u9700\u8981\u6253\u5370\u7684\u8BA2\u5355.");return}const r=[];if(i.value.forEach(_=>{o.has(_.id)&&r.push(_)}),r.length!=o.size){m.error("\u9009\u4E2D\u7684\u8BA2\u5355\u4FE1\u606F\u7F3A\u5931\u3002.");return}l.value.popupDialog(b.value,r)};return(o,r)=>{const _=n("t-radio-button"),$=n("t-radio-group"),a=n("t-form-item"),E=n("t-button"),W=n("t-space"),Q=n("t-form"),G=n("t-col"),H=n("t-row"),J=n("t-table"),X=n("t-pagination"),Y=n("t-card");return y(),T("div",null,[e(Y,null,{default:u(()=>[me,e(H,null,{default:u(()=>[e(G,{span:12},{default:u(()=>[e(Q,{layout:"inline"},{default:u(()=>[e(a,{label:"\u7269\u6D41\u65B9\u5F0F"},{default:u(()=>[e($,{modelValue:k.value,"onUpdate:modelValue":r[0]||(r[0]=g=>k.value=g),name:"shipping",variant:"default-filled",onChange:d},{default:u(()=>[(y(!0),T(z,null,L(F.value,g=>(y(),U(_,{value:g.value},{default:u(()=>[S(K(g.label),1)]),_:2},1032,["value"]))),256))]),_:1},8,["modelValue"])]),_:1}),e(a,null,{default:u(()=>[e(W,{size:"small",style:{"align-items":"center","margin-left":"30px"}},{default:u(()=>[e(E,{theme:"default",onClick:P},{default:u(()=>[S("\u5237 \u65B0")]),_:1}),e(E,{theme:"primary",onClick:B},{default:u(()=>[S("\u6253 \u5370")]),_:1})]),_:1})]),_:1})]),_:1})]),_:1})]),_:1}),ve,x("div",ge,[e(J,{columns:f,data:i.value,loading:c.value,"select-on-row-click":!0,"selected-row-keys":h.value,bordered:"",hover:"","row-key":"id",stripe:"",onSelectChange:v},{multilingualViewStatus:u(({row:g})=>[S(K(g.printLabelMark>0?"[\u5DF2\u6253\u5370]"+g.multilingualViewStatus:g.multilingualViewStatus),1)]),_:1},8,["data","loading","selected-row-keys"]),e(X,{modelValue:w.value,"onUpdate:modelValue":r[1]||(r[1]=g=>w.value=g),pageSize:D.value,"onUpdate:pageSize":r[2]||(r[2]=g=>D.value=g),"page-size-options":O,total:b.value,class:"pagination",onChange:V},null,8,["modelValue","pageSize","total"])])]),_:1}),e(j,{ref_key:"orderPrintConfirmDialog",ref:l},null,512)])}}});var we=N(he,[["__scopeId","data-v-cf49c91e"],["__file","/Users/jkguo/workspace/ec-erp-static/src/pages/warehouse/printOrder.vue"]]);export{we as default};
