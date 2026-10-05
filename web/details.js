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
      add(out,"รายละเอียด Main Battery แบบ 1 Cycle",[
        ["d_flat","d_oneway − L_slope",f(r.one_way_m,2)+" − "+f(r.slope_length_m,2),f(r.flat_one_way_m,3),"m/เที่ยว","หาระยะทางราบต่อเที่ยว","30 m ไม่ได้เป็นทางชันทั้งหมด"],
        ["D_cycle","2 × d_oneway","2 × "+f(r.one_way_m,2),f(r.cycle_distance_m,3),"m/Cycle","หาระยะไป-กลับ","1 Cycle = ไป + กลับ"],
        ["F_flat","Crr m g",f(p.rolling_coeff,4)+" × "+f(r.mass_kg,2)+" × 9.81",f(r.flat_force_n,3),"N","แรงต้านทางราบ","ใช้ทั้งเที่ยวไปและเที่ยวกลับ"],
        ["E_flat,oneway","F_flat d_flat /(η×3600)",f(r.flat_force_n,2)+" × "+f(r.flat_one_way_m,2)+" /(η×3600)",f(r.flat_energy_one_way_wh,4),"Wh","พลังงานทางราบต่อเที่ยว","มีทั้งไปและกลับ"],
        ["F_up","mg sinθ + Crr mg cosθ",f(r.grade_force_n,2)+" + "+f(r.slope_rolling_force_n,2),f(r.uphill_force_n,3),"N","แรงช่วงขึ้นลาด","แรงความชัน + แรงกลิ้ง"],
        ["E_up","F_up L_slope /(η×3600)",f(r.uphill_force_n,2)+" × "+f(r.slope_length_m,2)+" /(η×3600)",f(r.uphill_slope_energy_wh,4),"Wh","พลังงานขึ้นลาด","อยู่ในเที่ยวไป"],
        ["F_down","max(0,Frr_slope−Fgrade)","max(0,"+f(r.slope_rolling_force_n,2)+"−"+f(r.grade_force_n,2)+")",f(r.downhill_drive_force_n,3),"N","แรงขับช่วงลงลาด","ถ้าแรงโน้มถ่วงช่วยพออาจเป็น 0"],
        ["E_down","F_down L_slope /(η×3600)",f(r.downhill_drive_force_n,2)+" × "+f(r.slope_length_m,2)+" /(η×3600)",f(r.downhill_slope_energy_wh,4),"Wh","พลังงานช่วงลาดลง","ไม่หักพลังงานคืน"],
        ["E_go","E_flat + E_up",f(r.flat_energy_one_way_wh,4)+" + "+f(r.uphill_slope_energy_wh,4),f(r.outbound_drive_energy_wh,4),"Wh","พลังงานเที่ยวไป","ทางราบ + ขึ้นลาด"],
        ["E_return","E_down + E_flat",f(r.downhill_slope_energy_wh,4)+" + "+f(r.flat_energy_one_way_wh,4),f(r.return_drive_energy_wh,4),"Wh","พลังงานเที่ยวกลับ","ลงลาด + ทางราบ"],
        ["E_drive,cycle","E_go + E_return",f(r.outbound_drive_energy_wh,4)+" + "+f(r.return_drive_energy_wh,4),f(r.trip_drive_energy_wh,4),"Wh/Cycle","พลังงานขับต่อ Cycle","ยังไม่รวม Auxiliary"],
        ["t_cycle","t_drive + t_lift + t_other",f(r.drive_time_per_round_s,2)+" + "+f(r.lift_time_per_round_s,2)+" + "+f(r.other_stop_time_per_round_s,2),f(r.round_time_s,3),"s/Cycle","เวลาต่อ Cycle","งานยกมีผลต่อจำนวน Cycle แต่พลังงานวินช์แยก"],
        ["E_aux,cycle","P_aux × t_cycle",f(p.aux_power_w,2)+" × "+f(r.round_time_s/3600,6),f(r.aux_energy_per_cycle_wh,4),"Wh/Cycle","ไฟอุปกรณ์เสริมต่อ Cycle","ESP32/Display/Relay ฯลฯ"],
        ["E_cycle","E_drive,cycle + E_aux,cycle",f(r.trip_drive_energy_wh,4)+" + "+f(r.aux_energy_per_cycle_wh,4),f(r.total_energy_per_cycle_wh,4),"Wh/Cycle","พลังงานรวมต่อ Cycle","ตัวหลักที่ใช้คูณจำนวน Cycle"],
        ["N_cycle","floor(runtime/t_cycle)",f(r.runtime_h*3600,1)+" ÷ "+f(r.round_time_s,3),f(r.completed_round_trips,0),"Cycle","จำนวน Cycle เต็ม","ปัดลงเพราะต้องทำงานให้ครบรอบ"],
        ["E_total","E_cycle × N",f(r.total_energy_per_cycle_wh,4)+" × "+r.completed_round_trips,f(r.load_energy_wh,3),"Wh","พลังงานรวม","ก่อนเผื่อ DoD/Reserve"],
        ["E_design","(E_total/DoD)(1+Reserve)",f(r.load_energy_wh,3)+" / "+f(p.dod_pct/100,3)+" × (1+"+f(p.reserve_pct/100,3)+")",f(r.design_energy_wh,3),"Wh","พลังงานแบตออกแบบ","เผื่อความจุใช้งานและสำรอง"],
        ["Ah","E_design / V",f(r.design_energy_wh,3)+" ÷ "+f(r.voltage_v,1),f(r.design_ah,3),"Ah","ความจุแบต","ค่าหยาบสำหรับเลือกขนาดแบต"],
        ["I_up","P_up /(ηV)","จากกำลังขึ้นลาด",f(r.uphill_current_calc_a,3),"A","กระแสช่วงขึ้นลาด","ใช้ตรวจ BMS เบื้องต้นแยกจาก Ah"]
      ],"แบบจำลองนี้ตั้งใจให้เรียบง่าย: ไม่คิดพลังงานช่วงออกตัว และไม่นำพลังงานจากช่วงลงลาดมาหักคืนแบตเตอรี่ • เที่ยวกลับยังใช้ไฟบนทางราบเสมอ • Winch ใช้แบต 12 V แยก");
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