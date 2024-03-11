import{m as P,r as v,_ as V,d as S,n as j,p as M,a as s,b as _,j as B,w as t,c as I,F as O,e,f as m,g as x,k as d,q as $,M as E,u as A,t as T,s as q,v as U,x as G,L as J,y as K}from"./index.1f090450.js";const R=(r=60)=>{let c;P(()=>{clearInterval(c)});const l=v(0);return[l,()=>{l.value=r,c=setInterval(()=>{l.value>0?l.value-=1:(clearInterval(c),l.value=0)},1e3)}]};const Q={class:"check-container remember-pwd"},W=S({__name:"Login",setup(r){const c=j(),l={phone:"",account:"admin",password:"admin",verifyCode:"",checked:!1},g={phone:[{required:!0,message:"\u624B\u673A\u53F7\u5FC5\u586B",type:"error"}],account:[{required:!0,message:"\u8D26\u53F7\u5FC5\u586B",type:"error"}],password:[{required:!0,message:"\u5BC6\u7801\u5FC5\u586B",type:"error"}],verifyCode:[{required:!0,message:"\u9A8C\u8BC1\u7801\u5FC5\u586B",type:"error"}]},n=v("password"),y=v(),u=v({...l}),i=v(!1);R(),M();const f=async({validateResult:D})=>{if(D===!0)try{const a={...u.value};console.log("start login...",a),await c.login(a),await E.success("\u767B\u9646\u6210\u529F"),window.location.href="/index.html"}catch(a){console.log(a),await E.error("\u7528\u6237\u767B\u5F55\u5F02\u5E38",a.message)}};return(D,a)=>{const b=s("t-icon"),h=s("t-input"),o=s("t-form-item"),w=s("t-checkbox"),k=s("t-button"),F=s("t-form");return _(),B(F,{ref_key:"form",ref:y,class:$(["item-container",`login-${n.value}`]),data:u.value,rules:g,"label-width":"0",onSubmit:f},{default:t(()=>[n.value=="password"?(_(),I(O,{key:0},[e(o,{name:"account"},{default:t(()=>[e(h,{modelValue:u.value.account,"onUpdate:modelValue":a[0]||(a[0]=C=>u.value.account=C),placeholder:"\u8BF7\u8F93\u5165\u8D26\u53F7\uFF1Aadmin",size:"large"},{"prefix-icon":t(()=>[e(b,{name:"user"})]),_:1},8,["modelValue"])]),_:1}),e(o,{name:"password"},{default:t(()=>[e(h,{modelValue:u.value.password,"onUpdate:modelValue":a[2]||(a[2]=C=>u.value.password=C),type:i.value?"text":"password",clearable:"",placeholder:"\u8BF7\u8F93\u5165\u767B\u5F55\u5BC6\u7801\uFF1Aadmin",size:"large"},{"prefix-icon":t(()=>[e(b,{name:"lock-on"})]),"suffix-icon":t(()=>[e(b,{name:i.value?"browse":"browse-off",onClick:a[1]||(a[1]=C=>i.value=!i.value)},null,8,["name"])]),_:1},8,["modelValue","type"])]),_:1}),m("div",Q,[e(w,null,{default:t(()=>[x("\u8BB0\u4F4F\u8D26\u53F7")]),_:1})])],64)):d("v-if",!0),d(` \u626B\u7801\u767B\u9646
    <template v-else-if="type == 'qrcode'">
      <div class="tip-container">
        <span class="tip">\u8BF7\u4F7F\u7528\u5FAE\u4FE1\u626B\u4E00\u626B\u767B\u5F55</span>
        <span class="refresh">\u5237\u65B0 <t-icon name="refresh" /> </span>
      </div>
      <qrcode-vue value="" :size="192" level="H" />
    </template>
     `),d(` \u624B\u673A\u53F7\u767B\u9646
    <template v-else>
      <t-form-item name="phone">
        <t-input v-model="formData.phone" size="large" placeholder="\u8BF7\u8F93\u5165\u624B\u673A\u53F7\u7801">
          <template #prefix-icon>
            <t-icon name="mobile" />
          </template>
        </t-input>
      </t-form-item>

      <t-form-item class="verification-code" name="verifyCode">
        <t-input v-model="formData.verifyCode" size="large" placeholder="\u8BF7\u8F93\u5165\u9A8C\u8BC1\u7801" />
        <t-button variant="outline" :disabled="countDown > 0" @click="sendCode">
          {{ countDown == 0 ? '\u53D1\u9001\u9A8C\u8BC1\u7801' : \`\${countDown}\u79D2\u540E\u53EF\u91CD\u53D1\` }}
        </t-button>
      </t-form-item>
    </template>
    `),n.value!=="qrcode"?(_(),B(o,{key:1,class:"btn-container"},{default:t(()=>[e(k,{block:"",size:"large",type:"submit"},{default:t(()=>[x(" \u767B\u5F55")]),_:1})]),_:1})):d("v-if",!0),d('    <div class="switch-container">'),d(`      <span v-if="type !== 'password'" class="tip" @click="switchType('password')">\u4F7F\u7528\u8D26\u53F7\u5BC6\u7801\u767B\u5F55</span>`),d(`      <span v-if="type !== 'qrcode'" class="tip" @click="switchType('qrcode')">\u4F7F\u7528\u5FAE\u4FE1\u626B\u7801\u767B\u5F55</span>`),d(`      <span v-if="type !== 'phone'" class="tip" @click="switchType('phone')">\u4F7F\u7528\u624B\u673A\u53F7\u767B\u5F55</span>`),d("    </div>")]),_:1},8,["class","data"])}}});var X=V(W,[["__scopeId","data-v-625567e6"],["__file","/Users/jkguo/workspace/ec-erp-static/src/pages/user/login/components/Login.vue"]]);const z=r=>(q("data-v-21d24194"),r=r(),U(),r),Y=z(()=>m("span",null,"TDesign\u670D\u52A1\u534F\u8BAE",-1)),Z=z(()=>m("span",null,"TDesign \u9690\u79C1\u58F0\u660E",-1)),ee={class:"switch-container"},te=S({__name:"Register",emits:["registerSuccess"],setup(r,{emit:c}){const l={phone:"",email:"",password:"",verifyCode:"",checked:!1},g={phone:[{required:!0,message:"\u624B\u673A\u53F7\u5FC5\u586B",type:"error"}],email:[{required:!0,message:"\u90AE\u7BB1\u5FC5\u586B",type:"error"},{email:!0,message:"\u8BF7\u8F93\u5165\u6B63\u786E\u7684\u90AE\u7BB1",type:"warning"}],password:[{required:!0,message:"\u5BC6\u7801\u5FC5\u586B",type:"error"}],verifyCode:[{required:!0,message:"\u9A8C\u8BC1\u7801\u5FC5\u586B",type:"error"}]},n=v("phone"),y=v(),u=v({...l}),i=v(!1),[f,D]=R(),a=({validateResult:h})=>{if(h===!0){if(!u.value.checked){E.error("\u8BF7\u540C\u610FTDesign\u670D\u52A1\u534F\u8BAE\u548CTDesign \u9690\u79C1\u58F0\u660E");return}E.success("\u6CE8\u518C\u6210\u529F"),c("registerSuccess")}},b=h=>{y.value.reset(),n.value=h};return(h,o)=>{const w=s("t-icon"),k=s("t-input"),F=s("t-form-item"),C=s("t-button"),H=s("t-checkbox"),N=s("t-form");return _(),B(N,{ref_key:"form",ref:y,class:$(["item-container",`register-${n.value}`]),data:u.value,rules:g,"label-width":"0",onSubmit:a},{default:t(()=>[n.value=="phone"?(_(),B(F,{key:0,name:"phone"},{default:t(()=>[e(k,{modelValue:u.value.phone,"onUpdate:modelValue":o[0]||(o[0]=p=>u.value.phone=p),maxlength:11,placeholder:"\u8BF7\u8F93\u5165\u60A8\u7684\u624B\u673A\u53F7",size:"large"},{"prefix-icon":t(()=>[e(w,{name:"user"})]),_:1},8,["modelValue"])]),_:1})):d("v-if",!0),n.value=="email"?(_(),B(F,{key:1,name:"email"},{default:t(()=>[e(k,{modelValue:u.value.email,"onUpdate:modelValue":o[1]||(o[1]=p=>u.value.email=p),placeholder:"\u8BF7\u8F93\u5165\u60A8\u7684\u90AE\u7BB1",size:"large",type:"text"},{"prefix-icon":t(()=>[e(w,{name:"mail"})]),_:1},8,["modelValue"])]),_:1})):d("v-if",!0),e(F,{name:"password"},{default:t(()=>[e(k,{modelValue:u.value.password,"onUpdate:modelValue":o[3]||(o[3]=p=>u.value.password=p),type:i.value?"text":"password",clearable:"",placeholder:"\u8BF7\u8F93\u5165\u767B\u5F55\u5BC6\u7801",size:"large"},{"prefix-icon":t(()=>[e(w,{name:"lock-on"})]),"suffix-icon":t(()=>[e(w,{name:i.value?"browse":"browse-off",onClick:o[2]||(o[2]=p=>i.value=!i.value)},null,8,["name"])]),_:1},8,["modelValue","type"])]),_:1}),n.value=="phone"?(_(),B(F,{key:2,class:"verification-code",name:"verifyCode"},{default:t(()=>[e(k,{modelValue:u.value.verifyCode,"onUpdate:modelValue":o[4]||(o[4]=p=>u.value.verifyCode=p),placeholder:"\u8BF7\u8F93\u5165\u9A8C\u8BC1\u7801",size:"large"},null,8,["modelValue"]),e(C,{disabled:A(f)>0,variant:"outline",onClick:A(D)},{default:t(()=>[x(T(A(f)==0?"\u53D1\u9001\u9A8C\u8BC1\u7801":`${A(f)}\u79D2\u540E\u53EF\u91CD\u53D1`),1)]),_:1},8,["disabled","onClick"])]),_:1})):d("v-if",!0),e(F,{class:"check-container",name:"checked"},{default:t(()=>[e(H,{modelValue:u.value.checked,"onUpdate:modelValue":o[5]||(o[5]=p=>u.value.checked=p)},{default:t(()=>[x("\u6211\u5DF2\u9605\u8BFB\u5E76\u540C\u610F")]),_:1},8,["modelValue"]),Y,x(" \u548C "),Z]),_:1}),e(F,null,{default:t(()=>[e(C,{block:"",size:"large",type:"submit"},{default:t(()=>[x(" \u6CE8\u518C")]),_:1})]),_:1}),m("div",ee,[m("span",{class:"tip",onClick:o[6]||(o[6]=p=>b(n.value=="phone"?"email":"phone"))},T(n.value=="phone"?"\u4F7F\u7528\u90AE\u7BB1\u6CE8\u518C":"\u4F7F\u7528\u624B\u673A\u53F7\u6CE8\u518C"),1)])]),_:1},8,["class","data"])}}});var ue=V(te,[["__scopeId","data-v-21d24194"],["__file","/Users/jkguo/workspace/ec-erp-static/src/pages/user/login/components/Register.vue"]]);const oe={class:"login-header"},ne={class:"operations-container"},ae=S({__name:"Header",setup(r){const c=G(),l=()=>{c.updateConfig({showSettingPanel:!0})},g=()=>{window.open("https://github.com/tencent/tdesign-vue-next-starter")},n=()=>{window.open("http://tdesign.tencent.com/starter/docs/get-started")};return(y,u)=>{const i=s("t-icon"),f=s("t-button");return _(),I("header",oe,[e(A(J),{class:"logo"}),m("div",ne,[e(f,{shape:"square",theme:"default",variant:"text",onClick:g},{default:t(()=>[e(i,{class:"icon",name:"logo-github"})]),_:1}),e(f,{shape:"square",theme:"default",variant:"text",onClick:n},{default:t(()=>[e(i,{class:"icon",name:"help-circle"})]),_:1}),e(f,{shape:"square",theme:"default",variant:"text",onClick:l},{default:t(()=>[e(i,{class:"icon",name:"setting"})]),_:1})])])}}});var se=V(ae,[["__scopeId","data-v-6dfd9e40"],["__file","/Users/jkguo/workspace/ec-erp-static/src/pages/user/login/components/Header.vue"]]);const L=r=>(q("data-v-3682feec"),r=r(),U(),r),re={class:"login-wrapper"},le={class:"login-container"},ie=L(()=>m("div",{class:"title-container"},[m("h1",{class:"title margin-no"},"\u767B\u5F55\u5230"),m("h1",{class:"title"},"EC ERP")],-1)),ce=L(()=>m("footer",{class:"copyright"},"Copyright @ 2021-2022 Tencent. All Rights Reserved",-1)),de={name:"LoginIndex"},pe=S({...de,setup(r){const c=v("login"),l=g=>{c.value=g};return(g,n)=>(_(),I("div",re,[e(se),m("div",le,[ie,c.value==="login"?(_(),B(X,{key:0})):(_(),B(ue,{key:1,onRegisterSuccess:n[0]||(n[0]=y=>l("login"))})),e(K)]),ce]))}});var me=V(pe,[["__scopeId","data-v-3682feec"],["__file","/Users/jkguo/workspace/ec-erp-static/src/pages/user/login/index.vue"]]);export{me as default};