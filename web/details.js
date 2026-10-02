/* CVET V53.5 detailed web calculation tables.
   Loaded after app.js and appends step-by-step engineering details. */
(function(){
  function table(rows){
    const h=["ตัวแปร / รายการ","สูตรสัญลักษณ์","แทนค่าตัวเลข","ผลลัพธ์","หน่วย","คำนวณหาอะไร","อธิบายแบบง่าย"];
    return '<div class="detail-scroll"><table class="detail-table"><thead><tr>'+
      h.map(x=>'<th>'+x+'</th>').join('')+
      '</tr></thead><tbody>'+
      rows.map(r=>'<tr>'+r.map((x,i)=>'<td'+(i===3?' class="detail-result"':'')+'>'+x+'</td>').join('')+'</tr>').join('')+
      '</tbody></table></div>';
  }
  function add(out,title,rows,note){
    out.insertAdjacentHTML("beforeend",
      '<h3 class="detail-title">'+title+'</h3>'+table(rows)+(note?'<p class="check">'+note+'</p>':''));
  }
  function n(v,d){const x=Number(v);return Number.isFinite(x)?x:(d||0);}
  function wait(ms){return new Promise(r=>setTimeout(r,ms));}

  async function driveDetails(){
    await wait(1200);
    const form=$("#driveForm"), out=$("#driveResult"), p=formObject(form);
    try{
      const r=await api("/api/calc/drive-torque",p);
      const rr=r.wheel_radius_m, eff=r.efficiency;
      add(out,"รายละเอียดการคำนวณ Drive Torque แบบ Step-by-step",[
        ["v - ความเร็ว SI","v = v_kmh / 3.6",f(p.speed_kmh,3)+" ÷ 3.6",f(r.speed_m_s,6),"m/s","แปลงความเร็วเป็น SI","ใช้ในสมการแรง กำลัง และรอบล้อ"],
        ["r - รัศมีล้อ","r = D × 0.0254 / 2",f(p.wheel_diameter_in,3)+" × 0.0254 ÷ 2",f(rr,6),"m","หารัศมีล้อ","แปลงนิ้วเป็นเมตรแล้วหาร 2"],
        ["a - ความเร่ง","a = v / t_acc",f(r.speed_m_s,6)+" ÷ "+f(p.accel_time_s,3),f(r.accel_m_s2,6),"m/s²","หาความเร่งเฉลี่ย","ความเร็วเป้าหมาย ÷ เวลาเร่ง"],
        ["Fg - แรงความชัน","Fg = m g sinθ",f(p.mass_kg,2)+" × 9.81 × sin("+f(p.slope_deg,2)+"°)",f(r.fg_n,3),"N","แรงจากน้ำหนักตามทางลาด","มวล × g × sine มุมลาด"],
        ["Fr - แรงกลิ้ง","Fr = Crr m g cosθ",f(p.rolling_coeff,4)+" × "+f(p.mass_kg,2)+" × 9.81 × cos("+f(p.slope_deg,2)+"°)",f(r.fr_n,3),"N","แรงต้านการกลิ้ง","Crr × แรงกดตั้งฉาก"],
        ["Fa - แรงเร่ง","Fa = m a",f(p.mass_kg,2)+" × "+f(r.accel_m_s2,6),f(r.fa_n,3),"N","แรงเพิ่มในช่วงเร่ง","มวล × ความเร่ง"],
        ["FΣ - แรงรวม","Fg + Fr + Fa",f(r.fg_n,2)+" + "+f(r.fr_n,2)+" + "+f(r.fa_n,2),f(r.force_sum_n,3),"N","รวมแรงก่อนเผื่อ","แรงลาด + กลิ้ง + เร่ง"],
        ["Fdesign - แรงออกแบบ","FΣ × SF",f(r.force_sum_n,3)+" × "+f(p.safety_factor,2),f(r.design_force_n,3),"N","แรงขับหลังเผื่อ","แรงรวม × Safety Factor"],
        ["Fmotor - แรงต่อมอเตอร์","Fdesign / Nmotor",f(r.design_force_n,3)+" ÷ "+f(p.motors,0),f(r.force_per_motor_n,3),"N/motor","แบ่งแรงให้มอเตอร์","แรงรวม ÷ จำนวนมอเตอร์"],
        ["Tmotor - แรงบิดต่อล้อ","Fmotor × r",f(r.force_per_motor_n,3)+" × "+f(rr,6),f(r.torque_per_motor_nm,3),"N·m","แรงบิดที่ล้อต้องมี","แรงสัมผัสล้อ × รัศมี"],
        ["Wheel RPM","v/(2πr) × 60",f(r.speed_m_s,6)+" ÷ (2π×"+f(rr,6)+") × 60",f(r.wheel_rpm,3),"rpm","รอบล้อที่ความเร็วกำหนด","ความเร็วเชิงเส้น → รอบ"],
        ["Pwheel design","Fdesign × v",f(r.design_force_n,3)+" × "+f(r.speed_m_s,6),f(r.design_wheel_power_total_w,3),"W","กำลังกลที่ล้อ","แรงออกแบบ × ความเร็ว"],
        ["Pbattery","Pwheel / η",f(r.design_wheel_power_total_w,3)+" ÷ "+f(eff,3),f(r.electrical_power_total_w,3),"W","กำลังไฟจากแบต","ชดเชย Loss ระบบขับเคลื่อน"],
        ["Ibatt","Pbattery / V",f(r.electrical_power_total_w,3)+" ÷ "+f(p.voltage_v,1),f(r.battery_current_a,3),"A","กระแสแบตโดยประมาณ","กำลังไฟ ÷ แรงดัน"],
        ["Traction margin","Ftraction / Fdesign",f(r.traction_limit_n,2)+" ÷ "+f(r.design_force_n,2),f(r.traction_margin,3),"-","ตรวจแรงยึดเกาะ","มากกว่า 1 มี margin ตามโมเดล"]
      ],"ควรเทียบ Torque/Current curve ของ QS Motor และ VESC จริงอีกครั้งที่ความเร็วต่ำ");
    }catch(e){}
  }

  async function batteryDetails(){
    await wait(1200);
    const form=$("#batteryForm"), out=$("#batteryResult"), p=formObject(form);
    try{
      const r=await api("/api/calc/drive-battery",p);
      const v=r.speed_m_s, cyc=2*p.one_way_m;
      const flat=Math.max(0,cyc-2*p.slope_length_m), flatH=(flat/v)/3600, upH=(p.slope_length_m/v)/3600;
      const th=p.slope_deg*Math.PI/180, fflat=p.rolling_coeff*p.mass_kg*9.81, pflat=fflat*v;
      const fgrade=p.mass_kg*9.81*Math.sin(th), frr=p.rolling_coeff*p.mass_kg*9.81*Math.cos(th), fup=fgrade+frr, pup=fup*v;
      const a=v/p.accel_time_s, facc=p.mass_kg*a, pacc=(fup+facc)*v;
      const dod=p.dod_pct/100, reserve=p.reserve_pct/100;
      add(out,"รายละเอียดพลังงานและการเลือก Main Battery 72V",[
        ["v - ความเร็ว SI","v = km/h / 3.6",f(p.speed_kmh,3)+" ÷ 3.6",f(v,6),"m/s","แปลงความเร็ว","ใช้คำนวณเวลา แรง และกำลัง"],
        ["Dcycle - ระยะต่อรอบ","2 × one_way","2 × "+f(p.one_way_m,2),f(cyc,3),"m/รอบ","ระยะไป-กลับ","1 รอบ = ไป + กลับ"],
        ["tdrive","Dcycle / v",f(cyc,3)+" ÷ "+f(v,6),f(r.drive_time_per_round_s,3),"s/รอบ","เวลารถวิ่ง","เฉพาะเวลามอเตอร์ขับเคลื่อน"],
        ["tlift/event","จาก Winch Operating Time",f(p.lift_time_per_event_s,3),f(r.lift_time_per_event_s,3),"s/event","เวลา 1 งานยก","ขึ้น + ลง"],
        ["tlift/round","tlift/event × Nevent",f(r.lift_time_per_event_s,3)+" × "+r.lift_events_per_round,f(r.lift_time_per_round_s,3),"s/รอบ","เวลายกรวม","รถหยุดระหว่างยก"],
        ["tother","Other stop",f(r.other_stop_time_per_round_s,3),f(r.other_stop_time_per_round_s,3),"s/รอบ","เวลาหยุดอื่น","ไม่ใช่เวลายก"],
        ["tround","tdrive + tlift + tother",f(r.drive_time_per_round_s,3)+" + "+f(r.lift_time_per_round_s,3)+" + "+f(r.other_stop_time_per_round_s,3),f(r.round_time_s,3),"s/รอบ","เวลารวมหนึ่งรอบ","รวมวิ่ง + ยก + หยุด"],
        ["Ntheory","runtime / tround",f(p.runtime_h*3600,1)+" ÷ "+f(r.round_time_s,3),f(r.cycles_theoretical,4),"รอบ","จำนวนรอบเชิงทฤษฎี","ก่อนปัดลง"],
        ["Ncomplete","floor(Ntheory)",f(r.cycles_theoretical,4),f(r.completed_round_trips,0),"รอบ","จำนวนรอบเต็ม","ใช้คำนวณพลังงานขับรวม"],
        ["Dflat","Dcycle − 2Lslope",f(cyc,2)+" − 2×"+f(p.slope_length_m,2),f(flat,3),"m/รอบ","ระยะทางราบ","ส่วนที่ไม่ใช่ทางลาด"],
        ["tflat","Dflat/v/3600",f(flat,3)+" ÷ "+f(v,6)+" ÷ 3600",f(flatH,6),"h/รอบ","เวลาทางราบ","ระยะ ÷ ความเร็ว"],
        ["tup","Lslope/v/3600",f(p.slope_length_m,3)+" ÷ "+f(v,6)+" ÷ 3600",f(upH,6),"h/รอบ","เวลาขึ้นลาด","เวลา 1 ช่วงทางลาด"],
        ["Fflat","Crr m g",f(p.rolling_coeff,4)+" × "+f(p.mass_kg,2)+" × 9.81",f(fflat,3),"N","แรงกลิ้งทางราบ","Crr × น้ำหนัก"],
        ["Pflat","Fflat v",f(fflat,3)+" × "+f(v,6),f(pflat,3),"W","กำลังทางราบ","แรง × ความเร็ว"],
        ["Fgrade","m g sinθ",f(p.mass_kg,2)+" × 9.81 × sin("+f(p.slope_deg,2)+"°)",f(fgrade,3),"N","แรงจากความชัน","องค์ประกอบน้ำหนักตามลาด"],
        ["Frr slope","Crr m g cosθ",f(p.rolling_coeff,4)+" × "+f(p.mass_kg,2)+" × 9.81 × cos("+f(p.slope_deg,2)+"°)",f(frr,3),"N","แรงกลิ้งบนลาด","ใช้แรงปกติบนลาด"],
        ["Pup","(Fgrade+Frr)v",f(fup,3)+" × "+f(v,6),f(pup,3),"W","กำลังกลขึ้นลาด","แรงขึ้นลาด × ความเร็ว"],
        ["a","v/t_acc",f(v,6)+" ÷ "+f(p.accel_time_s,3),f(a,6),"m/s²","ความเร่ง","ใช้ตรวจ peak"],
        ["Pacc peak","(Fup+Facc)v","("+f(fup,3)+"+"+f(facc,3)+")×"+f(v,6),f(pacc,3),"W","กำลัง peak ตอนเร่ง","แรงขึ้นลาด + แรงเร่ง"],
        ["Edrive/trip","Energy model per complete round",r.energy_model,f(r.trip_drive_energy_wh,3),"Wh/รอบ","พลังงานขับต่อรอบ","ไม่รวมวินช์"],
        ["Edrive","Etrip × Ncomplete",f(r.trip_drive_energy_wh,3)+" × "+r.completed_round_trips,f(r.drive_energy_wh,3),"Wh","พลังงานขับรวม","นับเฉพาะรอบที่ทำครบ"],
        ["Eaux","Paux × runtime",f(p.aux_power_w,2)+" × "+f(p.runtime_h,3),f(r.aux_energy_wh,3),"Wh","พลังงานอุปกรณ์","สมมติเปิดตลอดเวลาทำงาน"],
        ["Eload","Edrive + Eaux",f(r.drive_energy_wh,3)+" + "+f(r.aux_energy_wh,3),f(r.load_energy_wh,3),"Wh","พลังงานโหลดรวม","ไม่รวมวินช์ 12 V"],
        ["Enom","Eload / DoD",f(r.load_energy_wh,3)+" ÷ "+f(dod,3),f(r.nominal_energy_wh,3),"Wh","พลังงาน nominal","จำกัดการคายประจุ"],
        ["Edesign","Enom × (1+Reserve)",f(r.nominal_energy_wh,3)+" × (1+"+f(reserve,3)+")",f(r.design_energy_wh,3),"Wh","พลังงานออกแบบ","เพิ่มพลังงานสำรอง"],
        ["Cdesign","Edesign / V",f(r.design_energy_wh,3)+" ÷ "+f(p.voltage_v,1),f(r.design_ah,3),"Ah","ความจุขั้นต่ำ","Wh ÷ V"],
        ["Cstandard","ปัดขึ้นขนาดมาตรฐาน","จาก "+f(r.design_ah,3)+" Ah",f(r.standard_ah,0),"Ah","ขนาดแบตที่เลือก","เลือกค่ามาตรฐาน ≥ ค่าคำนวณ"],
        ["Iup calc","Pup/η/V",f(pup,3)+" ÷ "+f(p.drive_eff_pct/100,3)+" ÷ "+f(p.voltage_v,1),f(r.uphill_current_calc_a,3),"A","กระแสขึ้นลาด","กำลัง ÷ η ÷ V"],
        ["Iacc calc","Pacc/η/V",f(pacc,3)+" ÷ "+f(p.drive_eff_pct/100,3)+" ÷ "+f(p.voltage_v,1),f(r.accel_current_calc_a,3),"A","กระแส peak เชิงคำนวณ","ช่วงเร่งขึ้นลาด"],
        ["BMS continuous","I required",f(r.continuous_current_required_a,3),f(r.continuous_current_required_a,3),"A","กระแสต่อเนื่องขั้นต่ำ","Candidate BMS ต้องไม่ต่ำกว่านี้"],
        ["BMS peak","I peak required",f(r.peak_current_required_a,3),f(r.peak_current_required_a,3),"A","กระแส peak ขั้นต่ำ","Candidate BMS ต้องรองรับ"],
        ["Candidate runtime","Eusable / Pavg",f(r.candidate.load_budget_wh,2)+" ÷ average operating power",f(r.candidate.runtime_h,3),"h","คำนวณย้อนกลับจาก Ah","ใช้ DoD + Reserve policy เดิม"],
        ["Candidate full rounds","floor(runtime / t_round)",f(r.candidate.runtime_h,3)+" h ÷ "+f(r.round_time_s/3600,6)+" h/รอบ",f(r.candidate.full_rounds,0),"รอบ","จำนวนรอบเต็มจากแบต Candidate","ไม่รวมพลังงานวินช์ 12 V"],
        ["Suggested Ah","max(Energy, C-rate) → standard",f(r.design_ah_with_current,3),f(r.suggested_ah,0),"Ah","ขนาดมาตรฐานที่ควรตรวจสเปก","ยังต้องยืนยัน datasheet จริง"]
      ],"เวลายกถูกใช้เพื่อหาจำนวนรอบที่รถวิ่งได้จริง แต่พลังงานวินช์ไม่ถูกรวมใน Main Battery 72 V เพราะใช้แบต 12 V แยก • Reverse runtime เป็นค่าประมาณจาก Operating Cycle ปัจจุบัน • No regen");
    }catch(e){}
  }

  async function winchDetails(){
    await wait(1200);
    const form=$("#winchForm"), out=$("#winchResult"), p=formObject(form);
    try{
      const r=await api("/api/calc/winch",p), c=r.core, o=r.operation, b=r.battery;
      add(out,"รายละเอียด Winch + จำนวนรอบ + แบตเตอรี่ 12V",[
        ["Interpolation","Linear interpolation จาก datasheet","Load = "+f(c.load_kg,2)+" kg",f(c.up_speed_m_min,4)+" m/min; "+f(c.up_current_a,3)+" A","-","หาความเร็วและกระแสตามโหลด","คั่นค่าจาก First Layer datasheet"],
        ["Rope layer","เลือกจากระยะยก","Lift = "+f(c.lift_m,3)+" m","Layer "+c.layer,"-","ตรวจชั้นเชือก","ชั้นสูงขึ้นแรงดึงลดลง"],
        ["Line pull check","Load ≤ line pull",f(c.load_kg,2)+" ≤ "+f(c.layer_line_pull_kg,2),statusSpan(c.layer_pull_ok),"-","ตรวจแรงดึงพอหรือไม่","ต้องผ่านก่อนใช้งาน"],
        ["t_up","Lift/Speed × 60",f(c.lift_m,3)+" ÷ "+f(c.up_speed_m_min,4)+" × 60",f(c.up_time_s,3),"s","เวลายกขึ้น 1 ครั้ง","ระยะ ÷ ความเร็ว"],
        ["t_down","ตาม Down mode",b.down_basis,f(b.down_time_s,3),"s","เวลาปล่อยลง","Conservative หรือ Custom"],
        ["t_event","t_up + t_down",f(o.up_time_s,3)+" + "+f(o.down_time_s,3),f(o.event_time_s,3),"s/event","เวลา 1 งานยก","1 งาน = ขึ้น + ลง"],
        ["t_oneway","Distance / speed",f(o.one_way_m,2)+" m @ "+f(o.vehicle_speed_kmh,3)+" km/h",f(o.one_way_time_s,3),"s","เวลารถเที่ยวเดียว","ใช้หารอบรวม"],
        ["t_round","drive + lift + stop",f(o.drive_round_time_s,2)+" + "+f(o.lift_round_time_s,2)+" + "+f(o.other_stop_s,2),f(o.round_time_s,3),"s/รอบ","เวลารวมหนึ่งรอบ","รวมวิ่ง+วินช์+หยุด"],
        ["Nround","floor(total/t_round)",f(o.operating_hours*3600,1)+" ÷ "+f(o.round_time_s,3),f(o.completed_round_trips,0),"รอบ","จำนวนรอบเต็ม","ปัดลง"],
        ["Lift events Auto","rounds × events/round",o.completed_round_trips+" × "+o.events_per_round,f(o.lift_events,0),"events","จำนวนงานยกอัตโนมัติ","ตามรอบใน 3 ชั่วโมง"],
        ["E_up/event","V I_up t_up /3600",f(b.voltage_v,1)+" × "+f(b.up_current_a,3)+" × "+f(b.up_time_s,3)+" ÷ 3600",f(b.e_up_wh,4),"Wh","พลังงานขึ้นต่องาน","สมการ VIt"],
        ["E_down/event","V I_down t_down /3600",f(b.voltage_v,1)+" × "+f(b.down_current_a,3)+" × "+f(b.down_time_s,3)+" ÷ 3600",f(b.e_down_wh,4),"Wh","พลังงานลงต่องาน","ตาม Down mode"],
        ["E_event","E_up + E_down",f(b.e_up_wh,4)+" + "+f(b.e_down_wh,4),f(b.e_event_wh,4),"Wh/event","พลังงานหนึ่งงานยก","ขึ้น + ลง"],
        ["Nevent used","Auto / Manual",b.event_mode,f(b.events,0),"events","จำนวนงานที่ใช้เลือกแบต","Manual ใช้ค่าที่กรอกเอง"],
        ["E_total","Nevent × E_event",b.events+" × "+f(b.e_event_wh,4),f(b.e_total_wh,3),"Wh","พลังงานวินช์รวม","จำนวนงาน × พลังงานต่องาน"],
        ["Ah used","E_total / V",f(b.e_total_wh,3)+" ÷ "+f(b.voltage_v,1),f(b.ah_used,3),"Ah","Ah ที่ใช้จริงตามโมเดล","ก่อน Reserve/DoD"],
        ["Ah design","E(1+Reserve)/(V×DoD)",f(b.e_total_wh,3)+" × (1+"+f(b.reserve,3)+") ÷ ("+f(b.voltage_v,1)+"×"+f(b.dod,3)+")",f(b.ah_design,3),"Ah","Ah ขั้นต่ำออกแบบ","รวม Reserve และ DoD"],
        ["Standard Ah","ปัดขึ้นขนาดมาตรฐาน","จาก "+f(b.ah_design,3),f(b.standard_ah,0),"Ah","แบตที่เลือก","ค่ามาตรฐาน ≥ ค่าคำนวณ"],
        ["Operating current","max(Iup,Idown)","max("+f(b.up_current_a,2)+","+f(b.down_current_a,2)+")",f(b.operating_current_a,3),"A","ตรวจ BMS continuous","ต้องรองรับกระแสทำงาน"],
        ["Peak current","ตรวจ Starting/Stall surge","BMS peak = "+f(b.bms_peak_a,1)+" A","CHECK","-","ตรวจ BMS peak","Datasheet ไม่มี surge จึงต้องทดสอบ/ดูสเปกเพิ่ม"]
      ],"โหมด Manual สามารถกำหนดจำนวนงานยกเองได้ โดย 1 งาน = ขึ้น 1 ครั้ง + ลง 1 ครั้ง");
    }catch(e){}
  }

  async function stabilityDetails(){
    await wait(1200);
    const form=$("#stabilityForm"), out=$("#stabilityResult"), p=formObject(form);
    try{
      const r=await api("/api/calc/stability",p);
      const ss=r.side.sf>=999?"∞":f(r.side.sf,3), fs=r.front.sf>=999?"∞":f(r.front.sf,3), rs=r.rear.sf>=999?"∞":f(r.rear.sf,3);
      const mveh=Math.max(0,p.total_mass_kg-p.payload_mass_kg-p.boom_mass_kg);
      add(out,"รายละเอียด Stability / Tipping",[
        ["Pivot side","track / 2",f(p.track_width_m,3)+" ÷ 2",f(r.side.pivot_m,4),"m","แนวล้อที่เป็นจุดหมุน","จุดหมุนด้านข้าง"],
        ["Vehicle mass model","Mtotal−Mload−Mboom",f(p.total_mass_kg,1)+"−"+f(p.payload_mass_kg,1)+"−"+f(p.boom_mass_kg,1),f(mveh,2),"kg","มวลรถที่เหลือในโมเดล","ใช้สร้างโมเมนต์ต้าน"],
        ["Load lateral","|L sin(angle)|",f(p.boom_length_m,3)+" × |sin("+f(p.crane_angle_deg,2)+"°)|",f(r.side.load_lateral_m,4),"m","ตำแหน่งโหลดด้านข้าง","เทียบกับ pivot"],
        ["Boom lateral","|(L/2) sin(angle)|",f(p.boom_length_m/2,3)+" × |sin("+f(p.crane_angle_deg,2)+"°)|",f(r.side.boom_lateral_m,4),"m","ตำแหน่ง CG boom โดยประมาณ","สมมติ CG ที่ครึ่งแขน"],
        ["MO side","Σ overturning moment","โหลด/boom × g × arm × factor",f(r.side.overturning_moment_nm,3),"N·m","โมเมนต์ทำให้คว่ำ","รวมส่วนที่เลย pivot"],
        ["MR side","Σ resisting moment","มวล × g × arm",f(r.side.resisting_moment_nm,3),"N·m","โมเมนต์ต้านการคว่ำ","รวมส่วนที่อยู่ในฐาน"],
        ["SF side","MR / MO",f(r.side.resisting_moment_nm,3)+" ÷ "+f(r.side.overturning_moment_nm,3),ss,"-","Safety Factor ด้านข้าง","เป้าหมาย ≥ "+f(p.required_sf,2)],
        ["SF front","MRfront / MOfront","จาก wheelbase + crane x + CG",fs,"-","Safety Factor ด้านหน้า","เป้าหมาย ≥ "+f(p.required_sf,2)],
        ["SF rear","MRrear / MOrear","จาก wheelbase + crane x + CG",rs,"-","Safety Factor ด้านหลัง","เป้าหมาย ≥ "+f(p.required_sf,2)],
        ["Crane x","rear pivot + crane_from_rear",f(r.geometry.rear_x_m,4)+" + "+f(p.crane_from_rear_m,4),f(r.geometry.crane_x_m,4),"m","ตำแหน่งเสาเครนตามยาว","ใช้หา front/rear moment"],
        ["Load x","crane x + boom cos(angle)",f(r.geometry.crane_x_m,4)+" + "+f(p.boom_length_m,3)+" cos("+f(p.crane_angle_deg,2)+"°)",f(r.geometry.load_x_m,4),"m","ตำแหน่งโหลดตามยาว","ใช้หาแนวโน้มคว่ำหน้า/หลัง"]
      ],"Static preliminary model — ต้องยืนยัน CG จริง, dynamic load, การแกว่งโหลด, การเบรก/เลี้ยว และความเอียงพื้นก่อนผลิต");
    }catch(e){}
  }

  $("#calcDrive").addEventListener("click",driveDetails);
  $("#calcBattery").addEventListener("click",batteryDetails);
  $("#calcWinch").addEventListener("click",winchDetails);
  $("#calcStability").addEventListener("click",stabilityDetails);
})();