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
  ["driveForm","rampForm","batteryForm","winchForm","winchBatteryForm","stabilityForm"].forEach(id=>{
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
      const key=inputStorageKey(el);
      if(el.type==="radio"){
        if(el.checked) data[key]=el.value;
      }else{
        data[key]=el.type==="checkbox"?!!el.checked:el.value;
      }
    });
    localStorage.setItem(CVET_INPUT_STORE,JSON.stringify(data));
  }catch(e){}
}

function restoreWebInputs(){
  try{
    const data=JSON.parse(localStorage.getItem(CVET_INPUT_STORE)||"{}");

    // V53.8.28 migration: Winch Battery inputs moved from winchForm to a
    // dedicated winchBatteryForm. Preserve values users already entered.
    const moved=["event_mode","manual_events","winch_voltage_v","dod_pct","reserve_pct","candidate_ah","bms_cont_a","bms_peak_a"];
    moved.forEach(name=>{
      const oldKey="winchForm."+name,newKey="winchBatteryForm."+name;
      if(!(newKey in data) && oldKey in data) data[newKey]=data[oldKey];
    });

    storedInputElements().forEach(el=>{
      const key=inputStorageKey(el);
      if(!(key in data)) return;
      if(el.type==="checkbox") el.checked=!!data[key];
      else if(el.type==="radio") el.checked=String(data[key])===String(el.value);
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
  const motorW=formValue("driveForm","motor_rated_w",1500);
  const motors=formValue("driveForm","motors",2);
  const slope=formValue("batteryForm","slope_deg",11.11);
  const runtime=formValue("batteryForm","runtime_h",3);
  const arm=formValue("stabilityForm","boom_length_m",1.2);
  const trackM=formValue("stabilityForm","track_width_m",0.7);
  const winchV=formValue("winchBatteryForm","winch_voltage_v",12);

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
  setParam("paramCraneBase","250 × 250 mm");
  setParam("paramTrack",smart(trackM*1000,0)+" mm");
  setParam("paramWinchSupply",smart(winchV,1)+" V Separate");
}

const CVET_SHARED_STORE="cvet_web_shared_project_v1";

const SHARED_PARAMETER_GROUPS={
  mass_kg:[["driveForm","mass_kg"],["rampForm","mass_kg"],["batteryForm","mass_kg"],["stabilityForm","total_mass_kg"]],
  slope_deg:[["driveForm","slope_deg"],["batteryForm","slope_deg"],["stabilityForm","slope_deg"]],
  speed_kmh:[["driveForm","speed_kmh"],["batteryForm","speed_kmh"],["winchForm","vehicle_speed_kmh"]],
  voltage_v:[["driveForm","voltage_v"],["batteryForm","voltage_v"]],
  motors:[["driveForm","motors"],["batteryForm","motors"]],
  one_way_m:[["batteryForm","one_way_m"],["winchForm","one_way_m"]],
  runtime_h:[["batteryForm","runtime_h"],["winchForm","operating_hours"]],
  track_width_m:[["stabilityForm","track_width_m"],["batteryForm","track_width_m"]]
};
const MANUAL_SHARED_GROUPS=new Set(["slope_deg"]);

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
      if(value!==undefined && !MANUAL_SHARED_GROUPS.has(group)){
        syncSharedProjectParameter(group,value);
      }
    });
    const track=getField("stabilityForm","track_width_m")?.value;
    if(track!==undefined) syncSharedProjectParameter("track_width_m",track);
    return;
  }

  Object.entries(data).forEach(([group,value])=>{
    if(group in SHARED_PARAMETER_GROUPS && !MANUAL_SHARED_GROUPS.has(group)){
      syncSharedProjectParameter(group,value);
    }
  });

  // New shared groups added after older web releases: initialise them from
  // the canonical visible input without overwriting other saved module values.
  if(data.track_width_m===undefined){
    const track=getField("stabilityForm","track_width_m")?.value;
    if(track!==undefined) syncSharedProjectParameter("track_width_m",track);
  }
}

function setupSharedProjectParameterSync(){
  Object.entries(SHARED_PARAMETER_GROUPS).forEach(([group,pairs])=>{
    if(MANUAL_SHARED_GROUPS.has(group)) return;
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

function migrateLegacyMeasuredSlopeDefault(){
  try{
    const marker="cvet_slope_1111_migrated_v53823";
    if(localStorage.getItem(marker)) return;
    const ramp=$("#rampForm");
    const rise=ramp&&ramp.elements.rise_cm?Number(ramp.elements.rise_cm.value):NaN;
    const run=ramp&&ramp.elements.run_cm?Number(ramp.elements.run_cm.value):NaN;
    const fields=[
      getField("driveForm","slope_deg"),
      getField("batteryForm","slope_deg"),
      getField("stabilityForm","slope_deg")
    ];
    const legacy=fields.every(el=>el&&Math.abs(Number(el.value)-19)<1e-6);
    const measured=Math.abs(rise-55)<1e-6&&Math.abs(run-280)<1e-6;
    if(legacy&&measured){
      fields.forEach(el=>{el.value="11.11";});
    }
    localStorage.setItem(marker,"1");
  }catch(e){}
}

function stabilityComponentRows(){
  const body=$("#stabilityComponentBody");
  if(!body) return [];
  return Array.from(body.querySelectorAll("tr")).map(row=>({
    name:$('[data-comp="name"]',row)?.value||"",
    mass_kg:num($('[data-comp="mass"]',row)?.value,0),
    x_m:num($('[data-comp="x"]',row)?.value,0),
    y_m:num($('[data-comp="y"]',row)?.value,0),
    z_m:num($('[data-comp="z"]',row)?.value,0)
  }));
}

function stabilityComponentSummary(rows=stabilityComponentRows()){
  const base=[],boom=[],payload=[];
  rows.forEach(r=>{
    const name=String(r.name||"").toLowerCase();
    if(name.includes("boom")||name.includes("แขนเครน")) boom.push(r);
    else if(name.includes("basket")||name.includes("ตะกร้า")||name.includes("payload")||name.includes("ซากสัตว์")) payload.push(r);
    else base.push(r);
  });
  const group=(items)=>{
    const mass=items.reduce((s,r)=>s+Math.max(0,num(r.mass_kg,0)),0);
    if(mass<=0) return {mass_kg:0,x_m:0,y_m:0,z_m:0};
    const weighted=(key)=>items.reduce((s,r)=>s+Math.max(0,num(r.mass_kg,0))*num(r[key],0),0)/mass;
    return {mass_kg:mass,x_m:weighted("x_m"),y_m:weighted("y_m"),z_m:weighted("z_m")};
  };
  return {total:group(rows),base:group(base),boom:group(boom),payload:group(payload)};
}

function stabilityMassMode(){
  return $('input[name="mass_mode"]:checked',$("#stabilityForm"))?.value||"total";
}

function applyComponentMassPreview(syncProject=true){
  if(stabilityMassMode()!=="components") return;
  const s=stabilityComponentSummary();
  const form=$("#stabilityForm");
  if(!form) return;
  const wb=num(form.elements.wheelbase_m?.value,1.1);
  if(form.elements.total_mass_kg) form.elements.total_mass_kg.value=s.total.mass_kg.toFixed(3);
  if(form.elements.payload_mass_kg) form.elements.payload_mass_kg.value=s.payload.mass_kg.toFixed(3);
  if(form.elements.boom_mass_kg) form.elements.boom_mass_kg.value=s.boom.mass_kg.toFixed(3);
  if(form.elements.vehicle_cg_x_from_center_m) form.elements.vehicle_cg_x_from_center_m.value=s.base.x_m.toFixed(4);
  if(form.elements.vehicle_cg_y_m) form.elements.vehicle_cg_y_m.value=s.base.y_m.toFixed(4);
  if(form.elements.combined_cg_from_rear_m) form.elements.combined_cg_from_rear_m.value=Math.max(0,s.total.x_m+wb/2).toFixed(4);
  if(form.elements.combined_cg_height_m) form.elements.combined_cg_height_m.value=Math.max(0,s.total.z_m).toFixed(4);

  const preview=$("#componentMassPreview");
  const derived=$("#componentDerivedPreview");
  if(preview) preview.textContent="Σm = "+f(s.total.mass_kg,2)+" kg • CG ("+f(s.total.x_m,3)+", "+f(s.total.y_m,3)+", "+f(s.total.z_m,3)+") m";
  if(derived) derived.textContent="Base "+f(s.base.mass_kg,2)+" kg • Boom "+f(s.boom.mass_kg,2)+" kg • Basket+Payload "+f(s.payload.mass_kg,2)+" kg";

  if(syncProject && s.total.mass_kg>0){
    const source=form.elements.total_mass_kg;
    syncSharedProjectParameter("mass_kg",s.total.mass_kg,source);
    saveWebInputs();
    syncVehicleParameters();
  }
}

function syncStabilityMassModeUI(syncProject=true){
  const mode=stabilityMassMode();
  $("#stabilityTotalMassFields")?.classList.toggle("hidden",mode!=="total");
  $("#stabilityComponentMassFields")?.classList.toggle("hidden",mode!=="components");
  Array.from($("#stabilityForm").querySelectorAll(".mass-mode-card")).forEach(card=>{
    const radio=$('input[type="radio"]',card);
    card.classList.toggle("selected",!!radio?.checked);
  });
  if(mode==="components") applyComponentMassPreview(syncProject);
}

function stabilityPayload(){
  const payload=formObject($("#stabilityForm"));
  payload.mass_mode=stabilityMassMode();
  payload.components=stabilityComponentRows();
  return payload;
}

function setupDynamicProjectParameters(){
  restoreWebInputs();
  migrateLegacyMeasuredSlopeDefault();
  restoreSharedProjectParameters();

  storedInputElements().forEach(el=>{
    ["input","change"].forEach(evt=>el.addEventListener(evt,()=>{
      saveWebInputs();
      syncVehicleParameters();
    }));
  });
  setupSharedProjectParameterSync();

  const stabilityForm=$("#stabilityForm");
  if(stabilityForm){
    Array.from(stabilityForm.querySelectorAll('input[name="mass_mode"]')).forEach(el=>el.addEventListener("change",()=>{
      syncStabilityMassModeUI();
      saveWebInputs();
    }));
    Array.from(document.querySelectorAll("#stabilityComponentBody input")).forEach(el=>["input","change"].forEach(evt=>el.addEventListener(evt,()=>{
      if(stabilityMassMode()==="components") applyComponentMassPreview(true);
    })));
    const wb=stabilityForm.elements.wheelbase_m;
    if(wb) ["input","change"].forEach(evt=>wb.addEventListener(evt,()=>{
      if(stabilityMassMode()==="components") applyComponentMassPreview(true);
    }));
    syncStabilityMassModeUI();
  }

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

async function apiGet(path){
  const headers={};
  const pin=getPin(); if(pin) headers["X-CVET-PIN"]=pin;
  const res=await fetch(path,{method:"GET",headers});
  const data=await res.json().catch(()=>({ok:false,message:"Invalid server response"}));
  if(res.status===401){
    $("#pinBar").classList.remove("hidden");
    $("#pinStatus").textContent="PIN ไม่ถูกต้อง";
    throw new Error("ต้องกรอก Web PIN ที่ถูกต้อง");
  }
  if(!res.ok||data.ok===false) throw new Error(data.message||"โหลดข้อมูล Desktop ไม่สำเร็จ");
  return data;
}

function applyDesktopFormValues(formId,values){
  const form=$("#"+formId);
  if(!form||!values) return 0;
  let changed=0;
  Object.entries(values).forEach(([name,value])=>{
    const field=form.elements[name];
    if(!field || value===undefined || value===null) return;

    // RadioNodeList, e.g. Stability mass_mode.
    if(typeof field.length==="number" && !field.tagName && field[0]){
      Array.from(field).forEach(el=>{
        if(el.type==="radio") el.checked=String(el.value)===String(value);
      });
      changed++;return;
    }

    if(field.type==="checkbox"){
      field.checked=!!value;
    }else if(field.type==="radio"){
      field.checked=String(field.value)===String(value);
    }else{
      field.value=String(value);
    }
    changed++;
  });
  return changed;
}

function applyDesktopComponentRows(rows){
  if(!Array.isArray(rows)||!rows.length) return 0;
  const tableRows=Array.from(document.querySelectorAll("#stabilityComponentBody tr"));
  let changed=0;
  rows.slice(0,tableRows.length).forEach((row,index)=>{
    const tr=tableRows[index];
    const pairs=[
      ["name",row.name],["mass",row.mass_kg],["x",row.x_m],["y",row.y_m],["z",row.z_m]
    ];
    pairs.forEach(([key,value])=>{
      const el=$('[data-comp="'+key+'"]',tr);
      if(el && value!==undefined && value!==null){el.value=String(value);changed++;}
    });
  });
  return changed;
}

function refreshDependentWebControlsAfterDesktopSync(){
  syncStabilityMassModeUI(false);
  const eventMode=$("#eventMode");
  if(eventMode) $("#manualEventsWrap").classList.toggle("hidden",eventMode.value!=="manual");
  const downMode=$("#downMode");
  if(downMode) $$(".customDown").forEach(x=>x.classList.toggle("hidden",downMode.value!=="custom"));
  syncTurnEnergyControls();
  saveWebInputs();
  syncVehicleParameters();
}

function recalculateAfterDesktopSync(){
  // Sequence avoids Main Battery running before Winch has refreshed its lift time.
  setTimeout(()=>$("#calcRamp")?.click(),80);
  setTimeout(()=>$("#calcDrive")?.click(),160);
  setTimeout(()=>$("#calcWinch")?.click(),260);
  setTimeout(()=>$("#calcWinchBattery")?.click(),520);
  setTimeout(()=>$("#calcBattery")?.click(),680);
  setTimeout(()=>$("#calcStability")?.click(),820);
}

async function syncDesktopProjectValues(options={}){
  const automatic=!!options.automatic;
  const btn=$("#syncDesktopValues");
  const status=$("#desktopSyncStatus");
  let locked=false;
  try{locked=localStorage.getItem("cvet_web_design_lock_v1")==="1";}catch(e){}
  if(locked){
    if(status)status.textContent="Design Inputs Locked — ปลดล็อกก่อน Sync Desktop";
    if(!automatic)actionToast("ปลดล็อก Design Inputs ก่อน Sync Desktop","error");
    return null;
  }
  if(!automatic) buttonBusy(btn,"กำลัง Sync...");
  if(status) status.textContent="กำลังอ่าน Desktop Save Values...";

  try{
    const data=await apiGet("/api/project-values");
    let changed=0;
    Object.entries(data.forms||{}).forEach(([formId,values])=>{
      changed+=applyDesktopFormValues(formId,values);
    });
    changed+=applyDesktopComponentRows(data.components||[]);

    // Desktop is the source of truth at this moment. Remove old cross-module
    // browser sharing values so they cannot immediately overwrite imported data.
    try{localStorage.removeItem(CVET_SHARED_STORE);}catch(e){}

    refreshDependentWebControlsAfterDesktopSync();

    const stamp=(data.saved_at&&data.saved_at!=="-")?String(data.saved_at).replace("T"," "):"-";
    if(status){
      status.textContent="Desktop V"+(data.desktop_version||"-")+" • "+stamp+" • "+data.source;
      status.classList.remove("sync-error");
      status.classList.add("sync-ok");
    }
    try{
      localStorage.setItem("cvet_desktop_sync_meta",JSON.stringify({
        desktop_version:data.desktop_version||"-",saved_at:data.saved_at||"-",source:data.source||"-"
      }));
    }catch(e){}

    recalculateAfterDesktopSync();
    if(!automatic) buttonSuccess(btn,"Synced ✓","โหลดค่าจาก Desktop แล้ว "+changed+" ค่า");
    return data;
  }catch(err){
    if(status){
      status.textContent=String(err.message||err);
      status.classList.remove("sync-ok");
      status.classList.add("sync-error");
    }
    if(!automatic) buttonError(btn,"Sync ไม่สำเร็จ","โหลด Desktop Save Values ไม่สำเร็จ");
    return null;
  }
}
function setLoading(el){el.classList.remove("empty");el.innerHTML="<p>กำลังคำนวณ...</p>";}
function setError(el,err){el.classList.remove("empty");el.innerHTML='<div class="error">'+String(err.message||err)+'</div>';}

function calcStepCard(no,title,body,finalStep=false){
  return '<section class="calc-step-card'+(finalStep?' final-step':'')+'">'+
    '<div class="calc-step-no">'+no+'</div><div><h5>'+title+'</h5>'+body+'</div></section>';
}
function calcStepSection(title,subtitle,steps){
  return '<div class="formula-human step-formula all-mode-steps">'+
    '<h3>'+title+'</h3><p class="step-meaning">'+subtitle+'</p>'+steps.join('')+'</div>';
}
function driveStepsHtml(r){
  const tractionOk=Number(r.traction_margin)>=1;
  return calcStepSection('STEP-BY-STEP — Drive Torque',
    'ลำดับเดียวกับ Desktop: แปลงค่า → หาแรง → ใส่ Safety Factor → แบ่งต่อมอเตอร์ → ตรวจ Traction/Current',[
      calcStepCard(1,'แปลงล้อ ความเร็ว และความเร่ง',
        '<p><b>r = D×0.0254÷2</b> = <b>'+f(r.wheel_radius_m,4)+' m</b><br>'+
        '<b>v = km/h ÷ 3.6</b> = '+f(r.speed_kmh,2)+'÷3.6 = <b>'+f(r.speed_m_s,4)+' m/s</b><br>'+
        '<b>a = v/t</b> = <b>'+f(r.accel_m_s2,4)+' m/s²</b></p>'),
      calcStepCard(2,'หาแรงต้านแต่ละส่วน',
        '<p><b>F_g = mg sinθ</b> = '+f(r.mass_kg,2)+'×9.81×sin('+f(r.slope_deg,2)+'°) = <b>'+f(r.fg_n,2)+' N</b><br>'+
        '<b>F_r = Crr·mg cosθ</b> = '+f(r.rolling_coeff,4)+'×'+f(r.mass_kg,2)+'×9.81×cos('+f(r.slope_deg,2)+'°) = <b>'+f(r.fr_n,2)+' N</b><br>'+
        '<b>F_a = ma</b> = '+f(r.mass_kg,2)+'×'+f(r.accel_m_s2,4)+' = <b>'+f(r.fa_n,2)+' N</b></p>'),
      calcStepCard(3,'รวมแรงและใส่ Safety Factor',
        '<p><b>F_sum = F_g + F_r + F_a</b> = '+f(r.fg_n,2)+' + '+f(r.fr_n,2)+' + '+f(r.fa_n,2)+' = <b>'+f(r.force_sum_n,2)+' N</b><br>'+
        '<b>F_design = F_sum × SF</b> = '+f(r.force_sum_n,2)+'×'+f(r.safety_factor,2)+' = <b>'+f(r.design_force_n,2)+' N</b></p>'),
      calcStepCard(4,'แรงบิด กำลัง และกระแส',
        '<p><b>F_motor = F_design/n</b> = '+f(r.design_force_n,2)+'÷'+r.motors+' = <b>'+f(r.force_per_motor_n,2)+' N</b><br>'+
        '<b>T = F_motor·r</b> = '+f(r.force_per_motor_n,2)+'×'+f(r.wheel_radius_m,4)+' = <b>'+f(r.torque_per_motor_nm,2)+' N·m/มอเตอร์</b><br>'+
        '<b>P_batt = P_wheel/η</b> = <b>'+f(r.electrical_power_total_w,2)+' W</b><br>'+
        '<b>I_batt = P_batt/V</b> = '+f(r.electrical_power_total_w,2)+'÷'+f(r.voltage_v,1)+' = <b>'+f(r.battery_current_a,2)+' A</b></p>'),
      calcStepCard(5,'ตรวจแรงยึดเกาะ / Traction',
        '<p><b>N_drive = mg cosθ × driven load fraction</b> = <b>'+f(r.driven_normal_load_n,2)+' N</b><br>'+
        '<b>F_traction = μN_drive</b> = '+f(r.traction_coeff,3)+'×'+f(r.driven_normal_load_n,2)+' = <b>'+f(r.traction_limit_n,2)+' N</b><br>'+
        'Traction margin = '+f(r.traction_limit_n,2)+'÷'+f(r.design_force_n,2)+' = <b>'+f(r.traction_margin,3)+'</b> • '+statusSpan(tractionOk)+'</p>'),
      calcStepCard(6,'ตรวจ Rated Power ของมอเตอร์',
        '<p>Required mechanical power / motor = <b>'+f(r.design_mech_power_per_motor_w,1)+' W</b><br>'+
        'Entered rated power / motor = <b>'+f(r.motor_rated_w,1)+' W</b><br>'+
        'Power margin = '+f(r.motor_power_margin,3)+'× • '+statusSpan(!!r.motor_power_ok)+'</p>',true)
    ]);
}
function rampStepsHtml(r){
  const measured=(r.measured_angle_deg===null||r.measured_angle_deg===undefined)?'—':f(r.measured_angle_deg,3)+'°';
  return calcStepSection('STEP-BY-STEP — Ramp Geometry',
    'ใช้ h และ x เป็นชุดหลักสำหรับมุมทางลาด; L ที่วัดใช้ตรวจสอบความสอดคล้อง',[
      calcStepCard(1,'หาความยาวทางลาดทฤษฎี',
        '<p><b>L = √(x²+h²)</b> = √('+f(r.run_cm,2)+'²+'+f(r.rise_cm,2)+'²) = <b>'+f(r.theoretical_slant_cm,3)+' cm</b> = '+f(r.theoretical_slant_m,4)+' m</p>'),
      calcStepCard(2,'หามุมทางลาด',
        '<p><b>θ = tan⁻¹(h/x)</b> = tan⁻¹('+f(r.rise_cm,2)+'/'+f(r.run_cm,2)+') = <b>'+f(r.angle_deg,3)+'°</b></p>'),
      calcStepCard(3,'หา Slope (%)',
        '<p><b>Slope = (h/x)×100</b> = ('+f(r.rise_cm,2)+'/'+f(r.run_cm,2)+')×100 = <b>'+f(r.slope_percent,3)+'%</b></p>'),
      calcStepCard(4,'ตรวจค่าความยาวที่วัดจริง',
        '<p>L measured = '+f(r.measured_slant_cm,2)+' cm • ต่างจากทฤษฎี = <b>'+f(r.measured_difference_abs_cm,3)+' cm</b> ('+f(r.measured_difference_pct,2)+'%)<br>'+
        'มุมจาก L measured = <b>'+measured+'</b></p>'),
      calcStepCard(5,'หาแรงจากความชันสำหรับมอเตอร์',
        '<p><b>F_slope = mg sinθ</b> = '+f(r.mass_kg,2)+'×9.81×sin('+f(r.angle_deg,3)+'°) = <b>'+f(r.f_slope_n,2)+' N</b><br>'+
        'ตรวจซ้ำด้วย <b>mg(h/L)</b> = <b>'+f(r.f_slope_ratio_n,2)+' N</b></p>',true)
    ]);
}
function batteryStepsHtml(r,c){
  return calcStepSection('STEP-BY-STEP — Main Battery 72 V',
    'ยึด Simple Cycle แบบ Desktop: แบ่งเส้นทาง → พลังงานต่อช่วง → พลังงานต่อ Cycle → จำนวน Cycle → Ah → BMS/แบตที่จะซื้อ',[
      calcStepCard(1,'แบ่งเส้นทางและเวลา 1 Cycle',
        '<p><b>d_flat = d_oneway − L_slope</b> = '+f(r.one_way_m,2)+'−'+f(r.slope_length_m,2)+' = <b>'+f(r.flat_one_way_m,2)+' m/เที่ยว</b><br>'+
        '<b>t_cycle = t_drive+t_lift+t_other+t_turn</b> = '+f(r.drive_time_per_round_s,2)+'+'+f(r.lift_time_per_round_s,2)+'+'+f(r.other_stop_time_per_round_s,2)+'+'+f(r.turn_time_per_round_s,2)+' = <b>'+f(r.round_time_s,2)+' s</b></p>'),
      calcStepCard(2,'หาแรงและพลังงานแต่ละช่วง',
        '<p><b>F_flat = Crr·mg</b> = <b>'+f(r.flat_force_n,2)+' N</b><br>'+
        '<b>F_up = mg sinθ + Crr·mg cosθ</b> = <b>'+f(r.uphill_force_n,2)+' N</b><br>'+
        '<b>F_down = max(0,Crr·mg cosθ−mg sinθ)</b> = <b>'+f(r.downhill_drive_force_n,2)+' N</b><br>'+
        'E_flat/เที่ยว = '+f(r.flat_energy_one_way_wh,4)+' Wh • E_up = '+f(r.uphill_slope_energy_wh,4)+' Wh • E_down = '+f(r.downhill_slope_energy_wh,4)+' Wh</p>'),
      calcStepCard(3,'รวม Differential / Pivot Turn ถ้าเปิดใช้',
        '<p>สถานะ = <b>'+(r.turn_enabled?'INCLUDED':'NOT INCLUDED')+'</b><br>'+
        '<b>s_turn = (W/2)φ</b> = '+f(r.turn_wheel_path_m,4)+' m • <b>F_turn = Cturn·mg</b> = '+f(r.turn_force_n,2)+' N<br>'+
        'E_turn/event = '+f(r.turn_energy_per_event_wh,5)+' Wh • E_turn/Cycle = <b>'+f(r.turn_energy_per_cycle_wh,5)+' Wh</b></p>'),
      calcStepCard(4,'รวมพลังงานต่อ 1 Cycle',
        '<p>E_go = <b>'+f(r.outbound_drive_energy_wh,4)+' Wh</b> • E_return = <b>'+f(r.return_drive_energy_wh,4)+' Wh</b><br>'+
        '<b>E_drive,cycle</b> = '+f(r.trip_drive_energy_wh,4)+' Wh<br>'+
        '<b>E_aux,cycle = P_aux·t_cycle</b> = '+f(r.aux_power_w,2)+'×'+f(r.round_time_s/3600,5)+' = '+f(r.aux_energy_per_cycle_wh,4)+' Wh<br>'+
        '<b>E_cycle = '+f(r.total_energy_per_cycle_wh,4)+' Wh</b></p>'),
      calcStepCard(5,'หาจำนวน Cycle และพลังงานรวม',
        '<p><b>N = floor(t_available/t_cycle)</b> = <b>'+r.completed_round_trips+' Cycle</b><br>'+
        '<b>E_drive,total = E_drive,cycle×N</b> = '+f(r.trip_drive_energy_wh,4)+'×'+r.completed_round_trips+' = <b>'+f(r.drive_energy_wh,2)+' Wh</b><br>'+
        '<b>E_aux,total = P_aux×t_runtime</b> = '+f(r.aux_power_w,2)+'×'+f(r.runtime_h,2)+' = <b>'+f(r.aux_energy_wh,2)+' Wh</b><br>'+
        '<b>E_total = E_drive,total + E_aux,total</b> = <b>'+f(r.load_energy_wh,2)+' Wh</b></p>'),
      calcStepCard(6,'แปลงเป็น Wh ออกแบบและ Ah',
        '<p><b>E_nom = E_total/DoD</b> = '+f(r.load_energy_wh,2)+'/'+f(r.dod,3)+' = '+f(r.nominal_energy_wh,2)+' Wh<br>'+
        '<b>E_design = E_nom×(1+Reserve)</b> = <b>'+f(r.design_energy_wh,2)+' Wh</b><br>'+
        '<b>Ah_min = E_design/V</b> = '+f(r.design_energy_wh,2)+'/'+f(r.voltage_v,1)+' = <b>'+f(r.design_ah,2)+' Ah</b><br>'+
        '<b>Ah_practical = Ah_min×Kb</b> = <b>'+f(r.recommended_ah,2)+' Ah</b> → แนะนำมาตรฐาน <b>'+f(r.suggested_ah,0)+' Ah</b></p>'),
      calcStepCard(7,'ตรวจ Continuous / Peak Current และ Candidate Battery',
        '<p>Auxiliary current = P_aux/V = <b>'+f(r.aux_current_a,2)+' A</b><br>'+
        'Continuous = max(Uphill '+f(r.uphill_current_calc_a,2)+' A, Pivot '+f(r.turn_average_current_a,2)+' A) + Aux = <b>'+f(r.continuous_current_required_a,2)+' A</b><br>'+
        'Peak = max(Continuous, Drive Torque ref '+f(r.drive_reference_current_a,2)+' A + Aux) = <b>'+f(r.peak_current_required_a,2)+' A</b><br>'+
        'Candidate '+f(c.capacity_ah,1)+' Ah • Energy '+statusSpan(!!c.energy_ok)+' • BMS Continuous '+(c.bms_cont_a>0?statusSpan(c.bms_cont_ok):'<span class="check">NOT SET</span>')+'</p>',true)
    ]);
}
function winchStepsHtml(r){
  const c=r.core,o=r.operation;
  return calcStepSection('STEP-BY-STEP — Winch / Operating Cycle',
    'ใช้ข้อมูลใบสเปก First Layer แบบเดียวกับ Desktop แล้วคำนวณเวลาและจำนวนรอบการทำงาน',[
      calcStepCard(1,'หาอัตราส่วน Interpolation ของโหลด',
        '<p><b>r = (x−x₁)/(x₂−x₁)</b> = ('+f(c.load_kg,2)+'−'+f(c.interp_lower_load_kg,2)+')/('+f(c.interp_upper_load_kg,2)+'−'+f(c.interp_lower_load_kg,2)+') = <b>'+f(c.interp_alpha,6)+'</b></p>'),
      calcStepCard(2,'Interpolation ความเร็วสลิงและกระแส',
        '<p><b>v = v₁+r(v₂−v₁)</b> = <b>'+f(c.up_speed_m_min,4)+' m/min</b><br>'+
        '<b>I = I₁+r(I₂−I₁)</b> = <b>'+f(c.up_current_a,3)+' A</b></p>'),
      calcStepCard(3,'หาเวลา UP / DOWN และตรวจ Rope Layer',
        '<p><b>t_up = h/v × 60</b> = '+f(c.lift_m,3)+'/'+f(c.up_speed_m_min,4)+'×60 = <b>'+f(o.up_time_s,3)+' s</b><br>'+
        't_down = <b>'+f(o.down_time_s,3)+' s</b> • Rope layer = '+c.layer+' • Line pull = '+f(c.layer_line_pull_kg,0)+' kg • '+statusSpan(c.layer_pull_ok)+'<br>'+
        (c.first_layer_performance_warning?'<span class="check"><b>WARNING:</b> '+c.first_layer_performance_warning+'</span>':'Performance basis: First-layer datasheet')+'</p>'),
      calcStepCard(4,'หาเวลา 1 งานยกและเวลา 1 รอบรถ',
        '<p><b>t_event = t_up+t_down</b> = '+f(o.up_time_s,3)+'+'+f(o.down_time_s,3)+' = <b>'+f(o.event_time_s,3)+' s</b><br>'+
        '<b>t_round = t_drive + N_event·t_event + t_other</b> = <b>'+f(o.round_time_s,3)+' s</b></p>'),
      calcStepCard(5,'หาจำนวนรอบและจำนวนงานยก',
        '<p><b>N_round = floor(t_available/t_round)</b> = <b>'+o.completed_round_trips+' รอบ</b><br>'+
        'เที่ยวทางเดียว = '+o.one_way_trips+' • งานยก = <b>'+o.lift_events+' งาน</b> • Winch moves = '+o.winch_moves+'</p>',true)
    ]);
}
function winchBatteryStepsHtml(r){
  const b=r.battery;
  return calcStepSection('STEP-BY-STEP — Winch Battery 12 V',
    'แบต 12 V คิดแยกจากแบตขับ 72 V; ใช้จำนวนงานยก Auto หรือ Manual ตามโหมดที่เลือก',[
      calcStepCard(1,'กำหนดจำนวนงานยกที่ใช้คำนวณ',
        '<p>Mode = <b>'+b.event_mode+'</b> • N_event = <b>'+b.events+'</b> • UP '+b.up_count+' ครั้ง • DOWN '+b.down_count+' ครั้ง</p>'),
      calcStepCard(2,'หาพลังงานยกขึ้น',
        '<p><b>E_up = V·I_up·t_up/3600</b> = '+f(b.voltage_v,1)+'×'+f(b.up_current_a,3)+'×'+f(b.up_time_s,3)+'/3600 = <b>'+f(b.e_up_wh,4)+' Wh</b></p>'),
      calcStepCard(3,'หาพลังงานลดลง',
        '<p><b>E_down = V·I_down·t_down/3600</b> = '+f(b.voltage_v,1)+'×'+f(b.down_current_a,3)+'×'+f(b.down_time_s,3)+'/3600 = <b>'+f(b.e_down_wh,4)+' Wh</b></p>'),
      calcStepCard(4,'หาพลังงานต่อ 1 งาน และพลังงานรวม',
        '<p><b>E_event = E_up+E_down</b> = <b>'+f(b.e_event_wh,4)+' Wh</b><br>'+
        '<b>E_total = N_event·E_event</b> = '+b.events+'×'+f(b.e_event_wh,4)+' = <b>'+f(b.e_total_wh,3)+' Wh</b></p>'),
      calcStepCard(5,'คำนวณ Ah หลัง DoD + Reserve',
        '<p><b>Ah_design = E_total(1+Reserve)/(V·DoD)</b> = <b>'+f(b.ah_design,3)+' Ah</b><br>'+
        'Standard ≥ <b>'+f(b.standard_ah,0)+' Ah @ '+f(b.voltage_v,0)+' V</b></p>'),
      calcStepCard(6,'ตรวจ Candidate Battery / BMS',
        '<p>Candidate '+f(b.candidate_ah,1)+' Ah = '+statusSpan(b.candidate_energy_ok)+'<br>'+
        'Operating current = '+f(b.operating_current_a,2)+' A • BMS Continuous '+f(b.bms_cont_a,1)+' A = '+(b.bms_cont_a>0?statusSpan(b.bms_cont_ok):'<span class="check">CHECK</span>')+'<br>'+
        'BMS Peak: <span class="check">CHECK DATASHEET — Starting/Stall surge ไม่ระบุ</span></p>',true)
    ]);
}

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
$("#syncDesktopValues")?.addEventListener("click",()=>syncDesktopProjectValues({automatic:false}));
$("#eventMode").addEventListener("change",()=>{$("#manualEventsWrap").classList.toggle("hidden",$("#eventMode").value!=="manual");});
$("#downMode").addEventListener("change",()=>{$$(".customDown").forEach(x=>x.classList.toggle("hidden",$("#downMode").value!=="custom"));});

let lastDriveResult=null;
let lastBatteryResult=null;
let lastWinchResult=null;
let lastWinchBatteryResult=null;

$("#calcDrive").addEventListener("click",async(evt)=>{
  const btn=$("#calcDrive"),interactive=!!evt.isTrusted;
  if(interactive) buttonBusy(btn,"กำลังคำนวณ...");
  const out=$("#driveResult");setLoading(out);
  try{
    const r=await api("/api/calc/drive-torque",formObject($("#driveForm")));
    lastDriveResult=r;
    out.innerHTML=
      '<h3>ผลการคำนวณ</h3><div class="metric-grid">'+
      '<div class="metric"><div class="k">แรงรวมก่อน SF</div><div class="v">'+f(r.force_sum_n,1)+' N</div></div>'+
      '<div class="metric"><div class="k">แรงออกแบบหลัง SF</div><div class="v">'+f(r.design_force_n,1)+' N</div></div>'+
      '<div class="metric"><div class="k">แรงบิด / มอเตอร์</div><div class="v">'+f(r.torque_per_motor_nm,2)+' N·m</div></div>'+
      '<div class="metric"><div class="k">รอบล้อ</div><div class="v">'+f(r.wheel_rpm,2)+' rpm</div></div>'+
      '<div class="metric"><div class="k">กำลังเชิงกล / มอเตอร์</div><div class="v">'+f(r.design_mech_power_per_motor_w,1)+' W</div></div>'+
      '<div class="metric"><div class="k">Rated Motor Power</div><div class="v">'+f(r.motor_rated_w,0)+' W • '+(r.motor_power_ok?'PASS':'FAIL')+'</div></div>'+
      '<div class="metric"><div class="k">กระแสแบตรวม</div><div class="v">'+f(r.battery_current_a,2)+' A</div></div></div>'+
      '<h3>สูตรหลัก</h3>'+
      '<div class="formula"><b>Fg = m × g × sin(θ)</b><br><b>สูตรภาษาไทย:</b> แรงจากความชัน = มวลรถ × ความเร่งโน้มถ่วง × sin(มุมทางลาด)<br><b>แทนค่า:</b> '+f(r.mass_kg,1)+' × 9.81 × sin('+f(r.slope_deg,1)+'°) = <b>'+f(r.fg_n,2)+' N</b></div>'+
      '<div class="formula"><b>Fdesign = (Fg + Fr + Fa) × SF</b><br><b>สูตรภาษาไทย:</b> แรงออกแบบรวม = (แรงทางลาด + แรงต้านกลิ้ง + แรงเร่ง) × Safety Factor<br><b>ผล:</b> '+f(r.design_force_n,2)+' N</div>'+
      '<div class="formula"><b>T = (Fdesign ÷ จำนวนมอเตอร์) × รัศมีล้อ</b><br><b>ผล:</b> '+f(r.torque_per_motor_nm,2)+' N·m/มอเตอร์</div>'+
      '<p>Traction margin = <b>'+f(r.traction_margin,2)+'</b> • Limit '+f(r.traction_limit_n,1)+' N</p>'+
      driveStepsHtml(r);
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

      '<div class="notice"><b>สำคัญ:</b> มุมหลักสำหรับสูตรมอเตอร์คือ <b>θ = atan(h/x) = '+f(r.angle_deg,2)+'°</b>. '+
      'ส่วนมุมจาก L ที่วัดได้ = '+measuredAngle+' เป็นค่าตรวจสอบจากข้อมูลวัดอีกชุดหนึ่ง และอาจต่างกันได้เมื่อ h, x, L_measured ไม่เป็นสามเหลี่ยมเดียวกันพอดี.<br>'+
      '<b>Slope '+f(r.slope_percent,2)+'%</b> เป็นเปอร์เซ็นต์ความชัน ไม่ใช่องศา.</div>'+
      rampStepsHtml(r);
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
    const driveRef=await api("/api/calc/drive-torque",formObject($("#driveForm")));
    lastDriveResult=driveRef;
    const batteryPayload=formObject($("#batteryForm"));
    batteryPayload.drive_reference_current_a=driveRef.battery_current_a;
    const r=await api("/api/calc/drive-battery",batteryPayload);
    lastBatteryResult=r;
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
      '<div class="system-result-head main-72v"><span class="system-chip green">72 V VEHICLE ONLY</span><b>Winch 12 V energy = NOT INCLUDED</b></div>'+
      '<h3>Main Battery 72 V — Simple Cycle</h3>'+
      '<div class="notice"><b>Current check:</b> Aux = '+f(r.aux_current_a,2)+' A • Continuous = max(Uphill '+f(r.uphill_current_calc_a,2)+' A, Pivot '+f(r.turn_average_current_a,2)+' A) + Aux = <b>'+f(r.continuous_current_required_a,2)+' A</b> • Peak = max(Continuous, Drive Torque design reference '+f(r.drive_reference_current_a,2)+' A + Aux) = <b>'+f(r.peak_current_required_a,2)+' A</b></div>'+
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
      'Eaux,cycle = <b>'+f(r.aux_energy_per_cycle_wh,3)+' Wh</b> (ใช้ดูต่อ Cycle)<br>'+
      'Ecycle = <b>'+f(r.total_energy_per_cycle_wh,3)+' Wh/Cycle</b><br>'+
      '<b>หมายเหตุ:</b> ตอน sizing 3 ชั่วโมง โปรแกรมคิด Auxiliary ต่อเนื่องครบ '+f(r.runtime_h,2)+' h รวมช่วงเวลาที่เหลือหลัง Cycle สุดท้ายด้วย</div>'+

      '<h3>5) จำนวน Cycle และขนาดแบต</h3>'+
      '<div class="formula"><b>t_cycle = t_drive + t_lift + t_other + t_turn</b><br>'+
      f(r.drive_time_per_round_s,2)+' + '+f(r.lift_time_per_round_s,2)+' + '+f(r.other_stop_time_per_round_s,2)+' + '+f(r.turn_time_per_round_s,2)+
      ' = <b>'+f(r.round_time_s,2)+' s</b><br>'+
      'N = floor(runtime/t_cycle) = <b>'+r.completed_round_trips+' Cycle</b><br>'+
      'Edrive,total = Edrive,cycle × N = <b>'+f(r.drive_energy_wh,2)+' Wh</b><br>'+
      'Eaux,total = Paux × runtime = <b>'+f(r.aux_energy_wh,2)+' Wh</b><br>'+
      'Etotal = Edrive,total + Eaux,total = <b>'+f(r.load_energy_wh,2)+' Wh</b><br>'+
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
      compare+'</table></div>'+
      batteryStepsHtml(r,c);
    if(interactive) buttonSuccess(btn,"คำนวณเสร็จ ✓","คำนวณ Main Battery เสร็จแล้ว");
  }catch(e){setError(out,e);if(interactive) buttonError(btn,"ไม่สำเร็จ","คำนวณ Main Battery เสร็จแล้ว ไม่สำเร็จ");}
});

$("#calcWinch").addEventListener("click",async(evt)=>{
  const btn=$("#calcWinch"),interactive=!!evt.isTrusted;
  if(interactive) buttonBusy(btn,"กำลังคำนวณ...");
  const out=$("#winchResult");setLoading(out);
  try{
    const r=await api("/api/calc/winch",formObject($("#winchForm"))),c=r.core,o=r.operation;
    lastWinchResult=r;
    const liftTime=$("#batteryLiftEventTime"), liftEvents=$("#batteryLiftEvents"), otherStop=$("#batteryOtherStop");
    if(liftTime) liftTime.value=Number(o.event_time_s).toFixed(2);
    if(liftEvents) liftEvents.value=o.events_per_round;
    if(otherStop) otherStop.value=Number(o.other_stop_s).toFixed(1);

    const source=$("#winchBatterySource");
    if(source){
      source.innerHTML='<b>Source from Winch:</b> Load '+f(c.load_kg,1)+' kg • Lift '+f(c.lift_m,2)+' m • '+
        'UP '+f(o.up_time_s,2)+' s • DOWN '+f(o.down_time_s,2)+' s • '+
        'Auto events '+o.lift_events+' งาน';
    }

    out.innerHTML=
      '<div class="system-result-head"><span class="system-chip neutral">WINCH MECHANICS</span><b>ไม่รวมการเลือกขนาดแบตเตอรี่ในหน้านี้</b></div>'+
      '<h3>Winch Datasheet / Load</h3><div class="metric-grid">'+
      '<div class="metric"><div class="k">First-layer speed</div><div class="v">'+f(c.up_speed_m_min,3)+' m/min</div></div>'+
      '<div class="metric"><div class="k">Current @ load</div><div class="v">'+f(c.up_current_a,2)+' A</div></div>'+
      '<div class="metric"><div class="k">เวลา UP</div><div class="v">'+f(c.up_time_s,2)+' s</div></div></div>'+
      '<p>Rope layer <b>'+c.layer+'</b> • Sheet line pull '+f(c.layer_line_pull_kg,0)+' kg • '+statusSpan(c.layer_pull_ok)+'</p>'+
      (c.first_layer_performance_warning?'<div class="notice"><b>Rope-layer warning:</b> '+c.first_layer_performance_warning+'</div>':'')+
      '<h3>Linear Interpolation — จากตาราง First Layer</h3>'+
      '<div class="formula"><b>ช่วงข้อมูลที่ใช้</b><br>'+
      f(c.interp_lower_load_kg,0)+' kg → '+f(c.interp_upper_load_kg,0)+' kg<br>'+
      'จุดล่าง: v₁ = '+f(c.interp_lower_speed_m_min,3)+' m/min, I₁ = '+f(c.interp_lower_current_a,2)+' A<br>'+
      'จุดบน: v₂ = '+f(c.interp_upper_speed_m_min,3)+' m/min, I₂ = '+f(c.interp_upper_current_a,2)+' A</div>'+
      '<div class="formula"><b>STEP 1 — r = (x − x₁) ÷ (x₂ − x₁)</b><br>'+
      '<b>สูตรภาษาไทย:</b> สัดส่วน = (โหลดที่ต้องการ − โหลดจุดล่าง) ÷ (โหลดจุดบน − โหลดจุดล่าง)<br>'+
      '<b>แทนค่า:</b> ('+f(c.load_kg,1)+' − '+f(c.interp_lower_load_kg,1)+') ÷ ('+f(c.interp_upper_load_kg,1)+' − '+f(c.interp_lower_load_kg,1)+') = <b>'+f(c.interp_alpha,6)+'</b> ('+f(c.interp_alpha*100,2)+'%)</div>'+
      '<div class="formula"><b>STEP 2 — v = v₁ + r(v₂ − v₁)</b><br>'+
      '<b>สูตรภาษาไทย:</b> ความเร็วสลิง = ความเร็วจุดล่าง + สัดส่วน × (ความเร็วจุดบน − ความเร็วจุดล่าง)<br>'+
      '<b>แทนค่า:</b> '+f(c.interp_lower_speed_m_min,3)+' + '+f(c.interp_alpha,6)+' × ('+f(c.interp_upper_speed_m_min,3)+' − '+f(c.interp_lower_speed_m_min,3)+') = <b>'+f(c.up_speed_m_min,3)+' m/min</b></div>'+
      '<div class="formula"><b>STEP 3 — I = I₁ + r(I₂ − I₁)</b><br>'+
      '<b>สูตรภาษาไทย:</b> กระแส = กระแสจุดล่าง + สัดส่วน × (กระแสจุดบน − กระแสจุดล่าง)<br>'+
      '<b>แทนค่า:</b> '+f(c.interp_lower_current_a,2)+' + '+f(c.interp_alpha,6)+' × ('+f(c.interp_upper_current_a,2)+' − '+f(c.interp_lower_current_a,2)+') = <b>'+f(c.up_current_a,2)+' A</b></div>'+
      '<div class="notice"><b>ใช้ต่อ:</b> ความเร็ว '+f(c.up_speed_m_min,3)+' m/min ใช้หาเวลา UP และกระแส '+f(c.up_current_a,2)+' A ใช้หา Wh ของ Winch Battery 12 V.</div>'+
      '<h3>Operating Cycles</h3><div class="metric-grid">'+
      '<div class="metric"><div class="k">รอบไป-กลับ</div><div class="v">'+o.completed_round_trips+'</div></div>'+
      '<div class="metric"><div class="k">เที่ยวทางเดียว</div><div class="v">'+o.one_way_trips+'</div></div>'+
      '<div class="metric"><div class="k">งานยกจากเวลาทำงาน</div><div class="v">'+o.lift_events+'</div></div></div>'+
      '<div class="formula"><b>t_event = t_up + t_down</b><br><b>สูตรภาษาไทย:</b> เวลา 1 งานยก = เวลาขึ้น + เวลาลง<br><b>แทนค่า:</b> '+f(o.up_time_s,2)+' + '+f(o.down_time_s,2)+' = <b>'+f(o.event_time_s,2)+' s</b></div>'+
      '<div class="formula"><b>Nround = floor(t_available ÷ t_round)</b><br><b>สูตรภาษาไทย:</b> จำนวนรอบที่ทำได้ครบ = ปัดลง(เวลาทำงานทั้งหมด ÷ เวลาต่อรอบ)<br><b>ผล:</b> '+o.completed_round_trips+' รอบ</div>'+
      '<div class="notice"><b>ต่อไป:</b> ถ้าต้องการหา Ah / Wh / BMS ของวินช์ ให้เปิดแท็บ <b>Winch Battery 12 V</b>. พลังงานส่วนนั้นแยกจาก Main Battery 72 V.</div>'+
      winchStepsHtml(r);
    if(interactive) buttonSuccess(btn,"คำนวณเสร็จ ✓","คำนวณ Winch / Operating Cycle เสร็จแล้ว");
  }catch(e){setError(out,e);if(interactive) buttonError(btn,"ไม่สำเร็จ","คำนวณ Winch ไม่สำเร็จ");}
});

function winchBatteryPayload(){
  return Object.assign({},formObject($("#winchForm")),formObject($("#winchBatteryForm")));
}

$("#calcWinchBattery").addEventListener("click",async(evt)=>{
  const btn=$("#calcWinchBattery"),interactive=!!evt.isTrusted;
  if(interactive) buttonBusy(btn,"กำลังคำนวณแบต 12 V...");
  const out=$("#winchBatteryResult");setLoading(out);
  try{
    const r=await api("/api/calc/winch",winchBatteryPayload()),c=r.core,o=r.operation,b=r.battery;
    lastWinchBatteryResult=r;
    const source=$("#winchBatterySource");
    if(source){
      source.innerHTML='<b>ใช้ค่าจากหน้า Winch:</b> Load '+f(c.load_kg,1)+' kg • Lift '+f(c.lift_m,2)+' m • '+
        'UP '+f(o.up_time_s,2)+' s • DOWN '+f(o.down_time_s,2)+' s • '+
        (b.event_mode==="Auto"?'Auto '+b.events+' งาน':'Manual '+b.events+' งาน');
    }

    out.innerHTML=
      '<div class="system-result-head separate-12v"><span class="system-chip orange">12 V WINCH ONLY</span>'+
      '<b>แบตชุดนี้ไม่รวมกับ Main Battery 72 V</b></div>'+
      '<h3>Winch Battery — '+b.event_mode+'</h3><div class="metric-grid">'+
      '<div class="metric"><div class="k">แรงดัน</div><div class="v">'+f(b.voltage_v,1)+' V</div></div>'+
      '<div class="metric"><div class="k">งานยกที่ใช้คำนวณ</div><div class="v">'+b.events+'</div></div>'+
      '<div class="metric"><div class="k">UP / DOWN</div><div class="v">'+b.up_count+' / '+b.down_count+'</div></div>'+
      '<div class="metric"><div class="k">E / งาน</div><div class="v">'+f(b.e_event_wh,3)+' Wh</div></div>'+
      '<div class="metric"><div class="k">E total</div><div class="v">'+f(b.e_total_wh,2)+' Wh</div></div>'+
      '<div class="metric"><div class="k">Ah design</div><div class="v">'+f(b.ah_design,2)+' Ah</div></div></div>'+
      '<div class="formula"><b>E_up = V × I_up × t_up ÷ 3600</b><br>'+
      '<b>สูตรภาษาไทย:</b> พลังงานยกขึ้น = แรงดันแบตวินช์ × กระแสตอนยก × เวลายก ÷ 3600<br>'+
      '<b>ผล:</b> '+f(b.e_up_wh,3)+' Wh</div>'+
      '<div class="formula"><b>E_down = V × I_down × t_down ÷ 3600</b><br>'+
      '<b>สูตรภาษาไทย:</b> พลังงานลดลง = แรงดันแบตวินช์ × กระแสตอนลด × เวลาลด ÷ 3600<br>'+
      '<b>ผล:</b> '+f(b.e_down_wh,3)+' Wh</div>'+
      '<div class="formula"><b>E_event = E_up + E_down</b><br>'+
      '<b>สูตรภาษาไทย:</b> พลังงานต่อ 1 งานยก = พลังงานยกขึ้น + พลังงานลดลง<br>'+
      '<b>แทนค่า:</b> '+f(b.e_up_wh,3)+' + '+f(b.e_down_wh,3)+' = <b>'+f(b.e_event_wh,3)+' Wh</b></div>'+
      '<div class="formula"><b>E_total = N_event × E_event</b><br>'+
      '<b>สูตรภาษาไทย:</b> พลังงานรวมของแบตวินช์ = จำนวนงานยก × พลังงานต่อ 1 งานยก<br>'+
      '<b>แทนค่า:</b> '+b.events+' × '+f(b.e_event_wh,3)+' = <b>'+f(b.e_total_wh,2)+' Wh</b></div>'+
      '<div class="formula"><b>Ah_design = E_total × (1 + Reserve) ÷ (V × DoD)</b><br>'+
      '<b>สูตรภาษาไทย:</b> ความจุแบตวินช์ที่ออกแบบ = พลังงานรวม × (1 + พลังงานสำรอง) ÷ (แรงดันแบตวินช์ × DoD)<br>'+
      '<b>ผล:</b> <b>'+f(b.ah_design,2)+' Ah</b> → Standard ≥ <b>'+f(b.standard_ah,0)+' Ah @ '+f(b.voltage_v,0)+' V</b></div>'+
      '<h3>Battery / BMS Check</h3>'+
      '<table><tr><th>รายการ</th><th>Required</th><th>Candidate</th><th>Status</th></tr>'+
      '<tr><td>Capacity</td><td>≥ '+f(b.ah_design,2)+' Ah</td><td>'+f(b.candidate_ah,1)+' Ah</td><td>'+statusSpan(b.candidate_energy_ok)+'</td></tr>'+
      '<tr><td>BMS Continuous</td><td>≥ '+f(b.operating_current_a,1)+' A</td><td>'+f(b.bms_cont_a,1)+' A</td><td>'+(b.bms_cont_a>0?statusSpan(b.bms_cont_ok):'<span class="check">CHECK</span>')+'</td></tr>'+
      '<tr><td>BMS Peak</td><td>Datasheet ไม่มี Starting/Stall surge</td><td>'+f(b.bms_peak_a,1)+' A</td><td><span class="check">CHECK DATASHEET</span></td></tr></table>'+
      '<div class="battery-separation-note result-separation"><b>ย้ำการแยกระบบ:</b>'+
      '<span>12 V Winch Battery: '+f(b.e_total_wh,2)+' Wh / '+f(b.ah_design,2)+' Ah design</span>'+
      '<span>72 V Main Battery: คำนวณอีกหน้า และไม่บวก Wh/Ah ชุดนี้เข้าไป</span>'+
      '<span>แชร์เฉพาะเวลา UP/DOWN เพื่อให้ Main Battery นับจำนวน Operating Cycle ได้สมจริง</span></div>'+
      winchBatteryStepsHtml(r);
    syncVehicleParameters();
    if(interactive) buttonSuccess(btn,"คำนวณเสร็จ ✓","คำนวณ Winch Battery 12 V เสร็จแล้ว");
  }catch(e){setError(out,e);if(interactive) buttonError(btn,"ไม่สำเร็จ","คำนวณ Winch Battery 12 V ไม่สำเร็จ");}
});


let lastStabilityResult=null;

function fbdSf(v){return Number(v)>=999?'∞':f(v,3);}
function fbdCaseSf(bal){
  if(!bal)return '—';
  if(Number(bal.overturning_moment_nm)<=1e-9)return 'N/A (M_O=0)';
  return fbdSf(bal.sf);
}
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

function stabilityVariableTableHtml(r){
  const rows=[
    ["m_total","มวลรวมทั้งระบบ",f(r.total_mass_kg,2),"kg",r.mass_mode==="components"?"Derived: Σm_i":"Input: Total Mass"],
    ["m_V","มวลรถฐาน",f(r.base_vehicle_mass_kg,2),"kg",r.mass_mode==="components"?"Derived: Base components":"Derived: m_total - m_L - m_B"],
    ["m_L","มวล Basket + Payload",f(r.payload_mass_kg,2),"kg",r.mass_mode==="components"?"Derived: Basket + Payload":"Input: Payload"],
    ["m_B","มวล Boom",f(r.boom_mass_kg,2),"kg",r.mass_mode==="components"?"Derived: Boom group":"Input: Boom"],
    ["W","Track width ศูนย์กลางล้อซ้าย-ขวา",f(r.track_width_m,3),"m","Input: Stability"],
    ["WB","Wheelbase ศูนย์กลางเพลาหน้า-หลัง",f(r.wheelbase_m,3),"m","Input: Stability"],
    ["L","ความยาวแขนเครนถึงโหลด",f(r.boom_length_m,3),"m","Input: Stability"],
    ["θ","มุมหมุนเครนปัจจุบัน",f(r.crane_angle_deg,2),"deg","Input: Stability"],
    ["Kdyn","Dynamic factor ของ Payload",f(r.dynamic_factor,2),"-","Input: Stability"],
    ["SF_req","Safety Factor ที่ต้องการ",f(r.required_sf,2),"-","Input: Stability"],
    ["x_CG,V","Base vehicle CG ตามแนวยาว",f(r.vehicle_cg_x_m,3),"m",r.mass_mode==="components"?"Derived: weighted CG":"Input: Stability"],
    ["y_CG,V","Base vehicle CG ตามแนวขวาง",f(r.vehicle_cg_y_m,3),"m",r.mass_mode==="components"?"Derived: weighted CG":"Input: Stability"],
    ["α","มุมทางลาด",f(r.slope.slope_deg,2),"deg","Input / Ramp Geometry"],
    ["a","ความเร่งขึ้นทางลาด",f(r.slope.accel_mps2,3),"m/s²","Input: Stability"],
    ["d_R","Combined CG จากเพลาหลัง",f(r.slope.combined_cg_from_rear_m,3),"m",r.mass_mode==="components"?"Derived: Combined CG":"Input: Stability"],
    ["h_CG","ความสูง Combined CG",f(r.slope.combined_cg_height_m,3),"m",r.mass_mode==="components"?"Derived: weighted CG z":"Input: Stability"],
    ["g","ความเร่งโน้มถ่วง","9.81","m/s²","Constant"],
    ["M_O","โมเมนต์คว่ำ","ตาม Case","N·m","Calculated"],
    ["M_R","โมเมนต์ต้าน","ตาม Case","N·m","Calculated"],
    ["SF","Safety Factor = M_R / M_O","ตาม Case","-","Calculated"]
  ];
  return '<div class="stability-unit-block">'+
    '<div class="unit-convention"><b>Unit Convention / มาตรฐานหน่วย:</b> Mass = kg • Distance = m • Force = N • Moment = N·m • Angle = deg • Acceleration = m/s² • Safety Factor = ไม่มีหน่วย</div>'+
    '<div class="variable-table-head"><h4>ตารางตัวแปรที่ใช้คำนวณ</h4><span>'+r.mass_mode_label+'</span></div>'+
    '<div class="variable-table-wrap"><table class="stability-variable-table">'+
    '<tr><th>ตัวแปร</th><th>ความหมาย</th><th>ค่า</th><th>หน่วย</th><th>แหล่งที่มา</th></tr>'+
    rows.map(x=>'<tr><td><b>'+x[0]+'</b></td><td>'+x[1]+'</td><td class="num-cell">'+x[2]+'</td><td class="unit-cell">'+x[3]+'</td><td>'+x[4]+'</td></tr>').join('')+
    '</table></div></div>';
}

function fbdFormulaHtml(key,bal,r){
  const flow='<div class="calc-flow-strip">'+
    '<span><b>1</b> แรง + ระยะ</span><i>→</i>'+
    '<span><b>2</b> M_O</span><i>→</i>'+
    '<span><b>3</b> M_R</span><i>→</i>'+
    '<span><b>4</b> Safety Factor</span></div>';

  if(key==="slope"){
    return '<div class="formula-human step-formula">'+
      '<h4>ขั้นตอนการคำนวณ — '+fbdName(key)+'</h4>'+flow+
      '<section class="calc-step-card"><div class="calc-step-no">1</div><div><h5>หาแรงที่กระทำบนทางลาด</h5>'+
      '<p><b>W_parallel = mg sinα</b><br>แทนค่า: '+f(r.total_mass_kg,2)+' × 9.81 × sin('+f(bal.slope_deg,2)+'°) = <b>'+f(bal.w_parallel_n,2)+' N</b></p>'+
      '<p><b>W_normal = mg cosα</b> = <b>'+f(bal.w_normal_n,2)+' N</b><br>'+
      '<b>F_I = ma</b> = '+f(r.total_mass_kg,2)+' × '+f(bal.accel_mps2,3)+' = <b>'+f(bal.inertia_n,2)+' N</b></p></div></section>'+
      '<section class="calc-step-card"><div class="calc-step-no">2</div><div><h5>กำหนดแขนโมเมนต์รอบแกนคว่ำหลัง P</h5>'+
      '<p>ระยะ CG ถึงแกนหลัง <b>d_R = '+f(bal.combined_cg_from_rear_m,3)+' m</b><br>'+
      'ความสูง CG <b>h_CG = '+f(bal.combined_cg_height_m,3)+' m</b></p></div></section>'+
      '<section class="calc-step-card"><div class="calc-step-no">3</div><div><h5>หาโมเมนต์คว่ำและโมเมนต์ต้าน</h5>'+
      '<p><b>M_O = (W_parallel + F_I)h_CG</b><br>('+f(bal.w_parallel_n,2)+' + '+f(bal.inertia_n,2)+') × '+f(bal.combined_cg_height_m,3)+' = <b>'+f(bal.overturning_moment_nm,2)+' N·m</b></p>'+
      '<p><b>M_R = W_normal d_R</b><br>'+f(bal.w_normal_n,2)+' × '+f(bal.combined_cg_from_rear_m,3)+' = <b>'+f(bal.resisting_moment_nm,2)+' N·m</b></p></div></section>'+
      '<section class="calc-step-card final-step"><div class="calc-step-no">4</div><div><h5>หา Safety Factor และตัดสินผล</h5>'+
      '<p><b>SF = M_R ÷ M_O</b> = '+f(bal.resisting_moment_nm,2)+' N·m ÷ '+f(bal.overturning_moment_nm,2)+' N·m = <b>'+fbdSf(bal.sf)+'</b> <span class="unit-note">(ไม่มีหน่วย)</span> &nbsp; '+statusSpan(bal.pass)+'</p>'+
      '<p class="step-meaning">เกณฑ์ของโปรเจกต์: SF ≥ '+f(r.required_sf,2)+'</p></div></section></div>';
  }

  const comps=bal.components||[];
  const mo=comps.filter(q=>q.role==="overturning");
  const mr=comps.filter(q=>q.role==="resisting");
  const term=(q)=>'('+f(q.force_n,2)+' × '+f(q.arm_m,3)+')';
  const posKey=(key==="side_left"||key==="side_right")?"y_m":"x_m";
  const forceRows=comps.map(q=>'<tr><td>'+fbdThaiComponent(q.name)+'</td><td>'+f(q.force_n,2)+' N</td><td>'+f(q[posKey],3)+' m</td><td>'+f(q.arm_m,3)+' m</td><td>'+fbdRoleThai(q.role)+'</td></tr>').join('');
  const details=(arr)=>arr.length?arr.map(q=>'• '+fbdThaiComponent(q.name)+': '+f(q.force_n,2)+' N × '+f(q.arm_m,3)+' m = <b>'+f(q.moment_nm,2)+' N·m</b>').join('<br>'):'• ไม่มีแรงในฝั่งนี้';
  return '<div class="formula-human step-formula">'+
    '<h4>ขั้นตอนการคำนวณ — '+fbdName(key)+'</h4>'+flow+
    '<section class="calc-step-card"><div class="calc-step-no">1</div><div><h5>หาแรงและระยะแขนโมเมนต์จากแกนคว่ำ P</h5>'+
    '<p class="step-meaning">ก่อนคิดโมเมนต์ ให้ดูว่าแต่ละแรงอยู่ฝั่ง “ทำให้คว่ำ” หรือ “ต้านการคว่ำ” แล้ววัดระยะตั้งฉากถึงแกน P</p>'+
    '<div class="step-table-wrap"><table><tr><th>ส่วน</th><th>แรง F (N)</th><th>ตำแหน่ง (m)</th><th>แขน d (m)</th><th>หน้าที่</th></tr>'+forceRows+'</table></div></div></section>'+
    '<section class="calc-step-card"><div class="calc-step-no">2</div><div><h5>หาโมเมนต์คว่ำ M_O</h5>'+
    '<p><b>สูตร:</b> M_O = Σ(F_i d_i)<br><b>อ่านง่าย:</b> รวม “แรง × แขนโมเมนต์” เฉพาะแรงที่พยายามทำให้รถคว่ำ</p>'+
    '<p>'+details(mo)+'<br><b>แทนค่า:</b> M_O = '+(mo.length?mo.map(term).join(' + '):'0')+' = <b>'+f(bal.overturning_moment_nm,2)+' N·m</b></p></div></section>'+
    '<section class="calc-step-card"><div class="calc-step-no">3</div><div><h5>หาโมเมนต์ต้าน M_R</h5>'+
    '<p><b>สูตร:</b> M_R = Σ(F_i d_i)<br><b>อ่านง่าย:</b> รวม “แรง × แขนโมเมนต์” ของแรงที่ช่วยพยุงรถไม่ให้คว่ำ</p>'+
    '<p>'+details(mr)+'<br><b>แทนค่า:</b> M_R = '+(mr.length?mr.map(term).join(' + '):'0')+' = <b>'+f(bal.resisting_moment_nm,2)+' N·m</b></p></div></section>'+
    '<section class="calc-step-card final-step"><div class="calc-step-no">4</div><div><h5>หา Safety Factor และตัดสินผล</h5>'+
    '<p><b>สูตร:</b> SF = M_R ÷ M_O<br><b>แทนค่า:</b> '+(bal.overturning_moment_nm>1e-9?f(bal.resisting_moment_nm,2)+' N·m ÷ '+f(bal.overturning_moment_nm,2)+' N·m = <b>'+fbdSf(bal.sf)+'</b> <span class="unit-note">(ไม่มีหน่วย)</span>':'ไม่มีแรงอยู่เลยแกน P ไปทางคว่ำใน Case/มุมนี้ → <b>M_O = 0</b> ดังนั้น <b>SF = N/A</b> (ไม่ใช้ ∞ เป็นค่าความปลอดภัยจริง)')+
    ' &nbsp; '+statusSpan(bal.pass)+'</p><p class="step-meaning">เกณฑ์ของโปรเจกต์: SF ≥ '+f(r.required_sf,2)+'</p></div></section></div>';
}

function renderWebFbd(){
  if(!lastStabilityResult)return;
  const key=$("#webFbdCase").value,view=$("#webFbdView").value;
  const source=view==="critical"?lastStabilityResult.critical_cases:lastStabilityResult.current_cases;
  const bal=source[key];
  if(!bal)return;
  const angle=key==="slope"
    ? 'α='+f(bal.slope_deg,2)+'°'
    : (bal.angle_deg===null||bal.angle_deg===undefined?'θ = N/A':'θ='+f(bal.angle_deg,1)+'°');
  let context='<b>'+(view==="critical"?'CRITICAL CASE':'CURRENT ANGLE')+'</b> • '+fbdName(key)+' • '+angle+' • SF '+fbdCaseSf(bal)+' • '+statusSpan(bal.pass);
  if(key!=="slope" && Number(bal.overturning_moment_nm)<=1e-9){
    context += view==="critical"
      ? ' • <b>ไม่พบโมเมนต์คว่ำในทิศนี้ภายในช่วงเครน -90°…+90°</b>'
      : ' • <b>มุมปัจจุบันยังไม่คว่ำด้านนี้ — เลือก Critical Case เพื่อดูมุมวิกฤตของด้านนี้</b>';
  }
  $("#webFbdContext").innerHTML=context;
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
    const r=await api("/api/calc/stability",stabilityPayload());
    lastStabilityResult=r;
    if(r.mass_mode==="components"){
      const form=$("#stabilityForm");
      if(form?.elements.total_mass_kg) form.elements.total_mass_kg.value=Number(r.total_mass_kg).toFixed(3);
      if(form?.elements.payload_mass_kg) form.elements.payload_mass_kg.value=Number(r.payload_mass_kg).toFixed(3);
      if(form?.elements.boom_mass_kg) form.elements.boom_mass_kg.value=Number(r.boom_mass_kg).toFixed(3);
      if(form?.elements.vehicle_cg_x_from_center_m) form.elements.vehicle_cg_x_from_center_m.value=Number(r.vehicle_cg_x_m).toFixed(4);
      if(form?.elements.vehicle_cg_y_m) form.elements.vehicle_cg_y_m.value=Number(r.vehicle_cg_y_m).toFixed(4);
      if(form?.elements.combined_cg_from_rear_m) form.elements.combined_cg_from_rear_m.value=Number(r.slope.combined_cg_from_rear_m).toFixed(4);
      if(form?.elements.combined_cg_height_m) form.elements.combined_cg_height_m.value=Number(r.slope.combined_cg_height_m).toFixed(4);
      syncSharedProjectParameter("mass_kg",r.total_mass_kg,form?.elements.total_mass_kg);
      saveWebInputs();syncVehicleParameters();
    }
    const cg=r.current_governing,crit=r.critical_governing;
    const cgSf=fbdSf(cg.sf),critSf=fbdSf(crit.sf);
    const massSource=r.mass_mode==="components"
      ? '<div class="mass-source-card"><b>MODE B — COMPONENT MASS</b><br>Σm = '+f(r.total_mass_kg,2)+' kg • Base '+f(r.base_vehicle_mass_kg,2)+' kg • Boom '+f(r.boom_mass_kg,2)+' kg • Basket+Payload '+f(r.payload_mass_kg,2)+' kg<br>Base CG x/y = '+f(r.vehicle_cg_x_m,3)+' / '+f(r.vehicle_cg_y_m,3)+' m • Combined h_CG = '+f(r.slope.combined_cg_height_m,3)+' m</div>'
      : '<div class="mass-source-card"><b>MODE A — TOTAL MASS</b><br>ใช้ m_total, Payload, Boom และ CG ที่กรอกเองโดยตรง</div>';
    out.innerHTML=
      '<h3>Stability Result</h3>'+massSource+
      stabilityVariableTableHtml(r)+
      '<div class="notice"><b>Inputs used:</b> m_total '+f(r.total_mass_kg,1)+' kg • Payload '+f(r.payload_mass_kg,1)+' kg • Boom '+f(r.boom_mass_kg,1)+' kg • Track '+f(r.track_width_m,3)+' m • WB '+f(r.wheelbase_m,3)+' m • θ '+f(r.crane_angle_deg,1)+' deg</div>'+
      '<div class="metric-grid">'+
      '<div class="metric"><div class="k">Current Governing SF</div><div class="v">'+cgSf+' <small class="metric-unit">-</small></div><div>'+fbdName(cg.key)+' • '+statusSpan(cg.pass)+'</div></div>'+
      '<div class="metric"><div class="k">Critical Worst SF</div><div class="v">'+critSf+' <small class="metric-unit">-</small></div><div>'+fbdName(crit.key)+' • '+statusSpan(crit.pass)+'</div></div>'+
      '<div class="metric"><div class="k">Required SF</div><div class="v">'+f(r.required_sf,2)+' <small class="metric-unit">-</small></div><div>ไม่มีหน่วย • เกณฑ์ออกแบบ</div></div></div>'+
      '<h3>Current Angle '+f(r.crane_angle_deg,1)+'°</h3>'+
      '<table><tr><th>Case</th><th>SF</th><th>Status</th></tr>'+
      ['side_left','side_right','front','rear','slope'].map(k=>'<tr><td>'+fbdName(k)+'</td><td>'+fbdCaseSf(r.current_cases[k])+'</td><td>'+statusSpan(r.current_cases[k].pass)+'</td></tr>').join('')+
      '</table>'+
      '<div class="notice"><b>Slope แยกจาก Crane Worst Case:</b> SF_slope = '+fbdSf(r.slope.sf)+' • '+statusSpan(r.slope.pass)+'</div>'+
      '<div class="notice"><b>STEP-BY-STEP ทุก Stability Mode:</b> เลือก Side Left / Side Right / Front / Rear / Slope และ Current/Critical ด้านล่าง ระบบจะแสดง STEP ของ Case นั้นพร้อมแทนค่าจริง</div>'+
      '<p class="check">เลือก Case และ Current/Critical ด้านล่างเพื่อดู FBD, Moment arm และสูตรแทนค่าจริง</p>';
    renderWebFbd();
    if(interactive) buttonSuccess(btn,"คำนวณเสร็จ ✓","คำนวณ Stability + FBD เสร็จแล้ว");
  }catch(e){setError(out,e);if(interactive) buttonError(btn,"ไม่สำเร็จ","คำนวณ Stability + FBD เสร็จแล้ว ไม่สำเร็จ");}
});


const CVET_WEB_LOCK_STORE="cvet_web_design_lock_v1";
const CVET_WEB_REV_A="cvet_web_revision_a_v1";
const CVET_WEB_REV_B="cvet_web_revision_b_v1";

function webDesignLockElements(){
  const specs=[
    ["driveForm",["mass_kg","wheel_diameter_in","slope_deg"]],
    ["rampForm",["rise_cm","run_cm","measured_slant_cm","mass_kg"]],
    ["batteryForm",["mass_kg","slope_deg","track_width_m"]],
    ["winchForm",["load_kg","lift_m"]],
    ["stabilityForm",["total_mass_kg","payload_mass_kg","boom_mass_kg","track_width_m","wheelbase_m","boom_length_m","crane_from_rear_m","vehicle_cg_x_from_center_m","vehicle_cg_y_m","combined_cg_from_rear_m","combined_cg_height_m","slope_deg","slope_accel_mps2"]]
  ];
  const out=[];
  specs.forEach(([formId,names])=>{
    const form=$("#"+formId); if(!form)return;
    names.forEach(name=>{const el=form.elements[name];if(el&&el.tagName)out.push(el);});
  });
  return [...new Set(out)];
}

function applyWebDesignLock(locked,save=true){
  webDesignLockElements().forEach(el=>{
    el.classList.toggle("design-input-locked",!!locked);
    if(locked){
      if(el.dataset.cvetTabindex===undefined)el.dataset.cvetTabindex=el.getAttribute("tabindex")??"";
      el.setAttribute("tabindex","-1");
      el.setAttribute("aria-readonly","true");
    }else{
      const old=el.dataset.cvetTabindex;
      if(old===undefined||old==="")el.removeAttribute("tabindex");else el.setAttribute("tabindex",old);
      delete el.dataset.cvetTabindex;el.removeAttribute("aria-readonly");
    }
  });
  const btn=$("#webDesignLock"),status=$("#webDesignLockStatus");
  if(btn)btn.textContent=locked?"🔒 Design Inputs Locked":"🔓 Design Inputs Unlocked";
  if(status)status.textContent=locked?"FINAL LOCK: ปลดล็อกก่อนแก้ W, WB, L, x_C, Mass, CG, Slope":"ค่าหลักยังแก้ไขได้";
  if(save){try{localStorage.setItem(CVET_WEB_LOCK_STORE,locked?"1":"0");}catch(e){}}
}

async function calculateWebDecisionSnapshot(){
  const drive=await api("/api/calc/drive-torque",formObject($("#driveForm")));
  const winch=await api("/api/calc/winch",winchBatteryPayload());
  const bp=formObject($("#batteryForm"));
  bp.drive_reference_current_a=drive.battery_current_a;
  if(winch?.operation){
    bp.lift_time_per_event_s=winch.operation.event_time_s;
    bp.lift_events_per_round=winch.operation.events_per_round;
    bp.other_stop_time_per_round_s=winch.operation.other_stop_s;
  }
  const battery=await api("/api/calc/drive-battery",bp);
  const stability=await api("/api/calc/stability",stabilityPayload());
  const ramp=await api("/api/calc/ramp-geometry",formObject($("#rampForm")));
  return {drive,winch,battery,stability,ramp};
}

function sfDecisionText(bal){
  if(!bal)return "—";
  if(Number(bal.overturning_moment_nm)<=1e-9)return "N/A (M_O=0)";
  return f(bal.sf,3);
}
function passDecision(bal,req){return !bal||Number(bal.overturning_moment_nm)<=1e-9||Number(bal.sf)>=Number(req);}

function webSummaryMetrics(x){
  const s=x.stability,req=s.required_sf||1.5,c=s.critical_cases||{},wb=x.winch?.battery||{};
  const cases=["side_left","side_right","front","rear"].map(k=>({key:k,bal:c[k]}));
  const valid=cases.filter(q=>q.bal&&Number(q.bal.overturning_moment_nm)>1e-9);
  valid.sort((a,b)=>Number(a.bal.sf)-Number(b.bal.sf));
  const gov=valid[0];
  const slopeSf=Number(s.slope?.sf??999);
  const overall=(gov && Number(gov.bal.sf)<=slopeSf)
    ? {name:fbdName(gov.key),sf:Number(gov.bal.sf)}
    : {name:"Slope",sf:slopeSf};
  return {
    "Torque required / motor (N·m)":x.drive.torque_per_motor_nm,
    "Motor power margin (×)":x.drive.motor_power_margin,
    "Main battery minimum (Ah)":x.battery.design_ah,
    "Main battery practical (Ah)":x.battery.recommended_ah,
    "Winch battery design (Ah)":wb.ah_design??0,
    "Side Left critical SF":c.side_left?.sf??999,
    "Side Right critical SF":c.side_right?.sf??999,
    "Front critical SF":c.front?.sf??999,
    "Rear critical SF":c.rear?.overturning_moment_nm>1e-9?c.rear.sf:"N/A",
    "Slope SF":s.slope?.sf??999,
    "Governing lifting case":gov?fbdName(gov.key):"No overturning case",
    "Governing lifting SF":gov?gov.bal.sf:"N/A",
    "Overall governing stability":overall.name,
    "Overall governing SF":overall.sf
  };
}

async function refreshEngineeringDecisionSummary(){
  const out=$("#engineeringWorstSummary"),btn=$("#refreshEngineeringSummary");
  if(!out)return;
  buttonBusy(btn,"กำลังสรุป...");
  try{
    const x=await calculateWebDecisionSnapshot();
    lastDriveResult=x.drive;lastBatteryResult=x.battery;lastWinchBatteryResult=x.winch;lastStabilityResult=x.stability;lastRampResult=x.ramp;
    const s=x.stability,c=s.critical_cases||{},req=s.required_sf||1.5;
    const rows=[];
    const add=(sys,item,value,ok,detail)=>rows.push('<tr><td>'+sys+'</td><td>'+item+'</td><td><b>'+value+'</b></td><td>'+statusSpan(ok)+'</td><td>'+detail+'</td></tr>');
    add("Drive","Torque / motor",f(x.drive.torque_per_motor_nm,2)+" N·m",true,"Design requirement");
    add("Drive","Motor rated power",f(x.drive.motor_rated_w,0)+" W",!!x.drive.motor_power_ok,"required "+f(x.drive.design_mech_power_per_motor_w,1)+" W • margin "+f(x.drive.motor_power_margin,2)+"×");
    add("Drive","Traction margin",f(x.drive.traction_margin,2)+"×",Number(x.drive.traction_margin)>=1,"≥ 1.00");
    add("Battery","Main battery minimum",f(x.battery.design_ah,2)+" Ah",true,"practical "+f(x.battery.recommended_ah,2)+" Ah");
    add("Battery","72 V load energy",f(x.battery.load_energy_wh,1)+" Wh",true,x.battery.completed_round_trips+" full Cycle");
    add("Winch","12 V battery design",f(x.winch.battery.ah_design,2)+" Ah",true,x.winch.battery.events+" jobs");
    ["side_left","side_right","front","rear"].forEach(k=>{
      const b=c[k],ok=passDecision(b,req);
      const detail=Number(b?.overturning_moment_nm)<=1e-9?"No overturning within permitted range":"θ="+f(b.angle_deg,0)+"° • M_O="+f(b.overturning_moment_nm,2)+" • M_R="+f(b.resisting_moment_nm,2)+" N·m";
      add("Stability",fbdName(k),sfDecisionText(b),ok,detail);
    });
    add("Stability","Slope SF",f(s.slope.sf,3),Number(s.slope.sf)>=req,"Required SF ≥ "+f(req,2));
    const valid=["side_left","side_right","front","rear"].map(k=>({key:k,b:c[k]})).filter(q=>q.b&&Number(q.b.overturning_moment_nm)>1e-9).sort((a,b)=>Number(a.b.sf)-Number(b.b.sf));
    const gov=valid[0];
    const slopeSf=Number(s.slope?.sf??999);
    const overall=(gov && Number(gov.b.sf)<=slopeSf)
      ? {name:fbdName(gov.key),sf:Number(gov.b.sf),detail:' @ '+f(gov.b.angle_deg,0)+'°'}
      : {name:'Slope',sf:slopeSf,detail:''};
    out.innerHTML='<h3>Engineering Worst-Case Summary</h3>'+
      '<div class="notice"><b>Overall governing stability:</b> '+overall.name+' • SF '+f(overall.sf,3)+overall.detail+
      '<br><b>Governing lifting case:</b> '+(gov?fbdName(gov.key)+' • SF '+f(gov.b.sf,3)+' @ '+f(gov.b.angle_deg,0)+'°':'No overturning case')+'</div>'+
      '<div style="overflow:auto"><table><tr><th>System</th><th>Check</th><th>Result</th><th>Status</th><th>Detail</th></tr>'+rows.join("")+'</table></div>';
    buttonSuccess(btn,"Summary ✓","สรุป Worst Case แล้ว");
    return x;
  }catch(e){setError(out,e);buttonError(btn,"ไม่สำเร็จ","สรุปผลไม่สำเร็จ");return null;}
}

async function runWebSensitivity(){
  const out=$("#webSensitivityResult"),btn=$("#runWebSensitivity");
  if(!out)return;
  buttonBusy(btn,"กำลังวิเคราะห์...");
  try{
    const span=Math.max(.05,Math.min(.50,num($("#webSensitivitySpan")?.value,20)/100));
    const base=stabilityPayload();
    const baseRes=await api("/api/calc/stability",base);
    const equivalent=Object.assign({},base,{
      mass_mode:"total",
      total_mass_kg:baseRes.total_mass_kg,
      payload_mass_kg:baseRes.payload_mass_kg,
      boom_mass_kg:baseRes.boom_mass_kg,
      vehicle_cg_x_from_center_m:baseRes.vehicle_cg_x_m,
      vehicle_cg_y_m:baseRes.vehicle_cg_y_m,
      combined_cg_from_rear_m:baseRes.slope.combined_cg_from_rear_m,
      combined_cg_height_m:baseRes.slope.combined_cg_height_m
    });
    delete equivalent.components;
    const specs=[
      ["Track width W","track_width_m","m"],
      ["Boom length L","boom_length_m","m"],
      ["Payload mass","payload_mass_kg","kg"],
      ["Crane x_C from rear axle","crane_from_rear_m","m"],
      ["Vehicle CG x","vehicle_cg_x_from_center_m","m"]
    ];
    let html='<h3>Sensitivity / What-if ±'+f(span*100,0)+'%</h3><p class="check">ทุกจุดใช้ Critical scan -90°…+90°. Component mode ใช้ equivalent mass/CG snapshot เพื่อไม่แก้ Component table จริง</p>';
    for(const [label,key,unit] of specs){
      const cur=num(equivalent[key],0),baseScale=Math.max(Math.abs(cur),key==="vehicle_cg_x_from_center_m"?.10:.05);
      const values=Math.abs(cur)<1e-12
        ? [-baseScale*span,-baseScale*span/2,0,baseScale*span/2,baseScale*span]
        : [1-span,1-span/2,1,1+span/2,1+span].map(q=>cur*q);
      const results=await Promise.all(values.map(async value=>{
        const p=Object.assign({},equivalent,{[key]:value});
        const r=await api("/api/calc/stability",p);
        return {value,r};
      }));
      html+='<h4>'+label+'</h4><div style="overflow:auto"><table><tr><th>Value</th><th>Governing</th><th>Worst SF</th><th>Status</th></tr>'+
        results.map(({value,r})=>'<tr><td>'+f(value,3)+' '+unit+'</td><td>'+fbdName(r.critical_governing.key)+'</td><td>'+f(r.critical_governing.sf,3)+'</td><td>'+statusSpan(r.critical_governing.pass)+'</td></tr>').join("")+
        '</table></div>';
    }
    out.innerHTML=html;buttonSuccess(btn,"Sensitivity ✓","Sensitivity เสร็จแล้ว");
  }catch(e){setError(out,e);buttonError(btn,"ไม่สำเร็จ","Sensitivity ไม่สำเร็จ");}
}

async function refreshWebCalculationTrace(){
  const out=$("#webTraceResult"),btn=$("#refreshWebTrace"),mode=$("#webTraceMode")?.value||"ALL";
  if(!out)return;
  buttonBusy(btn,"กำลังหาที่มาของคำตอบ...");
  try{
    const x=await calculateWebDecisionSnapshot(),blocks=[];
    if(mode==="ALL"||mode==="Drive Torque")blocks.push('<h3>แรงขับและทอร์ค — ค่าที่ใช้ → สูตร → แทนค่า → คำตอบ</h3>'+driveStepsHtml(x.drive));
    if(mode==="ALL"||mode==="Ramp Geometry")blocks.push('<h3>ทางลาด — ค่าที่ใช้ → สูตร → แทนค่า → คำตอบ</h3>'+rampStepsHtml(x.ramp));
    if(mode==="ALL"||mode==="Main Battery")blocks.push('<h3>แบตเตอรี่หลัก 72 V — ค่าที่ใช้ → สูตร → แทนค่า → คำตอบ</h3>'+batteryStepsHtml(x.battery,x.battery.candidate||{}));
    if(mode==="ALL"||mode==="Winch")blocks.push('<h3>วินช์ 12 V — ค่าที่ใช้ → สูตร → แทนค่า → คำตอบ</h3>'+winchStepsHtml(x.winch)+winchBatteryStepsHtml(x.winch));
    if(mode==="ALL"||mode==="Stability"){
      const key=x.stability.critical_governing.key;
      blocks.push('<h3>การคว่ำ / Stability — โมเมนต์คว่ำ → โมเมนต์ต้าน → SF → PASS/FAIL</h3>'+fbdFormulaHtml(key,x.stability.critical_cases[key],x.stability));
    }
    out.innerHTML=
      '<div class="notice"><b>ดูที่มาของคำตอบ:</b> หน้านี้ไม่ได้คำนวณด้วยสูตรใหม่ แต่เปิดขั้นตอนของผลลัพธ์เดิมให้ดู<br>'+
      '<b>อ่านตามนี้:</b> 1) ค่าที่ใช้ → 2) สูตร → 3) แทนค่าจริง → 4) คำตอบ → 5) ตรวจสอบ</div>'+
      blocks.join("");
    buttonSuccess(btn,"แสดงแล้ว ✓","แสดงที่มาของคำตอบแล้ว");
  }catch(e){setError(out,e);buttonError(btn,"ไม่สำเร็จ","แสดงที่มาของคำตอบไม่สำเร็จ");}
}

function webRevisionInputs(){
  const o={};
  ["driveForm","rampForm","batteryForm","winchForm","winchBatteryForm","stabilityForm"].forEach(id=>{o[id]=formObject($("#"+id));});
  o.stabilityComponents=stabilityComponentRows();
  return o;
}
async function captureWebRevision(slot){
  const key=slot==="A"?CVET_WEB_REV_A:CVET_WEB_REV_B;
  const label=$("#webRevision"+slot+"Label")?.value||("Design "+slot);
  const snapshot=await calculateWebDecisionSnapshot();
  const data={label,created:new Date().toISOString(),inputs:webRevisionInputs(),metrics:webSummaryMetrics(snapshot)};
  localStorage.setItem(key,JSON.stringify(data));
  $("#webRevisionResult").innerHTML='<div class="notice"><b>Captured '+label+'</b> • '+data.created.replace("T"," ").slice(0,19)+'</div>';
}
function flattenRevisionInputs(inputs){
  const out={};
  Object.entries(inputs||{}).forEach(([section,data])=>{
    if(section==="stabilityComponents"){
      (data||[]).forEach((row,i)=>{
        Object.entries(row||{}).forEach(([k,v])=>{out["Component "+(i+1)+" / "+k]=v;});
      });
      return;
    }
    Object.entries(data||{}).forEach(([k,v])=>{out[section+" / "+k]=v;});
  });
  return out;
}
function compareWebRevisionData(){
  const out=$("#webRevisionResult");
  let a,b;
  try{a=JSON.parse(localStorage.getItem(CVET_WEB_REV_A)||"null");b=JSON.parse(localStorage.getItem(CVET_WEB_REV_B)||"null");}catch(e){}
  if(!a||!b){out.innerHTML='<p class="check">Capture A และ B ก่อน</p>';return;}
  const ai=flattenRevisionInputs(a.inputs),bi=flattenRevisionInputs(b.inputs);
  const inputKeys=[...new Set([...Object.keys(ai),...Object.keys(bi)])];
  const inputRows=inputKeys.filter(k=>String(ai[k])!==String(bi[k])).map(k=>{
    const av=ai[k]??"—",bv=bi[k]??"—";
    const delta=(typeof av==="number"&&typeof bv==="number")?(bv-av):null;
    return '<tr><td>'+k+'</td><td>'+av+'</td><td>'+bv+'</td><td>'+(delta===null?"CHANGED":(delta>=0?"+":"")+f(delta,3))+'</td></tr>';
  }).join("");
  const keys=[...new Set([...Object.keys(a.metrics||{}),...Object.keys(b.metrics||{})])];
  const rows=keys.map(k=>{
    const av=a.metrics[k],bv=b.metrics[k];
    const delta=(typeof av==="number"&&typeof bv==="number")?(bv-av):null;
    return '<tr><td>'+k+'</td><td>'+((typeof av==="number")?f(av,3):av)+'</td><td>'+((typeof bv==="number")?f(bv,3):bv)+'</td><td>'+(delta===null?"—":(delta>=0?"+":"")+f(delta,3))+'</td></tr>';
  }).join("");
  out.innerHTML='<h3>'+a.label+' ↔ '+b.label+'</h3>'+
    '<h4>Input Revision Diff</h4>'+
    (inputRows?'<div style="overflow:auto"><table><tr><th>Input</th><th>'+a.label+'</th><th>'+b.label+'</th><th>Change</th></tr>'+inputRows+'</table></div>':'<p class="check">Input หลักเหมือนกัน</p>')+
    '<h4>Engineering Output Diff</h4>'+
    '<div style="overflow:auto"><table><tr><th>Metric</th><th>'+a.label+'</th><th>'+b.label+'</th><th>Δ B-A</th></tr>'+rows+'</table></div>';
}

$("#refreshEngineeringSummary")?.addEventListener("click",refreshEngineeringDecisionSummary);
$("#runWebSensitivity")?.addEventListener("click",runWebSensitivity);
$("#refreshWebTrace")?.addEventListener("click",refreshWebCalculationTrace);
$("#webDesignLock")?.addEventListener("click",()=>applyWebDesignLock(!(localStorage.getItem(CVET_WEB_LOCK_STORE)==="1")));
$("#captureWebRevisionA")?.addEventListener("click",async()=>{try{await captureWebRevision("A");}catch(e){setError($("#webRevisionResult"),e);}});
$("#captureWebRevisionB")?.addEventListener("click",async()=>{try{await captureWebRevision("B");}catch(e){setError($("#webRevisionResult"),e);}});
$("#compareWebRevisions")?.addEventListener("click",compareWebRevisionData);
try{applyWebDesignLock(localStorage.getItem(CVET_WEB_LOCK_STORE)==="1",false);}catch(e){}

setupDynamicProjectParameters();
checkHealth();
setTimeout(()=>syncDesktopProjectValues({automatic:true}),100);
setTimeout(()=>$("#calcRamp").click(),180);
setTimeout(()=>$("#calcWinch").click(),300);
setTimeout(()=>$("#calcWinchBattery").click(),360);
setTimeout(()=>$("#calcStability").click(),440);
