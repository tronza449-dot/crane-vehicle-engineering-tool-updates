from pathlib import Path
import sys, math, os, json, tempfile, re, hashlib, subprocess, threading, urllib.request, urllib.parse, shutil
from datetime import datetime
from PySide6.QtCore import Qt, QPointF, QRectF, QTimer, QStandardPaths, Signal
from PySide6.QtGui import QPainter,QPen,QBrush,QColor,QPolygonF,QPageSize,QPdfWriter,QFont,QTextDocument,QPageLayout,QFontDatabase,QIcon
from PySide6.QtWidgets import *
from PySide6.QtPrintSupport import QPrinter


APP_NAME = "Crane Vehicle Engineering Tool"
APP_VERSION = "51.0.5"
DEFAULT_UPDATE_MANIFEST_URL = "https://raw.githubusercontent.com/tronza449-dot/crane-vehicle-engineering-tool-updates/main/latest.json"

def resource_path(relative_path):
    """Resolve bundled resources both from source and PyInstaller."""
    base = Path(getattr(sys, "_MEIPASS", Path(__file__).resolve().parent))
    return base / relative_path

APP_STYLE = """
/* ==================== V51 MODERN / READABLE UI ==================== */
QMainWindow { background:#edf3f8; }
QWidget { color:#203246; }
QLabel { color:#2a3d50; font-size:10.8pt; }
QToolTip {
    background:#102a43; color:white; border:0; padding:7px 10px;
    border-radius:6px; font-size:10pt;
}

/* ---------- Tabs ---------- */
QTabWidget::pane {
    border:1px solid #d7e1eb; background:#ffffff; border-radius:12px; top:-1px;
}
QTabBar::tab {
    background:#eef3f8; color:#53677d; padding:9px 14px; margin-right:4px;
    min-height:30px; font-weight:750; font-size:10.4pt;
    border-top-left-radius:9px; border-top-right-radius:9px;
}
QTabBar::tab:hover { background:#e4edf6; color:#17324d; }
QTabBar::tab:selected { background:#245fbb; color:white; }

/* ---------- Cards / sections ---------- */
QGroupBox {
    font-weight:800; font-size:11pt; color:#17324d;
    border:1px solid #d8e2ec; border-radius:12px;
    margin-top:14px; padding:17px 14px 14px 14px; background:#ffffff;
}
QGroupBox::title {
    subcontrol-origin:margin; left:15px; padding:0 8px;
    background:#ffffff; color:#17324d;
}
QFrame#topHeader {
    background:qlineargradient(x1:0,y1:0,x2:1,y2:0,stop:0 #123554,stop:1 #1d638f);
    border:0; border-radius:15px;
}
QFrame#softPanel {
    background:#ffffff; border:1px solid #d8e3ed; border-radius:13px;
}
QFrame#metricPanel {
    background:#f6faff; border:1px solid #d7e5f3; border-radius:12px;
}
QFrame#navPanel {
    background:#f8fbfe; border-right:1px solid #d8e3ed;
}

/* ---------- Inputs ---------- */
QDoubleSpinBox,QSpinBox,QComboBox,QLineEdit {
    min-height:36px; font-size:10.8pt;
    border:1px solid #c7d4e1; border-radius:9px; padding:4px 9px;
    background:#ffffff; selection-background-color:#2f6fd1;
}
QDoubleSpinBox:hover,QSpinBox:hover,QComboBox:hover,QLineEdit:hover {
    border-color:#8baed1;
}
QDoubleSpinBox:focus,QSpinBox:focus,QComboBox:focus,QLineEdit:focus {
    border:2px solid #3d7bd8; padding:3px 8px;
}
QDoubleSpinBox:disabled,QSpinBox:disabled,QComboBox:disabled,QLineEdit:disabled {
    background:#f2f5f8; color:#8392a3;
}
QComboBox::drop-down { border:0; width:28px; }
QCheckBox { spacing:9px; font-size:10.6pt; }
QCheckBox::indicator { width:20px; height:20px; }
QRadioButton { spacing:8px; font-size:10.6pt; }
QRadioButton::indicator { width:19px; height:19px; }

/* ---------- Buttons ---------- */
QPushButton {
    min-height:39px; border-radius:9px; padding:7px 15px;
    background:#ffffff; border:1px solid #c8d5e2;
    color:#183a57; font-size:10.3pt; font-weight:750;
}
QPushButton:hover { background:#f2f7fc; border-color:#84a9ce; }
QPushButton:pressed { background:#e4edf7; }
QPushButton:disabled { background:#f2f4f6; color:#9ba6b2; border-color:#dce2e8; }

QPushButton#primaryButton {
    color:white; border:0;
    background:qlineargradient(x1:0,y1:0,x2:1,y2:0,stop:0 #245fbb,stop:1 #2382c7);
    font-weight:850;
}
QPushButton#primaryButton:hover { background:#1d64b8; }
QPushButton#secondaryButton {
    background:#f5f8fc; border:1px solid #c8d5e2; color:#24445f;
}
QPushButton#dangerButton {
    background:#fff4f4; color:#b42318; border:1px solid #efb6b1;
}

/* ---------- Persistent left navigation ---------- */
QPushButton#navButton {
    min-height:46px; max-height:50px; text-align:left;
    padding:7px 12px; border-radius:10px; border:1px solid transparent;
    background:transparent; color:#41566c; font-size:10.4pt; font-weight:750;
}
QPushButton#navButton:hover {
    background:#edf4fb; color:#173f63; border-color:#d8e6f3;
}
QPushButton#navButton[active="true"] {
    background:#e7f0ff; color:#174f96; border:1px solid #c8ddfa;
    font-weight:900;
}
QLabel#navSection {
    color:#8291a1; font-size:8.5pt; font-weight:900;
    padding:9px 8px 3px 8px;
}

/* ---------- Text / reports ---------- */
QPlainTextEdit,QTextEdit {
    background:#ffffff; border:1px solid #d7e1eb; border-radius:10px;
    padding:9px; font-size:10.8pt;
    selection-background-color:#d8e9ff; selection-color:#17324d;
}
QScrollArea { border:0; background:transparent; }
QScrollArea > QWidget > QWidget { background:transparent; }

/* ---------- Tables ---------- */
QTableWidget {
    background:white; alternate-background-color:#f7fafc;
    gridline-color:#e0e7ef; border:1px solid #d7e1eb;
    border-radius:9px; font-size:10.5pt;
}
QTableWidget::item { padding:6px; }
QHeaderView::section {
    background:#eaf1f8; color:#17324d; padding:9px;
    border:0; border-right:1px solid #d5e0ea; border-bottom:1px solid #d5e0ea;
    font-weight:850; font-size:10.3pt;
}

/* ---------- Progress / sliders / scrollbars ---------- */
QProgressBar {
    border:1px solid #cbd8e5; border-radius:7px;
    background:#eef3f7; text-align:center; min-height:18px;
}
QProgressBar::chunk { border-radius:6px; background:#2f6fd1; }
QSlider::groove:horizontal { height:7px; background:#dce6f0; border-radius:3px; }
QSlider::handle:horizontal {
    width:20px; margin:-7px 0; border-radius:10px;
    background:#2f6fd1; border:2px solid white;
}
QScrollBar:vertical { width:12px; background:#eef3f7; margin:0; }
QScrollBar::handle:vertical { background:#b9c8d8; min-height:32px; border-radius:6px; }
QScrollBar::handle:vertical:hover { background:#95aac0; }
QScrollBar::add-line:vertical,QScrollBar::sub-line:vertical { height:0; }

/* ---------- Status bar ---------- */
QStatusBar {
    background:#ffffff; color:#5f7387;
    border-top:1px solid #d8e3ed; font-size:9.5pt;
}
"""

G=9.81


class Model3D(QWidget):
    """Interactive 3D crane visualizer rendered with QPainter.

    - Drag mouse: orbit camera
    - Mouse wheel: zoom
    - Double click: reset camera
    - Crane angle animates smoothly when the input changes
    """
    def __init__(self):
        super().__init__()
        self.d={}
        self.setMinimumHeight(300)
        self.setMouseTracking(True)
        self.setCursor(Qt.OpenHandCursor)
        self.yaw=math.radians(38)
        self.pitch=math.radians(24)
        self.zoom=1.0
        self._drag=None
        self._target_angle=0.0
        self._display_angle=0.0
        self._angle_ready=False
        self._anim=QTimer(self)
        self._anim.setInterval(16)
        self._anim.timeout.connect(self._animate_angle)

    def setD(self,d):
        self.d=dict(d)
        target=float(self.d.get("th",0.0))
        self._target_angle=target
        if not self._angle_ready:
            self._display_angle=target
            self._angle_ready=True
        elif abs(self._display_angle-target)>0.05:
            self._anim.start()
        self.update()

    def setCamera(self,yaw_deg,pitch_deg,zoom=None):
        self.yaw=math.radians(float(yaw_deg))
        self.pitch=math.radians(float(pitch_deg))
        if zoom is not None:
            self.zoom=max(.55,min(2.0,float(zoom)))
        self.update()

    def resetCamera(self):
        self.setCamera(38,24,1.0)

    def _animate_angle(self):
        delta=self._target_angle-self._display_angle
        if abs(delta)<0.08:
            self._display_angle=self._target_angle
            self._anim.stop()
        else:
            self._display_angle += delta*.22
        self.update()

    def mousePressEvent(self,e):
        if e.button()==Qt.LeftButton:
            self._drag=e.position()
            self.setCursor(Qt.ClosedHandCursor)

    def mouseMoveEvent(self,e):
        if self._drag is None:
            return
        now=e.position()
        dx=now.x()-self._drag.x()
        dy=now.y()-self._drag.y()
        self._drag=now
        self.yaw += dx*.009
        self.pitch=max(math.radians(-5),min(math.radians(75),self.pitch+dy*.007))
        self.update()

    def mouseReleaseEvent(self,e):
        if e.button()==Qt.LeftButton:
            self._drag=None
            self.setCursor(Qt.OpenHandCursor)

    def mouseDoubleClickEvent(self,e):
        self.resetCamera()

    def wheelEvent(self,e):
        step=e.angleDelta().y()/120.0
        self.zoom=max(.55,min(2.0,self.zoom*(1.0+step*.09)))
        self.update()

    @staticmethod
    def _shade(color,factor):
        c=QColor(color)
        return c.lighter(int(100*factor)) if factor>=1 else c.darker(int(100/max(factor,.01)))

    def paintEvent(self,e):
        p=QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        p.setRenderHint(QPainter.TextAntialiasing)

        # background
        p.fillRect(self.rect(),QColor("#eef4fa"))
        grad_top=QColor("#fafdff")
        p.fillRect(QRectF(0,0,self.width(),self.height()*.54),grad_top)

        if not self.d:
            p.setPen(QColor("#64748b"))
            p.drawText(self.rect(),Qt.AlignCenter,"3D CRANE VIEW")
            return

        W=max(.4,float(self.d["W"]))
        WB=max(.5,float(self.d["WB"]))
        L=max(.1,float(self.d["L"]))
        H=max(.2,float(self.d["H"]))
        xC=float(self.d["xC"])
        th=math.radians(self._display_angle)

        # scene/camera scale
        scene=max(2.0,WB*1.55,L*1.55,W*1.8,H*1.5)
        scale=min(self.width()/scene,self.height()/scene)*.47*self.zoom
        cx=self.width()*.49
        cy=self.height()*.63
        cyaw=math.cos(self.yaw); syaw=math.sin(self.yaw)
        cp=math.cos(self.pitch); sp=math.sin(self.pitch)

        def project(v):
            x,y,z=v
            xr=cyaw*x-syaw*y
            depth=syaw*x+cyaw*y
            vertical=z*cp-depth*sp
            return QPointF(cx+xr*scale,cy-vertical*scale), depth*cp+z*sp

        def line3(a,b,color="#334155",width=2,style=Qt.SolidLine,alpha=255):
            A,_=project(a);B,_=project(b)
            c=QColor(color);c.setAlpha(alpha)
            pen=QPen(c,width,style,Qt.RoundCap,Qt.RoundJoin)
            p.setPen(pen);p.drawLine(A,B)

        def poly3(points,color="#dce5ee",edge="#334155",alpha=255):
            pts=[project(v) for v in points]
            qpoly=QPolygonF([q for q,_ in pts])
            fill=QColor(color);fill.setAlpha(alpha)
            ec=QColor(edge);ec.setAlpha(alpha)
            p.setBrush(fill);p.setPen(QPen(ec,1.1))
            p.drawPolygon(qpoly)

        def cuboid(center,size,color,edge="#334155",yaw=0.0,alpha=255):
            x0,y0,z0=center; sx,sy,sz=size
            c=math.cos(yaw);s=math.sin(yaw)
            verts=[]
            for dx,dy,dz in [(-1,-1,-1),(1,-1,-1),(1,1,-1),(-1,1,-1),
                             (-1,-1,1),(1,-1,1),(1,1,1),(-1,1,1)]:
                lx=dx*sx/2;ly=dy*sy/2
                rx=lx*c-ly*s; ry=lx*s+ly*c
                verts.append((x0+rx,y0+ry,z0+dz*sz/2))
            faces=[(0,1,2,3),(4,7,6,5),(0,4,5,1),(1,5,6,2),(2,6,7,3),(3,7,4,0)]
            shaded=[.72,1.10,.84,.94,.78,1.0]
            sortable=[]
            for i,face in enumerate(faces):
                depth=sum(project(verts[j])[1] for j in face)/4
                sortable.append((depth,i,face))
            for _,i,face in sorted(sortable,reverse=True):
                fc=self._shade(color,shaded[i])
                fc.setAlpha(alpha)
                pts=QPolygonF([project(verts[j])[0] for j in face])
                ec=QColor(edge);ec.setAlpha(alpha)
                p.setPen(QPen(ec,1.1));p.setBrush(fc);p.drawPolygon(pts)

        def ring3(center,r,z,color,width=2,style=Qt.SolidLine,alpha=255,start=-180,end=180):
            prev=None
            for deg in range(start,end+1,4):
                a=math.radians(deg)
                pt=(center[0]+r*math.cos(a),center[1]+r*math.sin(a),z)
                if prev is not None:
                    line3(prev,pt,color,width,style,alpha)
                prev=pt

        # soft ground shadow
        shadow=[]
        for deg in range(0,361,12):
            a=math.radians(deg)
            shadow.append((math.cos(a)*max(WB,1.1)*.82,math.sin(a)*W*.82,.008))
        pts=[project(v)[0] for v in shadow]
        sh=QColor("#33516b");sh.setAlpha(24)
        p.setPen(Qt.NoPen);p.setBrush(sh);p.drawPolygon(QPolygonF(pts))

        # ground grid
        grid=max(.5,round(scene/5,1))
        lim=scene*.95
        for i in range(-5,6):
            v=i*grid
            line3((-lim,v,0),(lim,v,0),"#c8d5e3",1,Qt.SolidLine,130)
            line3((v,-lim,0),(v,lim,0),"#c8d5e3",1,Qt.SolidLine,130)

        # coordinate axes
        line3((0,0,.02),(.42,0,.02),"#d94841",3)
        line3((0,0,.02),(0,.42,.02),"#2f9e44",3)
        line3((0,0,.02),(0,0,.42),"#1971c2",3)

        # vehicle
        half_body=max(.78,WB*.68)
        body_w=max(.62,W*.82)
        cuboid((0,0,.27),(half_body*2,body_w,.24),"#536170","#263746")
        cuboid((0,0,.43),(half_body*1.72,body_w*.92,.12),"#758493","#2d3748")
        # deck slats
        for x in [(-half_body*.55),(-half_body*.25),(.05*half_body),(.35*half_body),(.65*half_body)]:
            line3((x,-body_w*.43,.50),(x,body_w*.43,.50),"#aeb9c5",1,Qt.SolidLine,180)

        # wheels: rear hub wheels larger, front supports smaller
        rear=-WB/2; front=WB/2
        wheel_data=[(rear,-W/2,.22),(rear,W/2,.22),(front,-W/2,.16),(front,W/2,.16)]
        for x,y,r in wheel_data:
            q,_=project((x,y,r))
            rx=max(7,r*scale*.62); ry=max(11,r*scale*.95)
            p.setPen(QPen(QColor("#151b23"),2));p.setBrush(QColor("#242b34"))
            p.drawEllipse(q,rx,ry)
            p.setBrush(QColor("#8794a2"));p.setPen(QPen(QColor("#c7d0da"),1))
            p.drawEllipse(q,rx*.42,ry*.42)

        # crane mount and slewing bearing
        bx=rear+xC
        base_z=.56
        cuboid((bx,0,base_z),(0.38,0.38,.16),"#273444","#111827")
        ring3((bx,0,0),.26,base_z+.09,"#3b82f6",3,Qt.SolidLine,220)

        # permitted rotation arc + end stops
        ring3((bx,0,0),max(.48,L*.58),base_z+.13,"#60a5fa",2,Qt.DashLine,145,-90,90)
        for deg,label in [(-90,"-90°"),(0,"0°"),(90,"+90°")]:
            a=math.radians(deg)
            rr=max(.48,L*.58)
            pt=(bx+rr*math.cos(a),rr*math.sin(a),base_z+.13)
            q,_=project(pt)
            p.setPen(QColor("#2c5d96"));p.setFont(QFont("",8,QFont.Bold))
            p.drawText(q+QPointF(4,-4),label)

        # column
        column_z=base_z+.16+H/2
        cuboid((bx,0,column_z),(.18,.18,H),"#364657","#1f2937")

        # slewing head
        top=base_z+.16+H
        cuboid((bx,0,top),(.28,.28,.16),"#1f2f3f","#111827")

        # ghost boom positions to explain rotation envelope
        for ghost_deg in (-90,0,90):
            ga=math.radians(ghost_deg)
            gx=bx+L*math.cos(ga);gy=L*math.sin(ga)
            line3((bx,0,top),(gx,gy,top),"#8aa4bd",5,Qt.DashLine,62)

        # active boom as a true oriented 3D beam
        boom_center=(bx+(L/2)*math.cos(th),(L/2)*math.sin(th),top)
        cuboid(boom_center,(L,.15,.15),"#e87518","#7c3d08",yaw=th)

        # boom inner highlight
        ex=bx+L*math.cos(th);ey=L*math.sin(th)
        line3((bx,0,top+.045),(ex,ey,top+.045),"#ffc078",2,Qt.SolidLine,230)

        # winch rope, hook and basket/load
        hook_z=max(.37,top-.70)
        line3((ex,ey,top-.04),(ex,ey,hook_z),"#252b33",2)
        hq,_=project((ex,ey,hook_z))
        p.setPen(QPen(QColor("#d9480f"),3));p.setBrush(Qt.NoBrush)
        p.drawEllipse(hq+QPointF(0,5),6,10)
        cuboid((ex,ey,max(.12,hook_z-.18)),(.38,.28,.16),"#b9c5d0","#475569",yaw=th,alpha=235)

        # crane pivot axis highlight
        line3((bx,0,base_z+.08),(bx,0,top+.20),"#3b82f6",2,Qt.DashLine,185)

        # current-angle marker
        arm_r=max(.48,L*.58)
        marker=(bx+arm_r*math.cos(th),arm_r*math.sin(th),base_z+.13)
        mq,_=project(marker)
        p.setBrush(QColor("#2463eb"));p.setPen(QPen(QColor("white"),2));p.drawEllipse(mq,6,6)

        # labels / HUD
        p.setPen(QColor("#102a43"))
        p.setFont(QFont("",11,QFont.Bold))
        p.drawText(18,29,"INTERACTIVE 3D CRANE VIEW")
        p.setFont(QFont("",8))
        p.setPen(QColor("#60758b"))
        p.drawText(18,49,"ลากเมาส์ = หมุนมุมมอง  •  Scroll = Zoom  •  Double-click = Reset")

        # top-right info panel
        panel=QRectF(self.width()-245,16,226,124)
        p.setPen(QPen(QColor("#cbd8e6"),1))
        p.setBrush(QColor(255,255,255,235))
        p.drawRoundedRect(panel,11,11)
        p.setPen(QColor("#17324d"));p.setFont(QFont("",9,QFont.Bold))
        p.drawText(panel.x()+13,panel.y()+24,"CRANE LIVE DATA")
        p.setFont(QFont("",8))
        rows=[
            ("Rotation",f"{self._display_angle:+.1f}°"),
            ("Boom length",f"{L:.2f} m"),
            ("Column height",f"{H:.2f} m"),
            ("Track width",f"{W:.2f} m"),
        ]
        yy=panel.y()+47
        for name,val in rows:
            p.setPen(QColor("#60758b"));p.drawText(panel.x()+13,yy,name)
            p.setPen(QColor("#17324d"));p.setFont(QFont("",8,QFont.Bold))
            p.drawText(QRectF(panel.x()+105,yy-13,105,18),Qt.AlignRight|Qt.AlignVCenter,val)
            p.setFont(QFont("",8));yy+=20

        # current angle badge
        badge=QRectF(18,self.height()-52,142,34)
        p.setPen(Qt.NoPen);p.setBrush(QColor("#2463eb"));p.drawRoundedRect(badge,10,10)
        p.setPen(QColor("white"));p.setFont(QFont("",10,QFont.Bold))
        p.drawText(badge,Qt.AlignCenter,f"CRANE  {self._display_angle:+.1f}°")

def spin(v,a,b,s=.1,d=2):
    x=QDoubleSpinBox();x.setRange(a,b);x.setValue(v);x.setSingleStep(s);x.setDecimals(d);return x


def choose_ui_font_family():
    """Pick a font with reliable Thai shaping on Windows/Linux."""
    try:
        families=set(QFontDatabase.families())
    except Exception:
        families=set()
    for candidate in ("Leelawadee UI","Tahoma","Noto Sans Thai","Segoe UI Variable","Segoe UI","Arial"):
        if candidate in families:
            return candidate
    return QApplication.font().family()


def add_soft_shadow(widget, blur=22, y=5, alpha=30):
    """Small reusable shadow for cards; ignored gracefully by Qt if unsupported."""
    try:
        effect=QGraphicsDropShadowEffect(widget)
        effect.setBlurRadius(blur)
        effect.setOffset(0,y)
        effect.setColor(QColor(20,45,75,alpha))
        widget.setGraphicsEffect(effect)
    except Exception:
        pass


def make_chip(text, bg="#eaf2ff", fg="#2457a6"):
    label=QLabel(text)
    label.setAlignment(Qt.AlignCenter)
    label.setStyleSheet(f"background:{bg};color:{fg};border-radius:11px;padding:5px 11px;font-size:9.4pt;font-weight:800;")
    label.setSizePolicy(QSizePolicy.Fixed,QSizePolicy.Fixed)
    return label


def make_page_header(title, subtitle, back_callback, tag_text=None, tag_bg="#eaf2ff", tag_fg="#2457a6", action_text=None, action_callback=None):
    """Readable V51 page header with clear hierarchy and compact actions."""
    frame=QFrame();frame.setObjectName("topHeader");frame.setMinimumHeight(98);add_soft_shadow(frame,20,4,22)
    row=QHBoxLayout(frame);row.setContentsMargins(18,14,18,14);row.setSpacing(14)
    back=QPushButton("⌂  หน้าแรก");back.setObjectName("secondaryButton");back.setMinimumWidth(112);back.clicked.connect(back_callback);row.addWidget(back)
    col=QVBoxLayout();col.setSpacing(3)
    h=QLabel(title);hf=QFont();hf.setPointSize(16);hf.setBold(True);h.setFont(hf);h.setStyleSheet("color:white;background:transparent;")
    sh=QLabel(subtitle);sh.setWordWrap(True);sh.setStyleSheet("color:#d9ebf8;font-size:10pt;font-weight:650;background:transparent;")
    col.addWidget(h);col.addWidget(sh);row.addLayout(col,1)
    if tag_text:
        row.addWidget(make_chip(tag_text,tag_bg,tag_fg))
    if action_text and action_callback:
        action=QPushButton(action_text);action.setObjectName("primaryButton");action.setMinimumWidth(178);action.clicked.connect(action_callback);row.addWidget(action)
    return frame



class ModeCardButton(QPushButton):
    """V51 home module card: larger text, simpler hierarchy, clear click target."""
    def __init__(self,title,subtitle,badge="01",accent="#2463eb",parent=None):
        super().__init__("",parent)
        self.setObjectName("modeCard")
        self.setFixedHeight(158)
        self.setSizePolicy(QSizePolicy.Expanding,QSizePolicy.Fixed)
        self.setCursor(Qt.PointingHandCursor)
        self.setStyleSheet(f"""
            QPushButton#modeCard {{
                background:#ffffff; border:1px solid #d8e3ed; border-radius:15px; padding:0;
                min-height:158px; max-height:158px;
            }}
            QPushButton#modeCard:hover {{ background:#fbfdff; border:2px solid {accent}; }}
            QPushButton#modeCard:pressed {{ background:#f2f7fb; }}
        """)
        add_soft_shadow(self,20,4,22)

        outer=QVBoxLayout(self);outer.setContentsMargins(0,0,0,0);outer.setSpacing(0)
        accent_line=QFrame();accent_line.setFixedHeight(5)
        accent_line.setStyleSheet(f"background:{accent};border-top-left-radius:15px;border-top-right-radius:15px;")
        accent_line.setAttribute(Qt.WA_TransparentForMouseEvents,True);outer.addWidget(accent_line)

        body=QVBoxLayout();body.setContentsMargins(18,14,18,15);body.setSpacing(7);outer.addLayout(body)
        top=QHBoxLayout();top.setSpacing(8)
        badge_label=QLabel(badge);badge_label.setAlignment(Qt.AlignCenter);badge_label.setFixedSize(40,31)
        badge_label.setStyleSheet(f"background:{accent};color:white;border-radius:9px;font-weight:900;font-size:9.3pt;")
        status=QLabel("MODULE");status.setStyleSheet("color:#8795a6;font-size:8.5pt;font-weight:800;background:transparent;")
        top.addWidget(badge_label);top.addWidget(status);top.addStretch(1);body.addLayout(top)

        title_label=QLabel(title);title_label.setWordWrap(True)
        tf=QFont();tf.setPointSize(13.5);tf.setBold(True);title_label.setFont(tf)
        title_label.setStyleSheet("color:#102f4a;background:transparent;")
        sub_label=QLabel(subtitle);sub_label.setWordWrap(True)
        sf=QFont();sf.setPointSize(9.6);sf.setWeight(QFont.DemiBold);sub_label.setFont(sf)
        sub_label.setStyleSheet("color:#52697e;background:transparent;")
        body.addWidget(title_label);body.addWidget(sub_label);body.addStretch(1)

        action=QLabel("เปิดโมดูล  →");action.setStyleSheet(f"color:{accent};font-size:9.4pt;font-weight:850;background:transparent;")
        body.addWidget(action)
        for x in (accent_line,badge_label,status,title_label,sub_label,action):
            x.setAttribute(Qt.WA_TransparentForMouseEvents,True)



class TorqueFBDWidget(QWidget):
    """Engineering FBD for a vehicle climbing an incline."""
    def __init__(self,owner):
        super().__init__(); self.o=owner; self.setMinimumHeight(460)

    def arrow(self,p,a,b,color,label):
        A=QPointF(float(a[0]),float(a[1])); B=QPointF(float(b[0]),float(b[1]))
        p.setPen(QPen(QColor(color),2)); p.drawLine(A,B)
        ang=math.atan2(B.y()-A.y(),B.x()-A.x()); L=9
        for da in (2.55,-2.55):
            p.drawLine(B,QPointF(B.x()+L*math.cos(ang+da),B.y()+L*math.sin(ang+da)))
        p.setPen(QColor(color)); p.drawText(QPointF(B.x()+5,B.y()-5),label)

    def box(self,p,r,title):
        p.setBrush(QColor("#fbfdff")); p.setPen(QPen(QColor("#cbd5e1"),1)); p.drawRoundedRect(r,6,6)
        p.setPen(QColor("#17324d")); p.setFont(QFont("Arial",9,QFont.Bold)); p.drawText(QPointF(r.x()+9,r.y()+20),title)

    def paintEvent(self,e):
        p=QPainter(self); p.setRenderHint(QPainter.Antialiasing); p.fillRect(self.rect(),QColor("white"))
        q=self.o.torque_results(); W=float(self.width()); H=float(self.height())
        gap=9; noteH=120; pw=(W-3*gap)/2; ph=(H-noteH-3*gap)/2
        R=[QRectF(gap,gap,pw,ph),QRectF(2*gap+pw,gap,pw,ph),
           QRectF(gap,2*gap+ph,pw,ph),QRectF(2*gap+pw,2*gap+ph,pw,ph)]
        titles=["A. COMPLETE VEHICLE FBD","B. WEIGHT DECOMPOSITION",
                "C. EQUILIBRIUM / MOTION EQUATIONS","D. DRIVEN WHEEL FBD"]
        for r,t in zip(R,titles): self.box(p,r,t)

        al=math.radians(q["deg"]); ux=math.cos(al); uy=-math.sin(al); nx=-math.sin(al); ny=-math.cos(al)

        # A - external forces only
        r=R[0]; x0=r.x()+30; y0=r.bottom()-35; x1=r.right()-22
        rise=min(80,(x1-x0)*math.tan(al)); y1=y0-rise
        p.setPen(QPen(QColor("#64748b"),2)); p.drawLine(QPointF(x0,y0),QPointF(x1,y1))
        cx=(x0+x1)/2; cy=(y0+y1)/2-30
        p.save(); p.translate(cx,cy); p.rotate(-q["deg"])
        p.setBrush(QColor("#dce5ed")); p.setPen(QPen(QColor("#334155"),2)); p.drawRect(QRectF(-62,-22,124,44))
        p.setBrush(QColor("#374151")); p.drawEllipse(QRectF(-50,13,24,24)); p.drawEllipse(QRectF(27,13,24,24)); p.restore()
        self.arrow(p,(cx,cy),(cx,cy+75),"#111827","W = mg")
        self.arrow(p,(cx,cy+20),(cx+70*ux,cy+20+70*uy),"#2563eb","F_drive")
        self.arrow(p,(cx-3,cy+29),(cx-58*ux,cy+29-58*uy),"#b45309","F_r")
        self.arrow(p,(cx,cy+26),(cx+58*nx,cy+26+58*ny),"#16a34a","N")
        p.setPen(QColor("#475569")); p.drawText(QPointF(r.x()+9,r.bottom()-8),f"alpha={q['deg']:.1f} deg, a={q['a']:.3f} m/s^2")

        # B - decomposition only
        r=R[1]; cx=r.center().x(); cy=r.center().y()-4
        self.arrow(p,(cx,cy),(cx,cy+78),"#111827","W = mg")
        self.arrow(p,(cx,cy),(cx-66*ux,cy-66*uy),"#dc2626",f"mg sin(a)={q['Fg']:.0f} N")
        wn=q["m"]*9.81*math.cos(al)
        self.arrow(p,(cx,cy),(cx+54*(-nx),cy+54*(-ny)),"#7c3aed",f"mg cos(a)={wn:.0f} N")
        p.setPen(QColor("#475569")); p.drawText(QPointF(r.x()+9,r.bottom()-8),"W is resolved into parallel and normal components.")

        # C - equations
        r=R[2]; x=r.x()+14; y=r.y()+47
        p.setPen(QColor("#17324d")); p.setFont(QFont("Arial",9,QFont.Bold))
        lines=["x-axis parallel to slope (+ uphill):","Sum F_x = m a",
               "F_drive - mg sin(alpha) - F_r = m a",
               f"F_drive(calc) = {q['Fsum']:.1f} N",
               f"F_design = F_drive x SF = {q['Fdesign']:.1f} N","",
               "y-axis normal to slope:","Sum F_y = 0",
               "N_total - mg cos(alpha) = 0",f"N_total = {q['Ntotal']:.1f} N"]
        for line in lines: p.drawText(QPointF(x,y),line); y+=18

        # D - wheel
        r=R[3]; cx=r.center().x(); cy=r.center().y()+5; rad=min(55,pw*.18)
        p.setBrush(QColor("#303841")); p.setPen(QPen(QColor("#111827"),2)); p.drawEllipse(QPointF(cx,cy),rad,rad)
        p.setBrush(QColor("#d7dee6")); p.drawEllipse(QPointF(cx,cy),rad*.43,rad*.43)
        self.arrow(p,(cx,cy),(cx,cy-90),"#16a34a","N_d")
        self.arrow(p,(cx,cy+rad),(cx+90,cy+rad),"#2563eb","F_t")
        self.arrow(p,(cx,cy),(cx,cy+88),"#111827","W_wheel")
        p.setPen(QPen(QColor("#7c3aed"),3)); p.drawArc(QRectF(cx-rad*1.25,cy-rad*1.25,rad*2.5,rad*2.5),35*16,110*16)
        p.setPen(QColor("#7c3aed")); p.drawText(QPointF(r.x()+10,r.y()+45),f"T_wheel = F_t r = {q['T']:.1f} N.m")
        p.setPen(QColor("#475569")); p.drawText(QPointF(r.x()+10,r.bottom()-25),f"Prelim F_t = F_design/n = {q['Fmotor']:.1f} N")
        p.drawText(QPointF(r.x()+10,r.bottom()-8),"No-slip: abs(F_t) <= mu N_d")

        y=H-noteH+15; p.setPen(QColor("#17324d")); p.setFont(QFont("Arial",9,QFont.Bold))
        p.drawText(QPointF(12,y),"ENGINEERING FBD RULES")
        p.setFont(QFont("Arial",8)); p.setPen(QColor("#475569"))
        notes=["1) Complete FBD contains external forces only: W, N, traction/drive force, rolling resistance.",
               "2) mg sin(alpha) and mg cos(alpha) are components of W; do not double-count them with W in the same equation.",
               "3) ma is not an extra external force in a Newton FBD. It belongs in Sum F = ma.",
               "4) Real traction limit requires driven-wheel normal load N_d from CG and load transfer, not total N alone.",
               "5) Final motor selection must also check torque-speed curve, controller current, tire-road mu and transient loads."]
        for i,t in enumerate(notes): p.drawText(QPointF(12,y+18+i*16),t)


class TorqueGraphWidget(QWidget):
    def __init__(self,owner):
        super().__init__();self.o=owner;self.setMinimumHeight(360)
    def paintEvent(self,e):
        p=QPainter(self);p.setRenderHint(QPainter.Antialiasing);p.fillRect(self.rect(),QColor("white"))
        W=self.width();H=self.height();left=75;right=35;top=50;bottom=65
        p.setPen(QColor("#17324d"));p.setFont(QFont("Arial",12,QFont.Bold));p.drawText(left,28,"Required Wheel Torque vs Slope")
        # compute 0..30 degrees
        vals=[self.o.torque_results(slope=x)["T"] for x in range(31)]
        ymax=max(vals)*1.15 if max(vals)>0 else 1
        p.setPen(QPen(QColor("#94a3b8"),1));p.drawLine(left,H-bottom,W-right,H-bottom);p.drawLine(left,top,left,H-bottom)
        pts=[]
        for x,v in enumerate(vals):
            px=left+(W-left-right)*x/30;py=H-bottom-(H-top-bottom)*v/ymax;pts.append(QPointF(px,py))
        p.setPen(QPen(QColor("#2488ee"),3))
        for a,b in zip(pts[:-1],pts[1:]):p.drawLine(a,b)
        p.setPen(QColor("#475569"))
        for x in [0,5,10,15,20,25,30]:
            px=left+(W-left-right)*x/30;p.drawText(int(px-8),H-bottom+22,str(x)+"°")
        for i in range(5):
            val=ymax*i/4;py=H-bottom-(H-top-bottom)*i/4;p.drawText(8,int(py+4),f"{val:.0f} N·m")
        p.drawText(left,H-15,"Slope angle / ความชัน")

class App(QMainWindow):
    updateTaskFinished=Signal(object)
    updateProgressChanged=Signal(int)
    def __init__(self):
        super().__init__();self.setStyleSheet(APP_STYLE);self.setWindowTitle(f"{APP_NAME} — V{APP_VERSION}"); self.setWindowIcon(QIcon(str(resource_path("assets/CraneEngineeringTool.ico"))));self.setMinimumSize(1024,650);self.resize(1440,860)
        app_font=QFont(choose_ui_font_family());app_font.setPointSizeF(11.5);app_font.setStyleStrategy(QFont.PreferAntialias);self.setFont(app_font)
        self.tabs=QTabWidget()
        self.tabs.tabBar().hide();self.setCentralWidget(self.tabs)
        self.make_home();self.make_torque();self.make_electrical();self.make_winch();self.make_crane();self.make_slope();self.make_fbd();self.make_components();self.make_worstcase();self.make_calc_steps();self.make_design();self.make_graph();self.make_report();self.make_thai_help();self.make_stability_hub();self.make_project_tools();self.make_safety_logic_simulator();self.make_variable_dictionary_page();self.setup_navigation_dock();self.setup_status_bar_ui();self.setup_dynamic_tabs()
        self.calc_all()
        # Automatically restore the most recently entered values.
        self.restore_last_values(silent=True)
        self.setup_easy_autosave()

        # Built-in updater: all network/file work happens in a background thread.
        self.updateTaskFinished.connect(self._handle_update_task_result)
        self.updateProgressChanged.connect(self._set_update_progress)
        self.pending_update_manifest=None
        self._update_busy=False
        self._update_auto_requested=False
        QTimer.singleShot(1800,self.auto_check_for_update)


    def _thai_formula_text(self, title):
        """Return a plain-Thai equation before the engineering-symbol equation."""
        t = str(title)
        rules = [
            ("รอบดรัม", "รอบดรัม = รอบมอเตอร์ ÷ อัตราทดเกียร์"),
            ("ความเร็วสลิงที่วัด/กรอก", "ความเร็วสลิง = ค่าความเร็วที่วัดจริง หรือค่าที่ผู้ผลิตระบุ"),
            ("ความเร็วสลิง", "ความเร็วสลิง = π × เส้นผ่านศูนย์กลางดรัม × รอบดรัม"),
            ("ความเร็วของโหลด", "ความเร็วโหลด = ความเร็วสลิง ÷ จำนวนส่วนสลิงที่รองรับโหลด"),
            ("เวลายกและลด", "เวลา = ระยะยก × 60 ÷ ความเร็วโหลด"),
            ("แรงดึงสลิง", "แรงดึงสลิง = มวลโหลดรวม × g ÷ (จำนวนส่วนสลิง × ประสิทธิภาพรอก)"),
            ("แรงบิดที่ดรัม", "แรงบิดดรัม = แรงดึงสลิง × รัศมีดรัม"),
            ("แรงบิดที่เพลามอเตอร์", "แรงบิดเพลามอเตอร์ = แรงบิดดรัม ÷ (อัตราทดเกียร์ × ประสิทธิภาพเกียร์)"),
            ("กำลังกลที่ดรัม", "กำลังกลที่ดรัม = แรงดึงสลิง × ความเร็วสลิง"),
            ("แรงยกออกแบบ", "แรงยกออกแบบ = แรงยก × Safety Factor"),
            ("แรงยก", "แรงยก = มวลโหลดรวม × g"),
            ("พลังงานกลขั้นต่ำในการยก", "พลังงานกลในการยก = มวลโหลดรวม × g × ความสูงยก"),
            ("เวลายกขึ้น", "เวลายกขึ้น = ความสูงยก × 60 ÷ ความเร็วโหลดขาขึ้น"),
            ("เวลาลดลง", "เวลาลดลง = ความสูงยก × 60 ÷ ความเร็วโหลดขาลง"),
            ("กำลังไฟฟ้าขณะยก", "กำลังไฟฟ้าขณะยก = แรงดันแบตเตอรี่ × กระแสขณะยก"),
            ("พลังงานไฟฟ้าขณะยก", "พลังงานขณะยก = แรงดันแบตเตอรี่ × กระแสขณะยก × เวลายก ÷ 3600"),
            ("กำลังและพลังงานขณะลด", "กำลังขณะลด = แรงดันแบตเตอรี่ × กระแสขณะลด<br>พลังงานขณะลด = กำลังขณะลด × เวลาลด ÷ 3600"),
            ("พลังงานรวมตามจำนวนรอบ", "พลังงานรวม = (พลังงานยกขึ้น + พลังงานลดลง) × จำนวนรอบ"),
            ("ความจุแบตเตอรี่ 12 V", "ความจุแบตเตอรี่ (Ah) = พลังงานรวม × (1 + พลังงานสำรอง) ÷ (แรงดันแบตเตอรี่ × DoD)"),
            ("เวลาทำงานสะสมของวินช์", "เวลาทำงานรวม = (เวลายกขึ้น + เวลาลดลง) × จำนวนรอบ"),
            ("แปลงความเร็ว", "ความเร็ว (m/s) = ความเร็ว (km/h) ÷ 3.6"),
            ("เวลาและจำนวนรอบ", "ระยะต่อรอบ = 2 × ระยะเที่ยวเดียว<br>เวลาวิ่งต่อรอบ = ระยะต่อรอบ ÷ ความเร็ว<br>จำนวนรอบ = เวลาทำงานทั้งหมด ÷ (เวลาวิ่งต่อรอบ + เวลาหยุดต่อรอบ)"),
            ("แรงต้านและกำลังบนทางราบ", "แรงต้านการกลิ้ง = Crr × มวลรวมรถ × g<br>กำลังทางราบ = แรงต้านการกลิ้ง × ความเร็วรถ"),
            ("แรงและกำลังขึ้นทางลาด", "แรงจากความชัน = มวลรวมรถ × g × sin(มุมทางลาด)<br>แรงต้านการกลิ้งบนทางลาด = Crr × มวลรวมรถ × g × cos(มุมทางลาด)<br>แรงขึ้นลาดรวม = แรงจากความชัน + แรงต้านการกลิ้งบนทางลาด<br>กำลังขึ้นลาด = แรงขึ้นลาดรวม × ความเร็วรถ"),
            ("พลังงานออกตัว", "พลังงานจลน์ = ½ × มวลรวมรถ × ความเร็ว²<br>พลังงานออกตัวต่อรอบ = พลังงานจลน์ × จำนวนครั้งออกตัว ÷ 3600"),
            ("พลังงานกลรวมและไฟฟ้าประมาณ", "พลังงานกลรวม = (พลังงานทางราบ + พลังงานขึ้นลาด + พลังงานออกตัว) × จำนวนรอบ<br>พลังงานไฟฟ้าขับเคลื่อน = พลังงานกลรวม ÷ ประสิทธิภาพระบบขับ"),
            ("กรณี Worst-case ตอนขึ้นลาด", "กำลังไฟจากแบตเตอรี่กรณีหนักสุด = กำลังพิกัดมอเตอร์ต่อหนึ่งตัว × จำนวนมอเตอร์ ÷ ประสิทธิภาพขาขึ้น"),
            ("พลังงานโหลดทั้งหมด", "พลังงานอุปกรณ์เสริม = กำลังอุปกรณ์เสริม × เวลาทำงาน<br>พลังงานโหลดรวม = พลังงานขับเคลื่อน + พลังงานอุปกรณ์เสริม"),
            ("ความจุแบตเตอรี่หลังเผื่อ DoD และ Reserve", "พลังงานพิกัดแบตเตอรี่ = พลังงานโหลดรวม ÷ DoD<br>พลังงานออกแบบ = พลังงานพิกัดแบตเตอรี่ × (1 + พลังงานสำรอง)<br>ความจุแบตเตอรี่ (Ah) = พลังงานออกแบบ ÷ แรงดันแบตเตอรี่"),
            ("กระแสและ BMS", "กระแสแบตเตอรี่ = กำลังไฟฟ้า ÷ แรงดันแบตเตอรี่"),
            ("แปลงขนาดล้อเป็นรัศมี", "เส้นผ่านศูนย์กลางล้อ (m) = ขนาดล้อ (inch) × 0.0254<br>รัศมีล้อ = เส้นผ่านศูนย์กลางล้อ ÷ 2"),
            ("แปลงความเร็วและหาความเร่ง", "ความเร็ว (m/s) = ความเร็ว (km/h) ÷ 3.6<br>ความเร่ง = ความเร็ว ÷ เวลาเร่ง"),
            ("แรงจากความชัน", "แรงจากความชัน = มวลรวมรถ × g × sin(มุมทางลาด)"),
            ("แรงต้านการกลิ้ง", "แรงต้านการกลิ้ง = Crr × มวลรวมรถ × g × cos(มุมทางลาด)"),
            ("แรงสำหรับเร่งรถ", "แรงเร่ง = มวลรวมรถ × ความเร่ง"),
            ("แรงรวมและแรงออกแบบ", "แรงรวม = แรงจากความชัน + แรงต้านการกลิ้ง + แรงเร่ง<br>แรงออกแบบ = แรงรวม × Safety Factor"),
            ("แรงต่อมอเตอร์", "แรงต่อมอเตอร์ = แรงออกแบบรวม ÷ จำนวนมอเตอร์ขับ"),
            ("แรงบิดต่อล้อ", "แรงบิดที่ล้อ = แรงต่อมอเตอร์ × รัศมีล้อ"),
            ("รอบล้อและความเร็วเชิงมุม", "รอบล้อ = ความเร็วรถ ÷ เส้นรอบวงล้อ × 60<br>ความเร็วเชิงมุม = 2π × รอบล้อ ÷ 60"),
            ("กำลังกล", "กำลังกล = แรง × ความเร็ว = แรงบิด × ความเร็วเชิงมุม"),
            ("กำลังไฟฟ้าและกระแสแบตเตอรี่", "กำลังไฟฟ้า = กำลังกล ÷ ประสิทธิภาพระบบขับ<br>กระแสแบตเตอรี่ = กำลังไฟฟ้า ÷ แรงดันแบตเตอรี่"),
            ("ขีดจำกัดแรงยึดเกาะ", "แรงกดตั้งฉาก = มวลรวมรถ × g × cos(มุมทางลาด)<br>แรงยึดเกาะสูงสุด = สัมประสิทธิ์แรงเสียดทาน × แรงกดตั้งฉาก"),
            ("ตรวจมอเตอร์และ Controller", "Margin = ค่าพิกัดอุปกรณ์ ÷ ค่าที่ระบบต้องการ"),
            ("แรงโหลดออกแบบ", "แรงโหลดออกแบบ = Dynamic Factor × มวลโหลด × g"),
            ("ตำแหน่งโหลดด้านข้างและแนวคว่ำ", "ระยะโหลดด้านข้าง = |ความยาวแขน × sin(มุมเครน)|<br>ตำแหน่งแนวคว่ำ = ความกว้างฐานล้อ ÷ 2<br>แขนโมเมนต์โหลด = ระยะโหลดด้านข้าง − ตำแหน่งแนวคว่ำ"),
            ("โมเมนต์คว่ำด้านข้าง", "โมเมนต์คว่ำ = แรงโหลด × ระยะแขนโมเมนต์โหลด + น้ำหนักแขนเครน × g × ระยะแขนโมเมนต์ของแขน"),
            ("โมเมนต์ต้านและ SF ด้านข้าง", "มวลต้าน = มวลรวม − มวลโหลด − มวลแขนเครน<br>โมเมนต์ต้าน = มวลต้าน × g × (ความกว้างฐานล้อ ÷ 2)<br>Safety Factor ด้านข้าง = โมเมนต์ต้าน ÷ โมเมนต์คว่ำ"),
            ("ตำแหน่งตามแนวยาว", "ตำแหน่งเครน = ตำแหน่งเพลาหลัง + ระยะเครนจากเพลาหลัง<br>ตำแหน่งโหลด = ตำแหน่งเครน + ความยาวแขน × cos(มุมเครน)<br>ตำแหน่ง CG แขน = ตำแหน่งเครน + ครึ่งความยาวแขน × cos(มุมเครน)"),
            ("โมเมนต์คว่ำหน้า", "Safety Factor ด้านหน้า = ผลรวมโมเมนต์ต้านรอบเพลาหน้า ÷ ผลรวมโมเมนต์คว่ำรอบเพลาหน้า"),
            ("โมเมนต์คว่ำหลัง", "Safety Factor ด้านหลัง = ผลรวมโมเมนต์ต้านรอบเพลาหลัง ÷ ผลรวมโมเมนต์คว่ำรอบเพลาหลัง"),
            ("รถวิ่งบนทางลาด", "ระยะเลื่อนจากความชัน = ความสูง CG × tan(มุมทางลาด)<br>ระยะเลื่อนจากความเร่ง = ความสูง CG × ความเร่ง ÷ g<br>ระยะเลื่อนรวม = ระยะจากความชัน + ระยะจากความเร่ง"),
            ("มวลรวมและ Combined CG", "มวลรวม = ผลรวมมวลทุกชิ้น<br>ตำแหน่ง CG = ผลรวม(มวลแต่ละชิ้น × ตำแหน่งแต่ละชิ้น) ÷ มวลรวม"),
            ("Worst-case search", "Safety Factor ต่ำสุด = ค่าต่ำสุดของ SF ด้านข้าง, ด้านหน้า และด้านหลัง ในทุกมุมเครน"),
            ("Minimum Width / Counterweight", "หาความกว้างฐานล้อต่ำสุดหรือมวลถ่วงต่ำสุดที่ทำให้ Safety Factor ≥ ค่า Safety Factor ที่กำหนด"),
        ]
        for key, text in rules:
            if key in t:
                return text
        return "ผลลัพธ์ = ค่าตัวแปรที่เกี่ยวข้องตามสมการด้านล่าง"

    def inputs(self):
        return dict(mt=self.mt.value(),ml=self.ml.value(),mb=self.mb.value(),W=self.W.value(),L=self.L.value(),H=self.H.value(),
                    th=self.th.value(),kd=self.kd.value(),req=self.req.value(),WB=self.WB.value(),xC=self.xC.value(),
                    xCG=self.xCG.value(),driveXCG=self.driveXCG.value() if hasattr(self,"driveXCG") else self.xCG.value())




    # =====================================================================
    # V51 APPLICATION SHELL — NAVIGATION + READABILITY
    # =====================================================================
    def ui_preferences_path(self):
        base=QStandardPaths.writableLocation(QStandardPaths.AppConfigLocation)
        folder=Path(base) if base else (Path.home()/".CraneVehicleEngineeringTool")
        folder.mkdir(parents=True,exist_ok=True)
        return folder/"ui_preferences.json"

    def load_ui_preferences(self):
        default={"font_scale":1.00,"navigation_visible":True}
        try:
            p=self.ui_preferences_path()
            if not p.exists():return default
            d=json.loads(p.read_text(encoding="utf-8"))
            return {
                "font_scale":max(.90,min(1.30,float(d.get("font_scale",1.00)))),
                "navigation_visible":bool(d.get("navigation_visible",True)),
            }
        except Exception:
            return default

    def save_ui_preferences(self):
        try:
            data={
                "font_scale":float(getattr(self,"uiFontScale",1.0)),
                "navigation_visible":bool(getattr(self,"navDock",None) and self.navDock.isVisible()),
            }
            self.ui_preferences_path().write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding="utf-8")
        except Exception:
            pass

    def _font_scale_css(self,scale):
        s=max(.90,min(1.30,float(scale)))
        return f"""
        QLabel {{ font-size:{10.8*s:.2f}pt; }}
        QPushButton {{ font-size:{10.3*s:.2f}pt; }}
        QDoubleSpinBox,QSpinBox,QComboBox,QLineEdit {{ font-size:{10.8*s:.2f}pt; }}
        QCheckBox,QRadioButton {{ font-size:{10.5*s:.2f}pt; }}
        QTextEdit,QPlainTextEdit {{ font-size:{10.8*s:.2f}pt; }}
        QTableWidget {{ font-size:{10.5*s:.2f}pt; }}
        QHeaderView::section {{ font-size:{10.3*s:.2f}pt; }}
        """

    def apply_ui_scale(self,scale,save=True):
        self.uiFontScale=max(.90,min(1.30,float(scale)))
        font=QFont(choose_ui_font_family())
        font.setPointSizeF(11.5*self.uiFontScale)
        font.setStyleStrategy(QFont.PreferAntialias)
        QApplication.instance().setFont(font)
        self.setFont(font)
        self.setStyleSheet(APP_STYLE+self._font_scale_css(self.uiFontScale))
        if hasattr(self,"fontScaleLabel"):
            self.fontScaleLabel.setText(f"{round(self.uiFontScale*100):d}%")
        if save:self.save_ui_preferences()

    def change_ui_scale(self,delta):
        self.apply_ui_scale(getattr(self,"uiFontScale",1.0)+float(delta))

    def reset_ui_scale(self):
        self.apply_ui_scale(1.0)

    def _make_nav_button(self,key,text,callback):
        b=QPushButton(text);b.setObjectName("navButton");b.setProperty("active",False)
        b.setCursor(Qt.PointingHandCursor);b.clicked.connect(callback)
        self.navButtons[key]=b
        return b

    def _set_active_nav(self,key):
        if not hasattr(self,"navButtons"):return
        for k,b in self.navButtons.items():
            active=(k==key)
            b.setProperty("active",active)
            b.style().unpolish(b);b.style().polish(b);b.update()

    def setup_navigation_dock(self):
        self.navButtons={}
        dock=QDockWidget("",self);self.navDock=dock
        dock.setAllowedAreas(Qt.LeftDockWidgetArea)
        dock.setFeatures(QDockWidget.NoDockWidgetFeatures)
        dock.setFixedWidth(185)
        dock.setTitleBarWidget(QWidget())

        panel=QFrame();panel.setObjectName("navPanel")
        lay=QVBoxLayout(panel);lay.setContentsMargins(11,12,11,12);lay.setSpacing(5)

        brand=QLabel("CVET")
        bf=QFont();bf.setPointSize(17);bf.setBold(True);brand.setFont(bf)
        brand.setStyleSheet("color:#173e61;padding:2px 7px;")
        ver=QLabel(f"Crane Engineering  •  V{APP_VERSION}")
        ver.setWordWrap(True);ver.setStyleSheet("color:#708397;font-size:8.8pt;font-weight:700;padding:0 7px 8px 7px;")
        lay.addWidget(brand);lay.addWidget(ver)

        s=QLabel("MAIN");s.setObjectName("navSection");lay.addWidget(s)
        lay.addWidget(self._make_nav_button("home","⌂   หน้าแรก / Home",self.show_home_mode))
        lay.addWidget(self._make_nav_button("torque","T   Drive Torque",self.show_torque_mode))
        lay.addWidget(self._make_nav_button("electrical","B   Battery / Electrical",self.show_electrical_mode))
        lay.addWidget(self._make_nav_button("winch","W   Winch",self.show_winch_mode))
        lay.addWidget(self._make_nav_button("stability","S   Stability",self.show_stability_mode))
        lay.addWidget(self._make_nav_button("safety","C   Control Logic",self.show_safety_logic_mode))

        s2=QLabel("REFERENCE & OUTPUT");s2.setObjectName("navSection");lay.addWidget(s2)
        lay.addWidget(self._make_nav_button("variables","A–Z   Variables",self.show_variable_dictionary_mode))
        lay.addWidget(self._make_nav_button("tools","R   Project / Report",self.show_project_tools_mode))
        lay.addStretch(1)

        autosave=QLabel("● Auto Save ON")
        autosave.setStyleSheet("color:#177245;background:#eaf7ef;border:1px solid #c8e7d2;border-radius:8px;padding:7px;font-size:9pt;font-weight:800;")
        update=QLabel("● GitHub Update ON")
        update.setStyleSheet("color:#245f9e;background:#edf5ff;border:1px solid #d0e2f7;border-radius:8px;padding:7px;font-size:9pt;font-weight:800;")
        lay.addWidget(autosave);lay.addWidget(update)

        dock.setWidget(panel)
        self.addDockWidget(Qt.LeftDockWidgetArea,dock)
        prefs=self.load_ui_preferences()
        dock.setVisible(bool(prefs.get("navigation_visible",True)))

    def toggle_navigation(self):
        if hasattr(self,"navDock"):
            self.navDock.setVisible(not self.navDock.isVisible())
            self.save_ui_preferences()

    def setup_status_bar_ui(self):
        bar=QStatusBar(self);self.setStatusBar(bar)
        bar.setSizeGripEnabled(False)
        bar.setMinimumHeight(38)
        bar.showMessage("พร้อมใช้งาน • ค่าที่กรอกจะบันทึกอัตโนมัติ",5000)

        nav=QPushButton("เมนู");nav.setObjectName("secondaryButton")
        nav.setFixedSize(62,30);nav.clicked.connect(self.toggle_navigation)
        bar.addWidget(nav)

        # Keep font controls inside one fixed panel so QStatusBar cannot squeeze
        # individual buttons into unreadable symbols on smaller Windows displays.
        fontPanel=QFrame();fontPanel.setObjectName("metricPanel")
        fontPanel.setStyleSheet("QFrame#metricPanel{background:#f7fafc;border:1px solid #d7e1eb;border-radius:8px;}")
        fp=QHBoxLayout(fontPanel);fp.setContentsMargins(7,3,7,3);fp.setSpacing(5)
        fontTitle=QLabel("ตัวอักษร");fontTitle.setStyleSheet("font-size:9.3pt;font-weight:800;color:#445b70;")
        minus=QPushButton("A-");minus.setToolTip("ลดขนาดตัวอักษร")
        minus.setFixedSize(44,28);minus.clicked.connect(lambda:self.change_ui_scale(-.10))
        self.fontScaleLabel=QLabel("100%");self.fontScaleLabel.setAlignment(Qt.AlignCenter)
        self.fontScaleLabel.setFixedWidth(46);self.fontScaleLabel.setStyleSheet("font-weight:850;color:#294760;")
        plus=QPushButton("A+");plus.setToolTip("เพิ่มขนาดตัวอักษร")
        plus.setFixedSize(44,28);plus.clicked.connect(lambda:self.change_ui_scale(.10))
        reset=QPushButton("100%");reset.setToolTip("คืนขนาดตัวอักษรมาตรฐาน")
        reset.setFixedSize(54,28);reset.clicked.connect(self.reset_ui_scale)
        for b in (minus,plus,reset):
            b.setStyleSheet("QPushButton{min-height:26px;padding:0 5px;border-radius:6px;font-size:9.5pt;font-weight:800;}")
        fp.addWidget(fontTitle);fp.addWidget(minus);fp.addWidget(self.fontScaleLabel);fp.addWidget(plus);fp.addWidget(reset)
        fontPanel.setFixedWidth(255);fontPanel.setFixedHeight(34)
        bar.addPermanentWidget(fontPanel)

        version=QLabel(f"V{APP_VERSION}")
        version.setAlignment(Qt.AlignCenter);version.setFixedWidth(62)
        version.setStyleSheet("font-weight:900;color:#31506b;font-size:9.4pt;")
        bar.addPermanentWidget(version)

        prefs=self.load_ui_preferences()
        self.apply_ui_scale(prefs.get("font_scale",1.0),save=False)

    def setup_dynamic_tabs(self):
        """Top-level navigation uses one active page only; the top tab bar is hidden."""
        # Keep long internal tab sets usable on 1366×768 and smaller windows.
        for tab in self.findChildren(QTabWidget):
            try:
                tab.tabBar().setUsesScrollButtons(True)
                tab.setElideMode(Qt.ElideRight)
            except Exception:
                pass
        self._mode_pages={
            "home":self.homePage,"torque":self.torquePage,"electrical":self.electricalPage,"winch":self.winchPage,"crane":self.cranePage,
            "slope":self.slopePage,"fbd":self.fbdPage,"components":self.componentsPage,
            "worst":self.worstPage,"steps":self.stepsPage,"design":self.designPage,
            "graph":getattr(self,"graphPage",None),"report":self.reportPage,"help":self.helpPage,"tools":self.projectToolsPage,"safety":self.safetyPage,"variables":self.variableDictionaryPage}
        self.show_home_mode()

    def _show_only_page(self,page):
        while self.tabs.count():
            self.tabs.removeTab(0)
        self.tabs.addTab(page,"")
        self.tabs.setCurrentWidget(page)
        self.tabs.tabBar().hide()

    def show_home_mode(self):
        self._show_only_page(self.homePage)
        self._set_active_nav("home")

    def show_torque_mode(self):
        self._show_only_page(self.torquePage)
        self._set_active_nav("torque")
        self.calc_torque()

    def show_electrical_mode(self):
        self._show_only_page(self.electricalPage)
        self._set_active_nav("electrical")
        self.calc_electrical()

    def show_winch_mode(self):
        self._show_only_page(self.winchPage)
        self._set_active_nav("winch")
        self.calc_winch()

    def show_stability_mode(self):
        # Stability uses its own internal navigation created below.
        self._show_only_page(self.stabilityHubPage)
        self._set_active_nav("stability")
        self.calc_all()

    def show_project_tools_mode(self):
        self._show_only_page(self.projectToolsPage)
        self._set_active_nav("tools")
        self.update_project_tools()

    def show_safety_logic_mode(self):
        self._show_only_page(self.safetyPage)
        self._set_active_nav("safety")
        self.update_safety_logic(log_event=False)

    def show_variable_dictionary_mode(self):
        self._show_only_page(self.variableDictionaryPage)
        self._set_active_nav("variables")
        self.update_all_variable_tables()

    def make_stability_hub(self):
        hub=QWidget();self.stabilityHubPage=hub;lay=QVBoxLayout(hub);lay.setContentsMargins(16,16,16,16);lay.setSpacing(12)
        lay.addWidget(make_page_header("STABILITY ANALYSIS","วิเคราะห์การคว่ำ • ทางลาด • FBD • Mass & CG • Worst Case",self.show_home_mode,"SF / FBD","#eee8ff","#6542a5"))
        self.stabilityTabs=QTabWidget();lay.addWidget(self.stabilityTabs)
        pages=[(getattr(self,"cranePage",None),"Stability"),(getattr(self,"slopePage",None),"Slope"),
               (getattr(self,"fbdPage",None),"Engineering FBD"),(getattr(self,"componentsPage",None),"Mass & CG"),
               (getattr(self,"worstPage",None),"Worst Case"),
               (getattr(self,"designPage",None),"Design"),(getattr(self,"graphPage",None),"Graph"),
               (getattr(self,"reportPage",None),"Report"),(getattr(self,"helpPage",None),"Help")]
        for page,label in pages:
            if page is None:
                continue
            idx0=self.tabs.indexOf(page)
            if idx0>=0:self.tabs.removeTab(idx0)
            self.stabilityTabs.addTab(page,label)
        formulaPage=QWidget();fpl=QVBoxLayout(formulaPage)
        self.stabilityFormula=QTextEdit();self.stabilityFormula.setReadOnly(True);self.stabilityFormula.setStyleSheet("font-size:12px")
        fpl.addWidget(self.stabilityFormula)
        self.stabilityTabs.addTab(formulaPage,"สูตร + แทนค่า (แนะนำ)")
        self.stabilityVars=QTextEdit();self.stabilityVars.setReadOnly(True);self.stabilityTabs.addTab(self.stabilityVars,"ตัวแปร / Variables")
        # Recalculate Worst Case automatically whenever its tab is opened.
        # This makes the page usable even if the user does not press the button first.
        self.stabilityTabs.currentChanged.connect(self._on_stability_tab_changed)

    def _on_stability_tab_changed(self, index):
        page=self.stabilityTabs.widget(index)
        if page is getattr(self,"worstPage",None):
            self.calc_worst()
        elif hasattr(self,"stabilityFormula") and page is self.stabilityFormula.parentWidget():
            self.calc_all()

    def make_home(self):
        w=QWidget();self.homePage=w
        outer=QVBoxLayout(w);outer.setContentsMargins(0,0,0,0);outer.setSpacing(0)

        scroll=QScrollArea();scroll.setWidgetResizable(True);scroll.setFrameShape(QFrame.NoFrame)
        content=QWidget();root=QVBoxLayout(content);root.setContentsMargins(24,20,24,22);root.setSpacing(14)
        scroll.setWidget(content);outer.addWidget(scroll)

        # Hero
        hero=QFrame();hero.setObjectName("topHeader");hero.setMinimumHeight(142);add_soft_shadow(hero,24,5,28)
        hl=QHBoxLayout(hero);hl.setContentsMargins(25,20,25,20);hl.setSpacing(20)
        left=QVBoxLayout();left.setSpacing(6);hl.addLayout(left,1)
        chips=QHBoxLayout();chips.setSpacing(8)
        chips.addWidget(make_chip("V51  MODERN UI","#ffffff","#174a74"))
        chips.addWidget(make_chip("AUTO UPDATE","#dff3ff","#174a74"))
        chips.addStretch(1);left.addLayout(chips)

        title=QLabel("CRANE VEHICLE ENGINEERING TOOL")
        tf=QFont();tf.setPointSize(20);tf.setBold(True);title.setFont(tf)
        title.setStyleSheet("color:white;background:transparent;")
        left.addWidget(title)

        sub=QLabel("คำนวณระบบขับ • แบตเตอรี่ • วินช์ • เสถียรภาพ • Control Logic ในโปรแกรมเดียว")
        sub.setWordWrap(True);sub.setStyleSheet("color:#e1eff9;font-size:10.5pt;font-weight:650;background:transparent;")
        left.addWidget(sub)
        hint=QLabel("เริ่มจากเลือกโมดูลด้านล่าง หรือใช้เมนูซ้ายเพื่อสลับหน้าได้ทันที")
        hint.setStyleSheet("color:#b9d5e8;font-size:9.4pt;background:transparent;");left.addWidget(hint)

        side=QFrame();side.setObjectName("metricPanel");side.setFixedWidth(255)
        side.setStyleSheet("QFrame#metricPanel{background:rgba(255,255,255,0.11);border:1px solid rgba(255,255,255,0.22);border-radius:13px;}")
        sl=QVBoxLayout(side);sl.setContentsMargins(16,13,16,13);sl.setSpacing(5)
        ss=QLabel("PROJECT BASELINE");ss.setStyleSheet("color:#dcecf8;font-size:8.5pt;font-weight:900;background:transparent;");sl.addWidget(ss)
        for txt in ("Mass target ≤ 300 kg","Crane rotation ±90°","Main drive 72 V","Winch battery 12 V separate"):
            q=QLabel("•  "+txt);q.setStyleSheet("color:white;font-size:9.2pt;font-weight:650;background:transparent;");q.setWordWrap(True);sl.addWidget(q)
        hl.addWidget(side)
        root.addWidget(hero)

        # System status cards
        system=QHBoxLayout();system.setSpacing(12)
        quick=QFrame();quick.setObjectName("softPanel")
        ql=QVBoxLayout(quick);ql.setContentsMargins(15,11,15,11);ql.setSpacing(7)
        qtitle=QLabel("AUTO SAVE")
        qtitle.setStyleSheet("color:#173f5f;font-size:10.5pt;font-weight:900;")
        self.quickSaveStatus=QLabel("จำค่าที่กรอกล่าสุดให้อัตโนมัติ")
        self.quickSaveStatus.setWordWrap(True);self.quickSaveStatus.setStyleSheet("color:#667b8e;font-size:9.2pt;")
        ql.addWidget(qtitle);ql.addWidget(self.quickSaveStatus)
        qr=QHBoxLayout()
        qsave=QPushButton("บันทึกตอนนี้");qsave.setObjectName("primaryButton");qsave.clicked.connect(lambda:self.save_last_values(silent=False))
        qload=QPushButton("โหลดค่าล่าสุด");qload.clicked.connect(lambda:self.restore_last_values(silent=False))
        qclear=QPushButton("ล้างค่าที่จำ");qclear.setObjectName("secondaryButton");qclear.clicked.connect(self.clear_last_values)
        qr.addWidget(qsave);qr.addWidget(qload);qr.addWidget(qclear);ql.addLayout(qr)
        system.addWidget(quick,1)

        updatePanel=QFrame();updatePanel.setObjectName("softPanel")
        upl=QVBoxLayout(updatePanel);upl.setContentsMargins(15,11,15,11);upl.setSpacing(7)
        upTitle=QLabel(f"UPDATE CENTER  •  V{APP_VERSION}")
        upTitle.setStyleSheet("color:#173f5f;font-size:10.5pt;font-weight:900;")
        self.updateStatusLabel=QLabel("เชื่อม GitHub แล้ว • ตรวจเวอร์ชันใหม่อัตโนมัติ")
        self.updateStatusLabel.setWordWrap(True);self.updateStatusLabel.setStyleSheet("color:#667b8e;font-size:9.2pt;")
        self.updateProgress=QProgressBar();self.updateProgress.setRange(0,100);self.updateProgress.setValue(0)
        self.updateProgress.setMaximumHeight(8);self.updateProgress.setTextVisible(False);self.updateProgress.hide()
        upl.addWidget(upTitle);upl.addWidget(self.updateStatusLabel);upl.addWidget(self.updateProgress)
        ur=QHBoxLayout()
        checkUpdate=QPushButton("Check Update");checkUpdate.setObjectName("primaryButton");checkUpdate.clicked.connect(lambda:self.check_for_update(False))
        self.updateNowButton=QPushButton("Update Now");self.updateNowButton.setEnabled(False);self.updateNowButton.clicked.connect(self.download_pending_update)
        updateSettings=QPushButton("Settings");updateSettings.setObjectName("secondaryButton");updateSettings.clicked.connect(self.show_update_settings)
        ur.addWidget(checkUpdate);ur.addWidget(self.updateNowButton);ur.addWidget(updateSettings);upl.addLayout(ur)
        system.addWidget(updatePanel,1)
        root.addLayout(system)

        # Modules heading
        row=QHBoxLayout();row.setContentsMargins(2,3,2,0)
        sec=QLabel("เลือกโมดูล / ENGINEERING MODULES")
        sec.setStyleSheet("color:#17324d;font-size:11.5pt;font-weight:900;")
        row.addWidget(sec);row.addStretch(1)
        reportBtn=QPushButton("Project / Final Report");reportBtn.setObjectName("secondaryButton");reportBtn.clicked.connect(self.show_project_tools_mode)
        row.addWidget(reportBtn)
        root.addLayout(row)

        cards=QGridLayout();cards.setHorizontalSpacing(14);cards.setVerticalSpacing(14)
        bt=ModeCardButton("DRIVE TORQUE","แรงขับ • Torque • Motor Check • FBD","01","#2463eb")
        be=ModeCardButton("ELECTRICAL / BATTERY","Route Energy • Wh • Ah • Current • BMS","02","#0f8a73")
        bw=ModeCardButton("WINCH","แรงยก • ความเร็ว • เวลา • 12 V Battery","03","#d97706")
        bs=ModeCardButton("STABILITY","Side / Front / Rear tipping • Worst Case • CG","04","#7c3aed")
        bc=ModeCardButton("CONTROL LOGIC","E-stop • RC Failsafe • IMU • Limit • Interlock","05","#c45114")
        bv=ModeCardButton("VARIABLE DICTIONARY","ความหมายตัวแปร • หน่วย • ค่าปัจจุบัน","06","#4b647a")

        cards.addWidget(bt,0,0);cards.addWidget(be,0,1)
        cards.addWidget(bw,1,0);cards.addWidget(bs,1,1)
        cards.addWidget(bc,2,0);cards.addWidget(bv,2,1)
        cards.setColumnStretch(0,1);cards.setColumnStretch(1,1)
        root.addLayout(cards)

        bt.clicked.connect(self.show_torque_mode)
        be.clicked.connect(self.show_electrical_mode)
        bw.clicked.connect(self.show_winch_mode)
        bs.clicked.connect(self.show_stability_mode)
        bc.clicked.connect(self.show_safety_logic_mode)
        bv.clicked.connect(self.show_variable_dictionary_mode)

        footer=QFrame();footer.setObjectName("softPanel")
        fl=QHBoxLayout(footer);fl.setContentsMargins(14,9,14,9)
        ft=QLabel("Tip: ใช้ปุ่ม A− / A+ ด้านล่างเพื่อปรับขนาดตัวอักษรได้ทั้งโปรแกรม")
        ft.setStyleSheet("color:#6d7f90;font-size:9.2pt;");fl.addWidget(ft);fl.addStretch(1)
        helpBtn=QPushButton("Project Tools");helpBtn.setObjectName("secondaryButton");helpBtn.clicked.connect(self.show_project_tools_mode);fl.addWidget(helpBtn)
        root.addWidget(footer)
        root.addStretch(1)

        self.tabs.addTab(w,"")




    # =====================================================================
    # BUILT-IN UPDATER
    # =====================================================================
    def update_config_path(self):
        base=QStandardPaths.writableLocation(QStandardPaths.AppConfigLocation)
        folder=Path(base) if base else (Path.home()/".CraneVehicleEngineeringTool")
        folder.mkdir(parents=True,exist_ok=True)
        return folder/"update_config.json"

    def load_update_config(self):
        default={"manifest_url":DEFAULT_UPDATE_MANIFEST_URL,"check_on_startup":True}
        path=self.update_config_path()
        if not path.exists():
            return default
        try:
            data=json.loads(path.read_text(encoding="utf-8"))
            if not isinstance(data,dict):
                return default
            configured=str(data.get("manifest_url","")).strip()
            return {
                "manifest_url":configured or DEFAULT_UPDATE_MANIFEST_URL,
                "check_on_startup":bool(data.get("check_on_startup",True)),
            }
        except Exception:
            return default

    def save_update_config(self,manifest_url,check_on_startup):
        data={"manifest_url":str(manifest_url).strip(),"check_on_startup":bool(check_on_startup)}
        self.update_config_path().write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding="utf-8")

    def show_update_settings(self):
        cfg=self.load_update_config()
        dlg=QDialog(self);dlg.setWindowTitle("Update Settings");dlg.resize(720,250)
        lay=QVBoxLayout(dlg)
        info=QLabel(
            "โปรแกรมจะรู้ว่ามีเวอร์ชันใหม่จากไฟล์ latest.json ที่คุณวางไว้บนเว็บ/GitHub ของคุณ\\n"
            "แนะนำ HTTPS เท่านั้นสำหรับการใช้งานจริง หรือใช้ path ไฟล์ในเครื่องเพื่อทดสอบ"
        )
        info.setWordWrap(True);info.setStyleSheet("background:#eef6ff;color:#274c77;padding:10px;border:1px solid #cfe2f5;border-radius:8px;")
        lay.addWidget(info)
        form=QFormLayout()
        url=QLineEdit(cfg.get("manifest_url",""))
        url.setPlaceholderText("https://.../latest.json   หรือ C:\\path\\latest.json สำหรับทดสอบ")
        auto=QCheckBox("ตรวจสอบอัปเดตอัตโนมัติหลังเปิดโปรแกรม")
        auto.setChecked(cfg.get("check_on_startup",False))
        form.addRow("Manifest URL / Path",url);form.addRow("",auto)
        lay.addLayout(form)
        hint=QLabel(
            'รูปแบบ latest.json: {"latest_version":"50.1.0","download_url":"https://.../Setup.exe","sha256":"...","notes":"รายละเอียดเวอร์ชันใหม่"}'
        )
        hint.setWordWrap(True);hint.setStyleSheet("color:#61758a;font-size:9.5pt;")
        lay.addWidget(hint)
        buttons=QDialogButtonBox(QDialogButtonBox.Save|QDialogButtonBox.Cancel)
        buttons.accepted.connect(dlg.accept);buttons.rejected.connect(dlg.reject);lay.addWidget(buttons)
        if dlg.exec()==QDialog.Accepted:
            try:
                self.save_update_config(url.text(),auto.isChecked())
                self._set_update_status("บันทึก Update Settings แล้ว",ok=True)
            except Exception as exc:
                QMessageBox.warning(self,"Update Settings",str(exc))

    @staticmethod
    def _version_tuple(value):
        nums=re.findall(r"\d+",str(value))
        vals=[int(x) for x in nums[:4]]
        while len(vals)<4:
            vals.append(0)
        return tuple(vals)

    def _set_update_status(self,text,ok=None):
        if not hasattr(self,"updateStatusLabel"):
            return
        self.updateStatusLabel.setText(str(text))
        color="#66788a" if ok is None else ("#176337" if ok else "#b42318")
        self.updateStatusLabel.setStyleSheet(f"color:{color};font-size:9.5pt;")

    def _set_update_progress(self,value):
        if not hasattr(self,"updateProgress"):
            return
        value=max(0,min(100,int(value)))
        self.updateProgress.show()
        self.updateProgress.setValue(value)
        if value>=100:
            QTimer.singleShot(1200,self.updateProgress.hide)

    def auto_check_for_update(self):
        cfg=self.load_update_config()
        if cfg.get("check_on_startup") and cfg.get("manifest_url"):
            self._update_auto_requested=True
            self.check_for_update(silent=True)

    def check_for_update(self,silent=False):
        if self._update_busy:
            if not silent:
                QMessageBox.information(self,"Update","กำลังตรวจสอบอัปเดตอยู่")
            return
        cfg=self.load_update_config()
        source=cfg.get("manifest_url","").strip()
        if not source:
            self._set_update_status("ยังไม่ได้ตั้ง Manifest URL • กด Update Settings")
            if not silent:
                self.show_update_settings()
            return

        self._update_busy=True
        self._update_auto_requested=bool(silent)
        self._set_update_status("กำลังตรวจสอบเวอร์ชันใหม่...")
        self._set_update_progress(5)

        def worker():
            try:
                manifest=self._read_update_manifest(source)
                self.updateTaskFinished.emit({"type":"check","ok":True,"manifest":manifest,"silent":silent})
            except Exception as exc:
                self.updateTaskFinished.emit({"type":"check","ok":False,"error":str(exc),"silent":silent})
        threading.Thread(target=worker,daemon=True).start()

    def _read_update_manifest(self,source):
        src=str(source).strip()
        if not src:
            raise ValueError("Manifest URL ว่าง")

        parsed=urllib.parse.urlparse(src)
        if parsed.scheme in ("http","https"):
            if parsed.scheme!="https" and parsed.hostname not in ("localhost","127.0.0.1"):
                raise ValueError("เพื่อความปลอดภัย Remote Update ต้องใช้ HTTPS")
            req=urllib.request.Request(src,headers={"User-Agent":f"{APP_NAME}/{APP_VERSION}"})
            with urllib.request.urlopen(req,timeout=10) as r:
                raw=r.read(1024*1024)
        else:
            path=Path(urllib.request.url2pathname(parsed.path)) if parsed.scheme=="file" else Path(src)
            if not path.exists():
                raise FileNotFoundError(f"ไม่พบ manifest: {path}")
            raw=path.read_bytes()

        data=json.loads(raw.decode("utf-8-sig"))
        if not isinstance(data,dict):
            raise ValueError("latest.json ต้องเป็น JSON object")
        latest=str(data.get("latest_version","")).strip()
        download=str(data.get("download_url","")).strip()
        if not latest:
            raise ValueError("latest.json ไม่มี latest_version")
        if self._version_tuple(latest)>self._version_tuple(APP_VERSION) and not download:
            raise ValueError("พบเวอร์ชันใหม่แต่ latest.json ไม่มี download_url")
        data["latest_version"]=latest
        data["download_url"]=download
        data["notes"]=str(data.get("notes","")).strip()
        data["sha256"]=str(data.get("sha256","")).strip().lower()
        return data

    def _handle_update_task_result(self,result):
        self._update_busy=False
        if not isinstance(result,dict):
            return

        typ=result.get("type")
        if typ=="check":
            if not result.get("ok"):
                self._set_update_progress(0)
                self._set_update_status("ตรวจสอบอัปเดตไม่สำเร็จ: "+result.get("error","Unknown error"),ok=False)
                if not result.get("silent"):
                    QMessageBox.warning(self,"Check for Update",result.get("error","Unknown error"))
                return

            manifest=result["manifest"]
            latest=manifest.get("latest_version","")
            if self._version_tuple(latest)>self._version_tuple(APP_VERSION):
                self.pending_update_manifest=manifest
                if hasattr(self,"updateNowButton"):self.updateNowButton.setEnabled(True)
                notes=manifest.get("notes","")
                self._set_update_progress(100)
                self._set_update_status(f"มีเวอร์ชันใหม่ V{latest} • Current V{APP_VERSION}",ok=True)
                if not result.get("silent"):
                    msg=f"พบเวอร์ชันใหม่ V{latest}\\n\\nCurrent: V{APP_VERSION}"
                    if notes:msg+="\\n\\n"+notes
                    msg+="\\n\\nต้องการดาวน์โหลดและอัปเดตตอนนี้หรือไม่?"
                    if QMessageBox.question(self,"Update Available",msg,QMessageBox.Yes|QMessageBox.No,QMessageBox.Yes)==QMessageBox.Yes:
                        self.download_pending_update()
            else:
                self.pending_update_manifest=None
                if hasattr(self,"updateNowButton"):self.updateNowButton.setEnabled(False)
                self._set_update_progress(100)
                self._set_update_status(f"โปรแกรมเป็นเวอร์ชันล่าสุดแล้ว • V{APP_VERSION}",ok=True)
                if not result.get("silent"):
                    QMessageBox.information(self,"Check for Update",f"คุณใช้เวอร์ชันล่าสุดแล้ว: V{APP_VERSION}")

        elif typ=="download":
            if not result.get("ok"):
                self._set_update_status("ดาวน์โหลดอัปเดตไม่สำเร็จ: "+result.get("error","Unknown error"),ok=False)
                QMessageBox.warning(self,"Update Download",result.get("error","Unknown error"))
                return
            path=Path(result.get("path",""))
            self._set_update_progress(100)
            self._set_update_status(f"ดาวน์โหลดเสร็จแล้ว • {path.name}",ok=True)
            msg=(
                f"ดาวน์โหลดอัปเดตเรียบร้อย\\n\\n{path}\\n\\n"
                "กด Yes เพื่อปิดโปรแกรมและเริ่มติดตั้งอัปเดต\\n"
                "Windows อาจถาม UAC / SmartScreen"
            )
            if QMessageBox.question(self,"Install Update",msg,QMessageBox.Yes|QMessageBox.No,QMessageBox.Yes)==QMessageBox.Yes:
                self.launch_update_installer(path)

    def download_pending_update(self):
        manifest=self.pending_update_manifest
        if not manifest:
            QMessageBox.information(self,"Update","ยังไม่มีเวอร์ชันใหม่ที่ตรวจพบ กรุณากด Check for Update ก่อน")
            return
        if self._update_busy:
            return
        url=manifest.get("download_url","").strip()
        if not url:
            QMessageBox.warning(self,"Update","ไม่มี download_url ใน manifest")
            return

        self._update_busy=True
        self._set_update_status(f"กำลังดาวน์โหลด V{manifest.get('latest_version','')}...")
        self._set_update_progress(2)

        def worker():
            try:
                path=self._download_update_installer(manifest)
                self.updateTaskFinished.emit({"type":"download","ok":True,"path":str(path)})
            except Exception as exc:
                self.updateTaskFinished.emit({"type":"download","ok":False,"error":str(exc)})
        threading.Thread(target=worker,daemon=True).start()

    def _download_update_installer(self,manifest):
        src=manifest.get("download_url","").strip()
        latest=manifest.get("latest_version","update")
        parsed=urllib.parse.urlparse(src)
        target=Path(tempfile.gettempdir())/f"CraneVehicleEngineeringTool_Update_{re.sub(r'[^0-9A-Za-z_.-]','_',latest)}.exe"

        if parsed.scheme in ("http","https"):
            if parsed.scheme!="https" and parsed.hostname not in ("localhost","127.0.0.1"):
                raise ValueError("Remote installer download ต้องใช้ HTTPS")
            req=urllib.request.Request(src,headers={"User-Agent":f"{APP_NAME}/{APP_VERSION}"})
            with urllib.request.urlopen(req,timeout=30) as r, open(target,"wb") as f:
                total=int(r.headers.get("Content-Length","0") or 0)
                done=0
                while True:
                    chunk=r.read(1024*256)
                    if not chunk:break
                    f.write(chunk);done+=len(chunk)
                    if total>0:
                        self.updateProgressChanged.emit(min(95,int(done*95/total)))
        else:
            source_path=Path(urllib.request.url2pathname(parsed.path)) if parsed.scheme=="file" else Path(src)
            if not source_path.exists():
                raise FileNotFoundError(f"ไม่พบ installer: {source_path}")
            data=source_path.read_bytes()
            target.write_bytes(data)
            self.updateProgressChanged.emit(95)

        if target.suffix.lower()!=".exe":
            raise ValueError("ไฟล์อัปเดตต้องเป็น .exe")

        expected=manifest.get("sha256","").strip().lower()
        if expected:
            actual=hashlib.sha256(target.read_bytes()).hexdigest().lower()
            if actual!=expected:
                try:target.unlink()
                except Exception:pass
                raise ValueError("SHA256 ของไฟล์อัปเดตไม่ตรงกับ manifest — ยกเลิกเพื่อความปลอดภัย")
        return target

    def launch_update_installer(self,path):
        path=Path(path)
        if not path.exists():
            QMessageBox.warning(self,"Install Update","ไม่พบไฟล์ installer")
            return
        try:
            if sys.platform.startswith("win"):
                # Inno Setup switches: silent upgrade, close running app, no forced reboot.
                subprocess.Popen([
                    str(path),"/VERYSILENT","/SUPPRESSMSGBOXES","/NORESTART",
                    "/CLOSEAPPLICATIONS","/RESTARTAPPLICATIONS"
                ],close_fds=True)
            else:
                subprocess.Popen([str(path)],close_fds=True)
            QApplication.quit()
        except Exception as exc:
            QMessageBox.critical(self,"Install Update","เปิด installer ไม่สำเร็จ:\\n"+str(exc))

    # =====================================================================
    # VARIABLE DICTIONARY / ตารางตัวแปร
    # =====================================================================
    def _variable_table_html(self,title,subtitle,rows):
        body=[]
        for var,meaning,unit,value,note in rows:
            body.append(
                "<tr>"
                f"<td style='font-size:12pt;font-weight:900;color:#17456b;text-align:center'>{var}</td>"
                f"<td><b>{meaning}</b></td>"
                f"<td style='text-align:center'>{unit}</td>"
                f"<td style='text-align:center;font-weight:800;color:#176337'>{value}</td>"
                f"<td>{note}</td>"
                "</tr>"
            )
        return (
            f"<h2 style='color:#17324d'>{title}</h2>"
            f"<p style='font-size:11pt'>{subtitle}</p>"
            "<p><b>วิธีอ่าน:</b> ตัวแปร = สัญลักษณ์ที่ใช้ในสูตร • หน่วย = หน่วยที่ต้องใช้ • ค่าปัจจุบัน = ค่าที่โปรแกรมกำลังใช้คำนวณ</p>"
            "<table cellpadding='8' cellspacing='0' border='1' style='border-collapse:collapse;width:100%;font-size:10.5pt'>"
            "<tr style='background:#eaf1f8;color:#17324d'>"
            "<th style='width:11%'>ตัวแปร</th><th style='width:29%'>ความหมายภาษาไทย</th>"
            "<th style='width:11%'>หน่วย</th><th style='width:16%'>ค่าปัจจุบัน</th><th>หมายเหตุ / ใช้ทำอะไร</th></tr>"
            + "".join(body) + "</table>"
        )

    def torque_variables_html(self):
        q=self.torque_results()
        rows=[
            ("m","มวลรวมของรถพร้อมโหลด","kg",f"{q['m']:.2f}","ใช้หาแรงจากความชัน แรงต้าน และแรงเร่ง"),
            ("g","ความเร่งเนื่องจากแรงโน้มถ่วง","m/s²","9.81","ค่าคงที่ที่ใช้ในโปรแกรม"),
            ("θ","มุมความชันของทางลาด","deg",f"{q['deg']:.2f}","ใช้ใน sinθ และ cosθ"),
            ("v","ความเร็วรถ","m/s",f"{q['v']:.5f}",f"มาจาก {self.tspeed.value():.2f} km/h"),
            ("Crr / μr","สัมประสิทธิ์แรงต้านการกลิ้ง","-",f"{self.tmu.value():.3f}","ใช้คำนวณ Frr"),
            ("n","จำนวนมอเตอร์ขับ","ตัว",str(q["n"]),"แรงรวมถูกแบ่งให้มอเตอร์แต่ละตัว"),
            ("D","เส้นผ่านศูนย์กลางล้อ","inch",f"{self.twheelInch.value():.2f}","แปลงเป็นเมตรก่อนหารัศมี"),
            ("r","รัศมีล้อ","m",f"{q['r']:.5f}","ใช้ T = F × r"),
            ("SF","Safety Factor สำหรับแรงขับ","-",f"{self.tsf.value():.2f}","คูณแรงรวมก่อนเลือกมอเตอร์"),
            ("t_acc","เวลาเร่งจาก 0 ถึง v","s",f"{self.taccel.value():.2f}","ใช้หา a = v/t"),
            ("a","ความเร่งรถ","m/s²",f"{q['a']:.5f}","ใช้ Fa = ma"),
            ("η","ประสิทธิภาพระบบขับ","%",f"{self.teff.value():.1f}","ใช้แปลงกำลังกลเป็นกำลังไฟฟ้า"),
            ("μ","สัมประสิทธิ์แรงยึดเกาะ","-",f"{self.ttraction.value():.2f}","ใช้ตรวจ Traction limit"),
            ("λ_drive","สัดส่วนแรงกดปกติที่อยู่บนล้อขับ","%",f"{self.tDriveLoadFrac.value():.1f}","ค่าเริ่มต้น 50% สำหรับ 2 ล้อขับ + 2 ล้อรองรับ"),
            ("N_drive","แรงกดปกติรวมบนล้อขับ","N",f"{q['Ndrive']:.2f}","N_total × λ_drive"),
            ("V","แรงดันแบตเตอรี่หลัก","V",f"{self.tvoltage.value():.1f}","ใช้ประมาณกระแสจาก P/V"),
            ("Fgrade","แรงจากความชัน","N",f"{q['Fg']:.2f}","m g sinθ"),
            ("Frr","แรงต้านการกลิ้ง","N",f"{q['Fr']:.2f}","Crr m g cosθ"),
            ("Fa","แรงที่ใช้เร่งรถ","N",f"{q['Fa']:.2f}","m a"),
            ("Fdesign","แรงออกแบบรวมหลังคูณ SF","N",f"{q['Fdesign']:.2f}","แรงรวมที่มอเตอร์ทุกตัวต้องช่วยกันสร้าง"),
            ("Fmotor","แรงต่อมอเตอร์ 1 ตัว","N",f"{q['Fmotor']:.2f}","Fdesign ÷ n"),
            ("T","แรงบิดที่ล้อ/มอเตอร์ 1 ตัว","N·m",f"{q['T']:.2f}","Fmotor × r"),
            ("RPM","ความเร็วรอบล้อ","rpm",f"{q['rpm']:.2f}","ใช้ตรวจช่วงความเร็วของมอเตอร์"),
            ("Pmech","กำลังกลออกแบบรวม","W",f"{q['Pwheel']:.2f}","Fdesign × v"),
            ("Ibatt","กระแสแบตเตอรี่โดยประมาณ","A",f"{q['Ibatt']:.2f}","ใช้ตรวจ BMS/สาย/Controller เบื้องต้น"),
        ]
        return self._variable_table_html("DRIVE TORQUE — ตารางตัวแปร","รวมตัวแปร Input และผลคำนวณสำคัญของระบบขับ",rows)

    def electrical_variables_html(self):
        q=self.electrical_results()
        rows=[
            ("m","มวลรวมรถที่ใช้คำนวณพลังงาน","kg",f"{q['m']:.1f}","ควรรวมรถ เครน แบตเตอรี่ และ Payload โดยไม่ซ้ำ"),
            ("V","แรงดันแบตเตอรี่หลัก","V",f"{q['V']:.1f}","ระบบขับ 72 V ในแบบปัจจุบัน"),
            ("v","ความเร็วรถ","m/s",f"{q['v']:.5f}",f"{self.espeed.value():.2f} km/h"),
            ("d_oneway","ระยะทางเที่ยวเดียว","m",f"{q['one']:.2f}","ไป-กลับต่อรอบ = 2 × d_oneway"),
            ("L_slope","ความยาวช่วงทางลาดต่อเที่ยว","m",f"{q['Ls']:.2f}","ใช้หาพลังงานช่วงขึ้นลาด"),
            ("θ","มุมทางลาด","deg",f"{self.eslopeDeg.value():.1f}","ใช้หาแรงโน้มถ่วงตามทางลาด"),
            ("t_runtime","เวลาทำงานรวม","h",f"{q['runtime_h']:.2f}","ใช้คำนวณจำนวนรอบและ Aux energy"),
            ("Crr","สัมประสิทธิ์แรงต้านการกลิ้ง","-",f"{q['crr']:.3f}","แรงสูญเสียจากยาง/พื้น"),
            ("t_acc","เวลาเร่ง","s",f"{self.eaccel.value():.2f}","พลังงานจลน์ไม่ขึ้นกับเวลา แต่เวลานี้ใช้ตรวจ Peak force/current"),
            ("a_acc","ความเร่งช่วงออกตัว","m/s²",f"{q['accel_a']:.4f}","v ÷ t_acc"),
            ("P_down","กำลังขับขาลงแบบ No Regen","W",f"{q['Pdown_mech']:.2f}","เป็น 0 เมื่อแรงโน้มถ่วงพอให้รถไหลลงเอง"),
            ("I_peak,calc","กระแสคำนวณสูงสุดจากขึ้นลาด/เร่ง","A",f"{q['Icalc_peak']:.2f}","ใช้ประกอบการเลือก BMS/สาย"),
            ("N_start","จำนวนครั้งออกตัวต่อรอบ","ครั้ง",str(self.estops.value()),"พลังงานจลน์ถูกคิดตามจำนวนครั้งนี้"),
            ("t_stop","เวลาหยุดต่อรอบ","s",f"{q['stop_s']:.1f}","มีผลต่อจำนวนรอบในเวลาทำงาน"),
            ("η_drive","ประสิทธิภาพระบบขับสมมติ","%",f"{self.edriveEff.value():.1f}","ใช้แปลง Mechanical → Electrical"),
            ("P_aux","กำลังอุปกรณ์เสริมเฉลี่ย","W",f"{self.eaux.value():.1f}","เช่น ESP32, Relay, Display, Buzzer"),
            ("DoD","สัดส่วนความจุแบตเตอรี่ที่อนุญาตให้ใช้","%",f"{self.edod.value():.1f}","ไม่ควรตีความเป็นความจุรวมทั้งหมด"),
            ("Reserve","พลังงานสำรองที่เผื่อ","%",f"{self.ereserve.value():.1f}","เพิ่มความจุเพื่อเผื่อความคลาดเคลื่อน"),
            ("P_rated","กำลังพิกัดมอเตอร์ต่อหนึ่งตัว","W",f"{self.emotorRated.value():.0f}","ใช้ใน Worst-case model"),
            ("n_motor","จำนวนมอเตอร์ขับ","ตัว",str(self.enmot.value()),"ปัจจุบัน 2 Hub Motors"),
            ("η_up","ประสิทธิภาพกรณี Worst-case ขึ้นลาด","%",f"{self.eupEff.value():.1f}","ใช้ประเมินกระแส/พลังงานหนักสุด"),
            ("Emech","พลังงานกลรวม","Wh",f"{q['Emech_total']:.1f}","พลังงานเชิงกลก่อนความสูญเสีย"),
            ("Edrive","พลังงานไฟฟ้าขับเคลื่อนที่เลือกใช้","Wh",f"{q['Edrive']:.1f}","ขึ้นกับ Calculated/Worst-case mode"),
            ("Eaux","พลังงานอุปกรณ์เสริม","Wh",f"{q['Eaux']:.1f}","Paux × runtime"),
            ("Edesign","พลังงานแบตเตอรี่หลัง DoD + Reserve","Wh",f"{q['Edesign']:.1f}","ใช้แปลงเป็น Ah"),
            ("Ah","ความจุแบตเตอรี่ที่คำนวณได้","Ah",f"{q['Ah']:.2f}","ยังต้องตรวจกระแสและ BMS แยก"),
            ("Iworst","กระแส Worst-case indicator","A",f"{q['Iworst']:.1f}","ใช้เป็นตัวชี้เบื้องต้น ไม่ใช่กระแส Peak ที่ยืนยัน"),
        ]
        return self._variable_table_html("ELECTRICAL / BATTERY — ตารางตัวแปร","ตัวแปรเส้นทาง พลังงาน ความจุ และกระแสของแบตเตอรี่หลัก",rows)

    def winch_variables_html(self):
        q=self.winch_results();sp=self.winch_speed_results()
        rows=[
            ("m_load","มวลสิ่งที่ต้องการยก","kg",f"{self.wmass.value():.2f}","Payload หลัก"),
            ("m_basket","มวลตะกร้า/อุปกรณ์ยก","kg",f"{self.wbasket.value():.2f}","รวมกับ Payload ก่อนหาแรงยก"),
            ("h","ความสูงยกแนวดิ่ง","m",f"{self.wheight.value():.2f}","ใช้หาเวลาและพลังงาน mgh"),
            ("V","แรงดันแบตเตอรี่วินช์","V",f"{q['v']:.1f}","แบต 12 V แยกจากระบบรถ"),
            ("P_rated","กำลังพิกัดตามฉลากวินช์","W",f"{self.wrated.value():.0f}","ไม่ใช้แทนกระแสจริงโดยอัตโนมัติ"),
            ("i","อัตราทดเกียร์วินช์","-",f"{self.wratio.value():.0f}:1","ใช้แปลงรอบ/แรงบิดระหว่างมอเตอร์กับดรัม"),
            ("v_up","ความเร็วโหลดขาขึ้น","m/min",f"{q['up_speed']:.3f}","ใช้หาเวลายก"),
            ("v_down","ความเร็วโหลดขาลง","m/min",f"{q['down_speed']:.3f}","ใช้หาเวลาลด"),
            ("I_up","กระแสขณะยก","A",f"{self.wiup.value():.1f}","ปัจจุบันเป็นสมมติฐานจนกว่าจะวัดจริง"),
            ("I_down","กระแสขณะลด","A",f"{self.widown.value():.1f}","อาจต่างจากขาขึ้น"),
            ("N_cycle","จำนวนรอบยกขึ้น+ลง","รอบ",str(self.wcycles.value()),"ใช้หาพลังงานรวม"),
            ("DoD","สัดส่วนแบตเตอรี่ที่อนุญาตให้ใช้","%",f"{self.wdod.value():.1f}","ใช้เผื่อความลึกการคายประจุ"),
            ("Reserve","พลังงานสำรอง","%",f"{self.wreserve.value():.1f}","เผื่อความคลาดเคลื่อน"),
            ("D_drum","เส้นผ่านศูนย์กลางดรัมรวมสลิง","mm",f"{self.wdiameter.value():.1f}","0 = ยังไม่ทราบ"),
            ("SF_force","ตัวคูณแรงวิเคราะห์เบื้องต้น","-",f"{self.wsf.value():.2f}","ไม่ใช่ WLL ของอุปกรณ์ยก"),
            ("t_up","เวลายกขึ้น","s",f"{q['tu']:.1f}","h ÷ v_up"),
            ("t_down","เวลาลดลง","s",f"{q['td']:.1f}","h ÷ v_down"),
            ("F_lift","แรงยกเชิงน้ำหนัก","N",f"{q['f']:.1f}","(m_load + m_basket) × g"),
            ("E_total","พลังงานไฟฟ้ารวมตามจำนวนรอบ","Wh",f"{q['total']:.2f}","รวมขาขึ้นและขาลง"),
            ("Ah","ความจุแบตเตอรี่ที่คำนวณได้","Ah",f"{q['ah']:.2f}","ยังต้องตรวจ BMS/กระแสกระชาก"),
            ("n_motor","รอบมอเตอร์ที่ใช้หน้า Speed","rpm",f"{sp['motor_up']:.0f}","ค่าที่กรอก/สมมติใน Speed model"),
            ("n_drum","รอบดรัมขาขึ้น","rpm",f"{sp['drum_up']:.2f}","รอบมอเตอร์ ÷ อัตราทด"),
            ("T_rope","แรงตึงสลิง","N",f"{sp['tension']:.1f}","ขึ้นกับจำนวนส่วนสลิงและประสิทธิภาพรอก"),
            ("T_drum","แรงบิดดรัม","N·m",f"{sp['drum_torque']:.2f}","T_rope × รัศมีดรัม"),
        ]
        return self._variable_table_html("WINCH — ตารางตัวแปร","รวมตัวแปรแบตเตอรี่ เวลา ความเร็ว แรง และแรงบิดของวินช์",rows)

    def stability_variables_html(self):
        d=self.inputs();sf,MO,MR=self.calc_side(d);sfF,sfR=self.longitudinal_sf_at(d,d["th"])
        FL=d["kd"]*d["ml"]*G
        rows=[
            ("m_total","มวลรวมทั้งระบบ","kg",f"{d['mt']:.2f}","ควรรวมทุกชิ้นโดยไม่ซ้ำมวล"),
            ("m_L","มวล Payload / สิ่งที่ยก","kg",f"{d['ml']:.2f}","โหลดที่ปลายเครน"),
            ("m_B","มวลแขนเครน","kg",f"{d['mb']:.2f}","ใช้คำนวณโมเมนต์ของ Boom"),
            ("W","Track width ระยะศูนย์กลางล้อซ้าย-ขวา","m",f"{d['W']:.3f}","มีผลโดยตรงต่อ Side tipping"),
            ("WB","Wheelbase ระยะฐานล้อหน้า-หลัง","m",f"{d['WB']:.3f}","ใช้คำนวณ Front/Rear tipping"),
            ("L","ความยาวแขนเครน","m",f"{d['L']:.3f}","ระยะจากแกนหมุนถึงปลายแขน"),
            ("H","ความสูงเสาเครน","m",f"{d['H']:.3f}","ใช้ในโมเดล/ภาพ 3D และการจัดวาง"),
            ("x_C","ตำแหน่งแกนเครนจากเพลาหลัง","m",f"{d['xC']:.3f}","ใช้หาโมเมนต์หน้า/หลัง"),
            ("x_CG,base","ตำแหน่ง CG ของรถส่วนหลักที่ไม่รวม Payload+Boom","m",f"{d['xCG']:.3f}","ใช้ใน Front/Rear crane tipping"),
            ("x_CG,drive","ตำแหน่ง CG รวมตอนรถวิ่ง","m",f"{d['driveXCG']:.3f}","ใช้ใน Slope driving stability"),
            ("θ","มุมหมุนเครน","deg",f"{d['th']:.1f}","ช่วงใช้งาน -90° ถึง +90°"),
            ("Kdyn","Dynamic factor ของ Payload","-",f"{d['kd']:.2f}","เผื่อแรงกระชากในการวิเคราะห์เบื้องต้น"),
            ("SF_req","Safety Factor เป้าหมาย","-",f"{d['req']:.2f}","ใช้เทียบ PASS/FAIL เชิงแบบจำลอง"),
            ("F_L","แรงโหลดออกแบบ","N",f"{FL:.2f}","Kdyn × mL × g"),
            ("M_O","โมเมนต์ทำให้คว่ำด้านข้าง","N·m",f"{MO:.2f}","รวม Payload + Boom ตามโมเดล"),
            ("M_R","โมเมนต์ต้านการคว่ำด้านข้าง","N·m",f"{MR:.2f}","จากมวลต้านและฐานล้อ"),
            ("SF_side","Safety Factor ด้านข้าง","-",("∞" if sf>=999 else f"{sf:.3f}"),"MR ÷ MO"),
            ("SF_front","Safety Factor คว่ำด้านหน้า","-",("∞" if sfF>=999 else f"{sfF:.3f}"),"คำนวณรอบแนวเพลาหน้า"),
            ("SF_rear","Safety Factor คว่ำด้านหลัง","-",("∞" if sfR>=999 else f"{sfR:.3f}"),"คำนวณรอบแนวเพลาหลัง"),
        ]
        return self._variable_table_html("STABILITY — ตารางตัวแปร","ตัวแปรเรขาคณิต มวล โมเมนต์ และ Safety Factor ของรถเครน",rows)

    def safety_variables_html(self):
        if not hasattr(self,"safetyEStop"):
            return self._variable_table_html("CONTROL LOGIC — ตารางตัวแปร","ตัวแปร Logic และสัญญาณความปลอดภัย",[])
        v=self.safety_input_values();r=self.evaluate_safety_logic(v)
        rows=[
            ("E-STOP","สถานะ Emergency Stop","Boolean","ON" if v["estop"] else "OFF","ON = ตัดคำสั่งการเคลื่อนที่ทั้งหมด"),
            ("RC_OK","สถานะสัญญาณ RC / IBUS","Boolean","OK" if v["rc_ok"] else "LOST","LOST = เข้า RC Failsafe"),
            ("CH5","Drive Enable จากรีโมท","Boolean","ON" if v["drive_enable"] else "OFF","OFF = ไม่อนุญาต Drive"),
            ("Throttle","คำสั่งเดินหน้า/ถอยหลัง","%",f"{v['throttle']:+d}","ค่าบวก/ลบกำหนดทิศทาง"),
            ("Steering","คำสั่งเลี้ยว Differential","%",f"{v['steer']:+d}","ผสมกับ Throttle เพื่อสั่งล้อซ้าย/ขวา"),
            ("Crane Cmd","คำสั่งหมุนเครน","State",v["crane"],"STOP / LEFT / RIGHT"),
            ("Winch Cmd","คำสั่งวินช์","State",v["winch"],"STOP / UP / DOWN"),
            ("Tilt","มุมเอียงจาก IMU","deg",f"{v['tilt']:.1f}","เปรียบเทียบกับ Tilt Limit"),
            ("Tilt Limit","ค่ามุมที่เริ่ม Inhibit Drive","deg",f"{v['tilt_limit']:.1f}","ถึง/เกินค่านี้ Drive ถูกล็อก"),
            ("Limit L","Limit Switch ด้าน -90°","Boolean","ON" if v["left_limit"] else "OFF","ON = ห้ามหมุน LEFT ต่อ"),
            ("Limit R","Limit Switch ด้าน +90°","Boolean","ON" if v["right_limit"] else "OFF","ON = ห้ามหมุน RIGHT ต่อ"),
            ("Battery Low","สถานะแบตเตอรี่ต่ำ","Boolean","ON" if v["battery_low"] else "OFF","แจ้งเตือนหรือ Inhibit ตาม Policy"),
            ("Drive Permit","ผล Logic อนุญาต Drive","Boolean","ENABLE" if r["drive_permit"] else "LOCKED","ผลหลังตรวจ Fault/Interlock"),
            ("L Motor","คำสั่งมอเตอร์ซ้าย","%",f"{r['left_motor']:+d}","ผล Differential steering"),
            ("R Motor","คำสั่งมอเตอร์ขวา","%",f"{r['right_motor']:+d}","ผล Differential steering"),
            ("System State","สถานะระบบรวม","State",r["state"],r["reason"]),
        ]
        return self._variable_table_html("CONTROL / SAFETY LOGIC — ตารางตัวแปร","ความหมายของ Input/Output ที่ใช้จำลอง Logic ก่อนเขียนลง ESP32",rows)

    def update_all_variable_tables(self):
        pairs=[
            ("torqueVars",self.torque_variables_html),
            ("eVars",self.electrical_variables_html),
            ("wVars",self.winch_variables_html),
            ("stabilityVars",self.stability_variables_html),
            ("safetyVars",self.safety_variables_html),
            ("allTorqueVars",self.torque_variables_html),
            ("allEVars",self.electrical_variables_html),
            ("allWVars",self.winch_variables_html),
            ("allStabilityVars",self.stability_variables_html),
            ("allSafetyVars",self.safety_variables_html),
        ]
        for attr,fn in pairs:
            view=getattr(self,attr,None)
            if view is not None:
                try:view.setHtml(fn())
                except Exception as exc:view.setPlainText("Variable table error: "+str(exc))

    def make_variable_dictionary_page(self):
        w=QWidget();self.variableDictionaryPage=w
        root=QVBoxLayout(w);root.setContentsMargins(16,16,16,16);root.setSpacing(12)
        root.addWidget(make_page_header(
            "VARIABLE DICTIONARY / ตารางตัวแปรทั้งหมด",
            "ความหมาย • หน่วย • ค่าปัจจุบัน • ใช้ในสูตรไหน",
            self.show_home_mode,"A–Z / UNITS","#eaf4ff","#2457a6"
        ))
        intro=QLabel("รวมตัวแปรหลักของทุกโมดูลไว้ในหน้าเดียว เหมาะสำหรับใช้อธิบายอาจารย์และตรวจหน่วยก่อนคำนวณ")
        intro.setWordWrap(True);intro.setStyleSheet("background:#f5f9ff;color:#385570;padding:10px;border:1px solid #d5e4f2;border-radius:8px;font-size:10.5pt;")
        root.addWidget(intro)
        tabs=QTabWidget();self.allVariableTabs=tabs
        self.allTorqueVars=QTextEdit();self.allTorqueVars.setReadOnly(True);tabs.addTab(self.allTorqueVars,"Torque")
        self.allEVars=QTextEdit();self.allEVars.setReadOnly(True);tabs.addTab(self.allEVars,"Battery")
        self.allWVars=QTextEdit();self.allWVars.setReadOnly(True);tabs.addTab(self.allWVars,"Winch")
        self.allStabilityVars=QTextEdit();self.allStabilityVars.setReadOnly(True);tabs.addTab(self.allStabilityVars,"Stability")
        self.allSafetyVars=QTextEdit();self.allSafetyVars.setReadOnly(True);tabs.addTab(self.allSafetyVars,"Control Logic")
        root.addWidget(tabs,1)
        self.update_all_variable_tables()

    # =====================================================================
    # CONTROL / SAFETY LOGIC SIMULATOR
    # =====================================================================
    def make_safety_logic_simulator(self):
        w=QWidget();self.safetyPage=w
        root=QVBoxLayout(w);root.setContentsMargins(16,16,16,16);root.setSpacing(11)
        root.addWidget(make_page_header(
            "CONTROL LOGIC SIMULATOR",
            "จำลอง Logic ก่อนลง ESP32 • Drive/Crane Interlock • E-stop • RC Failsafe • IMU • Limit Switch",
            self.show_home_mode,"SAFETY / ESP32","#fff3e8","#c45114"
        ))

        note=QLabel(
            "หน้านี้เป็น Logic Simulator สำหรับตรวจเงื่อนไขควบคุม ไม่ได้สั่งฮาร์ดแวร์จริง "
            "ค่าทุกอย่างเป็นการจำลองเพื่อใช้ตรวจ Flow ก่อนนำ Logic ไปเขียนลง ESP32"
        )
        note.setWordWrap(True)
        note.setStyleSheet("background:#fff8ed;color:#6b3b0d;padding:9px 12px;border:1px solid #f3d3aa;border-radius:9px;")
        root.addWidget(note)

        body=QSplitter(Qt.Horizontal);body.setChildrenCollapsible(False);body.setHandleWidth(6)

        inp=QGroupBox("INPUT SIMULATOR / จำลองสัญญาณเข้า")
        il=QFormLayout(inp);il.setLabelAlignment(Qt.AlignRight);il.setFormAlignment(Qt.AlignTop)
        il.setRowWrapPolicy(QFormLayout.WrapLongRows);il.setFieldGrowthPolicy(QFormLayout.AllNonFixedFieldsGrow)
        il.setVerticalSpacing(7);il.setHorizontalSpacing(9)

        self.safetyEStop=QCheckBox("E-STOP ACTIVE")
        self.safetyRCSignal=QCheckBox("RC / IBUS signal OK");self.safetyRCSignal.setChecked(True)
        self.safetyDriveEnable=QCheckBox("CH5 Drive Enable");self.safetyDriveEnable.setChecked(True)
        self.safetyBatteryLow=QCheckBox("Battery Low")
        self.safetyBatteryInhibit=QCheckBox("Low battery inhibits drive")
        self.safetyLimitLeft=QCheckBox("Left limit (-90°) ACTIVE")
        self.safetyLimitRight=QCheckBox("Right limit (+90°) ACTIVE")
        self.safetyWinchStationaryOnly=QCheckBox("Winch only when vehicle stationary");self.safetyWinchStationaryOnly.setChecked(True)

        self.safetyThrottle=QSlider(Qt.Horizontal);self.safetyThrottle.setRange(-100,100);self.safetyThrottle.setValue(0)
        self.safetyThrottleLabel=QLabel("0 %");self.safetyThrottleLabel.setFixedWidth(48);self.safetyThrottleLabel.setAlignment(Qt.AlignRight|Qt.AlignVCenter)
        thw=QWidget();thl=QHBoxLayout(thw);thl.setContentsMargins(0,0,0,0);thl.addWidget(self.safetyThrottle);thl.addWidget(self.safetyThrottleLabel)

        self.safetySteer=QSlider(Qt.Horizontal);self.safetySteer.setRange(-100,100);self.safetySteer.setValue(0)
        self.safetySteerLabel=QLabel("0 %");self.safetySteerLabel.setFixedWidth(48);self.safetySteerLabel.setAlignment(Qt.AlignRight|Qt.AlignVCenter)
        stw=QWidget();stl=QHBoxLayout(stw);stl.setContentsMargins(0,0,0,0);stl.addWidget(self.safetySteer);stl.addWidget(self.safetySteerLabel)

        self.safetyCraneCmd=QComboBox();self.safetyCraneCmd.addItems(["STOP","LEFT (-)","RIGHT (+)"])
        self.safetyWinchCmd=QComboBox();self.safetyWinchCmd.addItems(["STOP","UP","DOWN"])
        self.safetyTilt=spin(0,-45,45,1,1)
        self.safetyTiltLimit=spin(12,1,45,1,1)

        il.addRow("Emergency stop",self.safetyEStop)
        il.addRow("RC receiver",self.safetyRCSignal)
        il.addRow("Drive enable / CH5",self.safetyDriveEnable)
        il.addRow("Throttle",thw)
        il.addRow("Steering",stw)
        il.addRow("Crane command",self.safetyCraneCmd)
        il.addRow("Winch command",self.safetyWinchCmd)
        il.addRow("IMU tilt (deg)",self.safetyTilt)
        il.addRow("Tilt inhibit limit (deg)",self.safetyTiltLimit)
        il.addRow("Left limit",self.safetyLimitLeft)
        il.addRow("Right limit",self.safetyLimitRight)
        il.addRow("Battery warning",self.safetyBatteryLow)
        il.addRow("Battery policy",self.safetyBatteryInhibit)
        il.addRow("Winch interlock",self.safetyWinchStationaryOnly)

        reset=QPushButton("Reset Simulator Inputs")
        reset.setObjectName("secondaryButton");reset.clicked.connect(self.reset_safety_simulator)
        il.addRow("",reset)
        inpScroll=QScrollArea();inpScroll.setWidgetResizable(True);inpScroll.setFrameShape(QFrame.NoFrame)
        inpScroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff);inpScroll.setWidget(inp);inpScroll.setMinimumWidth(250)
        body.addWidget(inpScroll)

        stateBox=QGroupBox("SYSTEM STATE / สถานะ Logic");stateBox.setMinimumWidth(275)
        sl=QVBoxLayout(stateBox);sl.setSpacing(9)
        self.safetyStateLabel=QLabel("READY")
        self.safetyStateLabel.setAlignment(Qt.AlignCenter);self.safetyStateLabel.setMinimumHeight(64)
        self.safetyStateLabel.setStyleSheet("font-size:18pt;font-weight:900;background:#eaf8ef;color:#176337;border:1px solid #a9ddba;border-radius:12px;")
        sl.addWidget(self.safetyStateLabel)

        self.safetyReason=QLabel("ระบบพร้อมรับคำสั่ง")
        self.safetyReason.setWordWrap(True);self.safetyReason.setAlignment(Qt.AlignCenter)
        self.safetyReason.setStyleSheet("font-size:10pt;font-weight:700;color:#4b6177;padding:6px;")
        sl.addWidget(self.safetyReason)

        self.safetyLogicFlow=QTextEdit();self.safetyLogicFlow.setReadOnly(True)
        self.safetyLogicFlow.setHtml("""
        <h3>Logic หลักที่จำลอง</h3>
        <p><b>1. E-stop</b> → Drive OFF + Crane OFF + Winch OFF</p>
        <p><b>2. RC/IBUS Lost</b> → Failsafe → คำสั่งขับเป็น 0</p>
        <p><b>3. IMU Tilt ≥ Limit</b> → Drive INHIBIT + Buzzer/LED</p>
        <p><b>4. Drive + Crane พร้อมกัน</b> → Interlock → ปฏิเสธทั้งสองคำสั่ง</p>
        <p><b>5. รถกำลังวิ่ง</b> → ห้ามหมุนเครน</p>
        <p><b>6. เครนกำลังหมุน</b> → ห้าม Drive</p>
        <p><b>7. Limit ±90°</b> → ห้ามหมุนต่อเข้า Limit แต่ยังหมุนย้อนออกได้</p>
        <p><b>8. Differential steering</b> → Steering อย่างเดียวสามารถ Pivot Turn (L/R motor คนละทิศ)</p>
        <p><b>9. Battery Low policy</b> → ถ้าเลือก Inhibit จะล็อก Drive; Crane/Winch ยังผ่าน interlock ของตน</p>
        <p><b>10. Buzzer + LED</b> → ON ขณะเคลื่อนที่ หรือเมื่อเกิด Fault/Warning</p>
        """)
        sl.addWidget(self.safetyLogicFlow,1)
        body.addWidget(stateBox)

        out=QGroupBox("OUTPUT / ผลจาก Logic");out.setMinimumWidth(220)
        ol=QFormLayout(out);ol.setLabelAlignment(Qt.AlignRight)
        ol.setRowWrapPolicy(QFormLayout.WrapLongRows);ol.setFieldGrowthPolicy(QFormLayout.AllNonFixedFieldsGrow)
        ol.setVerticalSpacing(7);ol.setHorizontalSpacing(8)

        def out_label():
            x=QLabel("-");x.setMinimumWidth(125);x.setAlignment(Qt.AlignCenter)
            x.setStyleSheet("font-weight:900;background:#f5f8fc;border:1px solid #d5dfeb;border-radius:7px;padding:7px;")
            return x

        self.safetyDrivePermit=out_label()
        self.safetyLeftMotor=out_label()
        self.safetyRightMotor=out_label()
        self.safetyCraneOut=out_label()
        self.safetyWinchOut=out_label()
        self.safetyBuzzerOut=out_label()
        self.safetyLEDOut=out_label()

        ol.addRow("Drive Permit",self.safetyDrivePermit)
        ol.addRow("Left Motor",self.safetyLeftMotor)
        ol.addRow("Right Motor",self.safetyRightMotor)
        ol.addRow("Crane Motor",self.safetyCraneOut)
        ol.addRow("Winch Permit",self.safetyWinchOut)
        ol.addRow("Buzzer",self.safetyBuzzerOut)
        ol.addRow("LED",self.safetyLEDOut)

        test=QPushButton("RUN SAFETY SELF-TEST")
        test.setObjectName("primaryButton");test.clicked.connect(self.run_safety_self_tests)
        ol.addRow("",test)
        body.addWidget(out)
        body.setStretchFactor(0,11);body.setStretchFactor(1,10);body.setStretchFactor(2,8)
        body.setSizes([330,360,260])
        root.addWidget(body,3)

        lower=QTabWidget()
        logPage=QWidget();ll=QVBoxLayout(logPage);ctl=QHBoxLayout()
        clear=QPushButton("Clear Event Log");clear.clicked.connect(lambda:self.safetyEventLog.clear())
        ctl.addWidget(QLabel("Event Log — บันทึกเมื่อสถานะหรือ Output เปลี่ยน"));ctl.addStretch(1);ctl.addWidget(clear);ll.addLayout(ctl)
        self.safetyEventLog=QTextEdit();self.safetyEventLog.setReadOnly(True);self.safetyEventLog.setMaximumHeight(180);ll.addWidget(self.safetyEventLog)
        lower.addTab(logPage,"Event Log")

        testPage=QWidget();tl=QVBoxLayout(testPage)
        self.safetyTestResults=QTextEdit();self.safetyTestResults.setReadOnly(True)
        self.safetyTestResults.setHtml("<h3>Safety Self-Test</h3><p>กด <b>RUN SAFETY SELF-TEST</b> เพื่อทดสอบชุดสถานการณ์มาตรฐานอัตโนมัติ</p>")
        tl.addWidget(self.safetyTestResults)
        lower.addTab(testPage,"Self-Test Results")

        varPage=QWidget();vl=QVBoxLayout(varPage)
        self.safetyVars=QTextEdit();self.safetyVars.setReadOnly(True);vl.addWidget(self.safetyVars)
        lower.addTab(varPage,"ตัวแปร / Variables")
        self.safetyLowerTabs=lower
        lower.setMinimumHeight(170)
        root.addWidget(lower,1)

        for obj in (self.safetyEStop,self.safetyRCSignal,self.safetyDriveEnable,
                    self.safetyBatteryLow,self.safetyBatteryInhibit,
                    self.safetyLimitLeft,self.safetyLimitRight,self.safetyWinchStationaryOnly):
            obj.toggled.connect(self.update_safety_logic)
        self.safetyThrottle.valueChanged.connect(self.update_safety_logic)
        self.safetySteer.valueChanged.connect(self.update_safety_logic)
        self.safetyCraneCmd.currentIndexChanged.connect(self.update_safety_logic)
        self.safetyWinchCmd.currentIndexChanged.connect(self.update_safety_logic)
        self.safetyTilt.valueChanged.connect(self.update_safety_logic)
        self.safetyTiltLimit.valueChanged.connect(self.update_safety_logic)

        self._lastSafetySignature=None
        self.update_safety_logic(log_event=False)

    def safety_input_values(self):
        return {
            "estop":self.safetyEStop.isChecked(),
            "rc_ok":self.safetyRCSignal.isChecked(),
            "drive_enable":self.safetyDriveEnable.isChecked(),
            "throttle":int(self.safetyThrottle.value()),
            "steer":int(self.safetySteer.value()),
            "crane":self.safetyCraneCmd.currentText(),
            "winch":self.safetyWinchCmd.currentText(),
            "tilt":float(self.safetyTilt.value()),
            "tilt_limit":max(.1,float(self.safetyTiltLimit.value())),
            "left_limit":self.safetyLimitLeft.isChecked(),
            "right_limit":self.safetyLimitRight.isChecked(),
            "battery_low":self.safetyBatteryLow.isChecked(),
            "battery_inhibit":self.safetyBatteryInhibit.isChecked(),
            "winch_stationary_only":self.safetyWinchStationaryOnly.isChecked(),
        }

    @staticmethod
    def evaluate_safety_logic(v):
        clamp=lambda x:max(-100,min(100,int(round(x))))
        result={
            "state":"READY","reason":"ระบบพร้อมรับคำสั่ง",
            "drive_permit":False,"drive_active":False,"left_motor":0,"right_motor":0,
            "crane":"STOP","winch":"STOP","buzzer":False,"led":False
        }

        if v.get("estop",False):
            result.update(state="E-STOP",reason="Emergency Stop ทำงาน — ตัดคำสั่งการเคลื่อนที่ทั้งหมด",buzzer=True,led=True)
            return result
        if not v.get("rc_ok",True):
            result.update(state="RC FAILSAFE",reason="สัญญาณ RC / IBUS หาย — คำสั่งทั้งหมดกลับ Safe State",buzzer=True,led=True)
            return result

        throttle=int(v.get("throttle",0))
        steer=int(v.get("steer",0))
        crane=str(v.get("crane","STOP"))
        winch=str(v.get("winch","STOP"))
        # Differential steering allows pivot-turn with steering even at zero throttle.
        drive_req=abs(throttle)>2 or abs(steer)>2
        crane_req=crane!="STOP"
        winch_req=winch!="STOP"
        tilt_fault=abs(float(v.get("tilt",0)))>=float(v.get("tilt_limit",12))
        drive_enabled=bool(v.get("drive_enable",True))
        battery_drive_inhibit=bool(v.get("battery_low",False) and v.get("battery_inhibit",False))

        if drive_req and crane_req:
            result.update(
                state="INTERLOCK CONFLICT",
                reason="มีคำสั่ง Drive และ Crane พร้อมกัน — ปฏิเสธทั้งสองคำสั่งเพื่อความปลอดภัย",
                buzzer=True,led=True
            )
            return result

        result["drive_permit"]=drive_enabled and not tilt_fault and not crane_req and not battery_drive_inhibit

        if drive_req:
            if not drive_enabled:
                result.update(state="DRIVE DISABLED",reason="CH5 / Drive Enable = OFF",drive_permit=False)
            elif battery_drive_inhibit:
                result.update(state="LOW BATTERY INHIBIT",reason="Battery Low — ล็อกเฉพาะ Drive ตาม Battery Policy",drive_permit=False,buzzer=True,led=True)
            elif tilt_fault:
                result.update(state="TILT INHIBIT",reason=f"IMU tilt {float(v.get('tilt',0)):.1f}° ถึง/เกิน Limit {float(v.get('tilt_limit',12)):.1f}° — ห้าม Drive",drive_permit=False,buzzer=True,led=True)
            else:
                left=clamp(throttle+steer)
                right=clamp(throttle-steer)
                result.update(
                    state="DRIVE",
                    reason="Drive Enable ผ่าน และไม่มี Fault / Crane command",
                    drive_permit=True,drive_active=True,left_motor=left,right_motor=right,
                    buzzer=True,led=True
                )

        elif crane_req:
            result["drive_permit"]=False
            blocked=False
            if crane.startswith("LEFT") and v.get("left_limit",False):
                blocked=True
                result.update(state="LEFT LIMIT STOP",reason="ถึง Limit -90° — ห้ามหมุน LEFT ต่อ แต่ยังสั่ง RIGHT เพื่อออกจาก Limit ได้",buzzer=True,led=True)
            elif crane.startswith("RIGHT") and v.get("right_limit",False):
                blocked=True
                result.update(state="RIGHT LIMIT STOP",reason="ถึง Limit +90° — ห้ามหมุน RIGHT ต่อ แต่ยังสั่ง LEFT เพื่อออกจาก Limit ได้",buzzer=True,led=True)
            if not blocked:
                result.update(state="CRANE",reason=f"อนุญาตให้เครนหมุน {crane}",crane=crane,buzzer=True,led=True)

        else:
            if not drive_enabled:
                result.update(state="DRIVE DISABLED",reason="CH5 / Drive Enable = OFF — Crane/Winch ยังตรวจตาม interlock ของตน",drive_permit=False)
            elif battery_drive_inhibit:
                result.update(state="LOW BATTERY INHIBIT",reason="Battery Low — Drive ถูกล็อกตาม Battery Policy",drive_permit=False,buzzer=True,led=True)
            elif tilt_fault:
                result.update(state="TILT WARNING",reason=f"IMU tilt {float(v.get('tilt',0)):.1f}° ถึง/เกิน Limit — Drive จะถูก Inhibit",drive_permit=False,buzzer=True,led=True)
            elif v.get("battery_low",False):
                result.update(state="BATTERY WARNING",reason="Battery Low — แจ้งเตือน แต่ยังไม่ Inhibit เพราะ Battery Policy = Warning only",buzzer=True,led=True)

        if winch_req:
            movement_active=result["drive_active"] or result["crane"]!="STOP" or drive_req or crane_req
            if v.get("winch_stationary_only",True) and movement_active:
                result["reason"] += " | Winch ถูกปฏิเสธเพราะกำหนดให้ใช้เฉพาะตอนรถ/เครนหยุด"
            else:
                result["winch"]=winch
                result["drive_permit"]=False
                if result["state"] in ("READY","BATTERY WARNING","TILT WARNING","DRIVE DISABLED","LOW BATTERY INHIBIT"):
                    result["state"]="WINCH"
                    result["reason"]=f"อนุญาต Winch {winch} ขณะรถและเครนหยุด"
                result["buzzer"]=True;result["led"]=True

        return result

    @staticmethod
    def _safety_out_style(on,warning=False):
        if warning:
            return "font-weight:900;background:#fff1e8;color:#b54708;border:1px solid #f2b27f;border-radius:7px;padding:7px;"
        if on:
            return "font-weight:900;background:#eaf8ef;color:#176337;border:1px solid #a9ddba;border-radius:7px;padding:7px;"
        return "font-weight:900;background:#f5f8fc;color:#536579;border:1px solid #d5dfeb;border-radius:7px;padding:7px;"

    def update_safety_logic(self,*args,log_event=True):
        if not hasattr(self,"safetyStateLabel"):
            return
        v=self.safety_input_values()
        r=self.evaluate_safety_logic(v)

        self.safetyThrottleLabel.setText(f"{v['throttle']:+d} %")
        self.safetySteerLabel.setText(f"{v['steer']:+d} %")

        state_colors={
            "READY":("#eaf8ef","#176337","#a9ddba"),
            "DRIVE":("#e8f1ff","#1756a9","#a9c8ef"),
            "CRANE":("#f3eaff","#6b34a5","#cbb0ea"),
            "WINCH":("#fff6df","#9a5a00","#efd08b"),
            "BATTERY WARNING":("#fff6df","#9a5a00","#efd08b"),
            "TILT WARNING":("#fff1e8","#b54708","#f2b27f"),
        }
        bg,fg,bd=state_colors.get(r["state"],("#fff0f0","#b42318","#efb2ad"))
        self.safetyStateLabel.setText(r["state"])
        self.safetyStateLabel.setStyleSheet(f"font-size:18pt;font-weight:900;background:{bg};color:{fg};border:1px solid {bd};border-radius:12px;")
        self.safetyReason.setText(r["reason"])

        self.safetyDrivePermit.setText("ENABLE" if r["drive_permit"] else "LOCKED")
        self.safetyDrivePermit.setStyleSheet(self._safety_out_style(r["drive_permit"]))
        self.safetyLeftMotor.setText(f"{r['left_motor']:+d} %")
        self.safetyRightMotor.setText(f"{r['right_motor']:+d} %")
        self.safetyLeftMotor.setStyleSheet(self._safety_out_style(r["left_motor"]!=0))
        self.safetyRightMotor.setStyleSheet(self._safety_out_style(r["right_motor"]!=0))
        self.safetyCraneOut.setText(r["crane"])
        self.safetyCraneOut.setStyleSheet(self._safety_out_style(r["crane"]!="STOP"))
        self.safetyWinchOut.setText(r["winch"])
        self.safetyWinchOut.setStyleSheet(self._safety_out_style(r["winch"]!="STOP"))
        self.safetyBuzzerOut.setText("ON" if r["buzzer"] else "OFF")
        self.safetyLEDOut.setText("ON" if r["led"] else "OFF")
        warning=r["state"] not in ("READY","DRIVE","CRANE","WINCH")
        self.safetyBuzzerOut.setStyleSheet(self._safety_out_style(r["buzzer"],warning))
        self.safetyLEDOut.setStyleSheet(self._safety_out_style(r["led"],warning))

        signature=(r["state"],r["drive_permit"],r["left_motor"],r["right_motor"],r["crane"],r["winch"],r["buzzer"],r["led"],r["reason"])
        if log_event and signature!=getattr(self,"_lastSafetySignature",None):
            ts=datetime.now().strftime("%H:%M:%S")
            self.safetyEventLog.append(
                f"[{ts}] {r['state']} | Drive={'ON' if r['drive_permit'] else 'OFF'} "
                f"| L={r['left_motor']:+d}% R={r['right_motor']:+d}% "
                f"| Crane={r['crane']} | Winch={r['winch']} | {r['reason']}"
            )
        self._lastSafetySignature=signature
        if hasattr(self,"safetyVars"):self.safetyVars.setHtml(self.safety_variables_html())
        if hasattr(self,"allSafetyVars"):self.allSafetyVars.setHtml(self.safety_variables_html())

    def reset_safety_simulator(self):
        self.safetyEStop.setChecked(False)
        self.safetyRCSignal.setChecked(True)
        self.safetyDriveEnable.setChecked(True)
        self.safetyThrottle.setValue(0)
        self.safetySteer.setValue(0)
        self.safetyCraneCmd.setCurrentIndex(0)
        self.safetyWinchCmd.setCurrentIndex(0)
        self.safetyTilt.setValue(0)
        self.safetyTiltLimit.setValue(12)
        self.safetyLimitLeft.setChecked(False)
        self.safetyLimitRight.setChecked(False)
        self.safetyBatteryLow.setChecked(False)
        self.safetyBatteryInhibit.setChecked(False)
        self.safetyWinchStationaryOnly.setChecked(True)
        self.update_safety_logic()

    def run_safety_self_tests(self):
        base={
            "estop":False,"rc_ok":True,"drive_enable":True,"throttle":0,"steer":0,
            "crane":"STOP","winch":"STOP","tilt":0.0,"tilt_limit":12.0,
            "left_limit":False,"right_limit":False,"battery_low":False,
            "battery_inhibit":False,"winch_stationary_only":True
        }
        tests=[
            ("READY — ไม่มีคำสั่ง",{},lambda r:r["state"]=="READY" and r["drive_permit"]),
            ("DRIVE — Throttle 50%",{"throttle":50},lambda r:r["state"]=="DRIVE" and r["left_motor"]==50 and r["right_motor"]==50),
            ("PIVOT TURN — Steering only",{"steer":40},lambda r:r["state"]=="DRIVE" and r["left_motor"]==40 and r["right_motor"]==-40),
            ("INTERLOCK — Drive + Crane",{"steer":40,"crane":"RIGHT (+)"},lambda r:r["state"]=="INTERLOCK CONFLICT" and not r["drive_permit"] and r["crane"]=="STOP"),
            ("E-STOP",{"estop":True,"throttle":60},lambda r:r["state"]=="E-STOP" and not r["drive_permit"]),
            ("RC FAILSAFE",{"rc_ok":False,"throttle":60},lambda r:r["state"]=="RC FAILSAFE" and not r["drive_permit"]),
            ("IMU TILT INHIBIT",{"throttle":50,"tilt":15},lambda r:r["state"]=="TILT INHIBIT" and not r["drive_permit"]),
            ("RIGHT LIMIT BLOCK",{"crane":"RIGHT (+)","right_limit":True},lambda r:r["state"]=="RIGHT LIMIT STOP" and r["crane"]=="STOP"),
            ("MOVE AWAY FROM RIGHT LIMIT",{"crane":"LEFT (-)","right_limit":True},lambda r:r["state"]=="CRANE" and r["crane"].startswith("LEFT")),
            ("LOW BATTERY DRIVE INHIBIT",{"battery_low":True,"battery_inhibit":True,"throttle":40},lambda r:r["state"]=="LOW BATTERY INHIBIT" and not r["drive_permit"]),
            ("LOW BATTERY STILL ALLOWS CRANE",{"battery_low":True,"battery_inhibit":True,"crane":"LEFT (-)"},lambda r:r["state"]=="CRANE" and r["crane"].startswith("LEFT")),
            ("WINCH STATIONARY",{"winch":"UP"},lambda r:r["state"]=="WINCH" and r["winch"]=="UP" and not r["drive_permit"]),
            ("WINCH BLOCKED WHILE DRIVE",{"throttle":50,"winch":"UP"},lambda r:r["state"]=="DRIVE" and r["winch"]=="STOP"),
        ]
        rows=[];passed=0
        for name,changes,check in tests:
            v=dict(base);v.update(changes)
            r=self.evaluate_safety_logic(v)
            ok=bool(check(r));passed+=int(ok)
            rows.append(
                f"<tr><td>{name}</td><td style='font-weight:800;color:{'#176337' if ok else '#b42318'}'>{'PASS' if ok else 'FAIL'}</td>"
                f"<td>{r['state']}</td><td>{r['reason']}</td></tr>"
            )
        self.safetyTestResults.setHtml(
            f"<h2>SAFETY LOGIC SELF-TEST</h2>"
            f"<p><b>ผลรวม: {passed}/{len(tests)} tests passed</b></p>"
            "<table cellpadding='6' cellspacing='0' border='1' style='border-collapse:collapse'>"
            "<tr style='background:#eef4fb'><th>Scenario</th><th>Result</th><th>State</th><th>Reason</th></tr>"
            + "".join(rows) + "</table>"
            "<p><b>หมายเหตุ:</b> Self-test นี้ตรวจ Logic ในโปรแกรม ไม่ใช่การทดสอบฮาร์ดแวร์จริงของ ESP32, VESC, Relay หรือ Limit Switch</p>"
        )
        self.safetyLowerTabs.setCurrentIndex(1)

    def make_project_tools(self):
        w=QWidget();self.projectToolsPage=w
        root=QVBoxLayout(w);root.setContentsMargins(16,16,16,16);root.setSpacing(12)
        root.addWidget(make_page_header("PROJECT TOOLS / ENGINEERING SUITE",
            "Save/Load • Presets • Compare Design • Design Check • Motor • BMS • Winch Duty • Final Report",
            self.show_home_mode,"V51 TOOLS","#e8f4ff","#174a74"))
        self.projectTabs=QTabWidget();root.addWidget(self.projectTabs)
        self.compareA=None;self.compareB=None

        # 1) PROJECT FILE + PRESETS
        # Easy autosave is intentionally shown only on HOME to avoid duplicate controls.
        pg=QWidget();pl=QVBoxLayout(pg)
        info=QLabel("ค่าที่กรอกถูกบันทึกอัตโนมัติจากหน้า Home แล้ว หน้านี้ใช้เฉพาะการเก็บ Project เป็นไฟล์ และ Preset เพิ่มเติม")
        info.setWordWrap(True)
        info.setStyleSheet("background:#eef6ff;color:#274c77;padding:10px;border:1px solid #cfe2f5;border-radius:8px")
        pl.addWidget(info)

        advancedBox=QGroupBox("Project File — Save/Load เป็นไฟล์ JSON")
        advancedLay=QHBoxLayout(advancedBox)
        save=QPushButton("Save Project As...");save.clicked.connect(self.save_project)
        load=QPushButton("Open Project File...");load.clicked.connect(self.load_project)
        advancedLay.addWidget(save);advancedLay.addWidget(load);advancedLay.addStretch(1)
        pl.addWidget(advancedBox)
        presetBox=QGroupBox("Scenario Presets / ชุดค่าตัวอย่างสำหรับสาธิต");grid=QGridLayout(presetBox)
        presets=[("Project Baseline","baseline"),("Full Load 300 kg","full_load"),("Ramp 19°","ramp19"),
                 ("Crane +90°","crane90"),("Apply Current Worst Angle","worst_angle"),("Presentation Demo","demo")]
        for i,(label,key) in enumerate(presets):
            b=QPushButton(label);b.clicked.connect(lambda checked=False,k=key:self.apply_scenario_preset(k));grid.addWidget(b,i//3,i%3)
        pl.addWidget(presetBox)
        self.projectStatus=QTextEdit();self.projectStatus.setReadOnly(True);self.projectStatus.setMaximumHeight(260);pl.addWidget(self.projectStatus)
        pl.addStretch(1);self.projectTabs.addTab(pg,"Project Files / Presets")

        # 2) DESIGN COMPARE
        cp=QWidget();cl=QVBoxLayout(cp)
        ctl=QHBoxLayout()
        self.compareALabel=QLineEdit("Design A");self.compareBLabel=QLineEdit("Design B")
        ca=QPushButton("Capture A / เก็บค่าปัจจุบันเป็น A");cb=QPushButton("Capture B / เก็บค่าปัจจุบันเป็น B")
        aa=QPushButton("Apply A");ab=QPushButton("Apply B");cmp=QPushButton("Compare / เปรียบเทียบ");cmp.setObjectName("primaryButton")
        ca.clicked.connect(lambda:self.capture_compare_design("A"));cb.clicked.connect(lambda:self.capture_compare_design("B"))
        aa.clicked.connect(lambda:self.apply_compare_design("A"));ab.clicked.connect(lambda:self.apply_compare_design("B"));cmp.clicked.connect(self.compare_designs)
        for x in (self.compareALabel,ca,aa,self.compareBLabel,cb,ab,cmp):ctl.addWidget(x)
        cl.addLayout(ctl)
        self.compareView=QTextEdit();self.compareView.setReadOnly(True);cl.addWidget(self.compareView)
        self.projectTabs.addTab(cp,"Compare Design")

        # 3) DESIGN CHECK
        dc=QWidget();dl=QVBoxLayout(dc)
        db=QPushButton("Recalculate Design Check / ตรวจแบบใหม่");db.setObjectName("primaryButton");db.clicked.connect(self.update_design_check);dl.addWidget(db)
        self.designCheckView=QTextEdit();self.designCheckView.setReadOnly(True);dl.addWidget(self.designCheckView)
        self.projectTabs.addTab(dc,"Design Check")

        # 4) MOTOR OPERATING CHECK
        mp=QWidget();ml=QVBoxLayout(mp)
        note=QLabel("กราฟนี้แสดง Required Operating Point เทียบกับค่าขีดจำกัดที่ผู้ใช้กรอก ไม่ใช่ Torque-Speed curve จากผู้ผลิต")
        note.setWordWrap(True);note.setStyleSheet("background:#fff8e9;color:#68420b;padding:10px;border:1px solid #ead39a;border-radius:9px");ml.addWidget(note)
        self.motorOpGraph=MotorOperatingGraphWidget(self);ml.addWidget(self.motorOpGraph,1)
        self.motorOpText=QTextEdit();self.motorOpText.setReadOnly(True);self.motorOpText.setMaximumHeight(210);ml.addWidget(self.motorOpText)
        self.projectTabs.addTab(mp,"Motor Operating")

        # 5) BATTERY + BMS
        bp=QWidget();bl=QHBoxLayout(bp)
        box=QGroupBox("Selected Battery / BMS Inputs");form=QFormLayout(box)
        self.mainSelectedAh=spin(0,0,2000,1,1);self.mainBMSCont=spin(0,0,2000,5,1);self.mainBMSPeak=spin(0,0,4000,5,1)
        self.winchSelectedAh=spin(0,0,1000,1,1);self.winchBMSCont=spin(0,0,2000,5,1);self.winchBMSPeak=spin(0,0,4000,5,1)
        for lab,obj in [("Main battery selected capacity (Ah; 0=not set)",self.mainSelectedAh),("Main BMS continuous (A; 0=not set)",self.mainBMSCont),
                        ("Main BMS peak (A; 0=not set)",self.mainBMSPeak),("Winch battery selected capacity (Ah; 0=not set)",self.winchSelectedAh),
                        ("Winch BMS continuous (A; 0=not set)",self.winchBMSCont),("Winch BMS peak (A; 0=not set)",self.winchBMSPeak)]:form.addRow(lab,obj)
        bl.addWidget(box,1)
        self.bmsView=QTextEdit();self.bmsView.setReadOnly(True);bl.addWidget(self.bmsView,2)
        for obj in (self.mainSelectedAh,self.mainBMSCont,self.mainBMSPeak,self.winchSelectedAh,self.winchBMSCont,self.winchBMSPeak):obj.valueChanged.connect(self.update_bms_check)
        self.projectTabs.addTab(bp,"Battery + BMS")

        # 6) WINCH DUTY CYCLE
        wp=QWidget();wl=QHBoxLayout(wp)
        wbox=QGroupBox("Duty Cycle Assumptions / สมมติฐาน");wf=QFormLayout(wbox)
        self.wDutyAllowed=spin(20,1,100,1,1);self.wDutyRest=spin(120,0,3600,10,1);self.wMaxContinuous=spin(60,1,3600,5,1)
        wf.addRow("Allowed duty cycle (%) [manufacturer value if known]",self.wDutyAllowed)
        wf.addRow("Cooling/rest time after each up+down cycle (s)",self.wDutyRest)
        wf.addRow("Maximum continuous run assumption (s)",self.wMaxContinuous)
        wl.addWidget(wbox,1)
        self.wDutyView=QTextEdit();self.wDutyView.setReadOnly(True);wl.addWidget(self.wDutyView,2)
        for obj in (self.wDutyAllowed,self.wDutyRest,self.wMaxContinuous):obj.valueChanged.connect(self.update_winch_duty)
        self.projectTabs.addTab(wp,"Winch Duty Cycle")

        # 7) FINAL REPORT
        rp=QWidget();rl=QVBoxLayout(rp)
        rr=QHBoxLayout();refresh=QPushButton("Refresh Preview");refresh.clicked.connect(self.update_final_report_preview)
        exp=QPushButton("Export FINAL Engineering PDF");exp.setObjectName("primaryButton");exp.clicked.connect(self.export_final_engineering_report)
        rr.addWidget(refresh);rr.addStretch(1);rr.addWidget(exp);rl.addLayout(rr)
        self.finalReportPreview=QTextEdit();self.finalReportPreview.setReadOnly(True);rl.addWidget(self.finalReportPreview)
        self.projectTabs.addTab(rp,"Final Report")

        self.projectTabs.currentChanged.connect(lambda i:self.update_project_tools())
        self.tabs.addTab(w,"Project Tools")
        self.update_project_tools()

    def _core_recalculate(self):
        self.calc_torque();self.calc_electrical();self.calc_winch();self.calc_all()


    # =====================================================================
    # V44 — EASY AUTO SAVE
    # =====================================================================
    def last_values_path(self):
        """Writable per-user location that also works after installation in Program Files."""
        base=QStandardPaths.writableLocation(QStandardPaths.AppDataLocation)
        folder=Path(base) if base else (Path.home()/".CraneVehicleEngineeringTool")
        folder.mkdir(parents=True,exist_ok=True)
        return folder/"last_values.json"

    def _set_quick_save_status(self,text,color="#66788a"):
        if hasattr(self,"quickSaveStatus"):
            self.quickSaveStatus.setText(str(text))
            self.quickSaveStatus.setStyleSheet(f"color:{color};font-size:8.5pt;")

    def save_last_values(self,silent=True):
        """Save current inputs without asking for a filename."""
        try:
            path=self.last_values_path()
            state=self.capture_project_state()
            path.write_text(json.dumps(state,ensure_ascii=False,indent=2),encoding="utf-8")
            stamp=datetime.now().strftime("%H:%M:%S")
            self._set_quick_save_status(f"บันทึกค่าล่าสุดแล้ว • {stamp} • เปิดโปรแกรมครั้งหน้าจะโหลดให้อัตโนมัติ","#176337")
            if hasattr(self,"projectStatus") and not silent:
                self.projectStatus.setHtml(f"<h3>บันทึกค่าปัจจุบันแล้ว</h3><p>โปรแกรมจะโหลดชุดค่านี้อัตโนมัติครั้งถัดไป</p><p>{path}</p>")
            return True
        except Exception as exc:
            self._set_quick_save_status("บันทึกอัตโนมัติไม่สำเร็จ: "+str(exc),"#b42318")
            if not silent:
                QMessageBox.warning(self,"บันทึกค่าล่าสุดไม่สำเร็จ",str(exc))
            return False

    def restore_last_values(self,silent=True):
        """Restore the last saved inputs automatically or by one click."""
        try:
            path=self.last_values_path()
            if not path.exists():
                self._set_quick_save_status("ยังไม่มีค่าที่บันทึกไว้ • กรอกค่าตามต้องการ โปรแกรมจะจำให้อัตโนมัติ")
                if not silent:
                    QMessageBox.information(self,"โหลดค่าล่าสุด","ยังไม่มีค่าที่บันทึกไว้")
                return False
            state=json.loads(path.read_text(encoding="utf-8"))
            self.apply_project_state(state,True)
            saved_at=state.get("saved_at","-")
            self._set_quick_save_status(f"โหลดค่าครั้งล่าสุดแล้ว • Saved at {saved_at}","#176337")
            if hasattr(self,"projectStatus") and not silent:
                self.projectStatus.setHtml(f"<h3>โหลดค่าล่าสุดแล้ว</h3><p>Saved at: {saved_at}</p><p>{path}</p>")
            return True
        except Exception as exc:
            self._set_quick_save_status("โหลดค่าล่าสุดไม่สำเร็จ: "+str(exc),"#b42318")
            if not silent:
                QMessageBox.warning(self,"โหลดค่าล่าสุดไม่สำเร็จ",str(exc))
            return False

    def clear_last_values(self):
        """Forget only the automatic last-values snapshot; normal Project JSON files are untouched."""
        ans=QMessageBox.question(self,"ล้างค่าที่จำ",
            "ต้องการล้างค่าที่โปรแกรมจำอัตโนมัติหรือไม่?\nไฟล์ Project JSON ที่คุณบันทึกเองจะไม่ถูกลบ",
            QMessageBox.Yes|QMessageBox.No,QMessageBox.No)
        if ans!=QMessageBox.Yes:
            return
        try:
            path=self.last_values_path()
            if path.exists():
                path.unlink()
            self._set_quick_save_status("ล้างค่าที่จำแล้ว • โปรแกรมจะเริ่มจากค่ามาตรฐานในการเปิดครั้งถัดไป")
        except Exception as exc:
            QMessageBox.warning(self,"ล้างค่าที่จำไม่สำเร็จ",str(exc))

    def schedule_easy_autosave(self,*args):
        """Debounce rapid edits so disk is not written on every arrow-key click."""
        if hasattr(self,"easyAutoSaveDebounce"):
            self.easyAutoSaveDebounce.start(1200)

    def setup_easy_autosave(self):
        # Save 1.2 s after the user stops editing any primary input.
        self.easyAutoSaveDebounce=QTimer(self)
        self.easyAutoSaveDebounce.setSingleShot(True)
        self.easyAutoSaveDebounce.timeout.connect(lambda:self.save_last_values(silent=True))

        for name,obj in list(vars(self).items()):
            try:
                if isinstance(obj,(QDoubleSpinBox,QSpinBox)):
                    obj.valueChanged.connect(self.schedule_easy_autosave)
                elif isinstance(obj,(QCheckBox,QRadioButton)):
                    obj.toggled.connect(self.schedule_easy_autosave)
                elif isinstance(obj,QComboBox):
                    obj.currentIndexChanged.connect(self.schedule_easy_autosave)
                elif isinstance(obj,QLineEdit):
                    obj.editingFinished.connect(self.schedule_easy_autosave)
            except Exception:
                pass

        # Periodic safety save in case the program is left open for a long time.
        self.easyAutoSavePeriodic=QTimer(self)
        self.easyAutoSavePeriodic.timeout.connect(lambda:self.save_last_values(silent=True))
        self.easyAutoSavePeriodic.start(60000)

    def closeEvent(self,event):
        # Always save once more when the program closes normally.
        self.save_last_values(silent=True)
        event.accept()

    def capture_project_state(self):
        widgets={}
        for name,obj in vars(self).items():
            if name.startswith("compare") or name.startswith("projectStatus"):
                continue
            try:
                if isinstance(obj,QDoubleSpinBox): widgets[name]={"kind":"double","value":obj.value()}
                elif isinstance(obj,QSpinBox): widgets[name]={"kind":"int","value":obj.value()}
                elif isinstance(obj,QRadioButton): widgets[name]={"kind":"radio","value":obj.isChecked()}
                elif isinstance(obj,QCheckBox): widgets[name]={"kind":"check","value":obj.isChecked()}
                elif isinstance(obj,QComboBox): widgets[name]={"kind":"combo","value":obj.currentIndex()}
                elif isinstance(obj,QLineEdit): widgets[name]={"kind":"text","value":obj.text()}
            except Exception:
                pass
        components=[]
        if hasattr(self,"comp"):
            for r in range(self.comp.rowCount()):
                components.append([self.comp.item(r,c).text() if self.comp.item(r,c) else "" for c in range(self.comp.columnCount())])
        return {"format":"CraneVehicleEngineeringToolProject","version":APP_VERSION,
                "saved_at":datetime.now().isoformat(timespec="seconds"),"widgets":widgets,"components":components}

    def apply_project_state(self,state,recalculate=True):
        if not isinstance(state,dict) or state.get("format")!="CraneVehicleEngineeringToolProject":
            raise ValueError("ไฟล์นี้ไม่ใช่ Project file ของ Crane Vehicle Engineering Tool")
        widgets=state.get("widgets",{})
        # Radio buttons: apply checked item only to preserve exclusivity.
        for name,data in widgets.items():
            obj=getattr(self,name,None)
            if obj is None or not isinstance(data,dict): continue
            kind=data.get("kind");val=data.get("value")
            try:
                obj.blockSignals(True)
                if kind=="radio":
                    if bool(val): obj.setChecked(True)
                elif kind=="double" and isinstance(obj,QDoubleSpinBox): obj.setValue(float(val))
                elif kind=="int" and isinstance(obj,QSpinBox): obj.setValue(int(val))
                elif kind=="check" and isinstance(obj,QCheckBox): obj.setChecked(bool(val))
                elif kind=="combo" and isinstance(obj,QComboBox): obj.setCurrentIndex(int(val))
                elif kind=="text" and isinstance(obj,QLineEdit): obj.setText(str(val))
            except Exception:
                pass
            finally:
                try: obj.blockSignals(False)
                except Exception: pass
        comps=state.get("components",[])
        if hasattr(self,"comp") and comps:
            for r,row in enumerate(comps[:self.comp.rowCount()]):
                for c,val in enumerate(row[:self.comp.columnCount()]):self.comp.setItem(r,c,QTableWidgetItem(str(val)))
        # Sync derived wheel radius and mass mode after blocking signals.
        self.update_wheel_from_inches()
        if hasattr(self,"massModeSum") and self.massModeSum.isChecked(): self.apply_mass_mode()
        if recalculate:
            self._core_recalculate();self.update_project_tools()

    def save_project(self):
        filename,_=QFileDialog.getSaveFileName(self,"Save Engineering Project","CraneVehicle_Project.json","Project JSON (*.json)")
        if not filename:return
        if not filename.lower().endswith(".json"):filename+=".json"
        try:
            Path(filename).write_text(json.dumps(self.capture_project_state(),ensure_ascii=False,indent=2),encoding="utf-8")
            self.projectStatus.setHtml(f"<h3>บันทึกโครงการเรียบร้อย</h3><p>{filename}</p><p>บันทึก Input, ตัวเลือก, Battery/BMS assumptions และ Component CG table แล้ว</p>")
        except Exception as exc:QMessageBox.critical(self,"Save Project ไม่สำเร็จ",str(exc))

    def load_project(self):
        filename,_=QFileDialog.getOpenFileName(self,"Load Engineering Project","","Project JSON (*.json)")
        if not filename:return
        try:
            state=json.loads(Path(filename).read_text(encoding="utf-8"));self.apply_project_state(state,True)
            self.projectStatus.setHtml(f"<h3>เปิดโครงการเรียบร้อย</h3><p>{filename}</p><p>Saved version: {state.get('version','-')} | Saved at: {state.get('saved_at','-')}</p>")
        except Exception as exc:QMessageBox.critical(self,"Load Project ไม่สำเร็จ",str(exc))

    def slope_stability_results(self,d=None):
        """Uphill forward-driving tipping model about the rear axle."""
        d=self.inputs() if d is None else d
        alpha=math.radians(self.slope.value())
        h=max(0.0,self.hcg.value())
        acc=max(0.0,self.acc.value())
        xcg=d.get("driveXCG",d.get("xCG",0.0))
        rear=-d["WB"]/2
        rear_arm=xcg-rear
        normal_g=G*math.cos(alpha)
        tangential_g=G*math.sin(alpha)+acc
        overturn_per_mass=h*tangential_g
        resist_per_mass=max(0.0,rear_arm)*normal_g
        sf=resist_per_mass/overturn_per_mass if overturn_per_mass>1e-12 else 999
        shift_slope=h*math.tan(alpha)
        shift_acc=h*acc/max(G*math.cos(alpha),1e-9)
        shift_total=shift_slope+shift_acc
        margin=rear_arm-shift_total
        return dict(alpha=alpha,h=h,acc=acc,xcg=xcg,rear=rear,rear_arm=rear_arm,
                    shift_slope=shift_slope,shift_acc=shift_acc,shift_total=shift_total,
                    margin=margin,sf=sf,normal_g=normal_g,tangential_g=tangential_g)

    def stability_worst_scan(self):
        """Single source of truth for -90°..+90° Side/Front/Rear worst-case search."""
        d=self.inputs()
        records=[]
        for ang in range(-90,91):
            side=self.calc_side(d,theta=ang)[0]
            front,rear=self.longitudinal_sf_at(d,ang)
            records.extend(((side,ang,"Side"),(front,ang,"Front"),(rear,ang,"Rear")))
        records.sort(key=lambda x:x[0])
        return records

    def stability_worst_record(self):
        records=self.stability_worst_scan()
        return records[0] if records else (999,None,None)

    def apply_scenario_preset(self,key):
        if key=="baseline":
            self.tm.setValue(300);self.emass.setValue(290);self.mt.setValue(300);self.ml.setValue(100);self.mb.setValue(20)
            self.tgrade.setValue(19);self.eslopeDeg.setValue(12);self.slope.setValue(19);self.W.setValue(1.0);self.WB.setValue(1.10);self.L.setValue(1.20);self.th.setValue(0)
        elif key=="full_load":
            self.tm.setValue(300);self.emass.setValue(300);self.mt.setValue(300);self.ml.setValue(100)
        elif key=="ramp19":
            self.tgrade.setValue(19);self.eslopeDeg.setValue(19);self.slope.setValue(19)
        elif key=="crane90": self.th.setValue(90)
        elif key=="worst_angle":
            _,ang,_=self.stability_worst_record();self.th.setValue(float(ang))
        elif key=="demo":
            self.tm.setValue(300);self.mt.setValue(300);self.ml.setValue(100);self.tgrade.setValue(19);self.tspeed.setValue(5)
            self.W.setValue(1.0);self.WB.setValue(1.10);self.L.setValue(1.20);self.th.setValue(90);self.espeed.setValue(1);self.eslopeDeg.setValue(12)
            self.wmass.setValue(100);self.wheight.setValue(1.5);self.wvolt.setValue(12);self.wcycles.setValue(50)
        self._core_recalculate();self.update_project_tools()
        self.projectStatus.setHtml(f"<h3>Applied preset: {key}</h3><p>Preset เป็นค่าช่วยสาธิตเท่านั้น โปรดตรวจ Input ก่อนนำผลไปใช้ในรายงาน</p>")

    def capture_compare_design(self,which):
        state=self.capture_project_state()
        if which=="A":self.compareA=state
        else:self.compareB=state
        self.compareView.setHtml(f"<h3>Captured Design {which}</h3><p>ปรับค่าที่หน้า Torque / Battery / Winch / Stability แล้ว Capture อีกแบบเพื่อเปรียบเทียบ</p>")

    def apply_compare_design(self,which):
        state=self.compareA if which=="A" else self.compareB
        if not state:
            QMessageBox.information(self,"Compare Design",f"ยังไม่ได้ Capture Design {which}");return
        self.apply_project_state(state,True)

    def engineering_metrics(self):
        t=self.torque_results();e=self.electrical_results();w=self.winch_results();d=self.inputs();worst=self.stability_worst_record()
        side=self.calc_side(d)[0];front,rear=self.longitudinal_sf_at(d,d['th'])
        return {
            "Vehicle mass (kg)":d['mt'],"Track width (m)":d['W'],"Boom length (m)":d['L'],"Crane angle (deg)":d['th'],
            "Required torque / motor (N·m)":t['T'],"Required mech power / motor (W)":t['Pmech_per'],"Drive battery design (Ah)":e['Ah'],
            "Drive current calculated (A)":e['Icalc_up'],"Drive current worst indicator (A)":e['Iworst'],"Winch battery design (Ah)":w['ah'],
            "Winch lift time (s)":w['tu'],"Side SF @ current angle":side,"Front SF @ current angle":front,"Rear SF @ current angle":rear,
            "Worst SF":worst[0],"Worst angle (deg)":worst[1],"Worst direction":worst[2]}

    def compare_designs(self):
        if not self.compareA or not self.compareB:
            self.compareView.setHtml("<h3>ยังเปรียบเทียบไม่ได้</h3><p>กรุณา Capture Design A และ Design B ก่อน</p>");return
        current=self.capture_project_state()
        try:
            self.apply_project_state(self.compareA,False);self._core_recalculate();a=self.engineering_metrics()
            self.apply_project_state(self.compareB,False);self._core_recalculate();b=self.engineering_metrics()
        finally:
            self.apply_project_state(current,False);self._core_recalculate()
        rows=[]
        for k in a:
            av,bv=a[k],b[k]
            if isinstance(av,(int,float)) and isinstance(bv,(int,float)):
                rows.append(f"<tr><td>{k}</td><td>{av:.3f}</td><td>{bv:.3f}</td><td>{bv-av:+.3f}</td></tr>")
            else: rows.append(f"<tr><td>{k}</td><td>{av}</td><td>{bv}</td><td>-</td></tr>")
        self.compareView.setHtml(f"<h2>DESIGN COMPARISON</h2><p>ตารางนี้แสดงความแตกต่างเชิงตัวเลข ไม่ตัดสินว่าแบบใดดีกว่าโดยอัตโนมัติ</p>"
            f"<table border='1' cellspacing='0' cellpadding='6'><tr><th>Metric</th><th>{self.compareALabel.text()}</th><th>{self.compareBLabel.text()}</th><th>Δ B-A</th></tr>{''.join(rows)}</table>")

    def winch_duty_results(self):
        w=self.winch_results();run=w['tu']+w['td'];rest=self.wDutyRest.value();allowed=self.wDutyAllowed.value();maxcont=self.wMaxContinuous.value()
        duty=100*run/(run+rest) if run+rest>0 else 100
        maxsegment=max(w['tu'],w['td']);total_run_min=w['n']*run/60;elapsed_min=w['n']*(run+rest)/60
        return dict(run=run,rest=rest,duty=duty,allowed=allowed,maxsegment=maxsegment,maxcont=maxcont,total_run_min=total_run_min,elapsed_min=elapsed_min,
                    duty_pass=duty<=allowed,continuous_pass=maxsegment<=maxcont)

    def winch_duty_html(self):
        x=self.winch_duty_results();s1="PASS" if x['duty_pass'] else "CHECK / OVER ASSUMPTION";s2="PASS" if x['continuous_pass'] else "CHECK / OVER ASSUMPTION"
        return f"""<h2>WINCH DUTY CYCLE — Preliminary Check</h2>
        <p><b>คำอธิบาย:</b> ใช้เวลายก+ลดเป็นเวลาที่มอเตอร์ทำงาน และใช้เวลาพักที่ผู้ใช้กำหนดเพื่อประมาณ Duty Cycle. ค่า Allowed duty และ Maximum continuous run ต้องแทนด้วยข้อมูลผู้ผลิตเมื่อหาได้</p>
        <p><b>สูตรภาษาไทย:</b> Duty Cycle = เวลามอเตอร์ทำงาน ÷ (เวลาทำงาน + เวลาพัก) × 100</p>
        <p><b>สูตรตัวแปร:</b> Duty = t_run/(t_run+t_rest) × 100</p>
        <p><b>แทนค่า:</b> t_run = {x['run']:.2f} s, t_rest = {x['rest']:.2f} s → Duty = {x['duty']:.2f}%</p>
        <p><b>คำตอบ:</b> Duty assumption = {x['duty']:.2f}% เทียบ Allowed {x['allowed']:.2f}% → <b>{s1}</b></p>
        <p>ช่วงทำงานต่อเนื่องยาวสุด = {x['maxsegment']:.2f} s เทียบสมมติฐานสูงสุด {x['maxcont']:.2f} s → <b>{s2}</b></p>
        <p>เวลามอเตอร์ทำงานสะสม = {x['total_run_min']:.2f} min; เวลารวมเมื่อใส่ช่วงพัก = {x['elapsed_min']:.2f} min</p>"""

    def update_winch_duty(self):
        if hasattr(self,"wDutyView"):self.wDutyView.setHtml(self.winch_duty_html())
        if hasattr(self,"designCheckView"):self.update_design_check()

    def bms_check_html(self):
        t=self.torque_results();e=self.electrical_results();w=self.winch_results()
        main_cont_req=max(t['Ibatt'],e['Icalc_up']);main_peak_ind=max(e['Iworst'],e.get('Icalc_peak',0),self.controllerCurrent.value()*t['n'])
        winch_cont_req=w['iup'];label_current=self.wrated.value()/max(self.wvolt.value(),.1);winch_peak_ind=max(w['iup'],label_current)
        def st(sel,req):
            if sel<=0:return "NOT SET / กรุณากรอก"
            return "PASS (preliminary)" if sel>=req else "CHECK / ต่ำกว่าค่าที่คำนวณ"
        return f"""<h2>BATTERY ENERGY + BMS CURRENT CHECK</h2>
        <p><b>หลักการ:</b> Ah/Wh ใช้ตรวจพลังงาน ส่วน A ใช้ตรวจความสามารถจ่ายกระแส ต้องผ่านทั้งสองส่วน</p>
        <h3>Main 72 V Drive</h3>
        <table border='1' cellspacing='0' cellpadding='6'>
        <tr><td>Required design capacity</td><td>{e['Ah']:.2f} Ah @ {e['V']:.1f} V</td><td>Selected {self.mainSelectedAh.value():.1f} Ah → {st(self.mainSelectedAh.value(),e['Ah'])}</td></tr>
        <tr><td>Continuous-current indicator</td><td>max(Torque model {t['Ibatt']:.1f}, Calculated uphill {e['Icalc_up']:.1f}) = {main_cont_req:.1f} A</td><td>BMS {self.mainBMSCont.value():.1f} A → {st(self.mainBMSCont.value(),main_cont_req)}</td></tr>
        <tr><td>Peak/conservative indicator</td><td>max(Worst battery {e['Iworst']:.1f}, calculated accel {e.get('Icalc_peak',0):.1f}, controller-limit indicator {self.controllerCurrent.value()*t['n']:.1f}) = {main_peak_ind:.1f} A</td><td>BMS peak {self.mainBMSPeak.value():.1f} A → {st(self.mainBMSPeak.value(),main_peak_ind)}</td></tr></table>
        <h3>Winch 12 V Separate Battery</h3>
        <table border='1' cellspacing='0' cellpadding='6'>
        <tr><td>Required design capacity</td><td>{w['ah']:.2f} Ah @ {w['v']:.1f} V</td><td>Selected {self.winchSelectedAh.value():.1f} Ah → {st(self.winchSelectedAh.value(),w['ah'])}</td></tr>
        <tr><td>Assumed operating current</td><td>{winch_cont_req:.1f} A</td><td>BMS {self.winchBMSCont.value():.1f} A → {st(self.winchBMSCont.value(),winch_cont_req)}</td></tr>
        <tr><td>Label-power current indicator</td><td>{self.wrated.value():.0f} W ÷ {self.wvolt.value():.1f} V = {label_current:.1f} A; stall current unknown</td><td>BMS peak {self.winchBMSPeak.value():.1f} A → {st(self.winchBMSPeak.value(),winch_peak_ind)}</td></tr></table>
        <p><b>ข้อจำกัด:</b> Controller current อาจเป็น phase/motor-current setting ไม่ใช่ battery current โดยตรง และ Winch stall current ยังไม่ทราบ จึงต้องยืนยัน datasheet/วัดจริงก่อนเลือก BMS ขั้นสุดท้าย</p>"""

    def update_bms_check(self):
        if hasattr(self,"bmsView"):self.bmsView.setHtml(self.bms_check_html())
        if hasattr(self,"designCheckView"):self.update_design_check()

    def design_check_rows(self):
        t=self.torque_results();e=self.electrical_results();w=self.winch_results();d=self.inputs();worst=self.stability_worst_record();duty=self.winch_duty_results()
        rows=[]
        def add(system,item,required,available,passed,note="",unknown=False):
            status="CHECK" if unknown else ("PASS" if passed else "FAIL")
            rows.append((system,item,required,available,status,note))
        add("Vehicle","Total mass ≤ 300 kg",f"≤ 300 kg",f"{d['mt']:.1f} kg",d['mt']<=300,"Project mass limit")
        add("Vehicle","Mass decomposition valid",f"m_total ≥ m_payload + m_boom",f"{d['mt']:.1f} ≥ {d['ml']+d['mb']:.1f} kg",d['mt']>=d['ml']+d['mb'],"ป้องกันมวลส่วนรถติดลบในโมเดล")
        add("Drive","Wheel torque / motor",f"{t['T']:.1f} N·m",f"Peak input {self.motorPeakTorque.value():.1f} N·m",self.motorPeakTorque.value()>=t['T'],"ใช้ค่าพิกัดที่ผู้ใช้กรอก")
        add("Drive","Mechanical power / motor",f"{t['Pmech_per']*self.powerReserve.value():.1f} W incl. reserve",f"Rated {self.motorRatedPower.value():.1f} W",self.motorRatedPower.value()>=t['Pmech_per']*self.powerReserve.value(),"Power reserve factor applied")
        add("Drive","Wheel RPM",f"{t['rpm']:.1f} rpm",f"Max input {self.motorMaxRPM.value():.1f} rpm",self.motorMaxRPM.value()>=t['rpm'])
        per_current=t['Ibatt']/max(1,t['n'])
        add("Drive","Controller current indicator / motor",f"{per_current:.1f} A",f"Limit {self.controllerCurrent.value():.1f} A",self.controllerCurrent.value()>=per_current,"preliminary")
        add("Drive","Traction",f"Fdesign {t['Fdesign']:.1f} N",f"Ftraction,max {t['Ftraction']:.1f} N",t['Ftraction']>=t['Fdesign'],f"ใช้แรงกดล้อขับ {t['drive_load_fraction']*100:.1f}% ของ N_total; final ต้องยืนยันจาก CG/load transfer")
        add("Stability","Worst-case SF",f"≥ {d['req']:.2f}",f"{worst[0]:.3f} @ {worst[1]}° {worst[2]}",worst[0]>=d['req'])
        if self.mainSelectedAh.value()>0:add("Main Battery","Energy capacity",f"≥ {e['Ah']:.2f} Ah",f"{self.mainSelectedAh.value():.1f} Ah",self.mainSelectedAh.value()>=e['Ah'])
        else:add("Main Battery","Energy capacity",f"{e['Ah']:.2f} Ah required","Selected not set",False,"กรอกใน Battery+BMS",True)
        main_cont=max(t['Ibatt'],e['Icalc_up'])
        if self.mainBMSCont.value()>0:add("Main BMS","Continuous current",f"≥ {main_cont:.1f} A",f"{self.mainBMSCont.value():.1f} A",self.mainBMSCont.value()>=main_cont)
        else:add("Main BMS","Continuous current",f"≥ {main_cont:.1f} A","Not set",False,"กรอกพิกัด BMS",True)
        if self.winchSelectedAh.value()>0:add("Winch Battery","Energy capacity",f"≥ {w['ah']:.2f} Ah",f"{self.winchSelectedAh.value():.1f} Ah",self.winchSelectedAh.value()>=w['ah'])
        else:add("Winch Battery","Energy capacity",f"{w['ah']:.2f} Ah required","Selected not set",False,"กรอกใน Battery+BMS",True)
        add("Winch","Duty cycle assumption",f"≤ {duty['allowed']:.1f}%",f"{duty['duty']:.1f}%",duty['duty_pass'],"Allowed value ยังเป็นสมมติฐาน",True if duty['allowed']==20 else False)
        add("Winch","Continuous run assumption",f"≤ {duty['maxcont']:.1f} s",f"{duty['maxsegment']:.1f} s",duty['continuous_pass'],"ใช้ข้อมูลผู้ผลิตเมื่อมี",True if duty['maxcont']==60 else False)
        return rows

    def design_check_html(self):
        rows=self.design_check_rows();counts={s:sum(1 for r in rows if r[4]==s) for s in ("PASS","FAIL","CHECK")}
        tr=[]
        for sys,item,req,av,status,note in rows:
            color={"PASS":"#176337","FAIL":"#b42318","CHECK":"#8a5a00"}[status]
            tr.append(f"<tr><td>{sys}</td><td>{item}</td><td>{req}</td><td>{av}</td><td style='color:{color};font-weight:700'>{status}</td><td>{note}</td></tr>")
        return f"""<h2>INTEGRATED DESIGN CHECK</h2>
        <p>PASS = ผ่านเงื่อนไขเชิงตัวเลขที่กำหนดในโปรแกรม, FAIL = ไม่ผ่านเงื่อนไขนั้น, CHECK = ข้อมูลยังไม่ยืนยัน/ยังไม่ได้กรอก. ผลนี้ไม่ใช่การรับรองความปลอดภัย.</p>
        <p><b>Summary:</b> PASS {counts['PASS']} | FAIL {counts['FAIL']} | CHECK {counts['CHECK']}</p>
        <table border='1' cellspacing='0' cellpadding='6'><tr><th>System</th><th>Check</th><th>Required</th><th>Available / Calculated</th><th>Status</th><th>Note</th></tr>{''.join(tr)}</table>"""

    def update_design_check(self):
        if hasattr(self,"designCheckView"):self.designCheckView.setHtml(self.design_check_html())

    def update_motor_operating(self):
        if not hasattr(self,"motorOpText"):return
        q=self.torque_results();tm=self.motorPeakTorque.value()/q['T'] if q['T'] else 999;rm=self.motorMaxRPM.value()/q['rpm'] if q['rpm'] else 999
        pm=self.motorRatedPower.value()/q['Pmech_per'] if q['Pmech_per'] else 999
        self.motorOpText.setHtml(f"""<h3>Motor Operating Point / จุดทำงานที่ต้องการ</h3>
        <p>Required point = <b>{q['T']:.2f} N·m @ {q['rpm']:.2f} rpm</b> ต่อมอเตอร์</p>
        <p>Entered limits: Rated torque {self.motorRatedTorque.value():.1f} N·m, Peak torque {self.motorPeakTorque.value():.1f} N·m, Max RPM {self.motorMaxRPM.value():.0f}, Rated power {self.motorRatedPower.value():.0f} W</p>
        <p>Torque margin = {tm:.2f}× | RPM margin = {rm:.2f}× | Power margin = {pm:.2f}×</p>
        <p><b>หมายเหตุ:</b> กราฟเป็น Limit Box จากค่าที่กรอก ไม่ได้สร้าง Torque-Speed curve ขึ้นมาเอง. ถ้ามีกราฟผู้ผลิตควรใช้กราฟนั้นยืนยันจุดทำงานจริง.</p>""")
        self.motorOpGraph.update()

    def update_final_report_preview(self):
        if not hasattr(self,"finalReportPreview"):return
        t=self.torque_results();e=self.electrical_results();w=self.winch_results();d=self.inputs();worst=self.stability_worst_record()
        self.finalReportPreview.setHtml(f"""<h1>FINAL ENGINEERING REPORT — Preview</h1>
        <p>Generated {datetime.now().strftime('%Y-%m-%d %H:%M')}</p>
        <h3>Key Results</h3><table border='1' cellspacing='0' cellpadding='6'>
        <tr><td>Vehicle mass</td><td>{d['mt']:.1f} kg</td></tr><tr><td>Drive torque required</td><td>{t['T']:.2f} N·m / motor</td></tr>
        <tr><td>Main battery design</td><td>{e['Ah']:.2f} Ah @ {e['V']:.1f} V</td></tr><tr><td>Winch battery design</td><td>{w['ah']:.2f} Ah @ {w['v']:.1f} V</td></tr>
        <tr><td>Worst stability</td><td>SF {worst[0]:.3f} @ {worst[1]}° ({worst[2]})</td></tr></table>
        {self.design_check_html()}<hr>{self.winch_duty_html()}""")

    def export_final_engineering_report(self):
        docs=QStandardPaths.writableLocation(QStandardPaths.DocumentsLocation) or str(Path.home())
        default_path=str(Path(docs)/"Crane_Vehicle_Final_Engineering_Report.pdf")
        filename,_=QFileDialog.getSaveFileName(self,"Export Final Engineering Report",default_path,"PDF (*.pdf)")
        if not filename:return
        if not filename.lower().endswith(".pdf"):filename+=".pdf"
        tmp=Path(tempfile.mkdtemp(prefix="cvet_final_report_"))
        try:
            self._core_recalculate();self.update_project_tools()
            t=self.torque_results();e=self.electrical_results();w=self.winch_results();worst=self.stability_worst_record()
            images=[]
            for name,widget in (("vehicle",getattr(self,"view",None)),("fbd",getattr(self,"forceDiagram",None)),
                                ("stability_map",getattr(self,"graph",None)),("motor_operating",getattr(self,"motorOpGraph",None))):
                if widget is not None:
                    fp=tmp/f"{name}.png"
                    if widget.grab().save(str(fp)):images.append((name,fp.as_uri()))
            img_html="".join(f"<h3>{name.replace('_',' ').title()}</h3><p><img src='{uri}' width='650'></p>" for name,uri in images)
            page="<div style='page-break-before:always'></div>"
            winch_formula=re.sub(r"</?(?:html|body)(?:\s[^>]*)?>","",self.winch_html(w),flags=re.I)
            winch_speed_formula=re.sub(r"</?(?:html|body)(?:\s[^>]*)?>","",self.winch_speed_html(self.winch_speed_results()),flags=re.I)
            html=f"""<html><body style="font-family:'Leelawadee UI',Tahoma,'Segoe UI',Arial;font-size:10pt">
            <h1>CRANE VEHICLE — FINAL ENGINEERING REPORT</h1>
            <p>Version {APP_VERSION} | Generated {datetime.now().strftime('%Y-%m-%d %H:%M')}</p>
            <p><b>Scope:</b> Drive Torque, Electrical/Battery, Winch, Stability, Worst Case, FBD, Motor Operating, Battery/BMS, Duty Cycle and integrated design checks.</p>
            {self.design_check_html()}{page}
            <h1>1. DRIVE TORQUE</h1>{self.torque_formula_html(t)}{page}
            <h1>2. ELECTRICAL / BATTERY</h1>{self.equation_html(e)}{page}
            <h1>3. WINCH</h1>{winch_formula}<hr>{winch_speed_formula}<hr>{self.winch_duty_html()}{page}
            <h1>4. STABILITY</h1>{self.stability_formula_html()}{page}
            <h1>5. WORST CASE</h1><p>SF_worst = {worst[0]:.3f} at θ={worst[1]}° ({worst[2]}), target SF={self.req.value():.2f}</p>{page}
            <h1>6. BATTERY + BMS</h1>{self.bms_check_html()}{page}
            <h1>7. FIGURES</h1>{img_html}
            <h2>Engineering limitations</h2>
            <p>ผลทั้งหมดเป็น Preliminary Engineering Calculation. ต้องยืนยันด้วยน้ำหนัก/CG จริง, datasheet, Torque-Speed curve, การทดสอบกระแส/แรงบิด/ความเร็วจริง, โครงสร้างและจุดยึด, สภาพพื้น, การถ่ายน้ำหนัก, Dynamic Shock, เบรกวินช์ และข้อกำหนดผู้ผลิตก่อนผลิตหรือใช้งานจริง.</p>
            </body></html>"""
            doc=QTextDocument();doc.setDefaultFont(QFont(choose_ui_font_family(),10));doc.setHtml(html)
            printer=QPrinter(QPrinter.HighResolution);printer.setOutputFormat(QPrinter.PdfFormat)
            printer.setOutputFileName(filename);printer.setPageSize(QPageSize(QPageSize.A4));doc.print_(printer)
            if not Path(filename).exists() or Path(filename).stat().st_size<1000:
                raise RuntimeError("PDF file was not created correctly")
            QMessageBox.information(self,"Final Report","บันทึกรายงานเรียบร้อย:\n"+filename)
        except Exception as exc:
            QMessageBox.critical(self,"Final Report ไม่สำเร็จ",str(exc))
        finally:
            shutil.rmtree(tmp,ignore_errors=True)

    def update_project_tools(self):
        if not hasattr(self,"projectTabs"):return
        try:
            self.update_motor_operating()
            if hasattr(self,"bmsView"):self.bmsView.setHtml(self.bms_check_html())
            if hasattr(self,"wDutyView"):self.wDutyView.setHtml(self.winch_duty_html())
            self.update_design_check()
            self.update_final_report_preview()
            if hasattr(self,"projectStatus") and not self.projectStatus.toPlainText().strip():
                self.projectStatus.setHtml("<h3>Project Tools พร้อมใช้งาน</h3><p>บันทึก/เปิด Project, ใช้ Preset, Capture Design A/B และสร้าง Final PDF ได้จากหน้านี้</p>")
        except Exception as exc:
            if hasattr(self,"projectStatus"):self.projectStatus.setPlainText("Project Tools update error: "+str(exc))

    def make_winch(self):
        w=QWidget();self.winchPage=w;root=QVBoxLayout(w);root.setContentsMargins(16,16,16,16);root.setSpacing(12)
        header=QFrame();header.setObjectName("topHeader");header.setMinimumHeight(96);add_soft_shadow(header,20,4,25)
        nav=QHBoxLayout(header);nav.setContentsMargins(18,14,18,14);nav.setSpacing(14)
        back=QPushButton("←  เมนูหลัก");back.setObjectName("secondaryButton");back.setMinimumWidth(120);back.clicked.connect(self.show_home_mode);nav.addWidget(back)
        textcol=QVBoxLayout();textcol.setSpacing(2)
        head=QLabel("WINCH CALCULATION");hf=QFont();hf.setPointSize(15);hf.setBold(True);head.setFont(hf);head.setStyleSheet("color:white;background:transparent;")
        subhead=QLabel("คำนวณแรง • ความเร็ว • เวลา • พลังงาน • แบตเตอรี่ 12 V แยกจากรถ");subhead.setWordWrap(True);subhead.setStyleSheet("color:#dbeafe;font-size:10pt;font-weight:600;background:transparent;")
        textcol.addWidget(head);textcol.addWidget(subhead);nav.addLayout(textcol,1)
        tag=make_chip("12 V WINCH", "#fff1dd", "#9a5800");nav.addWidget(tag)
        export=QPushButton("Export PDF / ส่งออกรายงาน");export.setObjectName("primaryButton");export.setMinimumWidth(190);export.clicked.connect(self.export_winch_pdf);nav.addWidget(export)
        root.addWidget(header)
        self.wTabs=QTabWidget();self.wTabs.setDocumentMode(True);root.addWidget(self.wTabs)
        inp=QWidget();layout=QHBoxLayout(inp);layout.setContentsMargins(14,14,14,14);layout.setSpacing(22)
        form=QFormLayout();form.setVerticalSpacing(10);form.setHorizontalSpacing(14);form.setFieldGrowthPolicy(QFormLayout.AllNonFixedFieldsGrow);form.setRowWrapPolicy(QFormLayout.WrapLongRows);layout.addLayout(form,1)
        def spin(v,lo,hi,dec=2):
            x=QDoubleSpinBox();x.setRange(lo,hi);x.setDecimals(dec);x.setValue(v);return x
        self.wmass=spin(100,0.1,10000);self.wbasket=spin(0,0,1000);self.wheight=spin(1.5,.01,100)
        self.wvolt=spin(12,1,100);self.wrated=spin(1400,1,100000,0);self.wratio=spin(136,1,10000,0)
        self.wspeedup=spin(3,.01,100);self.wspeeddown=spin(3,.01,100)
        self.wiup=spin(60,0,2000);self.widown=spin(30,0,2000)
        self.wcycles=QSpinBox();self.wcycles.setRange(1,100000);self.wcycles.setValue(50)
        self.wdod=spin(80,1,100);self.wreserve=spin(20,0,300)
        self.wdiameter=spin(0,0,1000);self.wsf=spin(1.5,1,10)
        fields=[("น้ำหนักสิ่งที่ยก (kg)",self.wmass),("น้ำหนักตะกร้าและอุปกรณ์ยกเพิ่ม (kg)",self.wbasket),
            ("ระยะยกแนวดิ่ง (m)",self.wheight),("แรงดันแบตเตอรี่แยก (V)",self.wvolt),
            ("กำลังพิกัดตามฉลาก (W) — ไม่ใช้แทนกระแสจริง",self.wrated),("อัตราทดเกียร์",self.wratio),
            ("ความเร็วโหลดขาขึ้น (m/min) [ใช้เมื่อปิด Auto]",self.wspeedup),("ความเร็วโหลดขาลง (m/min) [ใช้เมื่อปิด Auto]",self.wspeeddown),
            ("กระแสขณะยก (A) [สมมติ]",self.wiup),("กระแสขณะลด (A) [สมมติ]",self.widown),
            ("จำนวนรอบขึ้น+ลง",self.wcycles),("DoD ที่ใช้ได้ (%)",self.wdod),("พลังงานสำรอง (%)",self.wreserve),
            ("เส้นผ่านศูนย์กลางดรัมรวมสลิง (mm; 0=ไม่ทราบ)",self.wdiameter),
            ("ตัวคูณแรงเพื่อวิเคราะห์เบื้องต้น (ไม่ใช่ WLL)",self.wsf)]
        for label,widget in fields:
            lab=QLabel(label);lab.setWordWrap(True);lab.setMinimumWidth(245);lab.setSizePolicy(QSizePolicy.Preferred,QSizePolicy.Preferred)
            widget.setMinimumWidth(150)
            form.addRow(lab,widget)
        right=QVBoxLayout();right.setSpacing(12);layout.addLayout(right,1)
        self.wSummary=QLabel();self.wSummary.setWordWrap(True);self.wSummary.setMinimumWidth(350);self.wSummary.setStyleSheet("font-size:11pt;font-weight:700;background:qlineargradient(x1:0,y1:0,x2:1,y2:0,stop:0 #eefaf4,stop:1 #f8fffb);color:#155b2a;padding:16px;border:1px solid #a9d7ba;border-radius:11px")
        right.addWidget(self.wSummary)
        warn=QLabel("สมมติฐานเริ่มต้น: 3 m/min, 60 A ขาขึ้น, 30 A ขาลง, 50 รอบ\n"
          "ค่าเหล่านี้ยังไม่ใช่สเปกที่ยืนยันจากผู้ผลิต; แบตเตอรี่ต้องตรวจ BMS/กระแสกระชากแยกจาก Ah\n"
          "คำเตือน: พิกัดแรงดึง 4,500 lb ไม่ใช่ใบรับรองยกในแนวดิ่ง ตรวจสอบผู้ผลิตและระบบเบรกก่อนใช้จริง")
        warn.setWordWrap(True);warn.setStyleSheet("font-size:9.5pt;background:#fff8e9;color:#68420b;padding:14px;border:1px solid #ead39a;border-radius:11px");right.addWidget(warn)
        b=QPushButton("คำนวณใหม่ / Recalculate");b.setObjectName("primaryButton");b.clicked.connect(self.calc_winch);right.addWidget(b);right.addStretch()
        inp_scroll=QScrollArea();inp_scroll.setWidgetResizable(True);inp_scroll.setFrameShape(QFrame.NoFrame);inp_scroll.setWidget(inp)
        self.wTabs.addTab(inp_scroll,"Input / สมมติฐาน")
        self.wVars=QTextEdit();self.wVars.setReadOnly(True);self.wTabs.addTab(self.wVars,"ตัวแปร / Variables")
        self.wSteps=QTextEdit();self.wSteps.setReadOnly(True);self.wTabs.addTab(self.wSteps,"สูตร + แทนค่า")
        self.wGuide=QTextEdit();self.wGuide.setReadOnly(True);self.wTabs.addTab(self.wGuide,"คำอธิบายภาษาไทย")
        self.wResult=QTextEdit();self.wResult.setReadOnly(True);self.wTabs.addTab(self.wResult,"ผลแบตเตอรี่")
        # Independent speed calculator: measured line speed or motor RPM + effective drum diameter.
        speedpage=QWidget();speedlayout=QHBoxLayout(speedpage);speedlayout.setContentsMargins(14,14,14,14);speedlayout.setSpacing(22)
        speedform=QFormLayout();speedform.setVerticalSpacing(10);speedform.setHorizontalSpacing(14);speedform.setFieldGrowthPolicy(QFormLayout.AllNonFixedFieldsGrow);speedform.setRowWrapPolicy(QFormLayout.WrapLongRows);speedlayout.addLayout(speedform,1)
        self.wrpmup=spin(3000,1,100000,0); self.wrpmdown=spin(3000,1,100000,0)
        self.wdrumspeed=spin(60,1,1000); self.wparts=QSpinBox();self.wparts.setRange(1,12);self.wparts.setValue(1)
        self.wgear_eff=spin(80,1,100);self.wpulley_eff=spin(95,1,100)
        self.wmeasuredropeup=spin(3,.01,100);self.wmeasuredropedown=spin(3,.01,100)
        self.wspeedmethod=QComboBox();self.wspeedmethod.addItems(["คำนวณจากรอบมอเตอร์ + ดรัม (สมมติ)","ใช้ความเร็วสลิงที่วัด/กรอกในหน้า Speed"])
        for label,widget in [("วิธีหาความเร็ว",self.wspeedmethod),("รอบมอเตอร์ขาขึ้นขณะมีโหลด (RPM) [สมมติ]",self.wrpmup),
            ("รอบมอเตอร์ขาลง (RPM) [สมมติ]",self.wrpmdown),("เส้นผ่านศูนย์กลางดรัมรวมชั้นสลิง (mm) [สมมติ]",self.wdrumspeed),
            ("จำนวนเส้นสลิงที่รองรับโหลด (ส่วน)",self.wparts),("ประสิทธิภาพเกียร์ (%) [สมมติ]",self.wgear_eff),
            ("ประสิทธิภาพรอก (%) [สมมติ]",self.wpulley_eff),
            ("ความเร็วสลิงขาขึ้นที่วัด/สมมติ (m/min)",self.wmeasuredropeup),
            ("ความเร็วสลิงขาลงที่วัด/สมมติ (m/min)",self.wmeasuredropedown)]:
            lab=QLabel(label);lab.setWordWrap(True);lab.setMinimumWidth(245);widget.setMinimumWidth(150);speedform.addRow(lab,widget)
        speedright=QVBoxLayout();speedlayout.addLayout(speedright,1)
        self.wSpeedSummary=QLabel();self.wSpeedSummary.setWordWrap(True);self.wSpeedSummary.setMinimumWidth(350)
        self.wSpeedSummary.setStyleSheet("font-size:11pt;background:qlineargradient(x1:0,y1:0,x2:1,y2:0,stop:0 #eefaf4,stop:1 #f8fffb);color:#155b2a;padding:15px;border:1px solid #a9d7ba;border-radius:11px")
        speedright.addWidget(self.wSpeedSummary)
        self.wSpeedSteps=QTextEdit();self.wSpeedSteps.setReadOnly(True);speedright.addWidget(self.wSpeedSteps,1)
        applyspeed=QPushButton("นำความเร็วไปใช้ในหน้าแบตเตอรี่  →");applyspeed.setObjectName("primaryButton")
        applyspeed.clicked.connect(self.apply_winch_speed);speedright.addWidget(applyspeed)
        speed_scroll=QScrollArea();speed_scroll.setWidgetResizable(True);speed_scroll.setFrameShape(QFrame.NoFrame);speed_scroll.setWidget(speedpage)
        self.wTabs.addTab(speed_scroll,"ความเร็ววินช์ / Speed")
        for widget in (self.wrpmup,self.wrpmdown,self.wdrumspeed,self.wparts,self.wgear_eff,self.wpulley_eff,self.wmeasuredropeup,self.wmeasuredropedown):
            widget.valueChanged.connect(self.calc_winch)
        self.wspeedmethod.currentIndexChanged.connect(self.calc_winch)
        self.wusecalc=QCheckBox("ใช้ความเร็วจากหน้า Speed คำนวณแบตเตอรี่อัตโนมัติ (ไม่ต้องกดนำค่าไปใช้)")
        self.wusecalc.setChecked(True);speedform.addRow(self.wusecalc)
        self.wusecalc.toggled.connect(self.calc_winch)

        for _,widget in fields:
            widget.valueChanged.connect(self.calc_winch)
        self.tabs.addTab(w,"Winch")
        self.calc_winch()

    def winch_speed_results(self):
        ratio=self.wratio.value();d=self.wdrumspeed.value()/1000;parts=self.wparts.value()
        if self.wspeedmethod.currentIndex()==0:
            rope_up=math.pi*d*self.wrpmup.value()/ratio
            rope_down=math.pi*d*self.wrpmdown.value()/ratio
        else:
            rope_up=self.wmeasuredropeup.value();rope_down=self.wmeasuredropedown.value()
        load_up=rope_up/parts;load_down=rope_down/parts
        h=self.wheight.value();m=self.wmass.value()+self.wbasket.value()
        tension=m*G/(parts*self.wpulley_eff.value()/100)
        drum_torque=tension*d/2
        shaft_torque=drum_torque/(ratio*self.wgear_eff.value()/100)
        return dict(rope_up=rope_up,rope_down=rope_down,load_up=load_up,load_down=load_down,
                    time_up=h/load_up*60,time_down=h/load_down*60,diameter=d,parts=parts,
                    tension=tension,drum_torque=drum_torque,shaft_torque=shaft_torque,
                    drum_rpm_up=rope_up/(math.pi*d),drum_rpm_down=rope_down/(math.pi*d),
                    # Backward-compatible aliases used by the Variable Dictionary.
                    motor_up=self.wrpmup.value(),motor_down=self.wrpmdown.value(),
                    drum_up=rope_up/(math.pi*d),drum_down=rope_down/(math.pi*d))

    def winch_speed_html(self,x):
        def frac(top,bottom):
            return "<table cellspacing='0' style='display:inline-table;margin:5px'><tr><td align='center' style='border-bottom:1px solid #333'>"+str(top)+"</td></tr><tr><td align='center'>"+str(bottom)+"</td></tr></table>"
        def sec(n,title,thai,formula,sub,result):
            return (f"<h3 style='color:#b45309'>{n}. {title}</h3>"
                    f"<p><b>คำอธิบายภาษาไทย:</b> {thai}</p>"
                    f"<p><b>สูตรภาษาไทย</b></p><div style='margin-left:18px;font-size:12pt;color:#17324d'><b>{self._thai_formula_text(title)}</b></div>"
                    f"<p><b>สูตรตัวแปร</b></p><div style='margin-left:18px;font-size:12pt'>{formula}</div>"
                    f"<p><b>แทนค่า</b></p><div style='margin-left:18px'>{sub}</div>"
                    f"<p style='color:#176337'><b>คำตอบ: {result}</b></p><hr>")
        ratio=self.wratio.value(); d=x['diameter']; n=x['parts']
        mode="คำนวณจากรอบมอเตอร์" if self.wspeedmethod.currentIndex()==0 else "ใช้ความเร็วสลิงที่กรอก/วัดจริง"
        h=("<html><body style=\"font-family:'Leelawadee UI','Noto Sans Thai',Tahoma,Arial;font-size:11pt\">"
           "<h2>ความเร็วและเวลาวินช์ — คำอธิบาย → สูตรภาษาไทย → สูตรตัวแปร → แทนค่า → คำตอบ</h2>"
           f"<p><b>วิธีที่เลือก:</b> {mode}</p>")
        if self.wspeedmethod.currentIndex()==0:
            h+=sec(1,"รอบดรัม","เกียร์ทดทำให้ดรัมหมุนช้ากว่ามอเตอร์ โดยนำรอบมอเตอร์หารด้วยอัตราทดเกียร์",
                   "n<sub>drum</sub> = "+frac("n_motor","i"),
                   "n<sub>drum,up</sub> = "+frac(f"{self.wrpmup.value():.0f}",f"{ratio:.0f}")+f" = {x['drum_rpm_up']:.3f} RPM<br>"+
                   "n<sub>drum,down</sub> = "+frac(f"{self.wrpmdown.value():.0f}",f"{ratio:.0f}")+f" = {x['drum_rpm_down']:.3f} RPM",
                   f"รอบดรัมขึ้น {x['drum_rpm_up']:.3f} RPM, ลง {x['drum_rpm_down']:.3f} RPM")
            h+=sec(2,"ความเร็วสลิง","เมื่อดรัมหมุนหนึ่งรอบ สลิงเคลื่อนที่เท่ากับเส้นรอบวงของดรัม จึงใช้ πD คูณรอบดรัม",
                   "v<sub>rope</sub> = π D n<sub>drum</sub>",
                   f"v<sub>rope,up</sub> = π × {d:.3f} × {x['drum_rpm_up']:.3f} = {x['rope_up']:.3f} m/min<br>"
                   f"v<sub>rope,down</sub> = π × {d:.3f} × {x['drum_rpm_down']:.3f} = {x['rope_down']:.3f} m/min",
                   f"ความเร็วสลิงขึ้น {x['rope_up']:.3f} m/min, ลง {x['rope_down']:.3f} m/min")
        else:
            h+=sec(1,"ความเร็วสลิงที่วัด/กรอก","กรณีมีข้อมูล Line Speed จริง ให้ใช้ค่าที่วัดหรือผู้ผลิตระบุโดยตรง ไม่ต้องคำนวณจาก RPM",
                   "v<sub>rope</sub> = ค่าที่วัดหรือข้อมูลผู้ผลิต",
                   f"v<sub>rope,up</sub> = {x['rope_up']:.3f} m/min<br>v<sub>rope,down</sub> = {x['rope_down']:.3f} m/min",
                   f"ใช้ค่าความเร็วสลิงขึ้น/ลง {x['rope_up']:.3f}/{x['rope_down']:.3f} m/min")
        h+=sec(3,"ความเร็วของโหลด","ถ้ามีสลิงรองรับโหลดหลายส่วน ความเร็วโหลดจะช้าลงตามจำนวนส่วนสลิง",
               "v<sub>load</sub> = "+frac("v_rope","n"),
               "v<sub>load,up</sub> = "+frac(f"{x['rope_up']:.3f}",f"{n}")+f" = {x['load_up']:.3f} m/min<br>"+
               "v<sub>load,down</sub> = "+frac(f"{x['rope_down']:.3f}",f"{n}")+f" = {x['load_down']:.3f} m/min",
               f"ความเร็วโหลดขึ้น {x['load_up']:.3f} m/min, ลง {x['load_down']:.3f} m/min")
        h+=sec(4,"เวลายกและลด","เวลาเท่ากับระยะทางหารด้วยความเร็ว และคูณ 60 เพื่อเปลี่ยนนาทีเป็นวินาที",
               "t = "+frac("h × 60","v_load"),
               "t<sub>up</sub> = "+frac(f"{self.wheight.value():.2f} × 60",f"{x['load_up']:.3f}")+f" = {x['time_up']:.2f} s<br>"+
               "t<sub>down</sub> = "+frac(f"{self.wheight.value():.2f} × 60",f"{x['load_down']:.3f}")+f" = {x['time_down']:.2f} s",
               f"เวลายก {x['time_up']:.2f} s, เวลาลด {x['time_down']:.2f} s")
        h+=sec(5,"แรงดึงสลิง","แรงจากน้ำหนักถูกแบ่งด้วยจำนวนส่วนสลิงและประสิทธิภาพของรอก",
               "T<sub>rope</sub> = "+frac("m g","n η_pulley"),
               "T<sub>rope</sub> = "+frac(f"{self.wmass.value()+self.wbasket.value():.2f} × 9.81",f"{n} × {self.wpulley_eff.value()/100:.3f}")+f" = {x['tension']:.2f} N",
               f"แรงดึงสลิง {x['tension']:.2f} N")
        h+=sec(6,"แรงบิดที่ดรัม","แรงดึงสลิงกระทำที่รัศมีดรัม จึงได้แรงบิดจากแรงคูณรัศมี",
               "τ<sub>drum</sub> = T<sub>rope</sub> × "+frac("D","2"),
               f"τ<sub>drum</sub> = {x['tension']:.2f} × {d:.3f}/2 = {x['drum_torque']:.2f} N·m",
               f"แรงบิดดรัม {x['drum_torque']:.2f} N·m")
        h+=sec(7,"แรงบิดที่เพลามอเตอร์","เกียร์ช่วยทดแรงบิด จึงหารแรงบิดดรัมด้วยอัตราทดและประสิทธิภาพเกียร์",
               "τ<sub>motor</sub> = "+frac("τ_drum","i η_gear"),
               "τ<sub>motor</sub> = "+frac(f"{x['drum_torque']:.2f}",f"{ratio:.0f} × {self.wgear_eff.value()/100:.3f}")+f" = {x['shaft_torque']:.3f} N·m",
               f"แรงบิดเพลามอเตอร์ประมาณ {x['shaft_torque']:.3f} N·m")
        power=x['tension']*x['rope_up']/60
        available=self.wrated.value()*self.wgear_eff.value()/100
        h+=sec(8,"กำลังกลที่ดรัม","กำลังกลเท่ากับแรงดึงคูณความเร็วสลิงในหน่วย m/s ใช้ตรวจความสมเหตุสมผลของสมมติฐาน",
               "P<sub>drum</sub> = T<sub>rope</sub> × "+frac("v_rope","60"),
               f"P<sub>drum</sub> = {x['tension']:.2f} × {x['rope_up']:.3f}/60 = {power:.2f} W",
               f"กำลังกลที่ดรัมประมาณ {power:.2f} W; กำลังดรัมจากพิกัดสมมติ ≈ {available:.2f} W")
        h+=("<p><b>ข้อจำกัด:</b> รอบมอเตอร์, ขนาดดรัม, ประสิทธิภาพ และกำลัง 1,400 W ยังเป็นค่าที่ต้องยืนยันจากรุ่นจริง "
            "ชั้นสลิงทำให้เส้นผ่านศูนย์กลางดรัมเปลี่ยน และ Winch ดึงรถอาจไม่ได้รับรองสำหรับยกแนวดิ่ง</p></body></html>")
        return h

    def apply_winch_speed(self):
        x=self.winch_speed_results()
        # Explicit manual override: copy load speeds once, then turn off auto mode.
        self.wusecalc.setChecked(False)
        self.wspeedup.setValue(x['load_up']);self.wspeeddown.setValue(x['load_down'])
        self.wTabs.setCurrentIndex(0)
        QMessageBox.information(self,"อัปเดตความเร็ว","คัดลอกความเร็วโหลดไปยังหน้าแบตเตอรี่แล้ว และปิดโหมดเชื่อมอัตโนมัติ")

    def winch_results(self):
        m=self.wmass.value()+self.wbasket.value();h=self.wheight.value();v=self.wvolt.value()
        if self.wusecalc.isChecked():
            speed=self.winch_speed_results()
            up_speed=speed['load_up'];down_speed=speed['load_down']
        else:
            # Manual input fields ALWAYS mean load speed (not raw rope speed).
            up_speed=self.wspeedup.value();down_speed=self.wspeeddown.value()
        tu=h/up_speed*60;td=h/down_speed*60
        eu=v*self.wiup.value()*tu/3600;ed=v*self.widown.value()*td/3600
        n=self.wcycles.value();total=n*(eu+ed);dod=self.wdod.value()/100;reserve=self.wreserve.value()/100
        ah=total*(1+reserve)/(v*dod)
        return dict(m=m,h=h,v=v,tu=tu,td=td,eu=eu,ed=ed,n=n,total=total,ah=ah,
            f=m*9.81,fd=m*9.81*self.wsf.value(),mechanical=m*9.81*h/3600,
            iup=self.wiup.value(),idown=self.widown.value(),up_speed=up_speed,
            down_speed=down_speed,dod=dod,reserve=reserve)

    def winch_html(self,q):
        def frac(a,b):
            return ("<table style='display:inline-table;border-collapse:collapse;margin:4px 12px;vertical-align:middle'>"
                    "<tr><td align='center' style='border-bottom:1px solid black;padding:3px 8px'>"+str(a)+"</td></tr>"
                    "<tr><td align='center' style='padding:3px 8px'>"+str(b)+"</td></tr></table>")
        def sec(n,title,thai,formula,sub,result):
            return (f"<h3 style='color:#b45309'>{n}. {title}</h3>"
                    f"<p><b>คำอธิบายภาษาไทย:</b> {thai}</p>"
                    f"<p><b>สูตรภาษาไทย</b></p><div style='margin-left:18px;font-size:12pt;color:#17324d'><b>{self._thai_formula_text(title)}</b></div>"
                    f"<p><b>สูตรตัวแปร</b></p><div style='margin-left:18px;font-size:12pt'>{formula}</div>"
                    f"<p><b>แทนค่า</b></p><div style='margin-left:18px'>{sub}</div>"
                    f"<p style='color:#176337'><b>คำตอบ: {result}</b></p><hr>")
        x=q
        h=("<html><body style=\"font-family:'Leelawadee UI','Noto Sans Thai',Tahoma,Arial;font-size:12pt\">"
           "<h2>WINCH CALCULATION — คำอธิบาย → สูตรภาษาไทย → สูตรตัวแปร → แทนค่า → คำตอบ</h2>"
           "<p><b>ข้อควรระวัง:</b> ความเร็วและกระแสเป็นสมมติฐานที่แก้ได้ ไม่ใช่ข้อมูลทดสอบจริงของวินช์รุ่นนี้</p>"
           f"<h3>ตัวแปรและหน่วย</h3><table cellpadding='5' cellspacing='0' border='1'><tr><td>m</td><td>มวลโหลดรวม</td><td>{x['m']:.2f} kg</td></tr><tr><td>h</td><td>ระยะยก</td><td>{x['h']:.2f} m</td></tr><tr><td>V</td><td>แรงดันแบตวินช์</td><td>{x['v']:.2f} V</td></tr><tr><td>Iup / Idown</td><td>กระแสสมมติขณะขึ้น / ลง</td><td>{x['iup']:.1f} / {x['idown']:.1f} A</td></tr><tr><td>N</td><td>จำนวนรอบขึ้น+ลง</td><td>{x['n']}</td></tr><tr><td>DoD / Reserve</td><td>เงื่อนไขออกแบบแบตเตอรี่</td><td>{x['dod']:.3f} / {x['reserve']:.3f}</td></tr></table>"
           f"<p>แหล่งความเร็วโหลด: {'คำนวณจากหน้า Speed โดยอัตโนมัติ' if self.wusecalc.isChecked() else 'กรอกจากหน้า Input'}; ขึ้น {x['up_speed']:.3f} และลง {x['down_speed']:.3f} m/min</p>")
        h+=sec(1,"แรงยก","น้ำหนักของโหลดสร้างแรงลงจากแรงโน้มถ่วง จึงใช้มวลรวมคูณความเร่งโน้มถ่วง",
               "F = m g",f"F = {x['m']:.2f} × 9.81 = {x['f']:.2f} N",f"F = {x['f']:.2f} N")
        h+=sec(2,"แรงยกออกแบบ","คูณแรงยกด้วย Safety Factor เพื่อใช้เป็นแรงออกแบบเบื้องต้น ไม่ใช่การรับรองพิกัดยก",
               "F<sub>design</sub> = F × SF",f"F<sub>design</sub> = {x['f']:.2f} × {self.wsf.value():.2f} = {x['fd']:.2f} N",f"F_design = {x['fd']:.2f} N")
        h+=sec(3,"พลังงานกลขั้นต่ำในการยก","พลังงานศักย์ที่ต้องเพิ่มให้โหลดเท่ากับ mgh และแปลงจากจูลเป็น Wh ด้วยการหาร 3600",
               "E<sub>mech</sub> = "+frac("m g h","3600"),
               "E<sub>mech</sub> = "+frac(f"{x['m']:.2f} × 9.81 × {x['h']:.2f}","3600")+f" = {x['mechanical']:.4f} Wh",f"E_mech = {x['mechanical']:.4f} Wh")
        h+=sec(4,"เวลายกขึ้น","เวลาเท่ากับระยะยกหารด้วยความเร็วโหลด และคูณ 60 เพราะความเร็วเป็น m/min",
               "t<sub>up</sub> = "+frac("h × 60","v_up"),
               "t<sub>up</sub> = "+frac(f"{x['h']:.2f} × 60",f"{x['up_speed']:.3f}")+f" = {x['tu']:.2f} s",f"t_up = {x['tu']:.2f} s")
        h+=sec(5,"เวลาลดลง","ใช้หลักเดียวกับขาขึ้น แต่ใช้ความเร็วขาลงซึ่งอาจต่างกัน",
               "t<sub>down</sub> = "+frac("h × 60","v_down"),
               "t<sub>down</sub> = "+frac(f"{x['h']:.2f} × 60",f"{x['down_speed']:.3f}")+f" = {x['td']:.2f} s",f"t_down = {x['td']:.2f} s")
        h+=sec(6,"กำลังไฟฟ้าขณะยก","ประมาณกำลังไฟฟ้าจากแรงดันคูณกระแสที่วินช์ใช้ขณะยก",
               "P<sub>up</sub> = V I<sub>up</sub>",f"P<sub>up</sub> = {x['v']:.2f} × {x['iup']:.2f} = {x['v']*x['iup']:.2f} W",f"P_up = {x['v']*x['iup']:.2f} W")
        h+=sec(7,"พลังงานไฟฟ้าขณะยก","พลังงานไฟฟ้าเท่ากับกำลังคูณเวลา โดยหาร 3600 เพื่อให้เป็น Wh",
               "E<sub>up</sub> = "+frac("V I_up t_up","3600"),
               "E<sub>up</sub> = "+frac(f"{x['v']:.2f} × {x['iup']:.2f} × {x['tu']:.2f}","3600")+f" = {x['eu']:.3f} Wh",f"E_up = {x['eu']:.3f} Wh")
        h+=sec(8,"กำลังและพลังงานขณะลด","ขาลงอาจใช้กระแสน้อยกว่าขาขึ้น จึงคำนวณแยกด้วย I_down และ t_down",
               "P<sub>down</sub> = V I<sub>down</sub><br>E<sub>down</sub> = "+frac("V I_down t_down","3600"),
               f"P<sub>down</sub> = {x['v']:.2f} × {x['idown']:.2f} = {x['v']*x['idown']:.2f} W<br>E<sub>down</sub> = "+frac(f"{x['v']:.2f} × {x['idown']:.2f} × {x['td']:.2f}","3600")+f" = {x['ed']:.3f} Wh",f"P_down = {x['v']*x['idown']:.2f} W, E_down = {x['ed']:.3f} Wh")
        cycle=x['eu']+x['ed']
        h+=sec(9,"พลังงานรวมตามจำนวนรอบ","หนึ่งรอบประกอบด้วยยกขึ้นหนึ่งครั้งและลดลงหนึ่งครั้ง จากนั้นคูณจำนวนรอบใช้งาน",
               "E<sub>cycle</sub> = E_up + E_down<br>E<sub>total</sub> = N E_cycle",
               f"E<sub>cycle</sub> = {x['eu']:.3f} + {x['ed']:.3f} = {cycle:.3f} Wh<br>E<sub>total</sub> = {x['n']} × {cycle:.3f} = {x['total']:.3f} Wh",f"E_total = {x['total']:.3f} Wh")
        h+=sec(10,"ความจุแบตเตอรี่ 12 V","เผื่อ Reserve และจำกัดการใช้ความจุตาม DoD ก่อนแปลงพลังงาน Wh เป็น Ah",
               "Ah = "+frac("E_total (1 + Reserve)","V × DoD"),
               "Ah = "+frac(f"{x['total']:.3f} × (1 + {x['reserve']:.3f})",f"{x['v']:.2f} × {x['dod']:.3f}")+f" = {x['ah']:.2f} Ah",f"แบตเตอรี่ตามสมมติฐาน = {x['v']:.1f} V, {x['ah']:.2f} Ah")
        total_min=x['n']*(x['tu']+x['td'])/60
        h+=sec(11,"เวลาทำงานสะสมของวินช์","ใช้สำหรับตรวจ Duty Cycle โดยรวมเวลาขึ้นและลงทุกครั้ง",
               "t<sub>motor,total</sub> = "+frac("N (t_up + t_down)","60"),
               "t<sub>motor,total</sub> = "+frac(f"{x['n']} × ({x['tu']:.2f} + {x['td']:.2f})","60")+f" = {total_min:.2f} min",f"เวลามอเตอร์ทำงานรวม ≈ {total_min:.2f} นาที")
        h+=("<p><b>ข้อจำกัด:</b> กระแส 60/30 A และความเร็วยังเป็นสมมติฐาน ต้องตรวจจากผู้ผลิตหรือวัดจริง รวมถึงกระแสกระชาก, BMS, ฟิวส์, สายไฟ, Duty Cycle และพิกัดเบรกของวินช์</p></body></html>")
        return h

    def calc_winch(self):
        if not hasattr(self,"wSummary"):return
        q=self.winch_results()
        self.wSummary.setText(f"เวลายกขึ้น: {q['tu']:.1f} วินาที | เวลาลง: {q['td']:.1f} วินาที\n"
            f"พลังงานขึ้น/ลง: {q['eu']:.2f} / {q['ed']:.2f} Wh\n"
            f"พลังงานรวม {q['n']} รอบ: {q['total']:.2f} Wh\n"
            f"แบตเตอรี่ตามสมมติฐาน: {q['v']:.1f} V, {q['ah']:.2f} Ah\n"
            f"แหล่งความเร็ว: {'Speed (อัตโนมัติ)' if self.wusecalc.isChecked() else 'Input (กำหนดเอง)'}\n"
            "ยังต้องตรวจสอบกระแสกระชาก, BMS, Duty Cycle และการรับรองงานยก")
        self.wSteps.setHtml(self.winch_html(q))
        if hasattr(self,"wVars"):self.wVars.setHtml(self.winch_variables_html())
        if hasattr(self,"allWVars"):self.allWVars.setHtml(self.winch_variables_html())
        sp=self.winch_speed_results()
        self.wSpeedSummary.setText(f"ความเร็วสลิงขึ้น/ลง: {sp['rope_up']:.3f} / {sp['rope_down']:.3f} m/min\n"
            f"ความเร็วโหลดขึ้น/ลง: {sp['load_up']:.3f} / {sp['load_down']:.3f} m/min\n"
            f"เวลายกขึ้น/ลง: {sp['time_up']:.1f} / {sp['time_down']:.1f} วินาที\n"
            f"แรงดึงสลิง: {sp['tension']:.1f} N | แรงบิดดรัม: {sp['drum_torque']:.2f} N·m\n"
            "ความเร็วในหน้านี้เป็นการประมาณการ ต้องยืนยันด้วยข้อมูลผู้ผลิต/การทดสอบ")
        self.wSpeedSteps.setHtml(self.winch_speed_html(sp))

        self.wGuide.setHtml("<h2>อธิบายภาษาไทย</h2><p>โหมดนี้คำนวณขนาดแบตเตอรี่ 12 V แยกจากแบตเตอรี่ขับรถ 72 V "
            "โดยค่าเริ่มต้นยกตรง 1.5 เมตร เมื่อใช้รอกทด หน้า Speed จะแปลงความเร็วสลิงเป็นความเร็วโหลดหนึ่งครั้งเท่านั้น "
            "และส่งความเร็วโหลดให้หน้าแบตเตอรี่เมื่อเปิดโหมดอัตโนมัติ; ช่องความเร็วใน Input คือความเร็วโหลดเสมอ</p>"
            "<p>เวลายกหาได้จากระยะยกหารด้วยความเร็วโหลด (ซึ่งอาจช้ากว่าความเร็วสลิงเมื่อใช้รอกทด) ส่วนพลังงานไฟฟ้าหาจากแรงดัน × กระแส × เวลา "
            "คำนวณขาขึ้นและขาลงแยกกัน เพราะกระแสและความเร็วอาจต่างกัน จากนั้นคูณจำนวนรอบ</p>"
            "<p>DoD คือสัดส่วนความจุที่ตั้งใจนำมาใช้ และ Reserve คือพลังงานที่เผื่อเพิ่มเติม "
            "ทั้งสองค่าเป็นเงื่อนไขการออกแบบ ไม่ใช่ค่าที่ผู้ผลิตยืนยันสำหรับแบตเตอรี่ของคุณ</p>"
            "<p><b>ข้อจำกัด:</b> ค่ากระแส 60/30 A และความเร็ว 3/3 m/min เป็นเพียงตัวอย่าง "
            "ต้องตรวจสอบกราฟกระแส-แรงดึงและความเร็ว-แรงดึงของวินช์รุ่นจริง "
            "และไม่ควรใช้วินช์ดึงรถยกของในแนวดิ่งจนกว่าผู้ผลิตรับรองและมีเบรกสำหรับยกของ</p>")
        torque="ยังไม่ระบุขนาดดรัม"
        if self.wdiameter.value()>0:torque=f"{q['f']*self.wdiameter.value()/2000:.2f} N·m (เชิงทฤษฎีที่โหลดคงที่)"
        self.wResult.setHtml(f"<h2>ผลประมาณการแบตเตอรี่วินช์</h2><p>พลังงานกลขั้นต่ำ {q['mechanical']:.4f} Wh ต่อการยก</p>"
            f"<p>แหล่งความเร็ว: {'Speed (อัตโนมัติ)' if self.wusecalc.isChecked() else 'Input (กำหนดเอง)'}; "
            f"ความเร็วโหลดขึ้น/ลง {q['up_speed']:.3f}/{q['down_speed']:.3f} m/min</p>"
            f"<p>พลังงานไฟฟ้าต่อรอบ {q['eu']+q['ed']:.2f} Wh; พลังงาน {q['n']} รอบ = {q['total']:.2f} Wh</p>"
            f"<h2>{q['v']:.1f} V — {q['ah']:.2f} Ah</h2><p>แรงบิดดรัม: {torque}</p>"
            "<p>ห้ามเลือกซื้อจาก Ah อย่างเดียว: ตรวจ Continuous/Peak discharge, BMS, สายไฟ, ฟิวส์และระยะพัก</p>")

    def export_winch_pdf(self):
        filename,_=QFileDialog.getSaveFileName(self,"Export Winch PDF","Winch_Battery_Report.pdf","PDF (*.pdf)")
        if not filename:return
        if not filename.lower().endswith(".pdf"):filename+=".pdf"
        try:
            q=self.winch_results();doc=QTextDocument();doc.setDefaultFont(QFont(choose_ui_font_family(),10))
            doc.setHtml(self.winch_html(q)+"<hr/>"+self.winch_speed_html(self.winch_speed_results())+"<hr/>"+self.wGuide.toHtml()+"<hr/>"+self.wResult.toHtml())
            printer=QPrinter(QPrinter.HighResolution);printer.setOutputFormat(QPrinter.PdfFormat)
            printer.setOutputFileName(filename);printer.setPageSize(QPageSize(QPageSize.A4));doc.print_(printer)
            QMessageBox.information(self,"Export PDF","บันทึกรายงานเรียบร้อย:\n"+filename)
        except Exception as exc:QMessageBox.critical(self,"Export PDF ไม่สำเร็จ",str(exc))

    def make_electrical(self):
        w=QWidget();self.electricalPage=w
        root=QVBoxLayout(w);root.setContentsMargins(16,16,16,16);root.setSpacing(12)
        root.addWidget(make_page_header("ELECTRICAL / BATTERY CALCULATION","Route Energy • Wh • Ah • Peak Current • BMS check",self.show_home_mode,"72 V DRIVE","#e5faf4","#0b7665","Export PDF / ส่งออกรายงาน",self.export_electrical_pdf))
        self.eTabs=QTabWidget();root.addWidget(self.eTabs)

        def ds(v,lo,hi,dec=2):
            q=QDoubleSpinBox();q.setRange(lo,hi);q.setDecimals(dec);q.setValue(v)
            q.setMinimumWidth(150);q.setMaximumWidth(250);return q

        inp=QWidget();hl=QHBoxLayout(inp)
        left=QWidget();form=QFormLayout(left)
        form.setVerticalSpacing(7);form.setHorizontalSpacing(12);form.setFieldGrowthPolicy(QFormLayout.FieldsStayAtSizeHint)
        form.setVerticalSpacing(7);form.setHorizontalSpacing(12);form.setFieldGrowthPolicy(QFormLayout.FieldsStayAtSizeHint)
        self.emass=ds(290,1,5000,1); self.evolt=ds(72,1,200,1)
        self.espeed=ds(1,.05,50,2); self.eoneway=ds(30,.1,10000,2)
        self.eslopeLen=ds(2.9,0,1000,2); self.eslopeDeg=ds(12,0,45,1)
        self.eruntime=ds(3,.01,48,2); self.err=ds(.02,0,1,3)
        self.eaccel=ds(5,.1,120,2); self.estops=QSpinBox();self.estops.setRange(0,20);self.estops.setValue(2);self.estops.setMinimumWidth(150);self.estops.setMaximumWidth(250)
        self.estopTime=ds(0,0,3600,1)
        self.edriveEff=ds(60,1,100,1); self.eaux=ds(50,0,5000,1)
        self.edod=ds(80,1,100,1); self.ereserve=ds(20,0,200,1)
        self.emotorRated=ds(1500,1,50000,0); self.enmot=QSpinBox();self.enmot.setRange(1,8);self.enmot.setValue(2);self.enmot.setMinimumWidth(150);self.enmot.setMaximumWidth(250)
        self.eupEff=ds(80,1,100,1)
        self.euseTorqueMass=QCheckBox("ใช้ Total mass จาก Stability / Mass & CG");self.euseTorqueMass.setChecked(False)
        for lab,q in [
            ("มวลรวมรถ m (kg)",self.emass),("Battery voltage (V)",self.evolt),
            ("ความเร็ว (km/h)",self.espeed),("ระยะเที่ยวเดียว (m)",self.eoneway),
            ("ความยาวทางลาดต่อเที่ยว (m)",self.eslopeLen),("มุมทางลาด (deg)",self.eslopeDeg),
            ("เวลาทำงาน (h)",self.eruntime),("Rolling resistance Crr",self.err),
            ("เวลาเร่ง 0→v (s)",self.eaccel),("จำนวนครั้งออกตัวต่อรอบ",self.estops),
            ("เวลาหยุดต่อรอบ (s)",self.estopTime),("Estimated drive efficiency (%)",self.edriveEff),
            ("Auxiliary average power (W)",self.eaux),("Usable DoD (%)",self.edod),
            ("Battery reserve (%)",self.ereserve),("Motor rated power / motor (W)",self.emotorRated),
            ("จำนวนมอเตอร์",self.enmot),("Worst-case slope efficiency (%)",self.eupEff)
        ]: form.addRow(lab,q)
        form.addRow(self.euseTorqueMass);left.setMinimumWidth(410);hl.addWidget(left,1)

        right=QWidget();right.setMinimumWidth(340);rv=QVBoxLayout(right)
        modeBox=QGroupBox("Slope Energy Model / วิธีคิดช่วงขึ้นทางลาด");mb=QVBoxLayout(modeBox)
        self.ecalcRadio=QRadioButton("Calculated model: F = mg sinθ + Crr·mg cosθ (+ acceleration)")
        self.eworstRadio=QRadioButton("Worst-case model: ใช้ Rated Power ของมอเตอร์เต็มช่วงขึ้นลาด")
        self.ecalcRadio.setChecked(True);mb.addWidget(self.ecalcRadio);mb.addWidget(self.eworstRadio)
        rv.addWidget(modeBox)
        self.eSummary=QLabel();self.eSummary.setWordWrap(True)
        self.eSummary.setStyleSheet("font-size:11pt;font-weight:700;background:qlineargradient(x1:0,y1:0,x2:1,y2:0,stop:0 #eefaf4,stop:1 #f8fffb);color:#155b2a;padding:15px;border:1px solid #a9d7ba;border-radius:11px")
        rv.addWidget(self.eSummary)
        note=QLabel("สำคัญ: โปรแกรมแสดงทั้งพลังงานเชิงทฤษฎีและ Estimated Battery Energy แยกกัน\\n"
                    "Efficiency เป็นพารามิเตอร์ประมาณ จนกว่าจะมีค่ากระแส/กำลังที่วัดจริงจากรถ\\n"
                    "No Regen: พลังงานขาลงไม่ถูกนำมาหักคืนแบตเตอรี่")
        note.setWordWrap(True);note.setStyleSheet("background:#fff8e9;color:#68420b;padding:12px;border:1px solid #ead39a;border-radius:10px")
        rv.addWidget(note)
        b=QPushButton("คำนวณใหม่ / Calculate");b.setObjectName("primaryButton");b.clicked.connect(self.calc_electrical);rv.addWidget(b)
        rv.addStretch();hl.addWidget(right,1)
        eInputScroll=QScrollArea();eInputScroll.setWidgetResizable(True);eInputScroll.setFrameShape(QFrame.NoFrame)
        eInputScroll.setWidget(inp);self.eTabs.addTab(eInputScroll,"Input / ข้อมูล")
        self.eVars=QTextEdit();self.eVars.setReadOnly(True);self.eTabs.addTab(self.eVars,"ตัวแปร / Variables")

        step=QWidget();sv=QVBoxLayout(step);self.eSteps=QTextEdit();self.eSteps.setReadOnly(True);self.eSteps.setStyleSheet("font-size:13px");sv.addWidget(self.eSteps)
        self.eTabs.addTab(step,"สูตร + แทนค่า / Calculation Steps")

        explanation=QWidget()
        explanation_layout=QVBoxLayout(explanation)
        self.eThaiExplain=QTextEdit()
        self.eThaiExplain.setReadOnly(True)
        explanation_layout.addWidget(self.eThaiExplain)
        self.eTabs.addTab(explanation,"อธิบายภาษาไทย / Thai Guide")

        res=QWidget();resv=QVBoxLayout(res);self.eResults=QTextEdit();self.eResults.setReadOnly(True);resv.addWidget(self.eResults)
        self.eTabs.addTab(res,"Battery Result")

        controls=[self.emass,self.evolt,self.espeed,self.eoneway,self.eslopeLen,self.eslopeDeg,self.eruntime,
                  self.err,self.eaccel,self.estopTime,self.edriveEff,self.eaux,self.edod,self.ereserve,
                  self.emotorRated,self.eupEff]
        for q in controls:q.valueChanged.connect(self.calc_electrical)
        self.estops.valueChanged.connect(self.calc_electrical);self.enmot.valueChanged.connect(self.calc_electrical)
        self.ecalcRadio.toggled.connect(self.calc_electrical);self.eworstRadio.toggled.connect(self.calc_electrical)
        self.euseTorqueMass.toggled.connect(self.calc_electrical)
        self.tabs.addTab(w,"Electrical / Battery")
        self.calc_electrical()

    def electrical_results(self):
        m=self.mt.value() if self.euseTorqueMass.isChecked() and hasattr(self,"mt") else self.emass.value()
        g=G; V=self.evolt.value(); v=self.espeed.value()/3.6
        one=self.eoneway.value(); Ls=min(self.eslopeLen.value(),one); theta=math.radians(self.eslopeDeg.value())
        runtime_h=self.eruntime.value(); runtime_s=runtime_h*3600.0
        stop_s=self.estopTime.value()
        cycle_distance=2.0*one
        drive_cycle_s=cycle_distance/v if v>0 else 0
        cycle_total_s=drive_cycle_s+stop_s
        cycles=runtime_s/cycle_total_s if cycle_total_s>0 else 0
        flat_cycle=max(0.0,cycle_distance-2.0*Ls)
        flat_time_h=(flat_cycle/v)/3600.0 if v>0 else 0
        up_time_h=(Ls/v)/3600.0 if v>0 else 0
        down_time_h=up_time_h

        crr=self.err.value()
        Fflat=crr*m*g
        Pflat_mech=Fflat*v
        Fgrade=m*g*math.sin(theta)
        Frrs=crr*m*g*math.cos(theta)
        Fup=Fgrade+Frrs
        Pup_mech=Fup*v

        # Downhill: with no regen we never subtract energy from the battery.
        # If gravity is stronger than rolling resistance, traction power is 0
        # and the excess energy must be dissipated by braking/coasting losses.
        Fdown=max(0.0,Frrs-Fgrade)
        Pdown_mech=Fdown*v

        eff=max(self.edriveEff.value()/100.0,.01)
        up_eff=max(self.eupEff.value()/100.0,.01)
        Eflat_mech_cycle=Pflat_mech*flat_time_h
        Eup_mech_cycle=Pup_mech*up_time_h
        Edown_mech_cycle=Pdown_mech*down_time_h

        # Acceleration kinetic energy. Acceleration time affects peak force/power,
        # while ideal kinetic energy 1/2 mv² is independent of acceleration time.
        starts=self.estops.value()
        accel_time=max(self.eaccel.value(),.01)
        accel_a=v/accel_time
        Facc_peak=m*accel_a
        Pacc_peak_mech=(Fup+Facc_peak)*v
        Eacc_mech_cycle=(0.5*m*v*v/3600.0)*starts

        Emech_total=(Eflat_mech_cycle+Eup_mech_cycle+Edown_mech_cycle+Eacc_mech_cycle)*cycles
        Ecalc_drive=Emech_total/eff

        rated_total=self.emotorRated.value()*self.enmot.value()
        Pworst_batt=rated_total/up_eff
        Eworst_up_cycle=Pworst_batt*up_time_h
        Eflat_batt_cycle=Eflat_mech_cycle/eff
        Edown_batt_cycle=Edown_mech_cycle/eff
        Eacc_batt_cycle=Eacc_mech_cycle/eff
        Eworst_drive=(Eflat_batt_cycle+Edown_batt_cycle+Eacc_batt_cycle+Eworst_up_cycle)*cycles

        use_worst=self.eworstRadio.isChecked()
        Edrive=Eworst_drive if use_worst else Ecalc_drive
        Eaux=self.eaux.value()*runtime_h
        Eload=Edrive+Eaux
        dod=max(self.edod.value()/100.0,.01)
        reserve=self.ereserve.value()/100.0
        Enom=Eload/dod
        Edesign=Enom*(1.0+reserve)
        Ah=Edesign/V if V>0 else 0

        Icalc_up=(Pup_mech/eff)/V if V>0 else 0
        Icalc_accel=(Pacc_peak_mech/eff)/V if V>0 else 0
        Icalc_peak=max(Icalc_up,Icalc_accel)
        Iworst=Pworst_batt/V if V>0 else 0

        return locals()

    def equation_html(self, q):
        """Qt rich text fraction layout; numerator is above denominator, not slash notation."""
        from html import escape
        def frac(top,bottom):
            return (f"<table cellspacing='0' cellpadding='2' style='margin:3px 0'>"
                    f"<tr><td align='center' style='border-bottom:1px solid #243b53'><b>{top}</b></td></tr>"
                    f"<tr><td align='center'><b>{bottom}</b></td></tr></table>")
        def section(title,description,formula,substitution,result):
            return (f"<h3 style='color:#17456b'>{title}</h3>"
                    f"<p><b>คำอธิบายภาษาไทย:</b> {description}</p>"
                    f"<p><b>สูตรภาษาไทย</b></p><div style='margin-left:18px;font-size:12pt;color:#17324d'><b>{self._thai_formula_text(title)}</b></div>"
                    f"<p><b>สูตรตัวแปร</b></p><div style='margin-left:18px;font-size:12pt'>{formula}</div>"
                    f"<p><b>แทนค่า</b></p><div style='margin-left:18px'>{substitution}</div>"
                    f"<p style='color:#176337'><b>คำตอบ: {result}</b></p><hr/>")
        v=q['v']; m=q['m']; V=q['V']
        h="<h2>ELECTRICAL / BATTERY — สูตรครบ + แทนค่า</h2>"
        h+="<p>ตัวเลขในหน้านี้ปรับอัตโนมัติตามข้อมูลที่กรอก และแสดงตัวเศษไว้เหนือเส้น ตัวส่วนอยู่ด้านล่าง</p>"
        h+=("<h3>ตัวแปรและหน่วย</h3><table cellpadding='5' cellspacing='0' border='1'>"
            f"<tr><td>m</td><td>มวลรวมรถ</td><td>{m:.1f} kg</td></tr>"
            f"<tr><td>V</td><td>แรงดันแบตเตอรี่</td><td>{V:.1f} V</td></tr>"
            f"<tr><td>v</td><td>ความเร็วรถ</td><td>{self.espeed.value():.2f} km/h = {v:.5f} m/s</td></tr>"
            f"<tr><td>Crr</td><td>สัมประสิทธิ์แรงต้านการกลิ้ง</td><td>{q['crr']:.3f}</td></tr>"
            f"<tr><td>ηdrive</td><td>ประสิทธิภาพระบบขับสมมติ</td><td>{q['eff']:.3f}</td></tr>"
            f"<tr><td>DoD</td><td>สัดส่วนความจุที่อนุญาตให้ใช้</td><td>{q['dod']:.3f}</td></tr>"
            f"<tr><td>Reserve</td><td>พลังงานสำรอง</td><td>{q['reserve']:.3f}</td></tr></table>")
        h+=section("1. แปลงความเร็ว","เปลี่ยนหน่วยจากกิโลเมตรต่อชั่วโมงเป็นเมตรต่อวินาที",
                   frac("ความเร็ว (km/h)","3.6"),
                   frac(f"{self.espeed.value():.2f}","3.6"),f"{v:.5f} m/s")
        h+=section("2. เวลาและจำนวนรอบ","รวมระยะไปและกลับ และนับเวลาหยุดต่อรอบด้วย",
                   "ระยะต่อรอบ = 2 × ระยะเที่ยวเดียว<br/>เวลาวิ่ง = "+frac("ระยะต่อรอบ","ความเร็ว")+
                   "จำนวนรอบ = "+frac("เวลาทำงานทั้งหมด","เวลาวิ่งต่อรอบ + เวลาหยุดต่อรอบ"),
                   f"ระยะต่อรอบ = 2 × {q['one']:.2f} = {q['cycle_distance']:.2f} m; ทางราบต่อรอบ = {q['flat_cycle']:.2f} m; ทางลาดขึ้น = {q['Ls']:.2f} m<br/>"+
                   frac(f"{q['cycle_distance']:.2f} m",f"{v:.5f} m/s")+
                   frac(f"{q['runtime_s']:.2f} s",f"{q['drive_cycle_s']:.2f} + {q['stop_s']:.2f} s"),
                   f"{q['cycles']:.2f} รอบ (เวลาวิ่ง {q['drive_cycle_s']:.2f} s/รอบ)")
        h+=section("3. แรงต้านและกำลังบนทางราบ","แรงต้านการกลิ้งขึ้นกับมวลรวมและค่าสัมประสิทธิ์ Crr; กำลังกลเท่ากับแรงคูณความเร็ว",
                   "Frr = Crr × m × g<br/>Pflat = Frr × v",
                   f"Frr = {q['crr']:.3f} × {m:.1f} × 9.81 = {q['Fflat']:.2f} N<br/>"
                   f"Pflat = {q['Fflat']:.2f} × {v:.5f} = {q['Pflat_mech']:.2f} W",
                   f"พลังงานกลทางราบ {q['Eflat_mech_cycle']:.4f} Wh/รอบ")
        h+=section("4. แรงและกำลังขึ้นทางลาด","แรงที่ต้องเอาชนะคือแรงโน้มถ่วงตามแนวลาดบวกแรงต้านการกลิ้งบนทางลาด",
                   "Fgrade = m × g × sin(θ)<br/>Frr,slope = Crr × m × g × cos(θ)<br/>"
                   "Fup = Fgrade + Frr,slope<br/>Pup = Fup × v",
                   f"Fgrade = {m:.1f} × 9.81 × sin({self.eslopeDeg.value():.1f}°) = {q['Fgrade']:.2f} N<br/>"
                   f"Frr,slope = {q['crr']:.3f} × {m:.1f} × 9.81 × cos({self.eslopeDeg.value():.1f}°) = {q['Frrs']:.2f} N<br/>"
                   f"Pup = ({q['Fgrade']:.2f} + {q['Frrs']:.2f}) × {v:.5f}",
                   f"{q['Pup_mech']:.2f} W; พลังงานกลขึ้นลาด {q['Eup_mech_cycle']:.4f} Wh/รอบ")
        h+=section("5. พลังงานขาลงแบบ No Regen","ขาลงไม่หักพลังงานคืนแบตเตอรี่ หากแรงโน้มถ่วงมากกว่าแรงต้านการกลิ้งให้ถือว่ากำลังขับเป็นศูนย์และระบบเบรก/การไหลเป็นผู้รับพลังงานส่วนเกิน",
                   "Fdown = max(0, Frr,slope - Fgrade)<br>Pdown = Fdown × v",
                   f"Fdown = max(0,{q['Frrs']:.2f}-{q['Fgrade']:.2f}) = {q['Fdown']:.2f} N<br>Pdown = {q['Fdown']:.2f} × {v:.5f} = {q['Pdown_mech']:.2f} W",
                   f"พลังงานกลขาลงที่ต้องขับ = {q['Edown_mech_cycle']:.4f} Wh/รอบ")
        h+=section("6. พลังงานออกตัว","คิดพลังงานจลน์เมื่อรถเร่งจากหยุดนิ่งถึงความเร็วเป้าหมาย (ยังไม่รวม loss ช่วงกระแสกระชาก)",
                   "Ek = ½ × m × v²<br/>Eacc/cycle = "+frac("Ek × จำนวนครั้งออกตัว","3600 J/Wh"),
                   f"Ek = ½ × {m:.1f} × {v:.5f}² = {0.5*m*v*v:.4f} J<br/>"+
                   frac(f"{0.5*m*v*v:.4f} × {q['starts']}","3600"),
                   f"{q['Eacc_mech_cycle']:.6f} Wh/รอบ")
        h+=section("7. พลังงานกลรวมและไฟฟ้าประมาณ","รวมพลังงานกลทุกช่วงที่คิดเป็นงานบวกแล้วหารด้วยประสิทธิภาพโดยประมาณ",
                   "Emech = (Eflat + Eup + Edown + Eacc) × จำนวนรอบ<br/>Edrive = "+
                   frac("Emech","ηdrive"),
                   f"Emech = ({q['Eflat_mech_cycle']:.4f} + {q['Eup_mech_cycle']:.4f} + {q['Edown_mech_cycle']:.4f} + "
                   f"{q['Eacc_mech_cycle']:.6f}) × {q['cycles']:.2f} = {q['Emech_total']:.2f} Wh<br/>"+
                   frac(f"{q['Emech_total']:.2f} Wh",f"{q['eff']:.3f}"),
                   f"Calculated Drive = {q['Ecalc_drive']:.2f} Wh")
        h+=section("8. กรณี Worst-case ตอนขึ้นลาด","สมมติให้มอเตอร์ใช้กำลังกลพิกัดเต็มเฉพาะช่วงขึ้นทางลาด ไม่ใช่การใช้ไฟจริงที่ยืนยันแล้ว",
                   "Pworst,battery = "+frac("กำลังพิกัดต่อมอเตอร์ × จำนวนมอเตอร์","ηup"),
                   frac(f"{self.emotorRated.value():.0f} × {self.enmot.value()}",f"{q['up_eff']:.3f}"),
                   f"{q['Pworst_batt']:.2f} W; Worst-case Drive = {q['Eworst_drive']:.2f} Wh")
        h+=section("9. พลังงานโหลดทั้งหมด","เพิ่มพลังงานไฟเลี้ยงอุปกรณ์อื่นตลอดเวลาที่เปิดระบบ",
                   "Eaux = Paux × T<br/>Eload = Edrive + Eaux",
                   f"Eaux = {self.eaux.value():.1f} × {q['runtime_h']:.2f} = {q['Eaux']:.2f} Wh<br/>"
                   f"Eload = {q['Edrive']:.2f} + {q['Eaux']:.2f}",
                   f"{q['Eload']:.2f} Wh ({'Worst-case' if q['use_worst'] else 'Calculated'})")
        h+=section("10. ความจุแบตเตอรี่หลังเผื่อ DoD และ Reserve","หารด้วย DoD เพื่อให้เหลือความจุสำรอง และคูณเผื่อ Reserve เพิ่ม",
                   "Enominal = "+frac("Eload","DoD")+"Edesign = Enominal × (1 + Reserve)<br/>Ah = "+
                   frac("Edesign","แรงดันแบตเตอรี่"),
                   frac(f"{q['Eload']:.2f}",f"{q['dod']:.3f}")+
                   f"Edesign = {q['Enom']:.2f} × (1 + {q['reserve']:.3f}) = {q['Edesign']:.2f} Wh<br/>"+
                   frac(f"{q['Edesign']:.2f} Wh",f"{V:.1f} V"),
                   f"{q['Ah']:.2f} Ah")
        h+=section("11. กระแสและ BMS","Ah คือความจุพลังงาน ส่วน A คือกระแสที่แบตเตอรี่/BMS ต้องจ่าย ต้องตรวจแยกกัน",
                   "Iup = "+frac("Pup / ηup","Vbattery")+"Iworst = "+frac("Pworst,battery","Vbattery"),
                   frac(f"{q['Pup_mech']:.2f} / {q['up_eff']:.3f}",f"{V:.1f}")+
                   frac(f"{q['Pworst_batt']:.2f}",f"{V:.1f}"),
                   f"กระแสขึ้นลาดประมาณ {q['Icalc_up']:.2f} A; Worst-case {q['Iworst']:.2f} A")
        h+=("<p><b>ข้อจำกัด:</b> ไม่มีการหักพลังงาน Regen; "
            "แบบจำลองยังไม่รวมกำลังไฟเบรกขณะลงลาดและพลังงานวินช์/เครนที่แยกแบต "
            "ประสิทธิภาพมอเตอร์ความเร็วต่ำเป็นสมมติฐาน ควรตรวจจากค่ากระแสที่วัดจริงก่อนเลือกแบต</p>")
        return h

    def export_electrical_pdf(self):
        from PySide6.QtWidgets import QFileDialog, QMessageBox
        from PySide6.QtGui import QTextDocument
        from PySide6.QtPrintSupport import QPrinter
        filename,_=QFileDialog.getSaveFileName(self,"Export Battery Calculation PDF",
                                                "Battery_Calculation_Report.pdf","PDF (*.pdf)")
        if not filename:return
        if not filename.lower().endswith(".pdf"):filename+=".pdf"
        try:
            q=self.electrical_results()
            document=QTextDocument()
            document.setDefaultFont(QFont("Noto Sans Thai",10))
            summary=(f"<h1>Electrical / Battery Engineering Report</h1>"
                     f"<p>Model: {'Worst-case' if q['use_worst'] else 'Calculated'}; "
                     f"Total mass {q['m']:.1f} kg; Battery {q['V']:.1f} V; "
                     f"Target runtime {q['runtime_h']:.2f} h</p>")
            document.setHtml(summary+self.equation_html(q)+
                "<hr/><h2>คำอธิบายภาษาไทยเพิ่มเติม</h2>"+
                self.eThaiExplain.toHtml())
            printer=QPrinter(QPrinter.HighResolution)
            printer.setOutputFormat(QPrinter.PdfFormat)
            printer.setOutputFileName(filename)
            printer.setPageSize(QPageSize(QPageSize.A4))
            document.print_(printer)
            QMessageBox.information(self,"Export PDF","บันทึกรายงานเรียบร้อย:\\n"+filename)
        except Exception as exc:
            QMessageBox.critical(self,"Export PDF ไม่สำเร็จ",str(exc))

    def calc_electrical(self):
        if not hasattr(self,"eSummary"): return
        q=self.electrical_results()
        mode="WORST-CASE FULL RATED POWER" if q["use_worst"] else "CALCULATED LOAD MODEL"
        self.eSummary.setText(
            f"{mode}\\n"
            f"Cycles in {q['runtime_h']:.2f} h = {q['cycles']:.2f} | Total travel ≈ {q['cycles']*q['cycle_distance']/1000:.3f} km\\n"
            f"Mechanical energy = {q['Emech_total']:.1f} Wh | Estimated drive energy = {q['Edrive']:.1f} Wh\\n"
            f"Auxiliary = {q['Eaux']:.1f} Wh | Load total = {q['Eload']:.1f} Wh\\n"
            f"Battery design = {q['Edesign']:.1f} Wh → {q['Ah']:.2f} Ah @ {q['V']:.1f} V"
        )
        self.eSteps.setHtml(self.equation_html(q))
        if hasattr(self,"eVars"):self.eVars.setHtml(self.electrical_variables_html())
        if hasattr(self,"allEVars"):self.allEVars.setHtml(self.electrical_variables_html())
        self.eThaiExplain.setHtml(f"""
        <h2>คู่มืออธิบายการคำนวณแบตเตอรี่ (ภาษาไทย)</h2>
        <p><b>จุดประสงค์:</b> ประมาณพลังงานที่รถต้องใช้ตลอด {q['runtime_h']:.2f} ชั่วโมง
        แล้วแปลงเป็นความจุแบตเตอรี่ Wh และ Ah โดยแยกการตรวจความสามารถจ่ายกระแสของ BMS ออกต่างหาก
        ทุกตัวเลขในหน้านี้เปลี่ยนตามข้อมูล Input โดยอัตโนมัติ</p>
        <h3>1. กำหนดมวลและเส้นทาง</h3>
        <p>ใช้มวลรวมรถพร้อมบรรทุก <b>{q['m']:.1f} kg</b> (ห้ามนับน้ำหนักเครนหรือสิ่งบรรทุกซ้ำ)
        ความเร็ว {self.espeed.value():.2f} km/h หรือ {q['v']:.5f} m/s
        ระยะไป-กลับ {q['cycle_distance']:.2f} m ต่อรอบ โดยมีทางลาดขาขึ้นและขาลงด้านละ {q['Ls']:.2f} m
        และทางราบรวม {q['flat_cycle']:.2f} m ต่อรอบ</p>
        <p><b>สูตร:</b> เวลาวิ่งต่อรอบ = ระยะไป-กลับ ÷ ความเร็ว;
        เวลาต่อรอบ = เวลาวิ่ง + เวลาหยุด;
        จำนวนรอบ = เวลาทำงานทั้งหมด ÷ เวลาต่อรอบ</p>
        <p><b>แทนค่า:</b> {q['cycle_distance']:.2f} ÷ {q['v']:.5f}
        = {q['drive_cycle_s']:.2f} วินาทีที่รถวิ่ง
        และเมื่อบวกเวลาหยุด {q['stop_s']:.2f} วินาที จะได้ {q['cycle_total_s']:.2f} วินาที/รอบ
        ดังนั้นจำนวนรอบเชิงทฤษฎี = {q['cycles']:.2f} รอบ
        (จำนวนรอบจริงอาจลดลงจากเวลายกของหรือเลี้ยว)</p>
        <h3>2. แรงต้านบนทางราบ</h3>
        <p>รถต้องออกแรงเอาชนะแรงต้านการกลิ้ง แม้ทางราบไม่มีแรงโน้มถ่วงตามแนวการเคลื่อนที่</p>
        <p><b>สูตร:</b> Frr = Crr × m × g</p>
        <p><b>แทนค่า:</b> {q['crr']:.3f} × {q['m']:.1f} × 9.81
        = <b>{q['Fflat']:.2f} N</b></p>
        <p>กำลังกล = แรง × ความเร็ว = {q['Fflat']:.2f} × {q['v']:.5f}
        = <b>{q['Pflat_mech']:.2f} W</b> ซึ่งเป็นกำลังที่ล้อต้องใช้ตามแบบจำลอง
        ไม่ใช่กำลังไฟที่แบตเตอรี่จ่ายจริง</p>
        <h3>3. แรงและกำลังขณะขึ้นทางลาด</h3>
        <p>ทางลาดมีแรงโน้มถ่วงดึงรถลงตามแนวลาดเพิ่มจากแรงต้านการกลิ้ง
        จึงต้องนำแรงทั้งสองมารวมกัน</p>
        <p><b>สูตร:</b> Fgrade = m × g × sin(มุมลาด);
        Frr,slope = Crr × m × g × cos(มุมลาด);
        Fup = Fgrade + Frr,slope</p>
        <p><b>แทนค่า:</b> Fgrade = {q['m']:.1f} × 9.81 × sin({self.eslopeDeg.value():.1f}°)
        = {q['Fgrade']:.2f} N;
        Frr,slope = {q['crr']:.3f} × {q['m']:.1f} × 9.81 × cos({self.eslopeDeg.value():.1f}°)
        = {q['Frrs']:.2f} N</p>
        <p>แรงรวม = {q['Fgrade']:.2f} + {q['Frrs']:.2f}
        = <b>{q['Fup']:.2f} N</b>;
        กำลังกลขณะขึ้นลาด = {q['Fup']:.2f} × {q['v']:.5f}
        = <b>{q['Pup_mech']:.2f} W</b></p>
        <h3>4. พลังงานจากการเร่งความเร็ว</h3>
        <p>ใช้พลังงานจลน์เพิ่มขึ้นเมื่อรถออกตัวจากหยุดนิ่งจนถึงความเร็วเป้าหมาย
        โดยสมมติว่าออกตัว {q['starts']} ครั้งต่อรอบ</p>
        <p><b>สูตร:</b> Ekinetic = ½ × m × v²;
        แปลงจูลเป็น Wh โดยหาร 3600</p>
        <p><b>แทนค่า:</b> ½ × {q['m']:.1f} × {q['v']:.5f}²
        = {0.5*q['m']*q['v']**2:.3f} J ต่อครั้ง;
        พลังงานเร่งต่อรอบ = <b>{q['Eacc_mech_cycle']:.6f} Wh</b></p>
        <p>วิธีนี้นับเฉพาะพลังงานจลน์ ไม่รวมกระแสกระชากหรือการสูญเสียเฉพาะช่วงออกตัว
        จึงต้องตรวจมอเตอร์และ BMS แยก</p>
        <h3>5. รวมพลังงานกลและแปลงเป็นพลังงานไฟฟ้า</h3>
        <p>นำพลังงานทางราบ ขึ้นลาด และเร่งความเร็วมารวมกัน
        จากนั้นคูณจำนวนรอบ ได้พลังงานกล <b>{q['Emech_total']:.2f} Wh</b></p>
        <p><b>สูตรประมาณ:</b> Edrive = Emech ÷ ηdrive</p>
        <p><b>แทนค่า:</b> {q['Emech_total']:.2f} ÷ {q['eff']:.3f}
        = <b>{q['Ecalc_drive']:.2f} Wh</b> (Calculated Model)</p>
        <p>ηdrive = {self.edriveEff.value():.1f}% เป็นค่า <b>สมมติ</b> สำหรับประเมิน
        ไม่ใช่ประสิทธิภาพที่ยืนยันแล้วของ QS Hub Motor ณ 1 km/h</p>
        <h3>6. เปรียบเทียบกรณีเผื่อกำลังสูงสุด</h3>
        <p>Worst-case สมมติให้มอเตอร์ทุกตัวใช้กำลังพิกัดเต็มตลอดช่วงขึ้นทางลาด
        โดยกำลังพิกัดรวม = {self.emotorRated.value():.0f} × {self.enmot.value()}
        = {q['rated_total']:.0f} W (กำลังกล)</p>
        <p><b>สูตร:</b> กำลังไฟจากแบตช่วงขึ้นลาด = กำลังกลพิกัดรวม ÷ ηup</p>
        <p><b>แทนค่า:</b> {q['rated_total']:.0f} ÷ {q['up_eff']:.3f}
        = <b>{q['Pworst_batt']:.2f} W</b>;
        พลังงานขับเคลื่อนรวมแบบ Worst-case = <b>{q['Eworst_drive']:.2f} Wh</b></p>
        <p>กรณีนี้เป็นสมมติฐานเพื่อเผื่อขนาด ไม่ได้หมายความว่ามอเตอร์กินไฟเต็มพิกัดจริงตลอดช่วงขึ้นเนิน</p>
        <h3>7. เพิ่มไฟเลี้ยงอุปกรณ์อื่น</h3>
        <p>อุปกรณ์ควบคุม เซนเซอร์ จอ และระบบช่วยต่าง ๆ ใช้ไฟระหว่างทำงาน
        จึงเพิ่มพลังงาน Auxiliary ตลอดเวลาที่เปิดใช้งาน</p>
        <p><b>สูตร:</b> Eaux = Paux × เวลา</p>
        <p><b>แทนค่า:</b> {self.eaux.value():.1f} × {q['runtime_h']:.2f}
        = <b>{q['Eaux']:.2f} Wh</b></p>
        <h3>8. เลือกแบบจำลองและหาพลังงานรวม</h3>
        <p>ตอนนี้เลือก <b>{"Worst-case" if q['use_worst'] else "Calculated"}</b>
        พลังงานขับเคลื่อน = {q['Edrive']:.2f} Wh</p>
        <p><b>สูตร:</b> Eload = Edrive + Eaux</p>
        <p><b>แทนค่า:</b> {q['Edrive']:.2f} + {q['Eaux']:.2f}
        = <b>{q['Eload']:.2f} Wh</b></p>
        <h3>9. เผื่อความจุใช้งาน (DoD) และสำรอง (Reserve)</h3>
        <p>DoD คือสัดส่วนความจุแบตเตอรี่ที่อนุญาตให้ใช้ เช่น 80% หมายถึงไม่วางแผนใช้เต็ม 100%
        ส่วน Reserve คือพลังงานสำรองเพิ่มสำหรับความไม่แน่นอน</p>
        <p><b>สูตร:</b> Enominal = Eload ÷ DoD;
        Edesign = Enominal × (1 + Reserve)</p>
        <p><b>แทนค่า:</b> {q['Eload']:.2f} ÷ {q['dod']:.3f}
        = {q['Enom']:.2f} Wh;
        {q['Enom']:.2f} × (1 + {q['reserve']:.3f})
        = <b>{q['Edesign']:.2f} Wh</b></p>
        <h3>10. คำนวณ Ah และตรวจ BMS</h3>
        <p><b>สูตร:</b> Ah = Edesign ÷ Vbattery</p>
        <p><b>แทนค่า:</b> {q['Edesign']:.2f} ÷ {q['V']:.1f}
        = <b>{q['Ah']:.2f} Ah</b></p>
        <p>กระแสขึ้นลาดจากการประมาณ = {q['Icalc_up']:.2f} A;
        กระแส Worst-case = {q['Iworst']:.2f} A
        ต้องตรวจทั้งกระแสต่อเนื่อง กระแสสูงสุดของเซลล์และ BMS
        รวมถึงข้อจำกัดของ Controller ก่อนเลือกแบตจริง</p>
        <h3>ข้อจำกัดที่ต้องระบุในรายงาน</h3>
        <p>ผลนี้เป็นการประมาณเบื้องต้น: แบบจำลองยังไม่คิดพลังงานไฟฟ้าขณะลงลาดหรือการเบรกแบบละเอียด
        (ไม่มีการหักพลังงานคืนจาก Regen), ยังไม่รวมพลังงานวินช์/หมุนเครนแยกต่างหาก
        หากอุปกรณ์เหล่านั้นใช้แบตอีกลูกต้องคำนวณแยก และประสิทธิภาพมอเตอร์ที่ความเร็วต่ำยังไม่ทราบ
        ควรทดสอบแรงดันและกระแสจริงเพื่อปรับผลลัพธ์ก่อนซื้อแบตเตอรี่</p>
        """)
        self.eResults.setHtml(f"""
        <h2>Battery Sizing Result</h2>
        <table cellpadding='7'>
        <tr><td>Selected model</td><td><b>{mode}</b></td></tr>
        <tr><td>Cycles in runtime</td><td>{q['cycles']:.2f}</td></tr>
        <tr><td>Theoretical mechanical energy</td><td>{q['Emech_total']:.1f} Wh</td></tr>
        <tr><td>Calculated drive estimate</td><td>{q['Ecalc_drive']:.1f} Wh</td></tr>
        <tr><td>Worst-case drive estimate</td><td>{q['Eworst_drive']:.1f} Wh</td></tr>
        <tr><td>Selected drive energy</td><td><b>{q['Edrive']:.1f} Wh</b></td></tr>
        <tr><td>Auxiliary energy</td><td>{q['Eaux']:.1f} Wh</td></tr>
        <tr><td>Load energy total</td><td>{q['Eload']:.1f} Wh</td></tr>
        <tr><td>After DoD + reserve</td><td><b>{q['Edesign']:.1f} Wh</b></td></tr>
        <tr><td>Required battery capacity</td><td><b>{q['Ah']:.2f} Ah @ {q['V']:.1f} V</b></td></tr>
        <tr><td>Calculated uphill current indicator</td><td>{q['Icalc_up']:.1f} A</td></tr>
        <tr><td>Worst-case current indicator</td><td><b>{q['Iworst']:.1f} A</b></td></tr>
        </table>
        <p><b>อย่าเลือกแบตจาก Ah อย่างเดียว:</b> ต้องตรวจ BMS continuous/peak current และความสามารถจ่ายกระแสของเซลล์ด้วย</p>
        """)

    def make_torque(self):
        w=QWidget();self.torquePage=w
        root=QVBoxLayout(w);root.setContentsMargins(16,16,16,16);root.setSpacing(12)
        root.addWidget(make_page_header("DRIVE TORQUE CALCULATION","แรงขับ • แรงบิดล้อ • กำลังมอเตอร์ • Traction • Engineering FBD",self.show_home_mode,"2 × HUB MOTOR","#e7efff","#2457a6"))

        self.torqueTabs=QTabWidget()
        root.addWidget(self.torqueTabs)

        # --- INPUT ---
        inp=QWidget();il=QHBoxLayout(inp)
        left=QWidget();form=QFormLayout(left)
        def ds(v,lo,hi,dec=3):
            q=QDoubleSpinBox();q.setRange(lo,hi);q.setDecimals(dec);q.setValue(v)
            q.setMinimumWidth(145);q.setMaximumWidth(240);return q
        self.tm=ds(300,1,5000,1); self.tgrade=ds(19,0,45,1)
        self.tspeed=ds(5,.1,50,2); self.tmu=ds(.02,0,1,3)
        self.tmotors=QSpinBox();self.tmotors.setRange(1,8);self.tmotors.setValue(2)
        self.twheelInch=ds(10.0,1.0,60.0,2)
        self.tradius=ds(.127,.0127,.762,4); self.tradius.setReadOnly(True)
        self.tsf=ds(1.30,1,3,2)
        self.taccel=ds(5,.1,60,2); self.teff=ds(85,1,100,1)
        self.ttraction=ds(.70,.05,2,2); self.tDriveLoadFrac=ds(50,10,100,1); self.tvoltage=ds(72,12,120,1)
        for lab,q in [
            ("มวลรวม m (kg)",self.tm),("ความชัน θ (deg)",self.tgrade),
            ("ความเร็ว v (km/h)",self.tspeed),("Rolling resistance μr",self.tmu),
            ("จำนวนมอเตอร์ขับ n",self.tmotors),("เส้นผ่านศูนย์กลางล้อ D (inch)",self.twheelInch),
            ("รัศมีล้อ r (m) — Auto",self.tradius),
            ("Safety Factor",self.tsf),("เวลาเร่ง 0→v (s)",self.taccel),
            ("ประสิทธิภาพ η (%)",self.teff),("สัมประสิทธิ์ยึดเกาะ μ",self.ttraction),
            ("สัดส่วนแรงกดที่ล้อขับ (%) [สมมติ]",self.tDriveLoadFrac),
            ("แรงดันแบตเตอรี่ (V)",self.tvoltage)]: form.addRow(lab,q)
        self.tUseMain=QCheckBox("ใช้ Total mass จาก Stability / Mass & CG mode")
        self.tUseMain.setChecked(True);form.addRow(self.tUseMain)
        left.setMinimumWidth(360);il.addWidget(left,1)

        right=QWidget();right.setMinimumWidth(360);rl=QVBoxLayout(right)
        wheelBox=QGroupBox("Wheel Comparison / เปรียบเทียบขนาดล้อ");wl=QVBoxLayout(wheelBox)
        self.wheelTable=QTableWidget(5,4)
        self.wheelTable.setHorizontalHeaderLabels(["ล้อ","Radius (m)","Torque (N·m)","RPM"])
        self.wheelTable.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        wl.addWidget(self.wheelTable);rl.addWidget(wheelBox)
        self.torqueSummary=QLabel();self.torqueSummary.setWordWrap(True)
        self.torqueSummary.setStyleSheet("font-size:11pt;font-weight:700;background:qlineargradient(x1:0,y1:0,x2:1,y2:0,stop:0 #eefaf4,stop:1 #f8fffb);color:#155b2a;padding:15px;border:1px solid #a9d7ba;border-radius:11px")
        rl.addWidget(self.torqueSummary)
        convention=QLabel("นิยามที่ใช้ในโปรแกรม:\n"
                          "TOTAL = ผลรวมที่รถต้องการจากมอเตอร์ขับทุกตัว\n"
                          "PER MOTOR = ค่าของมอเตอร์ 1 ตัว\n"
                          "F_motor = F_design,total ÷ n\n"
                          "T_motor = F_motor × r\n"
                          "P_mech,motor = P_mech,total ÷ n")
        convention.setWordWrap(True)
        convention.setStyleSheet("background:#fff8e9;color:#68420b;padding:12px;border:1px solid #ead39a;border-radius:10px")
        rl.addWidget(convention)
        calc=QPushButton("คำนวณใหม่ / Calculate");calc.setObjectName("primaryButton")
        calc.clicked.connect(self.calc_torque);rl.addWidget(calc)
        il.addWidget(right,2)
        torqueInputScroll=QScrollArea();torqueInputScroll.setWidgetResizable(True);torqueInputScroll.setFrameShape(QFrame.NoFrame)
        torqueInputScroll.setWidget(inp);self.torqueTabs.addTab(torqueInputScroll,"Input / ข้อมูล")
        self.torqueVars=QTextEdit();self.torqueVars.setReadOnly(True);self.torqueTabs.addTab(self.torqueVars,"ตัวแปร / Variables")

        # --- STEP CALC ---
        step=QWidget();sl=QVBoxLayout(step)
        self.torqueSteps=QTextEdit();self.torqueSteps.setReadOnly(True)
        self.torqueSteps.setStyleSheet("font-size:12px")
        sl.addWidget(self.torqueSteps)
        self.torqueTabs.addTab(step,"Σ  สูตร + แทนค่า")

        guide=QWidget();tgl=QVBoxLayout(guide)
        self.torqueGuide=QTextEdit();self.torqueGuide.setReadOnly(True);tgl.addWidget(self.torqueGuide)
        self.torqueTabs.addTab(guide,"อธิบายสูตรภาษาไทย")

        # --- FBD ---
        fbd=QWidget();fl=QVBoxLayout(fbd)
        self.torqueFBD=TorqueFBDWidget(self)
        fl.addWidget(self.torqueFBD)
        legend=QLabel("FBD แสดง W=mg, N, Fgrade, Fr, Fa/Ftotal และแรง/ทอร์คที่ล้อ โดยปรับตามค่าความชันใน Input")
        legend.setWordWrap(True);fl.addWidget(legend)
        self.torqueTabs.addTab(fbd,"△  Free Body Diagram")

        # --- MOTOR CHECK ---
        mc=QWidget();mcl=QHBoxLayout(mc)
        mf=QWidget();mform=QFormLayout(mf)
        self.motorName=QLineEdit("QS 10-inch Single Shaft 1500W 72V")
        self.motorRatedPower=ds(1500,1,20000,0)
        self.motorRatedTorque=ds(110,1,1000,1)
        self.motorPeakTorque=ds(220,1,2000,1)
        self.motorMaxRPM=ds(600,1,5000,0)
        self.controllerCurrent=ds(100,1,1000,1)
        self.powerReserve=ds(1.20,1.0,3.0,2)
        for lab,q in [("Motor",self.motorName),("Rated Power / motor (W)",self.motorRatedPower),
                      ("Rated Torque (N·m)",self.motorRatedTorque),("Peak Torque (N·m)",self.motorPeakTorque),
                      ("Max RPM",self.motorMaxRPM),("Controller current limit (A)",self.controllerCurrent),("Power reserve factor",self.powerReserve)]:
            mform.addRow(lab,q)
        mcl.addWidget(mf,1)
        self.motorCheckText=QTextEdit();self.motorCheckText.setReadOnly(True);mcl.addWidget(self.motorCheckText,2)
        self.torqueTabs.addTab(mc,"▣  Motor Check")

        # --- GRAPH ---
        gp=QWidget();gl=QVBoxLayout(gp)
        self.torqueGraph=TorqueGraphWidget(self);gl.addWidget(self.torqueGraph)
        self.torqueTabs.addTab(gp,"▥  Graphs")

        # --- REPORT ---
        rp=QWidget();rpl=QVBoxLayout(rp)
        exp=QPushButton("Export PDF / ส่งออกรายงาน PDF");exp.setObjectName("primaryButton")
        exp.setStyleSheet("font-size:11pt")
        exp.clicked.connect(self.export_torque_pdf);rpl.addWidget(exp)
        self.torqueReportPreview=QPlainTextEdit();self.torqueReportPreview.setReadOnly(True);rpl.addWidget(self.torqueReportPreview)
        self.torqueTabs.addTab(rp,"▤  Report")

        controls=[self.tm,self.tgrade,self.tspeed,self.tmu,self.tradius,self.tsf,self.taccel,
                  self.teff,self.ttraction,self.tDriveLoadFrac,self.tvoltage,self.motorRatedPower,self.motorRatedTorque,
                  self.motorPeakTorque,self.motorMaxRPM,self.controllerCurrent,self.powerReserve]
        for q in controls:q.valueChanged.connect(self.calc_torque)
        self.tmotors.valueChanged.connect(self.calc_torque);self.tUseMain.toggled.connect(self.calc_torque)
        self.twheelInch.valueChanged.connect(self.update_wheel_from_inches)
        self.tabs.addTab(w,"Torque / แรงขับ-ทอร์ค")
        self.update_wheel_from_inches()

    def update_wheel_from_inches(self):
        """Convert entered wheel outside diameter in inches to radius in metres."""
        if not hasattr(self,"twheelInch"): return
        diameter_m=self.twheelInch.value()*0.0254
        radius_m=diameter_m/2.0
        self.tradius.blockSignals(True)
        self.tradius.setValue(radius_m)
        self.tradius.blockSignals(False)
        self.calc_torque()

    def torque_results(self, radius=None, slope=None):
        m=self.mt.value() if self.tUseMain.isChecked() and hasattr(self,"mt") else self.tm.value()
        r=self.tradius.value() if radius is None else radius
        deg=self.tgrade.value() if slope is None else slope
        th=math.radians(deg);v=self.tspeed.value()/3.6
        n=max(1,self.tmotors.value());eta=max(self.teff.value()/100.0,.01)
        a=v/max(self.taccel.value(),.01)
        Fg=m*G*math.sin(th)
        Fr=self.tmu.value()*m*G*math.cos(th)
        Fa=m*a
        Fsum=Fg+Fr+Fa
        Fdesign=Fsum*self.tsf.value()
        Fmotor=Fdesign/n
        T=Fmotor*r
        rpm=v/(2*math.pi*r)*60
        Pcalc_total=Fsum*v
        Pcalc_per=Pcalc_total/n
        Pwheel=Fdesign*v
        Pmech_per=Pwheel/n
        omega=2*math.pi*rpm/60.0
        Ptorque_per=T*omega
        Ptorque_total=Ptorque_per*n
        Ptotal=Pwheel/eta
        Pelec_per=Ptotal/n
        Ibatt=Ptotal/max(self.tvoltage.value(),.1)

        # Traction limit must use normal load carried by the driven wheels,
        # not the total vehicle normal load. Default assumption = 50% for
        # two driven hub wheels + two support wheels; user can edit it.
        Ntotal=m*G*math.cos(th)
        drive_load_fraction=max(0.0,min(1.0,self.tDriveLoadFrac.value()/100.0))
        Ndrive=Ntotal*drive_load_fraction
        Ftraction=self.ttraction.value()*Ndrive
        return dict(m=m,r=r,deg=deg,v=v,a=a,Fg=Fg,Fr=Fr,Fa=Fa,Fsum=Fsum,Fdesign=Fdesign,
                    Fmotor=Fmotor,T=T,rpm=rpm,Pcalc_total=Pcalc_total,Pcalc_per=Pcalc_per,
                    Pwheel=Pwheel,Pmech_per=Pmech_per,
                    omega=omega,Ptorque_per=Ptorque_per,Ptorque_total=Ptorque_total,
                    Ptotal=Ptotal,Pelec_per=Pelec_per,Ibatt=Ibatt,
                    Ntotal=Ntotal,Ndrive=Ndrive,drive_load_fraction=drive_load_fraction,
                    Ftraction=Ftraction,n=n,eta=eta)

    def torque_formula_html(self,q):
        def frac(a,b):
            return ("<table cellspacing='0' cellpadding='2' style='display:inline-table;margin:3px 8px;vertical-align:middle'>"
                    f"<tr><td align='center' style='border-bottom:1px solid #243b53;padding:2px 8px'><b>{a}</b></td></tr>"
                    f"<tr><td align='center' style='padding:2px 8px'><b>{b}</b></td></tr></table>")
        def sec(n,title,meaning,formula,sub,result):
            return (f"<h3 style='color:#17456b'>{n}. {title}</h3>"
                    f"<p><b>คำอธิบายภาษาไทย:</b> {meaning}</p>"
                    f"<p><b>สูตรภาษาไทย</b></p><div style='margin-left:18px;font-size:12pt;color:#17324d'><b>{self._thai_formula_text(title)}</b></div>"
                    f"<p><b>สูตรตัวแปร</b></p><div style='margin-left:18px;font-size:12pt'>{formula}</div>"
                    f"<p><b>แทนค่า</b></p><div style='margin-left:18px'>{sub}</div>"
                    f"<p style='color:#176337'><b>คำตอบ: {result}</b></p><hr>")
        traction_margin=q['Ftraction']/q['Fdesign'] if q['Fdesign'] else 999
        recommended=q['Pmech_per']*self.powerReserve.value()
        current_per=q['Ibatt']/q['n'] if q['n'] else 0
        tq_margin=self.motorPeakTorque.value()/q['T'] if q['T'] else 999
        power_margin=self.motorRatedPower.value()/q['Pmech_per'] if q['Pmech_per'] else 999
        rpm_margin=self.motorMaxRPM.value()/q['rpm'] if q['rpm'] else 999
        current_margin=self.controllerCurrent.value()/current_per if current_per else 999
        h="<h2>DRIVE TORQUE — สูตรครบ + คำอธิบายภาษาไทย + แทนค่า</h2>"
        h+=("<p>ทุกหัวข้อเรียงเป็น <b>ความหมาย → สูตรภาษาไทย → สูตรตัวแปร → แทนค่า → ผลลัพธ์</b> และเปลี่ยนตาม Input อัตโนมัติ</p>"
           "<h3>ตัวแปรและหน่วย</h3><table cellpadding='5' cellspacing='0' border='1'>"
           f"<tr><td>m</td><td>มวลรวมรถ</td><td>{q['m']:.2f} kg</td></tr>"
           f"<tr><td>θ</td><td>มุมทางลาด</td><td>{q['deg']:.2f}°</td></tr>"
           f"<tr><td>D, r</td><td>เส้นผ่านศูนย์กลาง / รัศมีล้อ</td><td>{self.twheelInch.value():.2f} in / {q['r']:.5f} m</td></tr>"
           f"<tr><td>v</td><td>ความเร็วรถ</td><td>{self.tspeed.value():.2f} km/h = {q['v']:.5f} m/s</td></tr>"
           f"<tr><td>n</td><td>จำนวนมอเตอร์ขับ</td><td>{q['n']} ตัว</td></tr>"
           f"<tr><td>SF</td><td>Safety Factor</td><td>{self.tsf.value():.2f}</td></tr>"
           f"<tr><td>η</td><td>ประสิทธิภาพระบบขับ</td><td>{q['eta']:.3f}</td></tr></table>")
        h+=sec(1,"แปลงขนาดล้อเป็นรัศมี","แรงบิดที่ล้อขึ้นกับรัศมีล้อ จึงต้องแปลงนิ้วเป็นเมตรก่อน",
               "D<sub>m</sub> = D<sub>inch</sub> × 0.0254<br>r = "+frac("D_m","2"),
               f"D_m = {self.twheelInch.value():.2f} × 0.0254 = {self.twheelInch.value()*0.0254:.5f} m<br>r = "+frac(f"{self.twheelInch.value()*0.0254:.5f}","2"),f"r = {q['r']:.5f} m")
        h+=sec(2,"แปลงความเร็วและหาความเร่ง","ใช้ความเร็วหน่วย m/s เพื่อคำนวณแรงและกำลัง",
               "v = "+frac("v(km/h)","3.6")+"<br>a = "+frac("v","t_acc"),
               "v = "+frac(f"{self.tspeed.value():.2f}","3.6")+"<br>a = "+frac(f"{q['v']:.5f}",f"{self.taccel.value():.2f}"),f"v = {q['v']:.5f} m/s, a = {q['a']:.5f} m/s²")
        h+=sec(3,"แรงจากความชัน","องค์ประกอบของน้ำหนักที่ดึงรถลงตามแนวลาด",
               "F<sub>grade</sub> = m g sinθ",f"F<sub>grade</sub> = {q['m']:.2f} × 9.81 × sin({q['deg']:.2f}°) = {q['Fg']:.2f} N",f"{q['Fg']:.2f} N")
        h+=sec(4,"แรงต้านการกลิ้ง","แรงต้านจากยางและพื้นในแบบจำลอง Crr",
               "F<sub>rr</sub> = Crr × m g cosθ",f"F<sub>rr</sub> = {self.tmu.value():.3f} × {q['m']:.2f} × 9.81 × cos({q['deg']:.2f}°) = {q['Fr']:.2f} N",f"{q['Fr']:.2f} N")
        h+=sec(5,"แรงสำหรับเร่งรถ","ตามกฎข้อที่สองของนิวตัน",
               "F<sub>a</sub> = m a",f"F<sub>a</sub> = {q['m']:.2f} × {q['a']:.5f} = {q['Fa']:.2f} N",f"{q['Fa']:.2f} N")
        h+=sec(6,"แรงรวมและแรงออกแบบ","รวมแรงที่รถต้องเอาชนะ แล้วคูณ Safety Factor",
               "F<sub>sum</sub> = Fgrade + Frr + Fa<br>F<sub>design</sub> = Fsum × SF",
               f"Fsum = {q['Fg']:.2f} + {q['Fr']:.2f} + {q['Fa']:.2f} = {q['Fsum']:.2f} N<br>Fdesign = {q['Fsum']:.2f} × {self.tsf.value():.2f}",f"Fdesign,total = {q['Fdesign']:.2f} N")
        h+=sec(7,"แรงต่อมอเตอร์","สมมติให้มอเตอร์ขับแบ่งแรงเท่ากัน",
               "F<sub>motor</sub> = "+frac("F_design,total","n"),frac(f"{q['Fdesign']:.2f}",str(q['n'])),f"{q['Fmotor']:.2f} N / motor")
        h+=sec(8,"แรงบิดต่อล้อ / Hub Motor","แรงขับคูณรัศมีล้อให้แรงบิดที่ล้อ",
               "T = F<sub>motor</sub> × r",f"{q['Fmotor']:.2f} × {q['r']:.5f}",f"{q['T']:.2f} N·m / motor")
        h+=sec(9,"รอบล้อและความเร็วเชิงมุม","ใช้เส้นรอบวงล้อหาจำนวนรอบต่อนาที และแปลงเป็น rad/s",
               "RPM = "+frac("v","2πr")+" × 60<br>ω = "+frac("2π × RPM","60"),
               "RPM = "+frac(f"{q['v']:.5f}",f"2π×{q['r']:.5f}")+f" × 60 = {q['rpm']:.2f}<br>ω = "+frac(f"2π×{q['rpm']:.2f}","60"),f"RPM = {q['rpm']:.2f}, ω = {q['omega']:.4f} rad/s")
        h+=sec(10,"กำลังกล","กำลังกลตรวจได้ทั้งจาก Fv และ Tω; สองวิธีควรให้ค่าเดียวกัน",
               "P<sub>design,total</sub> = Fdesign × v<br>P<sub>motor</sub> = "+frac("P_design,total","n")+"<br>P = Tω",
               f"Ptotal = {q['Fdesign']:.2f} × {q['v']:.5f} = {q['Pwheel']:.2f} W<br>Pmotor = "+frac(f"{q['Pwheel']:.2f}",str(q['n']))+f"<br>Tω = {q['T']:.2f} × {q['omega']:.4f} = {q['Ptorque_per']:.2f} W",f"{q['Pmech_per']:.2f} W / motor; รวม {q['Pwheel']:.2f} W")
        h+=sec(11,"กำลังไฟฟ้าและกระแสแบตเตอรี่","กำลังไฟฟ้าต้องมากกว่ากำลังกลเมื่อมีการสูญเสีย",
               "P<sub>elec,total</sub> = "+frac("P_mech,total","η")+"<br>I<sub>batt</sub> = "+frac("P_elec,total","V"),
               frac(f"{q['Pwheel']:.2f}",f"{q['eta']:.3f}")+"<br>I = "+frac(f"{q['Ptotal']:.2f}",f"{self.tvoltage.value():.1f}"),f"Pelec ≈ {q['Ptotal']:.2f} W, Ibatt ≈ {q['Ibatt']:.2f} A")
        h+=sec(12,"ขีดจำกัดแรงยึดเกาะ","แรงยึดเกาะต้องคำนวณจากแรงกดที่อยู่บนล้อขับจริง ไม่ใช่น้ำหนักรถทั้งหมด",
               "N<sub>total</sub> = mg cosθ<br>N<sub>drive</sub> = λ<sub>drive</sub>N<sub>total</sub><br>F<sub>traction,max</sub> = μN<sub>drive</sub><br>Margin = "+frac("F_traction,max","F_design"),
               f"Ntotal = {q['Ntotal']:.2f} N<br>Ndrive = {self.tDriveLoadFrac.value():.1f}% × {q['Ntotal']:.2f} = {q['Ndrive']:.2f} N<br>Fmax = {self.ttraction.value():.3f}×{q['Ndrive']:.2f} = {q['Ftraction']:.2f} N<br>Margin = "+frac(f"{q['Ftraction']:.2f}",f"{q['Fdesign']:.2f}"),f"Traction margin = {traction_margin:.3f}×")
        h+=sec(13,"ตรวจมอเตอร์และ Controller","เปรียบเทียบค่าที่ต้องการกับพิกัดที่กรอก โดยค่า margin ≥ 1 เป็นเพียงการผ่านเชิงตัวเลขเบื้องต้น",
               "Torque margin = "+frac("T_peak","T_required")+"Power margin = "+frac("P_rated","P_required")+"RPM margin = "+frac("RPM_max","RPM_required")+"Current margin = "+frac("I_controller","I_motor"),
               frac(f"{self.motorPeakTorque.value():.1f}",f"{q['T']:.2f}")+frac(f"{self.motorRatedPower.value():.0f}",f"{q['Pmech_per']:.2f}")+frac(f"{self.motorMaxRPM.value():.0f}",f"{q['rpm']:.2f}")+frac(f"{self.controllerCurrent.value():.1f}",f"{current_per:.2f}"),f"Torque {tq_margin:.2f}× | Power {power_margin:.2f}× | RPM {rpm_margin:.2f}× | Current {current_margin:.2f}×; กำลังแนะนำ ≈ {recommended:.1f} W/motor")
        h+=("<p><b>ข้อจำกัด:</b> สูตรนี้เป็นแบบจำลองกำลังขับเบื้องต้น ยังต้องใช้ Torque-speed curve, current limit, โหลดกดล้อขับจริง, "
           "ประสิทธิภาพที่ความเร็วใช้งานจริง และข้อมูลยาง/พื้นก่อนสรุปอุปกรณ์</p>")
        return h

    def torque_guide_html(self,q):
        return f"""<h2>คำอธิบายสูตร DRIVE TORQUE ภาษาไทย</h2>
        <p><b>ลำดับคิด:</b> เริ่มจากหาแรงที่รถต้องเอาชนะ 3 ส่วน ได้แก่ แรงจากทางชัน แรงต้านการกลิ้ง และแรงที่ใช้เร่งรถ จากนั้นรวมแรงและคูณ Safety Factor แล้วแบ่งให้มอเตอร์ {q['n']} ตัว</p>
        <p><b>แรงบิด:</b> หลังรู้แรงต่อมอเตอร์แล้วจึงคูณรัศมีล้อ ได้แรงบิดที่ Hub Motor แต่ละตัวต้องสร้างที่ล้อ หากใช้ล้อใหญ่ขึ้น แรงบิดที่ต้องการจะเพิ่มขึ้นเมื่อแรงขับเท่าเดิม</p>
        <p><b>กำลัง:</b> ใช้ P=Fv เป็นวิธีหลัก และตรวจซ้ำด้วย P=Tω เพื่อจับความผิดพลาดของหน่วย จากค่าปัจจุบันกำลังกลออกแบบต่อมอเตอร์คือ <b>{q['Pmech_per']:.2f} W</b></p>
        <p><b>กระแส:</b> ประมาณจากกำลังไฟฟ้ารวม ÷ แรงดันแบตเตอรี่ ได้ประมาณ <b>{q['Ibatt']:.2f} A</b> แต่กระแสจริงขึ้นกับ Controller, efficiency และจุดทำงานของมอเตอร์</p>
        <p><b>Traction:</b> ต่อให้มอเตอร์แรงพอ รถก็อาจล้อฟรีได้ถ้าแรงยึดเกาะไม่พอ จึงตรวจ μN_drive เพิ่มอีกชั้นหนึ่ง โดยใช้สัดส่วนแรงกดที่ล้อขับ</p>
        <p><b>หมายเหตุ:</b> ค่า PASS/CHECK เป็นการตรวจเบื้องต้นจากค่าที่กรอก ไม่ใช่การรับรองความปลอดภัยหรือการรับรองสมรรถนะของผู้ผลิต</p>"""

    def export_torque_pdf(self):
        docs=QStandardPaths.writableLocation(QStandardPaths.DocumentsLocation) or str(Path.home())
        default_path=str(Path(docs)/"Drive_Torque_Engineering_Report.pdf")
        filename,_=QFileDialog.getSaveFileName(self,"Export Drive Torque PDF",default_path,"PDF (*.pdf)")
        if not filename:return
        if not filename.lower().endswith(".pdf"):filename+=".pdf"
        try:
            q=self.torque_results()
            html=(
                f"<h1>DRIVE TORQUE ENGINEERING REPORT</h1><p>Version {APP_VERSION} | Generated {datetime.now().strftime('%Y-%m-%d %H:%M')}</p>"
                +self.torque_formula_html(q)
                +"<hr><h2>คำอธิบายเพิ่มเติม</h2>"+self.torque_guide_html(q)
                +"<hr><h2>Motor Check</h2>"+self.motorCheckText.toHtml()
            )
            doc=QTextDocument();doc.setDefaultFont(QFont(choose_ui_font_family(),10));doc.setHtml(html)
            printer=QPrinter(QPrinter.HighResolution);printer.setOutputFormat(QPrinter.PdfFormat)
            printer.setOutputFileName(filename);printer.setPageSize(QPageSize(QPageSize.A4));doc.print_(printer)
            if not Path(filename).exists() or Path(filename).stat().st_size<1000:
                raise RuntimeError("PDF file was not created correctly")
            QMessageBox.information(self,"Export PDF","บันทึกรายงานเรียบร้อย:\n"+filename)
        except Exception as exc:
            QMessageBox.critical(self,"Export PDF ไม่สำเร็จ",str(exc))

    def calc_torque(self):
        if not hasattr(self,"torqueSteps"):return
        q=self.torque_results()
        if self.tUseMain.isChecked() and hasattr(self,"mt"):
            self.tm.blockSignals(True);self.tm.setValue(q["m"]);self.tm.blockSignals(False)

        traction_margin=q["Ftraction"]/q["Fdesign"] if q["Fdesign"] else 999
        tq_margin=self.motorPeakTorque.value()/q["T"] if q["T"] else 999
        power_margin=self.motorRatedPower.value()/q["Pmech_per"] if q["Pmech_per"] else 999
        recommended_watt=q["Pmech_per"]*self.powerReserve.value()
        watt_cross_error=abs(q["Pwheel"]-q["Ptorque_total"])/max(q["Pwheel"],1e-9)*100.0
        rpm_margin=self.motorMaxRPM.value()/q["rpm"] if q["rpm"] else 999
        current_per=max(q["Ibatt"]/q["n"],0)
        current_margin=self.controllerCurrent.value()/current_per if current_per else 999

        self.torqueSummary.setText(
            f"TOTAL force ({q['n']} motors) = {q['Fdesign']:,.1f} N   |   "
            f"PER MOTOR force = {q['Fmotor']:,.1f} N   |   "
            f"PER WHEEL torque = {q['T']:,.1f} N·m   |   RPM {q['rpm']:,.0f}\n"
            f"Power before SF TOTAL = {q['Pcalc_total']:,.1f} W   |   "
            f"Design power TOTAL = {q['Pwheel']:,.1f} W   |   "
            f"Design power PER MOTOR = {q['Pmech_per']:,.1f} W   |   "
            f"Electrical input TOTAL = {q['Ptotal']/1000:.2f} kW   |   Ibattery ≈ {q['Ibatt']:.1f} A   |   Traction margin {traction_margin:.2f}×")

        # V45: removed obsolete plain-text calculation block; rich formula view below is the single source of truth.
        # V37: Thai explanation -> formula -> substitution -> result flow.
        self.torqueSteps.setHtml(self.torque_formula_html(q))
        if hasattr(self,"torqueVars"):self.torqueVars.setHtml(self.torque_variables_html())
        if hasattr(self,"allTorqueVars"):self.allTorqueVars.setHtml(self.torque_variables_html())
        if hasattr(self,"torqueGuide"):
            self.torqueGuide.setHtml(self.torque_guide_html(q))

        # Wheel comparison
        for row,(name,r) in enumerate([("8 in",.1016),("10 in",.127),("12 in",.1524),("16 in",.2032),("Custom",self.tradius.value())]):
            x=self.torque_results(radius=r)
            for col,val in enumerate([name,f"{r:.4f}",f"{x['T']:.1f}",f"{x['rpm']:.0f}"]):
                self.wheelTable.setItem(row,col,QTableWidgetItem(val))

        def verdict(x): return "PASS" if x>=1 else "CHECK"
        self.motorCheckText.setHtml(f"""
        <h2>Motor Check / ตรวจสอบมอเตอร์</h2>
        <p><b>{self.motorName.text()}</b></p>
        <table cellpadding='7'>
        <tr><td><b>Design force — TOTAL vehicle ({q['n']} motors)</b></td><td><b>{q['Fdesign']:.1f} N</b></td></tr>
        <tr><td>Drive force — PER MOTOR (1 motor)</td><td>{q['Fmotor']:.1f} N</td></tr>
        <tr><td>Required torque — PER MOTOR / wheel</td><td><b>{q['T']:.1f} N·m</b></td></tr>
        <tr><td>Calculated power before SF — TOTAL</td><td>{q['Pcalc_total']:.1f} W</td></tr>
        <tr><td>Calculated power before SF — PER MOTOR</td><td>{q['Pcalc_per']:.1f} W</td></tr>
        <tr><td><b>Design mechanical power after SF — TOTAL ({q['n']} motors)</b></td><td><b>{q['Pwheel']:.1f} W</b></td></tr>
        <tr><td><b>Design mechanical power after SF — PER MOTOR</b></td><td><b>{q['Pmech_per']:.1f} W</b></td></tr>
        <tr><td>Required torque / wheel</td><td><b>{q['T']:.1f} N·m</b></td></tr>
        <tr><td>Peak torque input</td><td>{self.motorPeakTorque.value():.1f} N·m</td></tr>
        <tr><td>Torque margin</td><td><b>{tq_margin:.2f}× — {verdict(tq_margin)}</b></td></tr>
        <tr><td>Required mechanical power / motor</td><td><b>{q['Pmech_per']:.0f} W</b></td></tr>
        <tr><td>Cross-check T×ω / motor</td><td>{q['Ptorque_per']:.0f} W</td></tr>
        <tr><td>Recommended motor power ({self.powerReserve.value():.2f}× reserve)</td><td><b>{recommended_watt:.0f} W / motor</b></td></tr>
        <tr><td>Motor rated power input</td><td>{self.motorRatedPower.value():.0f} W / motor</td></tr>
        <tr><td>Mechanical power margin</td><td><b>{power_margin:.2f}× — {verdict(power_margin)}</b></td></tr>
        <tr><td>Estimated electrical input total</td><td>{q['Ptotal']:.0f} W</td></tr>
        <tr><td>Estimated electrical input / motor</td><td>{q['Pelec_per']:.0f} W</td></tr>
        <tr><td>Fv vs Tω check error</td><td>{watt_cross_error:.4f}%</td></tr>
        <tr><td>Wheel RPM</td><td>{q['rpm']:.0f} rpm</td></tr>
        <tr><td>RPM margin</td><td><b>{rpm_margin:.2f}× — {verdict(rpm_margin)}</b></td></tr>
        <tr><td>Battery current approx.</td><td>{q['Ibatt']:.1f} A</td></tr>
        <tr><td>Approx. current / motor</td><td>{current_per:.1f} A</td></tr>
        <tr><td>Controller current margin</td><td><b>{current_margin:.2f}× — {verdict(current_margin)}</b></td></tr>
        <tr><td>Traction margin</td><td><b>{traction_margin:.2f}× — {verdict(traction_margin)}</b></td></tr>
        </table>
        <p><i>ใช้ข้อมูล Torque-speed curve และ current limits จากผู้ผลิตจริงก่อนสรุปการเลือกมอเตอร์/Controller</i></p>
        """)

        self.torqueReportPreview.setPlainText(
            f"TORQUE REPORT SUMMARY\n\nMass = {q['m']:.2f} kg\nSlope = {q['deg']:.2f}°\n"
            f"Speed = {self.tspeed.value():.2f} km/h\nDesign force = {q['Fdesign']:.2f} N\n"
            f"Wheel torque = {q['T']:.2f} N·m/wheel\nWheel RPM = {q['rpm']:.1f} rpm\n"
            f"Wheel diameter = {self.twheelInch.value():.2f} inch -> radius = {q['r']:.5f} m\n"
            f"Power before SF TOTAL = {q['Pcalc_total']:.1f} W\n"
            f"Design mechanical power TOTAL = {q['Pwheel']:.1f} W\n"
            f"Design mechanical power PER MOTOR = {q['Pmech_per']:.1f} W\n"
            f"Recommended motor watt = {recommended_watt:.1f} W/motor ({self.powerReserve.value():.2f}x reserve)\n"
            f"Electrical input total ≈ {q['Ptotal']:.1f} W\nBattery current ≈ {q['Ibatt']:.2f} A\n"
            f"Traction margin = {traction_margin:.2f}×\nTorque margin = {tq_margin:.2f}×\nPower margin = {power_margin:.2f}×")
        if hasattr(self,"torqueFBD"):self.torqueFBD.update()
        if hasattr(self,"torqueGraph"):self.torqueGraph.update()


    def stability_formula_html(self):
        d=self.inputs();g=G;th=math.radians(d["th"])
        sf,MO,MR=self.calc_side(d)
        pivot=d["W"]/2
        yL=abs(d["L"]*math.sin(th));yB=abs((d["L"]/2)*math.sin(th))
        mveh=max(0.0,d["mt"]-d["ml"]-d["mb"])
        FL=d["kd"]*d["ml"]*g
        dL=max(0.0,yL-pivot);rL=max(0.0,pivot-yL)
        dB=max(0.0,yB-pivot);rB=max(0.0,pivot-yB)
        MOL=FL*dL;MRL=d["ml"]*g*rL;MOB=d["mb"]*g*dB;MRB=d["mb"]*g*rB;MRV=mveh*g*pivot
        rear=-d["WB"]/2;front=d["WB"]/2;xc=rear+d["xC"]
        xload=xc+d["L"]*math.cos(th);xboom=xc+(d["L"]/2)*math.cos(th)
        sfF,sfR=self.longitudinal_sf_at(d,d["th"])
        slope=self.slope_stability_results(d)
        rows,sm,xg,yg,zg=self.component_values() if hasattr(self,"comp") else ([],0,0,0,0)

        def frac(a,b):
            return ("<table cellspacing='0' cellpadding='2' style='display:inline-table;margin:3px 8px;vertical-align:middle'>"
                    f"<tr><td align='center' style='border-bottom:1px solid #243b53;padding:2px 8px'><b>{a}</b></td></tr>"
                    f"<tr><td align='center' style='padding:2px 8px'><b>{b}</b></td></tr></table>")
        def sec(n,title,meaning,thai_formula,var_formula,sub,result):
            return (f"<div style='border:1px solid #d6e0ea;padding:14px 16px;margin:12px 0;background:#fbfdff'>"
                    f"<h3 style='color:#17456b'>{n}. {title}</h3><p><b>คำอธิบายภาษาไทย:</b> {meaning}</p>"
                    f"<p><b>สูตรภาษาไทย</b></p><div style='margin-left:18px;font-size:12pt'><b>{thai_formula}</b></div>"
                    f"<p><b>สูตรตัวแปร</b></p><div style='margin-left:18px;font-size:12pt'>{var_formula}</div>"
                    f"<p><b>แทนค่า</b></p><div style='margin-left:18px'>{sub}</div>"
                    f"<p style='color:#176337'><b>คำตอบ: {result}</b></p></div>")

        html="<h2>STABILITY ANALYSIS — สูตรครบ + แทนค่า</h2>"
        html+="<p><b>หลักสำคัญ:</b> มวลทุกก้อนต้องถูกนับเป็น Overturning หรือ Resisting รอบแนว Pivot เพียงครั้งเดียว และ Total mass ต้องไม่บวก Payload ซ้ำ</p>"
        html+=sec(1,"แรงโหลดออกแบบ","ใช้ Dynamic Factor กับ Payload เฉพาะเมื่อแรงนั้นทำให้คว่ำ; ด้านต้านใช้ Payload จริง",
                  "แรงโหลดออกแบบ = Dynamic Factor × มวลโหลด × g","F_L = Kdyn × m_L × g",
                  f"F_L = {d['kd']:.2f} × {d['ml']:.2f} × 9.81 = {FL:.2f} N",f"{FL:.2f} N")
        html+=sec(2,"ตำแหน่งด้านข้างและ Pivot","หาระยะ Payload/Boom จากกึ่งกลางรถและเทียบกับ W/2",
                  "ตำแหน่งด้านข้าง = |ระยะแขน × sinθ|; Pivot = W/2",
                  "y_L=|Lsinθ|, y_B=|(L/2)sinθ|, p=W/2",
                  f"y_L={yL:.3f} m, y_B={yB:.3f} m, p={pivot:.3f} m",
                  f"Payload {'เลย' if yL>pivot else 'ยังอยู่ใน'} แนวรองรับ")
        html+=sec(3,"โมเมนต์คว่ำด้านข้าง","มวลที่อยู่นอก Pivot เท่านั้นที่สร้างโมเมนต์คว่ำ",
                  "โมเมนต์คว่ำ = ผลรวม(น้ำหนัก × ระยะที่เลย Pivot)",
                  "M_O = F_L max(0,y_L-p) + m_B g max(0,y_B-p)",
                  f"M_OL={FL:.2f}×{dL:.3f}={MOL:.2f}<br>M_OB={d['mb']:.2f}×9.81×{dB:.3f}={MOB:.2f}",
                  f"M_O={MO:.2f} N·m")
        html+=sec(4,"โมเมนต์ต้านด้านข้าง","มวลส่วนรถ รวมถึง Payload/Boom ที่ยังอยู่ด้านใน Pivot ต้องช่วยต้าน ไม่ควรถูกละทิ้ง",
                  "โมเมนต์ต้าน = รถส่วนหลัก + Payload ที่อยู่ด้านใน + Boom ที่อยู่ด้านใน",
                  "M_R = m_vehicle g p + m_L g max(0,p-y_L) + m_B g max(0,p-y_B)",
                  f"M_vehicle={mveh:.2f}×9.81×{pivot:.3f}={MRV:.2f}<br>M_payload,res={d['ml']:.2f}×9.81×{rL:.3f}={MRL:.2f}<br>M_boom,res={d['mb']:.2f}×9.81×{rB:.3f}={MRB:.2f}",
                  f"M_R={MR:.2f} N·m; SF_side={'∞' if sf>=999 else f'{sf:.3f}'}")
        html+=sec(5,"การคว่ำหน้า-หลัง","ใช้เพลาหน้า/หลังเป็น Pivot และรวมโมเมนต์ทุกมวลตามตำแหน่งจริงในแนวยาว",
                  "Safety Factor = ผลรวมโมเมนต์ต้าน ÷ ผลรวมโมเมนต์คว่ำ",
                  "SF_front=ΣM_R/ΣM_O; SF_rear=ΣM_R/ΣM_O",
                  f"x_rear={rear:.3f}, x_front={front:.3f}, x_crane={xc:.3f}, x_load={xload:.3f}, x_boom={xboom:.3f}",
                  f"SF_front={'∞' if sfF>=999 else f'{sfF:.3f}'}, SF_rear={'∞' if sfR>=999 else f'{sfR:.3f}'}")
        html+=sec(6,"เสถียรภาพขณะวิ่งขึ้นทางลาด","ใช้ CG รวมตอนวิ่ง, ความสูง CG, ความชัน และความเร่ง ตรวจโมเมนต์รอบเพลาหลัง",
                  "ระยะจาก CG ถึงเพลาหลัง = x_CG,drive - x_rear; การเลื่อนแนวแรง = h[tanα + a/(g cosα)]",
                  "d_shift=h tanα + h a/(g cosα); SF_slope=[g cosα·d_rear]/[h(g sinα+a)]",
                  f"d_rear={slope['rear_arm']:.3f} m<br>d_slope={slope['shift_slope']:.3f} m<br>d_acc={slope['shift_acc']:.3f} m<br>margin={slope['margin']:.3f} m",
                  ("SF_slope=∞" if slope["sf"]>=999 else f"SF_slope={slope['sf']:.3f}"))
        if sm>0:
            contrib="<br>".join([f"{name}: m={m:.2f} kg, x={x:.3f}, y={y:.3f}, z={z:.3f}" for name,m,x,y,z in rows])
            html+=sec(7,"Combined CG จากตารางมวล","ใช้ค่าเฉลี่ยถ่วงน้ำหนักของมวลรายชิ้นสำหรับ Driving CG และ CG height",
                      "CG รวม = Σ(m_i × ตำแหน่ง_i) ÷ Σm_i",
                      "x_CG=Σ(m_i x_i)/Σm_i; y_CG=Σ(m_i y_i)/Σm_i; z_CG=Σ(m_i z_i)/Σm_i",
                      contrib+f"<br>Σm={sm:.2f} kg",f"x={xg:.3f}, y={yg:.3f}, z={zg:.3f} m")
        best=self.stability_worst_record()
        html+=sec(8,"Worst Case","สแกนมุมเครน -90° ถึง +90° ทีละ 1° และตรวจ Side/Front/Rear",
                  "Safety Factor วิกฤต = ค่าต่ำสุดจากทุกมุมและทุกทิศ",
                  "SF_worst=min(SF_side(θ),SF_front(θ),SF_rear(θ))",
                  f"181 มุม × 3 ทิศ = 543 กรณี; วิกฤตที่ θ={best[1]}° {best[2]}",
                  f"SF_worst={best[0]:.3f}")
        html+="<p><b>ข้อจำกัด:</b> เป็น Preliminary rigid-body model; ต้องยืนยัน CG จริง, load transfer, tire/ground compliance, โครงสร้าง, bearing, brake และ dynamic shock ก่อนใช้งานจริง</p>"
        return html

    def make_crane(self):
        w=QWidget();self.cranePage=w;m=QHBoxLayout(w); box=QGroupBox("INPUT PARAMETERS / ข้อมูลที่ใช้คำนวณ");f=QFormLayout(box)
        self.mt=spin(300,1,5000,10,1);self.ml=spin(100,0,2000,5,1);self.mb=spin(20,0,1000,1,1)
        self.W=spin(1,.1,5,.05);self.WB=spin(1.10,.2,5,.05);self.L=spin(1.2,.1,5,.05);self.H=spin(1,.2,3,.05)
        self.xC=spin(.15,-2,2,.05);self.xCG=spin(0,-2,2,.05);self.driveXCG=spin(0,-2,2,.05)
        self.th=spin(90,-90,90,5,0);self.kd=spin(1.2,1,3,.05);self.req=spin(1.5,1,5,.1)
        rows=[("Total mass / มวลรวมทั้งระบบ (kg)",self.mt),("Payload / น้ำหนักสัตว์+ตะกร้า (kg)",self.ml),("Boom mass / น้ำหนักแขนเครน (kg)",self.mb),("Track width W / ระยะศูนย์กลางล้อซ้าย-ขวา (m)",self.W),
              ("Wheelbase WB / ระยะฐานล้อหน้า-หลัง (m)",self.WB),("Boom length L / ความยาวแขนเครน (m)",self.L),("Column height / ความสูงเสาเครน (m)",self.H),
              ("Crane x from rear axle / ตำแหน่งเครนจากเพลาหลัง (m)",self.xC),
              ("Base vehicle CG x / CG รถส่วนหลัก ไม่รวม Payload+Boom (m)",self.xCG),
              ("Driving combined CG x / CG รวมตอนวิ่ง (m)",self.driveXCG),
              ("Rotation angle θ / มุมหมุนเครน (deg)",self.th),("Dynamic factor Kdyn / ตัวคูณแรงไดนามิก",self.kd),("Required SF / ค่า SF ที่ต้องการ",self.req)]
        f.setVerticalSpacing(7);f.setHorizontalSpacing(10);f.setRowWrapPolicy(QFormLayout.WrapLongRows)
        for a,b in rows:f.addRow(a,b);b.valueChanged.connect(self.calc_all)
        self.sl=QSlider(Qt.Horizontal);self.sl.setRange(-90,90);self.sl.setValue(90);self.sl.valueChanged.connect(lambda v:self.th.setValue(v));self.th.valueChanged.connect(lambda v:self.sl.setValue(int(v)));f.addRow("Rotate crane / เลื่อนเพื่อหมุนเครน",self.sl)
        craneInputScroll=QScrollArea();craneInputScroll.setWidgetResizable(True);craneInputScroll.setFrameShape(QFrame.NoFrame)
        craneInputScroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff);craneInputScroll.setWidget(box);craneInputScroll.setMinimumWidth(300)
        m.addWidget(craneInputScroll);r=QVBoxLayout()

        viewbar=QGridLayout();viewbar.setHorizontalSpacing(6);viewbar.setVerticalSpacing(6)
        viewbar.addWidget(QLabel("3D View:"),0,0)
        bPerspective=QPushButton("Perspective");bPerspective.clicked.connect(lambda:self.view.setCamera(38,24,1.0))
        bTop=QPushButton("Top");bTop.clicked.connect(lambda:self.view.setCamera(0,72,.95))
        bSide=QPushButton("Side");bSide.clicked.connect(lambda:self.view.setCamera(90,12,1.0))
        bRear=QPushButton("Rear");bRear.clicked.connect(lambda:self.view.setCamera(180,18,1.0))
        bReset=QPushButton("Reset");bReset.clicked.connect(lambda:self.view.resetCamera())
        for col,b in enumerate((bPerspective,bTop,bSide,bRear,bReset),1):viewbar.addWidget(b,0,col)
        self.craneSweepBtn=QPushButton("Animate crane  -90° ↔ +90°");self.craneSweepBtn.setObjectName("primaryButton");self.craneSweepBtn.clicked.connect(self.toggle_crane_sweep)
        viewbar.addWidget(self.craneSweepBtn,1,0,1,6)
        r.addLayout(viewbar)

        self.view=Model3D();r.addWidget(self.view)
        cards=QHBoxLayout();self.side=QLabel();self.front=QLabel();self.rear=QLabel()
        for t,x in [("SIDE SF / ด้านข้าง",self.side),("FRONT SF / ด้านหน้า",self.front),("REAR SF / ด้านหลัง",self.rear)]:
            g=QGroupBox(t);l=QVBoxLayout(g);x.setStyleSheet("font-size:21px;font-weight:bold");l.addWidget(x);cards.addWidget(g)
        r.addLayout(cards);self.craneout=QPlainTextEdit();self.craneout.setReadOnly(True);self.craneout.setStyleSheet("font-size:12px");self.craneout.setMinimumHeight(130);r.addWidget(self.craneout)
        rightPanel=QWidget();rightPanel.setLayout(r)
        rightScroll=QScrollArea();rightScroll.setWidgetResizable(True);rightScroll.setFrameShape(QFrame.NoFrame);rightScroll.setWidget(rightPanel)
        m.addWidget(rightScroll,1)
        self.tabs.addTab(w,"1. Crane Mode / โหมดเครน")


    def toggle_crane_sweep(self):
        if not hasattr(self,"craneSweepTimer"):
            self.craneSweepTimer=QTimer(self)
            self.craneSweepTimer.setInterval(70)
            self.craneSweepTimer.timeout.connect(self._crane_sweep_tick)
            self._craneSweepDir=1
        if self.craneSweepTimer.isActive():
            self.craneSweepTimer.stop()
            if hasattr(self,"craneSweepBtn"):
                self.craneSweepBtn.setText("▶ Animate -90° ↔ +90°")
        else:
            current=float(self.th.value())
            self._craneSweepDir=-1 if current>=89 else 1
            self.craneSweepTimer.start()
            if hasattr(self,"craneSweepBtn"):
                self.craneSweepBtn.setText("■ Stop Animation")

    def _crane_sweep_tick(self):
        if not hasattr(self,"th"):
            return
        v=float(self.th.value())+self._craneSweepDir*3.0
        if v>=90:
            v=90;self._craneSweepDir=-1
        elif v<=-90:
            v=-90;self._craneSweepDir=1
        self.th.setValue(v)

    def make_slope(self):
        w=QWidget();self.slopePage=w;l=QVBoxLayout(w);g=QGroupBox("DRIVING / SLOPE INPUT / ข้อมูลการวิ่งบนทางลาด");f=QFormLayout(g)
        self.slope=spin(19,0,45,1,1);self.hcg=spin(.55,.05,3,.05);self.acc=spin(.278,0,5,.05,3)
        for a,b in [("Slope angle α / มุมทางลาด (deg)",self.slope),("Combined CG height hCG / ความสูง CG รวม (m)",self.hcg),("Acceleration a / ความเร่งรถ (m/s²)",self.acc)]:f.addRow(a,b);b.valueChanged.connect(self.calc_all)
        l.addWidget(g);self.slopeout=QPlainTextEdit();self.slopeout.setReadOnly(True);self.slopeout.setStyleSheet("font-size:13px");l.addWidget(self.slopeout);self.tabs.addTab(w,"2. Driving / Slope / ทางลาด")


    def make_fbd(self):
        w=QWidget();self.fbdPage=w; l=QVBoxLayout(w)
        top=QHBoxLayout()
        self.fbdModeCombo=QComboBox(); self.fbdModeCombo.addItems(["Side Tipping / คว่ำด้านข้าง","Front-Rear / คว่ำหน้า-หลัง","Slope / ทางลาด"])
        self.fbdAuto=QCheckBox("Auto FBD: แสดงทิศทางวิกฤตตามมุมเครนปัจจุบัน")
        self.fbdAuto.setChecked(True)
        self.fbdCriticalLabel=QLabel("Critical direction: -")
        self.fbdCriticalLabel.setStyleSheet("font-weight:700;color:#6542a5")
        top.addWidget(self.fbdModeCombo);top.addWidget(self.fbdAuto);top.addStretch(1);top.addWidget(self.fbdCriticalLabel);l.addLayout(top)
        self.forceDiagram=ForceDiagram(self); l.addWidget(self.forceDiagram)
        t=QPlainTextEdit(); t.setReadOnly(True); t.setMaximumHeight(200)
        t.setPlainText("""สมการพื้นฐาน / BASIC FORCE EQUATIONS

แรง = มวล × ความเร่ง
F = m × a

น้ำหนัก = มวล × ความเร่งโน้มถ่วง
W = m × g

แรงโหลดออกแบบ = Dynamic Factor × มวลโหลด × g
F_L = Kdyn × m_L × g

โมเมนต์ = แรง × ระยะตั้งฉากจากจุดหมุน
M = F × d

ทางลาด:
แรงตามทางลาด = mg sin(alpha)
แรงตั้งฉากทางลาด = mg cos(alpha)

Safety Factor = โมเมนต์ต้านการคว่ำ ÷ โมเมนต์ทำให้คว่ำ
SF = M_R / M_O

Auto FBD จะเลือก Side หรือ Front-Rear ตามค่า SF ต่ำสุด ณ มุมเครนปัจจุบัน
หากต้องการดู Slope FBD ให้ปิด Auto แล้วเลือก Slope เอง
""")
        l.addWidget(t)
        self.fbdModeCombo.currentIndexChanged.connect(lambda i: self.forceDiagram.setMode(i) if not self.fbdAuto.isChecked() else None)
        self.fbdAuto.toggled.connect(self.update_auto_fbd)
        self.tabs.addTab(w,"3. FBD / แผนภาพแรง")

    def update_auto_fbd(self):
        if not hasattr(self,"fbdAuto") or not hasattr(self,"forceDiagram"): return
        if not self.fbdAuto.isChecked():
            self.forceDiagram.setMode(self.fbdModeCombo.currentIndex())
            self.fbdCriticalLabel.setText("Manual FBD")
            return
        d=self.inputs();side=self.calc_side(d,theta=d["th"])[0];front,rear=self.longitudinal_sf_at(d,d["th"])
        vals=[("Side",side,0),("Front",front,1),("Rear",rear,1)]
        typ,val,mode=min(vals,key=lambda x:x[1])
        self.fbdModeCombo.blockSignals(True);self.fbdModeCombo.setCurrentIndex(mode);self.fbdModeCombo.blockSignals(False)
        self.forceDiagram.setMode(mode)
        self.fbdCriticalLabel.setText(f"Critical @ θ={d['th']:.0f}°: {typ} | SF={'∞' if val>=999 else f'{val:.3f}'}")

    def make_components(self):
        w=QWidget();self.componentsPage=w; l=QVBoxLayout(w)
        l.addWidget(QLabel("COMPONENT MASS & CG TABLE / ตารางมวลและจุดศูนย์ถ่วงรายชิ้น"))
        modebox=QGroupBox("โหมดน้ำหนัก / Mass Calculation Mode")
        ml=QVBoxLayout(modebox)
        self.massModeFixed=QRadioButton("โหมด A: กำหนดน้ำหนักรวมเอง / Fixed Total Mass")
        self.massModeSum=QRadioButton("โหมด B: ใส่น้ำหนักอุปกรณ์แต่ละชิ้น แล้วรวมอัตโนมัติ / Sum Components")
        self.massModeFixed.setChecked(True)
        ml.addWidget(self.massModeFixed);ml.addWidget(self.massModeSum)
        note=QLabel("A = ใช้ Total mass จากหน้า Crane Mode\nB = โปรแกรมรวม Mass ในตารางและส่งค่าไปใช้เป็น Total mass อัตโนมัติ")
        note.setWordWrap(True);ml.addWidget(note);l.addWidget(modebox)
        self.massModeFixed.toggled.connect(self.apply_mass_mode)
        self.massModeSum.toggled.connect(self.apply_mass_mode)
        self.comp=QTableWidget(8,5)
        self.comp.setHorizontalHeaderLabels(["Component / อุปกรณ์","Mass m (kg)","x (m)","y (m)","z (m)"])
        defaults=[
            ("Frame / โครงรถ",70,0,0,0.35),
            ("Battery / แบตเตอรี่",35,0,0,0.25),
            ("Drive motors / มอเตอร์ขับ",15,0,0,0.18),
            ("Crane column+winch / เสาเครน+วินช์",60,-0.40,0,0.75),
            ("Boom / แขนเครน",20,-0.10,0,1.28),
            ("Basket+Payload / ตะกร้า+โหลด",100,0.62,0,0.60),
            ("Counterweight / ตุ้มน้ำหนัก",0,0,0,0.20),
            ("Other / อื่นๆ",0,0,0,0.30)]
        for r,row in enumerate(defaults):
            for c,val in enumerate(row): self.comp.setItem(r,c,QTableWidgetItem(str(val)))
        self.comp.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        l.addWidget(self.comp)
        row=QHBoxLayout()
        b=QPushButton("คำนวณ CG รวม / Calculate Combined CG");b.clicked.connect(self.calc_components);row.addWidget(b)
        self.applyMassBtn=QPushButton("ใช้ค่าน้ำหนักตามโหมด / Apply Mass Mode");self.applyMassBtn.clicked.connect(self.apply_mass_mode);row.addWidget(self.applyMassBtn)
        l.addLayout(row)
        self.compout=QPlainTextEdit();self.compout.setReadOnly(True);self.compout.setMaximumHeight(190);l.addWidget(self.compout)
        self.tabs.addTab(w,"4. Component CG / ตาราง CG")

    def component_values(self):
        rows=[];sm=sx=sy=sz=0.0
        for r in range(self.comp.rowCount()):
            try:
                name=self.comp.item(r,0).text()
                m=float(self.comp.item(r,1).text());x=float(self.comp.item(r,2).text())
                y=float(self.comp.item(r,3).text());z=float(self.comp.item(r,4).text())
                if m<0: continue
                rows.append((name,m,x,y,z));sm+=m;sx+=m*x;sy+=m*y;sz+=m*z
            except: pass
        if sm<=0:return rows,0,0,0,0
        return rows,sm,sx/sm,sy/sm,sz/sm

    def apply_mass_mode(self):
        if not hasattr(self,"massModeSum"): return
        rows,sm,xg,yg,zg=self.component_values()
        if self.massModeSum.isChecked():
            if sm>0:
                self.mt.setValue(sm)
                if hasattr(self,"driveXCG"): self.driveXCG.setValue(xg)
                self.hcg.setValue(max(0,zg))
                self.compout.setPlainText(
                    f"โหมด B: รวมมวลอุปกรณ์อัตโนมัติ\n"
                    f"Σm_i = {sm:.2f} kg → ส่งไป Total mass\n"
                    f"x_CG,combined = {xg:.3f} m → ส่งไป Driving combined CG x\n"
                    f"y_CG,combined = {yg:.3f} m\n"
                    f"z_CG,combined = {zg:.3f} m → ส่งไป CG height\n\n"
                    f"หมายเหตุ: Base vehicle CG x ในโมเดลเครนไม่ถูกเขียนทับ เพราะ Payload และ Boom ถูกจำลองแยกตามมุมเครน\n\n"
                    f"สูตร: m_total = Σm_i\n"
                    f"x_CG = Σ(m_i x_i)/Σm_i\n"
                    f"y_CG = Σ(m_i y_i)/Σm_i\n"
                    f"z_CG = Σ(m_i z_i)/Σm_i")
                self.calc_all()
        else:
            self.compout.setPlainText(
                f"โหมด A: กำหนดน้ำหนักรวมเอง\n"
                f"โปรแกรมใช้ Total mass = {self.mt.value():.2f} kg จากหน้า Crane Mode\n"
                f"ตารางอุปกรณ์ใช้สำหรับตรวจสอบมวลและ CG แต่จะไม่เขียนทับ Total mass")
            self.calc_all()

    def calc_components(self):
        rows,sm,xg,yg,zg=self.component_values()
        if sm<=0:
            self.compout.setPlainText("กรุณากรอกมวลให้มากกว่า 0 kg")
            return
        mode="B: Sum Components" if self.massModeSum.isChecked() else "A: Fixed Total Mass"
        diff=sm-self.mt.value()
        self.compout.setPlainText(f"""ผลการคำนวณ Component Mass & CG

โหมดปัจจุบัน = {mode}

1) มวลรวมจากอุปกรณ์
m_sum = Σm_i = {sm:.2f} kg

2) Combined CG แกน x
x_CG,combined = Σ(m_i x_i) / Σm_i = {xg:.3f} m

3) Combined CG แกน y
y_CG,combined = Σ(m_i y_i) / Σm_i = {yg:.3f} m

4) Combined CG แกน z
z_CG,combined = Σ(m_i z_i) / Σm_i = {zg:.3f} m

Total mass ใน Crane Mode = {self.mt.value():.2f} kg
ผลต่าง Component sum - Total mass = {diff:+.2f} kg

โหมด A: ใช้ Total mass ที่ผู้ใช้กำหนดเอง
โหมด B: กด Apply แล้ว m_sum, x_CG,combined และ z_CG,combined
จะถูกส่งไปใช้เป็น Total mass, Driving combined CG x และ CG height

Base vehicle CG x ใน Crane tipping เป็นคนละตัวแปร
เพราะ Payload และ Boom ถูกจำลองตำแหน่งแยกตามมุมเครนอยู่แล้ว
""")
        if self.massModeSum.isChecked():
            self.apply_mass_mode()

    def make_worstcase(self):
        w=QWidget();self.worstPage=w
        l=QVBoxLayout(w);l.setContentsMargins(18,18,18,18);l.setSpacing(12)
        top=QHBoxLayout()
        title=QLabel("WORST CASE / กรณีวิกฤต")
        title.setStyleSheet("font-size:16px;font-weight:800;color:#17456b")
        top.addWidget(title);top.addStretch(1)
        self.worstButton=QPushButton("คำนวณใหม่ / Recalculate Worst Case")
        self.worstButton.setMinimumHeight(42)
        self.worstButton.clicked.connect(self.calc_worst)
        top.addWidget(self.worstButton)
        l.addLayout(top)
        hint=QLabel("ตรวจมุมเครน -90° ถึง +90° ทุก 1° และเปรียบเทียบ Side / Front / Rear Safety Factor")
        hint.setWordWrap(True);hint.setStyleSheet("color:#52606d;font-size:11pt")
        l.addWidget(hint)
        self.worstout=QTextEdit();self.worstout.setReadOnly(True)
        self.worstout.setStyleSheet("font-size:12px;background:white")
        l.addWidget(self.worstout,1)
        self.tabs.addTab(w,"5. Worst Case / จุดวิกฤต")

    def longitudinal_sf_at(self,d,th):
        rear=-d["WB"]/2; front=d["WB"]/2
        xc=rear+d["xC"]
        xload=xc+d["L"]*math.cos(math.radians(th))
        xboom=xc+(d["L"]/2)*math.cos(math.radians(th))
        mveh=max(0.0,d["mt"]-d["ml"]-d["mb"])

        def chk(pivot,direction):
            # Vehicle + boom use static weight. Payload uses Kdyn only when it
            # is on the overturning side; resisting payload uses static weight.
            mo=0.0;mr=0.0
            for mass,x,is_payload in (
                (mveh,d["xCG"],False),
                (d["ml"],xload,True),
                (d["mb"],xboom,False),
            ):
                signed=direction*(x-pivot)
                if signed>0:
                    factor=d["kd"] if is_payload else 1.0
                    mo+=factor*mass*G*signed
                elif signed<0:
                    mr+=mass*G*(-signed)
            return mr/mo if mo>1e-12 else 999
        return chk(front,1),chk(rear,-1)

    def calc_worst(self):
        if not hasattr(self,"worstout") or not hasattr(self,"mt"):
            return
        try:
            d=self.inputs()
            raw=self.stability_worst_scan()
            map_name={"Side":"Side / ด้านข้าง","Front":"Front / ด้านหน้า","Rear":"Rear / ด้านหลัง"}
            records=[(v,ang,map_name.get(typ,typ)) for v,ang,typ in raw]
            val,ang,typ=records[0] if records else (999,None,"-")
            status="PASS / ผ่านเกณฑ์เบื้องต้น" if val>=d["req"] else "FAIL / ต้องปรับแบบ"
            top5=sorted(records,key=lambda x:x[0])[:5]
            top_rows="".join(
                f"<tr><td>{i+1}</td><td>{th}°</td><td>{typ0}</td><td>{'∞' if v>=999 else f'{v:.3f}'}</td></tr>"
                for i,(v,th,typ0) in enumerate(top5)
            )
            val_text='∞' if val>=999 else f'{val:.3f}'
            formula_text="SF_worst = min(SF_side(θ), SF_front(θ), SF_rear(θ))"
            html=f"""
            <h2 style='color:#17456b'>WORST CASE SEARCH / ค้นหากรณีวิกฤต</h2>
            <p>รูปแบบการแสดงผล: <b>คำอธิบายภาษาไทย → สูตรภาษาไทย → สูตรตัวแปร → แทนค่า → คำตอบ</b></p>

            <div style='border:1px solid #d6e0ea;padding:14px 16px;margin:10px 0;background:#fbfdff'>
              <h3 style='color:#17456b'>1. หลักการหา Worst Case</h3>
              <p><b>คำอธิบายภาษาไทย:</b> โปรแกรมหมุนเครนจำลองทุก 1° ตั้งแต่ -90° ถึง +90° และคำนวณ Safety Factor ด้านข้าง ด้านหน้า และด้านหลัง จากนั้นเลือกค่าต่ำที่สุด</p>
              <p><b>สูตรภาษาไทย</b></p>
              <p style='margin-left:18px'><b>Safety Factor วิกฤต = ค่า Safety Factor ที่ต่ำที่สุดจากทุกมุมและทุกทิศทาง</b></p>
              <p><b>สูตรตัวแปร</b></p>
              <p style='margin-left:18px'>{formula_text}<br>θ = -90°, -89°, ..., +90°</p>
              <p><b>แทนค่า</b></p>
              <p style='margin-left:18px'>181 มุม × 3 ทิศทาง = 543 กรณี</p>
              <p style='color:#176337'><b>คำตอบ: ตรวจครบ 543 กรณี</b></p>
            </div>

            <div style='border:1px solid #d6e0ea;padding:14px 16px;margin:10px 0;background:#fbfdff'>
              <h3 style='color:#17456b'>2. ผลลัพธ์กรณีวิกฤต</h3>
              <p><b>สูตรภาษาไทย</b></p>
              <p style='margin-left:18px'><b>มุมวิกฤต = มุมที่ทำให้ Safety Factor ต่ำที่สุด</b></p>
              <p><b>แทนค่า</b></p>
              <p style='margin-left:18px'>มุมวิกฤต = {ang}°<br>ทิศทางวิกฤต = {typ}<br>Safety Factor ต่ำสุด = {val_text}<br>Safety Factor เป้าหมาย = {d['req']:.2f}</p>
              <p style='color:#176337'><b>คำตอบ: θ = {ang}° | {typ} | SF_worst = {val_text} | {status}</b></p>
            </div>

            <div style='border:1px solid #d6e0ea;padding:14px 16px;margin:10px 0;background:#fbfdff'>
              <h3 style='color:#17456b'>3. 5 กรณีที่มี Safety Factor ต่ำที่สุด</h3>
              <table cellpadding='6' cellspacing='0' border='1' style='border-collapse:collapse'>
                <tr><th>อันดับ</th><th>มุมเครน</th><th>ทิศทาง</th><th>Safety Factor</th></tr>
                {top_rows}
              </table>
            </div>
            """
            self.worstout.setHtml(html)
        except Exception as exc:
            self.worstout.setPlainText("Worst Case calculation error / เกิดข้อผิดพลาดในการคำนวณ\n"+str(exc))

    def make_calc_steps(self):
        w=QWidget();self.stepsPage=w;l=QVBoxLayout(w)
        l.addWidget(QLabel("วิธีทำการคำนวณ / STEP-BY-STEP CALCULATION"))
        self.steps=QPlainTextEdit();self.steps.setReadOnly(True);self.steps.setStyleSheet("font-size:12px");l.addWidget(self.steps)
        self.tabs.addTab(w,"6. วิธีคำนวณ / Calculation Steps")

    def update_calc_steps(self,d,sf,MO,MR,sfF,sfR):
        th=math.radians(d["th"]);g=G
        pivot=d["W"]/2
        FL=d["kd"]*d["ml"]*g
        yL=abs(d["L"]*math.sin(th));yB=abs((d["L"]/2)*math.sin(th))
        dL=max(0.0,yL-pivot);rL=max(0.0,pivot-yL)
        dB=max(0.0,yB-pivot);rB=max(0.0,pivot-yB)
        mveh=max(0.0,d["mt"]-d["ml"]-d["mb"])
        MOL=FL*dL
        MOB=d["mb"]*g*dB
        MRveh=mveh*g*pivot
        MRL=d["ml"]*g*rL
        MRB=d["mb"]*g*rB
        rear=-d["WB"]/2;front=d["WB"]/2;xc=rear+d["xC"]
        xload=xc+d["L"]*math.cos(th);xboom=xc+(d["L"]/2)*math.cos(th)
        sr=self.slope_stability_results(d)
        sf_text="∞" if sf>=999 else f"{sf:.3f}"
        sfF_text="∞" if sfF>=999 else f"{sfF:.3f}"
        sfR_text="∞" if sfR>=999 else f"{sfR:.3f}"
        slope_text="∞" if sr["sf"]>=999 else f"{sr['sf']:.3f}"

        self.steps.setPlainText(f"""A) SIDE TIPPING / การคว่ำด้านข้าง

1) แรง Payload สำหรับด้านที่ทำให้คว่ำ
F_L,design = Kdyn × m_L × g
           = {d['kd']:.2f} × {d['ml']:.2f} × 9.81
           = {FL:.2f} N

หมายเหตุ: Kdyn ใช้เพิ่มเฉพาะโมเมนต์ด้านที่เป็นผลเสีย
ถ้า Payload ยังอยู่ด้านใน Pivot จะใช้มวลจริง m_L ในโมเมนต์ต้าน
เพื่อไม่ให้ Dynamic Factor สร้างความเสถียรเพิ่มแบบไม่สมเหตุผล

2) ตำแหน่งด้านข้าง
y_L = |L sinθ| = {yL:.3f} m
y_B = |(L/2) sinθ| = {yB:.3f} m
Pivot = W/2 = {d['W']:.3f}/2 = {pivot:.3f} m

3) แขนโมเมนต์คว่ำ
d_L = max(0, y_L-Pivot) = {dL:.3f} m
d_B = max(0, y_B-Pivot) = {dB:.3f} m

4) โมเมนต์คว่ำ
M_OL = F_L,design × d_L = {FL:.2f} × {dL:.3f} = {MOL:.2f} N·m
M_OB = m_B × g × d_B = {d['mb']:.2f} × 9.81 × {dB:.3f} = {MOB:.2f} N·m
M_O = M_OL + M_OB = {MO:.2f} N·m

5) โมเมนต์ต้าน
m_vehicle = m_total - m_L - m_B
          = {d['mt']:.2f} - {d['ml']:.2f} - {d['mb']:.2f}
          = {mveh:.2f} kg

M_R,vehicle = m_vehicle × g × Pivot = {MRveh:.2f} N·m
M_R,payload = m_L × g × max(0,Pivot-y_L) = {MRL:.2f} N·m
M_R,boom    = m_B × g × max(0,Pivot-y_B) = {MRB:.2f} N·m
M_R,total   = {MR:.2f} N·m

6) Safety Factor
SF_side = M_R / M_O = {sf_text}
Target SF = {d['req']:.2f}
Result = {'PASS / ผ่านเกณฑ์เบื้องต้น' if sf>=d['req'] else 'FAIL / ต้องปรับแบบ'}

------------------------------------------------------------

B) FRONT / REAR TIPPING / การคว่ำหน้า-หลัง

x_rear  = -WB/2 = {rear:.3f} m
x_front = +WB/2 = {front:.3f} m
x_crane = x_rear + x_C = {xc:.3f} m
x_load  = x_crane + L cosθ = {xload:.3f} m
x_boom  = x_crane + (L/2)cosθ = {xboom:.3f} m

หลักการ:
- แต่ละมวลถูกจัดเป็นโมเมนต์คว่ำหรือโมเมนต์ต้านตามด้านของ Pivot
- Payload ใช้ Kdyn เฉพาะเมื่อเป็นโมเมนต์คว่ำ
- ถ้า Payload เป็นโมเมนต์ต้าน ใช้น้ำหนักจริงของ Payload

SF_front = {sfF_text}
SF_rear  = {sfR_text}

------------------------------------------------------------

C) UPHILL DRIVING STABILITY / รถวิ่งขึ้นทางลาด

ใช้ Combined driving CG เพราะในโหมดวิ่ง โหลดวางอยู่บนรถ ไม่ได้แขวนที่ปลายเครน

x_CG,drive = {sr['xcg']:.3f} m
x_rear     = {sr['rear']:.3f} m
d_rear     = x_CG,drive - x_rear = {sr['rear_arm']:.3f} m

d_slope = h_CG tanα
        = {sr['h']:.3f} × tan({self.slope.value():.1f}°)
        = {sr['shift_slope']:.3f} m

d_acc = h_CG × a/(g cosα)
      = {sr['shift_acc']:.3f} m

d_total = {sr['shift_total']:.3f} m
Margin to rear pivot = {sr['margin']:.3f} m

SF_slope = [g cosα × d_rear] / [h_CG × (g sinα + a)]
         = {slope_text}

หมายเหตุ:
ผลทั้งหมดเป็น Preliminary Engineering Calculation
ต้องยืนยันมวล/CG จริง, การถ่ายน้ำหนัก, ยาง/พื้น, โครงสร้าง และแรงกระแทกก่อนผลิตจริง
""")

    def make_design(self):
        w=QWidget();self.designPage=w;l=QVBoxLayout(w);self.designout=QPlainTextEdit();self.designout.setReadOnly(True);self.designout.setStyleSheet("font-size:13px");l.addWidget(QLabel("Automatic preliminary sizing / คำนวณขนาดเบื้องต้นจากโหลดและมุมปัจจุบัน"));l.addWidget(self.designout);self.tabs.addTab(w,"3. Width / Counterweight / ความกว้าง-ตุ้มน้ำหนัก")

    def make_graph(self):
        self.graph=GraphWidget(self)
        self.graphPage=self.graph
        self.tabs.addTab(self.graph,"4. SF vs Angle / กราฟตามมุม")

    def make_report(self):
        w=QWidget();self.reportPage=w;l=QVBoxLayout(w)
        top=QHBoxLayout()
        title=QLabel("REPORT / รายงานสรุป")
        btn=QPushButton("Export PDF / ส่งออกรายงาน PDF")
        btn.setMinimumHeight(38); btn.clicked.connect(self.export_pdf_report)
        top.addWidget(title); top.addStretch(); top.addWidget(btn); l.addLayout(top)
        self.report=QPlainTextEdit();self.report.setReadOnly(True);self.report.setStyleSheet("font-size:12px");l.addWidget(self.report)
        self.tabs.addTab(w,"Report / รายงานสรุป")


    def export_pdf_report(self):
        docs=QStandardPaths.writableLocation(QStandardPaths.DocumentsLocation) or str(Path.home())
        default_path=str(Path(docs)/"Crane_Stability_Engineering_Report.pdf")
        path,_=QFileDialog.getSaveFileName(self,"Export Stability Engineering PDF",default_path,"PDF (*.pdf)")
        if not path:return
        if not path.lower().endswith(".pdf"):path+=".pdf"
        tmpdir=Path(tempfile.mkdtemp(prefix="cvet_stability_"))
        try:
            self.calc_all();self.calc_worst()
            d=self.inputs();worst=self.stability_worst_record();slope=self.slope_stability_results(d)
            figures=[]
            for name,widget in (("vehicle",getattr(self,"view",None)),("fbd",getattr(self,"forceDiagram",None)),("stability_map",getattr(self,"graph",None))):
                if widget is not None:
                    fp=tmpdir/f"{name}.png"
                    if widget.grab().save(str(fp)):
                        figures.append((name,fp.as_uri()))
            fig_html="".join(
                f"<h3>{name.replace('_',' ').title()}</h3><p><img src='{uri}' width='650'></p>"
                for name,uri in figures
            )
            slope_sf_text="∞" if slope["sf"]>=999 else f"{slope['sf']:.3f}"
            summary=f"""
            <h1>CRANE VEHICLE STABILITY ENGINEERING REPORT</h1>
            <p>Version {APP_VERSION} | Generated {datetime.now().strftime('%Y-%m-%d %H:%M')}</p>
            <table border='1' cellspacing='0' cellpadding='6'>
            <tr><th>Input / Result</th><th>Value</th></tr>
            <tr><td>Total mass</td><td>{d['mt']:.2f} kg</td></tr>
            <tr><td>Payload</td><td>{d['ml']:.2f} kg</td></tr>
            <tr><td>Boom mass</td><td>{d['mb']:.2f} kg</td></tr>
            <tr><td>Track / Wheelbase</td><td>{d['W']:.3f} / {d['WB']:.3f} m</td></tr>
            <tr><td>Worst stability</td><td>SF {worst[0]:.3f} @ {worst[1]}° ({worst[2]})</td></tr>
            <tr><td>Uphill driving stability</td><td>{slope_sf_text}</td></tr>
            </table>
            <p><b>Scope:</b> Preliminary tipping/stability calculation. Use measured mass/CG and validate the real structure, tires, ground, brakes, slewing bearing and lifting system before fabrication/use.</p>
            """
            html=(
                "<html><body style=\"font-family:'Leelawadee UI','Tahoma','Segoe UI',Arial;font-size:10pt\">"
                +summary+"<hr>"+self.stability_formula_html()
                +"<div style='page-break-before:always'></div><h2>Figures / รูปประกอบ</h2>"+fig_html
                +"</body></html>"
            )
            doc=QTextDocument();doc.setDefaultFont(QFont(choose_ui_font_family(),10));doc.setHtml(html)
            printer=QPrinter(QPrinter.HighResolution);printer.setOutputFormat(QPrinter.PdfFormat)
            printer.setOutputFileName(path);printer.setPageSize(QPageSize(QPageSize.A4));doc.print_(printer)
            if not Path(path).exists() or Path(path).stat().st_size<1000:
                raise RuntimeError("PDF file was not created correctly")
            QMessageBox.information(self,"PDF Export","สร้างรายงาน PDF สำเร็จแล้ว:\n"+path)
        except Exception as ex:
            QMessageBox.critical(self,"PDF Export Error","สร้าง PDF ไม่สำเร็จ\n"+str(ex))
        finally:
            shutil.rmtree(tmpdir,ignore_errors=True)

    def make_thai_help(self):
        w=QWidget();self.helpPage=w;l=QVBoxLayout(w)
        txt=QPlainTextEdit();txt.setReadOnly(True);txt.setStyleSheet("font-size:13px")
        txt.setPlainText("""คู่มือภาษาไทย / คำอธิบายตัวแปร

โปรแกรมนี้เป็น Preliminary Engineering Tool สำหรับรถขนซากสัตว์พร้อมเครนรูปตัว L
เครนไม่ก้ม-เงย แขนแนวนอนคงที่ และหมุนซ้าย-ขวา -90° ถึง +90°

1) Total mass (m_total)
มวลรวมทั้งระบบขณะใช้งาน รวมรถ เครน วินช์ แบตเตอรี่ ตะกร้า และ Payload
ห้ามบวก Payload ซ้ำถ้า Total mass รวม Payload อยู่แล้ว

2) Payload (m_L)
มวลที่แขวนปลายเครน เช่น สัตว์และตะกร้า

3) Boom mass (m_B)
มวลแขนเครนส่วนแนวนอนที่โปรแกรมจำลองตำแหน่งตามมุมเครน

4) Track width (W)
ระยะศูนย์กลางล้อซ้าย-ขวา ใช้กำหนด Pivot ด้านข้างที่ W/2

5) Wheelbase (WB)
ระยะศูนย์กลางแนวล้อหน้า-หลัง ใช้กำหนด Pivot Front/Rear

6) Boom length (L)
ระยะจากแกนหมุนเครนถึง Payload

7) Crane x from rear axle
ตำแหน่งแกนเสาเครน วัดจากแนวเพลาหลัง ค่าบวกคือเข้าหาด้านหน้ารถ

8) Base vehicle CG x (x_CG,base)
CG ตามแนวยาวของ “ส่วนรถหลัก” หลังแยก Payload และ Boom ออกจากมวลรวมแล้ว
ใช้ใน Crane Front/Rear tipping เพื่อป้องกันการนับ Payload/Boom ซ้ำ

9) Driving combined CG x (x_CG,drive)
CG รวมของรถเมื่อโหลดวางอยู่บนรถ ใช้ใน Driving/Slope Mode
ถ้าใช้ Mass Mode B โปรแกรมจะส่ง Combined CG จากตารางอุปกรณ์มาที่ตัวแปรนี้

10) CG height (h_CG)
ความสูง Combined CG จากพื้น ใช้ตรวจเสถียรภาพขณะขึ้นทางลาด

11) Kdyn — Dynamic Factor
ใช้เพิ่ม Payload เฉพาะเมื่อ Payload สร้างโมเมนต์คว่ำ
ถ้า Payload อยู่ด้านต้าน โปรแกรมใช้มวลจริง ไม่ใช้ Kdyn เพิ่มโมเมนต์ต้าน

12) Overturning Moment (M_O)
ผลรวมโมเมนต์ที่พยายามทำให้รถคว่ำ

13) Resisting Moment (M_R)
ผลรวมโมเมนต์ของมวลที่อยู่ด้านต้าน Pivot
Payload/Boom ที่ยังอยู่ภายในฐานรองรับสามารถช่วยต้านการคว่ำได้

14) Safety Factor (SF)
SF = M_R / M_O
PASS หมายถึงผ่านเกณฑ์ของแบบจำลองเบื้องต้นเท่านั้น ไม่ใช่การรับรองความปลอดภัย

CRANE MODE
ใช้ตอนรถหยุดและกำลังยกโหลด ตรวจ Side / Front / Rear ตามมุมหมุนเครน
Payload ใช้ Dynamic Factor เฉพาะด้านที่เป็นผลเสียต่อการคว่ำ

DRIVING / SLOPE MODE
ใช้ตอนโหลดวางบนรถ โปรแกรมใช้ Driving combined CG x, h_CG, มุมทางลาด และความเร่ง
เพื่อตรวจโมเมนต์รอบเพลาหลังขณะเร่งขึ้นทางลาด

DRIVE TORQUE / TRACTION
แรงยึดเกาะใช้ N_drive ไม่ใช่ N_total ทั้งคัน
ค่า “สัดส่วนแรงกดที่ล้อขับ” เป็นสมมติฐานจนกว่าจะคำนวณ/วัด load transfer จริง

CONTROL LOGIC
- E-stop และ RC failsafe ทำให้คำสั่งเคลื่อนที่เป็น Safe State
- Drive และ Crane ห้ามทำพร้อมกัน
- Differential steering รองรับ Pivot Turn ด้วย Steering แม้ Throttle = 0
- Battery Low + Inhibit ล็อก Drive ตามชื่อ policy
- Limit ±90° ห้ามหมุนเข้า Limit ต่อ แต่หมุนย้อนออกได้

WIDTH / COUNTERWEIGHT
เป็น numerical preliminary sizing เท่านั้น
ตุ้มน้ำหนักจริงต้องใส่ตำแหน่ง x/y/z และตรวจโครงสร้างด้วย

ข้อควรระวัง
โปรแกรมนี้ไม่แทนมาตรฐานรับรองเครื่องจักร
ก่อนผลิตจริงต้องใช้มวล/CG จริง ตรวจโครงสร้าง จุดยึด Slewing Bearing ระบบเบรกวินช์
ยาง/พื้น การถ่ายน้ำหนัก กระแสจริง Torque-Speed curve และ Dynamic Shock
""")
        l.addWidget(txt);self.tabs.addTab(w,"6. คำอธิบายภาษาไทย")

    def calc_side(self,d,W=None,theta=None,extra=0):
        W=d["W"] if W is None else W
        th=d["th"] if theta is None else theta
        pivot=W/2
        y_load=abs(d["L"]*math.sin(math.radians(th)))
        y_boom=abs((d["L"]/2)*math.sin(math.radians(th)))
        m_vehicle=max(0.0,d["mt"]-d["ml"]-d["mb"])+max(0.0,extra)

        # Static masses inside the support polygon contribute to resistance.
        # Kdyn is applied only when Payload produces an adverse overturning
        # moment, so a dynamic factor never creates artificial extra stability.
        vehicle_MR=m_vehicle*G*pivot
        payload_over=d["kd"]*d["ml"]*G*max(0.0,y_load-pivot)
        payload_res=d["ml"]*G*max(0.0,pivot-y_load)
        boom_over=d["mb"]*G*max(0.0,y_boom-pivot)
        boom_res=d["mb"]*G*max(0.0,pivot-y_boom)

        MO=payload_over+boom_over
        MR=vehicle_MR+payload_res+boom_res
        sf=MR/MO if MO>1e-12 else 999
        return sf,MO,MR

    def calc_all(self):
        if not hasattr(self,"mt"):return
        d=self.inputs(); sf,MO,MR=self.calc_side(d)
        # longitudinal model — reuse the same function used by Worst Case and formula pages.
        rear=-d["WB"]/2; front=d["WB"]/2
        xload=(-d["WB"]/2+d["xC"])+d["L"]*math.cos(math.radians(d["th"]))
        xboom=(-d["WB"]/2+d["xC"])+(d["L"]/2)*math.cos(math.radians(d["th"]))
        sfF,sfR=self.longitudinal_sf_at(d,d["th"])
        self.side.setText("∞" if sf>=999 else f"{sf:.2f}");self.front.setText("∞" if sfF>=999 else f"{sfF:.2f}");self.rear.setText("∞" if sfR>=999 else f"{sfR:.2f}")
        self.view.setD(d)
        if hasattr(self,"stabilityVars"):self.stabilityVars.setHtml(self.stability_variables_html())
        if hasattr(self,"allStabilityVars"):self.allStabilityVars.setHtml(self.stability_variables_html())
        if hasattr(self,'forceDiagram'):
            self.update_auto_fbd()
            self.forceDiagram.update()
        if hasattr(self,'steps'): self.update_calc_steps(d,sf,MO,MR,sfF,sfR)
        self.craneout.setPlainText(f"""การคำนวณการคว่ำรถเครน / CRANE TIPPING CALCULATION

1) คำนวณแรงโหลดออกแบบ (Design Load Force)
   ความหมาย: แรงโหลด = ตัวประกอบไดนามิก × มวลโหลด × ความเร่งโน้มถ่วง\n   สูตร: F_L = Kdyn × m_L × g
   แทนค่า: F_L = {d['kd']:.2f} × {d['ml']:.1f} × 9.81
   ผลลัพธ์: F_L = {d['kd']*d['ml']*G:.2f} N
   อธิบาย: เป็นแรงจากโหลดที่รวม Dynamic Factor เพื่อเผื่อแรงกระชากแล้ว

2) หาระยะโหลดในแนวด้านข้าง (Lateral Load Position)
   ความหมาย: ระยะด้านข้าง = ความยาวแขน × sin(มุมหมุน)\n   สูตร: y_L = |L × sin(theta)|
   แทนค่า: y_L = |{d['L']:.2f} × sin({d['th']:.0f}°)|
   ผลลัพธ์: y_L = {abs(d['L']*math.sin(math.radians(d['th']))):.3f} m
   อธิบาย: เมื่อเครนหมุนออกด้านข้าง ระยะ y_L จะเพิ่มและมีผลต่อการคว่ำด้านข้าง

3) โมเมนต์ทำให้คว่ำด้านข้าง (Overturning Moment)
   ผลลัพธ์: M_O = {MO:.2f} N·m
   อธิบาย: M_O คือโมเมนต์จากโหลดและแขนเครนที่พยายามหมุนรถรอบแนวล้อด้านนอก

4) โมเมนต์ต้านการคว่ำ (Resisting Moment)
   ผลลัพธ์: M_R = {MR:.2f} N·m
   อธิบาย: M_R รวมรถส่วนหลัก และ Payload/Boom ที่ยังอยู่ด้านในแนว Pivot

5) Safety Factor ด้านข้าง
   ความหมาย: SF = โมเมนต์ต้าน ÷ โมเมนต์ทำให้คว่ำ\n   สูตร: SF_side = M_R / M_O
   ผลลัพธ์: SF_side = {'∞' if sf>=999 else f'{sf:.3f}'}
   เกณฑ์ที่กำหนด: SF >= {d['req']:.2f}
   สถานะ: {'PASS / ผ่านเกณฑ์เบื้องต้น' if sf>=d['req'] else 'FAIL / ไม่ผ่านเกณฑ์'}

6) การคว่ำหน้า-หลัง (Longitudinal Tipping)
   แนวเพลาหลัง = {rear:.3f} m
   แนวเพลาหน้า = {front:.3f} m

   ตำแหน่งโหลด:
   x_load = x_crane + L cos(theta)
          = {xload:.3f} m

   ตำแหน่ง CG ของแขน:
   x_boom = x_crane + (L/2) cos(theta)
          = {xboom:.3f} m

   SF_front = {'∞' if sfF>=999 else f'{sfF:.3f}'}
   SF_rear  = {'∞' if sfR>=999 else f'{sfR:.3f}'}

   อธิบาย:
   - SF_front ใช้ตรวจแนวโน้มคว่ำผ่านแนวล้อหน้า
   - SF_rear ใช้ตรวจแนวโน้มคว่ำผ่านแนวล้อหลัง
   - เพราะเครนติดท้ายรถ ตำแหน่งเครนและ CG ตามแนวยาวมีผลโดยตรง

7) แรงปฏิกิริยาที่แนวล้อด้านข้าง / Side Support Reactions
   สำหรับโมเดลกึ่งกลางแบบเบื้องต้น:
   R_left + R_right = น้ำหนักรวม
   ใช้สมดุลแรง: ΣF_z = 0
   ใช้สมดุลโมเมนต์: ΣM = 0

   แนวคิดสำคัญ:
   ถ้า Reaction ที่ล้อด้านใดลดลงเข้าใกล้ 0 N
   หมายถึงล้อด้านนั้นกำลังเริ่มยกจากพื้น และเข้าใกล้สภาวะคว่ำ

หมายเหตุทางวิศวกรรม:
ผลนี้เป็นการคำนวณเบื้องต้น ต้องใช้ตำแหน่ง CG และน้ำหนักจริงของชุดประกอบ
ก่อนนำไปยืนยันความปลอดภัยของรถที่ผลิตจริง
""")
        # Uphill driving stability — single source of truth.
        sr=self.slope_stability_results(d)
        sr_text="∞" if sr["sf"]>=999 else f"{sr['sf']:.3f}"
        self.slopeout.setPlainText(f"""การคำนวณขณะรถวิ่งขึ้นทางลาด / UPHILL DRIVING STABILITY
หมายเหตุ: โหมดนี้ใช้ Combined driving CG และโหลดวางอยู่บนรถ ไม่ได้แขวนที่ปลายเครน

มุมทางลาด α = {self.slope.value():.1f}°
Wheelbase WB = {d['WB']:.3f} m
Driving combined CG x = {sr['xcg']:.3f} m
CG height hCG = {sr['h']:.3f} m
ความเร่งขึ้นทางลาด a = {sr['acc']:.3f} m/s²

1) ระยะจาก Combined CG ถึงเพลาหลัง
d_rear = x_CG,drive - x_rear
       = {sr['xcg']:.3f} - ({sr['rear']:.3f})
       = {sr['rear_arm']:.3f} m

2) การเลื่อนแนวแรงจากความลาด
d_slope = hCG × tan(α)
        = {sr['shift_slope']:.3f} m

3) การเลื่อนแนวแรงจากความเร่ง
d_acc = hCG × a / (g cosα)
      = {sr['shift_acc']:.3f} m

4) ระยะเลื่อนรวมและ Margin
d_total = {sr['shift_total']:.3f} m
Margin to rear pivot = d_rear - d_total
                     = {sr['margin']:.3f} m

5) Safety Factor เชิงโมเมนต์
SF_slope = [g cosα × d_rear] / [hCG × (g sinα + a)]
         = {sr_text}

คำอธิบาย:
- Margin > 0 หมายถึงแนวแรงลัพธ์ยังอยู่ด้านในเพลาหลังในแบบจำลองนี้
- x_CG,drive และ hCG ควรมาจาก Combined CG ของรถจริง
- ผลนี้เป็น Preliminary rigid-body calculation; ไม่รวม suspension/tire compliance และ dynamic shock
""")
        # minimum width numeric search; counterweight at centered CG only helps MR in this simplified model
        target=d["req"]; minW=None
        for i in range(20,401):
            ww=i/100
            s,_,_=self.calc_side(d,W=ww)
            if s>=target:minW=ww;break
        cw=None
        for kg in range(0,501):
            s,_,_=self.calc_side(d,extra=kg)
            if s>=target:cw=kg;break
        self.designout.setPlainText(f"""WIDTH / COUNTERWEIGHT — สูตร + แทนค่า

ข้อมูลปัจจุบัน
W = {d['W']:.2f} m
theta = {d['th']:.0f} deg
Target SF = {target:.2f}

1) Minimum Track Width — Numerical Search
ความหมาย: หา W ต่ำสุดที่ทำให้ SF_side ถึงค่าเป้าหมาย
สูตรเงื่อนไข: SF_side(W) >= SF_required
แทนค่าเป้าหมาย: SF_side(W) >= {target:.2f}
วิธีค้นหา: W = 0.20 ถึง 4.00 m, เพิ่มครั้งละ 0.01 m
ผลลัพธ์: W_min ≈ {minW if minW is not None else '> 4.00'} m

2) Centered Counterweight — Simplified Numerical Search
ความหมาย: เพิ่มมวลถ่วงที่สมมติให้อยู่กึ่งกลางต่ำในโมเดล แล้วหา kg ต่ำสุดที่ผ่าน SF
สูตรเงื่อนไข: SF_side(m_cw) >= SF_required
แทนค่าเป้าหมาย: SF_side(m_cw) >= {target:.2f}
วิธีค้นหา: m_cw = 0 ถึง 500 kg, เพิ่มครั้งละ 1 kg
ผลลัพธ์: Required additional mass ≈ {cw if cw is not None else '> 500'} kg

IMPORTANT:
A fixed counterweight on one side is not modeled here because the crane slews both left and right.
For a real design, use the counterweight's actual x/y/z position and include it as a separate mass component.
""")
        self.graph.update()
        if hasattr(self,"stabilityFormula"):
            self.stabilityFormula.setHtml(self.stability_formula_html())
        worst=min(sf,sfF,sfR)
        self.report.setPlainText(f"""CRANE VEHICLE STABILITY — PRELIMINARY REPORT

INPUTS
Total mass              {d['mt']:.1f} kg
Payload                 {d['ml']:.1f} kg
Boom mass               {d['mb']:.1f} kg
Track width             {d['W']:.3f} m
Wheelbase               {d['WB']:.3f} m
Boom length             {d['L']:.3f} m
Crane x from rear axle  {d['xC']:.3f} m
Base vehicle CG x       {d['xCG']:.3f} m
Driving combined CG x    {d['driveXCG']:.3f} m
Crane angle             {d['th']:.1f} deg
Kdyn                     {d['kd']:.2f}
Target SF                {d['req']:.2f}

RESULTS
Side SF                  {'INF' if sf>=999 else f'{sf:.3f}'}
Front SF                 {'INF' if sfF>=999 else f'{sfF:.3f}'}
Rear SF                  {'INF' if sfR>=999 else f'{sfR:.3f}'}
Minimum current SF       {'INF' if worst>=999 else f'{worst:.3f}'}

Design status             {'PASS (preliminary)' if worst>=d['req'] else 'FAIL / revise geometry'}

ASSUMPTIONS
- Fixed L-shaped boom; horizontal slew -90 to +90 deg.
- Crane mounted at rear.
- Side model assumes remaining vehicle mass on centerline.
- Boom CG assumed at L/2.
- Front/rear model uses user-entered vehicle CG x.
- Dynamic factor is applied to payload.
- Structural strength, tire compliance, suspension, ground deformation and shock are not certified by this tool.
""")


class ForceDiagram(QWidget):
    """Clean engineering-style FBD, scaled to the current vehicle geometry."""
    def __init__(self,app):
        super().__init__(); self.app=app; self.mode=0; self.setMinimumHeight(380)
    def setMode(self,i): self.mode=i; self.update()
    def A(self,p,a,b,c,label,off=QPointF(7,-7)):
        p.setPen(QPen(QColor(c),3,Qt.SolidLine,Qt.RoundCap));p.drawLine(a,b)
        ang=math.atan2(b.y()-a.y(),b.x()-a.x())
        for d in (2.55,-2.55):
            p.drawLine(b,QPointF(b.x()+12*math.cos(ang+d),b.y()+12*math.sin(ang+d)))
        p.setPen(QPen(QColor(c)));p.drawText(b+off,label)
    def D(self,p,a,b,label,vertical=False):
        pen=QPen(QColor("#52606d"),1,Qt.DashLine);p.setPen(pen);p.drawLine(a,b)
        if vertical:
            p.drawLine(a+QPointF(-5,0),a+QPointF(5,0));p.drawLine(b+QPointF(-5,0),b+QPointF(5,0))
            p.drawText((a+b)/2+QPointF(7,0),label)
        else:
            p.drawLine(a+QPointF(0,-5),a+QPointF(0,5));p.drawLine(b+QPointF(0,-5),b+QPointF(0,5))
            p.drawText((a+b)/2+QPointF(-28,-8),label)
    def title(self,p,t,sub):
        p.setPen(QPen(QColor("#17324d")));font=p.font();font.setBold(True);font.setPointSize(11);p.setFont(font);p.drawText(18,28,t)
        font.setBold(False);font.setPointSize(9);p.setFont(font);p.setPen(QPen(QColor("#52606d")));p.drawText(18,50,sub)
    def paintEvent(self,e):
        p=QPainter(self);p.setRenderHint(QPainter.Antialiasing);p.fillRect(self.rect(),QColor("#ffffff"))
        if not hasattr(self.app,"mt"):return
        d=self.app.inputs();ww,hh=self.width(),self.height()
        if self.mode==0:
            self.title(p,"FREE BODY DIAGRAM — SIDE TIPPING (TOP VIEW)","เครนติดท้ายรถ • แขนหมุนตาม θ • เส้นประสีม่วงคือแนวคว่ำ")
            # Geometry, intentionally centered with margins.
            cx,cy=ww*.46,hh*.52
            carL=min(330,ww*.40);carW=min(205,hh*.38)
            left,right=cx-carL/2,cx+carL/2;top,bottom=cy-carW/2,cy+carW/2
            # chassis
            p.setPen(QPen(QColor("#334155"),2));p.setBrush(QColor("#e5e9ee"));p.drawRoundedRect(int(left),int(top),int(carL),int(carW),10,10)
            # centerlines
            p.setPen(QPen(QColor("#a8b2bf"),1,Qt.DashLine));p.drawLine(QPointF(left-25,cy),QPointF(right+25,cy));p.drawLine(QPointF(cx,top-25),QPointF(cx,bottom+25))
            # wheels
            p.setBrush(QColor("#1f2933"));p.setPen(QPen(QColor("#111827"),1))
            for x in (left+carL*.24,right-carL*.24):
                for y in (top-11,bottom+11):p.drawRoundedRect(int(x-27),int(y-8),54,16,5,5)
            # crane at rear (left)
            bx=left+carL*.18;by=cy
            p.setBrush(QColor("#f28c28"));p.setPen(QPen(QColor("#a9510c"),2));p.drawEllipse(QPointF(bx,by),15,15)
            p.setPen(QPen(QColor("#17324d")));p.drawText(bx-28,by+34,"Crane axis")
            # boom, fit to available screen but preserve angle
            theta=math.radians(d["th"]); r=min(230,ww*.30)
            ex=bx+r*math.cos(theta);ey=by-r*math.sin(theta)
            p.setPen(QPen(QColor("#f28c28"),12,Qt.SolidLine,Qt.RoundCap));p.drawLine(QPointF(bx,by),QPointF(ex,ey))
            # load marker and force
            p.setBrush(QColor("#cbd5df"));p.setPen(QPen(QColor("#475569"),2));p.drawRect(int(ex-22),int(ey-15),44,30)
            self.A(p,QPointF(ex,ey-70),QPointF(ex,ey-22),"#d62828","F_L")
            # vehicle weight at CG center
            self.A(p,QPointF(cx,cy-70),QPointF(cx,cy-15),"#2459b3","W_R")
            # two support/tipping lines
            p.setPen(QPen(QColor("#7c3aed"),2,Qt.DashLine))
            p.drawLine(QPointF(left-35,top-11),QPointF(right+35,top-11));p.drawLine(QPointF(left-35,bottom+11),QPointF(right+35,bottom+11))
            p.setPen(QPen(QColor("#7c3aed")));p.drawText(right+40,top-7,"Pivot L");p.drawText(right+40,bottom+15,"Pivot R")
            # dimensions
            self.D(p,QPointF(right+85,top-11),QPointF(right+85,bottom+11),f"W={d['W']:.2f} m",True)
            # lateral projected distance schematic
            yproj=abs(d["L"]*math.sin(theta))
            p.setPen(QPen(QColor("#17324d")));p.drawText(18,hh-55,f"θ = {d['th']:.0f}°    y_L = |L sinθ| = {yproj:.3f} m")
            p.drawText(18,hh-32,"แรงที่ทำให้คว่ำ: F_L = Kdyn × m_L × g     โมเมนต์: M_O = F × d")
        elif self.mode==1:
            self.title(p,"FREE BODY DIAGRAM — FRONT / REAR TIPPING (SIDE VIEW)","ตรวจโมเมนต์รอบแนวเพลาหน้าและเพลาหลัง")
            gy=hh*.76;rear=ww*.30;front=ww*.70;deck=gy-80
            p.setPen(QPen(QColor("#64748b"),2));p.drawLine(QPointF(55,gy),QPointF(ww-55,gy))
            p.setPen(QPen(QColor("#334155"),2));p.setBrush(QColor("#e5e9ee"));p.drawRoundedRect(int(rear-70),int(deck),int(front-rear+140),55,8,8)
            for x,n in ((rear,"Rear pivot"),(front,"Front pivot")):
                p.setBrush(QColor("#1f2933"));p.drawEllipse(QPointF(x,gy-4),24,24)
                self.A(p,QPointF(x,gy+50),QPointF(x,gy-38),"#2459b3","R")
                p.setPen(QPen(QColor("#7c3aed"),1,Qt.DashLine));p.drawLine(QPointF(x,deck-175),QPointF(x,gy+35));p.drawText(x-35,deck-182,n)
            # rear crane
            mast=rear+max(-30,min(75,d["xC"]/max(d["WB"],.1)*(front-rear)))
            top=deck-125;p.setPen(QPen(QColor("#f28c28"),11,Qt.SolidLine,Qt.RoundCap));p.drawLine(QPointF(mast,deck),QPointF(mast,top))
            proj=160*math.cos(math.radians(d["th"]));tip=mast+proj;p.drawLine(QPointF(mast,top),QPointF(tip,top))
            self.A(p,QPointF(tip,top-60),QPointF(tip,top-8),"#d62828","F_L")
            cg=(rear+front)/2+d["xCG"]/max(d["WB"],.1)*(front-rear)
            self.A(p,QPointF(cg,deck-65),QPointF(cg,deck-8),"#2459b3","W_R")
            self.D(p,QPointF(rear,gy+58),QPointF(front,gy+58),f"WB={d['WB']:.2f} m")
            p.setPen(QPen(QColor("#17324d")));p.drawText(18,hh-30,"ΣM_about pivot = 0 ที่จุดใกล้เริ่มคว่ำ  |  SF = M_R / M_O")
        else:
            self.title(p,"FREE BODY DIAGRAM — DRIVING ON SLOPE","แตกน้ำหนัก mg เป็นแรงขนานและตั้งฉากกับทางลาด")
            alpha=math.radians(self.app.slope.value());x0,y0=90,hh*.78;run=ww*.68;x1=x0+run;y1=y0-run*math.tan(alpha)
            p.setPen(QPen(QColor("#64748b"),5));p.drawLine(QPointF(x0,y0),QPointF(x1,y1))
            cx,cy=(x0+x1)/2,(y0+y1)/2-50;u=QPointF(math.cos(alpha),-math.sin(alpha));n=QPointF(-math.sin(alpha),-math.cos(alpha))
            # car
            pts=QPolygonF([QPointF(cx,cy)+u*(-100)+n*(-27),QPointF(cx,cy)+u*(100)+n*(-27),QPointF(cx,cy)+u*(100)+n*(27),QPointF(cx,cy)+u*(-100)+n*(27)])
            p.setBrush(QColor("#e5e9ee"));p.setPen(QPen(QColor("#334155"),2));p.drawPolygon(pts)
            # CG
            p.setBrush(QColor("#111827"));p.drawEllipse(QPointF(cx,cy),6,6)
            self.A(p,QPointF(cx,cy-75),QPointF(cx,cy+90),"#d62828","W=mg")
            self.A(p,QPointF(cx,cy),QPointF(cx,cy)+u*(-125),"#b42318","mg sinα")
            self.A(p,QPointF(cx,cy),QPointF(cx,cy)+n*(95),"#2459b3","mg cosα")
            self.A(p,QPointF(cx,cy)+QPointF(0,18),QPointF(cx,cy)+u*(125)+QPointF(0,18),"#16803a","F_trac")
            p.setPen(QPen(QColor("#17324d")));p.drawText(18,hh-55,f"α={self.app.slope.value():.1f}°   W_parallel=mg sinα   W_normal=mg cosα")
            p.drawText(18,hh-30,"F = m × a     W = m × g     M = F × d")
class GraphWidget(QWidget):
    """Stability map: Side / Front / Rear SF over crane angle with target and worst marker."""
    def __init__(self,app):super().__init__();self.app=app;self.setMinimumHeight(400)
    def paintEvent(self,e):
        if not hasattr(self.app,"mt"):return
        d=self.app.inputs();p=QPainter(self);p.setRenderHint(QPainter.Antialiasing);p.fillRect(self.rect(),QColor("white"))
        L,T,R,B=75,62,self.width()-35,self.height()-72
        p.setPen(QPen(QColor("#374151"),2));p.drawLine(L,B,R,B);p.drawLine(L,T,L,B)
        data=[];finite=[]
        for a in range(-90,91,2):
            side=self.app.calc_side(d,theta=a)[0];front,rear=self.app.longitudinal_sf_at(d,a)
            data.append((a,side,front,rear))
            finite.extend([v for v in (side,front,rear) if v<100])
        req=d['req'];ymax=max(2.0,req*1.6,min(8.0,(max(finite)*1.12 if finite else 5.0)))
        # grid and y labels
        p.setFont(QFont("Arial",8));p.setPen(QPen(QColor("#e2e8f0"),1))
        for i in range(6):
            val=ymax*i/5;y=B-(B-T)*i/5;p.drawLine(L,y,R,y);p.setPen(QColor("#64748b"));p.drawText(12,int(y+4),f"{val:.1f}");p.setPen(QPen(QColor("#e2e8f0"),1))
        colors=[QColor("#2563eb"),QColor("#d97706"),QColor("#7c3aed")]
        labels=["Side SF","Front SF","Rear SF"]
        for j,color in enumerate(colors,1):
            pts=[]
            for row in data:
                a=row[0];v=min(row[j],ymax);x=L+(a+90)/180*(R-L);y=B-v/ymax*(B-T);pts.append(QPointF(x,y))
            p.setPen(QPen(color,2.5))
            for a,b in zip(pts[:-1],pts[1:]):p.drawLine(a,b)
        # target line
        yr=B-min(req,ymax)/ymax*(B-T);p.setPen(QPen(QColor("#b42318"),2,Qt.DashLine));p.drawLine(L,yr,R,yr);p.drawText(R-128,yr-6,f"Target SF {req:.2f}")
        # worst point
        worst=self.app.stability_worst_record();wv=min(worst[0],ymax);wx=L+(worst[1]+90)/180*(R-L);wy=B-wv/ymax*(B-T)
        p.setBrush(QColor("#b42318"));p.setPen(QPen(QColor("#b42318"),2));p.drawEllipse(QPointF(wx,wy),5,5);p.drawText(QPointF(wx+8,wy-8),f"Worst {worst[0]:.2f} @ {worst[1]}° {worst[2]}")
        # x labels
        p.setPen(QColor("#475569"))
        for a in (-90,-60,-30,0,30,60,90):
            x=L+(a+90)/180*(R-L);p.drawText(int(x-12),B+24,f"{a}°")
        # title & legend
        p.setFont(QFont("Arial",11,QFont.Bold));p.setPen(QColor("#17324d"));p.drawText(L,28,"STABILITY MAP — Safety Factor vs Crane Angle")
        p.setFont(QFont("Arial",8,QFont.Bold));x=L
        for lab,col in zip(labels,colors):
            p.setPen(QPen(col,3));p.drawLine(x,44,x+24,44);p.setPen(col);p.drawText(x+30,48,lab);x+=125
        p.setPen(QColor("#475569"));p.drawText(L,B+49,"Crane rotation angle θ (deg)")

class MotorOperatingGraphWidget(QWidget):
    """Shows required operating point against user-entered limits; deliberately not a fabricated torque-speed curve."""
    def __init__(self,app):super().__init__();self.app=app;self.setMinimumHeight(320)
    def paintEvent(self,e):
        if not hasattr(self.app,'motorPeakTorque'):return
        q=self.app.torque_results();p=QPainter(self);p.setRenderHint(QPainter.Antialiasing);p.fillRect(self.rect(),QColor('white'))
        L,T,R,B=75,52,self.width()-35,self.height()-70
        maxrpm=max(self.app.motorMaxRPM.value()*1.15,q['rpm']*1.25,100);maxt=max(self.app.motorPeakTorque.value()*1.18,q['T']*1.3,10)
        def X(r):return L+r/maxrpm*(R-L)
        def Y(t):return B-t/maxt*(B-T)
        p.setPen(QPen(QColor('#374151'),2));p.drawLine(L,B,R,B);p.drawLine(L,T,L,B)
        # rated and peak torque, max rpm limit lines
        p.setPen(QPen(QColor('#94a3b8'),1,Qt.DashLine));p.drawLine(L,Y(self.app.motorRatedTorque.value()),R,Y(self.app.motorRatedTorque.value()))
        p.setPen(QPen(QColor('#d97706'),2,Qt.DashLine));p.drawLine(L,Y(self.app.motorPeakTorque.value()),R,Y(self.app.motorPeakTorque.value()))
        p.setPen(QPen(QColor('#7c3aed'),2,Qt.DashLine));p.drawLine(X(self.app.motorMaxRPM.value()),T,X(self.app.motorMaxRPM.value()),B)
        # required point
        p.setBrush(QColor('#2563eb'));p.setPen(QPen(QColor('#2563eb'),2));p.drawEllipse(QPointF(X(q['rpm']),Y(q['T'])),7,7)
        p.setPen(QColor('#17324d'));p.setFont(QFont('Arial',10,QFont.Bold));p.drawText(L,28,'REQUIRED OPERATING POINT vs ENTERED MOTOR LIMITS')
        p.setFont(QFont('Arial',8));p.drawText(QPointF(X(q['rpm'])+10,Y(q['T'])-8),f"Required {q['T']:.1f} N·m @ {q['rpm']:.1f} rpm")
        p.setPen(QColor('#d97706'));p.drawText(L,T+15,f"Peak torque input = {self.app.motorPeakTorque.value():.1f} N·m")
        p.setPen(QColor('#7c3aed'));p.drawText(R-165,T+15,f"Max RPM input = {self.app.motorMaxRPM.value():.0f}")
        p.setPen(QColor('#64748b'));p.drawText(L,B+28,'Speed (rpm)');p.drawText(8,T+8,'Torque')
        p.drawText(L,B+49,'NOTE: limit lines only — NOT a manufacturer torque-speed curve')

if __name__=="__main__":
    a=QApplication(sys.argv)
    a.setApplicationName(APP_NAME)
    a.setApplicationVersion(APP_VERSION)
    a.setOrganizationName("Mechatronics Engineering Project")
    a.setWindowIcon(QIcon(str(resource_path("assets/CraneEngineeringTool.ico"))))
    a.setStyle("Fusion")
    ui_font=QFont(choose_ui_font_family());ui_font.setPointSizeF(11.5)
    ui_font.setStyleStrategy(QFont.PreferAntialias)
    a.setFont(ui_font)
    w=App();w.show();sys.exit(a.exec())




