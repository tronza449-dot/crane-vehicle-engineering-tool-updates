const $ = (s, root=document) => root.querySelector(s);
const $$ = (s, root=document) => [...root.querySelectorAll(s)];

function num(v,d=0){const n=Number(v);return Number.isFinite(n)?n:d;}
function f(v,d=2){return num(v).toLocaleString("th-TH",{minimumFractionDigits:d,maximumFractionDigits:d});}
function statusSpan(ok){return '<span class="'+(ok?'pass':'fail')+'">'+(ok?'PASS':'FAIL')+'</span>';}

function formObject(form){
  const out={};
  new FormData(form).forEach((value,key)=>{
    const el=form.elements[key];
    out[key]=(el && (el.type==="number"||el.type==="range"))?Number(value):value;
  });
  return out;
}
function getPin(){return localStorage.getItem("cvet_web_pin")||"";}

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
  $(".tab").forEach(x=>x.classList.remove("active"));
  $(".page").forEach(x=>x.classList.remove("active"));
  btn.classList.add("active");
  page.classList.add("active");
  window.scrollTo({top:0,behavior:"smooth"});
}
$(".tab").forEach(btn=>btn.addEventListener("click",()=>openTab(btn.dataset.tab)));
$("[data-open-tab]").forEach(card=>card.addEventListener("click",()=>openTab(card.dataset.openTab)));
$("#savePin").addEventListener("click",()=>{localStorage.setItem("cvet_web_pin",$("#webPin").value.trim());$("#pinStatus").textContent="บันทึกแล้ว";});
$("#eventMode").addEventListener("change",()=>{$("#manualEventsWrap").classList.toggle("hidden",$("#eventMode").value!=="manual");});
$("#downMode").addEventListener("change",()=>{$$(".customDown").forEach(x=>x.classList.toggle("hidden",$("#downMode").value!=="custom"));});

$("#calcDrive").addEventListener("click",async()=>{
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
  }catch(e){setError(out,e);}
});

$("#calcBattery").addEventListener("click",async()=>{
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
      '<h3>Main Battery 72 V Result</h3><div class="metric-grid">'+
      '<div class="metric"><div class="k">รอบเต็มในเวลาที่กำหนด</div><div class="v">'+r.completed_round_trips+' รอบ</div></div>'+
      '<div class="metric"><div class="k">เวลารวม / รอบ</div><div class="v">'+f(r.round_time_s/60,2)+' min</div></div>'+
      '<div class="metric"><div class="k">Drive energy</div><div class="v">'+f(r.drive_energy_wh,1)+' Wh</div></div>'+
      '<div class="metric"><div class="k">Design capacity</div><div class="v">'+f(r.design_ah,2)+' Ah</div></div>'+
      '<div class="metric"><div class="k">รวม Current/C-rate</div><div class="v">'+f(r.design_ah_with_current,2)+' Ah</div></div>'+
      '<div class="metric"><div class="k">Suggested standard</div><div class="v">'+f(r.suggested_ah,0)+' Ah</div></div>'+
      '<div class="metric"><div class="k">BMS Continuous ≥</div><div class="v">'+f(r.continuous_current_required_a,1)+' A</div></div>'+
      '<div class="metric"><div class="k">BMS Peak ≥</div><div class="v">'+f(r.peak_current_required_a,1)+' A</div></div></div>'+

      '<h3>Operating Time</h3>'+
      '<div class="formula"><b>t_round = t_drive + t_lift + t_other</b><br>'+
      '<b>แทนค่า:</b> '+f(r.drive_time_per_round_s,2)+' + '+f(r.lift_time_per_round_s,2)+' + '+f(r.other_stop_time_per_round_s,2)+
      ' = <b>'+f(r.round_time_s,2)+' s/รอบ</b><br>'+
      '<b>จำนวนรอบเชิงทฤษฎี:</b> '+f(r.cycles_theoretical,2)+' รอบ → นับรอบที่ทำครบ = <b>'+r.completed_round_trips+' รอบ</b></div>'+
      '<div class="formula"><b>เวลางานยกมีผลกับจำนวนรอบ แต่ไม่รวมพลังงานวินช์ในแบต 72 V</b><br>'+
      'Winch ใช้แบต 12 V แยก ดังนั้น Main Battery คิดเฉพาะพลังงานขับรถ + Auxiliary</div>'+

      '<h3>Reverse Calculation — แบตที่กำลังจะซื้อ</h3>'+
      '<div class="metric-grid">'+
      '<div class="metric"><div class="k">Candidate</div><div class="v">'+f(c.capacity_ah,1)+' Ah</div></div>'+
      '<div class="metric"><div class="k">Estimated runtime*</div><div class="v">'+f(c.runtime_h,2)+' h</div></div>'+
      '<div class="metric"><div class="k">Full rounds*</div><div class="v">'+c.full_rounds+' รอบ</div></div>'+
      '<div class="metric"><div class="k">Margin vs target</div><div class="v">'+(c.target_margin_pct>=0?'+':'')+f(c.target_margin_pct,1)+'%</div></div></div>'+
      '<table><tr><th>Candidate check</th><th>Required</th><th>Candidate</th><th>Status</th></tr>'+
      '<tr><td>Energy / Capacity</td><td>≥ '+f(r.design_ah,2)+' Ah</td><td>'+f(c.capacity_ah,1)+' Ah</td><td>'+statusSpan(c.energy_ok)+'</td></tr>'+
      '<tr><td>BMS Continuous</td><td>≥ '+f(r.continuous_current_required_a,1)+' A</td><td>'+f(c.bms_cont_a,1)+' A</td><td>'+bmsCont+'</td></tr>'+
      '<tr><td>BMS Peak</td><td>≥ '+f(r.peak_current_required_a,1)+' A</td><td>'+f(c.bms_peak_a,1)+' A</td><td>'+bmsPeak+'</td></tr></table>'+
      '<p class="check">*Runtime/รอบ เป็นค่าประมาณจาก Operating Cycle ปัจจุบัน + Auxiliary + DoD + Reserve ไม่รวมพลังงานวินช์ 12 V</p>'+

      '<h3>Compare Battery Size</h3>'+
      '<div style="overflow:auto"><table><tr><th>Battery</th><th>Rated Wh</th><th>Runtime*</th><th>Full rounds*</th><th>Margin target</th><th>Req cont C</th><th>Req peak C</th><th>Check</th></tr>'+
      compare+'</table></div>'+

      '<h3>สูตรแบต</h3>'+
      '<div class="formula"><b>Eload = Edrive + Eaux</b><br><b>สูตรภาษาไทย:</b> พลังงานโหลดรวม = พลังงานขับรถ + พลังงานอุปกรณ์เสริม<br><b>ผล:</b> '+f(r.load_energy_wh,2)+' Wh</div>'+
      '<div class="formula"><b>Edesign = (Eload ÷ DoD) × (1 + Reserve)</b><br><b>สูตรภาษาไทย:</b> พลังงานออกแบบ = พลังงานโหลดรวม ÷ DoD × (1 + พลังงานสำรอง)<br><b>ผล:</b> '+f(r.design_energy_wh,2)+' Wh</div>'+
      '<div class="formula"><b>Ah = Edesign ÷ V</b><br><b>สูตรภาษาไทย:</b> ความจุแบต = พลังงานออกแบบ ÷ แรงดันแบต<br><b>ผล:</b> '+f(r.design_ah,2)+' Ah @ '+f(r.voltage_v,0)+' V</div>'+
      '<div class="formula"><b>Runtime(reverse) = Usable energy budget ÷ Average operating power</b><br>'+
      '<b>สูตรภาษาไทย:</b> เวลาที่แบต Candidate ใช้งานได้ ≈ พลังงานที่อนุญาตตาม DoD/Reserve ÷ กำลังเฉลี่ยของ Operating Cycle</div>'+
      '<p>Current estimate: Continuous ≈ <b>'+f(r.continuous_current_required_a,2)+' A</b> • Peak ≈ <b>'+f(r.peak_current_required_a,2)+' A</b> • No regen</p>';
  }catch(e){setError(out,e);}
});

$("#calcWinch").addEventListener("click",async()=>{
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
  }catch(e){setError(out,e);}
});

$("#calcStability").addEventListener("click",async()=>{
  const out=$("#stabilityResult");setLoading(out);
  try{
    const r=await api("/api/calc/stability",formObject($("#stabilityForm")));
    const sideSf=r.side.sf>=999?'∞':f(r.side.sf,3),frontSf=r.front.sf>=999?'∞':f(r.front.sf,3),rearSf=r.rear.sf>=999?'∞':f(r.rear.sf,3);
    out.innerHTML=
      '<h3>Stability Result</h3><div class="metric-grid">'+
      '<div class="metric"><div class="k">Side SF</div><div class="v">'+sideSf+'</div><div>'+statusSpan(r.side.pass)+'</div></div>'+
      '<div class="metric"><div class="k">Front SF</div><div class="v">'+frontSf+'</div><div>'+statusSpan(r.front.pass)+'</div></div>'+
      '<div class="metric"><div class="k">Rear SF</div><div class="v">'+rearSf+'</div><div>'+statusSpan(r.rear.pass)+'</div></div></div>'+
      '<h3>Side tipping</h3><div class="formula"><b>SFside = MR ÷ MO</b><br><b>สูตรภาษาไทย:</b> Safety Factor ด้านข้าง = โมเมนต์ต้านการคว่ำ ÷ โมเมนต์ทำให้คว่ำ<br><b>แทนค่า:</b> '+f(r.side.resisting_moment_nm,2)+' ÷ '+f(r.side.overturning_moment_nm,2)+' = <b>'+sideSf+'</b></div>'+
      '<table><tr><th>รายการ</th><th>ค่า</th></tr><tr><td>Pivot = Track/2</td><td>'+f(r.side.pivot_m,3)+' m</td></tr><tr><td>ตำแหน่งโหลดด้านข้าง</td><td>'+f(r.side.load_lateral_m,3)+' m</td></tr><tr><td>MO</td><td>'+f(r.side.overturning_moment_nm,2)+' N·m</td></tr><tr><td>MR</td><td>'+f(r.side.resisting_moment_nm,2)+' N·m</td></tr></table>'+
      '<p class="check">โมเดลนี้เป็น Preliminary static model ต้องยืนยัน CG และน้ำหนักจริงก่อนผลิต</p>';
  }catch(e){setError(out,e);}
});

checkHealth();
setTimeout(()=>$("#calcWinch").click(),300);
