const $ = (s, root=document) => root.querySelector(s);
const $$ = (s, root=document) => [...root.querySelectorAll(s)];

function num(v,d=0){const n=Number(v);return Number.isFinite(n)?n:d;}
function f(v,d=2){return num(v).toLocaleString("th-TH",{minimumFractionDigits:d,maximumFractionDigits:d});}
function statusSpan(ok){return '<span class="'+(ok?'pass':'fail')+'">'+(ok?'PASS':'FAIL')+'</span>';}

function actionToast(message,type="success"){
  let box=document.getElementById("cvetActionToast");
  if(!box){
    box=document.createElement("div");
    box.id="cvetActionToast";
    document.body.appendChild(box);
  }
  box.className="action-toast "+type+" show";
  box.textContent=message;
  clearTimeout(box._hideTimer);
  box._hideTimer=setTimeout(()=>box.classList.remove("show"),1500);
}

function buttonBusy(btn,text="กำลังทำงาน..."){
  if(!btn)return;
  if(!btn.dataset.cvetOriginalText) btn.dataset.cvetOriginalText=btn.textContent;
  clearTimeout(btn._cvetRestoreTimer);
  btn.disabled=true;
  btn.classList.remove("btn-success","btn-error","btn-ack");
  btn.classList.add("btn-busy");
  btn.textContent=text;
}

function buttonRestore(btn){
  if(!btn)return;
  clearTimeout(btn._cvetRestoreTimer);
  btn.classList.remove("btn-busy","btn-success","btn-error","btn-ack");
  btn.disabled=false;
  if(btn.dataset.cvetOriginalText){
    btn.textContent=btn.dataset.cvetOriginalText;
    delete btn.dataset.cvetOriginalText;
  }
}

function buttonSuccess(btn,text="เสร็จแล้ว ✓",toastText=""){
  if(!btn)return;
  btn.classList.remove("btn-busy","btn-error","btn-ack");
  btn.classList.add("btn-success");
  btn.textContent=text;
  if(toastText) actionToast(toastText,"success");
  btn._cvetRestoreTimer=setTimeout(()=>buttonRestore(btn),1300);
}

function buttonError(btn,text="เกิดข้อผิดพลาด",toastText="ทำรายการไม่สำเร็จ"){
  if(!btn)return;
  btn.classList.remove("btn-busy","btn-success","btn-ack");
  btn.classList.add("btn-error");
  btn.textContent=text;
  if(toastText) actionToast(toastText,"error");
  btn._cvetRestoreTimer=setTimeout(()=>buttonRestore(btn),1700);
}

function buttonAck(btn){
  if(!btn || btn.disabled || btn.classList.contains("btn-busy") || btn.classList.contains("btn-success") || btn.classList.contains("btn-error")) return;
  btn.classList.add("btn-ack");
  clearTimeout(btn._cvetAckTimer);
  btn._cvetAckTimer=setTimeout(()=>btn.classList.remove("btn-ack"),420);
}

// ทุกปุ่มบนเว็บตอบสนองทันทีเมื่อกด แม้ปุ่มนั้นไม่ใช่ปุ่มคำนวณ
document.addEventListener("click",(evt)=>{
  const btn=evt.target.closest("button");
  if(btn) buttonAck(btn);
});

function formObject(form){
  const out={};
  new FormData(form).forEach((value,key)=>{
    const el=form.elements[key];
    out[key]=(el && (el.type==="number"||el.type==="range"))?Number(value):value;
  });
  return out;
}
function getPin(){return localStorage.getItem("cvet_web_pin")||"";}

const CVET_INPUT_STORE="cvet_web_inputs_v1";

function storedInputElements(){
  const els=[];
  ["driveForm","rampForm","batteryForm","winchForm","stabilityForm"].forEach(id=>{
    const form=$("#"+id);
    if(form) els.push(...$$("input,select",form));
  });
  ["projectVehicleWidth","projectVehicleLength","projectCraneRotation","projectDriveControl"].forEach(id=>{
    const el=$("#"+id); if(el) els.push(el);
  });
  return els;
}

function inputStorageKey(el){
  const form=el.closest("form");
  return (form?form.id:"project")+"."+(el.name||el.id);
}

function saveWebInputs(){
  try{
    const data={};
    storedInputElements().forEach(el=>{
      data[inputStorageKey(el)]=el.type==="checkbox"?!!el.checked:el.value;
    });
    localStorage.setItem(CVET_INPUT_STORE,JSON.stringify(data));
  }catch(e){}
}

function restoreWebInputs(){
  try{
    const data=JSON.parse(localStorage.getItem(CVET_INPUT_STORE)||"{}");
    storedInputElements().forEach(el=>{
      const key=inputStorageKey(el);
      if(!(key in data)) return;
      if(el.type==="checkbox") el.checked=!!data[key];
      else el.value=data[key];
    });
  }catch(e){}
}

function formValue(formId,name,fallback=0){
  const form=$("#"+formId);
  if(!form||!form.elements[name]) return fallback;
  const raw=form.elements[name].value;
  const n=Number(raw);
  return Number.isFinite(n)?n:fallback;
}

function projectValue(id,fallback=""){
  const el=$("#"+id);
  return el?el.value:fallback;
}

function setParam(id,value){
  const el=$("#"+id); if(el) el.textContent=value;
}

function smart(n,d=1){
  const x=Number(n);
  if(!Number.isFinite(x)) return "—";
  if(Math.abs(x-Math.round(x))<1e-9) return String(Math.round(x));
  return x.toFixed(d).replace(/\.?0+$/,"");
}

function syncVehicleParameters(){
  const width=Number(projectValue("projectVehicleWidth",1000))||1000;
  const length=Number(projectValue("projectVehicleLength",1500))||1500;
  const rotation=Number(projectValue("projectCraneRotation",90));
  const driveControl=projectValue("projectDriveControl","Differential");

  const mass=formValue("batteryForm","mass_kg",formValue("driveForm","mass_kg",300));
  const payload=formValue("stabilityForm","payload_mass_kg",100);
  const mainV=formValue("batteryForm","voltage_v",72);
  const motorW=formValue("batteryForm","motor_rated_w",1500);
  const motors=formValue("batteryForm","motors",2);
  const slope=formValue("batteryForm","slope_deg",19);
  const runtime=formValue("batteryForm","runtime_h",3);
  const arm=formValue("stabilityForm","boom_length_m",1.2);
  const trackM=formValue("stabilityForm","track_width_m",0.7);
  const winchV=formValue("winchForm","winch_voltage_v",12);

  setParam("paramVehicleSize",smart(width,0)+" × "+smart(length,0)+" mm");
  setParam("paramMass",smart(mass,1)+" kg");
  setParam("paramPayload",smart(payload,1)+" kg");
  setParam("paramMainBattery",smart(mainV,1)+" V");
  setParam("paramDriveMotors",smart(motors,0)+" × "+smart(motorW,0)+" W");
  setParam("paramDriveControl",driveControl);
  setParam("paramSlope",smart(slope,1)+"°");
  setParam("paramRuntime",smart(runtime,2)+" h");
  setParam("paramCraneRotation","±"+smart(rotation,1)+"°");
  setParam("paramCraneArm",smart(arm,2)+" m");
  setParam("paramTrack",smart(trackM*1000,0)+" mm");
  setParam("paramWinchSupply",smart(winchV,1)+" V Separate");
}

const CVET_SHARED_STORE="cvet_web_shared_project_v1";

const SHARED_PARAMETER_GROUPS={
  mass_kg:[["driveForm","mass_kg"],["rampForm","mass_kg"],["batteryForm","mass_kg"]],
  slope_deg:[["driveForm","slope_deg"],["batteryForm","slope_deg"],["stabilityForm","slope_deg"]],
  speed_kmh:[["driveForm","speed_kmh"],["batteryForm","speed_kmh"],["winchForm","vehicle_speed_kmh"]],
  voltage_v:[["driveForm","voltage_v"],["batteryForm","voltage_v"]],
  motors:[["driveForm","motors"],["batteryForm","motors"]],
  one_way_m:[["batteryForm","one_way_m"],["winchForm","one_way_m"]],
  runtime_h:[["batteryForm","runtime_h"],["winchForm","operating_hours"]]
};

function getField(formId,name){
  const form=$("#"+formId);
  return form && form.elements[name] ? form.elements[name] : null;
}

function loadSharedProjectValues(){
  try{return JSON.parse(localStorage.getItem(CVET_SHARED_STORE)||"{}");}
  catch(e){return {};}
}

function saveSharedProjectValues(data){
  try{localStorage.setItem(CVET_SHARED_STORE,JSON.stringify(data));}catch(e){}
}

function sharedGroupForElement(el){
  const form=el.closest("form");
  if(!form) return null;
  for(const [group,pairs] of Object.entries(SHARED_PARAMETER_GROUPS)){
    if(pairs.some(([fid,name])=>fid===form.id && name===el.name)) return group;
  }
  return null;
}

function syncSharedProjectParameter(group,value,sourceEl=null){
  const pairs=SHARED_PARAMETER_GROUPS[group]||[];
  pairs.forEach(([formId,name])=>{
    const el=getField(formId,name);
    if(el && el!==sourceEl) el.value=value;
  });
  const data=loadSharedProjectValues();
  data[group]=value;
  saveSharedProjectValues(data);
}

function restoreSharedProjectParameters(){
  const data=loadSharedProjectValues();

  // First install: use the primary project forms as the canonical baseline.
  if(Object.keys(data).length===0){
    const defaults={
      mass_kg:getField("batteryForm","mass_kg")?.value,
      slope_deg:getField("batteryForm","slope_deg")?.value,
      speed_kmh:getField("batteryForm","speed_kmh")?.value,
      voltage_v:getField("batteryForm","voltage_v")?.value,
      motors:getField("batteryForm","motors")?.value,
      one_way_m:getField("batteryForm","one_way_m")?.value,
      runtime_h:getField("batteryForm","runtime_h")?.value
    };
    Object.entries(defaults).forEach(([group,value])=>{
      if(value!==undefined) syncSharedProjectParameter(group,value);
    });
    return;
  }

  Object.entries(data).forEach(([group,value])=>{
    if(group in SHARED_PARAMETER_GROUPS) syncSharedProjectParameter(group,value);
  });
}

function setupSharedProjectParameterSync(){
  Object.entries(SHARED_PARAMETER_GROUPS).forEach(([group,pairs])=>{
    pairs.forEach(([formId,name])=>{
      const el=getField(formId,name);
      if(!el) return;
      ["input","change"].forEach(evt=>el.addEventListener(evt,()=>{
        syncSharedProjectParameter(group,el.value,el);
        saveWebInputs();
        syncVehicleParameters();
      }));
    });
  });
}

function syncTurnEnergyControls(){
  const form=$("#batteryForm");
  if(!form) return;
  const enabled=!!(form.elements.turn_enabled && form.elements.turn_enabled.checked);
  ["turns_per_cycle","turn_angle_deg","turn_time_s","track_width_m","turn_coeff"].forEach(name=>{
    const el=form.elements[name];
    if(el) el.disabled=!enabled;
  });
}

function setupDynamicProjectParameters(){
  restoreWebInputs();
  restoreSharedProjectParameters();

  storedInputElements().forEach(el=>{
    ["input","change"].forEach(evt=>el.addEventListener(evt,()=>{
      saveWebInputs();
      syncVehicleParameters();
    }));
  });
  setupSharedProjectParameterSync();

  // Restore dependent visibility after persisted select values.
  const eventMode=$("#eventMode");
  if(eventMode) $("#manualEventsWrap").classList.toggle("hidden",eventMode.value!=="manual");
  const downMode=$("#downMode");
  if(downMode) $$(".customDown").forEach(x=>x.classList.toggle("hidden",downMode.value!=="custom"));

  const turnEnable=getField("batteryForm","turn_enabled");
  if(turnEnable){
    turnEnable.addEventListener("change",syncTurnEnergyControls);
    syncTurnEnergyControls();
  }

  saveWebInputs();
  syncVehicleParameters();
}

async function api(path,payload){
  const headers={"Content-Type":"application/json"};
  const pin=getPin(); if(pin) headers["X-CVET-PIN"]=pin;
  const res=await fetch(path,{method:"POST",headers:headers,body:JSON.stringify(payload)});
  const data=await res.json().catch(()=>({ok:false,message:"Invalid server response"}));
  if(res.status===401){
    $("#pinBar").classList.remove("hidden");
    $("#pinStatus").textContent="PIN ไม่ถูกต้อง";
    throw new Error("ต้องกรอก Web PIN ที่ถูกต้อง");
  }
  if(!res.ok||data.ok===false) throw new Error(data.message||"คำนวณไม่สำเร็จ");
  return data.result;
}
function setLoading(el){el.classList.remove("empty");el.innerHTML="<p>กำลังคำนวณ...</p>";}
function setError(el,err){el.classList.remove("empty");el.innerHTML='<div class="error">'+String(err.message||err)+'</div>';}

async function checkHealth(){
  try{
    const res=await fetch("/api/health"); const h=await res.json();
    $("#serverDot").className="dot ok"; $("#serverStatus").textContent="Server Online";
    $("#appVersion").textContent=h.version||"-"; if(h.pin_required) $("#pinBar").classList.remove("hidden");
  }catch(e){$("#serverDot").className="dot bad";$("#serverStatus").textContent="Server Offline";}
}

function openTab(tabName){
  const btn=$('.tab[data-tab="'+tabName+'"]');
  const page=$("#"+tabName);
  if(!btn||!page) return;
  $$(".tab").forEach(x=>x.classList.remove("active"));
  $$(".page").forEach(x=>x.classList.remove("active"));
  btn.classList.add("active");
  page.classList.add("active");
  window.scrollTo({top:0,behavior:"smooth"});
}
$$(".tab").forEach(btn=>btn.addEventListener("click",()=>openTab(btn.dataset.tab)));
$$("[data-open-tab]").forEach(card=>card.addEventListener("click",()=>openTab(card.dataset.openTab)));
$("#savePin").addEventListener("click",()=>{localStorage.setItem("cvet_web_pin",$("#webPin").value.trim());$("#pinStatus").textContent="บันทึกแล้ว";});
$("#eventMode").addEventListener("change",()=>{$("#manualEventsWrap").classList.toggle("hidden",$("#eventMode").value!=="manual");});
$("#downMode").addEventListener("change",()=>{$$(".customDown").forEach(x=>x.classList.toggle("hidden",$("#downMode").value!=="custom"));});

$("#calcDrive").addEventListener("click",async(evt)=>{
  const btn=$("#calcDrive"),interactive=!!evt.isTrusted;
  if(interactive) buttonBusy(btn,"กำลังคำนวณ...");
  const out=$("#driveResult");setLoading(out);
  try{
    const r=await api("/api/calc/drive-torque",formObject($("#driveForm")));
    out.innerHTML=
      '<h3>ผลการคำนวณ</h3><div class="metric-grid">'+
      '<div class="metric"><div class="k">แรงรวมก่อน SF</div><div class="v">'+f(r.force_sum_n,1)+' N</div></div>'+
      '<div class="metric"><div class="k">แรงออกแบบหลัง SF</div><div class="v">'+f(r.design_force_n,1)+' N</div></div>'+
      '<div class="metric"><div class="k">แรงบิด / มอเตอร์</div><div class="v">'+f(r.torque_per_motor_nm,2)+' N·m</div></div>'+
      '<div class="metric"><div class="k">รอบล้อ</div><div class="v">'+f(r.wheel_rpm,2)+' rpm</div></div>'+
      '<div class="metric"><div class="k">กำลังเชิงกล / มอเตอร์</div><div class="v">'+f(r.design_mech_power_per_motor_w,1)+' W</div></div>'+
      '<div class="metric"><div class="k">กระแสแบตรวม</div><div class="v">'+f(r.battery_current_a,2)+' A</div></div></div>'+
      '<h3>สูตรหลัก</h3>'+
      '<div class="formula"><b>Fg = m × g × sin(θ)</b><br><b>สูตรภาษาไทย:</b> แรงจากความชัน = มวลรถ × ความเร่งโน้มถ่วง × sin(มุมทางลาด)<br><b>แทนค่า:</b> '+f(r.mass_kg,1)+' × 9.81 × sin('+f(r.slope_deg,1)+'°) = <b>'+f(r.fg_n,2)+' N</b></div>'+
      '<div class="formula"><b>Fdesign = (Fg + Fr + Fa) × SF</b><br><b>สูตรภาษาไทย:</b> แรงออกแบบรวม = (แรงทางลาด + แรงต้านกลิ้ง + แรงเร่ง) × Safety Factor<br><b>ผล:</b> '+f(r.design_force_n,2)+' N</div>'+
      '<div class="formula"><b>T = (Fdesign ÷ จำนวนมอเตอร์) × รัศมีล้อ</b><br><b>ผล:</b> '+f(r.torque_per_motor_nm,2)+' N·m/มอเตอร์</div>'+
      '<p>Traction margin = <b>'+f(r.traction_margin,2)+'</b> • Limit '+f(r.traction_limit_n,1)+' N</p>';
    if(interactive) buttonSuccess(btn,"คำนวณเสร็จ ✓","คำนวณ Drive Torque เสร็จแล้ว");
  }catch(e){setError(out,e);if(interactive) buttonError(btn,"ไม่สำเร็จ","คำนวณ Drive Torque เสร็จแล้ว ไม่สำเร็จ");}
});

let lastRampResult=null;

async function calculateRampGeometry(){
  const out=$("#rampResult");setLoading(out);
  try{
    const r=await api("/api/calc/ramp-geometry",formObject($("#rampForm")));
    lastRampResult=r;

    const measuredAngle=(r.measured_angle_deg===null||r.measured_angle_deg===undefined)
      ? "—" : f(r.measured_angle_deg,2)+"°";

    out.innerHTML=
      '<h3>Ramp Geometry Result</h3>'+
      '<div class="ramp-diagram">'+
      '<svg viewBox="0 0 620 260" role="img" aria-label="Ramp triangle">'+
      '<line x1="80" y1="215" x2="555" y2="215" class="ramp-base"/>'+
      '<line x1="80" y1="215" x2="80" y2="55" class="ramp-rise"/>'+
      '<line x1="80" y1="55" x2="555" y2="215" class="ramp-slant"/>'+
      '<text x="18" y="140">h = '+f(r.rise_cm,1)+' cm</text>'+
      '<text x="275" y="242">x = '+f(r.run_cm,1)+' cm</text>'+
      '<text x="292" y="112" class="slant-label">L = '+f(r.theoretical_slant_cm,2)+' cm</text>'+
      '<text x="475" y="198" class="angle-label">θ = '+f(r.angle_deg,2)+'°</text>'+
      '</svg></div>'+

      '<div class="metric-grid">'+
      '<div class="metric"><div class="k">L ทฤษฎี</div><div class="v">'+f(r.theoretical_slant_cm,2)+' cm</div></div>'+
      '<div class="metric"><div class="k">L ทฤษฎี</div><div class="v">'+f(r.theoretical_slant_m,3)+' m</div></div>'+
      '<div class="metric"><div class="k">มุมทางลาด θ</div><div class="v">'+f(r.angle_deg,2)+'°</div></div>'+
      '<div class="metric"><div class="k">Slope</div><div class="v">'+f(r.slope_percent,2)+'%</div></div>'+
      '<div class="metric"><div class="k">L ที่วัดได้</div><div class="v">'+f(r.measured_slant_cm,2)+' cm</div></div>'+
      '<div class="metric"><div class="k">ต่างจากทฤษฎี</div><div class="v">'+f(r.measured_difference_abs_cm,2)+' cm</div></div>'+
      '<div class="metric"><div class="k">มุมจาก L ที่วัด</div><div class="v">'+measuredAngle+'</div></div>'+
      '<div class="metric"><div class="k">F_slope @ '+f(r.mass_kg,0)+' kg</div><div class="v">'+f(r.f_slope_n,1)+' N</div></div></div>'+

      '<h3>1) ความยาวทางลาดจากพีทาโกรัส</h3>'+
      '<div class="formula"><b>L = √(x² + h²)</b><br>'+
      'แทนค่า: √('+f(r.run_cm,1)+'² + '+f(r.rise_cm,1)+'²) = <b>'+f(r.theoretical_slant_cm,2)+' cm</b> = '+f(r.theoretical_slant_m,3)+' m<br>'+
      'ค่าที่วัดได้ = '+f(r.measured_slant_cm,2)+' cm → ต่างประมาณ <b>'+f(r.measured_difference_abs_cm,2)+' cm</b> ('+f(r.measured_difference_pct,2)+'%)</div>'+

      '<h3>2) มุมทางลาด</h3>'+
      '<div class="formula"><b>θ = tan⁻¹(h / x)</b><br>'+
      'แทนค่า: tan⁻¹('+f(r.rise_cm,1)+' / '+f(r.run_cm,1)+') = <b>'+f(r.angle_deg,2)+'°</b></div>'+

      '<h3>3) เปอร์เซ็นต์ความชัน</h3>'+
      '<div class="formula"><b>Slope (%) = (h / x) × 100</b><br>'+
      'แทนค่า: ('+f(r.rise_cm,1)+' / '+f(r.run_cm,1)+') × 100 = <b>'+f(r.slope_percent,2)+'%</b></div>'+

      '<h3>4) ค่าที่ใช้คำนวณแรงมอเตอร์</h3>'+
      '<div class="formula"><b>F_slope = m g sin(θ)</b><br>'+
      'แทนค่า: '+f(r.mass_kg,1)+' × 9.81 × sin('+f(r.angle_deg,2)+'°) = <b>'+f(r.f_slope_n,2)+' N</b><br>'+
      'ตรวจซ้ำด้วย <b>F_slope = m g (h/L)</b> = '+f(r.f_slope_ratio_n,2)+' N</div>'+

      '<div class="notice"><b>สำคัญ:</b> '+f(r.slope_percent,2)+'% คือเปอร์เซ็นต์ความชัน ไม่ใช่ '+f(r.slope_percent,2)+'°. '+
      'สำหรับสูตร sin/cos ของมอเตอร์ให้ใช้ <b>'+f(r.angle_deg,2)+'°</b>.</div>';
    return r;
  }catch(e){setError(out,e);throw e;}
}

$("#calcRamp").addEventListener("click",async(evt)=>{
  const btn=$("#calcRamp"),interactive=!!evt.isTrusted;
  if(interactive) buttonBusy(btn,"กำลังคำนวณ...");
  try{
    await calculateRampGeometry();
    if(interactive) buttonSuccess(btn,"คำนวณเสร็จ ✓","คำนวณ Ramp Geometry เสร็จแล้ว");
  }catch(err){
    if(interactive) buttonError(btn,"คำนวณไม่สำเร็จ","คำนวณ Ramp Geometry ไม่สำเร็จ");
  }
});

$("#applyRampAngle").addEventListener("click",async()=>{
  const btn=$("#applyRampAngle");buttonBusy(btn,"กำลังใช้ค่า...");
  try{
    const r=lastRampResult||await calculateRampGeometry();
    const value=Number(r.angle_deg).toFixed(4);
    syncSharedProjectParameter("slope_deg",value);
    saveWebInputs();syncVehicleParameters();
    $("#rampResult").insertAdjacentHTML("beforeend",
      '<div class="pass-note">ใช้มุม <b>'+f(r.angle_deg,2)+'°</b> กับ Drive Torque + Main Battery + Stability แล้ว</div>');
    buttonSuccess(btn,"ใช้มุมแล้ว ✓","ใช้มุม "+f(r.angle_deg,2)+"° กับโมดูลที่เกี่ยวข้องแล้ว");
  }catch(err){
    buttonError(btn,"ใช้ค่าไม่สำเร็จ","ใช้มุมทางลาดไม่สำเร็จ");
  }
});

$("#applyRampLength").addEventListener("click",async()=>{
  const btn=$("#applyRampLength");buttonBusy(btn,"กำลังใช้ค่า...");
  try{
    const r=lastRampResult||await calculateRampGeometry();
    const el=getField("batteryForm","slope_length_m");
    if(el) el.value=Number(r.theoretical_slant_m).toFixed(4);
    saveWebInputs();syncVehicleParameters();
    $("#rampResult").insertAdjacentHTML("beforeend",
      '<div class="pass-note">ใช้ความยาวทางลาดทฤษฎี <b>'+f(r.theoretical_slant_m,3)+' m</b> ใน Main Battery แล้ว</div>');
    buttonSuccess(btn,"ใช้ระยะแล้ว ✓","ใช้ Slope Length "+f(r.theoretical_slant_m,3)+" m ใน Main Battery แล้ว");
  }catch(err){
    buttonError(btn,"ใช้ค่าไม่สำเร็จ","ใช้ Slope Length ไม่สำเร็จ");
  }
});

$("#calcBattery").addEventListener("click",async(evt)=>{
  const btn=$("#calcBattery"),interactive=!!evt.isTrusted;
  if(interactive) buttonBusy(btn,"กำลังคำนวณ...");
  const out=$("#batteryResult");setLoading(out);
  try{
    const r=await api("/api/calc/drive-battery",formObject($("#batteryForm")));
    const c=r.candidate||{};
    const bmsCont=(c.bms_cont_a>0?statusSpan(c.bms_cont_ok):'<span class="check">NOT SET</span>');
    const bmsPeak=(c.bms_peak_a>0?statusSpan(c.bms_peak_ok):'<span class="check">NOT SET</span>');
    const compare=(r.comparison||[]).map(x=>
      '<tr><td>'+f(x.capacity_ah,0)+' Ah</td>'+
      '<td>'+f(x.rated_wh,0)+' Wh</td>'+
      '<td>'+f(x.runtime_h,2)+' h</td>'+
      '<td>'+x.full_rounds+'</td>'+
      '<td>'+((x.target_margin_pct>=0?'+':'')+f(x.target_margin_pct,1))+'%</td>'+
      '<td>'+f(x.required_cont_c,2)+' C</td>'+
      '<td>'+f(x.required_peak_c,2)+' C</td>'+
      '<td>'+(x.check==='PASS'?'<span class="pass">PASS*</span>':'<span class="fail">'+x.check+'</span>')+'</td></tr>'
    ).join('');

    out.innerHTML=
      '<h3>Main Battery 72 V — Simple Cycle</h3>'+
      '<div class="notice"><b>1 Cycle</b> = ไป '+f(r.one_way_m,1)+' m + กลับ '+f(r.one_way_m,1)+' m • '+
      'แต่ละเที่ยว = ทางราบ '+f(r.flat_one_way_m,1)+' m + ทางลาด '+f(r.slope_length_m,1)+' m</div>'+

      '<div class="metric-grid">'+
      '<div class="metric"><div class="k">เที่ยวไป</div><div class="v">'+f(r.outbound_drive_energy_wh,3)+' Wh</div></div>'+
      '<div class="metric"><div class="k">เที่ยวกลับ</div><div class="v">'+f(r.return_drive_energy_wh,3)+' Wh</div></div>'+
      '<div class="metric"><div class="k">Drive / Cycle</div><div class="v">'+f(r.trip_drive_energy_wh,3)+' Wh</div></div>'+
      '<div class="metric"><div class="k">Total / Cycle</div><div class="v">'+f(r.total_energy_per_cycle_wh,3)+' Wh</div></div>'+
      '<div class="metric"><div class="k">Cycle เต็ม</div><div class="v">'+r.completed_round_trips+' รอบ</div></div>'+
      '<div class="metric"><div class="k">Energy รวม</div><div class="v">'+f(r.load_energy_wh,1)+' Wh</div></div>'+
      '<div class="metric"><div class="k">Calculated minimum</div><div class="v">'+f(r.design_ah,2)+' Ah</div></div>'+
      '<div class="metric"><div class="k">Practical recommendation</div><div class="v">'+f(r.recommended_ah,2)+' Ah → '+f(r.suggested_ah,0)+' Ah</div></div></div>'+

      '<h3>1) แบ่งเส้นทาง</h3>'+
      '<div class="formula">d_flat = d_oneway − L_slope = '+f(r.one_way_m,2)+' − '+f(r.slope_length_m,2)+
      ' = <b>'+f(r.flat_one_way_m,2)+' m</b><br>'+
      '1 Cycle = 2 × '+f(r.one_way_m,2)+' = <b>'+f(r.cycle_distance_m,2)+' m</b></div>'+

      '<h3>2) Energy ต่อช่วง</h3>'+
      '<div class="formula"><b>ทางราบ:</b> F = Crr·m·g = '+f(r.flat_force_n,2)+' N<br>'+
      'Eflat/เที่ยว = <b>'+f(r.flat_energy_one_way_wh,3)+' Wh</b></div>'+
      '<div class="formula"><b>ขึ้นลาด:</b> F = mg sinθ + Crr·mg cosθ = '+f(r.uphill_force_n,2)+' N<br>'+
      'Eup = <b>'+f(r.uphill_slope_energy_wh,3)+' Wh</b></div>'+
      '<div class="formula"><b>ลงลาด:</b> F = max(0, Crr·mg cosθ − mg sinθ) = '+f(r.downhill_drive_force_n,2)+' N<br>'+
      'Edown = <b>'+f(r.downhill_slope_energy_wh,3)+' Wh</b><br>'+
      'ถ้าช่วงลาดลงใช้ 0 Wh เที่ยวกลับยังไม่เป็น 0 เพราะมีทางราบ '+f(r.flat_one_way_m,1)+' m</div>'+

      '<h3>3) Differential / Pivot Turn</h3>'+
      '<div class="formula">โหมด = <b>'+(r.turn_enabled?'INCLUDED':'NOT INCLUDED')+'</b> • '+r.turns_per_cycle+' ครั้ง/Cycle × '+f(r.turn_angle_deg,0)+'°<br>'+
      's_turn = (W/2)φ = <b>'+f(r.turn_wheel_path_m,3)+' m</b><br>'+
      'F_turn = Cturn·m·g = <b>'+f(r.turn_force_n,2)+' N</b><br>'+
      'E_turn/event = <b>'+f(r.turn_energy_per_event_wh,4)+' Wh</b> • E_turn/Cycle = <b>'+f(r.turn_energy_per_cycle_wh,4)+' Wh</b><br>'+
      'ค่า Cturn เป็นค่าประมาณของการไถลบนพื้นจริง</div>'+
      '<h3>4) รวมเป็น 1 Cycle</h3>'+
      '<div class="formula">Ego = Eflat + Eup = <b>'+f(r.outbound_drive_energy_wh,3)+' Wh</b><br>'+
      'Ereturn = Edown + Eflat = <b>'+f(r.return_drive_energy_wh,3)+' Wh</b><br>'+
      'Edrive,cycle = Ego + Ereturn + Eturn = <b>'+f(r.trip_drive_energy_wh,3)+' Wh</b><br>'+
      'Eaux,cycle = <b>'+f(r.aux_energy_per_cycle_wh,3)+' Wh</b><br>'+
      'Ecycle = <b>'+f(r.total_energy_per_cycle_wh,3)+' Wh/Cycle</b></div>'+

      '<h3>5) จำนวน Cycle และขนาดแบต</h3>'+
      '<div class="formula"><b>t_cycle = t_drive + t_lift + t_other + t_turn</b><br>'+
      f(r.drive_time_per_round_s,2)+' + '+f(r.lift_time_per_round_s,2)+' + '+f(r.other_stop_time_per_round_s,2)+' + '+f(r.turn_time_per_round_s,2)+
      ' = <b>'+f(r.round_time_s,2)+' s</b><br>'+
      'N = floor(runtime/t_cycle) = <b>'+r.completed_round_trips+' Cycle</b><br>'+
      'Etotal = Ecycle × N = <b>'+f(r.load_energy_wh,2)+' Wh</b><br>'+
      'Edesign = (Etotal/DoD)×(1+Reserve) = <b>'+f(r.design_energy_wh,2)+' Wh</b><br>'+
      'Ah_min = Edesign/V = <b>'+f(r.design_ah,2)+' Ah</b><br>'+
      'Ah_practical = Ah_min × Kb = '+f(r.design_ah,2)+' × '+f(r.battery_design_factor,2)+
      ' = <b>'+f(r.recommended_ah,2)+' Ah</b> → ปัดเป็น <b>'+f(r.suggested_ah,0)+' Ah</b></div>'+

      '<div class="notice"><b>แบบจำลองนี้ตั้งใจให้หยาบและอธิบายง่าย:</b> ไม่คิดพลังงานช่วงออกตัว '+
      'และไม่นำพลังงานจากช่วงลงลาดมาหักคืนแบตเตอรี่ • Winch 12 V คำนวณแยก</div>'+

      '<h3>Battery Purchase / Reverse Calculation</h3>'+
      '<div class="metric-grid">'+
      '<div class="metric"><div class="k">Candidate</div><div class="v">'+f(c.capacity_ah,1)+' Ah</div></div>'+
      '<div class="metric"><div class="k">Estimated runtime*</div><div class="v">'+f(c.runtime_h,2)+' h</div></div>'+
      '<div class="metric"><div class="k">Full Cycles*</div><div class="v">'+c.full_rounds+' รอบ</div></div>'+
      '<div class="metric"><div class="k">Margin vs target</div><div class="v">'+(c.target_margin_pct>=0?'+':'')+f(c.target_margin_pct,1)+'%</div></div></div>'+
      '<table><tr><th>Candidate check</th><th>Required</th><th>Candidate</th><th>Status</th></tr>'+
      '<tr><td>Energy / Practical capacity</td><td>≥ '+f(r.recommended_ah,2)+' Ah</td><td>'+f(c.capacity_ah,1)+' Ah</td><td>'+statusSpan(c.energy_ok)+'</td></tr>'+
      '<tr><td>BMS Continuous</td><td>≥ '+f(r.continuous_current_required_a,1)+' A</td><td>'+f(c.bms_cont_a,1)+' A</td><td>'+bmsCont+'</td></tr>'+
      '<tr><td>BMS Peak (simple reference)</td><td>≥ '+f(r.peak_current_required_a,1)+' A</td><td>'+f(c.bms_peak_a,1)+' A</td><td>'+bmsPeak+'</td></tr></table>'+
      '<p class="check">*Runtime/Cycle เป็นค่าประมาณจาก Cycle ปัจจุบัน + DoD + Reserve; พลังงานวินช์ 12 V ไม่รวม</p>'+

      '<h3>Compare Battery Size</h3>'+
      '<div style="overflow:auto"><table><tr><th>Battery</th><th>Rated Wh</th><th>Runtime*</th><th>Full Cycles*</th><th>Margin target</th><th>Req cont C</th><th>Req peak C</th><th>Check</th></tr>'+
      compare+'</table></div>';
    if(interactive) buttonSuccess(btn,"คำนวณเสร็จ ✓","คำนวณ Main Battery เสร็จแล้ว");
  }catch(e){setError(out,e);if(interactive) buttonError(btn,"ไม่สำเร็จ","คำนวณ Main Battery เสร็จแล้ว ไม่สำเร็จ");}
});

$("#calcWinch").addEventListener("click",async(evt)=>{
  const btn=$("#calcWinch"),interactive=!!evt.isTrusted;
  if(interactive) buttonBusy(btn,"กำลังคำนวณ...");
  const out=$("#winchResult");setLoading(out);
  try{
    const r=await api("/api/calc/winch",formObject($("#winchForm"))),c=r.core,o=r.operation,b=r.battery;
    const liftTime=$("#batteryLiftEventTime"), liftEvents=$("#batteryLiftEvents"), otherStop=$("#batteryOtherStop");
    if(liftTime) liftTime.value=Number(o.event_time_s).toFixed(2);
    if(liftEvents) liftEvents.value=o.events_per_round;
    if(otherStop) otherStop.value=Number(o.other_stop_s).toFixed(1);
    out.innerHTML=
      '<h3>Winch Datasheet</h3><div class="metric-grid">'+
      '<div class="metric"><div class="k">First-layer speed</div><div class="v">'+f(c.up_speed_m_min,3)+' m/min</div></div>'+
      '<div class="metric"><div class="k">Current @ load</div><div class="v">'+f(c.up_current_a,2)+' A</div></div>'+
      '<div class="metric"><div class="k">เวลา UP</div><div class="v">'+f(c.up_time_s,2)+' s</div></div></div>'+
      '<p>Rope layer <b>'+c.layer+'</b> • Sheet line pull '+f(c.layer_line_pull_kg,0)+' kg • '+statusSpan(c.layer_pull_ok)+'</p>'+
      '<h3>Operating Cycles</h3><div class="metric-grid">'+
      '<div class="metric"><div class="k">รอบไป-กลับ</div><div class="v">'+o.completed_round_trips+'</div></div>'+
      '<div class="metric"><div class="k">เที่ยวทางเดียว</div><div class="v">'+o.one_way_trips+'</div></div>'+
      '<div class="metric"><div class="k">งานยกจาก 3h</div><div class="v">'+o.lift_events+'</div></div></div>'+
      '<div class="formula"><b>t_event = t_up + t_down</b><br><b>สูตรภาษาไทย:</b> เวลา 1 งานยก = เวลาขึ้น + เวลาลง<br><b>แทนค่า:</b> '+f(o.up_time_s,2)+' + '+f(o.down_time_s,2)+' = <b>'+f(o.event_time_s,2)+' s</b></div>'+
      '<div class="formula"><b>Nround = floor(t_available ÷ t_round)</b><br><b>สูตรภาษาไทย:</b> จำนวนรอบที่ทำได้ครบ = ปัดลง(เวลาทำงานทั้งหมด ÷ เวลาต่อรอบ)<br><b>ผล:</b> '+o.completed_round_trips+' รอบ</div>'+
      '<h3>Winch Battery — '+b.event_mode+'</h3><div class="metric-grid">'+
      '<div class="metric"><div class="k">งานยกที่ใช้คำนวณ</div><div class="v">'+b.events+'</div></div>'+
      '<div class="metric"><div class="k">UP / DOWN</div><div class="v">'+b.up_count+' / '+b.down_count+'</div></div>'+
      '<div class="metric"><div class="k">E / งาน</div><div class="v">'+f(b.e_event_wh,3)+' Wh</div></div>'+
      '<div class="metric"><div class="k">E total</div><div class="v">'+f(b.e_total_wh,2)+' Wh</div></div>'+
      '<div class="metric"><div class="k">Ah used</div><div class="v">'+f(b.ah_used,2)+' Ah</div></div>'+
      '<div class="metric"><div class="k">Ah design</div><div class="v">'+f(b.ah_design,2)+' Ah</div></div></div>'+
      '<div class="formula"><b>Etotal = Nevent × Eevent</b><br><b>สูตรภาษาไทย:</b> พลังงานรวม = จำนวนงานยก × พลังงานต่อ 1 งาน<br><b>แทนค่า:</b> '+b.events+' × '+f(b.e_event_wh,3)+' = <b>'+f(b.e_total_wh,2)+' Wh</b></div>'+
      '<div class="formula"><b>Ahdesign = Etotal × (1 + Reserve) ÷ (V × DoD)</b><br><b>สูตรภาษาไทย:</b> ความจุแบตออกแบบ = พลังงานรวม × (1 + สำรอง) ÷ (แรงดัน × DoD)<br><b>ผล:</b> <b>'+f(b.ah_design,2)+' Ah</b> → Standard ≥ '+f(b.standard_ah,0)+' Ah</div>'+
      '<p>Candidate '+f(b.candidate_ah,1)+' Ah: '+statusSpan(b.candidate_energy_ok)+' • BMS continuous: '+(b.bms_cont_a>0?statusSpan(b.bms_cont_ok):'<span class="check">CHECK</span>')+' • Peak: <span class="check">CHECK</span> (datasheet ไม่มี Starting/Stall surge)</p>';
    if(interactive) buttonSuccess(btn,"คำนวณเสร็จ ✓","คำนวณ Winch เสร็จแล้ว");
  }catch(e){setError(out,e);if(interactive) buttonError(btn,"ไม่สำเร็จ","คำนวณ Winch เสร็จแล้ว ไม่สำเร็จ");}
});


let lastStabilityResult=null;

function fbdSf(v){return Number(v)>=999?'∞':f(v,3);}
function fbdName(key){
  return ({side_left:"Side Left / คว่ำซ้าย",side_right:"Side Right / คว่ำขวา",front:"Front / คว่ำหน้า",rear:"Rear / คว่ำหลัง",slope:"Slope / ทางลาด"})[key]||key;
}
function fbdThaiComponent(name){
  return ({Vehicle:"ตัวรถ",Boom:"แขนเครน",Payload:"น้ำหนักบรรทุก"})[name]||name;
}
function fbdRoleThai(role){
  return role==="overturning"?"ทำให้คว่ำ":role==="resisting"?"ต้านการคว่ำ":"อยู่ที่แกน P";
}
function svgDefs(){
  return '<defs>'+
    '<marker id="arrBlack" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M 0 0 L 10 5 L 0 10 z" fill="#111827"/></marker>'+
    '<marker id="arrGreen" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M 0 0 L 10 5 L 0 10 z" fill="#16803a"/></marker>'+
    '<marker id="arrRed" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M 0 0 L 10 5 L 0 10 z" fill="#b42318"/></marker>'+
    '<marker id="arrPurple" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M 0 0 L 10 5 L 0 10 z" fill="#7c3aed"/></marker>'+
    '</defs>';
}
function svgText(x,y,text,cls){
  return '<text x="'+x+'" y="'+y+'" class="'+(cls||'')+'">'+text+'</text>';
}
function linearMap(values,left,right){
  let lo=Math.min.apply(null,values),hi=Math.max.apply(null,values);
  let span=Math.max(hi-lo,.25);lo-=span*.13;hi+=span*.13;
  return v=>left+(v-lo)*(right-left)/(hi-lo);
}
function roleColor(role){return role==="overturning"?"#b42318":role==="resisting"?"#176337":"#64748b";}

function renderLinearFbd(r,key,bal,view){
  const side=key==="side_left"||key==="side_right";
  const W=1000,H=520,ground=285,deckY=220,boomY=105;
  let supports,positions,pivot,axisLabel;
  if(side){
    supports=[-r.track_width_m/2,r.track_width_m/2];
    positions=bal.components.map(q=>q.y_m);
    pivot=bal.pivot_m;axisLabel="+y right";
  }else{
    supports=[bal.rear_x_m,bal.front_x_m];
    positions=bal.components.map(q=>q.x_m);
    pivot=bal.pivot_m;axisLabel="+x forward";
  }
  const mp=linearMap(supports.concat(positions,[pivot]),100,900);
  const s0=mp(supports[0]),s1=mp(supports[1]),px=mp(pivot);
  let svg='<svg class="engineering-fbd" viewBox="0 0 '+W+' '+H+'" role="img">'+svgDefs();
  svg+='<line x1="55" y1="'+ground+'" x2="945" y2="'+ground+'" class="ground"/>';
  svg+='<rect x="'+(Math.min(s0,s1)-60)+'" y="'+deckY+'" width="'+(Math.abs(s1-s0)+120)+'" height="38" rx="5" class="vehicle-body"/>';
  svg+='<circle cx="'+s0+'" cy="'+ground+'" r="17" class="wheel"/><circle cx="'+s1+'" cy="'+ground+'" r="17" class="wheel"/>';

  const craneBase=side?mp(0):mp(bal.crane_x_m);
  const loadComp=bal.components.find(q=>q.name==="Payload");
  const boomComp=bal.components.find(q=>q.name==="Boom");
  const loadPos=side?loadComp.y_m:loadComp.x_m;
  const loadX=mp(loadPos);
  svg+='<line x1="'+craneBase+'" y1="'+deckY+'" x2="'+craneBase+'" y2="'+boomY+'" class="crane"/>';
  svg+='<line x1="'+craneBase+'" y1="'+boomY+'" x2="'+loadX+'" y2="'+boomY+'" class="crane"/>';
  svg+='<rect x="'+(loadX-16)+'" y="'+(boomY-12)+'" width="32" height="24" class="payload"/>';

  const forceStarts={Vehicle:deckY+16,Boom:boomY+12,Payload:boomY+12};
  bal.components.forEach(q=>{
    const pos=side?q.y_m:q.x_m,x=mp(pos),y0=forceStarts[q.name]||boomY+12,y1=q.name==="Vehicle"?ground-20:boomY+102;
    svg+='<circle cx="'+x+'" cy="'+y0+'" r="4" class="cg"/>';
    svg+='<line x1="'+x+'" y1="'+y0+'" x2="'+x+'" y2="'+y1+'" class="weight-arrow" marker-end="url(#arrBlack)"/>';
    svg+=svgText(x+7,y1-4,'W_'+(q.name==="Vehicle"?'V':q.name==="Boom"?'B':'L')+' '+f(q.force_n,1)+' N','force-label');
  });

  svg+='<circle cx="'+px+'" cy="'+ground+'" r="7" class="pivot"/>'+svgText(px+12,ground-24,'Tipping axis P','pivot-label');
  svg+='<line x1="'+(px+18)+'" y1="'+(ground-5)+'" x2="'+(px+18)+'" y2="'+(ground-83)+'" class="reaction-arrow" marker-end="url(#arrGreen)"/>';
  svg+=svgText(px+27,ground-76,'R_P','reaction-label');

  const other=Math.abs(s0-px)<Math.abs(s1-px)?s1:s0;
  svg+=svgText(other-44,ground+35,'R_opposite = 0','zero-label');

  const lanes=[340,380,420];
  bal.components.forEach((q,i)=>{
    const x=mp(side?q.y_m:q.x_m),y=lanes[i];
    svg+='<line x1="'+px+'" y1="'+(ground+5)+'" x2="'+px+'" y2="'+y+'" class="dim-guide"/>';
    svg+='<line x1="'+x+'" y1="'+(ground-5)+'" x2="'+x+'" y2="'+y+'" class="dim-guide"/>';
    svg+='<line x1="'+px+'" y1="'+y+'" x2="'+x+'" y2="'+y+'" stroke="'+roleColor(q.role)+'" class="dim-line"/>';
    svg+=svgText((px+x)/2-45,y-7,'d_'+(q.name==="Vehicle"?'V':q.name==="Boom"?'B':'L')+' = '+f(q.arm_m,3)+' m','dim-label');
  });

  svg+=svgText(65,66,axisLabel,'axis-label');
  svg+='<line x1="70" y1="82" x2="135" y2="82" class="axis-line" marker-end="url(#arrBlack)"/>';
  svg+=svgText(615,55,'ดำ = Weight','legend-black')+svgText(715,55,'เขียว = Reaction/Resist','legend-green')+svgText(865,55,'แดง = Overturn','legend-red');
  svg+=svgText(60,485,'M_O = '+f(bal.overturning_moment_nm,2)+' N·m   •   M_R = '+f(bal.resisting_moment_nm,2)+' N·m   •   SF = '+fbdSf(bal.sf),'result-label');
  svg+='</svg>';
  return svg;
}

function renderSlopeFbd(r,bal){
  const W=1000,H=520,alpha=(bal.slope_deg||0)*Math.PI/180;
  const ux=Math.cos(alpha),uy=-Math.sin(alpha),nx=-Math.sin(alpha),ny=-Math.cos(alpha);
  const scale=Math.min(310/Math.max(r.wheelbase_m,.2),145/Math.max(bal.combined_cg_height_m,.2));
  const rear={x:245,y:330};
  const front={x:rear.x+ux*r.wheelbase_m*scale,y:rear.y+uy*r.wheelbase_m*scale};
  const proj={x:rear.x+ux*bal.combined_cg_from_rear_m*scale,y:rear.y+uy*bal.combined_cg_from_rear_m*scale};
  const cg={x:proj.x+nx*bal.combined_cg_height_m*scale,y:proj.y+ny*bal.combined_cg_height_m*scale};
  const p=(x)=>Number(x).toFixed(1);
  let svg='<svg class="engineering-fbd" viewBox="0 0 '+W+' '+H+'" role="img">'+svgDefs();
  svg+='<line x1="'+p(rear.x-ux*170)+'" y1="'+p(rear.y-uy*170)+'" x2="'+p(front.x+ux*280)+'" y2="'+p(front.y+uy*280)+'" class="ground slope-ground"/>';
  svg+='<line x1="'+p(rear.x)+'" y1="'+p(rear.y)+'" x2="'+p(front.x)+'" y2="'+p(front.y)+'" class="vehicle-slope"/>';
  svg+='<circle cx="'+p(cg.x)+'" cy="'+p(cg.y)+'" r="6" class="cg"/>'+svgText(cg.x+10,cg.y-12,'Combined CG','cg-label');
  svg+='<circle cx="'+p(rear.x)+'" cy="'+p(rear.y)+'" r="7" class="pivot"/>'+svgText(rear.x+12,rear.y+28,'Rear tipping axis P','pivot-label');
  svg+='<line x1="'+p(rear.x+nx*8)+'" y1="'+p(rear.y+ny*8)+'" x2="'+p(rear.x+nx*90)+'" y2="'+p(rear.y+ny*90)+'" class="reaction-arrow" marker-end="url(#arrGreen)"/>'+svgText(rear.x+nx*96+8,rear.y+ny*96,'N_R','reaction-label');
  svg+=svgText(front.x+14,front.y+28,'N_F = 0','zero-label');

  const wp=120,wn=105,fi=85;
  svg+='<line x1="'+p(cg.x)+'" y1="'+p(cg.y)+'" x2="'+p(cg.x-ux*wp)+'" y2="'+p(cg.y-uy*wp)+'" class="overturn-arrow" marker-end="url(#arrRed)"/>'+svgText(cg.x-ux*wp-35,cg.y-uy*wp+22,'W_parallel','red-label');
  svg+='<line x1="'+p(cg.x)+'" y1="'+p(cg.y)+'" x2="'+p(cg.x-nx*wn)+'" y2="'+p(cg.y-ny*wn)+'" class="weight-arrow" marker-end="url(#arrBlack)"/>'+svgText(cg.x-nx*wn+8,cg.y-ny*wn,'W_normal','force-label');
  const fix=cg.x+nx*17,fiy=cg.y+ny*17;
  svg+='<line x1="'+p(fix)+'" y1="'+p(fiy)+'" x2="'+p(fix-ux*fi)+'" y2="'+p(fiy-uy*fi)+'" class="inertia-arrow" marker-end="url(#arrPurple)"/>'+svgText(fix-ux*fi-18,fiy-uy*fi-12,'F_I = ma','purple-label');

  svg+='<line x1="'+p(rear.x-nx*32)+'" y1="'+p(rear.y-ny*32)+'" x2="'+p(proj.x-nx*32)+'" y2="'+p(proj.y-ny*32)+'" class="dim-line green-dim"/>'+svgText((rear.x+proj.x)/2-35,(rear.y+proj.y)/2-ny*32-8,'d_R = '+f(bal.combined_cg_from_rear_m,3)+' m','dim-label');
  svg+='<line x1="'+p(proj.x+ux*28)+'" y1="'+p(proj.y+uy*28)+'" x2="'+p(cg.x+ux*28)+'" y2="'+p(cg.y+uy*28)+'" class="dim-line"/>'+svgText((proj.x+cg.x)/2+ux*28+8,(proj.y+cg.y)/2+uy*28,'h_CG = '+f(bal.combined_cg_height_m,3)+' m','dim-label');
  svg+=svgText(610,55,'ดำ = Weight','legend-black')+svgText(705,55,'เขียว = Reaction','legend-green')+svgText(825,55,'แดง = Overturn','legend-red')+svgText(920,55,'ม่วง = F_I','legend-purple');
  svg+=svgText(55,480,'M_O = '+f(bal.overturning_moment_nm,2)+' N·m   •   M_R = '+f(bal.resisting_moment_nm,2)+' N·m   •   SF = '+fbdSf(bal.sf),'result-label');
  svg+='</svg>';
  return svg;
}

function fbdFormulaHtml(key,bal,r){
  if(key==="slope"){
    return '<div class="formula-human">'+
      '<h4>สูตรและการแทนค่า — ทางลาด</h4>'+
      '<p><b>W_parallel = mg sinα</b><br><b>อ่านแบบภาษาคน:</b> มวลรถ × แรงโน้มถ่วง × sin(มุมทางลาด) = แรงที่ดึงรถลงตามทางลาด<br>'+
      '<b>แทนค่า:</b> '+f(r.total_mass_kg,2)+' × 9.81 × sin('+f(bal.slope_deg,2)+'°) = <b>'+f(bal.w_parallel_n,2)+' N</b></p>'+
      '<p><b>W_normal = mg cosα</b><br><b>อ่านแบบภาษาคน:</b> มวลรถ × แรงโน้มถ่วง × cos(มุมทางลาด) = แรงที่กดรถเข้าหาพื้น<br>'+
      '<b>ผล:</b> <b>'+f(bal.w_normal_n,2)+' N</b></p>'+
      '<p><b>F_I = ma</b> = '+f(r.total_mass_kg,2)+' × '+f(bal.accel_mps2,3)+' = <b>'+f(bal.inertia_n,2)+' N</b></p>'+
      '<p><b>M_O = (W_parallel + F_I)h_CG</b> = ('+f(bal.w_parallel_n,2)+' + '+f(bal.inertia_n,2)+') × '+f(bal.combined_cg_height_m,3)+' = <b>'+f(bal.overturning_moment_nm,2)+' N·m</b></p>'+
      '<p><b>M_R = W_normal d_R</b> = '+f(bal.w_normal_n,2)+' × '+f(bal.combined_cg_from_rear_m,3)+' = <b>'+f(bal.resisting_moment_nm,2)+' N·m</b></p>'+
      '<p><b>SF = M_R ÷ M_O</b> = '+f(bal.resisting_moment_nm,2)+' ÷ '+f(bal.overturning_moment_nm,2)+' = <b>'+fbdSf(bal.sf)+'</b> '+statusSpan(bal.pass)+'</p>'+
      '</div>';
  }
  const comps=bal.components||[];
  const mo=comps.filter(q=>q.role==="overturning");
  const mr=comps.filter(q=>q.role==="resisting");
  const term=(q)=>'('+f(q.force_n,2)+' N × '+f(q.arm_m,3)+' m)';
  const details=(arr)=>arr.length?arr.map(q=>'• '+q.name+' / '+fbdThaiComponent(q.name)+': '+f(q.force_n,2)+' N × '+f(q.arm_m,3)+' m = '+f(q.moment_nm,2)+' N·m').join('<br>'):'• ไม่มีแรงในฝั่งนี้';
  return '<div class="formula-human">'+
    '<h4>สูตรและการแทนค่า — '+fbdName(key)+'</h4>'+
    '<p><b>M_O = Σ(F_i d_i)</b><br><b>อ่านสูตรแบบภาษาคน:</b> แรงของแต่ละส่วนที่ทำให้รถคว่ำ × ระยะตั้งฉากถึงแกน P แล้วบวกกันทั้งหมด<br>'+
    '<b>ตัวแปร:</b> M_O = โมเมนต์คว่ำ, Σ = รวมทุกพจน์, F_i = แรงของชิ้นส่วน, d_i = แขนโมเมนต์<br>'+
    '<b>แต่ละพจน์:</b><br>'+details(mo)+'<br><b>แทนค่า:</b> '+(mo.length?mo.map(term).join(' + '):'0')+' = <b>'+f(bal.overturning_moment_nm,2)+' N·m</b></p>'+
    '<p><b>M_R = Σ(F_i d_i)</b><br><b>อ่านสูตรแบบภาษาคน:</b> แรงของแต่ละส่วนที่ช่วยต้านการคว่ำ × ระยะถึงแกน P แล้วบวกกันทั้งหมด<br>'+
    '<b>แต่ละพจน์:</b><br>'+details(mr)+'<br><b>แทนค่า:</b> '+(mr.length?mr.map(term).join(' + '):'0')+' = <b>'+f(bal.resisting_moment_nm,2)+' N·m</b></p>'+
    '<p><b>SF = M_R ÷ M_O</b><br><b>อ่านสูตรแบบภาษาคน:</b> โมเมนต์ต้าน ÷ โมเมนต์คว่ำ<br>'+
    '<b>แทนค่า:</b> '+(bal.overturning_moment_nm>1e-9?f(bal.resisting_moment_nm,2)+' ÷ '+f(bal.overturning_moment_nm,2)+' = '+fbdSf(bal.sf):'ไม่มีโมเมนต์คว่ำ → SF = ∞')+
    ' &nbsp; '+statusSpan(bal.pass)+'</p></div>';
}

function renderWebFbd(){
  if(!lastStabilityResult)return;
  const key=$("#webFbdCase").value,view=$("#webFbdView").value;
  const source=view==="critical"?lastStabilityResult.critical_cases:lastStabilityResult.current_cases;
  const bal=source[key];
  if(!bal)return;
  const angle=key==="slope"?'α='+f(bal.slope_deg,2)+'°':'θ='+f(bal.angle_deg,1)+'°';
  $("#webFbdContext").innerHTML='<b>'+(view==="critical"?'CRITICAL CASE':'CURRENT ANGLE')+'</b> • '+fbdName(key)+' • '+angle+' • SF '+fbdSf(bal.sf)+' • '+statusSpan(bal.pass);
  const canvas=$("#webFbdCanvas");
  canvas.classList.remove("empty");
  canvas.innerHTML=key==="slope"?renderSlopeFbd(lastStabilityResult,bal):renderLinearFbd(lastStabilityResult,key,bal,view);
  $("#webFbdFormula").innerHTML=fbdFormulaHtml(key,bal,lastStabilityResult);
}

$("#webFbdCase").addEventListener("change",renderWebFbd);
$("#webFbdView").addEventListener("change",renderWebFbd);

$("#calcStability").addEventListener("click",async(evt)=>{
  const btn=$("#calcStability"),interactive=!!evt.isTrusted;
  if(interactive) buttonBusy(btn,"กำลังคำนวณ...");
  const out=$("#stabilityResult");setLoading(out);
  try{
    const r=await api("/api/calc/stability",formObject($("#stabilityForm")));
    lastStabilityResult=r;
    const cg=r.current_governing,crit=r.critical_governing;
    const cgSf=fbdSf(cg.sf),critSf=fbdSf(crit.sf);
    out.innerHTML=
      '<h3>Stability Result</h3><div class="metric-grid">'+
      '<div class="metric"><div class="k">Current Governing</div><div class="v">'+cgSf+'</div><div>'+fbdName(cg.key)+' • '+statusSpan(cg.pass)+'</div></div>'+
      '<div class="metric"><div class="k">Critical Worst</div><div class="v">'+critSf+'</div><div>'+fbdName(crit.key)+' • '+statusSpan(crit.pass)+'</div></div>'+
      '<div class="metric"><div class="k">Required SF</div><div class="v">'+f(r.required_sf,2)+'</div><div>เกณฑ์ออกแบบ</div></div></div>'+
      '<h3>Current Angle '+f(r.crane_angle_deg,1)+'°</h3>'+
      '<table><tr><th>Case</th><th>SF</th><th>Status</th></tr>'+
      ['side_left','side_right','front','rear','slope'].map(k=>'<tr><td>'+fbdName(k)+'</td><td>'+fbdSf(r.current_cases[k].sf)+'</td><td>'+statusSpan(r.current_cases[k].pass)+'</td></tr>').join('')+
      '</table>'+
      '<p class="check">เลือก Case และ Current/Critical ด้านล่างเพื่อดู FBD, Moment arm และสูตรแทนค่าจริง</p>';
    renderWebFbd();
    if(interactive) buttonSuccess(btn,"คำนวณเสร็จ ✓","คำนวณ Stability + FBD เสร็จแล้ว");
  }catch(e){setError(out,e);if(interactive) buttonError(btn,"ไม่สำเร็จ","คำนวณ Stability + FBD เสร็จแล้ว ไม่สำเร็จ");}
});

setupDynamicProjectParameters();
checkHealth();
setTimeout(()=>$("#calcRamp").click(),180);
setTimeout(()=>$("#calcWinch").click(),300);
setTimeout(()=>$("#calcStability").click(),420);
