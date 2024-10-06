import{i as U,_ as L,d as M,r,a,b as D,c as x,h as A,w as u,e,g as S,j as K,f as I,t as z,M as g,F as j,n as R,o as Z,p as ee,q as te,s as ue,v as ae}from"./index.ff9bc0ad.js";const ne=()=>U.post("/erp_api/warehouse/get_wait_print_order_ship_provider_list",{}),le=f=>U.post("/erp_api/warehouse/search_wait_print_order",f),oe=f=>U.post("/erp_api/warehouse/pre_submit_print_order",f),ie=f=>U.post("/erp_api/warehouse/start_run_print_order_task",f),re=f=>U.post("/erp_api/warehouse/submit_manual_mark_sku_picking_note",f),se=f=>U.post("/erp_api/warehouse/query_print_order_task",f),ce={style:{width:"80%"}},_e={name:"OrderPrintProgressDialog"},pe=M({..._e,setup(f,{expose:$}){const w=r(""),m=r(!1),s=r(null),c=r(null),E=r(!1),h=async()=>{c.value!==null&&clearTimeout(c.value),await F()||(c.value=setTimeout(h,1e3))},P=()=>s.value===null?!1:s.value.pdf_file_url!==null&&s.value.pdf_file_url!==void 0&&s.value.pdf_file_url!=="",F=async()=>{try{const k={task_id:w.value},o=await se(k);return s.value=o.task,P()?(E.value=!0,console.log("url",s.value.pdf_file_url),window.open(s.value.pdf_file_url,"_blank"),!0):!1}catch(k){return console.error(k),await g.error(`\u67E5\u8BE2\u6253\u5370\u8FDB\u5EA6\u5F02\u5E38: ${k}`),!1}},T=async k=>{w.value=k,E.value=!1,m.value=!0,await h()},B=()=>{c.value!==null&&clearTimeout(c.value),m.value=!1};return $({popupDialog:T}),(k,o)=>{const t=a("t-input"),p=a("t-form-item"),y=a("link-icon"),V=a("t-link"),C=a("t-progress"),n=a("t-collapse-panel"),l=a("t-collapse"),_=a("t-form"),O=a("t-dialog");return D(),x("div",null,[m.value?(D(),A(O,{key:0,visible:m.value,"onUpdate:visible":o[0]||(o[0]=d=>m.value=d),"close-on-esc-keydown":!1,"close-on-overlay-click":!1,"confirm-btn":null,header:"\u6253\u5370\u8BA2\u5355\u4E2D...","show-overlay":"",width:"80%",onCancel:B},{default:u(()=>[e(_,null,{default:u(()=>[e(p,{label:"\u4EFB\u52A1id"},{default:u(()=>{var d;return[e(t,{value:(d=s.value)==null?void 0:d.task_id,disabled:""},null,8,["value"])]}),_:1}),e(p,{label:"\u5F53\u524D\u6B65\u9AA4"},{default:u(()=>{var d;return[e(t,{value:(d=s.value)==null?void 0:d.current_step,current_step:"",disabled:""},null,8,["value"])]}),_:1}),E.value?(D(),A(p,{key:0,label:"\u6253\u5370\u94FE\u63A5"},{default:u(()=>{var d;return[e(V,{href:(d=s.value)==null?void 0:d.pdf_file_url,target:"_blank",theme:"primary",underline:""},{"prefix-icon":u(()=>[e(y)]),default:u(()=>[S(" \u6253\u5370PDF ")]),_:1},8,["href"])]}),_:1})):K("v-if",!0),e(p,{label:"\u8FDB\u5EA6"},{default:u(()=>[I("div",ce,[e(C,{percentage:s.value.progress,theme:"plump"},null,8,["percentage"])])]),_:1}),e(l,{"default-value":[]},{default:u(()=>[e(n,{header:"\u5904\u7406\u65E5\u5FD7"},{default:u(()=>{var d;return[I("pre",null,z((d=s.value)==null?void 0:d.logs.join(`
`)),1)]}),_:1})]),_:1})]),_:1})]),_:1},8,["visible"])):K("v-if",!0)])}}});var W=L(pe,[["__file","/Users/jkguo/workspace/ec-erp-static/src/pages/warehouse/components/orderPrintProgressDialog.vue"]]);const de={name:"OrderPrintConfirmDialog",components:{OrderPrintProgressDialog:W}},fe=M({...de,setup(f,{expose:$}){const w=r(null),m=r(!1),s=r(""),c=r([]),E=r([]),h=r(!1),P=async(o,t)=>{E.value=t,s.value=`\u672C\u6B21\u6253\u5370 ${t.length} \u5355 / \u5171 ${o} \u5355`,m.value=!0,await F()},F=async()=>{try{c.value=[],h.value=!0;const o={order_list:E.value},t=await oe(o);return t.need_manual_mark_sku_list.forEach(p=>{c.value.push({sku:p.sku,image_url:p.image_url,desc:p.desc,picking_unit:0,picking_unit_name:"pcs",picking_sku_name:p.sku,support_pkg_picking:!1,pkg_picking_unit:0,pkg_picking_unit_name:"pkg"})}),console.log("manualMarkSkuList",c.value),h.value=!1,c.value.length>0?(await g.info("\u9700\u8981\u8865\u5145sku\u62E3\u8D27\u5907\u6CE8."),null):(console.log("\u63D0\u4EA4\u6253\u5370\u8BA2\u5355\u6210\u529F\uFF0C\u9762\u5355id",t.task_id),t.task_id)}catch(o){console.error(o),await g.error(`\u6253\u5370\u8BA2\u5355\u5931\u8D25: ${o}`),h.value=!1}return null},T=async()=>{if(c.value.length===0)return!0;let o=!0;if(c.value.forEach(t=>{t.picking_unit<=0&&(g.info(`${t.sku} picking_unit \u672A\u586B`),o=!1),t.picking_unit_name===""&&(g.info(`${t.sku} picking_unit_name \u672A\u586B`),o=!1),t.picking_sku_name===""&&(g.info(`${t.sku} picking_sku_name \u672A\u586B`),o=!1),t.support_pkg_picking&&(t.pkg_picking_unit<=0&&(g.info(`${t.sku} pkg_picking_unit \u672A\u586B`),o=!1),t.pkg_picking_unit_name===""&&(g.info(`${t.sku} pkg_picking_unit_name \u672A\u586B`),o=!1))}),!o)return!1;try{const t={manual_mark_sku_list:c.value};return await re(t),!0}catch(t){return console.error(t),await g.error(`\u6DFB\u52A0sku\u62E3\u8D27\u5907\u6CE8\u5931\u8D25: ${t}`),!1}},B=async o=>{try{const p=await ie({task_id:o});console.log("task",p),m.value=!1,w.value.popupDialog(o)}catch(t){console.error(t),await g.error(`\u542F\u52A8\u540E\u53F0\u4EFB\u52A1\u5931\u8D25: ${t}`)}},k=async()=>{if(!await T())return;const t=await F();t!=null&&await B(t)};return $({popupDialog:P}),(o,t)=>{const p=a("t-input"),y=a("t-form-item"),V=a("t-list-item-meta"),C=a("t-input-number"),n=a("t-checkbox"),l=a("t-space"),_=a("t-list-item"),O=a("t-list"),d=a("t-form"),N=a("t-loading"),q=a("t-dialog");return D(),x("div",null,[m.value?(D(),A(q,{key:0,visible:m.value,"onUpdate:visible":t[0]||(t[0]=i=>m.value=i),"close-on-esc-keydown":!1,"close-on-overlay-click":!1,"confirm-btn":"\u786E\u8BA4 & \u63D0\u4EA4\u6253\u5370",header:"\u8BA2\u5355\u6253\u5370\u4FE1\u606F\u786E\u8BA4","show-overlay":"",width:"80%",onConfirm:k},{default:u(()=>[e(N,{loading:h.value},{default:u(()=>[e(d,null,{default:u(()=>[e(y,{label:"\u8BA2\u5355\u6570"},{default:u(()=>[e(p,{value:s.value,disabled:""},null,8,["value"])]),_:1}),e(y,{label:"sku\u62E3\u8D27\u5907\u6CE8"},{default:u(()=>[e(l,{direction:"vertical"},{default:u(()=>[e(O,{split:!0,stripe:""},{default:u(()=>[(D(!0),x(j,null,R(c.value,i=>(D(),A(_,{key:i==null?void 0:i.sku},{default:u(()=>[e(V,{description:i.desc,image:i.image_url,title:i==null?void 0:i.sku},null,8,["description","image","title"]),e(l,{direction:"vertical"},{default:u(()=>[e(y,{label:"1\u62E3\u8D27\u5355\u4F4D="},{default:u(()=>[e(C,{modelValue:i.picking_unit,"onUpdate:modelValue":v=>i.picking_unit=v},null,8,["modelValue","onUpdate:modelValue"]),S(" SKU ")]),_:2},1024),e(y,{label:"\u62E3\u8D27\u5355\u4F4D\u540D"},{default:u(()=>[e(p,{modelValue:i.picking_unit_name,"onUpdate:modelValue":v=>i.picking_unit_name=v},null,8,["modelValue","onUpdate:modelValue"])]),_:2},1024),e(y,{label:"\u6DFB\u52A0pkg\u6253\u5305"},{default:u(()=>[e(n,{modelValue:i.support_pkg_picking,"onUpdate:modelValue":v=>i.support_pkg_picking=v},null,8,["modelValue","onUpdate:modelValue"])]),_:2},1024),i.support_pkg_picking?(D(),A(y,{key:0,label:"1 PKG ="},{default:u(()=>[e(C,{modelValue:i.pkg_picking_unit,"onUpdate:modelValue":v=>i.pkg_picking_unit=v},null,8,["modelValue","onUpdate:modelValue"]),S(" SKU ")]),_:2},1024)):K("v-if",!0),i.support_pkg_picking?(D(),A(y,{key:1,label:"PKG\u6253\u5305\u5355\u4F4D"},{default:u(()=>[e(p,{modelValue:i.pkg_picking_unit_name,"onUpdate:modelValue":v=>i.pkg_picking_unit_name=v},null,8,["modelValue","onUpdate:modelValue"])]),_:2},1024)):K("v-if",!0),e(y,{label:"\u62E3\u8D27sku\u540D"},{default:u(()=>[e(p,{modelValue:i.picking_sku_name,"onUpdate:modelValue":v=>i.picking_sku_name=v},null,8,["modelValue","onUpdate:modelValue"])]),_:2},1024)]),_:2},1024)]),_:2},1024))),128))]),_:1})]),_:1})]),_:1})]),_:1})]),_:1},8,["loading"])]),_:1},8,["visible"])):K("v-if",!0),e(W,{ref_key:"orderPrintProgressDialog",ref:w},null,512)])}}});var G=L(fe,[["__file","/Users/jkguo/workspace/ec-erp-static/src/pages/warehouse/components/orderPrintConfirmDialog.vue"]]);const Q=f=>(ue("data-v-cf49c91e"),f=f(),ae(),f),ge=Q(()=>I("br",null,null,-1)),me=Q(()=>I("br",null,null,-1)),ke={class:"table-container"},ve={name:"PrintOrder",components:{OrderPrintConfirmDialog:G}},he=M({...ve,setup(f){const $=r("\u672A\u767B\u5F55"),w=r(null),m=[{width:50,colKey:"row-select",type:"multiple",checkProps:{allowUncheck:!0},align:"center"},{width:120,colKey:"id",title:"id",align:"center"},{width:60,colKey:"platformOrderId",title:"\u8BA2\u5355\u53F7",align:"center"},{width:120,colKey:"packageNo",title:"\u5305\u88F9\u53F7",align:"center"},{width:120,colKey:"shippingCarrierName",title:"\u7269\u6D41",align:"center"},{width:120,colKey:"trackingNo",title:"\u8FD0\u5355\u53F7",align:"center"},{width:120,colKey:"multilingualViewStatus",title:"\u72B6\u6001",align:"center"},{width:120,colKey:"amount",title:"\u91D1\u989D",align:"center"},{width:120,colKey:"platform",title:"\u5E73\u53F0",align:"center"}],s=r([]),c=r(!1),E=r([]),h=r(1),P=r(0),F=r(500),T=[10,20,50,100,200,500,1e3],B=r([]),k=r(null);Z(async()=>{const{query:n}=ee(),{token:l}=n;try{const _=await te(l);$.value=_.userName,await o()}catch(_){console.error(_),await g.error(`\u767B\u9646\u5F02\u5E38: ${_}`)}});const o=async()=>{try{const l=(await ne()).ship_provider_list;console.log("shipProviderList",l),B.value=[],l.forEach(_=>{B.value.push({label:`${_.name}(${_.count})`,value:_.id})})}catch(n){console.error(n),await g.error(`\u67E5\u8BE2\u8BA2\u5355\u7EDF\u8BA1\u4FE1\u606F\u5F02\u5E38: ${n}`)}},t=(n,l)=>{w.value=n,V()},p=(n,{selectedRowData:l})=>{E.value=n},y=({current:n,pageSize:l})=>{h.value=n,F.value=l,V()},V=async()=>{if(c.value=!0,await o(),w.value===null){c.value=!1;return}try{const n={shipping_provider_id:w.value,current_page:h.value,page_size:F.value};E.value=[];const l=await le(n);P.value=l.total,s.value=l.list,console.log("waitOrder",P.value,s.value)}catch(n){console.error(n),await g.error(`\u67E5\u8BE2\u8BA2\u5355\u4FE1\u606F\u5F02\u5E38: ${n}`)}c.value=!1},C=async()=>{const n=new Set;if(E.value.forEach(_=>{n.add(_)}),console.log("selected: ",n),n.size<=0){g.info("\u8BF7\u5148\u9009\u4E2D\u9700\u8981\u6253\u5370\u7684\u8BA2\u5355.");return}const l=[];if(s.value.forEach(_=>{n.has(_.id)&&l.push(_)}),l.length!=n.size){g.error("\u9009\u4E2D\u7684\u8BA2\u5355\u4FE1\u606F\u7F3A\u5931\u3002.");return}k.value.popupDialog(P.value,l)};return(n,l)=>{const _=a("t-radio"),O=a("t-space"),d=a("t-radio-group"),N=a("t-form-item"),q=a("t-button"),i=a("t-form"),v=a("t-col"),H=a("t-row"),J=a("t-table"),X=a("t-pagination"),Y=a("t-card");return D(),x("div",null,[e(Y,null,{default:u(()=>[ge,e(H,null,{default:u(()=>[e(v,{span:12},{default:u(()=>[e(i,{layout:"inline"},{default:u(()=>[e(N,{label:"\u7269\u6D41\u65B9\u5F0F"},{default:u(()=>[e(d,{modelValue:w.value,"onUpdate:modelValue":l[0]||(l[0]=b=>w.value=b),name:"shipping",variant:"default-filled",onChange:t},{default:u(()=>[e(O,{direction:"vertical"},{default:u(()=>[(D(!0),x(j,null,R(B.value,b=>(D(),A(_,{value:b.value},{default:u(()=>[S(z(b.label),1)]),_:2},1032,["value"]))),256))]),_:1})]),_:1},8,["modelValue"])]),_:1}),e(N,null,{default:u(()=>[e(O,{size:"small",style:{"align-items":"center","margin-left":"30px"}},{default:u(()=>[e(q,{theme:"default",onClick:V},{default:u(()=>[S("\u5237 \u65B0")]),_:1}),e(q,{theme:"primary",onClick:C},{default:u(()=>[S("\u6253 \u5370")]),_:1})]),_:1})]),_:1})]),_:1})]),_:1})]),_:1}),me,I("div",ke,[e(J,{columns:m,data:s.value,loading:c.value,"select-on-row-click":!0,"selected-row-keys":E.value,bordered:"",hover:"","row-key":"id",stripe:"",onSelectChange:p},{multilingualViewStatus:u(({row:b})=>[S(z(b.printLabelMark>0?"[\u5DF2\u6253\u5370]"+b.multilingualViewStatus:b.multilingualViewStatus),1)]),_:1},8,["data","loading","selected-row-keys"]),e(X,{modelValue:h.value,"onUpdate:modelValue":l[1]||(l[1]=b=>h.value=b),pageSize:F.value,"onUpdate:pageSize":l[2]||(l[2]=b=>F.value=b),"page-size-options":T,total:P.value,class:"pagination",onChange:y},null,8,["modelValue","pageSize","total"])])]),_:1}),e(G,{ref_key:"orderPrintConfirmDialog",ref:k},null,512)])}}});var be=L(he,[["__scopeId","data-v-cf49c91e"],["__file","/Users/jkguo/workspace/ec-erp-static/src/pages/warehouse/printOrder.vue"]]);export{be as default};