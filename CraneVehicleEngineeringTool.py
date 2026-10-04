from pathlib import Path
import sys, math, os, json, csv, tempfile, re, hashlib, subprocess, threading, urllib.request, urllib.parse, shutil, socket, time, webbrowser
from datetime import datetime
from PySide6.QtCore import Qt, QPointF, QRectF, QSize, QTimer, QStandardPaths, Signal
from PySide6.QtGui import QPainter,QPen,QBrush,QColor,QPolygonF,QPageSize,QPdfWriter,QFont,QTextDocument,QPageLayout,QFontDatabase,QIcon,QPixmap
from PySide6.QtWidgets import *
from PySide6.QtPrintSupport import QPrinter

try:
    import serial
    from serial.tools import list_ports
    SERIAL_AVAILABLE=True
except Exception:
    serial=None
    list_ports=None
    SERIAL_AVAILABLE=False



APP_NAME = "Crane Vehicle Engineering Tool"
APP_VERSION = "53.8.4"
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


class Esp32AnimatedBoardWidget(QWidget):
    """Interactive vector GPIO board view. It intentionally draws a schematic-style
    board instead of a photo so statuses can be animated and updated live."""
    def __init__(self,owner):
        super().__init__();self.o=owner;self.phase=0.0;self.hover_pin=None;self.selected_pin=None
        self.pinRects={};self.setMouseTracking(True)
        # Fixed logical canvas: never squash/stretch the ESP32 drawing with the page layout.
        self.logical_w=1080;self.logical_h=720
        self.setFixedSize(self.logical_w,self.logical_h)
        self.setSizePolicy(QSizePolicy.Fixed,QSizePolicy.Fixed)
        self.timer=QTimer(self);self.timer.timeout.connect(self._tick);self.timer.start(45)

    def sizeHint(self):
        return QSize(self.logical_w,self.logical_h)

    def _tick(self):
        self.phase=(self.phase+0.12)%(math.pi*2);self.update()

    def set_animation_enabled(self,on):
        if on and not self.timer.isActive():self.timer.start(45)
        elif not on and self.timer.isActive():self.timer.stop()
        self.update()

    def mouseMoveEvent(self,e):
        pos=e.position();pin=None
        for k,r in self.pinRects.items():
            if r.contains(pos):pin=k;break
        if pin!=self.hover_pin:
            self.hover_pin=pin;self.update()
        super().mouseMoveEvent(e)

    def leaveEvent(self,e):
        self.hover_pin=None;self.update();super().leaveEvent(e)

    def mousePressEvent(self,e):
        pos=e.position()
        for pin,r in self.pinRects.items():
            if r.contains(pos):
                self.selected_pin=pin
                if hasattr(self.o,"on_board_pin_clicked"):self.o.on_board_pin_clicked(pin)
                self.update();break
        super().mousePressEvent(e)

    @staticmethod
    def _status_color(status):
        return {
            "USED":"#22c55e","FREE":"#2f80ed","BOARD":"#f59e0b","CAUTION":"#fb923c",
            "CONFLICT":"#ef4444","INVALID":"#7f1d1d","MEMORY":"#a855f7","SHARED":"#06b6d4",
        }.get(status,"#64748b")

    def paintEvent(self,e):
        p=QPainter(self);p.setRenderHint(QPainter.Antialiasing)
        p.fillRect(self.rect(),QColor("#07182b"))
        W,H=self.width(),self.height()
        data=self.o.gpio_profile_data() if hasattr(self.o,"gpio_profile_data") else {"pins":[],"name":"ESP32","layout":"portrait"}
        snapshot=self.o.hardware_pin_snapshot() if hasattr(self.o,"hardware_pin_snapshot") else {}
        pins=data.get("pins",[])
        landscape=data.get("layout")=="landscape"

        # Header
        p.setPen(QColor("#eaf6ff"));p.setFont(QFont(choose_ui_font_family(),14,QFont.Bold))
        p.drawText(QRectF(18,10,W-36,30),Qt.AlignLeft|Qt.AlignVCenter,data.get("name","ESP32 GPIO MAP"))
        p.setFont(QFont(choose_ui_font_family(),9))
        p.setPen(QColor("#8db6d8"))
        p.drawText(QRectF(18,39,W-36,22),Qt.AlignLeft|Qt.AlignVCenter,
                   f"Physical GPIO: {len(pins)}  •  click a pin for details  •  pulsing = project used")

        top=76;bottom=72
        if landscape:
            board=QRectF(W*0.27,top+30,W*0.46,H-top-bottom-45)
        else:
            bw=min(W*0.34,330);board=QRectF(W/2-bw/2,top+12,bw,H-top-bottom-18)

        # Board body / screen / MCU
        p.setPen(QPen(QColor("#2f80ed"),2));p.setBrush(QColor("#102d46"));p.drawRoundedRect(board,22,22)
        if landscape:
            screen=QRectF(board.left()+board.width()*0.24,board.top()+28,board.width()*0.57,board.height()*0.53)
            p.setPen(QPen(QColor("#5ba8ff"),2));p.setBrush(QColor("#07111d"));p.drawRoundedRect(screen,10,10)
            p.setPen(QColor("#2b8cff"));p.setFont(QFont("Arial",18,QFont.Bold));p.drawText(screen,Qt.AlignCenter,"7-inch LCD\n1024 × 600")
            chip=QRectF(board.left()+board.width()*0.06,board.bottom()-board.height()*0.31,board.width()*0.23,board.height()*0.20)
        else:
            chip=QRectF(board.left()+board.width()*0.19,board.top()+board.height()*0.18,board.width()*0.62,board.height()*0.32)

        p.setPen(QPen(QColor("#9aa8b6"),1));p.setBrush(QColor("#dfe7ef"));p.drawRoundedRect(chip,8,8)
        p.setPen(QColor("#24384a"));p.setFont(QFont("Arial",11,QFont.Bold))
        p.drawText(chip,Qt.AlignCenter,data.get("module","ESP32-S3\nWROOM"))

        # USB and buttons for board feeling
        usb=QRectF(board.center().x()-35,board.bottom()-24,70,28)
        p.setPen(QPen(QColor("#93a4b5"),1));p.setBrush(QColor("#c8d2dc"));p.drawRoundedRect(usb,5,5)
        p.setPen(QColor("#26394a"));p.setFont(QFont("Arial",7,QFont.Bold));p.drawText(usb,Qt.AlignCenter,"USB-C")
        for x,label in ((board.left()+35,"BOOT"),(board.right()-65,"RESET")):
            rr=QRectF(x,board.bottom()-58,42,22);p.setBrush(QColor("#273b4c"));p.setPen(QColor("#7d91a3"));p.drawRoundedRect(rr,5,5)
            p.setPen(QColor("#dce8f2"));p.setFont(QFont("Arial",6,QFont.Bold));p.drawText(rr,Qt.AlignCenter,label)

        # Split physical GPIOs into left/right columns.
        half=(len(pins)+1)//2;leftPins=pins[:half];rightPins=pins[half:]
        maxRows=max(len(leftPins),len(rightPins),1)
        y0=top+5;avail=H-bottom-y0;rowH=max(19,min(28,avail/maxRows))
        labelW=min(220,max(130,W*0.20))
        self.pinRects={}
        for side,arr in ((0,leftPins),(1,rightPins)):
            for i,pin in enumerate(arr):
                y=y0+i*rowH
                info=snapshot.get(pin,{"status":data.get("pin_info",{}).get(pin,{}).get("status","FREE"),
                                       "function":data.get("pin_info",{}).get(pin,{}).get("function","Available"),
                                       "users":[]})
                status=info.get("status","FREE");color=QColor(self._status_color(status))
                if side==0:
                    rr=QRectF(12,y,labelW,rowH-3);node=QPointF(board.left()-7,y+rowH/2-1)
                    lineStart=QPointF(rr.right(),rr.center().y())
                else:
                    rr=QRectF(W-12-labelW,y,labelW,rowH-3);node=QPointF(board.right()+7,y+rowH/2-1)
                    lineStart=QPointF(rr.left(),rr.center().y())
                self.pinRects[pin]=rr

                # line from label toward board
                p.setPen(QPen(color,1.5));p.drawLine(lineStart,node)
                p.setBrush(color);p.setPen(Qt.NoPen);p.drawEllipse(node,4.2,4.2)

                # pulse project-used/conflict pins
                if status in ("USED","CONFLICT"):
                    pulse=7+3*(0.5+0.5*math.sin(self.phase+i*0.25))
                    pc=QColor(color);pc.setAlpha(70)
                    p.setBrush(pc);p.drawEllipse(node,pulse,pulse)

                bg=QColor(color);bg.setAlpha(55 if pin not in (self.hover_pin,self.selected_pin) else 95)
                p.setBrush(bg);p.setPen(QPen(color,1.2));p.drawRoundedRect(rr,7,7)
                p.setPen(QColor("#f3f8fc"));p.setFont(QFont("Arial",8,QFont.Bold))
                pinText=f"GPIO{pin}"
                p.drawText(QRectF(rr.left()+6,rr.top(),52,rr.height()),Qt.AlignLeft|Qt.AlignVCenter,pinText)
                func=str(info.get("function",""))[:28]
                p.setFont(QFont(choose_ui_font_family(),7))
                p.setPen(QColor("#d9e8f5"))
                p.drawText(QRectF(rr.left()+58,rr.top(),rr.width()-64,rr.height()),Qt.AlignLeft|Qt.AlignVCenter,func)

        # Legend
        legendY=H-52;x=18
        for label,status in (("USED","USED"),("FREE","FREE"),("ONBOARD","BOARD"),("SHARED","SHARED"),("CAUTION","CAUTION"),("CONFLICT","CONFLICT")):
            c=QColor(self._status_color(status));p.setBrush(c);p.setPen(Qt.NoPen);p.drawEllipse(QPointF(x+5,legendY+8),5,5)
            p.setPen(QColor("#cfe2f2"));p.setFont(QFont("Arial",7,QFont.Bold));p.drawText(x+14,legendY+13,label);x+=78



class SystemFlowchartWidget(QWidget):
    """Animated flowchart that follows the user's Final vehicle + crane document."""
    def __init__(self,owner):
        super().__init__();self.o=owner
        self.logical_w=1100;self.logical_h=2160;self.zoom=0.90
        self.phase=0.0;self.path=[];self.step_index=0;self.nodeRects={}
        self.anim=QTimer(self);self.anim.timeout.connect(self._tick);self.anim.start(70)
        self.set_zoom(self.zoom)

    def set_zoom(self,value):
        # Keep exact canvas dimensions so X/Y cannot be stretched independently.
        self.zoom=max(0.65,min(1.35,float(value)))
        w=max(1,int(round(self.logical_w*self.zoom)))
        h=max(1,int(round(self.logical_h*self.zoom)))
        self.setFixedSize(w,h)
        self.update()

    def _tick(self):
        self.phase=(self.phase+0.16)%(math.pi*2);self.update()

    def set_path(self,path,step_index=None):
        self.path=list(path or [])
        if step_index is not None:self.step_index=max(0,min(int(step_index),max(0,len(self.path)-1)))
        elif self.path:self.step_index=min(self.step_index,len(self.path)-1)
        else:self.step_index=0
        self.update()

    def active_nodes(self):
        if not self.path:return set()
        return set(self.path[:self.step_index+1])

    def current_node(self):
        if not self.path:return None
        return self.path[min(self.step_index,len(self.path)-1)]

    @staticmethod
    def _style(kind):
        styles={
            "start":("#e7f6df","#5a9b47"),
            "process":("#dfefff","#5b91ba"),
            "decision":("#ffe4e5","#c96d75"),
            "fault":("#ffdfe0","#c9535c"),
            "warning":("#fff0bd","#c49a29"),
            "ok":("#dff4df","#5c9f61"),
            "action":("#dcf3dc","#5c9f61"),
            "stop":("#ffdfe0","#c9535c"),
            "connector":("#eee9fb","#7766ad"),
        }
        return styles.get(kind,styles["process"])

    def _arrow_head(self,p,a,b,color,width=2.1):
        p.setPen(QPen(QColor(color),width,Qt.SolidLine,Qt.RoundCap,Qt.RoundJoin))
        p.drawLine(a,b)
        ang=math.atan2(b.y()-a.y(),b.x()-a.x());sz=9
        p1=QPointF(b.x()-sz*math.cos(ang-0.55),b.y()-sz*math.sin(ang-0.55))
        p2=QPointF(b.x()-sz*math.cos(ang+0.55),b.y()-sz*math.sin(ang+0.55))
        p.setBrush(QColor(color));p.setPen(Qt.NoPen);p.drawPolygon(QPolygonF([b,p1,p2]))

    def _poly_arrow(self,p,pts,color="#71879a",width=2.1):
        if len(pts)<2:return
        p.setPen(QPen(QColor(color),width,Qt.SolidLine,Qt.RoundCap,Qt.RoundJoin))
        for a,b in zip(pts[:-2],pts[1:-1]):p.drawLine(a,b)
        self._arrow_head(p,pts[-2],pts[-1],color,width)

    def _node(self,p,key,rect,text,shape="rect",kind="process"):
        active=key in self.active_nodes();current=(key==self.current_node())
        fill,border=self._style(kind)
        if active:border="#1d8d5a"
        if current:
            pulse=int(45+38*(0.5+0.5*math.sin(self.phase)))
            glow=QColor("#2eb875");glow.setAlpha(pulse)
            p.setPen(QPen(glow,9));p.setBrush(Qt.NoBrush)
            if shape=="diamond":
                c=rect.center();poly=QPolygonF([QPointF(c.x(),rect.top()),QPointF(rect.right(),c.y()),QPointF(c.x(),rect.bottom()),QPointF(rect.left(),c.y())]);p.drawPolygon(poly)
            elif shape=="round":p.drawRoundedRect(rect,rect.height()/2,rect.height()/2)
            else:p.drawRoundedRect(rect,10,10)
        p.setPen(QPen(QColor(border),2.2));p.setBrush(QColor(fill))
        if shape=="diamond":
            c=rect.center();poly=QPolygonF([QPointF(c.x(),rect.top()),QPointF(rect.right(),c.y()),QPointF(c.x(),rect.bottom()),QPointF(rect.left(),c.y())]);p.drawPolygon(poly)
        elif shape=="round":p.drawRoundedRect(rect,rect.height()/2,rect.height()/2)
        else:p.drawRoundedRect(rect,10,10)
        p.setPen(QColor("#17324d"));p.setFont(QFont(choose_ui_font_family(),8.8,QFont.Bold))
        pad=max(3.0,7.0*self.zoom)
        p.drawText(rect.adjusted(pad,pad*0.55,-pad,-pad*0.55),Qt.AlignCenter|Qt.TextWordWrap,text)
        self.nodeRects[key]=rect

    def paintEvent(self,e):
        p=QPainter(self);p.setRenderHint(QPainter.Antialiasing);p.fillRect(self.rect(),QColor("#fbfdff"))
        # Uniform geometry scale prevents stretched boxes and strange connector lines.
        scale=min(self.width()/self.logical_w,self.height()/self.logical_h)
        ox=(self.width()-self.logical_w*scale)/2.0
        oy=0.0
        # Original diagram coordinates occupy 0..1000. Add 50 px logical side margins.
        def R(x,y,w,h):return QRectF(ox+(x+50)*scale,oy+y*scale,w*scale,h*scale)
        self.nodeRects={}

        p.setPen(QColor("#17456b"));p.setFont(QFont(choose_ui_font_family(),15,QFont.Bold))
        p.drawText(R(40,10,920,38),Qt.AlignCenter,"Flowchart Final")
        p.setFont(QFont(choose_ui_font_family(),9,QFont.Bold));p.setPen(QColor("#456b8c"))
        p.drawText(R(40,46,920,24),Qt.AlignCenter,"Vehicle and Crane Control Flowchart")
        p.setFont(QFont(choose_ui_font_family(),8));p.setPen(QColor("#71879a"))
        p.drawText(R(40,70,920,22),Qt.AlignCenter,"ESP32 control logic • i-BUS remote • IMU • VESC • Crane ±90°")

        nodes={
            "start":(390,105,220,52,"Start\n(Power ON)","round","start"),
            "init":(340,182,320,60,"Start System\n(ESP32, remote, sensors, motors)","rect","process"),
            "remote":(340,267,320,62,"Read Remote Signal\n(FlySky FS-i6X via i-BUS)","rect","process"),
            "remoteq":(370,355,260,86,"Remote OK?","diamond","decision"),
            "remotefault":(700,360,250,76,"Stop Vehicle\nStop Crane Rotation\nTurn Alarm ON","rect","fault"),
            "tiltread":(340,474,320,58,"Read Tilt (IMU)","rect","process"),
            "limitsread":(340,555,320,58,"Read Crane Limits (Left / Right)","rect","process"),
            "motorread":(340,636,320,58,"Read Motor Status (VESC)","rect","process"),
            "motorq":(370,721,260,86,"Motor System OK?","diamond","decision"),
            "motorfault":(700,726,250,76,"Stop Vehicle\nStop Crane Rotation\nTurn Alarm ON","rect","fault"),
            "tiltq":(370,842,260,86,"Vehicle Tilt Too High?","diamond","decision"),
            "warningon":(65,852,245,66,"Warning ON\n(Buzzer + LED)","rect","warning"),
            "warningoff":(690,852,245,66,"Warning OFF","rect","ok"),
            "drivecmd":(340,965,320,58,"Read Driving Command\n(Forward / Reverse / Left / Right)","rect","process"),
            "mix":(340,1046,320,64,"Calculate Left / Right Motor Speed","rect","process"),
            "speedlimit":(340,1133,320,64,"Limit Speed to 1 km/h\n+ Soft Start / Stop","rect","process"),
            "driveq":(370,1225,260,86,"Drive Command Active?","diamond","decision"),
            "stopcrane_drive":(80,1345,260,58,"Stop Crane Rotation","rect","stop"),
            "senddrive":(80,1426,260,62,"Send Drive Command\nto VESC","rect","process"),
            "stopdrive":(660,1345,260,62,"Send Stop Command\nto VESC","rect","process"),
            "movingq":(660,1435,260,86,"Vehicle Still Moving?","diamond","decision"),
            "keepmoving":(800,1548,140,62,"Keep Crane\nStopped","rect","stop"),
            "stopped05":(530,1542,260,86,"Stopped for\nat least 0.5 s?","diamond","decision"),
            "keepwait":(800,1652,140,62,"Keep Crane\nStopped","rect","stop"),
            "controlcrane":(320,1652,300,62,"Control Crane\n(Read crane command from remote)","rect","process"),
            "cranedir":(390,1750,250,86,"Crane Direction?","diamond","decision"),
            "leftlimitq":(80,1858,240,80,"Left Limit Reached?","diamond","decision"),
            "rightlimitq":(680,1858,240,80,"Right Limit Reached?","diamond","decision"),
            "cranestop":(390,1870,220,58,"Stop Crane","rect","stop"),
            "stopleft":(55,1970,160,55,"Stop Crane","rect","stop"),
            "turnleft":(235,1970,160,55,"Turn Left","rect","action"),
            "turnright":(605,1970,160,55,"Turn Right","rect","action"),
            "stopright":(785,1970,160,55,"Stop Crane","rect","stop"),
            "Ain":(270,274,48,42,"A","round","connector"),
            "A_remote":(952,378,42,42,"A","round","connector"),
            "A_motor":(952,744,42,42,"A","round","connector"),
            "A_drive":(185,1512,50,42,"A","round","connector"),
            "A_move":(952,1560,42,42,"A","round","connector"),
            "A_wait":(952,1674,42,42,"A","round","connector"),
            "A_bottom":(445,2070,110,46,"A","round","connector"),
        }

        def C(key,side="bottom"):
            x,y,w,h,_,_,_=nodes[key];r=R(x,y,w,h)
            return {"top":QPointF(r.center().x(),r.top()),"bottom":QPointF(r.center().x(),r.bottom()),
                    "left":QPointF(r.left(),r.center().y()),"right":QPointF(r.right(),r.center().y())}[side]
        def label(x,y,w,h,text,color):
            p.setPen(QColor(color));p.setFont(QFont(choose_ui_font_family(),7.8,QFont.Bold))
            p.drawText(R(x,y,w,h),Qt.AlignCenter,text)

        col="#7890a4";green="#388b52";red="#b8464d";blue="#477fa7"

        for a,b in (("start","init"),("init","remote"),("remote","remoteq")):self._poly_arrow(p,[C(a),C(b,"top")],col)
        self._poly_arrow(p,[C("remoteq"),C("tiltread","top")],green);label(510,443,55,22,"YES",green)
        self._poly_arrow(p,[C("remoteq","right"),QPointF(R(675,0,0,0).x(),C("remoteq","right").y()),C("remotefault","left")],red);label(645,365,48,22,"NO",red)

        for a,b in (("tiltread","limitsread"),("limitsread","motorread"),("motorread","motorq")):self._poly_arrow(p,[C(a),C(b,"top")],col)
        self._poly_arrow(p,[C("motorq"),C("tiltq","top")],green);label(510,810,55,22,"YES",green)
        self._poly_arrow(p,[C("motorq","right"),QPointF(R(675,0,0,0).x(),C("motorq","right").y()),C("motorfault","left")],red);label(645,731,48,22,"NO",red)

        self._poly_arrow(p,[C("tiltq","left"),QPointF(C("warningon","right").x()+18,C("tiltq","left").y()),C("warningon","right")],green);label(310,852,55,22,"YES",green)
        self._poly_arrow(p,[C("tiltq","right"),QPointF(C("warningoff","left").x()-18,C("tiltq","right").y()),C("warningoff","left")],blue);label(635,852,55,22,"NO",blue)
        merge=QPointF(R(500,0,0,0).x(),R(944,0,0,0).y())
        for key in ("warningon","warningoff"):
            a=C(key);self._poly_arrow(p,[a,QPointF(a.x(),merge.y()),merge],col)
        self._poly_arrow(p,[merge,C("drivecmd","top")],col)

        for a,b in (("drivecmd","mix"),("mix","speedlimit"),("speedlimit","driveq")):self._poly_arrow(p,[C(a),C(b,"top")],col)
        self._poly_arrow(p,[C("driveq","left"),QPointF(R(210,0,0,0).x(),C("driveq","left").y()),C("stopcrane_drive","top")],green);label(275,1237,55,22,"YES",green)
        self._poly_arrow(p,[C("stopcrane_drive"),C("senddrive","top")],col)
        self._poly_arrow(p,[C("driveq","right"),QPointF(R(790,0,0,0).x(),C("driveq","right").y()),C("stopdrive","top")],blue);label(660,1237,45,22,"NO",blue)
        self._poly_arrow(p,[C("stopdrive"),C("movingq","top")],col)

        self._poly_arrow(p,[C("movingq","right"),QPointF(R(930,0,0,0).x(),C("movingq","right").y()),C("keepmoving","top")],red);label(915,1460,55,22,"YES",red)
        self._poly_arrow(p,[C("movingq"),C("stopped05","top")],blue);label(705,1518,45,22,"NO",blue)
        self._poly_arrow(p,[C("stopped05","left"),QPointF(R(515,0,0,0).x(),C("stopped05","left").y()),C("controlcrane","top")],green);label(460,1560,55,22,"YES",green)
        self._poly_arrow(p,[C("stopped05","right"),QPointF(R(900,0,0,0).x(),C("stopped05","right").y()),C("keepwait","top")],red);label(790,1560,45,22,"NO",red)
        self._poly_arrow(p,[C("controlcrane"),C("cranedir","top")],col)

        self._poly_arrow(p,[C("cranedir","left"),QPointF(R(200,0,0,0).x(),C("cranedir","left").y()),C("leftlimitq","top")],blue);label(250,1765,60,22,"LEFT",blue)
        self._poly_arrow(p,[C("cranedir"),C("cranestop","top")],col);label(482,1840,55,22,"STOP","#60758b")
        self._poly_arrow(p,[C("cranedir","right"),QPointF(R(800,0,0,0).x(),C("cranedir","right").y()),C("rightlimitq","top")],blue);label(690,1765,65,22,"RIGHT",blue)

        self._poly_arrow(p,[C("leftlimitq","left"),QPointF(R(135,0,0,0).x(),C("leftlimitq","left").y()),C("stopleft","top")],red);label(50,1900,55,22,"YES",red)
        self._poly_arrow(p,[C("leftlimitq","right"),QPointF(R(315,0,0,0).x(),C("leftlimitq","right").y()),C("turnleft","top")],green);label(330,1900,45,22,"NO",green)
        self._poly_arrow(p,[C("rightlimitq","left"),QPointF(R(685,0,0,0).x(),C("rightlimitq","left").y()),C("turnright","top")],green);label(620,1900,45,22,"NO",green)
        self._poly_arrow(p,[C("rightlimitq","right"),QPointF(R(865,0,0,0).x(),C("rightlimitq","right").y()),C("stopright","top")],red);label(900,1900,55,22,"YES",red)

        # Connector A is shown as local jump connectors (same style as the submitted Final).
        # This keeps return lines from crossing the main flowchart.
        self._poly_arrow(p,[C("Ain","right"),C("remote","left")],"#526f8a",2.0)
        self._poly_arrow(p,[C("remotefault","right"),C("A_remote","left")],col)
        self._poly_arrow(p,[C("motorfault","right"),C("A_motor","left")],col)
        self._poly_arrow(p,[C("senddrive"),C("A_drive","top")],col)
        self._poly_arrow(p,[C("keepmoving","right"),C("A_move","left")],col)
        self._poly_arrow(p,[C("keepwait","right"),C("A_wait","left")],col)

        # Crane terminal actions merge neatly into the bottom A connector.
        target=C("A_bottom","top");returnY=R(2045,0,0,0).y()
        for key in ("cranestop","stopleft","turnleft","turnright","stopright"):
            a=C(key);self._poly_arrow(p,[a,QPointF(a.x(),returnY),QPointF(target.x(),returnY),target],col)

        for key,(x,y,w,h,text,shape,kind) in nodes.items():self._node(p,key,R(x,y,w,h),text,shape,kind)

        p.setPen(QColor("#60758b"));p.setFont(QFont(choose_ui_font_family(),7.8))
        p.drawText(R(230,2120,540,24),Qt.AlignCenter,"Connector A = กลับไปอ่าน Remote Signal ใหม่ในรอบถัดไป")

class TelemetryChartWidget(QWidget):
    """Three compact live plots for Current, Speed and Tilt."""
    def __init__(self,owner):
        super().__init__();self.o=owner;self.setMinimumHeight(330)

    def _plot_lane(self,p,rect,key,title,unit):
        hist=getattr(self.o,"telemetryHistory",[])
        vals=[float(x.get(key,0.0) or 0.0) for x in hist[-180:]]
        p.setPen(QPen(QColor("#d8e3ed"),1));p.setBrush(QColor("#fbfdff"));p.drawRoundedRect(rect,8,8)
        p.setPen(QColor("#17324d"));p.setFont(QFont(choose_ui_font_family(),9,QFont.Bold))
        p.drawText(QRectF(rect.left()+10,rect.top()+4,rect.width()-20,20),Qt.AlignLeft|Qt.AlignVCenter,title)
        if not vals:
            p.setPen(QColor("#8a9bad"));p.setFont(QFont(choose_ui_font_family(),8))
            p.drawText(rect,Qt.AlignCenter,"No telemetry samples yet");return
        lo=min(vals);hi=max(vals)
        if abs(hi-lo)<1e-9:
            pad=max(1.0,abs(hi)*0.1);lo-=pad;hi+=pad
        else:
            pad=(hi-lo)*0.12;lo-=pad;hi+=pad
        plot=QRectF(rect.left()+52,rect.top()+28,rect.width()-64,rect.height()-43)
        p.setPen(QPen(QColor("#e4ebf2"),1))
        for j in range(3):
            y=plot.top()+plot.height()*j/2;p.drawLine(QPointF(plot.left(),y),QPointF(plot.right(),y))
        pts=[]
        for i,v in enumerate(vals):
            x=plot.left()+(plot.width()*(i/max(1,len(vals)-1)))
            y=plot.bottom()-(v-lo)/(hi-lo)*plot.height()
            pts.append(QPointF(x,y))
        p.setPen(QPen(QColor("#2672d8"),2.2))
        for a,b in zip(pts[:-1],pts[1:]):p.drawLine(a,b)
        latest=vals[-1]
        p.setPen(QColor("#334e68"));p.setFont(QFont("Arial",7))
        p.drawText(QRectF(rect.left()+4,plot.top()-2,45,15),Qt.AlignRight|Qt.AlignVCenter,f"{hi:.1f}")
        p.drawText(QRectF(rect.left()+4,plot.bottom()-12,45,15),Qt.AlignRight|Qt.AlignVCenter,f"{lo:.1f}")
        p.setPen(QColor("#0f6a5f"));p.setFont(QFont(choose_ui_font_family(),9,QFont.Bold))
        p.drawText(QRectF(rect.right()-155,rect.top()+4,145,20),Qt.AlignRight|Qt.AlignVCenter,f"{latest:.2f} {unit}")

    def paintEvent(self,e):
        p=QPainter(self);p.setRenderHint(QPainter.Antialiasing);p.fillRect(self.rect(),QColor("#ffffff"))
        margin=8;gap=9;lane=(self.height()-margin*2-gap*2)/3
        specs=[("battery_a","Battery / VESC Current","A"),("speed_kmh","Vehicle Speed","km/h"),("tilt_deg","IMU Tilt","°")]
        for i,(key,title,unit) in enumerate(specs):
            rect=QRectF(margin,margin+i*(lane+gap),self.width()-2*margin,lane)
            self._plot_lane(p,rect,key,title,unit)


class App(QMainWindow):
    updateTaskFinished=Signal(object)
    updateProgressChanged=Signal(int)
    telemetryNetworkPacket=Signal(object)
    def __init__(self):
        super().__init__();self.setStyleSheet(APP_STYLE);self.setWindowTitle(f"{APP_NAME} — V{APP_VERSION}"); self.setWindowIcon(QIcon(str(resource_path("assets/CraneEngineeringTool.ico"))));self.setMinimumSize(1024,650);self.resize(1440,860)
        app_font=QFont(choose_ui_font_family());app_font.setPointSizeF(11.5);app_font.setStyleStrategy(QFont.PreferAntialias);self.setFont(app_font)
        self.tabs=QTabWidget()
        self.tabs.tabBar().hide();self.setCentralWidget(self.tabs)
        self.make_home();self.make_torque();self.make_electrical();self.make_winch();self.make_crane();self.make_slope();self.make_fbd();self.make_components();self.make_worstcase();self.make_calc_steps();self.make_design();self.make_graph();self.make_report();self.make_thai_help();self.make_stability_hub();self.make_project_tools();self.make_safety_logic_simulator();self.make_variable_dictionary_page();self.make_hardware_io_manager();self.make_telemetry_page();self.make_integration_suite();self.setup_navigation_dock();self.setup_status_bar_ui();self.setup_dynamic_tabs()
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
            ("ขีดจำกัดแรงยึดเกาะ", "แรงกดล้อขับ = สัดส่วนแรงกดล้อขับ × มวลรวมรถ × g × cos(มุมทางลาด)<br>แรงยึดเกาะสูงสุด = สัมประสิทธิ์แรงเสียดทาน × แรงกดล้อขับ"),
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
        b.setToolTip(text)
        b.setMinimumHeight(40)
        self.navButtons[key]=b
        return b

    def _set_active_nav(self,key):
        if not hasattr(self,"navButtons"):return
        for k,b in self.navButtons.items():
            active=(k==key)
            b.setProperty("active",active)
            b.style().unpolish(b);b.style().polish(b);b.update()


    # =====================================================================
    # V52.5 FINAL SYSTEM FLOWCHART
    # =====================================================================
    def flowchart_scenario_path(self,name=None):
        name=(name or (self.flowScenario.currentText() if hasattr(self,"flowScenario") else "Drive Forward"))
        normal=["start","init","remote","remoteq","tiltread","limitsread","motorread","motorq","tiltq","warningoff","drivecmd","mix","speedlimit"]
        paths={
            "Drive Forward":normal+["driveq","stopcrane_drive","senddrive","A_drive","Ain","remote"],
            "Idle / Ready":normal+["driveq","stopdrive","movingq","stopped05","controlcrane","cranedir","cranestop","A_bottom","Ain","remote"],
            "Crane LEFT":normal+["driveq","stopdrive","movingq","stopped05","controlcrane","cranedir","leftlimitq","turnleft","A_bottom","Ain","remote"],
            "Crane RIGHT":normal+["driveq","stopdrive","movingq","stopped05","controlcrane","cranedir","rightlimitq","turnright","A_bottom","Ain","remote"],
            "Remote Fault":["start","init","remote","remoteq","remotefault","A_remote","Ain","remote"],
            "Motor / VESC Fault":["start","init","remote","remoteq","tiltread","limitsread","motorread","motorq","motorfault","A_motor","Ain","remote"],
            "Tilt Warning":["start","init","remote","remoteq","tiltread","limitsread","motorread","motorq","tiltq","warningon","drivecmd","mix","speedlimit","driveq","stopcrane_drive","senddrive","A_drive","Ain","remote"],
            "Vehicle Still Moving":normal+["driveq","stopdrive","movingq","keepmoving","A_move","Ain","remote"],
            "Stopped < 0.5 s":normal+["driveq","stopdrive","movingq","stopped05","keepwait","A_wait","Ain","remote"],
            "LEFT Limit Active":normal+["driveq","stopdrive","movingq","stopped05","controlcrane","cranedir","leftlimitq","stopleft","A_bottom","Ain","remote"],
            "RIGHT Limit Active":normal+["driveq","stopdrive","movingq","stopped05","controlcrane","cranedir","rightlimitq","stopright","A_bottom","Ain","remote"],
        }
        return paths.get(name,paths["Idle / Ready"])

    def set_flowchart_zoom(self,text):
        if not hasattr(self,"flowBoard"):return
        try:value=float(str(text).replace("%","").strip())/100.0
        except Exception:value=.90
        self.flowBoard.set_zoom(value)

    def fit_flowchart_width(self):
        """Fit only the diagram width while preserving aspect ratio."""
        if not hasattr(self,"flowBoard") or not hasattr(self,"flowScroll"):return
        try:
            available=max(640,self.flowScroll.viewport().width()-24)
            value=max(.70,min(1.30,available/float(self.flowBoard.logical_w)))
            pct=int(round(value*100))
            self.flowZoom.blockSignals(True)
            self.flowZoom.setCurrentText(f"{pct}%")
            self.flowZoom.blockSignals(False)
            self.flowBoard.set_zoom(value)
            self.flowScroll.horizontalScrollBar().setValue(0)
        except Exception:
            self.flowBoard.set_zoom(.90)

    def set_flowchart_scenario(self,*_):
        path=self.flowchart_scenario_path()
        self.flowStep=0
        self.flowBoard.set_path(path,0)
        self._update_flowchart_step_info()

    def flowchart_next_step(self):
        path=self.flowBoard.path
        if not path:return
        self.flowStep=(self.flowStep+1)%len(path)
        self.flowBoard.set_path(path,self.flowStep)
        self._update_flowchart_step_info()

    def flowchart_prev_step(self):
        path=self.flowBoard.path
        if not path:return
        self.flowStep=(self.flowStep-1)%len(path)
        self.flowBoard.set_path(path,self.flowStep)
        self._update_flowchart_step_info()

    def toggle_flowchart_play(self):
        if self.flowPlayTimer.isActive():
            self.flowPlayTimer.stop();self.flowPlayButton.setText("▶ Play")
        else:
            self.flowPlayTimer.start(800);self.flowPlayButton.setText("■ Stop")

    def _update_flowchart_step_info(self):
        current=self.flowBoard.current_node()
        labels={
            "start":"Start (Power ON)",
            "init":"Start System — เตรียม ESP32, remote, sensors และ motors",
            "remote":"Read Remote Signal — รับ FlySky FS-i6X ผ่าน i-BUS",
            "remoteq":"Remote OK? — ตรวจว่าสัญญาณรีโมทยังปกติ",
            "remotefault":"Remote ผิดปกติ → หยุดรถ + หยุดการหมุนเครน + Alarm ON",
            "tiltread":"Read Tilt (IMU)",
            "limitsread":"Read Crane Limits (Left / Right)",
            "motorread":"Read Motor Status (VESC)",
            "motorq":"Motor System OK? — ตรวจ VESC / motor communication",
            "motorfault":"Motor/VESC ผิดปกติ → หยุดรถ + หยุดเครน + Alarm ON",
            "tiltq":"Vehicle Tilt Too High? — ตรวจมุมเอียง",
            "warningon":"Tilt สูง → Warning ON (Buzzer + LED), แต่ Flowchart Final ไม่สั่งหยุดรถอัตโนมัติ",
            "warningoff":"Tilt ปกติ → Warning OFF",
            "drivecmd":"Read Driving Command — Forward / Reverse / Left / Right",
            "mix":"Calculate Left / Right Motor Speed — Differential Steering",
            "speedlimit":"Limit Speed to 1 km/h + Soft Start / Stop",
            "driveq":"Drive Command Active?",
            "stopcrane_drive":"มีคำสั่งขับ → Stop Crane Rotation ก่อน",
            "senddrive":"Send Drive Command to VESC",
            "stopdrive":"ไม่มีคำสั่งขับ → Send Stop Command to VESC",
            "movingq":"Vehicle Still Moving?",
            "keepmoving":"รถยังเคลื่อนที่ → Keep Crane Stopped",
            "stopped05":"รถหยุดแล้วหรือยังหยุดนิ่งต่อเนื่องอย่างน้อย 0.5 s?",
            "keepwait":"หยุดยังไม่ครบ 0.5 s → Keep Crane Stopped",
            "controlcrane":"Control Crane — อ่าน LEFT / STOP / RIGHT จากรีโมท",
            "cranedir":"Crane Direction?",
            "leftlimitq":"LEFT → Left Limit Reached?",
            "rightlimitq":"RIGHT → Right Limit Reached?",
            "stopleft":"Left Limit ทำงาน → Stop Crane",
            "turnleft":"Left Limit ยังไม่ทำงาน → Turn Left",
            "turnright":"Right Limit ยังไม่ทำงาน → Turn Right",
            "stopright":"Right Limit ทำงาน → Stop Crane",
            "cranestop":"STOP → Stop Crane",
            "Ain":"Connector A (entry) → Read Remote Signal รอบถัดไป",
            "A_remote":"Connector A → กลับไปอ่าน Remote Signal ใหม่",
            "A_motor":"Connector A → กลับไปอ่าน Remote Signal ใหม่",
            "A_drive":"Connector A → กลับไปอ่าน Remote Signal ใหม่",
            "A_move":"Connector A → กลับไปอ่าน Remote Signal ใหม่",
            "A_wait":"Connector A → กลับไปอ่าน Remote Signal ใหม่",
            "A_bottom":"Connector A → กลับไปอ่าน Remote Signal ใหม่",
        }
        step=self.flowStep+1 if self.flowBoard.path else 0
        total=len(self.flowBoard.path)
        self.flowStepLabel.setText(f"Step {step}/{total} • {labels.get(current,'')}")
        self.flowExplanation.setHtml(f"""
        <h2>Current Step</h2>
        <p style='font-size:12pt'><b>{labels.get(current,'—')}</b></p>
        <hr>
        <h3>Flowchart Final — หลักการตามเอกสาร</h3>
        <p>• ถ้ารถกำลังเคลื่อนที่ → <b>ห้ามหมุนเครน</b></p>
        <p>• ก่อนหมุนเครน รถต้องหยุดนิ่งต่อเนื่องอย่างน้อย <b>0.5 s</b></p>
        <p>• คำสั่งขับรถถูกคำนวณเป็นความเร็วมอเตอร์ซ้าย/ขวาด้วย <b>Differential Steering</b> และจำกัดความเร็วประมาณ <b>1 km/h</b></p>
        <p>• Tilt สูง → เปิด <b>Buzzer + LED</b>. ใน Flowchart Final ที่แนบ การเอียงเป็นการเตือนและ <b>ไม่สั่งหยุดรถอัตโนมัติ</b></p>
        <p>• Limit ด้านใดทำงาน จะห้ามหมุนต่อเข้าด้านนั้น แต่ยังหมุนย้อนออกจาก Limit ได้</p>
        <p>• Connector <b>A</b> หมายถึงกลับไปอ่าน Remote Signal ใหม่ในรอบถัดไป</p>
        <p style='background:#eef6ff;padding:9px;border:1px solid #cfe2f5'>
        หน้านี้ทำตามลำดับ Flowchart Final ในเอกสารที่ผู้ใช้ส่งมา ไม่รวม Winch ใน Control Flow หลัก.
        </p>
        """)

    def sync_flowchart_from_safety(self):
        if not hasattr(self,"flowBoard"):return
        v=self.safety_input_values() if hasattr(self,"safetyEStop") else {}
        tilt_warning=abs(float(v.get("tilt",0)))>=float(v.get("tilt_limit",12))
        drive_req=abs(int(v.get("throttle",0)))>2 or abs(int(v.get("steer",0)))>2
        crane=str(v.get("crane","STOP"))
        if v.get("estop") or not v.get("rc_ok",True):
            scenario="Remote Fault"
        elif v.get("vesc_fault",False):
            scenario="Motor / VESC Fault"
        elif tilt_warning:
            scenario="Tilt Warning"
        elif drive_req:
            scenario="Drive Forward"
        elif not v.get("stationary_05",True):
            scenario="Stopped < 0.5 s"
        elif crane.startswith("LEFT") and v.get("left_limit",False):
            scenario="LEFT Limit Active"
        elif crane.startswith("RIGHT") and v.get("right_limit",False):
            scenario="RIGHT Limit Active"
        elif crane.startswith("LEFT"):
            scenario="Crane LEFT"
        elif crane.startswith("RIGHT"):
            scenario="Crane RIGHT"
        else:
            scenario="Idle / Ready"
        idx=self.flowScenario.findText(scenario)
        if idx>=0:
            old=self.flowScenario.blockSignals(True);self.flowScenario.setCurrentIndex(idx);self.flowScenario.blockSignals(old)
        self.set_flowchart_scenario()

    def export_flowchart_png(self):
        docs=QStandardPaths.writableLocation(QStandardPaths.DocumentsLocation) or str(Path.home())
        filename,_=QFileDialog.getSaveFileName(self,"Export System Flowchart",str(Path(docs)/"CVET_System_Flowchart.png"),"PNG Image (*.png)")
        if not filename:return
        if not filename.lower().endswith(".png"):filename+=".png"
        pix=self.flowBoard.grab()
        if pix.save(filename):
            QMessageBox.information(self,"Flowchart","บันทึก Flowchart แล้ว:\n"+filename)
        else:
            QMessageBox.warning(self,"Flowchart","บันทึกรูปไม่สำเร็จ")


    # =====================================================================
    # V52.6 REAL-TIME ESP32 TELEMETRY / DATA LOGGER
    # =====================================================================
    def make_telemetry_page(self):
        w=QWidget();self.telemetryPage=w
        root=QVBoxLayout(w);root.setContentsMargins(16,14,16,16);root.setSpacing(10)
        root.addWidget(make_page_header(
            "ESP32 REAL-TIME TELEMETRY / DATA LOGGER",
            "WiFi UDP JSON • USB Serial JSON • Battery • VESC • Speed • IMU • RPM • RC • Limits • CSV",
            self.show_home_mode,"V53.1 WIFI LIVE","#e6fbfa","#087e8b"
        ))

        # Connection / acquisition toolbar
        bar=QFrame();bar.setObjectName("softPanel")
        bl=QGridLayout(bar);bl.setContentsMargins(12,9,12,9);bl.setHorizontalSpacing(8);bl.setVerticalSpacing(7)

        bl.addWidget(QLabel("Source"),0,0)
        self.telemetrySource=QComboBox()
        self.telemetrySource.addItems(["Simulation / Demo (NO ESP32)","ESP32 Serial JSON","ESP32 WiFi UDP JSON"])
        self.telemetrySource.setCurrentIndex(2)
        self.telemetrySource.currentIndexChanged.connect(self.telemetry_source_changed);bl.addWidget(self.telemetrySource,0,1,1,2)
        bl.addWidget(QLabel("Sender rate"),0,3)
        self.telemetryRateHz=QSpinBox();self.telemetryRateHz.setRange(1,20);self.telemetryRateHz.setValue(10);self.telemetryRateHz.setSuffix(" Hz")
        self.telemetryRateHz.valueChanged.connect(self.telemetry_rate_changed);bl.addWidget(self.telemetryRateHz,0,4)

        self.telemetryConnectButton=QPushButton("Connect / Start");self.telemetryConnectButton.setObjectName("primaryButton");self.telemetryConnectButton.clicked.connect(self.connect_telemetry)
        self.telemetryDisconnectButton=QPushButton("Disconnect");self.telemetryDisconnectButton.clicked.connect(self.disconnect_telemetry)
        self.telemetryLogButton=QPushButton("Start Logging");self.telemetryLogButton.clicked.connect(self.toggle_telemetry_logging)
        export=QPushButton("Export CSV");export.clicked.connect(self.export_telemetry_csv)
        clear=QPushButton("Clear Data");clear.setObjectName("secondaryButton");clear.clicked.connect(self.clear_telemetry_data)
        openHw=QPushButton("ESP32 I/O Manager");openHw.clicked.connect(self.show_hardware_mode)
        bl.addWidget(self.telemetryConnectButton,0,5);bl.addWidget(self.telemetryDisconnectButton,0,6)
        bl.addWidget(self.telemetryLogButton,0,7);bl.addWidget(export,0,8)

        self.telemetrySerialLabel=QLabel("Serial")
        bl.addWidget(self.telemetrySerialLabel,1,0)
        self.telemetryPort=QComboBox();self.telemetryPort.setMinimumWidth(150);bl.addWidget(self.telemetryPort,1,1)
        self.telemetryRefreshPorts=QPushButton("Refresh COM");self.telemetryRefreshPorts.clicked.connect(self.refresh_serial_ports);bl.addWidget(self.telemetryRefreshPorts,1,2)
        self.telemetryBaudLabel=QLabel("Baud");bl.addWidget(self.telemetryBaudLabel,1,3)
        self.telemetryBaud=QComboBox();self.telemetryBaud.addItems(["115200","230400","460800","921600"]);bl.addWidget(self.telemetryBaud,1,4)
        bl.addWidget(clear,1,7);bl.addWidget(openHw,1,8)

        self.telemetryWifiLabel=QLabel("WiFi UDP")
        bl.addWidget(self.telemetryWifiLabel,2,0)
        self.telemetryLocalIp=QComboBox();self.telemetryLocalIp.setMinimumWidth(150);self.telemetryLocalIp.currentIndexChanged.connect(self.refresh_telemetry_code_view);bl.addWidget(self.telemetryLocalIp,2,1)
        self.telemetryRefreshIp=QPushButton("Refresh PC IP");self.telemetryRefreshIp.clicked.connect(self.refresh_telemetry_local_ips);bl.addWidget(self.telemetryRefreshIp,2,2)
        self.telemetryUdpPortLabel=QLabel("UDP Port");bl.addWidget(self.telemetryUdpPortLabel,2,3)
        self.telemetryUdpPort=QSpinBox();self.telemetryUdpPort.setRange(1024,65535);self.telemetryUdpPort.setValue(4210);self.telemetryUdpPort.valueChanged.connect(self.refresh_telemetry_code_view);bl.addWidget(self.telemetryUdpPort,2,4)
        self.telemetryDeviceLabel=QLabel("Device ID");bl.addWidget(self.telemetryDeviceLabel,2,5)
        self.telemetryDeviceId=QLineEdit("CVET-ESP32");self.telemetryDeviceId.setPlaceholderText("ว่าง = รับทุก device");self.telemetryDeviceId.textChanged.connect(self.refresh_telemetry_code_view);bl.addWidget(self.telemetryDeviceId,2,6)
        self.telemetryLoopbackButton=QPushButton("Test WiFi Packet");self.telemetryLoopbackButton.clicked.connect(self.send_telemetry_loopback_test);bl.addWidget(self.telemetryLoopbackButton,2,7)
        self.telemetryWifiHelp=QLabel("Receive-only LAN telemetry");self.telemetryWifiHelp.setStyleSheet("color:#087e8b;font-weight:800;");bl.addWidget(self.telemetryWifiHelp,2,8)

        bl.setColumnStretch(1,1);bl.setColumnStretch(6,1);root.addWidget(bar)

        # Compact two-row status dashboard.
        statusGrid=QGridLayout();statusGrid.setHorizontalSpacing(9);statusGrid.setVerticalSpacing(9)
        def stat_card(title):
            box=QFrame();box.setObjectName("metricPanel");lay=QVBoxLayout(box);lay.setContentsMargins(11,8,11,8);lay.setSpacing(2)
            t=QLabel(title);t.setStyleSheet("color:#60758b;font-size:8.5pt;font-weight:900;")
            v=QLabel("—");v.setWordWrap(True);v.setStyleSheet("color:#17324d;font-size:13pt;font-weight:900;")
            lay.addWidget(t);lay.addWidget(v);return box,v
        cards=[]
        for title,attr in (
            ("CONNECTION","telemetryConnLabel"),("REMOTE / RATE","telemetryRemoteLabel"),
            ("BATTERY","telemetryBatteryLabel"),("CURRENT","telemetryCurrentLabel"),
            ("SPEED","telemetrySpeedLabel"),("IMU TILT","telemetryTiltLabel"),
            ("MOTOR RPM","telemetryRpmLabel"),("LOGGER","telemetryLogLabel")):
            c,v=stat_card(title);setattr(self,attr,v);cards.append(c)
        for i,c in enumerate(cards):statusGrid.addWidget(c,i//4,i%4)
        for col in range(4):statusGrid.setColumnStretch(col,1)
        root.addLayout(statusGrid)

        self.telemetryTabs=QTabWidget();root.addWidget(self.telemetryTabs,1)

        # Live dashboard
        live=QWidget();ll=QHBoxLayout(live);ll.setContentsMargins(8,8,8,8);ll.setSpacing(10)
        self.telemetryChart=TelemetryChartWidget(self);ll.addWidget(self.telemetryChart,3)
        side=QVBoxLayout()
        self.telemetryStateView=QTextEdit();self.telemetryStateView.setReadOnly(True);self.telemetryStateView.setMinimumWidth(300)
        side.addWidget(self.telemetryStateView,2)
        self.telemetryProtocolStatus=QPlainTextEdit();self.telemetryProtocolStatus.setReadOnly(True);self.telemetryProtocolStatus.setMaximumHeight(185)
        side.addWidget(self.telemetryProtocolStatus,1)
        sw=QWidget();sw.setLayout(side);ll.addWidget(sw,1)
        self.telemetryTabs.addTab(live,"Live Dashboard")

        # Recent sample table
        samples=QWidget();sl=QVBoxLayout(samples);sl.setContentsMargins(8,8,8,8)
        self.telemetryTable=QTableWidget(0,15)
        self.telemetryTable.setHorizontalHeaderLabels([
            "Time","Battery V","Battery A","Speed","Tilt","RPM L","RPM R",
            "VESC A","Throttle","Steer","Limit L","Limit R","State","Device","Source IP"
        ])
        self.telemetryTable.verticalHeader().setVisible(False);self.telemetryTable.setAlternatingRowColors(True)
        self.telemetryTable.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.telemetryTable.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        self.telemetryTable.horizontalHeader().setSectionResizeMode(12,QHeaderView.Stretch)
        sl.addWidget(self.telemetryTable,1);self.telemetryTabs.addTab(samples,"Recent Samples")

        # ESP32 protocol/code page — follows selected transport.
        proto=QWidget();pl=QVBoxLayout(proto);pl.setContentsMargins(8,8,8,8);pl.setSpacing(7)
        top=QHBoxLayout()
        copy=QPushButton("Copy ESP32 Sender Template");copy.setObjectName("primaryButton");copy.clicked.connect(self.copy_telemetry_esp32_template)
        exp=QPushButton("Export .ino");exp.clicked.connect(self.export_telemetry_esp32_template)
        top.addWidget(copy);top.addWidget(exp);top.addStretch(1);pl.addLayout(top)
        self.telemetryGuideLabel=QLabel("")
        self.telemetryGuideLabel.setWordWrap(True);self.telemetryGuideLabel.setStyleSheet("background:#eef8ff;color:#294d6b;padding:9px;border:1px solid #d3e6f5;border-radius:8px;");pl.addWidget(self.telemetryGuideLabel)
        self.telemetryCodeView=QPlainTextEdit();self.telemetryCodeView.setReadOnly(True)
        self.telemetryCodeView.setStyleSheet("font-family:Consolas,'Courier New',monospace;font-size:9.5pt;")
        pl.addWidget(self.telemetryCodeView,1);self.telemetryTabs.addTab(proto,"ESP32 Protocol / Code")

        wifiInfo=QPlainTextEdit();wifiInfo.setReadOnly(True)
        wifiInfo.setPlainText("""WIFI TELEMETRY — DESIGN RULES

1) PC และ ESP32 ต้องอยู่เครือข่าย LAN/WiFi เดียวกัน
2) เลือก Source = ESP32 WiFi UDP JSON
3) เลือก PC IP ที่ ESP32 เข้าถึงได้ และกำหนด UDP Port (ค่าเริ่มต้น 4210)
4) กด Connect / Start = เปิด UDP LISTENER เท่านั้น ยังไม่ถือว่าเชื่อม ESP32
5) ใส่ PC IP + Port เดียวกันใน ESP32 template แล้ว Upload
6) โปรแกรมจะขึ้น CONNECTED เฉพาะเมื่อได้รับ CVET telemetry packet จริงจาก Device ID ที่ตรงกัน
7) ถ้า ESP32 หยุดส่งเกิน 2.5 s สถานะจะไม่ค้างเป็น CONNECTED และค่าจริงจะถูกซ่อน
8) Windows Firewall อาจถามสิทธิ์ครั้งแรก — อนุญาต Private networks หากเป็นเครือข่ายที่ไว้ใจได้

ความปลอดภัย:
• ช่องทางนี้เป็น TELEMETRY RECEIVE-ONLY — โปรแกรมไม่ส่งคำสั่ง Drive/Crane/Winch กลับผ่าน WiFi
• UDP ไม่มี encryption/authentication ในตัว จึงเหมาะกับ LAN ที่ไว้ใจได้
• Device ID เป็น filter เพื่อกัน packet อื่น ไม่ใช่ security key
• ถ้าจะควบคุมรถผ่าน WiFi ในอนาคต ควรทำ protocol ที่มี authentication + failsafe แยกจาก telemetry
""")
        self.telemetryTabs.addTab(wifiInfo,"WiFi Setup / Safety")

        self.telemetryHistory=[];self.telemetryLogRows=[];self.telemetryConnected=False;self.telemetryListening=False;self.telemetryLogging=False
        self.telemetrySerial=None;self.telemetrySampleCounter=0;self.telemetryParseErrors=0
        self.telemetryUdpSocket=None;self.telemetryUdpThread=None;self.telemetryUdpStop=None
        self.telemetryLastRx=0.0;self.telemetryRemoteAddr="";self.telemetryRxTimes=[];self.telemetryFilteredPackets=0
        self.telemetryLastValidDevice=""
        self.telemetryTimer=QTimer(self);self.telemetryTimer.timeout.connect(self.telemetry_tick)
        self.telemetryNetworkPacket.connect(self.handle_wifi_telemetry_event)

        self.refresh_serial_ports();self.refresh_telemetry_local_ips()
        self.telemetry_source_changed();self.update_telemetry_ui()
        self.tabs.addTab(w,"")

    def refresh_telemetry_local_ips(self,*_):
        if not hasattr(self,"telemetryLocalIp"):return
        old=self.telemetryLocalIp.currentText().strip()
        ips=set()
        try:
            for item in socket.getaddrinfo(socket.gethostname(),None,socket.AF_INET,socket.SOCK_DGRAM):
                ip=item[4][0]
                if ip and not ip.startswith("127."):ips.add(ip)
        except Exception:
            pass
        # Route-based lookup often finds the active WiFi/Ethernet interface even
        # when hostname resolution only returns loopback. connect() sends no packet.
        try:
            probe=socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
            probe.connect(("8.8.8.8",80));ip=probe.getsockname()[0];probe.close()
            if ip and not ip.startswith("127."):ips.add(ip)
        except Exception:
            pass
        def rank(ip):
            if ip.startswith("192.168."):return (0,ip)
            if ip.startswith("10."):return (1,ip)
            if ip.startswith("172."):return (2,ip)
            return (3,ip)
        values=sorted(ips,key=rank) or ["127.0.0.1"]
        self.telemetryLocalIp.blockSignals(True);self.telemetryLocalIp.clear();self.telemetryLocalIp.addItems(values)
        idx=self.telemetryLocalIp.findText(old)
        if idx>=0:self.telemetryLocalIp.setCurrentIndex(idx)
        self.telemetryLocalIp.blockSignals(False)
        self.refresh_telemetry_code_view()

    def telemetry_packet_rate(self):
        now=time.monotonic()
        self.telemetryRxTimes=[x for x in getattr(self,"telemetryRxTimes",[]) if now-x<=2.0]
        xs=self.telemetryRxTimes
        if len(xs)<2:return 0.0
        span=max(xs[-1]-xs[0],1e-6)
        return (len(xs)-1)/span

    def start_wifi_telemetry_listener(self):
        self.stop_wifi_telemetry_listener()
        port=int(self.telemetryUdpPort.value())
        sock=socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
        sock.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)
        sock.bind(("0.0.0.0",port));sock.settimeout(0.40)
        self.telemetryUdpSocket=sock
        self.telemetryUdpGeneration=getattr(self,"telemetryUdpGeneration",0)+1
        generation=self.telemetryUdpGeneration
        stop=threading.Event();self.telemetryUdpStop=stop
        self.telemetryListening=True;self.telemetryConnected=False;self.telemetryLastRx=0.0;self.telemetryRemoteAddr="";self.telemetryRxTimes=[];self.telemetryLastValidDevice=""
        def worker():
            while not stop.is_set():
                try:
                    raw,addr=sock.recvfrom(8192)
                    if len(raw)>4096:
                        self.telemetryNetworkPacket.emit({"type":"parse_error","generation":generation,"error":"UDP packet > 4096 bytes"})
                        continue
                    try:
                        payload=json.loads(raw.decode("utf-8","strict"))
                        if not isinstance(payload,dict):raise ValueError("JSON root must be object")
                        self.telemetryNetworkPacket.emit({"type":"packet","generation":generation,"payload":payload,"addr":addr,"bytes":len(raw)})
                    except Exception as exc:
                        self.telemetryNetworkPacket.emit({"type":"parse_error","generation":generation,"error":str(exc)})
                except socket.timeout:
                    continue
                except OSError:
                    break
                except Exception as exc:
                    self.telemetryNetworkPacket.emit({"type":"network_error","generation":generation,"error":str(exc)})
                    break
        self.telemetryUdpThread=threading.Thread(target=worker,name="CVET-UDP-Telemetry",daemon=True);self.telemetryUdpThread.start()

    def stop_wifi_telemetry_listener(self):
        self.telemetryUdpGeneration=getattr(self,"telemetryUdpGeneration",0)+1
        stop=getattr(self,"telemetryUdpStop",None)
        if stop is not None:
            try:stop.set()
            except Exception:pass
        sock=getattr(self,"telemetryUdpSocket",None)
        if sock is not None:
            try:sock.close()
            except Exception:pass
        self.telemetryUdpSocket=None;self.telemetryUdpStop=None
        th=getattr(self,"telemetryUdpThread",None)
        if th is not None and th.is_alive():
            try:th.join(timeout=0.15)
            except Exception:pass
        self.telemetryUdpThread=None

    def validate_telemetry_payload(self,payload,transport="wifi"):
        """Verify that a packet is actual CVET ESP32 telemetry, not merely an open socket."""
        if not isinstance(payload,dict):
            return False,"JSON root is not an object"
        if self._telemetry_bool(payload.get("cvet_loopback_test",False)):
            return False,"loopback-test"

        known={
            "battery_v","voltage","vbat","battery_a","battery_current","ibat",
            "speed_kmh","speed","tilt_deg","tilt","left_rpm","rpm_l",
            "right_rpm","rpm_r","vesc_current_a","rc_throttle","throttle",
            "rc_steer","steer","limit_left","limit_right","estop","rc_ok"
        }
        present=sum(1 for k in known if k in payload)
        protocol=str(payload.get("protocol","")).strip()
        device=str(payload.get("device","")).strip()
        expected=self.telemetryDeviceId.text().strip() if hasattr(self,"telemetryDeviceId") else "CVET-ESP32"

        if protocol and protocol!="CVET1":
            return False,f"protocol {protocol!r} ไม่ใช่ CVET1"

        if transport=="wifi":
            if not device:
                return False,"WiFi packet ไม่มี Device ID"
            if expected and device!=expected:
                return False,f"Device ID {device!r} ไม่ตรงกับ {expected!r}"
            if present<4:
                return False,"packet มี telemetry fields ไม่พอ"
            return True,"verified"

        if device and expected and device!=expected:
            return False,f"Device ID {device!r} ไม่ตรงกับ {expected!r}"
        if device==expected and present>=3:
            return True,"verified"
        if present>=7:
            return True,"legacy-cvet"
        return False,"Serial JSON ยังไม่ใช่ CVET telemetry packet"

    def _mark_real_esp32_sample(self,sample,transport):
        first=not getattr(self,"telemetryConnected",False)
        self.telemetryConnected=True
        self.telemetryLastRx=time.monotonic()
        self.telemetryLastValidDevice=str(sample.get("device","") or "CVET-ESP32")
        if transport=="Serial":
            self.telemetryRemoteAddr=self.telemetryPort.currentText().strip()
        if first:
            self.statusBar().showMessage(
                f"ESP32 VERIFIED • {transport} • {self.telemetryLastValidDevice}",4000
            )

    def handle_wifi_telemetry_event(self,event):
        if not isinstance(event,dict):return
        if event.get("generation")!=getattr(self,"telemetryUdpGeneration",None):return
        typ=event.get("type")
        if typ=="parse_error":
            self.telemetryParseErrors+=1
            self.update_telemetry_ui();return
        if typ=="network_error":
            if hasattr(self,"telemetryProtocolStatus"):self.telemetryProtocolStatus.setPlainText("WiFi UDP error:\n"+str(event.get("error","")))
            return
        if typ!="packet":return
        payload=event.get("payload",{})
        if self._telemetry_bool(payload.get("cvet_loopback_test",False)):
            if hasattr(self,"telemetryProtocolStatus"):
                self.telemetryProtocolStatus.setPlainText(
                    "LOCAL UDP LOOPBACK TEST = PASS\n"
                    "ทดสอบเฉพาะ UDP listener ในคอม • ไม่ถือว่าเชื่อมต่อ ESP32"
                )
            self.statusBar().showMessage("Local UDP test PASS • ESP32 ยังไม่ถูกยืนยัน",3000)
            self.update_telemetry_ui();return
        ok,reason=self.validate_telemetry_payload(payload,"wifi")
        if not ok:
            self.telemetryFilteredPackets+=1
            if hasattr(self,"telemetryProtocolStatus"):
                self.telemetryProtocolStatus.setPlainText("Ignored UDP packet:\n"+str(reason))
            self.update_telemetry_ui();return
        try:
            sample=self.normalize_telemetry_sample(payload)
        except Exception:
            self.telemetryParseErrors+=1;self.update_telemetry_ui();return
        addr=event.get("addr",("",0))
        sample["source_ip"]=str(addr[0]);sample["source_port"]=int(addr[1])
        sample["transport"]="WiFi UDP"
        self.telemetryRemoteAddr=f"{addr[0]}:{addr[1]}"
        self._mark_real_esp32_sample(sample,"WiFi UDP")
        self.telemetryRxTimes.append(self.telemetryLastRx)
        self.telemetryRxTimes=[x for x in self.telemetryRxTimes if self.telemetryLastRx-x<=2.0]
        self.ingest_telemetry_sample(sample)

    def send_telemetry_loopback_test(self,*_):
        if self.telemetrySource.currentIndex()!=2:self.telemetrySource.setCurrentIndex(2)
        if not getattr(self,"telemetryListening",False):self.connect_telemetry()
        if not getattr(self,"telemetryListening",False):return
        payload={
            "cvet_loopback_test":True,"protocol":"CVET1",
            "device":self.telemetryDeviceId.text().strip() or "CVET-ESP32",
            "seq":1,"uptime_ms":12345,"battery_v":72.4,"battery_pct":84.0,"battery_a":8.2,
            "speed_kmh":1.0,"tilt_deg":2.1,"left_rpm":13.2,"right_rpm":13.0,
            "vesc_current_a":9.0,"rc_throttle":25.0,"rc_steer":0.0,
            "limit_left":False,"limit_right":False,"estop":False,"rc_ok":True,
            "wifi_rssi_dbm":-55,"state":"WIFI TEST"
        }
        try:
            tx=socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
            tx.sendto(json.dumps(payload,separators=(",",":")).encode("utf-8"),("127.0.0.1",int(self.telemetryUdpPort.value())))
            tx.close();self.statusBar().showMessage("Sent local WiFi telemetry test packet",2500)
        except Exception as exc:
            QMessageBox.warning(self,"WiFi Telemetry Test",str(exc))

    def refresh_telemetry_code_view(self,*_):
        if not hasattr(self,"telemetryCodeView") or not hasattr(self,"telemetrySource"):return
        idx=self.telemetrySource.currentIndex()
        if idx==2:
            self.telemetryCodeView.setPlainText(self.telemetry_wifi_esp32_template())
            if hasattr(self,"telemetryGuideLabel"):
                self.telemetryGuideLabel.setText("WiFi mode: ESP32 ส่ง JSON datagram ผ่าน UDP ไปยัง PC IP + UDP Port ที่แสดงด้านบน ไม่ต้องเสียบสาย USB หลัง Upload แล้ว")
        else:
            self.telemetryCodeView.setPlainText(self.telemetry_esp32_template())
            if hasattr(self,"telemetryGuideLabel"):
                self.telemetryGuideLabel.setText('Serial mode: ESP32 ส่ง JSON 1 บรรทัดต่อ sample ผ่าน USB Serial เช่น {"battery_v":72.4,"battery_a":12.3,"speed_kmh":1.0,...}')

    def telemetry_source_changed(self,*_):
        self.disconnect_telemetry(silent=True)
        idx=self.telemetrySource.currentIndex() if hasattr(self,"telemetrySource") else 0
        serial_mode=idx==1;wifi_mode=idx==2
        for name in ("telemetrySerialLabel","telemetryPort","telemetryRefreshPorts","telemetryBaudLabel","telemetryBaud"):
            if hasattr(self,name):getattr(self,name).setEnabled(serial_mode)
        for name in ("telemetryWifiLabel","telemetryLocalIp","telemetryRefreshIp","telemetryUdpPortLabel",
                     "telemetryUdpPort","telemetryDeviceLabel","telemetryDeviceId","telemetryLoopbackButton","telemetryWifiHelp"):
            if hasattr(self,name):getattr(self,name).setEnabled(wifi_mode)
        self.refresh_telemetry_code_view()
        self.update_telemetry_ui()

    def telemetry_rate_changed(self,*_):
        if hasattr(self,"telemetryTimer") and self.telemetryTimer.isActive():
            if hasattr(self,"telemetrySource") and self.telemetrySource.currentIndex()==2:
                self.telemetryTimer.setInterval(250)
            else:
                self.telemetryTimer.setInterval(max(50,int(1000/max(1,self.telemetryRateHz.value()))))
        self.refresh_telemetry_code_view()

    def refresh_serial_ports(self,*_):
        if not hasattr(self,"telemetryPort"):return
        old=self.telemetryPort.currentText()
        self.telemetryPort.blockSignals(True);self.telemetryPort.clear()
        ports=[]
        if SERIAL_AVAILABLE and list_ports is not None:
            try:ports=[p.device for p in list_ports.comports()]
            except Exception:ports=[]
        if ports:self.telemetryPort.addItems(ports)
        else:self.telemetryPort.addItem("No COM port found" if SERIAL_AVAILABLE else "pyserial unavailable")
        idx=self.telemetryPort.findText(old)
        if idx>=0:self.telemetryPort.setCurrentIndex(idx)
        self.telemetryPort.blockSignals(False)

    def connect_telemetry(self,*_):
        self.disconnect_telemetry(silent=True)
        self.telemetryParseErrors=0
        self.telemetryLastRx=0.0
        self.telemetryLastValidDevice=""
        idx=self.telemetrySource.currentIndex()

        if idx==0:
            self.telemetryListening=False
            self.telemetryConnected=True
            self.telemetryTimer.start(max(50,int(1000/max(1,self.telemetryRateHz.value()))))
            self.statusBar().showMessage("DEMO MODE • NO ESP32 • ข้อมูลจำลองเท่านั้น",5000)
        elif idx==1:
            if not SERIAL_AVAILABLE or serial is None:
                QMessageBox.warning(self,"ESP32 Telemetry","pyserial ไม่พร้อมใช้งานในโปรแกรมรุ่นนี้")
                return
            port=self.telemetryPort.currentText().strip()
            if not port or port.startswith("No ") or port.startswith("pyserial"):
                QMessageBox.warning(self,"ESP32 Telemetry","ไม่พบ COM Port ของ ESP32")
                return
            try:
                self.telemetrySerial=serial.Serial(port,int(self.telemetryBaud.currentText()),timeout=0)
                self.telemetryListening=True
                self.telemetryConnected=False
                self.telemetryTimer.start(max(50,int(1000/max(1,self.telemetryRateHz.value()))))
                self.statusBar().showMessage(
                    f"เปิด {port} แล้ว • WAITING FOR REAL ESP32 TELEMETRY",4500
                )
            except Exception as exc:
                self.telemetrySerial=None;self.telemetryListening=False;self.telemetryConnected=False
                QMessageBox.warning(self,"ESP32 Telemetry",f"เปิด {port} ไม่สำเร็จ\n{exc}")
        else:
            try:
                self.start_wifi_telemetry_listener()
                self.telemetryTimer.start(250)
                self.statusBar().showMessage(
                    f"UDP :{self.telemetryUdpPort.value()} พร้อมรับ • WAITING FOR ESP32 {self.telemetryDeviceId.text().strip() or 'CVET-ESP32'}",
                    5000
                )
            except Exception as exc:
                self.telemetryListening=False;self.telemetryConnected=False
                QMessageBox.warning(self,"ESP32 WiFi Telemetry",f"เปิด UDP listener ไม่สำเร็จ\n{exc}")
        self.update_telemetry_ui()

    def disconnect_telemetry(self,*_,silent=False):
        if hasattr(self,"telemetryTimer"):self.telemetryTimer.stop()
        ser=getattr(self,"telemetrySerial",None)
        if ser is not None:
            try:ser.close()
            except Exception:pass
        self.telemetrySerial=None
        self.stop_wifi_telemetry_listener()
        self.telemetryListening=False
        self.telemetryConnected=False
        self.telemetryLastRx=0.0;self.telemetryRemoteAddr="";self.telemetryRxTimes=[]
        if not silent and hasattr(self,"statusBar"):self.statusBar().showMessage("Telemetry disconnected",2500)
        if hasattr(self,"telemetryConnLabel"):self.update_telemetry_ui()

    @staticmethod
    def _telemetry_bool(value):
        if isinstance(value,bool):return value
        if isinstance(value,(int,float)):return bool(value)
        return str(value).strip().lower() in ("1","true","yes","on","active")

    @staticmethod
    def _telemetry_num(value,default=0.0):
        try:return float(value)
        except Exception:return float(default)

    def normalize_telemetry_sample(self,data):
        if not isinstance(data,dict):raise ValueError("Telemetry JSON must be an object")
        aliases={
            "battery_v":("battery_v","voltage","vbat","v"),
            "battery_a":("battery_a","battery_current","ibat","current","a"),
            "speed_kmh":("speed_kmh","speed","vehicle_speed"),
            "tilt_deg":("tilt_deg","tilt","imu_tilt"),
            "left_rpm":("left_rpm","rpm_l","motor_left_rpm"),
            "right_rpm":("right_rpm","rpm_r","motor_right_rpm"),
            "vesc_current_a":("vesc_current_a","vesc_current","motor_current"),
            "rc_throttle":("rc_throttle","throttle"),
            "rc_steer":("rc_steer","steer"),
        }
        out={}
        for dst,keys in aliases.items():
            val=next((data[k] for k in keys if k in data),0.0);out[dst]=self._telemetry_num(val)
        pct=next((data[k] for k in ("battery_pct","battery_percent","soc") if k in data),-1.0)
        out["battery_pct"]=max(-1.0,min(100.0,self._telemetry_num(pct)))
        out["wifi_rssi_dbm"]=self._telemetry_num(data.get("wifi_rssi_dbm",data.get("rssi",-999)))
        out["seq"]=int(max(0,self._telemetry_num(data.get("seq",0))))
        out["uptime_ms"]=int(max(0,self._telemetry_num(data.get("uptime_ms",data.get("uptime",0)))))
        out["device"]=str(data.get("device","")).strip()
        out["limit_left"]=self._telemetry_bool(data.get("limit_left",data.get("left_limit",False)))
        out["limit_right"]=self._telemetry_bool(data.get("limit_right",data.get("right_limit",False)))
        out["estop"]=self._telemetry_bool(data.get("estop",False))
        out["rc_ok"]=self._telemetry_bool(data.get("rc_ok",True))
        out["state"]=str(data.get("state","LIVE")).strip() or "LIVE"
        out["timestamp"]=str(data.get("timestamp","")).strip() or datetime.now().isoformat(timespec="milliseconds")
        return out

    def parse_telemetry_line(self,line):
        if isinstance(line,bytes):line=line.decode("utf-8","replace")
        text=str(line).strip()
        if not text:return None
        try:return self.normalize_telemetry_sample(json.loads(text))
        except Exception as exc:
            self.telemetryParseErrors+=1
            self.telemetryProtocolStatus.setPlainText(f"JSON parse error #{self.telemetryParseErrors}\n{text[:220]}\n{exc}")
            return None

    def simulated_telemetry_sample(self):
        n=self.telemetrySampleCounter;phase=n/10.0
        speed=max(0.0,1.0+0.12*math.sin(phase*0.65))
        current=max(0.0,10.5+5.0*math.sin(phase*0.72)+1.7*math.sin(phase*1.9))
        tilt=2.5+4.5*math.sin(phase*0.21)
        rpm=speed/3.6/(2*math.pi*max(self.tradius.value(),0.01))*60 if hasattr(self,"tradius") else speed*12
        return self.normalize_telemetry_sample({
            "battery_v":72.5-0.003*n+0.15*math.sin(phase*0.3),
            "battery_a":current,"speed_kmh":speed,"tilt_deg":tilt,
            "left_rpm":rpm*(1+0.035*math.sin(phase)),"right_rpm":rpm*(1-0.035*math.sin(phase)),
            "vesc_current_a":current*1.08,"rc_throttle":28+8*math.sin(phase*0.4),
            "rc_steer":10*math.sin(phase*0.3),"limit_left":False,"limit_right":False,
            "estop":False,"rc_ok":True,"state":"DRIVE" if speed>0.05 else "READY"
        })

    def telemetry_tick(self):
        idx=self.telemetrySource.currentIndex()

        if idx==0:
            if not getattr(self,"telemetryConnected",False):return
            self.telemetrySampleCounter+=1
            self.ingest_telemetry_sample(self.simulated_telemetry_sample())
            return

        if idx==2:
            if getattr(self,"telemetryConnected",False) and getattr(self,"telemetryLastRx",0)>0:
                if time.monotonic()-self.telemetryLastRx>2.5:
                    self.telemetryConnected=False
            self.update_telemetry_ui()
            return

        ser=getattr(self,"telemetrySerial",None)
        if ser is None:return
        try:
            count=0
            while getattr(ser,"in_waiting",0)>0 and count<50:
                line=ser.readline();count+=1
                raw_text=line.decode("utf-8","replace").strip() if isinstance(line,bytes) else str(line).strip()
                if not raw_text:continue
                try:
                    payload=json.loads(raw_text)
                except Exception as exc:
                    self.telemetryParseErrors+=1
                    self.telemetryProtocolStatus.setPlainText(
                        f"Serial JSON parse error #{self.telemetryParseErrors}\n{raw_text[:220]}\n{exc}"
                    )
                    continue
                ok,reason=self.validate_telemetry_payload(payload,"serial")
                if not ok:
                    self.telemetryFilteredPackets+=1
                    self.telemetryProtocolStatus.setPlainText("Ignored Serial packet:\n"+str(reason))
                    continue
                sample=self.normalize_telemetry_sample(payload)
                sample["transport"]="USB Serial"
                sample["source_ip"]=""
                self._mark_real_esp32_sample(sample,"Serial")
                self.ingest_telemetry_sample(sample)

            if getattr(self,"telemetryConnected",False) and getattr(self,"telemetryLastRx",0)>0:
                if time.monotonic()-self.telemetryLastRx>2.5:
                    self.telemetryConnected=False
            self.update_telemetry_ui()
        except Exception as exc:
            self.telemetryProtocolStatus.setPlainText("Serial read error:\n"+str(exc))
            self.disconnect_telemetry(silent=True)
            self.update_telemetry_ui()

    def ingest_telemetry_sample(self,sample):
        if not isinstance(sample,dict):return
        if "timestamp" not in sample:sample=self.normalize_telemetry_sample(sample)
        self.telemetryHistory.append(sample)
        if len(self.telemetryHistory)>600:self.telemetryHistory=self.telemetryHistory[-600:]
        if self.telemetryLogging:
            self.telemetryLogRows.append(dict(sample))
            if len(self.telemetryLogRows)>200000:
                self.telemetryLogRows=self.telemetryLogRows[-200000:]
        self._insert_telemetry_table_row(sample)
        self.update_telemetry_ui()

    def _insert_telemetry_table_row(self,s):
        if not hasattr(self,"telemetryTable"):return
        self.telemetryTable.insertRow(0)
        vals=[
            str(s.get("timestamp","")).split("T")[-1],
            f"{s.get('battery_v',0):.2f}",f"{s.get('battery_a',0):.2f}",f"{s.get('speed_kmh',0):.3f}",
            f"{s.get('tilt_deg',0):.2f}",f"{s.get('left_rpm',0):.1f}",f"{s.get('right_rpm',0):.1f}",
            f"{s.get('vesc_current_a',0):.2f}",f"{s.get('rc_throttle',0):.1f}",f"{s.get('rc_steer',0):.1f}",
            "1" if s.get("limit_left") else "0","1" if s.get("limit_right") else "0",str(s.get("state","")),
            str(s.get("device","")),str(s.get("source_ip",""))
        ]
        for c,val in enumerate(vals):
            item=QTableWidgetItem(val);item.setTextAlignment(Qt.AlignCenter);self.telemetryTable.setItem(0,c,item)
        while self.telemetryTable.rowCount()>100:self.telemetryTable.removeRow(self.telemetryTable.rowCount()-1)

    def update_telemetry_ui(self,*_):
        if not hasattr(self,"telemetryConnLabel"):return
        connected=getattr(self,"telemetryConnected",False)
        listening=getattr(self,"telemetryListening",False)
        idx=self.telemetrySource.currentIndex()
        now=time.monotonic()
        fresh=(connected and getattr(self,"telemetryLastRx",0)>0 and now-self.telemetryLastRx<=2.5)
        if idx==0:
            conn_text=("DEMO\nNO ESP32" if connected else "OFFLINE\nDEMO");conn_ok=None if connected else False
            remote_text="SIMULATED DATA"
        elif idx==1:
            if fresh:
                conn_text="CONNECTED\nESP32 SERIAL";conn_ok=True
            elif listening:
                conn_text="WAITING\nESP32 SERIAL";conn_ok=None
            else:
                conn_text="OFFLINE\nSERIAL";conn_ok=False
            remote_text=(self.telemetryPort.currentText() if listening else "—")
            if listening and not fresh:remote_text+="\nwaiting valid CVET JSON"
        else:
            if fresh:
                conn_text="CONNECTED\nESP32 WIFI";conn_ok=True
            elif listening:
                conn_text="WAITING\nESP32 WIFI";conn_ok=None
            else:
                conn_text="OFFLINE\nWIFI UDP";conn_ok=False
            hz=self.telemetry_packet_rate()
            remote_text=(getattr(self,"telemetryRemoteAddr","") if fresh else "")
            remote_text=remote_text or ("waiting real ESP32 packet" if listening else "—")
            remote_text+=f"\n{hz:.1f} Hz"
        color="#176337" if conn_ok is True else ("#b54708" if conn_ok is None else "#b42318")
        self.telemetryConnLabel.setText(conn_text)
        self.telemetryConnLabel.setStyleSheet(f"color:{color};font-size:13pt;font-weight:900;")
        self.telemetryRemoteLabel.setText(remote_text)

        sample=self.telemetryHistory[-1] if self.telemetryHistory else None
        if idx in (1,2) and not fresh:
            sample=None
        if sample:
            pct=sample.get("battery_pct",-1)
            self.telemetryBatteryLabel.setText(f"{sample['battery_v']:.2f} V"+(f"\n{pct:.0f}%" if pct>=0 else ""))
            self.telemetryCurrentLabel.setText(f"{sample['battery_a']:.2f} A")
            self.telemetrySpeedLabel.setText(f"{sample['speed_kmh']:.3f} km/h")
            self.telemetryTiltLabel.setText(f"{sample['tilt_deg']:.2f}°")
            self.telemetryRpmLabel.setText(f"L {sample['left_rpm']:.1f}\nR {sample['right_rpm']:.1f}")
            fault=[]
            if sample.get("estop"):fault.append("E-STOP")
            if not sample.get("rc_ok",True):fault.append("RC LOST")
            if sample.get("limit_left"):fault.append("LEFT LIMIT")
            if sample.get("limit_right"):fault.append("RIGHT LIMIT")
            tilt_limit=getattr(getattr(self,"safetyTiltLimit",None),"value",lambda:12.0)()
            if abs(sample.get("tilt_deg",0))>=tilt_limit:fault.append("TILT LIMIT")
            state_color="#b42318" if fault else "#176337"
            net=""
            if sample.get("source_ip"):
                rssi=sample.get("wifi_rssi_dbm",-999)
                net=f"<tr><td>WiFi</td><td>{sample.get('device','') or 'ESP32'} @ {sample.get('source_ip','')}"+(f" / RSSI {rssi:.0f} dBm" if rssi>-200 else "")+"</td></tr>"
            self.telemetryStateView.setHtml(f"""
            <h2 style='color:{state_color}'>{sample.get('state','LIVE')}</h2>
            <table border='1' cellspacing='0' cellpadding='5'>
            <tr><td>Battery</td><td>{sample['battery_v']:.2f} V / {sample['battery_a']:.2f} A</td></tr>
            <tr><td>VESC current</td><td>{sample['vesc_current_a']:.2f} A</td></tr>
            <tr><td>Speed</td><td>{sample['speed_kmh']:.3f} km/h</td></tr>
            <tr><td>IMU tilt</td><td>{sample['tilt_deg']:.2f}°</td></tr>
            <tr><td>Motor RPM</td><td>L {sample['left_rpm']:.1f} / R {sample['right_rpm']:.1f}</td></tr>
            <tr><td>RC command</td><td>Throttle {sample['rc_throttle']:.1f}% / Steer {sample['rc_steer']:.1f}%</td></tr>
            <tr><td>Limits</td><td>L {int(sample['limit_left'])} / R {int(sample['limit_right'])}</td></tr>
            {net}
            </table>
            <p><b>Fault:</b> {', '.join(fault) if fault else 'None'}</p>
            """)
        else:
            for lab in (self.telemetryBatteryLabel,self.telemetryCurrentLabel,self.telemetrySpeedLabel,self.telemetryTiltLabel,self.telemetryRpmLabel):lab.setText("—")
            if idx==0:
                self.telemetryStateView.setHtml("<h3>DEMO MODE</h3><p>ข้อมูลจำลองเท่านั้น • ไม่ได้เชื่อม ESP32</p>")
            elif listening:
                self.telemetryStateView.setHtml("<h3 style='color:#b54708'>WAITING FOR ESP32</h3><p>สถานะนี้หมายถึงโปรแกรมเปิด Port/Listener แล้ว แต่ยังไม่ได้รับข้อมูลจาก ESP32 จริง จึงยังไม่แสดงค่ารถ</p>")
            else:
                self.telemetryStateView.setHtml("<h3>ESP32 OFFLINE</h3><p>ยังไม่มีการเชื่อมต่อฮาร์ดแวร์จริง</p>")

        count=len(self.telemetryLogRows)
        self.telemetryLogLabel.setText(("RECORDING" if self.telemetryLogging else "STOPPED")+f"\n{count} rows")
        self.telemetryLogLabel.setStyleSheet(f"color:{'#b42318' if self.telemetryLogging else '#17324d'};font-size:12pt;font-weight:900;")
        if hasattr(self,"telemetryChart"):self.telemetryChart.update()

        extra=""
        if idx==2:
            local=self.telemetryLocalIp.currentText() if hasattr(self,"telemetryLocalIp") else ""
            verify=("VERIFIED ESP32" if fresh else ("WAITING FOR REAL ESP32" if listening else "OFFLINE"))
            extra=(f"Hardware verification: {verify}\n"
                   f"Expected Device ID: {self.telemetryDeviceId.text().strip() or 'CVET-ESP32'}\n"
                   f"WiFi listener: 0.0.0.0:{self.telemetryUdpPort.value()}\n"
                   f"PC IP for ESP32: {local}\n"
                   f"Remote: {getattr(self,'telemetryRemoteAddr','') or 'waiting'}\n"
                   f"Packet rate: {self.telemetry_packet_rate():.2f} Hz\n"
                   f"Filtered packets: {getattr(self,'telemetryFilteredPackets',0)}\n")
        elif idx==1:
            verify=("VERIFIED ESP32" if fresh else ("WAITING FOR REAL ESP32" if listening else "OFFLINE"))
            extra=(f"Hardware verification: {verify}\n"
                   f"Serial Port: {self.telemetryPort.currentText()}\n"
                   f"Filtered packets: {getattr(self,'telemetryFilteredPackets',0)}\n")
        self.telemetryProtocolStatus.setPlainText(
            f"Transport: {self.telemetrySource.currentText()}\n"
            +extra+
            f"Serial support: {'OK' if SERIAL_AVAILABLE else 'NOT INSTALLED'}\n"
            f"Samples in live buffer: {len(self.telemetryHistory)}\n"
            f"Logged rows: {len(self.telemetryLogRows)}\n"
            f"JSON parse errors: {self.telemetryParseErrors}"
        )

    def toggle_telemetry_logging(self,*_):
        if not self.telemetryLogging:
            self.telemetryLogRows=[];self.telemetryLogging=True;self.telemetryLogButton.setText("Stop Logging")
        else:
            self.telemetryLogging=False;self.telemetryLogButton.setText("Start Logging")
        self.update_telemetry_ui()

    def clear_telemetry_data(self,*_):
        self.telemetryHistory=[];self.telemetryLogRows=[];self.telemetrySampleCounter=0;self.telemetryParseErrors=0
        if hasattr(self,"telemetryTable"):self.telemetryTable.setRowCount(0)
        self.update_telemetry_ui()

    def export_telemetry_csv(self,*_):
        rows=self.telemetryLogRows if self.telemetryLogRows else self.telemetryHistory
        if not rows:
            QMessageBox.information(self,"Telemetry CSV","ยังไม่มีข้อมูลสำหรับ Export");return
        docs=QStandardPaths.writableLocation(QStandardPaths.DocumentsLocation) or str(Path.home())
        default=str(Path(docs)/f"CVET_Telemetry_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv")
        filename,_=QFileDialog.getSaveFileName(self,"Export Telemetry CSV",default,"CSV (*.csv)")
        if not filename:return
        if not filename.lower().endswith(".csv"):filename+=".csv"
        fields=["timestamp","device","transport","source_ip","source_port","seq","uptime_ms","wifi_rssi_dbm",
                "battery_v","battery_pct","battery_a","speed_kmh","tilt_deg","left_rpm","right_rpm",
                "vesc_current_a","rc_throttle","rc_steer","limit_left","limit_right","estop","rc_ok","state"]
        try:
            with open(filename,"w",newline="",encoding="utf-8-sig") as fh:
                writer=csv.DictWriter(fh,fieldnames=fields);writer.writeheader()
                for row in rows:writer.writerow({k:row.get(k,"") for k in fields})
            QMessageBox.information(self,"Telemetry CSV",f"บันทึก {len(rows)} samples แล้ว:\n{filename}")
        except Exception as exc:
            QMessageBox.critical(self,"Telemetry CSV",str(exc))

    def telemetry_esp32_template(self):
        header=self.generate_hardware_header_text() if hasattr(self,"hwRows") else "// Hardware map unavailable"
        interval=max(50,int(1000/max(1,self.telemetryRateHz.value()))) if hasattr(self,"telemetryRateHz") else 100
        return f"""/*
  CVET ESP32 Serial Telemetry Sender
  Generated by Crane Vehicle Engineering Tool V{APP_VERSION}

  Protocol: one JSON object + newline per sample over USB Serial.
  Replace TODO values with real VESC / BNO086 / RC / limit data.
*/

{header}

void setup() {{
  Serial.begin(115200);
}}

void loop() {{
  float battery_v = 72.0;
  float battery_a = 0.0;
  float speed_kmh = 0.0;
  float tilt_deg = 0.0;
  float left_rpm = 0.0;
  float right_rpm = 0.0;
  float vesc_current_a = 0.0;
  float rc_throttle = 0.0;
  float rc_steer = 0.0;
  bool limit_left = false;
  bool limit_right = false;
  bool estop = false;
  bool rc_ok = true;

  Serial.printf(
    "{{\\\"protocol\\\":\\\"CVET1\\\",\\\"device\\\":\\\"CVET-ESP32\\\",\\\"battery_v\\\":%.2f,\\\"battery_a\\\":%.2f,\\\"speed_kmh\\\":%.3f,"
    "\\\"tilt_deg\\\":%.2f,\\\"left_rpm\\\":%.1f,\\\"right_rpm\\\":%.1f,"
    "\\\"vesc_current_a\\\":%.2f,\\\"rc_throttle\\\":%.1f,\\\"rc_steer\\\":%.1f,"
    "\\\"limit_left\\\":%d,\\\"limit_right\\\":%d,\\\"estop\\\":%d,"
    "\\\"rc_ok\\\":%d,\\\"state\\\":\\\"LIVE\\\"}}\\n",
    battery_v,battery_a,speed_kmh,tilt_deg,left_rpm,right_rpm,
    vesc_current_a,rc_throttle,rc_steer,
    limit_left,limit_right,estop,rc_ok
  );

  delay({interval});
}}
"""

    def telemetry_wifi_esp32_template(self):
        header=self.generate_hardware_header_text() if hasattr(self,"hwRows") else "// Hardware map unavailable"
        pc_ip=(self.telemetryLocalIp.currentText().strip() if hasattr(self,"telemetryLocalIp") else "") or "192.168.1.100"
        if pc_ip.startswith("127."):pc_ip="192.168.1.100"
        port=int(self.telemetryUdpPort.value()) if hasattr(self,"telemetryUdpPort") else 4210
        rate=max(1,int(self.telemetryRateHz.value())) if hasattr(self,"telemetryRateHz") else 10
        interval=max(50,int(1000/rate))
        device=(self.telemetryDeviceId.text().strip() if hasattr(self,"telemetryDeviceId") else "CVET-ESP32") or "CVET-ESP32"
        device=re.sub(r"[^A-Za-z0-9_.-]","_",device)[:40]
        return f"""/*
  CVET ESP32 WiFi UDP Telemetry Sender
  Generated by Crane Vehicle Engineering Tool V{APP_VERSION}

  PC destination: {pc_ip}:{port}
  Sender rate: {rate} Hz
  Device ID: {device}

  IMPORTANT:
  - Replace WIFI_SSID / WIFI_PASSWORD.
  - PC and ESP32 must be on the same trusted LAN/WiFi.
  - This sketch SENDS TELEMETRY ONLY. It does not receive drive commands.
  - WiFi reconnect is NON-BLOCKING so loss of WiFi does not freeze the vehicle control loop.
  - Replace TODO values with real VESC / BNO086 / RC / limit data.
*/

#include <WiFi.h>
#include <WiFiUdp.h>

{header}

const char* WIFI_SSID = "YOUR_WIFI_SSID";
const char* WIFI_PASSWORD = "YOUR_WIFI_PASSWORD";
const char* CVET_PC_IP = "{pc_ip}";
const uint16_t CVET_UDP_PORT = {port};
const char* CVET_DEVICE_ID = "{device}";

WiFiUDP cvetUdp;
uint32_t cvetSeq = 0;
unsigned long cvetLastWifiAttempt = 0;
unsigned long cvetLastTelemetrySend = 0;

void startWiFi() {{
  WiFi.mode(WIFI_STA);
  WiFi.begin(WIFI_SSID, WIFI_PASSWORD);
  cvetLastWifiAttempt = millis();
}}

void serviceWiFiNonBlocking() {{
  if (WiFi.status() == WL_CONNECTED) return;
  unsigned long now = millis();
  if (now - cvetLastWifiAttempt >= 5000UL) {{
    cvetLastWifiAttempt = now;
    WiFi.disconnect();
    WiFi.begin(WIFI_SSID, WIFI_PASSWORD);
  }}
}}

void sendTelemetry() {{
  float battery_v = 72.0;       // TODO
  float battery_pct = 100.0;    // TODO
  float battery_a = 0.0;        // TODO
  float speed_kmh = 0.0;        // TODO
  float tilt_deg = 0.0;         // TODO BNO086
  float left_rpm = 0.0;         // TODO VESC/CAN
  float right_rpm = 0.0;
  float vesc_current_a = 0.0;
  float rc_throttle = 0.0;
  float rc_steer = 0.0;
  bool limit_left = false;
  bool limit_right = false;
  bool estop = false;
  bool rc_ok = true;

  char payload[768];
  int n = snprintf(
    payload, sizeof(payload),
    "{{\\\"protocol\\\":\\\"CVET1\\\",\\\"device\\\":\\\"%s\\\",\\\"seq\\\":%lu,\\\"uptime_ms\\\":%lu,"
    "\\\"wifi_rssi_dbm\\\":%ld,\\\"battery_v\\\":%.2f,\\\"battery_pct\\\":%.1f,"
    "\\\"battery_a\\\":%.2f,\\\"speed_kmh\\\":%.3f,\\\"tilt_deg\\\":%.2f,"
    "\\\"left_rpm\\\":%.1f,\\\"right_rpm\\\":%.1f,\\\"vesc_current_a\\\":%.2f,"
    "\\\"rc_throttle\\\":%.1f,\\\"rc_steer\\\":%.1f,\\\"limit_left\\\":%d,"
    "\\\"limit_right\\\":%d,\\\"estop\\\":%d,\\\"rc_ok\\\":%d,"
    "\\\"state\\\":\\\"LIVE\\\"}}",
    CVET_DEVICE_ID,(unsigned long)cvetSeq++,(unsigned long)millis(),(long)WiFi.RSSI(),
    battery_v,battery_pct,battery_a,speed_kmh,tilt_deg,left_rpm,right_rpm,
    vesc_current_a,rc_throttle,rc_steer,
    limit_left,limit_right,estop,rc_ok
  );

  if (n > 0 && n < (int)sizeof(payload)) {{
    cvetUdp.beginPacket(CVET_PC_IP, CVET_UDP_PORT);
    cvetUdp.write((const uint8_t*)payload, (size_t)n);
    cvetUdp.endPacket();
  }}
}}

void setup() {{
  Serial.begin(115200);
  startWiFi();
}}

void loop() {{
  // Keep safety/control logic running regardless of WiFi status.
  // TODO: runVehicleSafetyAndControl();

  serviceWiFiNonBlocking();

  unsigned long now = millis();
  if (WiFi.status() == WL_CONNECTED && now - cvetLastTelemetrySend >= {interval}UL) {{
    cvetLastTelemetrySend = now;
    sendTelemetry();
  }}

  // No blocking wait for WiFi here.
  delay(1);
}}
"""

    def current_telemetry_esp32_template(self):
        return self.telemetry_wifi_esp32_template() if hasattr(self,"telemetrySource") and self.telemetrySource.currentIndex()==2 else self.telemetry_esp32_template()

    def copy_telemetry_esp32_template(self,*_):
        QApplication.clipboard().setText(self.current_telemetry_esp32_template())
        mode="WiFi UDP" if self.telemetrySource.currentIndex()==2 else "Serial"
        self.statusBar().showMessage(f"คัดลอก ESP32 {mode} Telemetry template แล้ว",3000)

    def export_telemetry_esp32_template(self,*_):
        docs=QStandardPaths.writableLocation(QStandardPaths.DocumentsLocation) or str(Path.home())
        wifi=hasattr(self,"telemetrySource") and self.telemetrySource.currentIndex()==2
        default=str(Path(docs)/("CVET_ESP32_WiFi_Telemetry.ino" if wifi else "CVET_ESP32_Serial_Telemetry.ino"))
        filename,_=QFileDialog.getSaveFileName(self,"Export ESP32 Telemetry Template",default,"Arduino Sketch (*.ino);;Text (*.txt)")
        if not filename:return
        if not Path(filename).suffix:filename+=".ino"
        try:
            Path(filename).write_text(self.current_telemetry_esp32_template(),encoding="utf-8")
            QMessageBox.information(self,"ESP32 Telemetry","บันทึก Template แล้ว:\n"+filename)
        except Exception as exc:
            QMessageBox.critical(self,"ESP32 Telemetry",str(exc))

    def make_system_flowchart_page(self):
        w=QWidget();self.flowchartPage=w
        root=QVBoxLayout(w);root.setContentsMargins(12,10,12,12);root.setSpacing(8)
        root.addWidget(make_page_header(
            "FLOWCHART FINAL — VEHICLE + CRANE CONTROL",
            "อ้างอิง Flowchart Final • Remote → IMU/Limits/VESC → Drive Interlock → 0.5 s Stop Gate → Crane Limits",
            self.show_home_mode,"V53.2.4 FLOW","#e8f4ff","#245fbb"
        ))

        toolbar=QFrame();toolbar.setObjectName("softPanel")
        tl=QGridLayout(toolbar);tl.setContentsMargins(10,8,10,8);tl.setHorizontalSpacing(8);tl.setVerticalSpacing(7)
        tl.addWidget(QLabel("Scenario"),0,0)
        self.flowScenario=QComboBox();self.flowScenario.addItems([
            "Drive Forward","Idle / Ready","Crane LEFT","Crane RIGHT",
            "Remote Fault","Motor / VESC Fault","Tilt Warning","Vehicle Still Moving",
            "Stopped < 0.5 s","LEFT Limit Active","RIGHT Limit Active"
        ])
        self.flowScenario.currentIndexChanged.connect(self.set_flowchart_scenario)
        tl.addWidget(self.flowScenario,0,1,1,3)
        sync=QPushButton("Sync from Control Logic");sync.clicked.connect(self.sync_flowchart_from_safety);tl.addWidget(sync,0,4)
        exp=QPushButton("Export PNG");exp.clicked.connect(self.export_flowchart_png);tl.addWidget(exp,0,5)

        prev=QPushButton("◀ Prev");prev.clicked.connect(self.flowchart_prev_step);tl.addWidget(prev,1,0)
        nxt=QPushButton("Next ▶");nxt.clicked.connect(self.flowchart_next_step);tl.addWidget(nxt,1,1)
        self.flowPlayButton=QPushButton("▶ Play");self.flowPlayButton.setObjectName("primaryButton");self.flowPlayButton.clicked.connect(self.toggle_flowchart_play);tl.addWidget(self.flowPlayButton,1,2)
        tl.addWidget(QLabel("Zoom"),1,3)
        self.flowZoom=QComboBox();self.flowZoom.setEditable(True);self.flowZoom.addItems(["70%","80%","90%","100%","110%","120%"])
        self.flowZoom.setCurrentText("90%");self.flowZoom.currentTextChanged.connect(self.set_flowchart_zoom);tl.addWidget(self.flowZoom,1,4)
        fit=QPushButton("Fit Width");fit.clicked.connect(self.fit_flowchart_width);tl.addWidget(fit,1,5)
        resetFlow=QPushButton("100%");resetFlow.setToolTip("Reset Flowchart zoom to 100%");resetFlow.clicked.connect(lambda:self.flowZoom.setCurrentText("100%"));tl.addWidget(resetFlow,1,6)
        tl.setColumnStretch(1,1);tl.setColumnStretch(2,1);tl.setColumnStretch(4,2);tl.setColumnStretch(6,0)
        root.addWidget(toolbar)

        self.flowStepLabel=QLabel("Step 1")
        self.flowStepLabel.setWordWrap(True)
        self.flowStepLabel.setStyleSheet("font-size:10.5pt;font-weight:900;color:#245fbb;padding:4px 6px;background:#f5f9ff;border-radius:6px;")
        root.addWidget(self.flowStepLabel)

        self.flowTabs=QTabWidget();self.flowTabs.setUsesScrollButtons(True);root.addWidget(self.flowTabs,1)

        flowPage=QWidget();fl=QVBoxLayout(flowPage);fl.setContentsMargins(0,0,0,0)
        self.flowScroll=QScrollArea()
        self.flowScroll.setWidgetResizable(False)
        self.flowScroll.setFrameShape(QFrame.NoFrame)
        self.flowScroll.setStyleSheet("QScrollArea{background:#ffffff;} QScrollArea>QWidget>QWidget{background:#ffffff;}")
        self.flowScroll.setAlignment(Qt.AlignHCenter|Qt.AlignTop)
        self.flowScroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.flowScroll.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.flowBoard=SystemFlowchartWidget(self)
        self.flowScroll.setWidget(self.flowBoard)
        fl.addWidget(self.flowScroll)
        self.flowTabs.addTab(flowPage,"Flowchart")

        explainPage=QWidget();el=QVBoxLayout(explainPage);el.setContentsMargins(8,8,8,8)
        note=QLabel("คำอธิบายหน้านี้อ้างอิง Flowchart Final ที่ส่งมา: Tilt เป็น Warning only และรถต้องหยุดนิ่ง ≥0.5 s ก่อนหมุนเครน")
        note.setWordWrap(True);note.setStyleSheet("background:#fff8e9;color:#68420b;padding:9px;border:1px solid #ead39a;border-radius:8px;font-weight:700;")
        el.addWidget(note)
        self.flowExplanation=QTextEdit();self.flowExplanation.setReadOnly(True);el.addWidget(self.flowExplanation,1)
        self.flowTabs.addTab(explainPage,"คำอธิบาย / Explanation")

        self.flowPlayTimer=QTimer(self);self.flowPlayTimer.timeout.connect(self.flowchart_next_step)
        self.flowStep=0
        self.set_flowchart_zoom("90%")
        self.set_flowchart_scenario()
        QTimer.singleShot(0,self.fit_flowchart_width)
        self.tabs.addTab(w,"")

    def setup_navigation_dock(self):
        self.navButtons={}
        dock=QDockWidget("",self);self.navDock=dock
        dock.setAllowedAreas(Qt.LeftDockWidgetArea)
        dock.setFeatures(QDockWidget.NoDockWidgetFeatures)
        dock.setFixedWidth(225)
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
        lay.addWidget(self._make_nav_button("hardware","H   Hardware I/O",self.show_hardware_mode))
        lay.addWidget(self._make_nav_button("telemetry","D   WiFi / Live Telemetry",self.show_telemetry_mode))
        lay.addWidget(self._make_nav_button("integration","I   Engineering Suite",self.show_integration_suite_mode))

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


    # =====================================================================
    # V52 HARDWARE I/O & WIRING MANAGER
    # =====================================================================
    def _hardware_defs(self):
        return [
            dict(key="IBUS_RX",device="FlySky RC Receiver",signal="iBUS OUT",interface="UART RX",
                 supply="5V",logic="5V",gpio="",protection="Level Shifter / Divider",
                 allowed_supply=("5V",),note="Receiver supply 5 V; verify iBUS signal level before ESP32."),
            dict(key="CAN_TX",device="SN65HVD230",signal="TXD",interface="CAN TX",
                 supply="3.3V",logic="3.3V",gpio="",protection="CAN Transceiver",
                 allowed_supply=("3.3V",),note="ESP32 logic side of CAN transceiver."),
            dict(key="CAN_RX",device="SN65HVD230",signal="RXD",interface="CAN RX",
                 supply="3.3V",logic="3.3V",gpio="",protection="CAN Transceiver",
                 allowed_supply=("3.3V",),note="ESP32 logic side of CAN transceiver."),
            dict(key="I2C_SDA",device="BNO086 IMU",signal="SDA",interface="I2C SDA",
                 supply="3.3V",logic="3.3V",gpio="",protection="Direct",
                 allowed_supply=("3.3V","5V"),note="Breakout-board supply capability must be verified from its datasheet."),
            dict(key="I2C_SCL",device="BNO086 IMU",signal="SCL",interface="I2C SCL",
                 supply="3.3V",logic="3.3V",gpio="",protection="Direct",
                 allowed_supply=("3.3V","5V"),note="Breakout-board supply capability must be verified from its datasheet."),
            dict(key="LIMIT_LEFT",device="OMRON D4N-112G + PC817",signal="Left limit -90°",interface="Digital IN",
                 supply="5V",logic="3.3V",gpio="",protection="PC817 Isolation",
                 allowed_supply=("3.3V","5V","12V"),note="ESP32 side must remain 3.3 V after isolation/pull-up."),
            dict(key="LIMIT_RIGHT",device="OMRON D4N-112G + PC817",signal="Right limit +90°",interface="Digital IN",
                 supply="5V",logic="3.3V",gpio="",protection="PC817 Isolation",
                 allowed_supply=("3.3V","5V","12V"),note="ESP32 side must remain 3.3 V after isolation/pull-up."),
            dict(key="BUZZER",device="5 V Buzzer + MOSFET",signal="Buzzer command",interface="Digital OUT",
                 supply="5V",logic="3.3V",gpio="",protection="MOSFET / Driver",
                 allowed_supply=("5V",),note="Do not drive a high-current buzzer directly from GPIO."),
            dict(key="LED",device="Status LED / Lamp",signal="LED command",interface="Digital OUT",
                 supply="5V",logic="3.3V",gpio="",protection="MOSFET / Driver",
                 allowed_supply=("3.3V","5V"),note="Use resistor/driver appropriate to the actual indicator."),
        ]

    def _gpio_items(self):
        data=self.gpio_profile_data() if hasattr(self,"hwBoardProfile") else {"pins":list(range(0,49))}
        return ["Not assigned"]+[f"GPIO {i}" for i in data.get("pins",[])]


    def gpio_profile_data(self):
        idx=self.hwBoardProfile.currentIndex() if hasattr(self,"hwBoardProfile") else 0
        s3pins=list(range(0,22))+list(range(26,49))
        if idx==3:
            pins=list(range(0,20))+[21,22,23,25,26,27]+list(range(32,40))
            info={p:{"status":"FREE","function":"Available GPIO","note":""} for p in pins}
            for p in (34,35,36,39):info[p]={"status":"CAUTION","function":"Input only","note":"Classic ESP32 input-only GPIO"}
            for p in (0,2,5,12,15):info[p]={"status":"CAUTION","function":"Boot / strapping","note":"Use with boot-state care"}
            info[1]={"status":"SHARED","function":"UART0 TX","note":"Serial/programming"}
            info[3]={"status":"SHARED","function":"UART0 RX","note":"Serial/programming"}
            return dict(name="ESP32 DevKit V1 / ESP-WROOM-32",module="ESP-WROOM-32",pins=pins,pin_info=info,
                        layout="portrait",profile="classic",source="Espressif ESP32 GPIO summary")
        if idx==1:
            info={p:{"status":"CAUTION","function":"Not exposed / verify","note":"Not a general external header pin on this board"} for p in s3pins}
            lcd={0:"LCD G3",1:"LCD R3",2:"LCD R4",3:"LCD VSYNC",5:"LCD DE",7:"LCD PCLK",10:"LCD B7",
                 14:"LCD B3",17:"LCD B6",18:"LCD B5",21:"LCD G7",38:"LCD B4",39:"LCD G2",40:"LCD R7",
                 41:"LCD R6",42:"LCD R5",45:"LCD G4",46:"LCD HSYNC",47:"LCD G6",48:"LCD G5"}
            for p,fn in lcd.items():info[p]={"status":"BOARD","function":fn,"note":"Used by onboard RGB LCD"}
            info[4]={"status":"BOARD","function":"Touch IRQ","note":"GT911 touch interrupt"}
            info[8]={"status":"SHARED","function":"I2C SDA / Touch","note":"Exposed I2C header; shared with touch and IO extension"}
            info[9]={"status":"SHARED","function":"I2C SCL / Touch","note":"Exposed I2C header; shared with touch and IO extension"}
            for p,fn in ((11,"TF MOSI"),(12,"TF SCK"),(13,"TF MISO")):info[p]={"status":"BOARD","function":fn,"note":"Used by TF/microSD"}
            info[15]={"status":"BOARD","function":"RS485 UART RX","note":"Connected to onboard RS485 transceiver"}
            info[16]={"status":"BOARD","function":"RS485 UART TX","note":"Connected to onboard RS485 transceiver"}
            info[19]={"status":"SHARED","function":"CAN RX / USB D-","note":"Board mux selects CAN or USB"}
            info[20]={"status":"SHARED","function":"CAN TX / USB D+","note":"Board mux selects CAN or USB"}
            info[43]={"status":"SHARED","function":"UART0 TX","note":"UART header / USB-UART selected by switch"}
            info[44]={"status":"SHARED","function":"UART0 RX","note":"UART header / USB-UART selected by switch"}
            info[6]={"status":"FREE","function":"GP6 external GPIO","note":"Dedicated GPIO header; best general-purpose external pin"}
            for p in range(26,38):
                info[p]={"status":"MEMORY","function":"Flash / PSRAM module","note":"Not for project GPIO on N16R8 module"}
            return dict(name="Waveshare ESP32-S3-Touch-LCD-7B",module="ESP32-S3-WROOM-1\nN16R8",pins=s3pins,pin_info=info,
                        layout="landscape",profile="waveshare7b",
                        source="Waveshare 7B official interface map + Espressif S3 GPIO summary",
                        exposed={6,8,9,43,44,19,20})
        info={p:{"status":"FREE","function":"Available GPIO","note":""} for p in s3pins}
        for p in (0,3,45,46):info[p]={"status":"CAUTION","function":"Strapping pin","note":"Boot-state sensitive"}
        info[19]={"status":"SHARED","function":"USB-JTAG D-","note":"USB-JTAG by default"}
        info[20]={"status":"SHARED","function":"USB-JTAG D+","note":"USB-JTAG by default"}
        for p in range(26,33):info[p]={"status":"MEMORY","function":"Flash / PSRAM dependent","note":"Usually memory-related on S3 modules"}
        for p in range(33,38):info[p]={"status":"CAUTION","function":"PSRAM dependent","note":"May be used by octal PSRAM depending on module"}
        return dict(name=("Generic ESP32-S3" if idx==0 else "Custom ESP32-S3"),
                    module="ESP32-S3",pins=s3pins,pin_info=info,layout="portrait",
                    profile=("generic_s3" if idx==0 else "custom_s3"),
                    source="Espressif ESP32-S3 GPIO summary")

    def _profile_compatible_pin(self,key,pin,row=None):
        data=self.gpio_profile_data();profile=data.get("profile")
        if profile=="waveshare7b":
            compatible={"I2C_SDA":8,"I2C_SCL":9,"CAN_RX":19,"CAN_TX":20,"IBUS_RX":44}
            if key in compatible:return compatible[key]==pin
            if row and row.get("custom",False):
                iface=str(row.get("interface",""))
                if pin in (8,9) and iface in ("I2C SDA","I2C SCL"):return (pin==8 and iface=="I2C SDA") or (pin==9 and iface=="I2C SCL")
                if pin==43 and iface=="UART TX":return True
                if pin==44 and iface=="UART RX":return True
                if pin==19 and iface=="CAN RX":return True
                if pin==20 and iface=="CAN TX":return True
                if pin==6:return True
                return False
            return key in ("LIMIT_LEFT","LIMIT_RIGHT","BUZZER","LED") and pin==6
        return True

    def refresh_gpio_combo_items(self):
        if not hasattr(self,"hwRows"):return
        items=self._gpio_items();valid={x for x in items}
        for row in self.hwRows:
            combo=row["gpio"];old=combo.currentText()
            block=combo.blockSignals(True);combo.clear();combo.addItems(items)
            combo.setCurrentText(old if old in valid else "Not assigned");combo.blockSignals(block)

    def hardware_pin_snapshot(self):
        data=self.gpio_profile_data();snap={p:dict(data.get("pin_info",{}).get(p,{"status":"FREE","function":"Available","note":""}),users=[]) for p in data.get("pins",[])}
        manual=self._manual_reserved_gpio_set() if hasattr(self,"hwReservedPins") else set()
        for p in manual:
            if p in snap:snap[p].update(status="CAUTION",function="Manual reserved",note="Reserved by user")
        if hasattr(self,"hwRows"):
            used={}
            for row in self.hwRows:
                if not row["enabled"].isChecked():continue
                txt=row["gpio"].currentText()
                if txt=="Not assigned":continue
                m=re.search(r"\d+",txt)
                if not m:continue
                pin=int(m.group());used.setdefault(pin,[]).append(row["key"])
            for pin,users in used.items():
                if pin not in snap:
                    snap[pin]={"status":"INVALID","function":"Invalid for profile","note":"","users":users}
                    continue
                base=snap[pin]["status"]
                if len(users)>1:
                    snap[pin].update(status="CONFLICT",function="GPIO conflict",users=users)
                elif base in ("BOARD","MEMORY") or (base in ("CAUTION","SHARED") and not self._profile_compatible_pin(users[0],pin,next((r for r in self.hwRows if r["key"]==users[0]),None))):
                    snap[pin].update(status="CONFLICT",function=f"{snap[pin]['function']} / {users[0]}",users=users)
                else:
                    snap[pin].update(status="USED",function=users[0],users=users)
        return snap

    def gpio_profile_summary(self):
        data=self.gpio_profile_data();snap=self.hardware_pin_snapshot()
        counts={k:0 for k in ("USED","FREE","BOARD","SHARED","CAUTION","MEMORY","CONFLICT","INVALID")}
        for x in snap.values():counts[x.get("status","FREE")]=counts.get(x.get("status","FREE"),0)+1
        return data,counts,snap

    def on_board_pin_clicked(self,pin):
        data,counts,snap=self.gpio_profile_summary();info=snap.get(pin,{})
        users=info.get("users",[])
        self.hwBoardPinInfo.setHtml(
            f"<h2>GPIO{pin}</h2>"
            f"<p><b>Status:</b> {info.get('status','—')}</p>"
            f"<p><b>Board function:</b> {info.get('function','—')}</p>"
            f"<p><b>Project assignment:</b> {', '.join(users) if users else 'None'}</p>"
            f"<p><b>Note:</b> {info.get('note','')}</p>"
            f"<p><b>Profile:</b> {data.get('name')}</p>"
        )
        # Select corresponding Device Manager row when this GPIO is assigned.
        if users and hasattr(self,"hwTable"):
            for i,row in enumerate(self.hwRows):
                if row["key"] in users:self.hwTable.selectRow(i);break

    def on_hardware_profile_changed(self,*_):
        self.refresh_gpio_combo_items()
        if hasattr(self,"hwBoardVerified"):self.hwBoardVerified.setChecked(False)
        self.update_hardware_manager()

    def _hardware_interface_items(self):
        return ["Digital IN","Digital OUT","ADC IN","PWM OUT","UART RX","UART TX",
                "I2C SDA","I2C SCL","CAN RX","CAN TX","SPI MISO","SPI MOSI","SPI SCK",
                "Interrupt IN","Other"]

    def _hardware_supply_items(self):
        return ["3.3V","5V","12V","24V","72V","External / Other"]

    def _hardware_logic_items(self):
        return ["3.3V","5V","12V","24V","72V","Isolated / Other"]

    def _hardware_protection_items(self):
        return ["Direct","Level Shifter / Divider","PC817 Isolation","MOSFET / Driver",
                "CAN Transceiver","Optocoupler / Isolator","Relay / Contactor","Other"]

    @staticmethod
    def _hardware_key(text,existing=None):
        key=re.sub(r"[^A-Za-z0-9]+","_",str(text).upper()).strip("_") or "CUSTOM_IO"
        existing=set(existing or [])
        base=key;i=2
        while key in existing:
            key=f"{base}_{i}";i+=1
        return key

    def _append_hardware_row(self,d,select=False):
        r=self.hwTable.rowCount();self.hwTable.insertRow(r)
        en=QCheckBox();en.setChecked(bool(d.get("enabled",True)))
        ec=QWidget();el=QHBoxLayout(ec);el.setContentsMargins(0,0,0,0);el.setAlignment(Qt.AlignCenter);el.addWidget(en)
        self.hwTable.setCellWidget(r,0,ec)
        for c,key in ((1,"device"),(2,"signal"),(3,"interface")):
            item=QTableWidgetItem(str(d.get(key,"")))
            if d.get("custom"):item.setToolTip("Custom I/O — ดับเบิลคลิก Edit Selected เพื่อแก้ข้อมูล")
            self.hwTable.setItem(r,c,item)

        supply=QComboBox();supply.addItems(self._hardware_supply_items())
        if supply.findText(str(d.get("supply","3.3V")))<0:supply.addItem(str(d.get("supply")))
        supply.setCurrentText(str(d.get("supply","3.3V")));self.hwTable.setCellWidget(r,4,supply)

        logic=QComboBox();logic.addItems(self._hardware_logic_items())
        if logic.findText(str(d.get("logic","3.3V")))<0:logic.addItem(str(d.get("logic")))
        logic.setCurrentText(str(d.get("logic","3.3V")));self.hwTable.setCellWidget(r,5,logic)

        gpio=QComboBox();gpio.addItems(self._gpio_items())
        gpio_text=str(d.get("gpio","Not assigned") or "Not assigned")
        gpio.setCurrentText(gpio_text if gpio.findText(gpio_text)>=0 else "Not assigned")
        self.hwTable.setCellWidget(r,6,gpio)

        prot=QComboBox();prot.addItems(self._hardware_protection_items())
        if prot.findText(str(d.get("protection","Direct"))) < 0:prot.addItem(str(d.get("protection")))
        prot.setCurrentText(str(d.get("protection","Direct")));self.hwTable.setCellWidget(r,7,prot)

        st=QLabel("CHECK");st.setAlignment(Qt.AlignCenter);self.hwTable.setCellWidget(r,8,st)
        row=dict(d)
        row.setdefault("allowed_supply",tuple(self._hardware_supply_items()) if d.get("custom") else (str(d.get("supply","3.3V")),))
        row.setdefault("note","")
        row["custom"]=bool(d.get("custom",False))
        row.update(enabled=en,supply=supply,logic=logic,gpio=gpio,protection=prot,status=st)
        self.hwRows.append(row)

        en.stateChanged.connect(self.update_hardware_manager)
        supply.currentIndexChanged.connect(self.update_hardware_manager)
        logic.currentIndexChanged.connect(self.update_hardware_manager)
        gpio.currentIndexChanged.connect(self.update_hardware_manager)
        prot.currentIndexChanged.connect(self.update_hardware_manager)

        # Custom-row values live in dictionaries, so connect them explicitly to autosave if available.
        if hasattr(self,"easyAutosaveTimer"):
            for sig in (en.toggled,supply.currentIndexChanged,logic.currentIndexChanged,gpio.currentIndexChanged,prot.currentIndexChanged):
                try:sig.connect(self.schedule_easy_autosave)
                except Exception:pass

        if select:
            self.hwTable.selectRow(r);self.hwTable.scrollToItem(self.hwTable.item(r,1))
        return row

    def _selected_hardware_row(self):
        if not hasattr(self,"hwTable"):return None,None
        r=self.hwTable.currentRow()
        if r<0 or r>=len(self.hwRows):return None,None
        return r,self.hwRows[r]

    def _hardware_io_dialog(self,title,row=None):
        dlg=QDialog(self);dlg.setWindowTitle(title);dlg.resize(570,610)
        root=QVBoxLayout(dlg)
        info=QLabel("เพิ่ม Input/Output ใหม่แล้วระบบจะนำไปตรวจ GPIO, Voltage, Conflict, Board Animation และ Generate ESP32 Pin Map ให้อัตโนมัติ")
        info.setWordWrap(True);info.setStyleSheet("background:#eef6ff;color:#274c77;padding:10px;border:1px solid #cfe2f5;border-radius:8px;")
        root.addWidget(info)
        form=QFormLayout();form.setLabelAlignment(Qt.AlignRight);form.setVerticalSpacing(9)
        device=QLineEdit();device.setPlaceholderText("เช่น Proximity Sensor, Relay Board, Encoder")
        signal=QLineEdit();signal.setPlaceholderText("เช่น SENSOR_IN, RELAY_ENABLE, ENCODER_A")
        interface=QComboBox();interface.addItems(self._hardware_interface_items())
        supply=QComboBox();supply.addItems(self._hardware_supply_items())
        logic=QComboBox();logic.addItems(self._hardware_logic_items())
        gpio=QComboBox();gpio.addItems(self._gpio_items())
        protection=QComboBox();protection.addItems(self._hardware_protection_items())
        note=QPlainTextEdit();note.setPlaceholderText("หมายเหตุ เช่น Active LOW, ต้อง Pull-up 10k, ผ่าน Optocoupler");note.setMaximumHeight(100)

        if row:
            device.setText(str(row.get("device","")));signal.setText(str(row.get("signal","")))
            interface.setCurrentText(str(row.get("interface","Digital IN")))
            supply.setCurrentText(row["supply"].currentText() if hasattr(row.get("supply"),"currentText") else str(row.get("supply","3.3V")))
            logic.setCurrentText(row["logic"].currentText() if hasattr(row.get("logic"),"currentText") else str(row.get("logic","3.3V")))
            gpio.setCurrentText(row["gpio"].currentText() if hasattr(row.get("gpio"),"currentText") else str(row.get("gpio","Not assigned")))
            protection.setCurrentText(row["protection"].currentText() if hasattr(row.get("protection"),"currentText") else str(row.get("protection","Direct")))
            note.setPlainText(str(row.get("note","")))
        else:
            interface.setCurrentText("Digital IN");supply.setCurrentText("5V");logic.setCurrentText("3.3V")
            protection.setCurrentText("Direct");gpio.setCurrentText("Not assigned")

        form.addRow("Device / อุปกรณ์",device)
        form.addRow("Signal / ชื่อ Input-Output",signal)
        form.addRow("Interface",interface)
        form.addRow("Device supply",supply)
        form.addRow("Signal logic to ESP32",logic)
        form.addRow("ESP32 GPIO",gpio)
        form.addRow("Protection / Driver",protection)
        form.addRow("Note",note)
        root.addLayout(form)

        hint=QLabel("ตัวอย่าง: Sensor 12V + Digital IN → Logic 3.3V + Optocoupler/Divider ก่อนเข้า ESP32. ห้ามเอา 12V เข้า GPIO โดยตรง")
        hint.setWordWrap(True);hint.setStyleSheet("color:#8a4b08;background:#fff8e9;padding:9px;border:1px solid #ead39a;border-radius:8px")
        root.addWidget(hint)

        buttons=QDialogButtonBox(QDialogButtonBox.Save|QDialogButtonBox.Cancel)
        buttons.accepted.connect(dlg.accept);buttons.rejected.connect(dlg.reject);root.addWidget(buttons)

        if dlg.exec()!=QDialog.Accepted:return None
        if not device.text().strip() or not signal.text().strip():
            QMessageBox.warning(self,"Add Hardware I/O","กรุณากรอกชื่ออุปกรณ์และชื่อ Signal")
            return self._hardware_io_dialog(title,row)

        existing=[x["key"] for x in self.hwRows if x is not row]
        key=row.get("key") if row and not row.get("custom",False) else self._hardware_key(signal.text().strip(),existing)
        return dict(key=key,device=device.text().strip(),signal=signal.text().strip(),
                    interface=interface.currentText(),supply=supply.currentText(),logic=logic.currentText(),
                    gpio=gpio.currentText(),protection=protection.currentText(),note=note.toPlainText().strip(),
                    allowed_supply=tuple(self._hardware_supply_items()),custom=True,enabled=True)

    def add_custom_hardware_io(self):
        data=self._hardware_io_dialog("Add New Device / Input / Output")
        if not data:return
        self._append_hardware_row(data,select=True)
        self.update_hardware_manager()
        self.schedule_easy_autosave() if hasattr(self,"easyAutosaveTimer") else None
        self.statusBar().showMessage(f"เพิ่ม {data['device']} / {data['signal']} แล้ว",3500)

    def edit_selected_hardware_io(self):
        r,row=self._selected_hardware_row()
        if row is None:
            QMessageBox.information(self,"Edit Hardware I/O","เลือกแถวที่ต้องการแก้ก่อน")
            return
        if not row.get("custom",False):
            QMessageBox.information(self,"Edit Hardware I/O","รายการมาตรฐานแก้ชื่อ/Interface ไม่ได้ แต่สามารถเปลี่ยน Supply, Logic, GPIO และ Protection ได้จากตาราง\nถ้าต้องการรายการใหม่ให้กด Add New I/O")
            return
        data=self._hardware_io_dialog("Edit Custom Device / I/O",row)
        if not data:return
        # Keep the existing key stable so project mappings remain compatible.
        data["key"]=row["key"]
        row.update({k:v for k,v in data.items() if k not in ("supply","logic","gpio","protection")})
        self.hwTable.item(r,1).setText(data["device"]);self.hwTable.item(r,2).setText(data["signal"]);self.hwTable.item(r,3).setText(data["interface"])
        row["supply"].setCurrentText(data["supply"]);row["logic"].setCurrentText(data["logic"])
        row["gpio"].setCurrentText(data["gpio"]);row["protection"].setCurrentText(data["protection"])
        self.update_hardware_manager()
        self.schedule_easy_autosave() if hasattr(self,"easyAutosaveTimer") else None

    def duplicate_selected_hardware_io(self):
        r,row=self._selected_hardware_row()
        if row is None:
            QMessageBox.information(self,"Duplicate Hardware I/O","เลือกแถวก่อน")
            return
        existing=[x["key"] for x in self.hwRows]
        data=dict(key=self._hardware_key(str(row.get("signal","IO"))+"_COPY",existing),
                  device=str(row.get("device","Custom Device")),
                  signal=str(row.get("signal","IO"))+"_COPY",
                  interface=str(row.get("interface","Digital IN")),
                  supply=row["supply"].currentText(),logic=row["logic"].currentText(),
                  gpio="Not assigned",protection=row["protection"].currentText(),
                  note=str(row.get("note","")),allowed_supply=tuple(self._hardware_supply_items()),
                  custom=True,enabled=row["enabled"].isChecked())
        self._append_hardware_row(data,select=True);self.update_hardware_manager()
        self.schedule_easy_autosave() if hasattr(self,"easyAutosaveTimer") else None

    def delete_selected_hardware_io(self):
        r,row=self._selected_hardware_row()
        if row is None:
            QMessageBox.information(self,"Delete Hardware I/O","เลือกแถวที่ต้องการลบก่อน")
            return
        if not row.get("custom",False):
            QMessageBox.information(self,"Delete Hardware I/O","รายการมาตรฐานลบไม่ได้ — หากไม่ใช้ให้เอาเครื่องหมาย Use ออก")
            return
        if QMessageBox.question(self,"Delete Hardware I/O",f"ลบ {row.get('device')} / {row.get('signal')} ?",QMessageBox.Yes|QMessageBox.No,QMessageBox.No)!=QMessageBox.Yes:
            return
        self.hwTable.removeRow(r);self.hwRows.pop(r);self.update_hardware_manager()
        self.schedule_easy_autosave() if hasattr(self,"easyAutosaveTimer") else None

    def _make_hw_status_card(self,title):
        box=QFrame();box.setObjectName("metricPanel");box.setMinimumHeight(82)
        lay=QVBoxLayout(box);lay.setContentsMargins(12,9,12,9);lay.setSpacing(3)
        t=QLabel(title);t.setStyleSheet("color:#60758b;font-size:8.8pt;font-weight:900;")
        v=QLabel("—");v.setStyleSheet("color:#17324d;font-size:15pt;font-weight:900;")
        lay.addWidget(t);lay.addWidget(v)
        return box,v

    def make_hardware_io_manager(self):
        w=QWidget();self.hardwarePage=w
        root=QVBoxLayout(w);root.setContentsMargins(12,10,12,12);root.setSpacing(9)
        root.addWidget(make_page_header(
            "ESP32 / VESC HARDWARE I/O MANAGER",
            "ESP32 GPIO • VESC CAN • Voltage/Protection • Wiring • Pin Map",
            self.show_home_mode,"V53.2.4 ESP32 I/O","#e4fbf5","#08705e"
        ))

        cfg=QFrame();cfg.setObjectName("softPanel")
        cl=QGridLayout(cfg);cl.setContentsMargins(14,10,14,10);cl.setHorizontalSpacing(10);cl.setVerticalSpacing(7)
        cl.addWidget(QLabel("ESP32 board profile"),0,0)
        self.hwBoardProfile=QComboBox()
        self.hwBoardProfile.addItems([
            "Generic ESP32-S3 — 45 physical GPIO",
            "Waveshare ESP32-S3-Touch-LCD-7B — Project board",
            "Custom / Other ESP32-S3",
            "ESP32 DevKit V1 / ESP-WROOM-32 — PROJECT ESP32",
        ])
        self.hwBoardProfile.setCurrentIndex(3)  # V52.6 project default: classic ESP32
        cl.addWidget(self.hwBoardProfile,0,1)
        cl.addWidget(QLabel("Reserved GPIOs"),0,2)
        self.hwReservedPins=QLineEdit()
        self.hwReservedPins.setPlaceholderText("Manual reserve เพิ่มเติม เช่น 0, 2, 5 — โปรแกรมตรวจตาม Board Profile ให้อัตโนมัติ")
        cl.addWidget(self.hwReservedPins,0,3)
        self.hwBoardVerified=QCheckBox("ฉันตรวจ GPIO กับ pinout/datasheet ของบอร์ดจริงแล้ว")
        cl.addWidget(self.hwBoardVerified,1,0,1,2)
        bSuggest=QPushButton("Apply Suggested Map");bSuggest.setObjectName("primaryButton");bSuggest.clicked.connect(self.apply_suggested_hardware_map)
        bClear=QPushButton("Clear GPIO");bClear.clicked.connect(self.clear_hardware_gpio)
        cl.addWidget(bSuggest,1,2);cl.addWidget(bClear,1,3)
        cl.setColumnStretch(1,1);cl.setColumnStretch(3,2)
        root.addWidget(cfg)

        status=QGridLayout();status.setHorizontalSpacing(10)
        c1,self.hwConflictLabel=self._make_hw_status_card("GPIO CONFLICT")
        c2,self.hwVoltageLabel=self._make_hw_status_card("VOLTAGE ERROR")
        c3,self.hwMissingLabel=self._make_hw_status_card("MISSING PIN")
        c4,self.hwProtectionLabel=self._make_hw_status_card("PROTECTION")
        c5,self.hwReadyLabel=self._make_hw_status_card("READY FOR CODE")
        for i,c in enumerate((c1,c2,c3,c4,c5)):status.addWidget(c,0,i)
        root.addLayout(status)

        self.hwTabs=QTabWidget();root.addWidget(self.hwTabs,1)

        boardPage=QWidget();boardLayout=QVBoxLayout(boardPage);boardLayout.setContentsMargins(6,6,6,6);boardLayout.setSpacing(6)
        boardToolbar=QHBoxLayout()
        self.hwAnimateCheck=QCheckBox("Animate used GPIO");self.hwAnimateCheck.setChecked(True)
        self.hwAnimateCheck.toggled.connect(lambda on:self.hwBoardView.set_animation_enabled(on) if hasattr(self,"hwBoardView") else None)
        self.hwBoardCountLabel=QLabel("GPIO —")
        self.hwBoardCountLabel.setStyleSheet("font-weight:900;color:#174a74;")
        boardToolbar.addWidget(self.hwAnimateCheck);boardToolbar.addStretch(1);boardToolbar.addWidget(self.hwBoardCountLabel)
        boardLayout.addLayout(boardToolbar)

        # Splitter keeps the board and detail panel independent. The board itself lives
        # on a fixed canvas inside a scroll area, so resizing the window cannot distort it.
        self.hwBoardSplitter=QSplitter(Qt.Horizontal)
        self.hwBoardSplitter.setChildrenCollapsible(False)

        leftWrap=QWidget();leftLay=QVBoxLayout(leftWrap);leftLay.setContentsMargins(0,0,0,0)
        self.hwBoardScroll=QScrollArea()
        self.hwBoardScroll.setWidgetResizable(False)
        self.hwBoardScroll.setFrameShape(QFrame.NoFrame)
        self.hwBoardScroll.setAlignment(Qt.AlignHCenter|Qt.AlignTop)
        self.hwBoardScroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.hwBoardScroll.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.hwBoardView=Esp32AnimatedBoardWidget(self)
        self.hwBoardScroll.setWidget(self.hwBoardView)
        leftLay.addWidget(self.hwBoardScroll)
        self.hwBoardSplitter.addWidget(leftWrap)

        rightWrap=QWidget();rightWrap.setMinimumWidth(300);rightWrap.setMaximumWidth(460)
        boardRight=QVBoxLayout(rightWrap);boardRight.setContentsMargins(8,0,0,0);boardRight.setSpacing(6)
        self.hwBoardSummary=QTextEdit();self.hwBoardSummary.setReadOnly(True);self.hwBoardSummary.setMinimumWidth(285)
        self.hwBoardPinInfo=QTextEdit();self.hwBoardPinInfo.setReadOnly(True);self.hwBoardPinInfo.setMinimumHeight(170)
        boardRight.addWidget(QLabel("BOARD GPIO SUMMARY"))
        boardRight.addWidget(self.hwBoardSummary,3)
        boardRight.addWidget(QLabel("CLICKED PIN"))
        boardRight.addWidget(self.hwBoardPinInfo,2)
        self.hwBoardSplitter.addWidget(rightWrap)
        self.hwBoardSplitter.setStretchFactor(0,1)
        self.hwBoardSplitter.setStretchFactor(1,0)
        self.hwBoardSplitter.setSizes([1100,340])
        boardLayout.addWidget(self.hwBoardSplitter,1)
        self.hwTabs.addTab(boardPage,"Board GPIO Map")

        pinPage=QWidget();pinLay=QVBoxLayout(pinPage);pinLay.setContentsMargins(8,8,8,8)
        hint=QLabel("เพิ่มอุปกรณ์/Input/Output ใหม่ได้เองด้วย + Add New I/O • โปรแกรมตรวจ GPIO ซ้ำ, Reserved pin, Voltage และแสดงบน Board Animation อัตโนมัติ")
        hint.setWordWrap(True);hint.setStyleSheet("color:#60758b;font-weight:650;");pinLay.addWidget(hint)
        defs=self._hardware_defs();self.hwRows=[]
        self.hwTable=QTableWidget(len(defs),9)
        self.hwTable.setHorizontalHeaderLabels(["Use","Device","Signal","Interface","Supply","Logic","ESP32 GPIO","Protection","Status"])
        self.hwTable.verticalHeader().setVisible(False);self.hwTable.setAlternatingRowColors(True)
        self.hwTable.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.hwTable.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.hwTable.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        self.hwTable.horizontalHeader().setSectionResizeMode(1,QHeaderView.Stretch)
        self.hwTable.horizontalHeader().setSectionResizeMode(2,QHeaderView.Stretch)
        # Build standard project signals using the same row factory used by Custom I/O.
        self.hwTable.setRowCount(0)
        for d in defs:self._append_hardware_row(d)
        toolbar=QHBoxLayout()
        addIo=QPushButton("+ Add New I/O");addIo.setObjectName("primaryButton");addIo.clicked.connect(self.add_custom_hardware_io)
        editIo=QPushButton("Edit Selected");editIo.clicked.connect(self.edit_selected_hardware_io)
        dupIo=QPushButton("Duplicate");dupIo.clicked.connect(self.duplicate_selected_hardware_io)
        delIo=QPushButton("Delete Custom");delIo.setObjectName("secondaryButton");delIo.clicked.connect(self.delete_selected_hardware_io)
        toolbar.addWidget(addIo);toolbar.addWidget(editIo);toolbar.addWidget(dupIo);toolbar.addWidget(delIo);toolbar.addStretch(1)
        pinLay.addLayout(toolbar)
        pinLay.addWidget(self.hwTable,1)
        self.hwTabs.addTab(pinPage,"GPIO Devices")

        wirePage=QWidget();wl=QHBoxLayout(wirePage);wl.setContentsMargins(10,10,10,10);wl.setSpacing(12)
        protection=QGroupBox("Protection Checklist / การป้องกัน")
        pl=QVBoxLayout(protection)
        checks=[
            ("hwMainBMS","Main 72 V battery has BMS",True),
            ("hwMainFuse","Main fuse installed near 72 V battery",True),
            ("hwEstopHardware","Hardware E-stop cuts traction power / enable",True),
            ("hwDc72to5","72 V → regulated 5 V supply for controller/logic",True),
            ("hwRcRegulated","RC receiver supplied from regulated 5 V",True),
            ("hwLimitIsolation","Limit switches isolated/conditioned before ESP32",True),
            ("hwBuzzerMosfet","5 V buzzer driven through MOSFET/driver",True),
            ("hwWinchSeparate","Winch uses separate 12 V battery",True),
            ("hwWinchFuse","12 V winch battery has appropriate fuse",True),
            ("hwWinchContactor","Winch reversing contactor/relay rated for actual current",True),
        ]
        self.hwProtectionChecks=[]
        for attr,label,default in checks:
            cb=QCheckBox(label);cb.setChecked(default);setattr(self,attr,cb);self.hwProtectionChecks.append(cb)
            cb.stateChanged.connect(self.update_hardware_manager);pl.addWidget(cb)
        pl.addStretch(1);wl.addWidget(protection,1)

        wiring=QGroupBox("Wiring Check / เส้นทางไฟ")
        wr=QVBoxLayout(wiring)
        self.hwWiringSummary=QTextEdit();self.hwWiringSummary.setReadOnly(True);wr.addWidget(self.hwWiringSummary,1)
        wl.addWidget(wiring,2)
        self.hwTabs.addTab(wirePage,"Voltage && Wiring")

        genPage=QWidget();gl=QVBoxLayout(genPage);gl.setContentsMargins(10,10,10,10);gl.setSpacing(8)
        bar=QHBoxLayout()
        refresh=QPushButton("Refresh Code");refresh.setObjectName("primaryButton");refresh.clicked.connect(self.update_hardware_manager)
        copy=QPushButton("Copy");copy.clicked.connect(self.copy_hardware_code)
        export=QPushButton("Export .h");export.clicked.connect(self.export_hardware_header)
        bar.addWidget(refresh);bar.addWidget(copy);bar.addWidget(export);bar.addStretch(1);gl.addLayout(bar)
        self.hwCode=QPlainTextEdit();self.hwCode.setReadOnly(True)
        self.hwCode.setStyleSheet("font-family:Consolas,'Courier New',monospace;font-size:10.5pt;")
        gl.addWidget(self.hwCode,1)
        self.hwTabs.addTab(genPage,"ESP32 Pin Map")

        notes=QPlainTextEdit();notes.setReadOnly(True)
        notes.setPlainText("""V52 HARDWARE I/O NOTES

• Board Animation แสดง GPIO ทั้งหมดของชิปตาม Profile และสถานะ USED/FREE/ONBOARD/SHARED/CAUTION/CONFLICT
• Project default = ESP32 DevKit V1 / ESP-WROOM-32; ESP32-S3 profiles ยังเก็บไว้เป็น reference/alternate board\n• ESP32 DevKit V1 profile แสดง 34 physical GPIO และแยก input-only/strapping/UART pins
• Waveshare ESP32-S3-Touch-LCD-7B: โปรแกรมใส่ขา LCD, Touch/I2C, TF, RS485, USB/CAN และ UART0 จากเอกสารบอร์ดไว้ให้อัตโนมัติ
• Manual Reserved GPIO ใช้สำหรับขาที่คุณต้องการกันเพิ่มเองเท่านั้น
• ESP32 GPIO เป็น 3.3 V logic — ห้ามป้อน 5/12/72 V เข้า GPIO โดยตรง
• FlySky iBUS: ต้องยืนยันระดับสัญญาณจริงของ Receiver; ค่าเริ่มต้นในโปรแกรมถือว่า 5 V logic และต้องมี level shifting
• SN65HVD230 ใช้เป็น CAN transceiver ระหว่าง ESP32 กับ VESC; CANH/CANL ไม่ต่อเข้าขา GPIO ตรง
• Limit switch OMRON + PC817: โปรแกรมถือว่าฝั่ง ESP32 ถูก pull-up เป็น 3.3 V
• Buzzer 5 V: ใช้ MOSFET/driver ไม่ดึงกระแสโหลดจาก GPIO โดยตรง
• Winch 12 V เป็นระบบกำลังแยกจาก 72 V traction battery ตามแบบปัจจุบัน
• สำหรับ Waveshare 7B พอร์ตภายนอกที่เหลือมีจำกัดมาก; GPIO6 เป็น GP6 โดยตรง, GPIO8/9 เป็น I2C shared, GPIO43/44 เป็น UART0, GPIO19/20 แชร์ CAN/USB
• ค่าที่ขึ้น READY FOR CODE เป็น Preliminary Wiring Check — ต้องตรวจ datasheet, pinout, fuse/current rating และ wiring จริงก่อนจ่ายไฟ
• กด + Add New I/O เพื่อเพิ่ม Sensor, Relay, Encoder, Switch หรืออุปกรณ์ใหม่เองได้ โดยเลือก Input/Output, Voltage, GPIO และ Protection
• Custom I/O จะถูก Save/Load พร้อม Project และขึ้นบน Board Animation เหมือนอุปกรณ์มาตรฐาน
• Data source: Espressif ESP32/ESP32-S3 GPIO documentation + Waveshare ESP32-S3-Touch-LCD-7B official interface documentation
""")
        self.hwTabs.addTab(notes,"Notes / Safety")

        self.hwBoardProfile.currentIndexChanged.connect(self.on_hardware_profile_changed)
        self.hwReservedPins.textChanged.connect(self.update_hardware_manager)
        self.hwBoardVerified.stateChanged.connect(self.update_hardware_manager)
        self.tabs.addTab(w,"")
        self.update_hardware_manager()

    def _manual_reserved_gpio_set(self):
        if not hasattr(self,"hwReservedPins"):return set()
        valid=set(self.gpio_profile_data().get("pins",[]))
        return {int(x) for x in re.findall(r"\d+",self.hwReservedPins.text()) if int(x) in valid}

    def _reserved_gpio_set(self):
        # Backward-compatible name: manual reservations only. Board-level usage is
        # represented by gpio_profile_data()/hardware_pin_snapshot().
        return self._manual_reserved_gpio_set()

    @staticmethod
    def _logic_voltage_value(text):
        m=re.match(r"\s*(\d+(?:\.\d+)?)",str(text))
        return float(m.group(1)) if m else None

    def apply_suggested_hardware_map(self):
        profile=self.gpio_profile_data().get("profile")
        if profile=="waveshare7b":
            suggested={"IBUS_RX":44,"CAN_TX":20,"CAN_RX":19,"I2C_SDA":8,"I2C_SCL":9,
                       "LIMIT_LEFT":6,"LIMIT_RIGHT":None,"BUZZER":None,"LED":None}
        elif profile=="classic":
            suggested={"IBUS_RX":16,"CAN_TX":21,"CAN_RX":22,"I2C_SDA":18,"I2C_SCL":19,
                       "LIMIT_LEFT":32,"LIMIT_RIGHT":33,"BUZZER":25,"LED":26}
        else:
            suggested={"IBUS_RX":18,"CAN_TX":17,"CAN_RX":16,"I2C_SDA":8,"I2C_SCL":9,
                       "LIMIT_LEFT":10,"LIMIT_RIGHT":11,"BUZZER":12,"LED":13}
        for row in self.hwRows:
            pin=suggested.get(row["key"])
            row["gpio"].setCurrentText(f"GPIO {pin}" if pin is not None else "Not assigned")
        self.hwBoardVerified.setChecked(False)
        self.update_hardware_manager()

    def clear_hardware_gpio(self):
        for row in self.hwRows:row["gpio"].setCurrentText("Not assigned")
        self.hwBoardVerified.setChecked(False)
        self.update_hardware_manager()

    def hardware_check_results(self):
        data=self.gpio_profile_data();valid=set(data.get("pins",[]));profile=data.get("profile")
        manual=self._manual_reserved_gpio_set();used={};conflicts=[];missing=[];voltage=[];row_status={}
        base_info=data.get("pin_info",{})

        for row in self.hwRows:
            if not row["enabled"].isChecked():
                row_status[row["key"]]=("OFF","#64748b");continue
            gpio=row["gpio"].currentText()
            if gpio=="Not assigned":
                missing.append(row["key"]);row_status[row["key"]]=("MISSING","#b54708")
                continue

            m=re.search(r"\d+",gpio)
            if not m:
                conflicts.append(f"{row['key']}: invalid GPIO text");row_status[row["key"]]=("INVALID","#b42318");continue
            pin=int(m.group())
            if pin not in valid:
                conflicts.append(f"{row['key']} uses GPIO {pin}, which does not exist in {data['name']}")
                row_status[row["key"]]=("INVALID","#b42318");continue
            if pin in manual:
                conflicts.append(f"{row['key']} uses manually reserved GPIO {pin}")
            used.setdefault(pin,[]).append(row["key"])

            board_status=base_info.get(pin,{}).get("status","FREE")
            board_fn=base_info.get(pin,{}).get("function","")
            if profile=="waveshare7b":
                if board_status in ("BOARD","MEMORY"):
                    conflicts.append(f"{row['key']} uses GPIO {pin} reserved by board: {board_fn}")
                elif board_status in ("SHARED","CAUTION") and not self._profile_compatible_pin(row["key"],pin,row):
                    conflicts.append(f"{row['key']} cannot use GPIO {pin} on Waveshare 7B: {board_fn}")
            elif profile=="classic":
                if board_status=="CAUTION" and "Input only" in board_fn and row["interface"] in ("Digital OUT","CAN TX","I2C SCL"):
                    conflicts.append(f"{row['key']} requires output but GPIO {pin} is input-only")
            else:
                if board_status=="MEMORY":
                    conflicts.append(f"{row['key']} uses memory-related GPIO {pin}; choose another pin or verify module wiring")

            supply=row["supply"].currentText()
            logic=row["logic"].currentText()
            prot=row["protection"].currentText()
            if not row.get("custom",False) and supply not in row["allowed_supply"]:
                voltage.append(f"{row['device']} / {row['signal']}: supply {supply} not in expected {', '.join(row['allowed_supply'])}")
            lv=self._logic_voltage_value(logic)
            if lv is not None and lv>3.6 and prot=="Direct":
                voltage.append(f"{row['device']} / {row['signal']}: {logic} logic cannot go directly to ESP32 GPIO")
            if lv is not None and lv>=12:
                voltage.append(f"{row['device']} / {row['signal']}: {logic} signal requires isolation/conditioning")
            if row["key"]=="IBUS_RX" and lv is not None and lv>3.6 and prot not in ("Level Shifter / Divider","PC817 Isolation","Other"):
                voltage.append("iBUS input above 3.3 V requires level shifting/conditioning")
            if row["key"].startswith("LIMIT_") and prot!="PC817 Isolation":
                voltage.append(f"{row['key']}: current project expects PC817 isolation")
            if row["key"]=="BUZZER" and prot!="MOSFET / Driver":
                voltage.append("BUZZER: current project expects MOSFET/driver")

        for pin,keys in used.items():
            if len(keys)>1:conflicts.append(f"GPIO {pin} duplicated: "+", ".join(keys))

        for row in self.hwRows:
            if row_status.get(row["key"],("",""))[0] in ("OFF","MISSING","INVALID"):continue
            txt=row["gpio"].currentText();m=re.search(r"\d+",txt)
            if not m:continue
            pin=int(m.group())
            related=[x for x in conflicts if row["key"] in x or f"GPIO {pin}" in x]
            rowVoltage=[x for x in voltage if row["device"] in x or row["key"] in x]
            if related:row_status[row["key"]]=("CONFLICT","#b42318")
            elif rowVoltage:row_status[row["key"]]=("VOLTAGE","#b42318")
            else:row_status[row["key"]]=("OK","#176337")

        protection_missing=[cb.text() for cb in self.hwProtectionChecks if not cb.isChecked()]
        if not self.hwBoardVerified.isChecked():
            protection_missing.append("Board GPIO pinout not verified by user")

        ready=not conflicts and not missing and not voltage and not protection_missing
        return dict(conflicts=conflicts,missing=missing,voltage=voltage,
                    protection_missing=protection_missing,row_status=row_status,ready=ready)

    def _set_hw_metric(self,label,text,ok):
        label.setText(str(text))
        label.setStyleSheet(f"color:{'#176337' if ok else '#b42318'};font-size:15pt;font-weight:900;")

    def generate_hardware_header_text(self):
        result=self.hardware_check_results()
        lines=[
            "#pragma once",
            "// Auto-generated by Crane Vehicle Engineering Tool",
            f"// Version {APP_VERSION}",
            f"// Board: {self.hwBoardProfile.currentText()}",
            "// Verify this file against the actual ESP32 board pinout before flashing.",
            "",
        ]
        for row in self.hwRows:
            if not row["enabled"].isChecked():continue
            gpio=row["gpio"].currentText()
            if gpio=="Not assigned":
                lines.append(f"// {row['key']}: NOT ASSIGNED")
            else:
                pin=int(re.search(r"\d+",gpio).group())
                macro=re.sub(r"[^A-Z0-9_]+","_",str(row["key"]).upper()).strip("_")
                lines.append(f"#define PIN_{macro} {pin}")
        lines+=["","// Interface summary"]
        for row in self.hwRows:
            if row["enabled"].isChecked():
                lines.append(f"// {row['key']}: {row['device']} | {row['interface']} | supply {row['supply'].currentText()} | logic {row['logic'].currentText()} | {row['protection'].currentText()}")
        lines+=["",f"// GPIO conflicts: {len(result['conflicts'])}",
                f"// Voltage errors: {len(result['voltage'])}",
                f"// Missing pins: {len(result['missing'])}",
                f"// Protection issues: {len(result['protection_missing'])}",
                f"// Ready for code: {'YES' if result['ready'] else 'NO'}"]
        return "\n".join(lines)

    def update_hardware_manager(self,*_):
        if not hasattr(self,"hwRows"):return
        result=self.hardware_check_results()
        for row in self.hwRows:
            text,color=result["row_status"].get(row["key"],("CHECK","#64748b"))
            row["status"].setText(text);row["status"].setStyleSheet(f"color:{color};font-weight:900;")
        self._set_hw_metric(self.hwConflictLabel,len(result["conflicts"]),not result["conflicts"])
        self._set_hw_metric(self.hwVoltageLabel,len(result["voltage"]),not result["voltage"])
        self._set_hw_metric(self.hwMissingLabel,len(result["missing"]),not result["missing"])
        self._set_hw_metric(self.hwProtectionLabel,"PASS" if not result["protection_missing"] else f"{len(result['protection_missing'])} CHECK",not result["protection_missing"])
        self._set_hw_metric(self.hwReadyLabel,"YES" if result["ready"] else "NO",result["ready"])

        data,counts,snap=self.gpio_profile_summary()
        if hasattr(self,"hwBoardCountLabel"):
            self.hwBoardCountLabel.setText(f"{len(data['pins'])} physical GPIO  •  USED {counts.get('USED',0)}  •  CONFLICT {counts.get('CONFLICT',0)}")
        if hasattr(self,"hwBoardSummary"):
            exposed=data.get("exposed")
            exposed_text=f"{len(exposed)} board-exposed/shared pins" if exposed else "Chip-level profile"
            self.hwBoardSummary.setHtml(f"""
            <h2>{data['name']}</h2>
            <p><b>Physical GPIO:</b> {len(data['pins'])}</p>
            <p><b>Profile scope:</b> {exposed_text}</p>
            <table border='1' cellspacing='0' cellpadding='5'>
            <tr><th>Status</th><th>Count</th></tr>
            <tr><td style='color:#176337'><b>USED by project</b></td><td>{counts.get('USED',0)}</td></tr>
            <tr><td style='color:#2f80ed'><b>FREE</b></td><td>{counts.get('FREE',0)}</td></tr>
            <tr><td style='color:#b76e00'><b>ONBOARD</b></td><td>{counts.get('BOARD',0)}</td></tr>
            <tr><td style='color:#087e8b'><b>SHARED</b></td><td>{counts.get('SHARED',0)}</td></tr>
            <tr><td style='color:#b54708'><b>CAUTION</b></td><td>{counts.get('CAUTION',0)}</td></tr>
            <tr><td style='color:#7c3aed'><b>MEMORY</b></td><td>{counts.get('MEMORY',0)}</td></tr>
            <tr><td style='color:#b42318'><b>CONFLICT</b></td><td>{counts.get('CONFLICT',0)}</td></tr>
            </table>
            <p><b>Source model:</b> {data.get('source','')}</p>
            <p>คลิก GPIO บนรูปบอร์ดเพื่อดูว่าขานั้นถูกใช้โดยอะไร</p>
            """)
        if hasattr(self,"hwBoardView"):self.hwBoardView.update()

        issues=[]
        if result["conflicts"]:issues+=["GPIO: "+x for x in result["conflicts"]]
        if result["voltage"]:issues+=["VOLTAGE: "+x for x in result["voltage"]]
        if result["missing"]:issues+=["MISSING PIN: "+x for x in result["missing"]]
        if result["protection_missing"]:issues+=["PROTECTION: "+x for x in result["protection_missing"]]
        issue_text="\n".join("• "+x for x in issues) if issues else "• ไม่พบ Conflict / Voltage Error / Missing Pin / Protection issue"

        main_chain="72 V Battery → BMS → Main Fuse → Hardware E-stop / Enable → Flipsky Dual 75100 → QS Hub Motors ×2"
        logic_chain="72 V Battery → DC-DC 5 V → ESP32 / RC Receiver / Logic"
        profile=data.get("profile")
        can_chain=("ESP32-S3 GPIO20/19 → onboard CAN transceiver → CANH/CANL → VESC" if profile=="waveshare7b"
                   else "ESP32 CAN TX/RX → CAN transceiver → CANH/CANL → VESC")
        limit_chain="OMRON Limit ±90° → PC817 → 3.3 V ESP32 Digital IN"
        winch_chain="Separate 12 V Battery → Winch Fuse → Reversing Contactor → 12 V Winch"
        extra=""
        if profile=="waveshare7b":
            extra="\n\nWAVESHARE 7B NOTE\n• LCD consumes many GPIO internally.\n• GPIO8/9 are shared I2C. GPIO19/20 share CAN/USB. GPIO43/44 are UART0. GPIO6 is the dedicated GP6 header.\n• The current project has more direct digital signals than the board exposes; an external I/O expander or separate controller may be required."
        self.hwWiringSummary.setPlainText(
            "WIRING PATH — CURRENT PROJECT\n\n"
            +main_chain+"\n\n"+logic_chain+"\n\n"+can_chain+"\n\n"+limit_chain+"\n\n"+winch_chain
            +extra+"\n\nSYSTEM CHECK\n"+issue_text
            +"\n\nหมายเหตุ: ตรวจ datasheet, fuse/current rating, wire gauge, grounding และ actual board pinout ก่อนจ่ายไฟจริง"
        )
        self.hwCode.setPlainText(self.generate_hardware_header_text())
        if hasattr(self,"telemetryCodeView"):
            self.telemetryCodeView.setPlainText(self.telemetry_esp32_template())

    def copy_hardware_code(self):
        QApplication.clipboard().setText(self.generate_hardware_header_text())
        self.statusBar().showMessage("คัดลอก ESP32 Pin Map แล้ว",3000)

    def export_hardware_header(self):
        docs=QStandardPaths.writableLocation(QStandardPaths.DocumentsLocation) or str(Path.home())
        default=str(Path(docs)/"cvet_hardware_pins.h")
        filename,_=QFileDialog.getSaveFileName(self,"Export ESP32 Pin Map",default,"C/C++ Header (*.h);;Text (*.txt)")
        if not filename:return
        if not Path(filename).suffix:filename+=".h"
        try:
            Path(filename).write_text(self.generate_hardware_header_text(),encoding="utf-8")
            QMessageBox.information(self,"Hardware Pin Map","บันทึกไฟล์เรียบร้อย:\n"+filename)
        except Exception as exc:
            QMessageBox.critical(self,"Hardware Pin Map",str(exc))


    # =====================================================================
    # V53 — ENGINEERING INTEGRATION SUITE
    # Validation • Diagnostics • Device Library • BOM • Revisions • Final Verification
    # =====================================================================
    def _table_rows_text(self,table):
        rows=[]
        for r in range(table.rowCount()):
            row=[]
            for c in range(table.columnCount()):
                item=table.item(r,c);row.append(item.text() if item else "")
            rows.append(row)
        return rows

    def _load_table_rows_text(self,table,rows):
        table.blockSignals(True)
        table.setRowCount(0)
        for row in rows or []:
            r=table.rowCount();table.insertRow(r)
            for c,val in enumerate(row[:table.columnCount()]):
                table.setItem(r,c,QTableWidgetItem(str(val)))
        table.blockSignals(False)

    def make_integration_suite(self):
        w=QWidget();self.integrationPage=w
        root=QVBoxLayout(w);root.setContentsMargins(16,14,16,16);root.setSpacing(12)
        root.addWidget(make_page_header(
            "ENGINEERING INTEGRATION SUITE",
            "Device Library • Validation • Diagnostics • BOM/Cost • Revisions • Final Verification",
            self.show_home_mode,"V53 INTEGRATION","#eee9ff","#5b4bb7"
        ))
        self.integrationTabs=QTabWidget();root.addWidget(self.integrationTabs,1)

        # -------------------------------------------------------------
        # 1) DEVICE LIBRARY
        # -------------------------------------------------------------
        dp=QWidget();dl=QVBoxLayout(dp);dl.setContentsMargins(9,9,9,9);dl.setSpacing(8)
        dbar=QHBoxLayout()
        add=QPushButton("+ Add Device");add.setObjectName("primaryButton");add.clicked.connect(self.add_device_library_item)
        edit=QPushButton("Edit");edit.clicked.connect(self.edit_device_library_item)
        duplicate=QPushButton("Duplicate");duplicate.clicked.connect(self.duplicate_device_library_item)
        remove=QPushButton("Delete");remove.setObjectName("secondaryButton");remove.clicked.connect(self.delete_device_library_item)
        send=QPushButton("Add to Hardware I/O");send.clicked.connect(self.add_library_device_to_hardware)
        sendBom=QPushButton("Add to BOM");sendBom.clicked.connect(self.add_library_device_to_bom)
        for b in (add,edit,duplicate,remove,send,sendBom):dbar.addWidget(b)
        dbar.addStretch(1);dl.addLayout(dbar)
        note=QLabel("เพิ่ม Sensor / Relay / Encoder / Switch / Display / Communication / Power module ได้เอง แล้วส่งไป Hardware I/O ได้ทันที • 1 แถว = 1 signal ของอุปกรณ์")
        note.setWordWrap(True);note.setStyleSheet("color:#60758b;font-weight:650;");dl.addWidget(note)
        self.deviceLibraryTable=QTableWidget(0,8)
        self.deviceLibraryTable.setHorizontalHeaderLabels(["Device","Category","Signal","Interface","Supply","Logic","Protection","Note"])
        self.deviceLibraryTable.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.deviceLibraryTable.setSelectionMode(QAbstractItemView.SingleSelection)
        self.deviceLibraryTable.setAlternatingRowColors(True)
        self.deviceLibraryTable.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        self.deviceLibraryTable.horizontalHeader().setSectionResizeMode(0,QHeaderView.Stretch)
        self.deviceLibraryTable.horizontalHeader().setSectionResizeMode(7,QHeaderView.Stretch)
        self.deviceLibraryTable.itemChanged.connect(lambda *_: self.schedule_easy_autosave() if hasattr(self,"easyAutosaveTimer") else None)
        dl.addWidget(self.deviceLibraryTable,1)
        self.integrationTabs.addTab(dp,"Device Library")

        # -------------------------------------------------------------
        # 2) TEST & VALIDATION CENTER
        # -------------------------------------------------------------
        vp=QWidget();vl=QVBoxLayout(vp);vl.setContentsMargins(9,9,9,9);vl.setSpacing(8)
        vbar=QHBoxLayout()
        load=QPushButton("Load Current Calculated Targets");load.setObjectName("primaryButton");load.clicked.connect(self.load_validation_targets)
        addv=QPushButton("+ Add Test");addv.clicked.connect(self.add_validation_row)
        delv=QPushButton("Delete Selected");delv.clicked.connect(self.delete_validation_row)
        clearv=QPushButton("Clear Measured");clearv.clicked.connect(self.clear_validation_measured)
        fromTele=QPushButton("Fill from Latest Telemetry");fromTele.clicked.connect(self.fill_validation_from_telemetry)
        for b in (load,fromTele,addv,delv,clearv):vbar.addWidget(b)
        vbar.addStretch(1);vl.addLayout(vbar)
        vh=QLabel("กรอกค่าที่วัดจากรถจริงในคอลัมน์ Measured → โปรแกรมคำนวณ Error % และ PASS/FAIL อัตโนมัติ")
        vh.setWordWrap(True);vh.setStyleSheet("color:#60758b;font-weight:650;");vl.addWidget(vh)
        self.validationTable=QTableWidget(0,8)
        self.validationTable.setHorizontalHeaderLabels(["Test","Unit","Calculated","Measured","Tolerance %","Error %","Status","Note"])
        self.validationTable.verticalHeader().setVisible(False);self.validationTable.setAlternatingRowColors(True)
        self.validationTable.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        self.validationTable.horizontalHeader().setSectionResizeMode(0,QHeaderView.Stretch)
        self.validationTable.horizontalHeader().setSectionResizeMode(7,QHeaderView.Stretch)
        self.validationTable.itemChanged.connect(self.update_validation_results)
        vl.addWidget(self.validationTable,1)
        self.validationSummary=QLabel("Validation: ยังไม่มีข้อมูลวัดจริง")
        self.validationSummary.setStyleSheet("font-weight:900;color:#17324d;padding:8px;");vl.addWidget(self.validationSummary)
        self.integrationTabs.addTab(vp,"Test & Validation")

        # -------------------------------------------------------------
        # 3) FAULT & DIAGNOSTIC CENTER
        # -------------------------------------------------------------
        fp=QWidget();fl=QVBoxLayout(fp);fl.setContentsMargins(9,9,9,9);fl.setSpacing(8)
        fbar=QHBoxLayout()
        run=QPushButton("Run Diagnostics");run.setObjectName("primaryButton");run.clicked.connect(self.run_diagnostics)
        clearlog=QPushButton("Clear Fault Log");clearlog.clicked.connect(self.clear_diagnostic_log)
        fbar.addWidget(run);fbar.addWidget(clearlog);fbar.addStretch(1);fl.addLayout(fbar)
        self.diagnosticSummary=QLabel("กด Run Diagnostics เพื่อตรวจ Safety, Hardware, Battery, Design และ Telemetry")
        self.diagnosticSummary.setWordWrap(True);self.diagnosticSummary.setStyleSheet("font-weight:750;color:#60758b;");fl.addWidget(self.diagnosticSummary)
        split=QSplitter(Qt.Vertical)
        self.diagnosticTable=QTableWidget(0,4)
        self.diagnosticTable.setHorizontalHeaderLabels(["Severity","System","Finding","Recommended action"])
        self.diagnosticTable.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        self.diagnosticTable.horizontalHeader().setSectionResizeMode(2,QHeaderView.Stretch)
        self.diagnosticTable.horizontalHeader().setSectionResizeMode(3,QHeaderView.Stretch)
        self.diagnosticTable.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.diagnosticLog=QPlainTextEdit();self.diagnosticLog.setReadOnly(True)
        split.addWidget(self.diagnosticTable);split.addWidget(self.diagnosticLog);split.setSizes([430,180]);fl.addWidget(split,1)
        self.integrationTabs.addTab(fp,"Fault & Diagnostic")

        # -------------------------------------------------------------
        # 4) BOM + COST + WEIGHT
        # -------------------------------------------------------------
        bp=QWidget();bl=QVBoxLayout(bp);bl.setContentsMargins(9,9,9,9);bl.setSpacing(8)
        bbar=QHBoxLayout()
        base=QPushButton("Load Project Baseline BOM");base.setObjectName("primaryButton");base.clicked.connect(self.load_baseline_bom)
        addb=QPushButton("+ Add Item");addb.clicked.connect(self.add_bom_row)
        delb=QPushButton("Delete Selected");delb.clicked.connect(self.delete_bom_row)
        for b in (base,addb,delb):bbar.addWidget(b)
        bbar.addStretch(1);bl.addLayout(bbar)
        self.bomTable=QTableWidget(0,8)
        self.bomTable.setHorizontalHeaderLabels(["Item","Category","Qty","Unit Cost (THB)","Unit Mass (kg)","Supplier / URL","Status","Note"])
        self.bomTable.setAlternatingRowColors(True);self.bomTable.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.bomTable.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        self.bomTable.horizontalHeader().setSectionResizeMode(0,QHeaderView.Stretch)
        self.bomTable.horizontalHeader().setSectionResizeMode(5,QHeaderView.Stretch)
        self.bomTable.horizontalHeader().setSectionResizeMode(7,QHeaderView.Stretch)
        self.bomTable.itemChanged.connect(self.update_bom_summary)
        bl.addWidget(self.bomTable,1)
        self.bomSummary=QLabel("BOM: 0 items")
        self.bomSummary.setWordWrap(True);self.bomSummary.setStyleSheet("font-weight:900;color:#17324d;padding:8px;");bl.addWidget(self.bomSummary)
        self.integrationTabs.addTab(bp,"BOM / Cost / Weight")

        # -------------------------------------------------------------
        # 5) DESIGN REVISION MANAGER
        # -------------------------------------------------------------
        rp=QWidget();rl=QVBoxLayout(rp);rl.setContentsMargins(9,9,9,9);rl.setSpacing(8)
        rbar=QHBoxLayout()
        cap=QPushButton("Capture Revision");cap.setObjectName("primaryButton");cap.clicked.connect(self.capture_design_revision)
        apply=QPushButton("Apply Selected");apply.clicked.connect(self.apply_design_revision)
        compare=QPushButton("Compare 2 Selected");compare.clicked.connect(self.compare_design_revisions)
        dele=QPushButton("Delete");dele.clicked.connect(self.delete_design_revision)
        for b in (cap,apply,compare,dele):rbar.addWidget(b)
        rbar.addStretch(1);rl.addLayout(rbar)
        self.revisionTable=QTableWidget(0,4)
        self.revisionTable.setHorizontalHeaderLabels(["Name","Created","Version","Note"])
        self.revisionTable.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.revisionTable.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.revisionTable.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        self.revisionTable.horizontalHeader().setSectionResizeMode(0,QHeaderView.Stretch)
        self.revisionTable.horizontalHeader().setSectionResizeMode(3,QHeaderView.Stretch)
        rl.addWidget(self.revisionTable,1)
        self.revisionCompare=QTextEdit();self.revisionCompare.setReadOnly(True);self.revisionCompare.setMinimumHeight(220);rl.addWidget(self.revisionCompare)
        self.designRevisions=[]
        self.integrationTabs.addTab(rp,"Design Revisions")

        # -------------------------------------------------------------
        # 6) FINAL PROJECT VERIFICATION
        # -------------------------------------------------------------
        cp=QWidget();cl=QVBoxLayout(cp);cl.setContentsMargins(9,9,9,9);cl.setSpacing(8)
        cbar=QHBoxLayout()
        refresh=QPushButton("Refresh Final Verification");refresh.setObjectName("primaryButton");refresh.clicked.connect(self.update_final_verification)
        goReport=QPushButton("Open Final Report");goReport.clicked.connect(self.show_project_tools_mode)
        cbar.addWidget(refresh);cbar.addWidget(goReport);cbar.addStretch(1);cl.addLayout(cbar)
        self.finalVerificationView=QTextEdit();self.finalVerificationView.setReadOnly(True);cl.addWidget(self.finalVerificationView,1)
        self.integrationTabs.addTab(cp,"Final Verification")

        self.integrationTabs.currentChanged.connect(lambda i:self.refresh_integration_suite())
        self.tabs.addTab(w,"")
        self.refresh_integration_suite()

    # ---------------- DEVICE LIBRARY ----------------
    def _device_library_dialog(self,title,existing=None):
        dlg=QDialog(self);dlg.setWindowTitle(title);dlg.resize(620,500)
        lay=QVBoxLayout(dlg);form=QFormLayout()
        existing=existing or {}
        name=QLineEdit(existing.get("device",""))
        category=QComboBox();category.addItems(["Sensor","Actuator","Communication","Switch / Input","Display / HMI","Power","Safety","Other"])
        category.setCurrentText(existing.get("category","Sensor"))
        signal=QLineEdit(existing.get("signal",""))
        interface=QComboBox();interface.addItems(["Digital IN","Digital OUT","ADC","PWM","UART RX","UART TX","I2C SDA","I2C SCL","CAN RX","CAN TX","SPI","Other"])
        interface.setCurrentText(existing.get("interface","Digital IN"))
        supply=QComboBox();supply.addItems(self._hardware_supply_items());supply.setCurrentText(existing.get("supply","3.3V"))
        logic=QComboBox();logic.addItems(self._hardware_logic_items());logic.setCurrentText(existing.get("logic","3.3V"))
        protection=QComboBox();protection.addItems(self._hardware_protection_items());protection.setCurrentText(existing.get("protection","Direct"))
        note=QLineEdit(existing.get("note",""))
        for lab,obj in (("Device name",name),("Category",category),("Signal",signal),("Interface",interface),
                        ("Supply",supply),("Logic",logic),("Protection",protection),("Note",note)):form.addRow(lab,obj)
        lay.addLayout(form)
        info=QLabel("ถ้าอุปกรณ์มีหลาย signal ให้เพิ่มหลายแถวโดยใช้ Device name เดียวกัน เช่น Encoder A / Encoder B")
        info.setWordWrap(True);info.setStyleSheet("background:#eef6ff;color:#31506b;padding:8px;border-radius:8px;");lay.addWidget(info)
        buttons=QDialogButtonBox(QDialogButtonBox.Save|QDialogButtonBox.Cancel);buttons.accepted.connect(dlg.accept);buttons.rejected.connect(dlg.reject);lay.addWidget(buttons)
        if dlg.exec()!=QDialog.Accepted:return None
        if not name.text().strip() or not signal.text().strip():
            QMessageBox.warning(self,title,"กรอก Device name และ Signal ก่อน")
            return None
        return dict(device=name.text().strip(),category=category.currentText(),signal=signal.text().strip(),
                    interface=interface.currentText(),supply=supply.currentText(),logic=logic.currentText(),
                    protection=protection.currentText(),note=note.text().strip())

    def _device_library_row_data(self,r):
        if r<0 or r>=self.deviceLibraryTable.rowCount():return None
        vals=[self.deviceLibraryTable.item(r,c).text() if self.deviceLibraryTable.item(r,c) else "" for c in range(8)]
        return dict(zip(("device","category","signal","interface","supply","logic","protection","note"),vals))

    def _append_device_library_row(self,data):
        r=self.deviceLibraryTable.rowCount();self.deviceLibraryTable.insertRow(r)
        for c,key in enumerate(("device","category","signal","interface","supply","logic","protection","note")):
            self.deviceLibraryTable.setItem(r,c,QTableWidgetItem(str(data.get(key,""))))
        return r

    def add_device_library_item(self):
        data=self._device_library_dialog("Add Device to Library")
        if not data:return
        r=self._append_device_library_row(data);self.deviceLibraryTable.selectRow(r)
        self.schedule_easy_autosave() if hasattr(self,"easyAutosaveTimer") else None

    def edit_device_library_item(self):
        r=self.deviceLibraryTable.currentRow()
        data=self._device_library_row_data(r)
        if not data:
            QMessageBox.information(self,"Device Library","เลือกอุปกรณ์ก่อน");return
        new=self._device_library_dialog("Edit Device",data)
        if not new:return
        for c,key in enumerate(("device","category","signal","interface","supply","logic","protection","note")):
            self.deviceLibraryTable.setItem(r,c,QTableWidgetItem(str(new.get(key,""))))
        self.schedule_easy_autosave() if hasattr(self,"easyAutosaveTimer") else None

    def duplicate_device_library_item(self):
        r=self.deviceLibraryTable.currentRow();data=self._device_library_row_data(r)
        if not data:return
        data["signal"]=data["signal"]+" Copy"
        nr=self._append_device_library_row(data);self.deviceLibraryTable.selectRow(nr)

    def delete_device_library_item(self):
        r=self.deviceLibraryTable.currentRow()
        if r>=0:self.deviceLibraryTable.removeRow(r);self.schedule_easy_autosave() if hasattr(self,"easyAutosaveTimer") else None

    def add_library_device_to_hardware(self):
        data=self._device_library_row_data(self.deviceLibraryTable.currentRow())
        if not data:
            QMessageBox.information(self,"Device Library","เลือกอุปกรณ์ก่อน");return
        existing={row["key"] for row in self.hwRows}
        definition=dict(key=self._hardware_key(data["signal"],existing),device=data["device"],signal=data["signal"],
                        interface=data["interface"],supply=data["supply"],logic=data["logic"],gpio="Not assigned",
                        protection=data["protection"],note=data["note"],allowed_supply=tuple(self._hardware_supply_items()),
                        custom=True,enabled=True)
        self._append_hardware_row(definition,select=True);self.update_hardware_manager()
        self.statusBar().showMessage(f"เพิ่ม {data['device']} / {data['signal']} ไป Hardware I/O แล้ว",3500)

    def add_library_device_to_bom(self):
        data=self._device_library_row_data(self.deviceLibraryTable.currentRow())
        if not data:
            QMessageBox.information(self,"Device Library","เลือกอุปกรณ์ก่อน");return
        self.bomTable.blockSignals(True)
        self._append_bom_row(data["device"],data["category"],1,0,0,"","Planned",f"{data['signal']} • {data['interface']}")
        self.bomTable.blockSignals(False);self.update_bom_summary()
        self.integrationTabs.setCurrentWidget(self.bomTable.parentWidget()) if False else None
        self.statusBar().showMessage(f"เพิ่ม {data['device']} ไป BOM แล้ว",3000)

    # ---------------- VALIDATION CENTER ----------------
    def _append_validation_row(self,name,unit,calc="",measured="",tol="10",note=""):
        r=self.validationTable.rowCount();self.validationTable.insertRow(r)
        vals=[name,unit,str(calc),str(measured),str(tol),"","PENDING",note]
        for c,val in enumerate(vals):
            item=QTableWidgetItem(val)
            if c in (5,6):item.setFlags(item.flags() & ~Qt.ItemIsEditable)
            self.validationTable.setItem(r,c,item)
        return r

    def load_validation_targets(self):
        t=self.torque_results();e=self.electrical_results();w=self.winch_results();sp=self.winch_speed_results()
        cycles=max(e["cycles"],1e-12);trip=e["Edrive"]/cycles
        self.validationTable.blockSignals(True);self.validationTable.setRowCount(0)
        rows=[
            ("Vehicle speed","km/h",self.tspeed.value(),"","5","วัดความเร็วรถจริง"),
            ("Wheel torque required","N·m",t["T"],"","10","เทียบกับค่าทดสอบ/ประเมิน"),
            ("Uphill battery current","A",e["Icalc_up"],"","15","วัดด้วย DC current sensor"),
            ("Drive energy per trip","Wh",trip,"","15","วัด Wh จากแบต/Power meter"),
            ("Winch lift time","s",w["tu"],"","10","ยกความสูงเดียวกับโมเดล"),
            ("Winch load speed up","m/min",w["up_speed"],"","10","ความเร็วโหลด ไม่ใช่ rope speed"),
            ("IMU zero tilt","deg",0,"","2","รถอยู่พื้นราบ"),
        ]
        for row in rows:self._append_validation_row(*row)
        self.validationTable.blockSignals(False);self.update_validation_results()

    def add_validation_row(self):
        self.validationTable.blockSignals(True);r=self._append_validation_row("New test","-",0,"",10,"")
        self.validationTable.blockSignals(False);self.validationTable.selectRow(r);self.update_validation_results()

    def delete_validation_row(self):
        r=self.validationTable.currentRow()
        if r>=0:self.validationTable.removeRow(r);self.update_validation_results()

    def clear_validation_measured(self):
        self.validationTable.blockSignals(True)
        for r in range(self.validationTable.rowCount()):
            self.validationTable.setItem(r,3,QTableWidgetItem(""))
        self.validationTable.blockSignals(False);self.update_validation_results()

    def fill_validation_from_telemetry(self):
        if not getattr(self,"telemetryHistory",None):
            QMessageBox.information(self,"Validation","ยังไม่มี Telemetry sample");return
        sample=self.telemetryHistory[-1]
        mapping={"Vehicle speed":"speed_kmh","Uphill battery current":"battery_a","IMU zero tilt":"tilt_deg"}
        self.validationTable.blockSignals(True);filled=0
        for r in range(self.validationTable.rowCount()):
            name=self.validationTable.item(r,0).text() if self.validationTable.item(r,0) else ""
            key=mapping.get(name)
            if key and key in sample:
                self.validationTable.setItem(r,3,QTableWidgetItem(f"{float(sample[key]):.4g}"));filled+=1
        self.validationTable.blockSignals(False);self.update_validation_results()
        self.statusBar().showMessage(f"นำ Telemetry ล่าสุดมาใส่ Validation {filled} ค่า",3000)

    def update_validation_results(self,*_):
        if not hasattr(self,"validationTable"):return
        self.validationTable.blockSignals(True);p=f=pend=0
        for r in range(self.validationTable.rowCount()):
            def val(c):
                try:return float((self.validationTable.item(r,c).text() if self.validationTable.item(r,c) else "").strip())
                except:return None
            calc=val(2);meas=val(3);tol=val(4)
            errItem=QTableWidgetItem("");statusItem=QTableWidgetItem("PENDING")
            if calc is not None and meas is not None and tol is not None:
                err=abs(meas-calc)/abs(calc)*100 if abs(calc)>1e-12 else abs(meas-calc)
                ok=err<=tol
                errItem=QTableWidgetItem(f"{err:.2f}")
                statusItem=QTableWidgetItem("PASS" if ok else "FAIL")
                statusItem.setForeground(QColor("#176337" if ok else "#b42318"));font=statusItem.font();font.setBold(True);statusItem.setFont(font)
                p+=int(ok);f+=int(not ok)
            else:pend+=1
            errItem.setFlags(errItem.flags() & ~Qt.ItemIsEditable);statusItem.setFlags(statusItem.flags() & ~Qt.ItemIsEditable)
            self.validationTable.setItem(r,5,errItem);self.validationTable.setItem(r,6,statusItem)
        self.validationTable.blockSignals(False)
        self.validationSummary.setText(f"Validation: PASS {p} • FAIL {f} • PENDING {pend}")
        self.validationSummary.setStyleSheet(f"font-weight:900;color:{'#176337' if f==0 and p>0 else '#b42318' if f else '#17324d'};padding:8px;")
        if hasattr(self,"finalVerificationView"):self.update_final_verification()
        self.schedule_easy_autosave() if hasattr(self,"easyAutosaveTimer") else None

    def validation_status_counts(self):
        out={"PASS":0,"FAIL":0,"PENDING":0}
        if not hasattr(self,"validationTable"):return out
        for r in range(self.validationTable.rowCount()):
            st=self.validationTable.item(r,6).text() if self.validationTable.item(r,6) else "PENDING"
            out[st]=out.get(st,0)+1
        return out

    # ---------------- DIAGNOSTICS ----------------
    def diagnostic_results(self):
        findings=[]
        def add(sev,system,finding,action):findings.append((sev,system,finding,action))
        try:
            sv=self.evaluate_safety_logic(self.safety_input_values())
            if sv["state"] in ("E-STOP","RC FAILSAFE","VESC FAULT","TILT INHIBIT","INTERLOCK CONFLICT"):
                add("CRITICAL","Safety",sv["state"]+" — "+sv["reason"],"แก้ Fault ก่อนอนุญาตให้รถเคลื่อนที่")
            elif sv["state"] not in ("READY","DRIVE","CRANE","WINCH"):
                add("WARNING","Safety",sv["state"]+" — "+sv["reason"],"ตรวจเงื่อนไข Safety / Command")
        except Exception as ex:add("WARNING","Safety","อ่าน Safety state ไม่สำเร็จ: "+str(ex),"ตรวจหน้า Control Logic")

        if hasattr(self,"hwRows"):
            hw=self.hardware_check_results()
            for x in hw["conflicts"]:add("ERROR","Hardware GPIO",x,"เปลี่ยน GPIO หรือ Board Profile")
            for x in hw["voltage"]:add("ERROR","Voltage",x,"เพิ่ม level shifting/isolation หรือแก้ Supply/Logic")
            for x in hw["missing"]:add("WARNING","Hardware I/O","Missing pin: "+x,"กำหนด GPIO หรือเพิ่ม I/O expander/controller")
            for x in hw["protection_missing"]:add("WARNING","Protection",x,"ตรวจ/ยืนยัน Protection checklist")

        try:
            for system,item,required,available,status,note in self.design_check_rows():
                if status=="FAIL":add("ERROR",system,f"{item}: {available} (required {required})",note or "แก้ค่าการออกแบบ")
        except Exception as ex:add("WARNING","Design Check","อ่าน Design Check ไม่สำเร็จ: "+str(ex),"ตรวจ Project Tools")

        if hasattr(self,"batterySelectionView"):
            br=self.battery_selection_results()
            if self.eCandidateAh.value()>0 and self.eCandidateAh.value()+1e-9<br["energy_min"]:
                add("ERROR","Main Battery",f"Candidate {self.eCandidateAh.value():.1f} Ah < minimum {br['energy_min']:.2f} Ah","เลือกแบตความจุมากขึ้น")
            if self.eCandidateContA.value()>0 and self.eCandidateContA.value()+1e-9<br["cont_req"]:
                add("ERROR","Main Battery",f"Continuous rating {self.eCandidateContA.value():.1f} A < required {br['cont_req']:.1f} A","เลือก Pack/BMS ที่จ่าย Continuous current ได้มากขึ้น")
            if self.eCandidatePeakA.value()>0 and self.eCandidatePeakA.value()+1e-9<br["peak_calc"]:
                add("ERROR","Main Battery",f"Peak rating {self.eCandidatePeakA.value():.1f} A < calculated {br['peak_calc']:.1f} A","เลือก Pack/BMS ที่รับ Peak current ได้มากขึ้น")

        vs=self.validation_status_counts()
        if vs["FAIL"]>0:add("WARNING","Validation",f"{vs['FAIL']} measured test(s) FAIL","ตรวจความคลาดเคลื่อนและปรับโมเดล/ฮาร์ดแวร์")
        if getattr(self,"telemetryHistory",None):
            sample=self.telemetryHistory[-1]
            if sample.get("estop"):add("CRITICAL","Live Telemetry","ESP32 reports E-stop active","ตรวจ E-stop และวงจร enable ก่อนเคลื่อนที่")
            if not sample.get("rc_ok",True):add("CRITICAL","Live Telemetry","ESP32 reports RC signal lost","ตรวจ receiver/iBUS/failsafe")
            if abs(float(sample.get("tilt_deg",0)))>=float(self.safetyTiltLimit.value()):
                add("WARNING","Live Telemetry",f"Tilt {float(sample.get('tilt_deg',0)):.1f}° exceeds limit","หยุด Drive และตรวจพื้น/เสถียรภาพ")
        if not findings:add("INFO","System","No active issue found by current software checks","ยังต้องตรวจฮาร์ดแวร์จริงและ datasheet ก่อนใช้งาน")
        return findings

    def run_diagnostics(self):
        findings=self.diagnostic_results()
        self.diagnosticTable.setRowCount(len(findings))
        colors={"CRITICAL":"#8b0000","ERROR":"#b42318","WARNING":"#b54708","INFO":"#176337"}
        active=0
        for r,row in enumerate(findings):
            for c,val in enumerate(row):
                item=QTableWidgetItem(str(val))
                if c==0:
                    item.setForeground(QColor(colors.get(str(val),"#17324d")));font=item.font();font.setBold(True);item.setFont(font)
                self.diagnosticTable.setItem(r,c,item)
            if row[0]!="INFO":active+=1
        self.diagnosticSummary.setText(f"Diagnostics: {active} active issue(s) • {len(findings)-active} info")
        stamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        for row in findings:
            if row[0]!="INFO":self.diagnosticLog.appendPlainText(f"[{stamp}] {row[0]} | {row[1]} | {row[2]}")
        if hasattr(self,"finalVerificationView"):self.update_final_verification()

    def clear_diagnostic_log(self):
        self.diagnosticLog.clear()

    # ---------------- BOM ----------------
    def _append_bom_row(self,item="",category="Other",qty=1,cost=0,mass=0,supplier="",status="Planned",note=""):
        r=self.bomTable.rowCount();self.bomTable.insertRow(r)
        vals=[item,category,str(qty),str(cost),str(mass),supplier,status,note]
        for c,val in enumerate(vals):self.bomTable.setItem(r,c,QTableWidgetItem(str(val)))
        return r

    def load_baseline_bom(self):
        if self.bomTable.rowCount()>0:
            ans=QMessageBox.question(self,"Baseline BOM","แทนที่ BOM ปัจจุบันด้วยรายการพื้นฐานหรือไม่?",QMessageBox.Yes|QMessageBox.No,QMessageBox.No)
            if ans!=QMessageBox.Yes:return
        self.bomTable.blockSignals(True);self.bomTable.setRowCount(0)
        rows=[
            ("QS 10in 1500W Hub Motor","Drive",2,0,0,"","Planned","72 V single shaft"),
            ("Flipsky Dual 75100","Drive Controller",1,0,0,"","Planned","VESC based"),
            ("72 V Main Battery","Battery",1,0,0,"","Planned","Fill selected Ah/BMS"),
            ("ESP32 Main Controller","Control",1,0,0,"","Planned","Board profile from Hardware I/O"),
            ("SN65HVD230","Communication",1,0,0,"","Planned","CAN transceiver"),
            ("BNO086","Sensor",1,0,0,"","Planned","9-DOF IMU"),
            ("OMRON D4N-112G","Safety Sensor",2,0,0,"","Planned","Crane ±90° limit"),
            ("PC817 Isolation","Safety / Interface",2,0,0,"","Planned","Limit switch isolation"),
            ("5 V Buzzer + MOSFET","Indicator",1,0,0,"","Planned","Motion/fault alarm"),
            ("Status LED / Lamp","Indicator",1,0,0,"","Planned","Motion/fault indicator"),
            ("12 V Winch","Winch",1,0,10.3,"","Planned","4500 lb listed pull; verify lifting approval"),
            ("12 V Winch Battery","Battery",1,0,0,"","Planned","Separate from 72 V main"),
        ]
        for row in rows:self._append_bom_row(*row)
        self.bomTable.blockSignals(False);self.update_bom_summary()

    def add_bom_row(self):
        self.bomTable.blockSignals(True);r=self._append_bom_row("New item","Other",1,0,0,"","Planned","")
        self.bomTable.blockSignals(False);self.bomTable.selectRow(r);self.update_bom_summary()

    def delete_bom_row(self):
        r=self.bomTable.currentRow()
        if r>=0:self.bomTable.removeRow(r);self.update_bom_summary()

    def bom_totals(self):
        total_cost=0.0;total_mass=0.0;qty_total=0.0;mass_missing=0;cost_missing=0
        for r in range(self.bomTable.rowCount()):
            try:qty=float(self.bomTable.item(r,2).text())
            except:qty=0
            try:cost=float(self.bomTable.item(r,3).text())
            except:cost=0
            try:mass=float(self.bomTable.item(r,4).text())
            except:mass=0
            qty_total+=qty;total_cost+=qty*cost;total_mass+=qty*mass
            if qty>0 and mass<=0:mass_missing+=1
            if qty>0 and cost<=0:cost_missing+=1
        return dict(cost=total_cost,mass=total_mass,qty=qty_total,items=self.bomTable.rowCount(),
                    mass_missing=mass_missing,cost_missing=cost_missing)

    def update_bom_summary(self,*_):
        if not hasattr(self,"bomTable"):return
        t=self.bom_totals()
        notes=[]
        if t["mass"]>300:notes.append("exceeds 300 kg target")
        if t["mass_missing"]:notes.append(f"{t['mass_missing']} row(s) missing mass")
        if t["cost_missing"]:notes.append(f"{t['cost_missing']} row(s) missing cost")
        suffix=(" • "+" • ".join(notes)) if notes else ""
        self.bomSummary.setText(f"BOM: {t['items']} rows • Qty {t['qty']:.0f} • Cost {t['cost']:,.2f} THB • Entered component mass {t['mass']:.2f} kg{suffix}")
        self.bomSummary.setStyleSheet(f"font-weight:900;color:{'#b42318' if t['mass']>300 else '#b54708' if t['mass_missing'] else '#17324d'};padding:8px;")
        if hasattr(self,"finalVerificationView"):self.update_final_verification()
        self.schedule_easy_autosave() if hasattr(self,"easyAutosaveTimer") else None

    def _revision_summary_values(self,state):
        widgets=state.get("widgets",{}) if isinstance(state,dict) else {}
        def get(name,default="—"):
            d=widgets.get(name,{})
            return d.get("value",default) if isinstance(d,dict) else default
        return {
            "Total mass kg":get("mt"),"Track m":get("W"),"Wheelbase m":get("WB"),"Boom length m":get("L"),
            "Slope deg":get("eSlopeDeg",get("eslopeDeg")),"Speed km/h":get("tspeed"),
            "Battery V":get("evolt"),"Runtime h":get("eruntime"),"Payload kg":get("ml"),
        }

    def refresh_revision_table(self):
        self.revisionTable.setRowCount(len(self.designRevisions))
        for r,rev in enumerate(self.designRevisions):
            vals=[rev.get("name",""),rev.get("created",""),rev.get("version",""),rev.get("note","")]
            for c,val in enumerate(vals):self.revisionTable.setItem(r,c,QTableWidgetItem(str(val)))

    def capture_design_revision(self):
        name,ok=QInputDialog.getText(self,"Capture Revision","Revision name:")
        if not ok or not name.strip():return
        note,ok2=QInputDialog.getText(self,"Capture Revision","Note (optional):")
        if not ok2:note=""
        state=self.capture_project_state()
        if isinstance(state.get("integration"),dict):state["integration"].pop("revisions",None)
        rev=dict(name=name.strip(),created=datetime.now().isoformat(timespec="seconds"),version=APP_VERSION,note=note,state=state)
        self.designRevisions.append(rev);self.refresh_revision_table()
        self.revisionTable.selectRow(len(self.designRevisions)-1)
        self.revisionCompare.setHtml(f"<h3>Captured {name}</h3><p>{note}</p>")
        self.schedule_easy_autosave() if hasattr(self,"easyAutosaveTimer") else None

    def apply_design_revision(self):
        r=self.revisionTable.currentRow()
        if r<0 or r>=len(self.designRevisions):return
        rev=self.designRevisions[r]
        if QMessageBox.question(self,"Apply Revision",f"ใช้ Revision '{rev['name']}' แทนค่าปัจจุบันหรือไม่?",QMessageBox.Yes|QMessageBox.No,QMessageBox.No)!=QMessageBox.Yes:return
        self.apply_project_state(rev["state"],True);self.refresh_integration_suite()

    def delete_design_revision(self):
        r=self.revisionTable.currentRow()
        if 0<=r<len(self.designRevisions):
            self.designRevisions.pop(r);self.refresh_revision_table();self.schedule_easy_autosave() if hasattr(self,"easyAutosaveTimer") else None

    def compare_design_revisions(self):
        rows=sorted({i.row() for i in self.revisionTable.selectionModel().selectedRows()})
        if len(rows)!=2:
            QMessageBox.information(self,"Compare Revisions","เลือก 2 Revision ก่อน");return
        a,b=[self.designRevisions[i] for i in rows]
        av=self._revision_summary_values(a["state"]);bv=self._revision_summary_values(b["state"])
        trs=[]
        for key in av:
            va=av[key];vb=bv[key]
            trs.append(f"<tr><td>{key}</td><td>{va}</td><td>{vb}</td><td>{'CHANGED' if va!=vb else 'same'}</td></tr>")
        self.revisionCompare.setHtml(
            f"<h2>{a['name']} ↔ {b['name']}</h2><table border='1' cellspacing='0' cellpadding='6'>"
            f"<tr><th>Parameter</th><th>{a['name']}</th><th>{b['name']}</th><th>Status</th></tr>{''.join(trs)}</table>"
        )

    # ---------------- FINAL VERIFICATION ----------------
    def final_verification_rows(self):
        rows=[]
        def add(area,item,status,detail):rows.append((area,item,status,detail))
        try:
            checks=self.design_check_rows()
            fail=sum(1 for x in checks if x[4]=="FAIL");check=sum(1 for x in checks if x[4]=="CHECK")
            add("Engineering","Integrated Design Check","PASS" if fail==0 else "FAIL",f"{fail} FAIL / {check} CHECK")
        except Exception as ex:add("Engineering","Integrated Design Check","CHECK",str(ex))
        if hasattr(self,"hwRows"):
            hw=self.hardware_check_results();add("Hardware","GPIO / Voltage / Protection","PASS" if hw["ready"] else "FAIL",
               f"{len(hw['conflicts'])} conflict, {len(hw['voltage'])} voltage, {len(hw['missing'])} missing, {len(hw['protection_missing'])} protection")
        vs=self.validation_status_counts()
        if sum(vs.values())==0:add("Validation","Measured vs Calculated","CHECK","ยังไม่มี Validation test")
        elif vs["FAIL"]>0:add("Validation","Measured vs Calculated","FAIL",f"{vs['FAIL']} FAIL / {vs['PENDING']} PENDING")
        elif vs["PENDING"]>0:add("Validation","Measured vs Calculated","CHECK",f"{vs['PASS']} PASS / {vs['PENDING']} PENDING")
        else:add("Validation","Measured vs Calculated","PASS",f"{vs['PASS']} PASS")
        bt=self.bom_totals() if hasattr(self,"bomTable") else dict(items=0,mass=0,cost=0,mass_missing=0,cost_missing=0)
        bom_status="CHECK" if bt["items"]==0 or bt.get("mass_missing",0)>0 else ("FAIL" if bt["mass"]>300 else "PASS")
        add("BOM","BOM / Cost / Weight",bom_status,
            f"{bt['items']} rows • entered mass {bt['mass']:.1f} kg • {bt['cost']:,.0f} THB • missing mass {bt.get('mass_missing',0)}")
        add("Revisions","Design Revision Snapshot","PASS" if len(getattr(self,"designRevisions",[]))>0 else "CHECK",
            f"{len(getattr(self,'designRevisions',[]))} revision(s)")
        findings=self.diagnostic_results()
        active=sum(1 for x in findings if x[0]!="INFO")
        add("Diagnostics","Active software-detected issues","PASS" if active==0 else "FAIL",f"{active} active issue(s)")
        if hasattr(self,"telemetryConnected"):
            add("Telemetry","ESP32 Data Logger","PASS" if self.telemetryConnected else "CHECK",
                "Connected" if self.telemetryConnected else "Not connected — connect during vehicle validation")
        return rows

    def update_final_verification(self):
        if not hasattr(self,"finalVerificationView"):return
        self.finalVerificationView.setHtml(self.final_verification_html())

    def validation_report_html(self):
        if not hasattr(self,"validationTable") or self.validationTable.rowCount()==0:
            return "<h2>Validation</h2><p>No validation records.</p>"
        rows=[]
        for r in range(self.validationTable.rowCount()):
            vals=[self.validationTable.item(r,c).text() if self.validationTable.item(r,c) else "" for c in range(self.validationTable.columnCount())]
            status=vals[6] if len(vals)>6 else "PENDING"
            color="#176337" if status=="PASS" else "#b42318" if status=="FAIL" else "#b54708"
            rows.append(f"<tr><td>{vals[0]}</td><td>{vals[1]}</td><td>{vals[2]}</td><td>{vals[3]}</td><td>{vals[4]}</td><td>{vals[5]}</td><td style='color:{color};font-weight:900'>{status}</td><td>{vals[7]}</td></tr>")
        c=self.validation_status_counts()
        return (f"<h2>TEST & VALIDATION</h2><p>PASS {c['PASS']} • FAIL {c['FAIL']} • PENDING {c['PENDING']}</p>"
                "<table border='1' cellspacing='0' cellpadding='5'><tr><th>Test</th><th>Unit</th><th>Calculated</th><th>Measured</th><th>Tol %</th><th>Error %</th><th>Status</th><th>Note</th></tr>"
                +"".join(rows)+"</table>")

    def bom_report_html(self):
        if not hasattr(self,"bomTable") or self.bomTable.rowCount()==0:
            return "<h2>BOM / COST / WEIGHT</h2><p>No BOM rows.</p>"
        rows=[]
        for r in range(self.bomTable.rowCount()):
            vals=[self.bomTable.item(r,c).text() if self.bomTable.item(r,c) else "" for c in range(self.bomTable.columnCount())]
            rows.append("<tr>"+"".join(f"<td>{v}</td>" for v in vals)+"</tr>")
        t=self.bom_totals()
        return (f"<h2>BOM / COST / WEIGHT</h2><p><b>Total entered cost:</b> {t['cost']:,.2f} THB • <b>Entered component mass:</b> {t['mass']:.2f} kg</p>"
                "<table border='1' cellspacing='0' cellpadding='5'><tr><th>Item</th><th>Category</th><th>Qty</th><th>Unit Cost</th><th>Unit Mass</th><th>Supplier</th><th>Status</th><th>Note</th></tr>"
                +"".join(rows)+"</table>")

    def diagnostic_report_html(self):
        findings=self.diagnostic_results()
        rows=[]
        for sev,system,finding,action in findings:
            color="#176337" if sev=="INFO" else "#b54708" if sev=="WARNING" else "#b42318"
            rows.append(f"<tr><td style='color:{color};font-weight:900'>{sev}</td><td>{system}</td><td>{finding}</td><td>{action}</td></tr>")
        return ("<h2>FAULT & DIAGNOSTIC</h2><table border='1' cellspacing='0' cellpadding='5'><tr><th>Severity</th><th>System</th><th>Finding</th><th>Recommended action</th></tr>"
                +"".join(rows)+"</table>")

    def revision_report_html(self):
        revs=getattr(self,"designRevisions",[])
        if not revs:return "<h2>DESIGN REVISIONS</h2><p>No captured revision.</p>"
        rows="".join(f"<tr><td>{r.get('name','')}</td><td>{r.get('created','')}</td><td>{r.get('version','')}</td><td>{r.get('note','')}</td></tr>" for r in revs)
        return "<h2>DESIGN REVISIONS</h2><table border='1' cellspacing='0' cellpadding='5'><tr><th>Name</th><th>Created</th><th>Version</th><th>Note</th></tr>"+rows+"</table>"

    def final_verification_html(self):
        rows=self.final_verification_rows()
        fail=sum(1 for x in rows if x[2]=="FAIL");check=sum(1 for x in rows if x[2]=="CHECK");passed=sum(1 for x in rows if x[2]=="PASS")
        color="#176337" if fail==0 and check==0 else "#b42318" if fail else "#b54708"
        overall="READY FOR FINAL REVIEW" if fail==0 and check==0 else ("NOT READY" if fail else "REVIEW REQUIRED")
        trs=[]
        for area,item,status,detail in rows:
            sc="#176337" if status=="PASS" else "#b42318" if status=="FAIL" else "#b54708"
            trs.append(f"<tr><td>{area}</td><td>{item}</td><td style='color:{sc};font-weight:900'>{status}</td><td>{detail}</td></tr>")
        return (f"<h1>FINAL PROJECT VERIFICATION</h1><p style='font-size:15pt;color:{color}'><b>{overall}</b></p>"
                f"<p>PASS {passed} • CHECK {check} • FAIL {fail}</p>"
                "<table border='1' cellspacing='0' cellpadding='7'><tr><th>Area</th><th>Check</th><th>Status</th><th>Detail</th></tr>"
                +"".join(trs)+"</table>"
                "<p><b>หมายเหตุ:</b> PASS ในโปรแกรมคือผ่านเกณฑ์ของแบบจำลอง/ข้อมูลที่กรอก ไม่ใช่การรับรองความปลอดภัยของเครื่องจักรจริง</p>")

    def refresh_integration_suite(self):
        if hasattr(self,"validationTable"):self.update_validation_results()
        if hasattr(self,"bomTable"):self.update_bom_summary()
        if hasattr(self,"revisionTable"):self.refresh_revision_table()
        if hasattr(self,"finalVerificationView"):self.update_final_verification()

    def setup_dynamic_tabs(self):
        """Top-level navigation uses one active page only; the top tab bar is hidden."""
        # Keep long internal tab sets usable on 1366×768 and smaller windows.
        for tab in self.findChildren(QTabWidget):
            try:
                tab.tabBar().setUsesScrollButtons(True)
                tab.setElideMode(Qt.ElideNone)
            except Exception:
                pass
        self._mode_pages={
            "home":self.homePage,"torque":self.torquePage,"electrical":self.electricalPage,"winch":self.winchPage,"crane":self.cranePage,
            "slope":self.slopePage,"fbd":self.fbdPage,"components":self.componentsPage,
            "worst":self.worstPage,"steps":self.stepsPage,"design":self.designPage,
            "graph":getattr(self,"graphPage",None),"report":self.reportPage,"help":self.helpPage,"tools":self.projectToolsPage,"safety":self.safetyPage,"variables":self.variableDictionaryPage,"hardware":self.hardwarePage,"telemetry":self.telemetryPage,"integration":self.integrationPage}
        self.show_home_mode()

    def _show_only_page(self,page):
        while self.tabs.count():
            self.tabs.removeTab(0)
        self.tabs.addTab(page,"")
        self.tabs.setCurrentWidget(page)
        self.tabs.tabBar().hide()

    def _web_server_command(self):
        """Return the bundled Web Server command for installed and source modes."""
        if getattr(sys,"frozen",False):
            exe=Path(sys.executable).resolve().parent/"CraneVehicleWebServer.exe"
            return [str(exe)] if exe.exists() else None
        launcher=Path(__file__).resolve().parent/"web_launcher.py"
        return [sys.executable,str(launcher)] if launcher.exists() else None

    def _web_status_path(self):
        base=os.environ.get("LOCALAPPDATA") or str(Path.home())
        folder=Path(base)/"CraneVehicleEngineeringTool"/"web"
        folder.mkdir(parents=True,exist_ok=True)
        return folder/"web_status.json"

    def _reset_web_link_ui(self):
        self.currentWebUrl=""
        if hasattr(self,"openWebLinkButton"):
            self.openWebLinkButton.setEnabled(False)
        if hasattr(self,"copyWebLinkButton"):
            self.copyWebLinkButton.setEnabled(False)

    def _start_web_status_monitor(self):
        if not hasattr(self,"webStatusTimer"):
            self.webStatusTimer=QTimer(self)
            self.webStatusTimer.setInterval(700)
            self.webStatusTimer.timeout.connect(self._poll_web_server_status)
        self.webStatusTimer.start()
        QTimer.singleShot(120000, lambda: self.webStatusTimer.stop() if self.webStatusTimer.isActive() and not getattr(self,"currentWebUrl","") else None)

    def _poll_web_server_status(self):
        path=self._web_status_path()
        if not path.exists():
            return
        try:
            data=json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            return
        state=str(data.get("state","")).strip().lower()
        url=str(data.get("url","")).strip()
        message=str(data.get("message","")).strip()
        mode=str(data.get("mode","")).strip()

        if url and state=="ready":
            self.currentWebUrl=url
            if hasattr(self,"webServerStatusLabel"):
                self.webServerStatusLabel.setText(f"{mode}: {url}")
                self.webServerStatusLabel.setTextInteractionFlags(Qt.TextSelectableByMouse)
            if hasattr(self,"openWebLinkButton"):
                self.openWebLinkButton.setEnabled(True)
            if hasattr(self,"copyWebLinkButton"):
                self.copyWebLinkButton.setEnabled(True)
            if hasattr(self,"webStatusTimer"):
                self.webStatusTimer.stop()
            return

        if message and hasattr(self,"webServerStatusLabel"):
            self.webServerStatusLabel.setText(message)

        if state=="error":
            if hasattr(self,"webStatusTimer"):
                self.webStatusTimer.stop()
            if message:
                QMessageBox.warning(self,"Web Server",message)

    def open_current_web_link(self):
        url=getattr(self,"currentWebUrl","").strip()
        if not url:
            QMessageBox.information(self,"Web Link","ยังไม่มีลิงก์ครับ\nรอให้ Web Server แสดงสถานะพร้อมใช้งานก่อน")
            return
        try:
            webbrowser.open(url)
        except Exception as ex:
            QMessageBox.warning(self,"Web Link",f"เปิด Browser ไม่สำเร็จ:\n{ex}")

    def copy_current_web_link(self):
        url=getattr(self,"currentWebUrl","").strip()
        if not url:
            QMessageBox.information(self,"Web Link","ยังไม่มีลิงก์ให้คัดลอก")
            return
        QApplication.clipboard().setText(url)
        if hasattr(self,"webServerStatusLabel"):
            self.webServerStatusLabel.setText(f"คัดลอกแล้ว: {url}")

    def launch_web_server_dialog(self):
        cmd=self._web_server_command()
        if not cmd:
            QMessageBox.warning(
                self,"Web Server not found",
                "ไม่พบ CraneVehicleWebServer.exe\n\n"
                "กรุณาอัปเดต/ติดตั้ง V53.4.1 หรือใหม่กว่า แล้วลองอีกครั้ง."
            )
            return

        choices=[
            "FREE PERMANENT LINK — Tailscale Funnel (*.ts.net) [แนะนำ]",
            "QUICK PUBLIC LINK — Cloudflare (ลิงก์สุ่ม)",
            "LAN / Wi-Fi — เครือข่ายเดียวกัน",
            "LOCAL — ใช้เฉพาะเครื่องนี้",
        ]
        choice,ok=QInputDialog.getItem(
            self,"เปิด Web Server","เลือกโหมดการเปิดเว็บ:",choices,0,False
        )
        if not ok:return

        args=list(cmd)
        mode="PERMANENT"
        if choice.startswith("FREE PERMANENT"):
            host_name,okhost=QInputDialog.getText(
                self,"ชื่อ Web Link",
                "ตั้งชื่อส่วนหน้าของลิงก์ *.ts.net\nตัวอย่าง: cvet → https://cvet.<tailnet>.ts.net",
                QLineEdit.Normal,
                "cvet"
            )
            if not okhost:return
            host_name=re.sub(r"[^a-zA-Z0-9-]+","-",host_name.strip().lower()).strip("-") or "cvet"
            args.extend(["--tailscale","--tailscale-hostname",host_name])
            pin,okpin=QInputDialog.getText(
                self,"Web PIN (แนะนำ)",
                "ตั้ง PIN สำหรับลิงก์ถาวร\nเว้นว่างได้ แต่แนะนำให้ตั้ง:",
                QLineEdit.Password
            )
            if not okpin:return
            pin=pin.strip()
            if pin:args.extend(["--pin",pin])
        elif choice.startswith("QUICK PUBLIC"):
            mode="QUICK";args.append("--public")
            pin,okpin=QInputDialog.getText(
                self,"Web PIN (แนะนำ)",
                "ตั้ง PIN สำหรับคนที่เปิดลิงก์เว็บ\nเว้นว่างได้ แต่แนะนำให้ตั้ง:",
                QLineEdit.Password
            )
            if not okpin:return
            pin=pin.strip()
            if pin:args.extend(["--pin",pin])
        elif choice.startswith("LAN"):
            mode="LAN";args.append("--lan")
        else:
            mode="LOCAL"

        try:
            self._reset_web_link_ui()
            try:
                self._web_status_path().unlink(missing_ok=True)
            except Exception:
                pass
            kwargs={}
            if os.name=="nt":
                kwargs["creationflags"]=getattr(subprocess,"CREATE_NEW_CONSOLE",0)
            subprocess.Popen(args,**kwargs)
            self._start_web_status_monitor()
            if hasattr(self,"webServerStatusLabel"):
                self.webServerStatusLabel.setText(
                    f"{mode} Server กำลังเปิด • Browser จะเปิดอัตโนมัติเมื่อ Server พร้อม"
                )
            if mode=="PERMANENT":
                detail=("FREE PERMANENT LINK:\n"
                        "• ครั้งแรกโปรแกรมจะช่วยติดตั้ง/เปิด Tailscale\n"
                        "• Login Tailscale ฟรี 1 ครั้ง\n"
                        "• อนุญาต Funnel 1 ครั้ง\n"
                        "• จากนั้นจะได้ลิงก์ HTTPS แบบ https://cvet.<tailnet>.ts.net\n"
                        "• ลิงก์เดิมใช้ซ้ำได้ ไม่สุ่มใหม่ทุกครั้ง\n")
            elif mode=="QUICK":
                detail=("QUICK PUBLIC: รอ Server แสดงลิงก์ https://xxxxx.trycloudflare.com\n"
                        "ลิงก์นี้จะเปลี่ยนเมื่อปิดแล้วเปิดใหม่\n")
            else:
                detail="Browser จะเปิดหน้า Web Calculator อัตโนมัติ\n"
            QMessageBox.information(
                self,"Web Server",
                "กำลังเปิด Web Server แล้วครับ\n\n"+detail+
                "\nอย่าปิดหน้าต่าง Web Server ระหว่างที่ต้องการให้คนอื่นเข้าเว็บ"
            )
        except Exception as ex:
            QMessageBox.critical(self,"Web Server",f"เปิด Web Server ไม่สำเร็จ:\n{ex}")

    def show_web_server_help(self):
        QMessageBox.information(
            self,"วิธีใช้ Web Server",
            "โหมดแนะนำ: FREE PERMANENT LINK\n"
            "1) กด ‘เปิด Web Server’\n"
            "2) เลือก FREE PERMANENT LINK — Tailscale Funnel\n"
            "3) ครั้งแรกติดตั้งและ Login Tailscale ฟรี\n"
            "4) อนุญาต Funnel 1 ครั้ง\n"
            "5) โปรแกรมจะได้ลิงก์ https://cvet.<tailnet>.ts.net\n"
            "6) ครั้งต่อไปใช้ลิงก์เดิมได้ ไม่ต้องซื้อ Domain\n\n"
            "QUICK PUBLIC LINK ยังใช้ Cloudflare ได้เหมือนเดิม แต่ URL จะสุ่มใหม่\n"
            "เครื่องนี้ต้องเปิด CVET Web Server และ Tailscale ขณะใช้งานเว็บ"
        )

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

    def show_hardware_mode(self):
        self._show_only_page(self.hardwarePage)
        self._set_active_nav("hardware")
        self.update_hardware_manager()

    def show_telemetry_mode(self):
        self._show_only_page(self.telemetryPage)
        self._set_active_nav("telemetry")
        self.refresh_serial_ports()
        self.refresh_telemetry_local_ips()
        self.refresh_telemetry_code_view()
        self.update_telemetry_ui()

    def show_integration_suite_mode(self):
        self._show_only_page(self.integrationPage)
        self._set_active_nav("integration")
        self.refresh_integration_suite()

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
        chips.addWidget(make_chip(f"V{APP_VERSION}  ENGINEERING SUITE","#ffffff","#174a74"))
        chips.addWidget(make_chip("AUTO UPDATE","#dff3ff","#174a74"))
        chips.addStretch(1);left.addLayout(chips)

        title=QLabel("CRANE VEHICLE ENGINEERING TOOL")
        tf=QFont();tf.setPointSize(20);tf.setBold(True);title.setFont(tf)
        title.setStyleSheet("color:white;background:transparent;")
        left.addWidget(title)

        sub=QLabel("คำนวณ • Hardware I/O • Telemetry • Validation • Diagnostics • BOM • Revisions • Final Verification ในโปรแกรมเดียว")
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
        repairUpdate=QPushButton("Repair Update");repairUpdate.setToolTip("Reset update source to official GitHub latest.json and check again");repairUpdate.clicked.connect(lambda:self.reset_update_source(True))
        updateSettings=QPushButton("Settings");updateSettings.setObjectName("secondaryButton");updateSettings.clicked.connect(self.show_update_settings)
        ur.addWidget(checkUpdate);ur.addWidget(self.updateNowButton);ur.addWidget(repairUpdate);ur.addWidget(updateSettings);upl.addLayout(ur)
        system.addWidget(updatePanel,1)

        webPanel=QFrame();webPanel.setObjectName("softPanel")
        wpl=QVBoxLayout(webPanel);wpl.setContentsMargins(15,11,15,11);wpl.setSpacing(7)
        webTitle=QLabel("WEB SERVER  •  FREE PERMANENT LINK")
        webTitle.setStyleSheet("color:#173f5f;font-size:10.5pt;font-weight:900;")
        self.webServerStatusLabel=QLabel("ฟรี • ลิงก์ HTTPS เดิมผ่าน Tailscale Funnel • Quick Cloudflare ยังใช้ได้")
        self.webServerStatusLabel.setWordWrap(True);self.webServerStatusLabel.setStyleSheet("color:#667b8e;font-size:9.2pt;")
        wpl.addWidget(webTitle);wpl.addWidget(self.webServerStatusLabel)
        wr=QHBoxLayout()
        self.openWebServerButton=QPushButton("เปิด Web Server")
        self.openWebServerButton.setObjectName("primaryButton")
        self.openWebServerButton.setToolTip("แนะนำ Free Permanent Link (*.ts.net) • รองรับ Quick Public / LAN / Local")
        self.openWebServerButton.clicked.connect(self.launch_web_server_dialog)
        self.openWebLinkButton=QPushButton("เปิดลิงก์")
        self.openWebLinkButton.setObjectName("secondaryButton")
        self.openWebLinkButton.setEnabled(False)
        self.openWebLinkButton.clicked.connect(self.open_current_web_link)
        self.copyWebLinkButton=QPushButton("คัดลอกลิงก์")
        self.copyWebLinkButton.setObjectName("secondaryButton")
        self.copyWebLinkButton.setEnabled(False)
        self.copyWebLinkButton.clicked.connect(self.copy_current_web_link)
        webHelp=QPushButton("วิธีใช้");webHelp.setObjectName("secondaryButton");webHelp.clicked.connect(self.show_web_server_help)
        wr.addWidget(self.openWebServerButton);wr.addWidget(self.openWebLinkButton);wr.addWidget(self.copyWebLinkButton);wr.addWidget(webHelp);wr.addStretch(1);wpl.addLayout(wr)
        system.addWidget(webPanel,1)
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
        be=ModeCardButton("ELECTRICAL / BATTERY","Trip Summary • Battery Selection • BMS","02","#0f8a73")
        bw=ModeCardButton("WINCH","แรงยก • ความเร็ว • เวลา • 12 V Battery","03","#d97706")
        bs=ModeCardButton("STABILITY","Side / Front / Rear tipping • Worst Case • CG","04","#7c3aed")
        bc=ModeCardButton("CONTROL LOGIC","E-stop • RC Failsafe • IMU • Limit • Interlock","05","#c45114")
        bv=ModeCardButton("VARIABLE DICTIONARY","ความหมายตัวแปร • หน่วย • ค่าปัจจุบัน","06","#4b647a")
        bh=ModeCardButton("HARDWARE I/O & WIRING","Animated Board • All GPIO • Used/Free/Conflict","07","#0b7a75")
        btele=ModeCardButton("LIVE TELEMETRY","ESP32 WiFi/Serial • Live Graph • CSV Data Logger","08","#087e8b")
        binteg=ModeCardButton("ENGINEERING SUITE","Validation • Diagnostics • BOM • Revisions • Final Check","09","#5b4bb7")

        cards.addWidget(bt,0,0);cards.addWidget(be,0,1)
        cards.addWidget(bw,1,0);cards.addWidget(bs,1,1)
        cards.addWidget(bc,2,0);cards.addWidget(bv,2,1)
        cards.addWidget(bh,3,0);cards.addWidget(btele,3,1)
        cards.addWidget(binteg,4,0,1,2)
        cards.setColumnStretch(0,1);cards.setColumnStretch(1,1)
        root.addLayout(cards)

        bt.clicked.connect(self.show_torque_mode)
        be.clicked.connect(self.show_electrical_mode)
        bw.clicked.connect(self.show_winch_mode)
        bs.clicked.connect(self.show_stability_mode)
        bc.clicked.connect(self.show_safety_logic_mode)
        bv.clicked.connect(self.show_variable_dictionary_mode)
        bh.clicked.connect(self.show_hardware_mode)
        btele.clicked.connect(self.show_telemetry_mode)
        binteg.clicked.connect(self.show_integration_suite_mode)

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

    def reset_update_source(self,check_now=True):
        """Reset a stale/custom updater source back to the official GitHub manifest."""
        self.save_update_config(DEFAULT_UPDATE_MANIFEST_URL,True)
        self.pending_update_manifest=None
        if hasattr(self,"updateNowButton"):self.updateNowButton.setEnabled(False)
        self._set_update_status(f"รีเซ็ต Update Source แล้ว • Current V{APP_VERSION}")
        if check_now:
            self.check_for_update(False)

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
            # Avoid stale latest.json responses from GitHub/CDN just after a release.
            cache_token=str(int(time.time()*1000))
            sep="&" if "?" in src else "?"
            fetch_url=src+sep+"_cvet="+cache_token
            req=urllib.request.Request(fetch_url,headers={
                "User-Agent":f"{APP_NAME}/{APP_VERSION}",
                "Cache-Control":"no-cache, no-store, max-age=0",
                "Pragma":"no-cache",
            })
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
        data["_source"]=src
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
                source=manifest.get("_source",self.load_update_config().get("manifest_url",""))
                self._set_update_status(f"มีเวอร์ชันใหม่ V{latest} • Current V{APP_VERSION}",ok=True)
                if not result.get("silent"):
                    msg=f"พบเวอร์ชันใหม่ V{latest}\\n\\nCurrent: V{APP_VERSION}\\nSource: {source}"
                    if notes:msg+="\\n\\n"+notes
                    msg+="\\n\\nต้องการดาวน์โหลดและอัปเดตตอนนี้หรือไม่?"
                    if QMessageBox.question(self,"Update Available",msg,QMessageBox.Yes|QMessageBox.No,QMessageBox.Yes)==QMessageBox.Yes:
                        self.download_pending_update()
            else:
                self.pending_update_manifest=None
                if hasattr(self,"updateNowButton"):self.updateNowButton.setEnabled(False)
                self._set_update_progress(100)
                source=manifest.get("_source",self.load_update_config().get("manifest_url",""))
                self._set_update_status(f"Current V{APP_VERSION} • Latest V{latest}",ok=True)
                if not result.get("silent"):
                    QMessageBox.information(
                        self,"Check for Update",
                        f"Current: V{APP_VERSION}\\nLatest from manifest: V{latest}\\n\\nSource:\\n{source}"
                    )

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
        q=self.winch_results();b=self.winch_battery_results() if hasattr(self,"wbVoltage") else None;sp=self.winch_speed_results()
        rows=[
            ("m_load","มวลสิ่งที่ต้องการยก","kg",f"{self.wmass.value():.2f}","Payload หลัก"),
            ("m_basket","มวลตะกร้า/อุปกรณ์ยก","kg",f"{self.wbasket.value():.2f}","รวมกับ Payload ก่อนหาแรงยก"),
            ("h","ความสูงยกแนวดิ่ง","m",f"{self.wheight.value():.2f}","ใช้หาเวลาและพลังงาน mgh"),
            ("V","แรงดันแบตเตอรี่วินช์","V",f"{q['v']:.1f}","แบต 12 V แยกจากระบบรถ"),
            ("P_rated","กำลังพิกัดตามฉลากวินช์","W",f"{self.wrated.value():.0f}","ไม่ใช้แทนกระแสจริงโดยอัตโนมัติ"),
            ("i","อัตราทดเกียร์วินช์","-",f"{self.wratio.value():.0f}:1","ใช้แปลงรอบ/แรงบิดระหว่างมอเตอร์กับดรัม"),
            ("v_up","ความเร็วโหลดขาขึ้น","m/min",f"{q['up_speed']:.3f}","ใช้หาเวลายก"),
            ("v_down","ความเร็วโหลดขาลง","m/min",f"{q['down_speed']:.3f}","ใช้หาเวลาลด"),
            ("I_up","กระแสขณะยก","A",f"{q['iup']:.2f}","interpolate จากตาราง First Layer ของใบสเปก"),
            ("I_down","กระแสขณะลด","A",f"{q['idown']:.2f}","มาจาก Down mode ในแท็บ Battery"),
            ("N_event","จำนวนงานยกสัตว์","งาน",str(q["n"]),"ดึงจาก Operating Cycles หรือ Manual ใน Battery"),
            ("DoD","สัดส่วนแบตเตอรี่ที่อนุญาตให้ใช้","%",f"{q['dod']*100:.1f}","ตั้งในแท็บ Battery"),
            ("Reserve","พลังงานสำรอง","%",f"{q['reserve']*100:.1f}","ตั้งในแท็บ Battery"),
            ("D_drum","เส้นผ่านศูนย์กลางดรัม","mm",f"{self.wdiameter.value():.1f}","Ø37 mm จากใบสเปก"),
            ("SF_force","ตัวคูณแรงวิเคราะห์เบื้องต้น","-",f"{self.wsf.value():.2f}","ไม่ใช่ WLL ของอุปกรณ์ยก"),
            ("t_up","เวลายกขึ้น","s",f"{q['tu']:.1f}","h ÷ v_up"),
            ("t_down","เวลาลดลง","s",f"{q['td']:.1f}","h ÷ v_down"),
            ("F_lift","แรงยกเชิงน้ำหนัก","N",f"{q['f']:.1f}","(m_load + m_basket) × g"),
            ("E_total","พลังงานไฟฟ้ารวมตามจำนวนรอบ","Wh",f"{q['total']:.2f}","รวมขาขึ้นและขาลง"),
            ("Ah","ความจุแบตเตอรี่ที่คำนวณได้","Ah",f"{q['ah']:.2f}","ยังต้องตรวจ BMS/กระแสกระชาก"),
            ("n_motor","รอบมอเตอร์โดยอนุมานจาก Line Speed","rpm",f"{sp['motor_up']:.0f}","derived จาก line speed, drum Ø37 mm และ ratio 136:1; ไม่ใช่ค่าที่ใบสเปกระบุ"),
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
            ("VESC_FAULT","สถานะ VESC / Motor Fault","Boolean","ON" if v["vesc_fault"] else "OFF","ON = Drive 0 + Crane STOP + Alarm"),
            ("CH5","Drive Enable จากรีโมท","Boolean","ON" if v["drive_enable"] else "OFF","OFF = ไม่อนุญาต Drive"),
            ("STOP_0.5s","รถหยุดนิ่งต่อเนื่องอย่างน้อย 0.5 s","Boolean","YES" if v["stationary_05"] else "NO","ต้องเป็น YES ก่อนอนุญาต Crane"),
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
        self.safetyVescFault=QCheckBox("VESC / Motor Fault")
        self.safetyDriveEnable=QCheckBox("CH5 Drive Enable");self.safetyDriveEnable.setChecked(True)
        self.safetyStationary05=QCheckBox("Vehicle stopped ≥ 0.5 s");self.safetyStationary05.setChecked(True)
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
        il.addRow("VESC / Motor fault",self.safetyVescFault)
        il.addRow("Drive enable / CH5",self.safetyDriveEnable)
        il.addRow("Vehicle stationary",self.safetyStationary05)
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
        <p><b>3. VESC / Motor Fault</b> → Drive OFF + Crane STOP + Alarm</p>
        <p><b>4. IMU Tilt ≥ Limit</b> → Drive INHIBIT + Buzzer/LED</p>
        <p><b>5. Drive + Crane พร้อมกัน</b> → Interlock → ปฏิเสธทั้งสองคำสั่ง</p>
        <p><b>6. รถกำลังวิ่ง</b> → ห้ามหมุนเครน</p>
        <p><b>7. รถต้องหยุดนิ่ง ≥ 0.5 s</b> → จึงอนุญาต Crane</p>
        <p><b>8. เครนกำลังหมุน</b> → ห้าม Drive</p>
        <p><b>9. Limit ±90°</b> → ห้ามหมุนต่อเข้า Limit แต่ยังหมุนย้อนออกได้</p>
        <p><b>10. Differential steering</b> → Steering อย่างเดียวสามารถ Pivot Turn</p>
        <p><b>11. Battery Low policy</b> → ถ้าเลือก Inhibit จะล็อก Drive</p>
        <p><b>12. Buzzer + LED</b> → ON ขณะเคลื่อนที่ หรือเมื่อเกิด Fault/Warning</p>
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

        for obj in (self.safetyEStop,self.safetyRCSignal,self.safetyVescFault,self.safetyDriveEnable,self.safetyStationary05,
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
            "vesc_fault":self.safetyVescFault.isChecked(),
            "drive_enable":self.safetyDriveEnable.isChecked(),
            "stationary_05":self.safetyStationary05.isChecked(),
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
        if v.get("vesc_fault",False):
            result.update(state="VESC FAULT",reason="VESC / Motor Fault — Drive = 0, Crane STOP และแจ้งเตือน",buzzer=True,led=True)
            return result

        throttle=int(v.get("throttle",0))
        steer=int(v.get("steer",0))
        crane=str(v.get("crane","STOP"))
        winch=str(v.get("winch","STOP"))
        drive_req=abs(throttle)>2 or abs(steer)>2
        crane_req=crane!="STOP"
        winch_req=winch!="STOP"
        tilt_fault=abs(float(v.get("tilt",0)))>=float(v.get("tilt_limit",12))
        drive_enabled=bool(v.get("drive_enable",True))
        stationary_05=bool(v.get("stationary_05",True))
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
                    reason="Drive Enable ผ่าน — ล็อก Crane และส่ง Differential command ไป VESC",
                    drive_permit=True,drive_active=True,left_motor=left,right_motor=right,
                    buzzer=True,led=True
                )

        elif crane_req:
            result["drive_permit"]=False
            if not stationary_05:
                result.update(state="WAIT VEHICLE STOP",reason="Drive command เป็น 0 แล้ว แต่รถยังหยุดนิ่งไม่ครบ 0.5 s — Crane ยังถูกล็อก",led=True)
            else:
                blocked=False
                if crane.startswith("LEFT") and v.get("left_limit",False):
                    blocked=True
                    result.update(state="LEFT LIMIT STOP",reason="ถึง Limit -90° — ห้ามหมุน LEFT ต่อ แต่ยังสั่ง RIGHT เพื่อออกจาก Limit ได้",buzzer=True,led=True)
                elif crane.startswith("RIGHT") and v.get("right_limit",False):
                    blocked=True
                    result.update(state="RIGHT LIMIT STOP",reason="ถึง Limit +90° — ห้ามหมุน RIGHT ต่อ แต่ยังสั่ง LEFT เพื่อออกจาก Limit ได้",buzzer=True,led=True)
                if not blocked:
                    result.update(state="CRANE",reason=f"รถหยุดนิ่ง ≥0.5 s — อนุญาตให้เครนหมุน {crane}",crane=crane,buzzer=True,led=True)

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
            stationary_block=v.get("winch_stationary_only",True) and not stationary_05
            if v.get("winch_stationary_only",True) and (movement_active or stationary_block):
                result["reason"] += " | Winch ถูกปฏิเสธเพราะรถ/เครนยังไม่อยู่ในสถานะหยุดนิ่ง"
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
            "WAIT VEHICLE STOP":("#fff6df","#9a5a00","#efd08b"),
            "VESC FAULT":("#fff0f0","#b42318","#efb2ad"),
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
        self.safetyVescFault.setChecked(False)
        self.safetyDriveEnable.setChecked(True)
        self.safetyStationary05.setChecked(True)
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
            "estop":False,"rc_ok":True,"vesc_fault":False,"drive_enable":True,"stationary_05":True,
            "throttle":0,"steer":0,"crane":"STOP","winch":"STOP","tilt":0.0,"tilt_limit":12.0,
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
            ("VESC FAULT",{"vesc_fault":True,"throttle":60},lambda r:r["state"]=="VESC FAULT" and not r["drive_permit"] and r["crane"]=="STOP"),
            ("IMU TILT INHIBIT",{"throttle":50,"tilt":15},lambda r:r["state"]=="TILT INHIBIT" and not r["drive_permit"]),
            ("CRANE WAIT 0.5s",{"crane":"LEFT (-)","stationary_05":False},lambda r:r["state"]=="WAIT VEHICLE STOP" and r["crane"]=="STOP"),
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
            self.show_home_mode,"V53 TOOLS","#e8f4ff","#174a74"))
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
        if hasattr(self,"eCandidateAh"):
            self.eCandidateAh.valueChanged.connect(lambda v:self.mainSelectedAh.setValue(v))
            self.eCandidateContA.valueChanged.connect(lambda v:self.mainBMSCont.setValue(v))
            self.eCandidatePeakA.valueChanged.connect(lambda v:self.mainBMSPeak.setValue(v))
            self.mainSelectedAh.valueChanged.connect(lambda v:self.eCandidateAh.setValue(v))
            self.mainBMSCont.valueChanged.connect(lambda v:self.eCandidateContA.setValue(v))
            self.mainBMSPeak.valueChanged.connect(lambda v:self.eCandidatePeakA.setValue(v))
            self._sync_project_tools_to_battery_candidate()
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
        if hasattr(self,"hwRows"):self.update_hardware_manager()


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
            # V52.6 project migration: the user's main controller target is now classic ESP32.
            # Apply only to automatic last-values restore; manually opened old project files keep their board choice.
            if hasattr(self,"hwBoardProfile") and self._version_tuple(state.get("version","0")) < self._version_tuple("52.6.0"):
                self.hwBoardProfile.setCurrentIndex(3)
                self.refresh_gpio_combo_items()
                self.update_hardware_manager()
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

        # Hardware I/O row widgets live inside self.hwRows dictionaries, not directly in vars(self).
        if hasattr(self,"hwRows"):
            for row in self.hwRows:
                try:
                    row["enabled"].toggled.connect(self.schedule_easy_autosave)
                    row["supply"].currentIndexChanged.connect(self.schedule_easy_autosave)
                    row["logic"].currentIndexChanged.connect(self.schedule_easy_autosave)
                    row["gpio"].currentIndexChanged.connect(self.schedule_easy_autosave)
                    row["protection"].currentIndexChanged.connect(self.schedule_easy_autosave)
                except Exception:
                    pass

        # Periodic safety save in case the program is left open for a long time.
        self.easyAutoSavePeriodic=QTimer(self)
        self.easyAutoSavePeriodic.timeout.connect(lambda:self.save_last_values(silent=True))
        self.easyAutoSavePeriodic.start(60000)

    def closeEvent(self,event):
        # Always stop serial/network acquisition and save once more.
        try:self.disconnect_telemetry(silent=True)
        except Exception:pass
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
        hardware=[]
        if hasattr(self,"hwRows"):
            for row in self.hwRows:
                hardware.append({
                    "key":row["key"],
                    "enabled":row["enabled"].isChecked(),
                    "device":row.get("device",""),
                    "signal":row.get("signal",""),
                    "interface":row.get("interface",""),
                    "supply":row["supply"].currentText(),
                    "logic":row["logic"].currentText(),
                    "gpio":row["gpio"].currentText(),
                    "protection":row["protection"].currentText(),
                    "note":row.get("note",""),
                    "custom":bool(row.get("custom",False)),
                })
        integration={}
        if hasattr(self,"deviceLibraryTable"):integration["device_library"]=self._table_rows_text(self.deviceLibraryTable)
        if hasattr(self,"validationTable"):integration["validation"]=self._table_rows_text(self.validationTable)
        if hasattr(self,"bomTable"):integration["bom"]=self._table_rows_text(self.bomTable)
        if hasattr(self,"designRevisions"):integration["revisions"]=self.designRevisions
        return {"format":"CraneVehicleEngineeringToolProject","version":APP_VERSION,
                "saved_at":datetime.now().isoformat(timespec="seconds"),"widgets":widgets,
                "components":components,"hardware":hardware,"integration":integration}

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
        if hasattr(self,"hwRows"):
            saved_list=[x for x in state.get("hardware",[]) if isinstance(x,dict)]
            # Remove current custom rows first, then rebuild them from the project file.
            for i in range(len(self.hwRows)-1,-1,-1):
                if self.hwRows[i].get("custom",False):
                    self.hwRows.pop(i);self.hwTable.removeRow(i)
            existing={x["key"] for x in self.hwRows}
            for data in saved_list:
                if not data.get("custom",False) or data.get("key") in existing:continue
                definition=dict(key=str(data.get("key") or self._hardware_key(data.get("signal","CUSTOM_IO"),existing)),
                                device=str(data.get("device","Custom Device")),
                                signal=str(data.get("signal","Custom I/O")),
                                interface=str(data.get("interface","Digital IN")),
                                supply=str(data.get("supply","3.3V")),logic=str(data.get("logic","3.3V")),
                                gpio=str(data.get("gpio","Not assigned")),protection=str(data.get("protection","Direct")),
                                note=str(data.get("note","")),allowed_supply=tuple(self._hardware_supply_items()),
                                custom=True,enabled=bool(data.get("enabled",True)))
                self._append_hardware_row(definition);existing.add(definition["key"])
            saved={x.get("key"):x for x in saved_list}
            for row in self.hwRows:
                data=saved.get(row["key"])
                if not data: continue
                row["enabled"].blockSignals(True);row["enabled"].setChecked(bool(data.get("enabled",True)));row["enabled"].blockSignals(False)
                for field in ("supply","logic","gpio","protection"):
                    combo=row[field];value=str(data.get(field,""))
                    idx=combo.findText(value)
                    if idx<0 and field in ("supply","logic","protection") and value:
                        combo.addItem(value);idx=combo.findText(value)
                    if idx>=0:
                        combo.blockSignals(True);combo.setCurrentIndex(idx);combo.blockSignals(False)
            self.update_hardware_manager()

        integration=state.get("integration",{}) if isinstance(state.get("integration",{}),dict) else {}
        if hasattr(self,"deviceLibraryTable"):
            self._load_table_rows_text(self.deviceLibraryTable,integration.get("device_library",[]))
        if hasattr(self,"validationTable"):
            self._load_table_rows_text(self.validationTable,integration.get("validation",[]))
            self.update_validation_results()
        if hasattr(self,"bomTable"):
            self._load_table_rows_text(self.bomTable,integration.get("bom",[]))
            self.update_bom_summary()
        if hasattr(self,"designRevisions") and "revisions" in integration:
            revs=integration.get("revisions",[])
            self.designRevisions=revs if isinstance(revs,list) else []
            self.refresh_revision_table()
        # Keep V52.2 Battery Selection and the older Project Tools Battery+BMS fields consistent.
        if all(hasattr(self,x) for x in ("eCandidateAh","eCandidateContA","eCandidatePeakA","mainSelectedAh","mainBMSCont","mainBMSPeak")):
            if "eCandidateAh" not in widgets and "mainSelectedAh" in widgets:
                self._sync_project_tools_to_battery_candidate()
            else:
                self._sync_battery_candidate_to_project_tools()
        # Sync derived wheel radius and mass mode after blocking signals.
        self.update_wheel_from_inches()
        if hasattr(self,"massModeSum") and self.massModeSum.isChecked(): self.apply_mass_mode()
        if recalculate:
            self._core_recalculate();self.update_project_tools()
            if hasattr(self,"integrationPage"):self.refresh_integration_suite()

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
            self.wmass.setValue(100);self.wheight.setValue(1.0);self.wvolt.setValue(12);self.wcycles.setValue(50)
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
        br=self.battery_selection_results() if hasattr(self,"bselTargetContC") else None
        winch_cont_req=w['iup'];label_current=self.wrated.value()/max(self.wvolt.value(),.1);winch_peak_ind=max(w['iup'],w.get("max_spec_current",140.0))
        def st(sel,req):
            if sel<=0:return "NOT SET / กรุณากรอก"
            return "PASS (preliminary)" if sel>=req else "CHECK / ต่ำกว่าค่าที่คำนวณ"
        return f"""<h2>BATTERY ENERGY + BMS CURRENT CHECK</h2>
        <p><b>หลักการ:</b> Ah/Wh ใช้ตรวจพลังงาน ส่วน A ใช้ตรวจความสามารถจ่ายกระแส ต้องผ่านทั้งสองส่วน</p>
        <h3>Main 72 V Drive</h3>
        {f"<p><b>Battery Selection:</b> minimum energy {br['energy_min']:.2f} Ah; design target including C-rate = {br['design_ah']:.2f} Ah; suggested standard size to investigate = <b>{br['suggested']:.0f} Ah</b> @ {e['V']:.0f} V.</p>" if br else ""}
        <table border='1' cellspacing='0' cellpadding='6'>
        <tr><td>Required design capacity</td><td>{e['Ah']:.2f} Ah @ {e['V']:.1f} V</td><td>Selected {self.mainSelectedAh.value():.1f} Ah → {st(self.mainSelectedAh.value(),e['Ah'])}</td></tr>
        <tr><td>Continuous-current indicator</td><td>max(Torque model {t['Ibatt']:.1f}, Calculated uphill {e['Icalc_up']:.1f}) = {main_cont_req:.1f} A</td><td>BMS {self.mainBMSCont.value():.1f} A → {st(self.mainBMSCont.value(),main_cont_req)}</td></tr>
        <tr><td>Peak/conservative indicator</td><td>max(Worst battery {e['Iworst']:.1f}, calculated accel {e.get('Icalc_peak',0):.1f}, controller-limit indicator {self.controllerCurrent.value()*t['n']:.1f}) = {main_peak_ind:.1f} A</td><td>BMS peak {self.mainBMSPeak.value():.1f} A → {st(self.mainBMSPeak.value(),main_peak_ind)}</td></tr></table>
        <h3>Winch 12 V Separate Battery</h3>
        <table border='1' cellspacing='0' cellpadding='6'>
        <tr><td>Required design capacity</td><td>{w['ah']:.2f} Ah @ {w['v']:.1f} V</td><td>Selected {self.winchSelectedAh.value():.1f} Ah → {st(self.winchSelectedAh.value(),w['ah'])}</td></tr>
        <tr><td>Interpolated current @ {w['m']:.1f} kg</td><td>{winch_cont_req:.1f} A (First-layer table)</td><td>BMS {self.winchBMSCont.value():.1f} A → {st(self.winchBMSCont.value(),winch_cont_req)}</td></tr>
        <tr><td>Manufacturer-table maximum</td><td>140 A at 4500 lb / 2041 kg first-layer pull; start/stall surge not stated</td><td>BMS peak {self.winchBMSPeak.value():.1f} A → {st(self.winchBMSPeak.value(),winch_peak_ind)}</td></tr></table>
        <p><b>ข้อจำกัด:</b> Controller current อาจเป็น phase/motor-current setting ไม่ใช่ battery current โดยตรง และ Winch stall current ยังไม่ทราบ จึงต้องยืนยัน datasheet/วัดจริงก่อนเลือก BMS ขั้นสุดท้าย</p>"""

    def update_bms_check(self):
        if hasattr(self,"bmsView"):self.bmsView.setHtml(self.bms_check_html())
        if hasattr(self,"wopSummary"):self.calc_winch_operation()
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
        else:add("Main Battery","Energy capacity",f"{e['Ah']:.2f} Ah required","Selected not set",False,"กรอกใน Battery Selection / Battery+BMS",True)
        if hasattr(self,"batterySelectionView"):
            br=self.battery_selection_results()
            add("Main Battery","Suggested standard size",f"≥ {br['design_ah']:.2f} Ah by energy/C-rate target",
                f"{br['suggested']:.0f} Ah standard size",False,f"Target {br['target_cont']:.1f}C continuous / {br['target_peak']:.1f}C peak",True)
        main_cont=max(t['Ibatt'],e['Icalc_up'])
        if self.mainBMSCont.value()>0:add("Main BMS","Continuous current",f"≥ {main_cont:.1f} A",f"{self.mainBMSCont.value():.1f} A",self.mainBMSCont.value()>=main_cont)
        else:add("Main BMS","Continuous current",f"≥ {main_cont:.1f} A","Not set",False,"กรอกพิกัด BMS",True)
        peak_calc=max(e['Iworst'],e.get('Icalc_peak',0))
        if self.mainBMSPeak.value()>0:add("Main BMS","Peak current (calculated)",f"≥ {peak_calc:.1f} A",f"{self.mainBMSPeak.value():.1f} A",self.mainBMSPeak.value()>=peak_calc,"VESC battery-current limit ต้องตรวจแยกจาก phase/motor current")
        else:add("Main BMS","Peak current (calculated)",f"≥ {peak_calc:.1f} A","Not set",False,"กรอกพิกัด Peak ของ Pack/BMS",True)
        if self.winchSelectedAh.value()>0:add("Winch Battery","Energy capacity",f"≥ {w['ah']:.2f} Ah",f"{self.winchSelectedAh.value():.1f} Ah",self.winchSelectedAh.value()>=w['ah'])
        else:add("Winch Battery","Energy capacity",f"{w['ah']:.2f} Ah required","Selected not set",False,"กรอกใน Battery+BMS",True)
        add("Winch","Duty cycle assumption",f"≤ {duty['allowed']:.1f}%",f"{duty['duty']:.1f}%",duty['duty_pass'],"Allowed value ยังเป็นสมมติฐาน",True if duty['allowed']==20 else False)
        add("Winch","Continuous run assumption",f"≤ {duty['maxcont']:.1f} s",f"{duty['maxsegment']:.1f} s",duty['continuous_pass'],"ใช้ข้อมูลผู้ผลิตเมื่อมี",True if duty['maxcont']==60 else False)
        if hasattr(self,"hwRows"):
            hw=self.hardware_check_results()
            issues=len(hw["conflicts"])+len(hw["voltage"])+len(hw["missing"])+len(hw["protection_missing"])
            add("Hardware I/O","GPIO / Voltage / Protection", "0 unresolved issue",
                f"{issues} issue(s)",hw["ready"],
                "V52 Hardware I/O Manager; READY requires verified board pinout")
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
        {self.final_verification_html()}<hr>{self.design_check_html()}<hr>{self.validation_report_html()}<hr>{self.bom_report_html()}<hr>{self.winch_duty_html()}""")

    def export_final_engineering_report(self):
        docs=QStandardPaths.writableLocation(QStandardPaths.DocumentsLocation) or str(Path.home())
        default_path=str(Path(docs)/"Crane_Vehicle_Final_Engineering_Report.pdf")
        filename,_=QFileDialog.getSaveFileName(self,"Export Final Engineering Report",default_path,"PDF (*.pdf)")
        if not filename:return
        if not filename.lower().endswith(".pdf"):filename+=".pdf"
        tmp=Path(tempfile.mkdtemp(prefix="cvet_final_report_"))
        try:
            self._core_recalculate();self.update_project_tools();self.refresh_integration_suite()
            t=self.torque_results();e=self.electrical_results();w=self.winch_results();worst=self.stability_worst_record()
            images=[]
            for name,widget in (("vehicle",getattr(self,"view",None)),
                                ("stability_map",getattr(self,"graph",None)),("motor_operating",getattr(self,"motorOpGraph",None)),
                                ("gpio_board",getattr(self,"hwBoardView",None)),("system_flowchart",getattr(self,"flowchartView",None))):
                if widget is not None:
                    fp=tmp/f"{name}.png"
                    if widget.grab().save(str(fp)):images.append((name,fp.as_uri()))
            img_html="".join(f"<h3>{name.replace('_',' ').title()}</h3><p><img src='{uri}' width='650'></p>" for name,uri in images)
            fbd_html=self.stability_fbd_report_html(tmp,self.inputs())
            page="<div style='page-break-before:always'></div>"
            winch_formula=re.sub(r"</?(?:html|body)(?:\s[^>]*)?>","",self.winch_html(w),flags=re.I)
            winch_speed_formula=re.sub(r"</?(?:html|body)(?:\s[^>]*)?>","",self.winch_speed_html(self.winch_speed_results()),flags=re.I)
            html=f"""<html><body style="font-family:'Leelawadee UI',Tahoma,'Segoe UI',Arial;font-size:10pt">
            <h1>CRANE VEHICLE — FINAL ENGINEERING REPORT</h1>
            <p>Version {APP_VERSION} | Generated {datetime.now().strftime('%Y-%m-%d %H:%M')}</p>
            <p><b>Scope:</b> Drive, Battery, Winch, Stability, Control, Hardware I/O, Validation, Diagnostics, BOM, Revisions and Final Verification.</p>
            {self.final_verification_html()}{page}
            {self.design_check_html()}{page}
            <h1>1. DRIVE TORQUE</h1>{self.torque_formula_html(t)}{page}
            <h1>2. ELECTRICAL / BATTERY</h1>{self.equation_html(e)}{page}
            <h1>3. WINCH</h1>{winch_formula}<hr>{winch_speed_formula}<hr>{self.winch_duty_html()}{page}
            <h1>4. STABILITY</h1>{self.stability_formula_html()}{page}
            <h1>4A. STABILITY FBD - ALL DIRECTIONS</h1>{fbd_html}{page}
            <h1>5. WORST CASE</h1><p>SF_worst = {worst[0]:.3f} at θ={worst[1]}° ({worst[2]}), target SF={self.req.value():.2f}</p>{page}
            <h1>6. BATTERY + BMS</h1>{self.bms_check_html()}{page}
            <h1>7. VALIDATION</h1>{self.validation_report_html()}{page}
            <h1>8. DIAGNOSTICS</h1>{self.diagnostic_report_html()}{page}
            <h1>9. BOM / COST / WEIGHT</h1>{self.bom_report_html()}{page}
            <h1>10. DESIGN REVISIONS</h1>{self.revision_report_html()}{page}
            <h1>11. FIGURES</h1>{img_html}
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


    # =====================================================================
    # V53.3 WINCH — SPEC-SHEET DRIVEN SINGLE-PAGE CALCULATOR
    # =====================================================================
    def _winch_locked_spec(self):
        return {
            "rated_pull_lb":4500.0,
            "rated_pull_kg":2041.0,
            "motor_kw":1.4,
            "motor_hp":1.9,
            "gear_ratio":136.0,
            "gear_train":"Differential Planetary",
            "rope_d_mm":5.0,
            "rope_len_m":10.0,
            "control":"Remote switch",
            "drum_d_mm":37.0,
            "drum_l_mm":72.0,
            "clutch":"Sliding Ring Gear",
            "braking":"Automatic In-The-Drum",
            "overall_mm":"316 × 120 × 106 mm",
            "mounting":"166 × 76 mm, Ø9 mm",
            "net_weight_kg":9.0,
            "gross_weight_kg":10.0,
            "packing":"43 × 30.5 × 36 cm, 2PC",
            "perf":[
                (0.0,3.3,12.0,"0"),
                (454.0,2.5,60.0,"1,000 lb / 454 kg"),
                (907.0,1.1,100.0,"2,000 lb / 907 kg"),
                (2041.0,0.8,140.0,"4,500 lb / 2041 kg"),
            ],
            "layers":[
                (1,"4500 lb / 2041 kg","4.9 ft / 1.5 m"),
                (2,"3520 lb / 1597 kg","14.2 ft / 4.4 m"),
                (3,"2600 lb / 1197 kg","18.7 ft / 5.8 m"),
                (4,"2050 lb / 930 kg","26.1 ft / 8.1 m"),
                (5,"1630 lb / 739 kg","32.3 ft / 10.0 m"),
            ],
            # Project assumptions not printed in the visible sheet.
            "project_load_kg":100.0,
            "project_lift_m":1.0,
            "project_voltage_v":12.0,
            "project_dod":0.80,
            "project_reserve":0.20,
            "force_sf":1.50,
        }

    def _winch_interp_first_layer(self,load_kg):
        spec=self._winch_locked_spec()
        pts=spec["perf"]
        x=max(pts[0][0],min(float(load_kg),pts[-1][0]))
        if x<=pts[0][0]:
            return pts[0][1],pts[0][2]
        for (x0,v0,i0,_),(x1,v1,i1,_) in zip(pts[:-1],pts[1:]):
            if x<=x1:
                frac=(x-x0)/(x1-x0) if x1>x0 else 0.0
                return v0+(v1-v0)*frac, i0+(i1-i0)*frac
        return pts[-1][1],pts[-1][2]

    def _winch_layer_for_distance(self,distance_m):
        """Estimate ending rope layer from cumulative rope-on-drum values on the supplied sheet."""
        d=max(0.0,float(distance_m))
        limits=[(1,1.5,2041.0),(2,4.4,1597.0),(3,5.8,1197.0),(4,8.1,930.0),(5,10.0,739.0)]
        for layer,cap,pull in limits:
            if d<=cap+1e-9:
                return layer,cap,pull
        return 5,10.0,739.0

    def _make_locked_winch_spin(self,value,maximum=100000.0,decimals=2):
        obj=QDoubleSpinBox(self.winchPage)
        obj.setRange(0.0,maximum);obj.setDecimals(decimals);obj.setValue(float(value))
        obj.setEnabled(False);obj.hide()
        return obj

    def _sync_locked_winch_widgets(self):
        spec=self._winch_locked_spec()
        load=self.wmass.value() if hasattr(self,"wmass") else spec["project_load_kg"]
        speed,current=self._winch_interp_first_layer(load)
        locked={
            "wbasket":0.0,
            "wvolt":spec["project_voltage_v"],
            "wrated":spec["motor_kw"]*1000.0,
            "wratio":spec["gear_ratio"],
            "wspeedup":speed,
            "wspeeddown":speed,
            "wiup":current,
            "widown":current,
            "wdod":spec["project_dod"]*100.0,
            "wreserve":spec["project_reserve"]*100.0,
            "wdiameter":spec["drum_d_mm"],
            "wsf":spec["force_sf"],
            "wdrumspeed":spec["drum_d_mm"],
            "wgear_eff":100.0,
            "wpulley_eff":100.0,
            "wmeasuredropeup":speed,
            "wmeasuredropedown":speed,
        }
        for attr,val in locked.items():
            obj=getattr(self,attr,None)
            if obj is not None and hasattr(obj,"setValue"):
                old=obj.blockSignals(True);obj.setValue(float(val));obj.blockSignals(old)
        if hasattr(self,"wparts"):
            old=self.wparts.blockSignals(True);self.wparts.setValue(1);self.wparts.blockSignals(old)
        d=spec["drum_d_mm"]/1000.0
        drum_rpm=speed/(math.pi*d) if d>0 else 0.0
        motor_rpm=drum_rpm*spec["gear_ratio"]
        for attr,val in (("wrpmup",motor_rpm),("wrpmdown",motor_rpm)):
            obj=getattr(self,attr,None)
            if obj is not None:
                old=obj.blockSignals(True);obj.setValue(val);obj.blockSignals(old)

    def make_winch(self):
        w=QWidget();self.winchPage=w
        outer=QVBoxLayout(w);outer.setContentsMargins(0,0,0,0);outer.setSpacing(0)
        self.wTabs=QTabWidget(w);self.wTabs.setDocumentMode(True);self.wTabs.setUsesScrollButtons(True)
        outer.addWidget(self.wTabs)
        scroll=QScrollArea();scroll.setWidgetResizable(True);scroll.setFrameShape(QFrame.NoFrame)
        content=QWidget();root=QVBoxLayout(content);root.setContentsMargins(18,16,18,20);root.setSpacing(12)
        scroll.setWidget(content);self.wTabs.addTab(scroll,"Spec / Datasheet")

        header=QFrame();header.setObjectName("topHeader");header.setMinimumHeight(96);add_soft_shadow(header,20,4,25)
        nav=QHBoxLayout(header);nav.setContentsMargins(18,14,18,14);nav.setSpacing(14)
        back=QPushButton("←  เมนูหลัก");back.setObjectName("secondaryButton");back.setMinimumWidth(120);back.clicked.connect(self.show_home_mode);nav.addWidget(back)
        textcol=QVBoxLayout();textcol.setSpacing(2)
        head=QLabel("4500LB. WINCH SPECIFICATION / DATASHEET")
        hf=QFont();hf.setPointSize(15);hf.setBold(True);head.setFont(hf);head.setStyleSheet("color:white;background:transparent;")
        subhead=QLabel("ยึดใบสเปกที่ผู้ใช้ส่งมา • ปรับเฉพาะ Load / Lift Distance • Battery คำนวณในแท็บ Battery เพียงจุดเดียว")
        subhead.setWordWrap(True);subhead.setStyleSheet("color:#dbeafe;font-size:10pt;font-weight:600;background:transparent;")
        textcol.addWidget(head);textcol.addWidget(subhead);nav.addLayout(textcol,1)
        nav.addWidget(make_chip("SPEC + 2 INPUTS","#fff1dd","#9a5800"))
        export=QPushButton("Export PDF");export.setObjectName("primaryButton");export.setMinimumWidth(140);export.clicked.connect(self.export_winch_pdf);nav.addWidget(export)
        root.addWidget(header)

        # Two editable design inputs on Datasheet: load and lift distance. Cycle count comes from Operating Cycles.
        self.wmass=QDoubleSpinBox(w);self.wmass.setRange(1.0,2041.0);self.wmass.setDecimals(1);self.wmass.setValue(100.0);self.wmass.setSuffix(" kg");self.wmass.setMinimumWidth(180)
        self.wheight=QDoubleSpinBox(w);self.wheight.setRange(0.05,10.0);self.wheight.setDecimals(2);self.wheight.setValue(1.0);self.wheight.setSuffix(" m");self.wheight.setMinimumWidth(180)
        # Remaining compatibility/report values stay hidden and locked.
        self.wbasket=self._make_locked_winch_spin(0)
        self.wvolt=self._make_locked_winch_spin(12)
        self.wrated=self._make_locked_winch_spin(1400)
        self.wratio=self._make_locked_winch_spin(136)
        self.wspeedup=self._make_locked_winch_spin(3.0)
        self.wspeeddown=self._make_locked_winch_spin(3.0)
        self.wiup=self._make_locked_winch_spin(20)
        self.widown=self._make_locked_winch_spin(20)
        self.wdod=self._make_locked_winch_spin(80)
        self.wreserve=self._make_locked_winch_spin(20)
        self.wdiameter=self._make_locked_winch_spin(37)
        self.wsf=self._make_locked_winch_spin(1.5)
        self.wrpmup=self._make_locked_winch_spin(3000)
        self.wrpmdown=self._make_locked_winch_spin(3000)
        self.wdrumspeed=self._make_locked_winch_spin(37)
        self.wgear_eff=self._make_locked_winch_spin(100)
        self.wpulley_eff=self._make_locked_winch_spin(100)
        self.wmeasuredropeup=self._make_locked_winch_spin(3.0)
        self.wmeasuredropedown=self._make_locked_winch_spin(3.0)
        self.wparts=QSpinBox(w);self.wparts.setRange(1,12);self.wparts.setValue(1);self.wparts.setEnabled(False);self.wparts.hide()
        self.wspeedmethod=QComboBox(w);self.wspeedmethod.addItem("Manufacturer spec interpolation");self.wspeedmethod.setEnabled(False);self.wspeedmethod.hide()
        self.wusecalc=QCheckBox(w);self.wusecalc.setChecked(True);self.wusecalc.setEnabled(False);self.wusecalc.hide()
        self.wSteps=QTextEdit(w);self.wSteps.setReadOnly(True)
        self.wSteps.setStyleSheet("font-size:11pt;padding:8px;")
        self.wSteps.hide()  # V53.3.8: formulas live inside Operation and Battery only
        self.wVars=QTextEdit(w);self.wVars.setReadOnly(True)
        self.wVars.setStyleSheet("font-size:10.5pt;padding:8px;")
        self.wVars.setReadOnly(True);self.wVars.hide()  # compatibility/PDF only
        self.wCalcSummary=QTextEdit(w);self.wCalcSummary.setReadOnly(True)
        self.wCalcSummary.setStyleSheet("font-size:11pt;padding:8px;")

        # V53.3.4 — Operating-cycle calculator: driving + winch UP/DOWN on outbound and return trips.
        opScroll=QScrollArea(w);opScroll.setWidgetResizable(True);opScroll.setFrameShape(QFrame.NoFrame)
        opContent=QWidget();opRoot=QVBoxLayout(opContent);opRoot.setContentsMargins(18,16,18,20);opRoot.setSpacing(12)
        opScroll.setWidget(opContent)
        opTitle=QLabel("OPERATING CYCLES / จำนวนรอบการทำงาน")
        of=QFont();of.setPointSize(15);of.setBold(True);opTitle.setFont(of);opTitle.setStyleSheet("color:#17324d;")
        opSub=QLabel(
            "1 รอบ = วิ่งไป + งานยกสัตว์ขาไป (วินช์ขึ้น+ลง) + วิ่งกลับ + "
            "งานยกสัตว์ขากลับ (วินช์ขึ้น+ลง) • Load และ Lift Distance ใช้ค่าจากหน้า Spec / Datasheet"
        )
        opSub.setWordWrap(True);opSub.setStyleSheet("color:#60758b;font-size:10.3pt;font-weight:650;")
        opRoot.addWidget(opTitle);opRoot.addWidget(opSub)

        opInputBox=QGroupBox("ข้อมูลการทำงาน / Operation Inputs")
        opForm=QFormLayout(opInputBox);opForm.setVerticalSpacing(10);opForm.setHorizontalSpacing(14)
        self.wopSpeed=QDoubleSpinBox(w);self.wopSpeed.setRange(0.05,50.0);self.wopSpeed.setDecimals(2);self.wopSpeed.setValue(1.0);self.wopSpeed.setSuffix(" km/h")
        self.wopDistance=QDoubleSpinBox(w);self.wopDistance.setRange(0.1,10000.0);self.wopDistance.setDecimals(2);self.wopDistance.setValue(30.0);self.wopDistance.setSuffix(" m")
        self.wopHours=QDoubleSpinBox(w);self.wopHours.setRange(0.01,48.0);self.wopHours.setDecimals(2);self.wopHours.setValue(3.0);self.wopHours.setSuffix(" h")
        self.wopEvents=QSpinBox(w);self.wopEvents.setRange(1,20);self.wopEvents.setValue(2);self.wopEvents.setSuffix(" งาน/รอบ")
        self.wopOther=QDoubleSpinBox(w);self.wopOther.setRange(0.0,36000.0);self.wopOther.setDecimals(1);self.wopOther.setValue(0.0);self.wopOther.setSuffix(" s/รอบ")
        for qx in (self.wopSpeed,self.wopDistance,self.wopHours,self.wopEvents,self.wopOther):qx.setMinimumWidth(190)
        opForm.addRow("ความเร็วรถ / Vehicle speed",self.wopSpeed)
        opForm.addRow("ระยะเที่ยวเดียว / One-way distance",self.wopDistance)
        opForm.addRow("เวลาทำงานรวม / Operating time",self.wopHours)
        opForm.addRow("งานยกสัตว์ต่อรอบ / Lift events per round",self.wopEvents)
        opForm.addRow("เวลาหยุดอื่นต่อรอบ / Other stop time",self.wopOther)
        opRoot.addWidget(opInputBox)

        opButtons=QHBoxLayout()
        opCalc=QPushButton("คำนวณรอบการทำงาน");opCalc.setObjectName("primaryButton");opCalc.clicked.connect(self.calc_winch_operation)
        self.wopApply=QPushButton("ส่งจำนวนงานยกไป Battery");self.wopApply.hide()  # compatibility only
        self.wopApply.clicked.connect(self.apply_winch_operation_cycles)
        opAuto=QLabel("จำนวนงานยกจากหน้านี้ถูกส่งไป Battery อัตโนมัติเมื่อเลือก “ใช้จำนวนงานยกจากหน้า รอบการทำงาน / 3h”")
        opAuto.setWordWrap(True);opAuto.setStyleSheet("color:#60758b;font-weight:650;")
        opButtons.addWidget(opCalc);opButtons.addWidget(opAuto,1);opRoot.addLayout(opButtons)

        self.wopSummary=QLabel();self.wopSummary.setWordWrap(True)
        self.wopSummary.setStyleSheet("font-size:12pt;font-weight:800;background:#eefaf4;color:#155b2a;padding:14px;border:1px solid #a9d7ba;border-radius:10px")
        opRoot.addWidget(self.wopSummary)
        self.wopDetails=QTextEdit(w);self.wopDetails.setReadOnly(True);self.wopDetails.setMinimumHeight(520)
        self.wopDetails.setStyleSheet("font-size:10.8pt;padding:8px;")
        opRoot.addWidget(self.wopDetails);opRoot.addStretch(1)
        self.wTabs.addTab(opScroll,"รอบการทำงาน / 3h")

        for qx in (self.wopSpeed,self.wopDistance,self.wopHours,self.wopEvents,self.wopOther):
            qx.valueChanged.connect(self.calc_winch_operation)

        # V53.3.5 — Advanced Winch Battery calculator.
        # Separates UP and DOWN energy and can use measured/custom lowering data.
        batScroll=QScrollArea(w);batScroll.setWidgetResizable(True);batScroll.setFrameShape(QFrame.NoFrame)
        batContent=QWidget();batRoot=QVBoxLayout(batContent);batRoot.setContentsMargins(18,16,18,20);batRoot.setSpacing(12)
        batScroll.setWidget(batContent)

        batTitle=QLabel("WINCH BATTERY / คำนวณแบตเตอรี่วินช์")
        btf=QFont();btf.setPointSize(15);btf.setBold(True);batTitle.setFont(btf);batTitle.setStyleSheet("color:#17324d;")
        batSub=QLabel(
            "แยกพลังงานขาขึ้นและขาลง • Conservative ใช้ค่าขาลงเท่าขาขึ้น • "
            "Measured / Custom ให้กรอก Current และ Speed หรือ Time ขาลงจริง"
        )
        batSub.setWordWrap(True);batSub.setStyleSheet("color:#60758b;font-size:10.3pt;font-weight:650;")
        batRoot.addWidget(batTitle);batRoot.addWidget(batSub)

        batInputs=QGroupBox("Battery Design Inputs / ข้อมูลออกแบบแบต")
        bif=QFormLayout(batInputs);bif.setVerticalSpacing(10);bif.setHorizontalSpacing(14)
        self.wbVoltage=QDoubleSpinBox(w);self.wbVoltage.setRange(6.0,60.0);self.wbVoltage.setDecimals(2);self.wbVoltage.setValue(12.0);self.wbVoltage.setSuffix(" V")
        self.wbEventMode=QComboBox(w)
        self.wbEventMode.addItems([
            "Auto — ใช้จำนวนงานยกจากรอบการทำงาน / 3h",
            "Manual — กำหนดจำนวนงานยกเอง"
        ])
        self.wbEventMode.setCurrentIndex(0);self.wbEventMode.setMinimumWidth(330)
        # Compatibility flag for saved state / older internal tools. The visible source selector is wbEventMode.
        self.wbUseOp=QCheckBox(w);self.wbUseOp.setChecked(True);self.wbUseOp.hide()
        self.wbEvents=QSpinBox(w);self.wbEvents.setRange(1,100000);self.wbEvents.setValue(64);self.wbEvents.setSuffix(" งาน")
        self.wbEventNote=QLabel(
            "Auto: โปรแกรมใช้จำนวนงานยกจากหน้า รอบการทำงาน / 3h โดยอัตโนมัติ\n"
            "Manual: กรอกจำนวนงานยกเองได้ • 1 งานยก = ขึ้น 1 ครั้ง + ลง 1 ครั้ง"
        )
        self.wbEventNote.setWordWrap(True)
        self.wbEventNote.setStyleSheet("background:#f2f7fd;color:#36566f;padding:10px;border:1px solid #c9d9e8;border-radius:9px")
        self.wbDoD=QDoubleSpinBox(w);self.wbDoD.setRange(1.0,100.0);self.wbDoD.setDecimals(1);self.wbDoD.setValue(80.0);self.wbDoD.setSuffix(" %")
        self.wbReserve=QDoubleSpinBox(w);self.wbReserve.setRange(0.0,200.0);self.wbReserve.setDecimals(1);self.wbReserve.setValue(20.0);self.wbReserve.setSuffix(" %")
        for qx in (self.wbVoltage,self.wbEvents,self.wbDoD,self.wbReserve):qx.setMinimumWidth(190)
        bif.addRow("System voltage / แรงดันระบบ",self.wbVoltage)
        bif.addRow("โหมดจำนวนงานยก / Lift event mode",self.wbEventMode)
        bif.addRow("จำนวนงานยกที่กำหนดเอง / Manual events",self.wbEvents)
        bif.addRow(self.wbEventNote)
        bif.addRow("Usable DoD",self.wbDoD)
        bif.addRow("Reserve",self.wbReserve)
        batRoot.addWidget(batInputs)

        downBox=QGroupBox("DOWN Calculation / การคำนวณขาลง")
        df=QFormLayout(downBox);df.setVerticalSpacing(10);df.setHorizontalSpacing(14)
        self.wbDownMode=QComboBox(w)
        self.wbDownMode.addItems(["Conservative — Down = Up","Measured / Custom"])
        self.wbDownBasis=QComboBox(w)
        self.wbDownBasis.addItems(["ใช้ Down Speed (m/min)","ใช้ Down Time (s)"])
        self.wbDownCurrent=QDoubleSpinBox(w);self.wbDownCurrent.setRange(0.0,1000.0);self.wbDownCurrent.setDecimals(2);self.wbDownCurrent.setValue(10.0);self.wbDownCurrent.setSuffix(" A")
        self.wbDownSpeed=QDoubleSpinBox(w);self.wbDownSpeed.setRange(0.01,100.0);self.wbDownSpeed.setDecimals(3);self.wbDownSpeed.setValue(3.0);self.wbDownSpeed.setSuffix(" m/min")
        self.wbDownTime=QDoubleSpinBox(w);self.wbDownTime.setRange(0.01,3600.0);self.wbDownTime.setDecimals(2);self.wbDownTime.setValue(30.0);self.wbDownTime.setSuffix(" s")
        for qx in (self.wbDownMode,self.wbDownBasis,self.wbDownCurrent,self.wbDownSpeed,self.wbDownTime):qx.setMinimumWidth(230)
        df.addRow("Mode",self.wbDownMode)
        df.addRow("Custom time method",self.wbDownBasis)
        df.addRow("Down current",self.wbDownCurrent)
        df.addRow("Down speed",self.wbDownSpeed)
        df.addRow("Down time",self.wbDownTime)
        downNote=QLabel(
            "ใบสเปก 4500LB ที่ใช้ในโปรแกรมไม่ให้ Current/Speed ขาลงแยกต่างหาก "
            "ดังนั้น Conservative เป็นค่าประมาณเพื่อออกแบบ ส่วน Measured / Custom ควรใช้ค่าที่วัดจากวินช์จริง."
        )
        downNote.setWordWrap(True);downNote.setStyleSheet("background:#fff8e9;color:#68420b;padding:10px;border:1px solid #ead39a;border-radius:9px")
        df.addRow(downNote)
        batRoot.addWidget(downBox)

        candidateBox=QGroupBox("Battery Check / ตรวจแบตที่จะซื้อ")
        cf=QFormLayout(candidateBox);cf.setVerticalSpacing(10);cf.setHorizontalSpacing(14)
        self.wbCandidateAh=QDoubleSpinBox(w);self.wbCandidateAh.setRange(0.0,2000.0);self.wbCandidateAh.setDecimals(1);self.wbCandidateAh.setValue(40.0);self.wbCandidateAh.setSuffix(" Ah")
        self.wbBmsCont=QDoubleSpinBox(w);self.wbBmsCont.setRange(0.0,2000.0);self.wbBmsCont.setDecimals(1);self.wbBmsCont.setValue(0.0);self.wbBmsCont.setSuffix(" A")
        self.wbBmsPeak=QDoubleSpinBox(w);self.wbBmsPeak.setRange(0.0,5000.0);self.wbBmsPeak.setDecimals(1);self.wbBmsPeak.setValue(0.0);self.wbBmsPeak.setSuffix(" A")
        for qx in (self.wbCandidateAh,self.wbBmsCont,self.wbBmsPeak):qx.setMinimumWidth(190)
        cf.addRow("Candidate capacity",self.wbCandidateAh)
        cf.addRow("BMS continuous current",self.wbBmsCont)
        cf.addRow("BMS peak current",self.wbBmsPeak)
        batRoot.addWidget(candidateBox)

        batButtons=QHBoxLayout()
        batCalc=QPushButton("คำนวณแบตวินช์");batCalc.setObjectName("primaryButton");batCalc.clicked.connect(self.calc_winch_battery)
        batButtons.addWidget(batCalc);batButtons.addStretch(1);batRoot.addLayout(batButtons)

        self.wbSummary=QLabel();self.wbSummary.setWordWrap(True)
        self.wbSummary.setStyleSheet("font-size:12pt;font-weight:800;background:#eef6ff;color:#174a74;padding:14px;border:1px solid #bfd6ee;border-radius:10px")
        batRoot.addWidget(self.wbSummary)
        self.wbDetails=QTextEdit(w);self.wbDetails.setReadOnly(True);self.wbDetails.setMinimumHeight(620)
        self.wbDetails.setStyleSheet("font-size:10.8pt;padding:8px;")
        batRoot.addWidget(self.wbDetails);batRoot.addStretch(1)
        self.wTabs.addTab(batScroll,"Battery / แบตวินช์")
        self.wTabs.addTab(self.wCalcSummary,"สรุป / Summary")

        self.wbDownMode.currentIndexChanged.connect(self.refresh_winch_battery_and_operation)
        self.wbDownBasis.currentIndexChanged.connect(self.refresh_winch_battery_and_operation)
        self.wbDownCurrent.valueChanged.connect(self.refresh_winch_battery_and_operation)
        self.wbDownSpeed.valueChanged.connect(self.refresh_winch_battery_and_operation)
        self.wbDownTime.valueChanged.connect(self.refresh_winch_battery_and_operation)
        self.wbEventMode.currentIndexChanged.connect(self.set_winch_event_mode)
        self.wbUseOp.toggled.connect(self.calc_winch_battery)
        for qx in (self.wbVoltage,self.wbEvents,self.wbDoD,self.wbReserve,self.wbCandidateAh,self.wbBmsCont,self.wbBmsPeak):
            qx.valueChanged.connect(self.calc_winch_battery)
        self._update_winch_battery_mode_ui()

        self.wGuide=QTextEdit(w);self.wGuide.hide()
        self.wResult=QTextEdit(w);self.wResult.hide()
        self.wSpeedSummary=QLabel(w);self.wSpeedSummary.hide()
        self.wSpeedSteps=QTextEdit(w);self.wSpeedSteps.hide()

        spec=self._winch_locked_spec()

        specBox=QGroupBox("4500LB. WINCH SPECIFICATION — จากใบสเปก")
        sl=QVBoxLayout(specBox)
        self.wSpecTable=QTableWidget(13,2)
        self.wSpecTable.setHorizontalHeaderLabels(["Item","Specification"])
        self.wSpecTable.verticalHeader().setVisible(False)
        self.wSpecTable.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.wSpecTable.setSelectionMode(QAbstractItemView.NoSelection)
        spec_rows=[
            ("Rated line pull","4500 lb (2041 kg) single line"),
            ("Motor","Permanent magnet, 1.4 kW / 1.9 hp"),
            ("Gear reduction ratio","136 : 1"),
            ("Gear train","Differential Planetary"),
            ("Cable (Dia × L)","Diameter 5 mm × Length 10 m"),
            ("Control","Remote switch"),
            ("Drum size (Dia × L)","Ø37 mm × 72 mm"),
            ("Clutch","Sliding Ring Gear"),
            ("Braking action","Automatic In-The-Drum"),
            ("Overall dimensions (L×W×H)","316 × 120 × 106 mm"),
            ("Mounting bolt pattern","166 × 76 mm, Ø9 mm"),
            ("Weight","N.W. 9 kg / G.W. 10 kg"),
            ("Packing size","43 × 30.5 × 36 cm, 2PC"),
        ]
        for r,(a,b) in enumerate(spec_rows):
            self.wSpecTable.setItem(r,0,QTableWidgetItem(a));self.wSpecTable.setItem(r,1,QTableWidgetItem(b))
        self.wSpecTable.horizontalHeader().setSectionResizeMode(0,QHeaderView.ResizeToContents)
        self.wSpecTable.horizontalHeader().setSectionResizeMode(1,QHeaderView.Stretch)
        self.wSpecTable.setMinimumHeight(410)
        sl.addWidget(self.wSpecTable);root.addWidget(specBox)

        tables=QHBoxLayout();tables.setSpacing(12)
        perfBox=QGroupBox("Pull, Speed, Motor Current — First Layer")
        pl=QVBoxLayout(perfBox)
        self.wPerfTable=QTableWidget(4,3)
        self.wPerfTable.setHorizontalHeaderLabels(["Line Pull","Line Speed","Motor (A)"])
        self.wPerfTable.verticalHeader().setVisible(False);self.wPerfTable.setEditTriggers(QAbstractItemView.NoEditTriggers);self.wPerfTable.setSelectionMode(QAbstractItemView.NoSelection)
        perf_rows=[
            ("0","10.8 ft/min (3.3 m/min)","12"),
            ("1,000 lb (454 kg)","8.2 ft/min (2.5 m/min)","60"),
            ("2,000 lb (907 kg)","3.6 ft/min (1.1 m/min)","100"),
            ("4,500 lb (2041 kg)","2.6 ft/min (0.8 m/min)","140"),
        ]
        for r,row in enumerate(perf_rows):
            for c,val in enumerate(row):self.wPerfTable.setItem(r,c,QTableWidgetItem(val))
        self.wPerfTable.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch);self.wPerfTable.setMinimumHeight(190)
        pl.addWidget(self.wPerfTable);tables.addWidget(perfBox,1)

        layerBox=QGroupBox("Line Pull And Rope Capacity In Layer")
        ll=QVBoxLayout(layerBox)
        self.wLayerTable=QTableWidget(5,3)
        self.wLayerTable.setHorizontalHeaderLabels(["Layer","Rated Line Pull","Total Rope On Drum"])
        self.wLayerTable.verticalHeader().setVisible(False);self.wLayerTable.setEditTriggers(QAbstractItemView.NoEditTriggers);self.wLayerTable.setSelectionMode(QAbstractItemView.NoSelection)
        for r,row in enumerate(spec["layers"]):
            for c,val in enumerate(row):self.wLayerTable.setItem(r,c,QTableWidgetItem(str(val)))
        self.wLayerTable.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch);self.wLayerTable.setMinimumHeight(210)
        ll.addWidget(self.wLayerTable);tables.addWidget(layerBox,1)
        root.addLayout(tables)

        calcBox=QGroupBox("Design Inputs + Datasheet Result")
        cg=QGridLayout(calcBox);cg.setContentsMargins(14,14,14,14);cg.setHorizontalSpacing(16);cg.setVerticalSpacing(10)
        locked=QLabel(
            "<b>หน้านี้ไม่คำนวณแบตเตอรี่แล้ว</b><br>"
            "แก้ได้เฉพาะ Load และ Lift Distance • Speed/Current ขาขึ้น interpolate จากตาราง First Layer • "
            "จำนวนงานและ Battery Ah อยู่ในแท็บ รอบการทำงาน และ Battery"
        )
        locked.setWordWrap(True);locked.setStyleSheet("background:#fff8e9;color:#68420b;padding:12px;border:1px solid #ead39a;border-radius:10px;")
        cg.addWidget(locked,0,0,1,3)
        loadLab=QLabel("โหลดที่ยก / Load");loadLab.setStyleSheet("font-size:11pt;font-weight:900;color:#17324d;")
        heightLab=QLabel("ระยะยก / Lift Distance");heightLab.setStyleSheet("font-size:11pt;font-weight:900;color:#17324d;")
        cg.addWidget(loadLab,1,0);cg.addWidget(self.wmass,1,1)
        cg.addWidget(heightLab,2,0);cg.addWidget(self.wheight,2,1)
        self.wSpecResult=QLabel();self.wSpecResult.setWordWrap(True)
        self.wSpecResult.setStyleSheet("font-size:11pt;font-weight:700;background:#eefaf4;color:#155b2a;padding:14px;border:1px solid #a9d7ba;border-radius:10px")
        cg.addWidget(self.wSpecResult,3,0,1,3)
        # Old widgets remain hidden only for backward compatibility with reports/tools.
        self.wcycles=QSpinBox(w);self.wcycles.setRange(1,100000);self.wcycles.setValue(1);self.wcycles.setEnabled(False);self.wcycles.hide()
        self.wSummary=QLabel(w);self.wSummary.hide()
        self.wBatteryResult=QLabel(w);self.wBatteryResult.hide()
        root.addWidget(calcBox)

        safety=QLabel(
            "<b>หมายเหตุ:</b> ใบนี้ให้ performance ที่ First Layer แต่ไม่ระบุ starting/stall surge และไม่ยืนยันว่าเป็น lifting-rated. "
            "การเลือก BMS/ฟิวส์/สายไฟขั้นสุดท้ายต้องตรวจข้อมูลผู้ผลิต/ทดสอบจริง และตารางนี้มีค่าสูงสุด 140 A."
        )
        safety.setWordWrap(True);safety.setStyleSheet("background:#fff4f4;color:#8a241c;padding:12px;border:1px solid #efb6b1;border-radius:10px")
        root.addWidget(safety);root.addStretch(1)

        self.wmass.valueChanged.connect(self.calc_winch)
        self.wheight.valueChanged.connect(self.calc_winch)
        self.tabs.addTab(w,"Winch")
        self._sync_locked_winch_widgets();self.calc_winch()

    def winch_speed_results(self):
        self._sync_locked_winch_widgets()
        spec=self._winch_locked_spec()
        m=self.wmass.value();h=self.wheight.value()
        speed,current=self._winch_interp_first_layer(m)
        d=spec["drum_d_mm"]/1000.0
        drum_rpm=speed/(math.pi*d) if d>0 else 0.0
        motor_rpm=drum_rpm*spec["gear_ratio"]
        tension=m*G
        drum_torque=tension*d/2.0
        shaft_torque=drum_torque/spec["gear_ratio"]
        t=h/speed*60.0 if speed>0 else 0.0
        return dict(rope_up=speed,rope_down=speed,load_up=speed,load_down=speed,
                    time_up=t,time_down=t,diameter=d,parts=1,
                    tension=tension,drum_torque=drum_torque,shaft_torque=shaft_torque,
                    drum_rpm_up=drum_rpm,drum_rpm_down=drum_rpm,
                    motor_up=motor_rpm,motor_down=motor_rpm,drum_up=drum_rpm,drum_down=drum_rpm,
                    current_a=current)

    def winch_speed_html(self,x):
        return (f"<h2>First-layer performance</h2>"
                f"<p>Project load {self.wmass.value():.1f} kg → speed <b>{x['load_up']:.3f} m/min</b>, "
                f"motor current <b>{x.get('current_a',self.wiup.value()):.2f} A</b>.</p>"
                "<p>ได้จาก linear interpolation ของตาราง First Layer. ใบสเปกไม่ให้ performance ขาลงแยกต่างหาก.</p>")

    def apply_winch_speed(self):
        self.calc_winch()
        QMessageBox.information(self,"Winch","V53.3 ใช้ความเร็วจากตาราง First Layer ของใบสเปกโดยอัตโนมัติ")

    @staticmethod
    def _next_standard_capacity(required_ah,step_up=False):
        sizes=[10,12,15,20,30,40,50,60,80,100,120,150,200,250,300]
        for idx,size in enumerate(sizes):
            if size+1e-9>=required_ah:
                if step_up and idx+1<len(sizes):return sizes[idx+1]
                return size
        return math.ceil(required_ah/50.0)*50.0

    def winch_core_results(self):
        """Single source for datasheet/performance geometry. No total battery-cycle calculation here."""
        self._sync_locked_winch_widgets()
        spec=self._winch_locked_spec()
        m=self.wmass.value();h=self.wheight.value()
        speed,current=self._winch_interp_first_layer(m)
        layer,layer_capacity_m,layer_pull_kg=self._winch_layer_for_distance(h)
        tu=h/speed*60.0 if speed>0 else 0.0
        return dict(
            m=m,h=h,v=spec["project_voltage_v"],tu=tu,
            f=m*G,fd=m*G*spec["force_sf"],mechanical=m*G*h/3600.0,
            iup=current,up_speed=speed,
            max_spec_current=140.0,spec_source="4500LB WINCH SPECIFICATION — user supplied",
            rope_layer=layer,layer_capacity_m=layer_capacity_m,layer_pull_kg=layer_pull_kg,
            layer_pull_ok=(m<=layer_pull_kg)
        )

    def winch_results(self):
        """Compatibility view. Battery totals come from the canonical Battery calculator."""
        q=dict(self.winch_core_results())
        if hasattr(self,"wbVoltage"):
            b=self.winch_battery_results()
            q.update(
                v=b["voltage"],td=b["down_time"],eu=b["e_up"],ed=b["e_down"],
                n=b["events"],total=b["total"],ah=b["ah_design"],
                idown=b["down_current"],down_speed=b["down_speed"],
                dod=b["dod"],reserve=b["reserve"],
                standard_ah=b["standard_ah"],extra_margin_ah=b["extra_margin_ah"]
            )
        else:
            spec=self._winch_locked_spec()
            td=q["tu"];eu=q["v"]*q["iup"]*q["tu"]/3600.0;ed=eu
            n=1;total=eu+ed;dod=spec["project_dod"];reserve=spec["project_reserve"]
            ah=total*(1.0+reserve)/(q["v"]*dod)
            q.update(td=td,eu=eu,ed=ed,n=n,total=total,ah=ah,idown=q["iup"],
                     down_speed=q["up_speed"],dod=dod,reserve=reserve,
                     standard_ah=self._next_standard_capacity(ah,False),
                     extra_margin_ah=self._next_standard_capacity(ah,True))
        return q

    def set_winch_event_mode(self,*_):
        if not hasattr(self,"wbEventMode"):return
        auto=self.wbEventMode.currentIndex()==0
        if hasattr(self,"wbUseOp"):
            old=self.wbUseOp.blockSignals(True)
            self.wbUseOp.setChecked(auto)
            self.wbUseOp.blockSignals(old)
        self._update_winch_battery_mode_ui()
        if hasattr(self,"wbSummary"):self.calc_winch_battery()

    def _update_winch_battery_mode_ui(self):
        if not hasattr(self,"wbDownMode"):return
        custom=self.wbDownMode.currentIndex()==1
        use_speed=self.wbDownBasis.currentIndex()==0
        self.wbDownBasis.setEnabled(custom)
        self.wbDownCurrent.setEnabled(custom)
        self.wbDownSpeed.setEnabled(custom and use_speed)
        self.wbDownTime.setEnabled(custom and not use_speed)
        auto=(self.wbEventMode.currentIndex()==0) if hasattr(self,"wbEventMode") else self.wbUseOp.isChecked()
        if hasattr(self,"wbUseOp"):
            old=self.wbUseOp.blockSignals(True)
            self.wbUseOp.setChecked(auto)
            self.wbUseOp.blockSignals(old)
        if hasattr(self,"wbEvents"):
            self.wbEvents.setEnabled(not auto)
        if hasattr(self,"wbEventNote"):
            if auto:
                self.wbEventNote.setText(
                    "AUTO — ใช้จำนวนงานยกจากหน้า รอบการทำงาน / 3h โดยอัตโนมัติ\n"
                    "1 งานยก = วินช์ขึ้น 1 ครั้ง + วินช์ลง 1 ครั้ง"
                )
            else:
                self.wbEventNote.setText(
                    "MANUAL — กรอกจำนวนงานยกเองในช่องด้านบน\n"
                    "1 งานยก = วินช์ขึ้น 1 ครั้ง + วินช์ลง 1 ครั้ง"
                )

    def winch_down_profile(self,q=None):
        if q is None:q=self.winch_core_results()
        conservative=not hasattr(self,"wbDownMode") or self.wbDownMode.currentIndex()==0
        if conservative:
            return dict(mode="Conservative",current=q["iup"],speed=q["up_speed"],time=q["tu"],basis="Down = Up")
        current=float(self.wbDownCurrent.value())
        if self.wbDownBasis.currentIndex()==0:
            speed=float(self.wbDownSpeed.value())
            time=q["h"]/speed*60.0 if speed>0 else 0.0
            basis="Measured / Custom Speed"
        else:
            time=float(self.wbDownTime.value())
            speed=q["h"]/(time/60.0) if time>0 else 0.0
            basis="Measured / Custom Time"
        return dict(mode="Measured / Custom",current=current,speed=speed,time=time,basis=basis)

    def winch_battery_results(self):
        q=self.winch_core_results()
        down=self.winch_down_profile(q)
        voltage=float(self.wbVoltage.value()) if hasattr(self,"wbVoltage") else q["v"]
        dod=(float(self.wbDoD.value())/100.0) if hasattr(self,"wbDoD") else q["dod"]
        reserve=(float(self.wbReserve.value())/100.0) if hasattr(self,"wbReserve") else q["reserve"]
        if hasattr(self,"wbEventMode"):
            use_operation=self.wbEventMode.currentIndex()==0
        else:
            use_operation=bool(self.wbUseOp.isChecked()) if hasattr(self,"wbUseOp") else False
        if use_operation and hasattr(self,"wopSpeed"):
            op=self.winch_operation_results()
            events=int(op["lift_events"])
        else:
            op=None
            events=int(self.wbEvents.value()) if hasattr(self,"wbEvents") else int(q["n"])
        e_up=voltage*q["iup"]*q["tu"]/3600.0
        e_down=voltage*down["current"]*down["time"]/3600.0
        e_event=e_up+e_down
        total=events*e_event
        ah_used=total/voltage if voltage>0 else 0.0
        ah_design=total*(1.0+reserve)/(voltage*dod) if voltage>0 and dod>0 else 0.0
        std=self._next_standard_capacity(ah_design,False)
        extra=self._next_standard_capacity(ah_design,True)
        candidate_ah=float(self.wbCandidateAh.value()) if hasattr(self,"wbCandidateAh") else 0.0
        bms_cont=float(self.wbBmsCont.value()) if hasattr(self,"wbBmsCont") else 0.0
        bms_peak=float(self.wbBmsPeak.value()) if hasattr(self,"wbBmsPeak") else 0.0
        operating_current=max(q["iup"],down["current"])
        energy_ok=(candidate_ah+1e-9)>=ah_design if candidate_ah>0 else False
        cont_entered=bms_cont>0
        cont_ok=bms_cont+1e-9>=operating_current if cont_entered else False
        table140_ok=bms_cont+1e-9>=140.0 if cont_entered else False
        return dict(
            voltage=voltage,dod=dod,reserve=reserve,use_operation=use_operation,
            events=events,op=op,load=q["m"],lift=q["h"],
            up_speed=q["up_speed"],up_current=q["iup"],up_time=q["tu"],
            down_mode=down["mode"],down_basis=down["basis"],
            down_speed=down["speed"],down_current=down["current"],down_time=down["time"],
            e_up=e_up,e_down=e_down,e_event=e_event,total=total,
            ah_used=ah_used,ah_design=ah_design,standard_ah=std,extra_margin_ah=extra,
            candidate_ah=candidate_ah,bms_cont=bms_cont,bms_peak=bms_peak,
            operating_current=operating_current,energy_ok=energy_ok,
            cont_entered=cont_entered,cont_ok=cont_ok,table140_ok=table140_ok,
            max_spec_current=140.0
        )

    def winch_battery_html(self,b):
        source_events=("จากหน้า รอบการทำงาน / 3h" if b["use_operation"] else "กรอกเอง")
        energy_status=("PASS" if b["energy_ok"] else "FAIL")
        if b["bms_cont"]<=0:
            cont_status="CHECK — ยังไม่ได้กรอก BMS continuous"
            table_status="CHECK — ยังไม่ได้กรอก BMS continuous"
        else:
            cont_status=("PASS" if b["cont_ok"] else "FAIL")
            table_status=("PASS" if b["table140_ok"] else "CHECK")
        peak_status="CHECK — ใบสเปกไม่ระบุ Starting/Stall surge"
        return f"""
        <html><body style="font-family:'Leelawadee UI','Noto Sans Thai',Tahoma,Arial;font-size:11pt;line-height:1.5">
        <h1 style="color:#17324d">WINCH BATTERY — ขึ้น / ลงแยกพลังงาน</h1>
        <p><b>Input:</b> Load = {b['load']:.1f} kg, Lift = {b['lift']:.2f} m,
        Lift events = {b['events']} งาน ({source_events}), V = {b['voltage']:.2f} V,
        DoD = {b['dod']*100:.0f}%, Reserve = {b['reserve']*100:.0f}%</p>

        <h2>1) ขาขึ้น / UP</h2>
        <p>จาก First Layer interpolation: v<sub>up</sub> = <b>{b['up_speed']:.3f} m/min</b>,
        I<sub>up</sub> = <b>{b['up_current']:.2f} A</b></p>
        <p><b>สูตรตัวแปร:</b> t<sub>up</sub> = (h / v<sub>up</sub>) × 60</p>
        <p><b>สูตรภาษาไทย:</b> เวลายกขึ้น = ระยะยก ÷ ความเร็ววินช์ขาขึ้น × 60</p>
        <p><b>แทนค่า:</b> ({b['lift']:.2f} / {b['up_speed']:.3f}) × 60 = <b>{b['up_time']:.2f} s</b></p>
        <p><b>สูตรตัวแปร:</b> E<sub>up</sub> = V × I<sub>up</sub> × t<sub>up</sub> / 3600</p>
        <p><b>สูตรภาษาไทย:</b> พลังงานขาขึ้น = แรงดันแบต × กระแสขณะยกขึ้น × เวลายกขึ้น ÷ 3600</p>
        <p><b>แทนค่า:</b> {b['voltage']:.2f} × {b['up_current']:.2f} × {b['up_time']:.2f} / 3600
        = <b>{b['e_up']:.3f} Wh</b></p>

        <h2>2) ขาลง / DOWN</h2>
        <p><b>Mode:</b> {b['down_mode']} — {b['down_basis']}</p>
        <p>v<sub>down</sub> = <b>{b['down_speed']:.3f} m/min</b>,
        I<sub>down</sub> = <b>{b['down_current']:.2f} A</b>,
        t<sub>down</sub> = <b>{b['down_time']:.2f} s</b></p>
        <p><b>สูตรตัวแปร:</b> E<sub>down</sub> = V × I<sub>down</sub> × t<sub>down</sub> / 3600</p>
        <p><b>สูตรภาษาไทย:</b> พลังงานขาลง = แรงดันแบต × กระแสขณะลดลง × เวลาลดลง ÷ 3600</p>
        <p><b>แทนค่า:</b> {b['voltage']:.2f} × {b['down_current']:.2f} × {b['down_time']:.2f} / 3600
        = <b>{b['e_down']:.3f} Wh</b></p>

        <h2>3) พลังงานต่อ 1 งานยกสัตว์</h2>
        <p><b>สูตรตัวแปร:</b> E<sub>event</sub> = E<sub>up</sub> + E<sub>down</sub></p>
        <p><b>สูตรภาษาไทย:</b> พลังงานต่อ 1 งานยกสัตว์ = พลังงานขาขึ้น + พลังงานขาลง</p>
        <p><b>แทนค่า:</b> {b['e_up']:.3f} + {b['e_down']:.3f} = <b>{b['e_event']:.3f} Wh/งาน</b></p>

        <h2>4) พลังงานรวม</h2>
        <p><b>สูตรตัวแปร:</b> E<sub>total</sub> = N<sub>event</sub> × E<sub>event</sub></p>
        <p><b>สูตรภาษาไทย:</b> พลังงานรวม = จำนวนงานยกสัตว์ × พลังงานต่อ 1 งานยกสัตว์</p>
        <p><b>แทนค่า:</b> {b['events']} × {b['e_event']:.3f} = <b>{b['total']:.2f} Wh</b></p>

        <h2>5) Ah ที่ใช้จริง</h2>
        <p><b>สูตรตัวแปร:</b> Ah<sub>used</sub> = E<sub>total</sub> / V</p>
        <p><b>สูตรภาษาไทย:</b> ความจุแบตที่ใช้จริง = พลังงานรวม ÷ แรงดันแบตเตอรี่</p>
        <p><b>แทนค่า:</b> {b['total']:.2f} / {b['voltage']:.2f} = <b>{b['ah_used']:.2f} Ah</b></p>

        <h2>6) Ah ออกแบบหลัง DoD + Reserve</h2>
        <p><b>สูตรตัวแปร:</b> Ah<sub>design</sub> = E<sub>total</sub>(1+Reserve) / (V × DoD)</p>
        <p><b>สูตรภาษาไทย:</b> ความจุแบตออกแบบ = พลังงานรวม × (1 + พลังงานสำรอง) ÷ (แรงดันแบต × สัดส่วน DoD ที่อนุญาตให้ใช้)</p>
        <p><b>แทนค่า:</b> {b['total']:.2f} × (1+{b['reserve']:.2f}) /
        ({b['voltage']:.2f} × {b['dod']:.2f}) = <b>{b['ah_design']:.2f} Ah</b></p>
        <p>ขนาดมาตรฐาน ≥ ค่าคำนวณ = <b>{b['standard_ah']:.0f} Ah</b> •
        เผื่อเพิ่มอีกหนึ่งขนาด = <b>{b['extra_margin_ah']:.0f} Ah</b></p>

        <h2>7) Battery Check</h2>
        <table border="1" cellspacing="0" cellpadding="7" width="100%">
        <tr><th>Check</th><th>Candidate</th><th>Required / Reference</th><th>Status</th></tr>
        <tr><td>Energy capacity</td><td>{b['candidate_ah']:.1f} Ah</td><td>≥ {b['ah_design']:.2f} Ah</td><td><b>{energy_status}</b></td></tr>
        <tr><td>Operating continuous current</td><td>{b['bms_cont']:.1f} A</td><td>≥ {b['operating_current']:.2f} A</td><td><b>{cont_status}</b></td></tr>
        <tr><td>Manufacturer table max reference</td><td>{b['bms_cont']:.1f} A</td><td>140 A</td><td><b>{table_status}</b></td></tr>
        <tr><td>BMS peak</td><td>{b['bms_peak']:.1f} A</td><td>Starting/Stall surge ไม่ระบุ</td><td><b>{peak_status}</b></td></tr>
        </table>

        <p><b>สำคัญ:</b> 140 A คือค่าสูงสุดที่ปรากฏในตาราง First Layer ที่ 2041 kg ไม่ใช่กระแสใช้งานปกติของโหลด {b['load']:.1f} kg.
        ส่วน Starting/Stall surge ไม่มีในใบสเปก จึงไม่ควรสรุป Peak PASS จากข้อมูลใบนี้เพียงอย่างเดียว.</p>
        </body></html>
        """

    def calc_winch_battery(self):
        if not hasattr(self,"wbSummary"):return
        self._update_winch_battery_mode_ui()
        b=self.winch_battery_results()
        energy=("PASS" if b["energy_ok"] else "FAIL")
        cont=("ยังไม่กรอก BMS" if b["bms_cont"]<=0 else ("PASS" if b["cont_ok"] else "FAIL"))
        source_text=("AUTO จากรอบการทำงาน / 3h" if b["use_operation"] else "MANUAL กำหนดเอง")
        self.wbSummary.setText(
            f"{source_text} • {b['events']} งานยก = UP {b['events']} ครั้ง + DOWN {b['events']} ครั้ง\n"
            f"UP {b['e_up']:.3f} Wh + DOWN {b['e_down']:.3f} Wh = {b['e_event']:.3f} Wh/งาน\n"
            f"รวม {b['total']:.2f} Wh • ใช้จริง {b['ah_used']:.2f} Ah • Design {b['ah_design']:.2f} Ah @ {b['voltage']:.2f} V\n"
            f"Standard ≥ {b['standard_ah']:.0f} Ah • Candidate {b['candidate_ah']:.1f} Ah: {energy} • Continuous current: {cont}"
        )
        if hasattr(self,"wbEventNote"):
            self.wbEventNote.setText(
                (f"AUTO — ใช้ {b['events']} งานยกจากหน้า รอบการทำงาน / 3h" if b["use_operation"]
                 else f"MANUAL — ใช้ {b['events']} งานยกที่กำหนดเอง")
                + "\n1 งานยก = วินช์ขึ้น 1 ครั้ง + วินช์ลง 1 ครั้ง"
            )
        self.wbDetails.setHtml(self.winch_battery_html(b))

    def refresh_winch_battery_and_operation(self):
        self._update_winch_battery_mode_ui()
        if hasattr(self,"wopSummary"):self.calc_winch_operation()
        elif hasattr(self,"wbSummary"):self.calc_winch_battery()

    def winch_operation_results(self):
        q=self.winch_core_results()
        speed_kmh=float(self.wopSpeed.value()) if hasattr(self,"wopSpeed") else 1.0
        one_way=float(self.wopDistance.value()) if hasattr(self,"wopDistance") else 30.0
        hours=float(self.wopHours.value()) if hasattr(self,"wopHours") else 3.0
        events_per_round=int(self.wopEvents.value()) if hasattr(self,"wopEvents") else 2
        other=float(self.wopOther.value()) if hasattr(self,"wopOther") else 0.0
        car_mps=speed_kmh*1000.0/3600.0
        t_one=one_way/car_mps if car_mps>0 else 0.0
        down=self.winch_down_profile(q)
        t_event=q["tu"]+down["time"]
        t_drive_round=2.0*t_one
        t_lift_round=t_event*events_per_round
        t_round=t_drive_round+t_lift_round+other
        total_s=hours*3600.0
        n_theory=total_s/t_round if t_round>0 else 0.0
        rounds=int(math.floor(n_theory+1e-12))
        trips=rounds*2
        lift_events=rounds*events_per_round
        up_count=lift_events
        down_count=lift_events
        winch_moves=up_count+down_count
        distance_total=rounds*(2.0*one_way)
        time_used=rounds*t_round
        remaining=max(0.0,total_s-time_used)
        return dict(
            speed_kmh=speed_kmh,car_mps=car_mps,one_way=one_way,hours=hours,
            events_per_round=events_per_round,other=other,
            load_kg=q["m"],lift_m=q["h"],winch_speed=q["up_speed"],
            t_up=q["tu"],t_down=down["time"],down_mode=down["mode"],down_basis=down["basis"],
            t_event=t_event,t_one=t_one,
            t_drive_round=t_drive_round,t_lift_round=t_lift_round,t_round=t_round,
            total_s=total_s,n_theory=n_theory,rounds=rounds,trips=trips,
            lift_events=lift_events,up_count=up_count,down_count=down_count,
            winch_moves=winch_moves,distance_total=distance_total,
            time_used=time_used,remaining=remaining
        )

    def winch_operation_html(self,r):
        return f"""
        <html><body style="font-family:'Leelawadee UI','Noto Sans Thai',Tahoma,Arial;font-size:11pt;line-height:1.5">
        <h1 style="color:#17324d">WINCH + VEHICLE — รอบการทำงาน</h1>
        <p><b>นิยาม:</b> 1 รอบไป-กลับ = วิ่งไป {r['one_way']:.2f} m + งานยกสัตว์ขาไป 1 งาน +
        วิ่งกลับ {r['one_way']:.2f} m + งานยกสัตว์ขากลับ 1 งาน โดย 1 งานยก = วินช์ขึ้น + วินช์ลง</p>
        <p><b>Input:</b> Vehicle speed = {r['speed_kmh']:.2f} km/h, Operating time = {r['hours']:.2f} h,
        Lift events/round = {r['events_per_round']}, Other stop = {r['other']:.1f} s/round,
        Load = {r['load_kg']:.1f} kg, Lift distance = {r['lift_m']:.2f} m</p>

        <h2>1) แปลงความเร็วรถ</h2>
        <p><b>สูตรตัวแปร:</b> v<sub>car</sub> = V<sub>km/h</sub> × 1000 / 3600</p>
        <p><b>สูตรภาษาไทย:</b> ความเร็วรถ (m/s) = ความเร็วรถ (km/h) × 1000 ÷ 3600</p>
        <p><b>ความหมาย:</b> แปลงความเร็วรถจาก km/h เป็น m/s</p>
        <p><b>แทนค่า:</b> {r['speed_kmh']:.2f} × 1000 / 3600 = <b>{r['car_mps']:.5f} m/s</b></p>

        <h2>2) เวลาวิ่งเที่ยวเดียว</h2>
        <p><b>สูตรตัวแปร:</b> t<sub>oneway</sub> = d / v<sub>car</sub></p>
        <p><b>สูตรภาษาไทย:</b> เวลาวิ่งเที่ยวเดียว = ระยะทางเที่ยวเดียว ÷ ความเร็วรถ</p>
        <p><b>ความหมาย:</b> ใช้หาเวลาที่รถใช้สำหรับขาไปหรือขากลับหนึ่งเที่ยว</p>
        <p><b>แทนค่า:</b> {r['one_way']:.2f} / {r['car_mps']:.5f} = <b>{r['t_one']:.2f} s</b></p>

        <h2>3) เวลาวินช์ขึ้น</h2>
        <p><b>สูตรตัวแปร:</b> t<sub>up</sub> = (h / v<sub>winch</sub>) × 60</p>
        <p><b>สูตรภาษาไทย:</b> เวลายกขึ้น = ระยะยก ÷ ความเร็ววินช์ขาขึ้น × 60</p>
        <p><b>ความหมาย:</b> คูณ 60 เพื่อแปลงเวลาจากนาทีเป็นวินาที</p>
        <p><b>แทนค่า:</b> ({r['lift_m']:.2f} / {r['winch_speed']:.3f}) × 60 = <b>{r['t_up']:.2f} s</b></p>

        <h2>4) เวลาวินช์ลง</h2>
        <p><b>Mode ขาลง:</b> {r['down_mode']} — {r['down_basis']}</p>
        <p><b>สูตรตัวแปร:</b> t<sub>down</sub> = (h / v<sub>down</sub>) × 60 เมื่อใช้ Down Speed</p>
        <p><b>สูตรภาษาไทย:</b> เวลาลดลง = ระยะยก ÷ ความเร็ววินช์ขาลง × 60</p>
        <p><b>เวลา:</b> t<sub>down</sub> = <b>{r['t_down']:.2f} s</b></p>

        <h2>5) เวลา 1 งานยกสัตว์</h2>
        <p><b>สูตรตัวแปร:</b> t<sub>event</sub> = t<sub>up</sub> + t<sub>down</sub></p>
        <p><b>สูตรภาษาไทย:</b> เวลา 1 งานยกสัตว์ = เวลาวินช์ขึ้น + เวลาวินช์ลง</p>
        <p><b>ความหมาย:</b> งานยกสัตว์ 1 งาน = วินช์ขึ้นหนึ่งครั้ง + วินช์ลงหนึ่งครั้ง</p>
        <p><b>แทนค่า:</b> {r['t_up']:.2f} + {r['t_down']:.2f} = <b>{r['t_event']:.2f} s</b></p>

        <h2>6) เวลาวิ่งไป-กลับ</h2>
        <p><b>สูตรตัวแปร:</b> t<sub>drive,round</sub> = 2 × t<sub>oneway</sub></p>
        <p><b>สูตรภาษาไทย:</b> เวลาวิ่งรถต่อรอบไป-กลับ = 2 × เวลาวิ่งเที่ยวเดียว</p>
        <p><b>แทนค่า:</b> 2 × {r['t_one']:.2f} = <b>{r['t_drive_round']:.2f} s</b></p>

        <h2>7) เวลางานยกรวมต่อรอบ</h2>
        <p><b>สูตรตัวแปร:</b> t<sub>lift,round</sub> = t<sub>event</sub> × N<sub>event/round</sub></p>
        <p><b>สูตรภาษาไทย:</b> เวลางานยกรวมต่อรอบ = เวลา 1 งานยกสัตว์ × จำนวนงานยกต่อรอบ</p>
        <p><b>ความหมาย:</b> รวมเวลาวินช์ของทุกงานยกในหนึ่งรอบไป-กลับ</p>
        <p><b>แทนค่า:</b> {r['t_event']:.2f} × {r['events_per_round']} = <b>{r['t_lift_round']:.2f} s</b></p>

        <h2>8) เวลารวมต่อ 1 รอบไป-กลับ</h2>
        <p><b>สูตรตัวแปร:</b> t<sub>round</sub> = t<sub>drive,round</sub> + t<sub>lift,round</sub> + t<sub>other</sub></p>
        <p><b>สูตรภาษาไทย:</b> เวลารวมต่อรอบ = เวลาวิ่งรถไป-กลับ + เวลางานยกรวม + เวลาหยุดอื่น</p>
        <p><b>แทนค่า:</b> {r['t_drive_round']:.2f} + {r['t_lift_round']:.2f} + {r['other']:.2f}
        = <b>{r['t_round']:.2f} s/รอบ</b></p>

        <h2>9) จำนวนรอบในเวลาที่กำหนด</h2>
        <p><b>สูตรตัวแปร:</b> N<sub>theory</sub> = t<sub>available</sub> / t<sub>round</sub></p>
        <p><b>สูตรภาษาไทย:</b> จำนวนรอบทางทฤษฎี = เวลาทำงานที่มีทั้งหมด ÷ เวลาที่ใช้ต่อ 1 รอบ</p>
        <p><b>แทนค่า:</b> ({r['hours']:.2f} × 3600) / {r['t_round']:.2f}
        = <b>{r['n_theory']:.2f} รอบ</b></p>
        <p>นับเฉพาะรอบที่ทำครบ → <b>{r['rounds']} รอบไป-กลับ</b></p>

        <h2>10) สรุปจำนวนงาน</h2>
        <table border="1" cellspacing="0" cellpadding="7" width="100%">
        <tr><td>รอบไป-กลับที่ทำครบ</td><td><b>{r['rounds']} รอบ</b></td><td>floor({r['n_theory']:.2f})</td></tr>
        <tr><td>เที่ยวทางเดียว</td><td><b>{r['trips']} เที่ยว</b></td><td>{r['rounds']} × 2</td></tr>
        <tr><td>งานยกสัตว์</td><td><b>{r['lift_events']} งาน</b></td><td>{r['rounds']} × {r['events_per_round']}</td></tr>
        <tr><td>วินช์ขึ้น</td><td><b>{r['up_count']} ครั้ง</b></td><td>1 ครั้ง/งาน</td></tr>
        <tr><td>วินช์ลง</td><td><b>{r['down_count']} ครั้ง</b></td><td>1 ครั้ง/งาน</td></tr>
        <tr><td>การเคลื่อนที่วินช์รวม</td><td><b>{r['winch_moves']} ครั้ง</b></td><td>UP + DOWN</td></tr>
        <tr><td>ระยะทางรวม</td><td><b>{r['distance_total']:.0f} m</b></td><td>{r['rounds']} × 2 × {r['one_way']:.2f}</td></tr>
        <tr><td>เวลาที่ใช้</td><td><b>{r['time_used']:.2f} s</b></td><td>{r['rounds']} × {r['t_round']:.2f}</td></tr>
        <tr><td>เวลาเหลือ</td><td><b>{r['remaining']:.2f} s</b></td><td>{r['total_s']:.0f} - {r['time_used']:.2f}</td></tr>
        </table>

        <hr>
        <p><b>หมายเหตุ:</b> ค่านี้ยังไม่รวมเวลาจัดตะกร้า/เกี่ยวสลิง/ปลดสลิง เว้นแต่กรอกใน Other stop time.
        ความเร็วและเวลาวินช์อิง First Layer interpolation และใช้ขาลงเท่าขาขึ้นเพราะใบสเปกไม่ได้ให้ข้อมูลขาลงแยก.</p>
        </body></html>
        """

    def calc_winch_operation(self):
        if not hasattr(self,"wopSummary"):return
        r=self.winch_operation_results()
        self.wopSummary.setText(
            f"{r['rounds']} รอบไป-กลับ • {r['trips']} เที่ยวทางเดียว • {r['lift_events']} งานยกสัตว์\n"
            f"วินช์ขึ้น {r['up_count']} ครั้ง + ลง {r['down_count']} ครั้ง = {r['winch_moves']} การเคลื่อนที่\n"
            f"เวลา 1 รอบ = {r['t_round']:.2f} s • ระยะทางรวม = {r['distance_total']:.0f} m • เวลาเหลือ = {r['remaining']:.2f} s"
        )
        self.wopDetails.setHtml(self.winch_operation_html(r))
        if hasattr(self,"wbSummary"):self.calc_winch_battery()
        if hasattr(self,"eSummary") and hasattr(self,"euseOperationCycle") and self.euseOperationCycle.isChecked():
            self.calc_electrical()

    def apply_winch_operation_cycles(self):
        if not hasattr(self,"wcycles"):return
        r=self.winch_operation_results()
        self.wcycles.setValue(max(1,int(r["lift_events"])))
        if hasattr(self,"wbEvents"):self.wbEvents.setValue(max(1,int(r["lift_events"])))
        self.calc_winch()
        if hasattr(self,"wopSummary"):
            self.wopSummary.setText(self.wopSummary.text()+f"\nตั้ง Battery Cycles = {r['lift_events']} รอบขึ้น+ลงแล้ว")

    def winch_formula_html(self,q=None):
        core=self.winch_core_results()
        b=self.winch_battery_results()
        r=self.winch_operation_results()
        spec=self._winch_locked_spec();pts=spec["perf"];m=core["m"]
        x0,v0,i0,_=pts[0];x1,v1,i1,_=pts[1]
        for a,z in zip(pts[:-1],pts[1:]):
            if m<=z[0]:
                x0,v0,i0,_=a;x1,v1,i1,_=z;break
        alpha=(m-x0)/(x1-x0) if x1>x0 else 0.0
        alpha=max(0.0,min(1.0,alpha))
        return f"""
        <html><body style="font-family:'Leelawadee UI','Noto Sans Thai',Tahoma,Arial;font-size:11pt;line-height:1.5">
        <h1 style="color:#17324d">WINCH — สูตร + วิธีคำนวณ</h1>
        <p><b>หลักการ:</b> หน้านี้เป็นหน้าคำอธิบายเท่านั้น ผลตัวเลขดึงจาก Datasheet → รอบการทำงาน → Battery ชุดเดียวกัน ไม่คำนวณแบตอีกชุดแยกต่างหาก</p>

        <h2>1) Interpolation ความเร็วและกระแสขาขึ้น</h2>
        <p><b>สูตรตัวแปร:</b> α = (m-m₀)/(m₁-m₀)</p>
        <p><b>สูตรภาษาไทย:</b> สัดส่วนการอินเตอร์โพเลต = (โหลดที่ต้องการ - โหลดจุดล่าง) ÷ (โหลดจุดบน - โหลดจุดล่าง)</p>
        <p><b>ความหมาย:</b> หาตำแหน่งของ Load ปัจจุบันระหว่างจุดข้อมูลสองจุดใน First Layer table</p>
        <p><b>แทนค่า:</b> ({core['m']:.1f}-{x0:.1f})/({x1:.1f}-{x0:.1f}) = <b>{alpha:.4f}</b></p>
        <p><b>สูตรตัวแปร:</b> v_up = v₀ + α(v₁-v₀)</p>
        <p><b>สูตรภาษาไทย:</b> ความเร็ววินช์ขาขึ้น = ความเร็วจุดล่าง + สัดส่วนการอินเตอร์โพเลต × (ความเร็วจุดบน - ความเร็วจุดล่าง)</p>
        <p><b>แทนค่า:</b> {v0:.3f}+{alpha:.4f}({v1:.3f}-{v0:.3f}) = <b>{core['up_speed']:.3f} m/min</b></p>
        <p><b>สูตรตัวแปร:</b> I_up = I₀ + α(I₁-I₀)</p>
        <p><b>สูตรภาษาไทย:</b> กระแสขณะยกขึ้น = กระแสจุดล่าง + สัดส่วนการอินเตอร์โพเลต × (กระแสจุดบน - กระแสจุดล่าง)</p>
        <p><b>แทนค่า:</b> {i0:.2f}+{alpha:.4f}({i1:.2f}-{i0:.2f}) = <b>{core['iup']:.2f} A</b></p>

        <h2>2) เวลาวินช์ขึ้น</h2>
        <p><b>สูตรตัวแปร:</b> t_up = (h/v_up) × 60</p>
        <p><b>สูตรภาษาไทย:</b> เวลายกขึ้น = ระยะยก ÷ ความเร็ววินช์ขาขึ้น × 60</p>
        <p><b>ความหมาย:</b> คูณ 60 เพื่อแปลงเวลาจากนาทีเป็นวินาที</p>
        <p><b>แทนค่า:</b> ({core['h']:.2f}/{core['up_speed']:.3f})×60 = <b>{core['tu']:.2f} s</b></p>

        <h2>3) เวลาขาลง</h2>
        <p><b>Mode:</b> {b['down_mode']} — {b['down_basis']}</p>
        <p><b>สูตรตัวแปรเมื่อใช้ Down Speed:</b> t_down = (h/v_down) × 60</p>
        <p><b>สูตรภาษาไทย:</b> เวลาลดลง = ระยะยก ÷ ความเร็ววินช์ขาลง × 60</p>
        <p>I_down = <b>{b['down_current']:.2f} A</b>, v_down = <b>{b['down_speed']:.3f} m/min</b>,
        t_down = <b>{b['down_time']:.2f} s</b></p>

        <h2>4) รอบการทำงาน</h2>
        <p><b>สูตรตัวแปร:</b> t_event = t_up + t_down</p>
        <p><b>สูตรภาษาไทย:</b> เวลา 1 งานยกสัตว์ = เวลาวินช์ขึ้น + เวลาวินช์ลง</p>
        <p><b>แทนค่า:</b> {core['tu']:.2f}+{b['down_time']:.2f} = <b>{r['t_event']:.2f} s/งาน</b></p>
        <p><b>สูตรตัวแปร:</b> t_round = t_drive,round + t_lift,round + t_other</p>
        <p><b>สูตรภาษาไทย:</b> เวลารวมต่อรอบ = เวลาวิ่งรถไป-กลับ + เวลางานยกรวม + เวลาหยุดอื่น</p>
        <p><b>แทนค่า:</b>
        {r['t_drive_round']:.2f}+{r['t_lift_round']:.2f}+{r['other']:.2f} = <b>{r['t_round']:.2f} s/รอบ</b></p>
        <p><b>สูตรตัวแปร:</b> N_round = floor(t_available/t_round)</p>
        <p><b>สูตรภาษาไทย:</b> จำนวนรอบที่ทำได้ครบ = ปัดลง(เวลาทำงานทั้งหมด ÷ เวลาต่อ 1 รอบ)</p>
        <p><b>แทนค่า:</b> floor({r['total_s']:.0f}/{r['t_round']:.2f}) = <b>{r['rounds']} รอบ</b></p>
        <p><b>สูตรตัวแปร:</b> N_event = N_round × events/round</p>
        <p><b>สูตรภาษาไทย:</b> จำนวนงานยกสัตว์ = จำนวนรอบที่ทำได้ครบ × จำนวนงานยกต่อรอบ</p>
        <p><b>แทนค่า:</b> {r['rounds']}×{r['events_per_round']} = <b>{r['lift_events']} งาน</b></p>

        <h2>5) พลังงานแบตวินช์ — ชุดคำนวณหลัก</h2>
        <p><b>สูตรตัวแปร:</b> E_up = V × I_up × t_up / 3600</p>
        <p><b>สูตรภาษาไทย:</b> พลังงานขาขึ้น = แรงดันแบต × กระแสขณะยกขึ้น × เวลายกขึ้น ÷ 3600</p>
        <p><b>แทนค่า:</b> {b['voltage']:.2f}×{b['up_current']:.2f}×{b['up_time']:.2f}/3600 = <b>{b['e_up']:.3f} Wh</b></p>
        <p><b>สูตรตัวแปร:</b> E_down = V × I_down × t_down / 3600</p>
        <p><b>สูตรภาษาไทย:</b> พลังงานขาลง = แรงดันแบต × กระแสขณะลดลง × เวลาลดลง ÷ 3600</p>
        <p><b>แทนค่า:</b> {b['voltage']:.2f}×{b['down_current']:.2f}×{b['down_time']:.2f}/3600 = <b>{b['e_down']:.3f} Wh</b></p>
        <p><b>สูตรตัวแปร:</b> E_event = E_up + E_down</p>
        <p><b>สูตรภาษาไทย:</b> พลังงานต่อ 1 งานยกสัตว์ = พลังงานขาขึ้น + พลังงานขาลง</p>
        <p><b>แทนค่า:</b> {b['e_up']:.3f}+{b['e_down']:.3f} = <b>{b['e_event']:.3f} Wh/งาน</b></p>
        <p><b>สูตรตัวแปร:</b> E_total = N_event × E_event</p>
        <p><b>สูตรภาษาไทย:</b> พลังงานรวม = จำนวนงานยกสัตว์ × พลังงานต่อ 1 งานยกสัตว์</p>
        <p><b>แทนค่า:</b> {b['events']}×{b['e_event']:.3f} = <b>{b['total']:.2f} Wh</b></p>
        <p><b>สูตรตัวแปร:</b> Ah_used = E_total/V</p>
        <p><b>สูตรภาษาไทย:</b> ความจุแบตที่ใช้จริง = พลังงานรวม ÷ แรงดันแบตเตอรี่</p>
        <p><b>แทนค่า:</b> {b['total']:.2f}/{b['voltage']:.2f} = <b>{b['ah_used']:.2f} Ah</b></p>
        <p><b>สูตรตัวแปร:</b> Ah_design = E_total(1+Reserve)/(V×DoD)</p>
        <p><b>สูตรภาษาไทย:</b> ความจุแบตออกแบบ = พลังงานรวม × (1 + พลังงานสำรอง) ÷ (แรงดันแบต × สัดส่วน DoD ที่อนุญาตให้ใช้)</p>
        <p><b>แทนค่า:</b> {b['total']:.2f}×(1+{b['reserve']:.2f})/({b['voltage']:.2f}×{b['dod']:.2f})
        = <b>{b['ah_design']:.2f} Ah</b></p>

        <p><b>ขนาดมาตรฐาน ≥ ค่าคำนวณ:</b> {b['standard_ah']:.0f} Ah •
        Extra margin: {b['extra_margin_ah']:.0f} Ah</p>
        </body></html>
        """

    def winch_summary_html(self,q=None):
        core=self.winch_core_results();r=self.winch_operation_results();b=self.winch_battery_results()
        energy_status="PASS" if b["energy_ok"] else "FAIL"
        return f"""
        <html><body style="font-family:'Leelawadee UI','Noto Sans Thai',Tahoma,Arial;font-size:11pt;line-height:1.5">
        <h1 style="color:#17324d">WINCH — FINAL SUMMARY</h1>
        <p><b>สรุปผลเท่านั้น:</b> หน้านี้ไม่แสดงสูตรและไม่คำนวณซ้ำ</p>
        <table border="1" cellspacing="0" cellpadding="8" width="100%">
        <tr><th>รายการ</th><th>ผลลัพธ์สุดท้าย</th></tr>
        <tr><td>Load / Lift Distance</td><td><b>{core['m']:.1f} kg / {core['h']:.2f} m</b></td></tr>
        <tr><td>รอบไป-กลับที่ทำได้</td><td><b>{r['rounds']} รอบ</b></td></tr>
        <tr><td>เที่ยวเดินรถทั้งหมด</td><td><b>{r['trips']} เที่ยว</b></td></tr>
        <tr><td>งานยกสัตว์</td><td><b>{r['lift_events']} งาน</b></td></tr>
        <tr><td>Winch UP / DOWN</td><td><b>{r['up_count']} / {r['down_count']} ครั้ง</b></td></tr>
        <tr><td>พลังงานวินช์รวม</td><td><b>{b['total']:.2f} Wh</b></td></tr>
        <tr><td>Battery used</td><td><b>{b['ah_used']:.2f} Ah</b></td></tr>
        <tr><td>Battery design</td><td><b>{b['ah_design']:.2f} Ah @ {b['voltage']:.2f} V</b></td></tr>
        <tr><td>Standard size ขั้นต่ำ</td><td><b>{b['standard_ah']:.0f} Ah</b></td></tr>
        <tr><td>Candidate battery</td><td><b>{b['candidate_ah']:.1f} Ah — {energy_status}</b></td></tr>
        </table>
        <p>สูตรและการแทนค่าดูได้ตรงหน้าที่เกี่ยวข้อง: <b>รอบการทำงาน</b> และ <b>Battery</b> เท่านั้น</p>
        </body></html>
        """

    def winch_html(self,q=None):
        core=self.winch_core_results()
        return f"""
        <html><body style="font-family:'Leelawadee UI','Noto Sans Thai',Tahoma,Arial;font-size:11pt">
        <h1>4500LB. WINCH — DATASHEET / PERFORMANCE</h1>
        <p><b>Source:</b> ใบ 4500LB. WINCH SPECIFICATION ที่ผู้ใช้ส่งมา</p>
        <p>Rated line pull 4500 lb (2041 kg), single line • Motor 1.4 kW / 1.9 hp • Gear ratio 136:1 • Cable Ø5 mm × 10 m • Drum Ø37 × 72 mm</p>
        <h2>Current design input</h2>
        <p>Load = <b>{core['m']:.1f} kg</b> • Lift Distance = <b>{core['h']:.2f} m</b></p>
        <p>First-layer interpolation → speed = <b>{core['up_speed']:.3f} m/min</b>,
        current = <b>{core['iup']:.2f} A</b>, t_up = <b>{core['tu']:.2f} s</b></p>
        <p>Estimated rope layer = <b>{core['rope_layer']}</b> • sheet line-pull = <b>{core['layer_pull_kg']:.0f} kg</b> →
        <b>{'PASS' if core['layer_pull_ok'] else 'CHECK'}</b></p>
        <p><b>Battery totals are intentionally not calculated in this Datasheet section.</b> ใช้แท็บ Battery เป็นตัวคำนวณหลักเพียงจุดเดียว.</p>
        </body></html>
        """

    def calc_winch(self):
        if not hasattr(self,"wmass"):return
        self._sync_locked_winch_widgets()
        core=self.winch_core_results()
        if hasattr(self,"wSpecResult"):
            self.wSpecResult.setText(
                f"Load {core['m']:.1f} kg • Lift {core['h']:.2f} m\n"
                f"First Layer: speed {core['up_speed']:.3f} m/min • current {core['iup']:.2f} A • t_up {core['tu']:.2f} s\n"
                f"Rope Layer {core['rope_layer']} • sheet line-pull {core['layer_pull_kg']:.0f} kg • {'PASS' if core['layer_pull_ok'] else 'CHECK LOAD'}"
            )
        if hasattr(self,"wopSummary"):self.calc_winch_operation()
        if hasattr(self,"wbSummary"):self.calc_winch_battery()
        if hasattr(self,"wSteps"):self.wSteps.setHtml(self.winch_formula_html())
        if hasattr(self,"wCalcSummary"):self.wCalcSummary.setHtml(self.winch_summary_html())
        if hasattr(self,"wVars"):self.wVars.setHtml(self.winch_variables_html())
        if hasattr(self,"allWVars"):self.allWVars.setHtml(self.winch_variables_html())
        sp=self.winch_speed_results()
        if hasattr(self,"wSpeedSummary"):self.wSpeedSummary.setText(f"{sp['load_up']:.3f} m/min • {sp['current_a']:.2f} A")
        if hasattr(self,"wSpeedSteps"):self.wSpeedSteps.setHtml(self.winch_speed_html(sp))
        if hasattr(self,"wGuide"):self.wGuide.setHtml("<h2>Winch V53.3.9</h2><p>Datasheet → Operating Cycles → Battery → Summary; สูตรอยู่เฉพาะหน้าที่ใช้งานจริง.</p>")
        if hasattr(self,"wResult"):self.wResult.setHtml(self.winch_html())
        if hasattr(self,"wDutyView"):self.update_winch_duty()
        if hasattr(self,"bmsView"):self.bmsView.setHtml(self.bms_check_html())

    def export_winch_pdf(self):
        filename,_=QFileDialog.getSaveFileName(self,"Export Winch PDF","Winch_4500LB_Spec_Battery.pdf","PDF (*.pdf)")
        if not filename:return
        if not filename.lower().endswith(".pdf"):filename+=".pdf"
        try:
            doc=QTextDocument();doc.setDefaultFont(QFont(choose_ui_font_family(),10))
            op_html=self.winch_operation_html(self.winch_operation_results()) if hasattr(self,"wopSpeed") else ""
            battery_html=self.winch_battery_html(self.winch_battery_results()) if hasattr(self,"wbVoltage") else ""
            doc.setHtml(self.winch_summary_html()+"<hr>"+self.winch_html()+"<hr>"+op_html+"<hr>"+battery_html+"<hr>"+self.winch_variables_html())
            printer=QPrinter(QPrinter.HighResolution);printer.setOutputFormat(QPrinter.PdfFormat)
            printer.setOutputFileName(filename);printer.setPageSize(QPageSize(QPageSize.A4));doc.print_(printer)
            QMessageBox.information(self,"Export PDF","บันทึกรายงานเรียบร้อย:\\n"+filename)
        except Exception as exc:
            QMessageBox.critical(self,"Export PDF ไม่สำเร็จ",str(exc))


    def make_electrical(self):
        w=QWidget();self.electricalPage=w
        root=QVBoxLayout(w);root.setContentsMargins(16,16,16,16);root.setSpacing(12)
        root.addWidget(make_page_header("ELECTRICAL / BATTERY CALCULATION","Trip Summary • Route Energy • Wh • Ah • Peak Current • BMS check",self.show_home_mode,"72 V DRIVE","#e5faf4","#0b7665","Export PDF / ส่งออกรายงาน",self.export_electrical_pdf))
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
        self.eslopeLen=ds(2.9,0,1000,3); self.eslopeDeg=ds(12,0,45,2)
        self.eruntime=ds(3,.01,48,2); self.err=ds(.02,0,1,3)
        self.eaccel=ds(5,.1,120,2); self.estops=QSpinBox();self.estops.setRange(0,20);self.estops.setValue(2);self.estops.setMinimumWidth(150);self.estops.setMaximumWidth(250)
        self.estopTime=ds(0,0,3600,1)
        self.euseOperationCycle=QCheckBox("รวมเวลายกจาก Winch Operating Cycles อัตโนมัติ")
        self.euseOperationCycle.setChecked(True)
        self.eOperationTimeNote=QLabel("Auto: เวลายกถูกใช้คำนวณจำนวนรอบของรถ แต่พลังงานวินช์ 12 V ไม่ถูกรวมในแบตรถ 72 V")
        self.eOperationTimeNote.setWordWrap(True)
        self.eOperationTimeNote.setStyleSheet("background:#eef8ff;color:#294d6b;padding:8px;border:1px solid #d3e6f5;border-radius:8px")
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
            ("เวลาหยุดอื่นต่อรอบ (s)",self.estopTime),("Estimated drive efficiency (%)",self.edriveEff),
            ("Auxiliary average power (W)",self.eaux),("Usable DoD (%)",self.edod),
            ("Battery reserve (%)",self.ereserve),("Motor rated power / motor (W)",self.emotorRated),
            ("จำนวนมอเตอร์",self.enmot),("Worst-case slope efficiency (%)",self.eupEff)
        ]: form.addRow(lab,q)
        form.addRow(self.euseOperationCycle)
        form.addRow(self.eOperationTimeNote)
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
        bSummary=QPushButton("ดูสรุปไป-กลับ / Trip Summary");bSummary.clicked.connect(lambda:self.eTabs.setCurrentIndex(1));rv.addWidget(bSummary)
        bBattery=QPushButton("เลือกแบตที่จะซื้อ / Battery Selection");bBattery.clicked.connect(lambda:self.eTabs.setCurrentIndex(2));rv.addWidget(bBattery)
        rv.addStretch();hl.addWidget(right,1)
        eInputScroll=QScrollArea();eInputScroll.setWidgetResizable(True);eInputScroll.setFrameShape(QFrame.NoFrame)
        eInputScroll.setWidget(inp);self.eTabs.addTab(eInputScroll,"Input / ข้อมูล")

        # V52.1 — simple one-page trip/battery summary for quick reading.
        trip=QWidget();tripOuter=QVBoxLayout(trip);tripOuter.setContentsMargins(10,10,10,10);tripOuter.setSpacing(12)
        tripTitle=QLabel("สรุปพลังงานไป-กลับ / TRIP ENERGY SUMMARY")
        tf=QFont();tf.setPointSize(15);tf.setBold(True);tripTitle.setFont(tf)
        tripTitle.setStyleSheet("color:#17324d;")
        tripSub=QLabel("ดูตัวเลขสำคัญหน้าเดียว: 1 รอบใช้เท่าไร → วิ่งได้กี่รอบ → รวมกี่ Wh → ต้องใช้แบตกี่ Ah")
        tripSub.setWordWrap(True);tripSub.setStyleSheet("color:#60758b;font-size:10.3pt;font-weight:650;")
        tripOuter.addWidget(tripTitle);tripOuter.addWidget(tripSub)

        def energy_card(title,accent="#245fbb"):
            box=QFrame();box.setObjectName("softPanel");box.setMinimumHeight(108)
            lay=QVBoxLayout(box);lay.setContentsMargins(14,11,14,11);lay.setSpacing(5)
            t=QLabel(title);t.setWordWrap(True);t.setStyleSheet("color:#667b8e;font-size:9.2pt;font-weight:850;")
            value=QLabel("—");value.setWordWrap(True)
            value.setStyleSheet(f"color:{accent};font-size:17pt;font-weight:900;")
            lay.addWidget(t);lay.addWidget(value);lay.addStretch(1)
            return box,value

        grid=QGridLayout();grid.setHorizontalSpacing(12);grid.setVerticalSpacing(12)
        c,self.tripDistanceLabel=energy_card("ระยะ 1 รอบไป-กลับ","#245fbb");grid.addWidget(c,0,0)
        c,self.tripTimeLabel=energy_card("เวลา 1 รอบ","#245fbb");grid.addWidget(c,0,1)
        c,self.tripCountLabel=energy_card("จำนวนรอบในเวลาที่กำหนด","#7c3aed");grid.addWidget(c,1,0)
        c,self.tripEnergyLabel=energy_card("พลังงานขับ / 1 รอบ","#0f8a73");grid.addWidget(c,1,1)
        c,self.tripDriveTotalLabel=energy_card("พลังงานขับรวมทุก รอบ","#0f8a73");grid.addWidget(c,2,0)
        c,self.tripAuxLabel=energy_card("ไฟอุปกรณ์เสริมรวม","#d97706");grid.addWidget(c,2,1)
        c,self.tripLoadTotalLabel=energy_card("พลังงานรวมก่อนเผื่อแบต","#c45114");grid.addWidget(c,3,0)
        c,self.tripBatteryLabel=energy_card("แบตที่ต้องการหลัง DoD + Reserve","#b42318");grid.addWidget(c,3,1)
        grid.setColumnStretch(0,1);grid.setColumnStretch(1,1)
        tripOuter.addLayout(grid)

        self.tripEnergyExplain=QTextEdit();self.tripEnergyExplain.setReadOnly(True);self.tripEnergyExplain.setMinimumHeight(190)
        tripOuter.addWidget(self.tripEnergyExplain)
        tripScroll=QScrollArea();tripScroll.setWidgetResizable(True);tripScroll.setFrameShape(QFrame.NoFrame);tripScroll.setWidget(trip)
        self.eTabs.addTab(tripScroll,"สรุปไป-กลับ / Trip Summary")

        # V52.2 — Battery Selection: separate calculated minimum from a battery you may actually buy.
        bsel=QWidget();bselOuter=QVBoxLayout(bsel);bselOuter.setContentsMargins(10,10,10,10);bselOuter.setSpacing(12)
        bselTitle=QLabel("BATTERY SELECTION / เลือกแบตที่จะซื้อ")
        bf=QFont();bf.setPointSize(15);bf.setBold(True);bselTitle.setFont(bf);bselTitle.setStyleSheet("color:#17324d;")
        bselSub=QLabel("แยกให้ชัด: ค่าขั้นต่ำจากพลังงาน ≠ แบตที่ควรซื้อจริง • ต้องผ่านทั้ง Ah/Wh และกระแส Continuous/Peak")
        bselSub.setWordWrap(True);bselSub.setStyleSheet("color:#60758b;font-size:10.3pt;font-weight:650;")
        bselOuter.addWidget(bselTitle);bselOuter.addWidget(bselSub)

        metricGrid=QGridLayout();metricGrid.setHorizontalSpacing(10);metricGrid.setVerticalSpacing(10)
        def bmetric(title):
            box=QFrame();box.setObjectName("metricPanel");box.setMinimumHeight(90)
            lay=QVBoxLayout(box);lay.setContentsMargins(12,9,12,9);lay.setSpacing(3)
            t=QLabel(title);t.setWordWrap(True);t.setStyleSheet("color:#667b8e;font-size:8.9pt;font-weight:850;")
            v=QLabel("—");v.setWordWrap(True);v.setStyleSheet("color:#17324d;font-size:15pt;font-weight:900;")
            lay.addWidget(t);lay.addWidget(v);lay.addStretch(1)
            return box,v
        c,self.bselMinAhLabel=bmetric("ขั้นต่ำจากพลังงาน");metricGrid.addWidget(c,0,0)
        c,self.bselContLabel=bmetric("กระแสต่อเนื่องที่ต้องรองรับ");metricGrid.addWidget(c,0,1)
        c,self.bselPeakLabel=bmetric("กระแส Peak ที่คำนวณ");metricGrid.addWidget(c,0,2)
        c,self.bselSuggestedLabel=bmetric("ขนาดมาตรฐานที่แนะนำให้ตรวจ");metricGrid.addWidget(c,0,3)
        for col in range(4):metricGrid.setColumnStretch(col,1)
        bselOuter.addLayout(metricGrid)

        controlBox=QGroupBox("Design Target & Candidate Battery / เกณฑ์และแบตที่กำลังจะซื้อ")
        cf=QGridLayout(controlBox);cf.setHorizontalSpacing(12);cf.setVerticalSpacing(8)
        def bds(v,lo,hi,step=0.1,dec=1):
            q=QDoubleSpinBox();q.setRange(lo,hi);q.setDecimals(dec);q.setSingleStep(step);q.setValue(v);q.setMinimumWidth(120);return q
        self.bselTargetContC=bds(3.0,0.1,20,0.5,1)
        self.bselTargetPeakC=bds(5.0,0.1,30,0.5,1)
        self.eCandidateAh=bds(0,0,500,1,1)
        self.eCandidateContA=bds(0,0,2000,5,1)
        self.eCandidatePeakA=bds(0,0,4000,5,1)
        cf.addWidget(QLabel("Target max continuous C-rate"),0,0);cf.addWidget(self.bselTargetContC,0,1)
        cf.addWidget(QLabel("Target max peak C-rate"),0,2);cf.addWidget(self.bselTargetPeakC,0,3)
        cf.addWidget(QLabel("Candidate capacity (Ah)"),1,0);cf.addWidget(self.eCandidateAh,1,1)
        cf.addWidget(QLabel("Candidate continuous rating (A)"),1,2);cf.addWidget(self.eCandidateContA,1,3)
        cf.addWidget(QLabel("Candidate peak rating (A)"),2,0);cf.addWidget(self.eCandidatePeakA,2,1)
        self.bselUseSuggested=QPushButton("ใช้ Suggested Ah เป็น Candidate")
        self.bselUseSuggested.setObjectName("primaryButton");self.bselUseSuggested.clicked.connect(self.apply_suggested_battery_capacity)
        cf.addWidget(self.bselUseSuggested,2,2,1,2)
        noteC=QLabel("C-rate เป็นเกณฑ์ออกแบบที่ผู้ใช้ตั้งเอง ไม่ใช่สเปกเซลล์จริงจากผู้ผลิต • ตอนซื้อให้ใช้ Continuous/Peak current rating จริงของ Pack/BMS")
        noteC.setWordWrap(True);noteC.setStyleSheet("color:#68420b;background:#fff8e9;padding:8px;border:1px solid #ead39a;border-radius:8px")
        cf.addWidget(noteC,3,0,1,4)
        bselOuter.addWidget(controlBox)

        self.bselCompareTable=QTableWidget(0,8)
        self.bselCompareTable.setHorizontalHeaderLabels([
            "Capacity","Rated energy","Runtime*","Full rounds",
            "Margin vs target","Required cont C","Required peak C","Check"
        ])
        self.bselCompareTable.verticalHeader().setVisible(False);self.bselCompareTable.setAlternatingRowColors(True)
        self.bselCompareTable.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.bselCompareTable.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.bselCompareTable.setMinimumHeight(300)
        bselOuter.addWidget(self.bselCompareTable)

        self.batterySelectionView=QTextEdit();self.batterySelectionView.setReadOnly(True);self.batterySelectionView.setMinimumHeight(210)
        bselOuter.addWidget(self.batterySelectionView)
        bselScroll=QScrollArea();bselScroll.setWidgetResizable(True);bselScroll.setFrameShape(QFrame.NoFrame);bselScroll.setWidget(bsel)
        self.eTabs.addTab(bselScroll,"เลือกแบต / Battery Selection")

        for obj in (self.bselTargetContC,self.bselTargetPeakC,self.eCandidateAh,self.eCandidateContA,self.eCandidatePeakA):
            obj.valueChanged.connect(self.update_battery_selection)

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
        self.euseOperationCycle.toggled.connect(self.calc_electrical)
        self.tabs.addTab(w,"Electrical / Battery")
        self.calc_electrical()

    def electrical_results(self):
        m=self.mt.value() if self.euseTorqueMass.isChecked() and hasattr(self,"mt") else self.emass.value()
        g=G; V=self.evolt.value(); v=self.espeed.value()/3.6
        one=self.eoneway.value(); Ls=min(self.eslopeLen.value(),one); theta=math.radians(self.eslopeDeg.value())
        runtime_h=self.eruntime.value(); runtime_s=runtime_h*3600.0

        # 1 operating round = drive out/back + lifting time + other stop.
        # Winch energy is excluded from the 72 V main battery because the project
        # uses a separate 12 V winch battery; only the lifting TIME affects how
        # many complete driving rounds fit inside the operating window.
        other_stop_s=self.estopTime.value()
        use_operation_cycle=bool(
            getattr(self,"euseOperationCycle",None)
            and self.euseOperationCycle.isChecked()
            and hasattr(self,"wopEvents")
        )
        lift_event_s=0.0
        lift_events_per_round=0
        lift_round_s=0.0
        if use_operation_cycle:
            op=self.winch_operation_results()
            lift_event_s=float(op["t_event"])
            lift_events_per_round=int(op["events_per_round"])
            lift_round_s=lift_event_s*lift_events_per_round

        cycle_distance=2.0*one
        drive_cycle_s=cycle_distance/v if v>0 else 0.0
        stop_s=lift_round_s+other_stop_s
        cycle_total_s=drive_cycle_s+stop_s
        cycles_theoretical=runtime_s/cycle_total_s if cycle_total_s>0 else 0.0
        cycles=int(math.floor(cycles_theoretical+1e-12))

        drive_time_total_s=cycles*drive_cycle_s
        lift_time_total_s=cycles*lift_round_s
        other_stop_total_s=cycles*other_stop_s
        operation_time_used_s=cycles*cycle_total_s
        remaining_time_s=max(0.0,runtime_s-operation_time_used_s)

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
        Fdown=max(0.0,Frrs-Fgrade)
        Pdown_mech=Fdown*v

        eff=max(self.edriveEff.value()/100.0,.01)
        up_eff=max(self.eupEff.value()/100.0,.01)
        Eflat_mech_cycle=Pflat_mech*flat_time_h
        Eup_mech_cycle=Pup_mech*up_time_h
        Edown_mech_cycle=Pdown_mech*down_time_h

        starts=self.estops.value()
        accel_time=max(self.eaccel.value(),.01)
        accel_a=v/accel_time
        Facc_peak=m*accel_a
        Pacc_peak_mech=(Fup+Facc_peak)*v
        Eacc_mech_cycle=(0.5*m*v*v/3600.0)*starts

        Emech_cycle=Eflat_mech_cycle+Eup_mech_cycle+Edown_mech_cycle+Eacc_mech_cycle
        Emech_total=Emech_cycle*cycles
        Ecalc_drive_cycle=Emech_cycle/eff
        Ecalc_drive=Ecalc_drive_cycle*cycles

        rated_total=self.emotorRated.value()*self.enmot.value()
        Pworst_batt=rated_total/up_eff
        Eworst_up_cycle=Pworst_batt*up_time_h
        Eflat_batt_cycle=Eflat_mech_cycle/eff
        Edown_batt_cycle=Edown_mech_cycle/eff
        Eacc_batt_cycle=Eacc_mech_cycle/eff
        Eworst_drive_cycle=Eflat_batt_cycle+Edown_batt_cycle+Eacc_batt_cycle+Eworst_up_cycle
        Eworst_drive=Eworst_drive_cycle*cycles

        use_worst=self.eworstRadio.isChecked()
        Edrive_cycle=Eworst_drive_cycle if use_worst else Ecalc_drive_cycle
        Edrive=Edrive_cycle*cycles

        # Auxiliary electronics are assumed ON for the full requested runtime.
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

    def battery_runtime_from_capacity(self,capacity_ah,e=None):
        """Reverse-calculate runtime/rounds for a candidate 72 V main battery."""
        e=e or self.electrical_results()
        ah=max(0.0,float(capacity_ah))
        rated_wh=e["V"]*ah
        # Preserve the same DoD + Reserve policy used by forward sizing:
        # Edesign=(Eload/DoD)*(1+Reserve)  -> allowed modeled load budget below.
        load_budget_wh=(rated_wh*e["dod"]/(1.0+e["reserve"])) if (1.0+e["reserve"])>0 else 0.0
        cycle_h=e["cycle_total_s"]/3600.0 if e["cycle_total_s"]>0 else 0.0
        aux_per_cycle=self.eaux.value()*cycle_h
        drive_per_cycle=max(0.0,e.get("Edrive_cycle",0.0))
        load_per_cycle=drive_per_cycle+aux_per_cycle
        avg_load_w=(load_per_cycle/cycle_h) if cycle_h>0 else 0.0
        runtime_h=(load_budget_wh/avg_load_w) if avg_load_w>0 else 0.0
        full_rounds=int(math.floor(runtime_h/cycle_h+1e-12)) if cycle_h>0 else 0
        used_full_rounds_wh=full_rounds*load_per_cycle
        remaining_after_full_rounds_wh=max(0.0,load_budget_wh-used_full_rounds_wh)
        target_margin_wh=rated_wh-e["Edesign"]
        target_margin_pct=(100.0*target_margin_wh/rated_wh) if rated_wh>0 else -100.0
        return dict(
            capacity_ah=ah,rated_wh=rated_wh,load_budget_wh=load_budget_wh,
            drive_per_cycle_wh=drive_per_cycle,aux_per_cycle_wh=aux_per_cycle,
            load_per_cycle_wh=load_per_cycle,avg_load_w=avg_load_w,
            runtime_h=runtime_h,full_rounds=full_rounds,
            remaining_after_full_rounds_wh=remaining_after_full_rounds_wh,
            target_margin_wh=target_margin_wh,target_margin_pct=target_margin_pct,
            target_energy_ok=(ah+1e-9>=e["Ah"])
        )

    def battery_selection_results(self):
        e=self.electrical_results();t=self.torque_results()
        energy_min=max(0.0,e["Ah"])
        cont_req=max(0.0,t["Ibatt"],e["Icalc_up"])
        peak_calc=max(0.0,e["Iworst"],e.get("Icalc_peak",0.0))
        controller_indicator=self.controllerCurrent.value()*max(1,t["n"]) if hasattr(self,"controllerCurrent") else 0.0
        target_cont=max(0.1,self.bselTargetContC.value()) if hasattr(self,"bselTargetContC") else 3.0
        target_peak=max(0.1,self.bselTargetPeakC.value()) if hasattr(self,"bselTargetPeakC") else 5.0
        ah_by_cont=cont_req/target_cont
        ah_by_peak=peak_calc/target_peak
        design_ah=max(energy_min,ah_by_cont,ah_by_peak)
        standards=[5,10,15,20,25,30,40,50,60,80,100,120,150,200]
        suggested=next((x for x in standards if x+1e-9>=design_ah),None)
        if suggested is None:
            suggested=math.ceil(design_ah/10.0)*10.0
        suggested=float(suggested)
        suggested_runtime=self.battery_runtime_from_capacity(suggested,e)
        design_runtime=suggested_runtime["runtime_h"]
        bms_cont=math.ceil(cont_req/5.0)*5.0 if cont_req>0 else 0.0
        bms_peak=math.ceil(peak_calc/5.0)*5.0 if peak_calc>0 else 0.0
        return dict(e=e,t=t,energy_min=energy_min,cont_req=cont_req,peak_calc=peak_calc,
                    controller_indicator=controller_indicator,target_cont=target_cont,target_peak=target_peak,
                    ah_by_cont=ah_by_cont,ah_by_peak=ah_by_peak,design_ah=design_ah,
                    standards=standards,suggested=suggested,design_runtime=design_runtime,
                    suggested_runtime=suggested_runtime,bms_cont=bms_cont,bms_peak=bms_peak)

    def apply_suggested_battery_capacity(self):
        if not hasattr(self,"eCandidateAh"):return
        r=self.battery_selection_results()
        self.eCandidateAh.setValue(r["suggested"])
        self.update_battery_selection()

    def _sync_battery_candidate_to_project_tools(self):
        if not all(hasattr(self,x) for x in ("eCandidateAh","eCandidateContA","eCandidatePeakA",
                                             "mainSelectedAh","mainBMSCont","mainBMSPeak")):
            return
        pairs=((self.eCandidateAh,self.mainSelectedAh),
               (self.eCandidateContA,self.mainBMSCont),
               (self.eCandidatePeakA,self.mainBMSPeak))
        changed=False
        for src,dst in pairs:
            if abs(dst.value()-src.value())>1e-9:
                old=dst.blockSignals(True);dst.setValue(src.value());dst.blockSignals(old);changed=True
        # Refresh mirrors directly. Do not call update_bms_check() here because that
        # can call Battery Selection again and create an update recursion.
        if changed and hasattr(self,"bmsView"):self.bmsView.setHtml(self.bms_check_html())
        if changed and hasattr(self,"designCheckView"):self.update_design_check()

    def _sync_project_tools_to_battery_candidate(self):
        if not all(hasattr(self,x) for x in ("eCandidateAh","eCandidateContA","eCandidatePeakA",
                                             "mainSelectedAh","mainBMSCont","mainBMSPeak")):
            return
        pairs=((self.mainSelectedAh,self.eCandidateAh),
               (self.mainBMSCont,self.eCandidateContA),
               (self.mainBMSPeak,self.eCandidatePeakA))
        for src,dst in pairs:
            if abs(dst.value()-src.value())>1e-9:
                old=dst.blockSignals(True);dst.setValue(src.value());dst.blockSignals(old)
        self.update_battery_selection()

    def update_battery_selection(self,*_):
        if not hasattr(self,"batterySelectionView"):return
        r=self.battery_selection_results();e=r["e"]
        self.bselMinAhLabel.setText(f"{r['energy_min']:.2f} Ah\n({e['Edesign']:.0f} Wh @ {e['V']:.0f} V)")
        self.bselContLabel.setText(f"{r['cont_req']:.1f} A\nBMS ≥ {r['bms_cont']:.0f} A")
        self.bselPeakLabel.setText(f"{r['peak_calc']:.1f} A\nBMS peak ≥ {r['bms_peak']:.0f} A")
        self.bselSuggestedLabel.setText(f"{r['suggested']:.0f} Ah\n≈ {r['design_runtime']:.2f} h")

        rows=r["standards"]
        self.bselCompareTable.setRowCount(len(rows))
        for i,ah in enumerate(rows):
            rev=self.battery_runtime_from_capacity(ah,e)
            rated_wh=rev["rated_wh"]
            cont_c=r["cont_req"]/ah if ah>0 else 999
            peak_c=r["peak_calc"]/ah if ah>0 else 999
            energy_ok=ah+1e-9>=r["energy_min"]
            c_ok=cont_c<=r["target_cont"]+1e-9 and peak_c<=r["target_peak"]+1e-9
            status="PASS*" if energy_ok and c_ok else ("ENERGY LOW" if not energy_ok else "C-RATE CHECK")
            margin=rev["target_margin_pct"]
            vals=[
                f"{ah:.0f} Ah",f"{rated_wh:.0f} Wh",f"{rev['runtime_h']:.2f} h",
                f"{rev['full_rounds']} รอบ",f"{margin:+.1f}%",
                f"{cont_c:.2f} C",f"{peak_c:.2f} C",status
            ]
            for c,val in enumerate(vals):
                item=QTableWidgetItem(val);item.setTextAlignment(Qt.AlignCenter)
                if c==4:
                    item.setForeground(QColor("#176337" if margin>=0 else "#b42318"))
                if c==7:
                    item.setForeground(QColor("#176337" if status=="PASS*" else "#b42318"))
                    font=item.font();font.setBold(True);item.setFont(font)
                self.bselCompareTable.setItem(i,c,item)

        cand_ah=self.eCandidateAh.value();cand_cont=self.eCandidateContA.value();cand_peak=self.eCandidatePeakA.value()
        energy_ok=cand_ah>0 and cand_ah+1e-9>=r["energy_min"]
        cont_ok=cand_cont>0 and cand_cont+1e-9>=r["cont_req"]
        peak_ok=cand_peak>0 and cand_peak+1e-9>=r["peak_calc"]
        all_ok=energy_ok and cont_ok and peak_ok
        cand_rev=self.battery_runtime_from_capacity(cand_ah,e)
        cand_wh=cand_rev["rated_wh"]
        cand_runtime=cand_rev["runtime_h"]
        cand_rounds=cand_rev["full_rounds"]
        cand_margin=cand_rev["target_margin_pct"]
        def state(ok,set_value=True):
            if not set_value:return "<span style='color:#b54708'><b>NOT SET</b></span>"
            return "<span style='color:#176337'><b>PASS</b></span>" if ok else "<span style='color:#b42318'><b>CHECK</b></span>"

        overall=("READY TO VERIFY DATASHEET" if all_ok else "NOT READY")
        overall_color="#176337" if all_ok else "#b42318"
        self.batterySelectionView.setHtml(f"""
        <h2>Battery Purchase Check / ตรวจแบตก่อนซื้อ</h2>
        <p><b>Minimum by energy:</b> {r['energy_min']:.2f} Ah ({e['Edesign']:.0f} Wh) — รวม DoD และ Reserve แล้ว</p>
        <p><b>Current requirement:</b> Continuous ≈ {r['cont_req']:.1f} A, calculated Peak ≈ {r['peak_calc']:.1f} A</p>
        <p><b>Recommended BMS floor:</b> Continuous ≥ <b>{r['bms_cont']:.0f} A</b> • Peak ≥ <b>{r['bms_peak']:.0f} A</b>
        (ปัดขึ้นทีละ 5 A จากค่าคำนวณ)</p>
        <p><b>Design target C-rate:</b> ≤ {r['target_cont']:.1f}C continuous, ≤ {r['target_peak']:.1f}C peak
        → ต้องการอย่างน้อย max({r['energy_min']:.2f}, {r['ah_by_cont']:.2f}, {r['ah_by_peak']:.2f}) = <b>{r['design_ah']:.2f} Ah</b></p>
        <p style='background:#eefaf4;padding:10px;border:1px solid #a9d7ba'>
        <b>Suggested standard size to investigate: {r['suggested']:.0f} Ah @ {e['V']:.0f} V</b><br>
        Reverse calculation: runtime ≈ <b>{r['suggested_runtime']['runtime_h']:.2f} h</b> •
        full operating rounds ≈ <b>{r['suggested_runtime']['full_rounds']} รอบ</b><br>
        Required C ≈ {r['cont_req']/max(r['suggested'],1e-9):.2f}C continuous /
        {r['peak_calc']/max(r['suggested'],1e-9):.2f}C peak
        </p>

        <h3>Candidate ที่กรอก — Reverse Calculation</h3>
        <table border='1' cellspacing='0' cellpadding='6'>
        <tr><th>Check</th><th>Required</th><th>Candidate</th><th>Status</th></tr>
        <tr><td>Capacity</td><td>≥ {r['energy_min']:.2f} Ah</td><td>{cand_ah:.1f} Ah ({cand_wh:.0f} Wh)</td><td>{state(energy_ok,cand_ah>0)}</td></tr>
        <tr><td>BMS Continuous</td><td>≥ {r['cont_req']:.1f} A</td><td>{cand_cont:.1f} A</td><td>{state(cont_ok,cand_cont>0)}</td></tr>
        <tr><td>BMS Peak</td><td>≥ {r['peak_calc']:.1f} A</td><td>{cand_peak:.1f} A</td><td>{state(peak_ok,cand_peak>0)}</td></tr>
        </table>
        <p><b>ถ้าใช้แบต Candidate นี้:</b> Estimated repeating-operation runtime ≈ <b>{cand_runtime:.2f} h</b>
        • ทำงานครบประมาณ <b>{cand_rounds} รอบ</b>
        • Capacity margin เทียบเป้าหมาย {e['runtime_h']:.2f} h = <b>{cand_margin:+.1f}%</b></p>
        <p>พลังงานที่อนุญาตให้ใช้ตาม DoD + Reserve policy ≈ {cand_rev['load_budget_wh']:.0f} Wh;
        พลังงานเฉลี่ยต่อ Operating Cycle ≈ {cand_rev['load_per_cycle_wh']:.2f} Wh</p>
        <p style='color:{overall_color};font-size:13pt'><b>{overall}</b></p>
        <p style='background:#fff8e9;padding:10px;border:1px solid #ead39a'>
        <b>สำคัญ:</b> Runtime เป็นค่าประมาณจาก Operating Cycle ปัจจุบัน (Drive + Lift time + Other stop + Auxiliary).
        พลังงานวินช์ 12 V ไม่ถูกรวมในแบตรถ 72 V.
        ก่อนซื้อจริงต้องยืนยัน Pack voltage, chemistry, Continuous/Peak current ของเซลล์และ BMS, connector, fuse, charger และ Battery Current limit ของ VESC.
        ค่า Controller indicator ≈ {r['controller_indicator']:.1f} A เป็น conservative indicator และอาจเป็น motor/phase-current setting ไม่ใช่ battery current โดยตรง.
        </p>
        <p>*PASS ในตารางหมายถึงผ่าน Energy + C-rate target ที่กำหนด ไม่ใช่การรับรองแบตจากผู้ขาย</p>
        """)
        self._sync_battery_candidate_to_project_tools()

    def calc_electrical(self):
        if not hasattr(self,"eSummary"): return
        q=self.electrical_results()
        mode="WORST-CASE FULL RATED POWER" if q["use_worst"] else "CALCULATED LOAD MODEL"
        self.eSummary.setText(
            f"{mode}\\n"
            f"Completed rounds in {q['runtime_h']:.2f} h = {q['cycles']} (theory {q['cycles_theoretical']:.2f}) | Total travel ≈ {q['cycles']*q['cycle_distance']/1000:.3f} km\\n"
            f"Time/round: Drive {q['drive_cycle_s']:.1f} s + Lift {q['lift_round_s']:.1f} s + Other {q['other_stop_s']:.1f} s = {q['cycle_total_s']:.1f} s\\n"
            f"Mechanical energy = {q['Emech_total']:.1f} Wh | Estimated drive energy = {q['Edrive']:.1f} Wh\\n"
            f"Auxiliary = {q['Eaux']:.1f} Wh | Load total = {q['Eload']:.1f} Wh\\n"
            f"Battery design = {q['Edesign']:.1f} Wh → {q['Ah']:.2f} Ah @ {q['V']:.1f} V"
        )

        cycles=max(q["cycles"],1)
        drive_per_trip=q["Edrive_cycle"]
        load_per_trip=q["Eload"]/cycles if q["cycles"]>0 else 0.0
        self.tripDistanceLabel.setText(f"{q['cycle_distance']:.1f} m")
        self.tripTimeLabel.setText(f"{q['cycle_total_s']/60.0:.2f} min")
        self.tripCountLabel.setText(f"{q['cycles']} รอบเต็ม\\n(theory {q['cycles_theoretical']:.2f})")
        self.tripEnergyLabel.setText(f"{drive_per_trip:.2f} Wh / รอบ")
        self.tripDriveTotalLabel.setText(f"{q['Edrive']:.1f} Wh")
        self.tripAuxLabel.setText(f"{q['Eaux']:.1f} Wh")
        self.tripLoadTotalLabel.setText(f"{q['Eload']:.1f} Wh")
        self.tripBatteryLabel.setText(f"{q['Edesign']:.0f} Wh\\n= {q['Ah']:.2f} Ah @ {q['V']:.0f} V")
        self.tripEnergyExplain.setHtml(f"""
        <h3 style='color:#17324d'>อ่านหน้านี้แบบง่าย</h3>
        <p><b>1 รอบไป-กลับ</b> = {q['cycle_distance']:.1f} m</p>
        <p>เวลารถวิ่ง <b>{q['drive_cycle_s']:.2f} s</b> + เวลางานยก <b>{q['lift_round_s']:.2f} s</b> + เวลาหยุดอื่น <b>{q['other_stop_s']:.2f} s</b>
        = <b>{q['cycle_total_s']/60.0:.2f} นาที/รอบ</b></p>
        <p>จำนวนรอบเชิงทฤษฎี = {q['cycles_theoretical']:.2f} รอบ → นับเฉพาะรอบที่ทำครบ = <b>{q['cycles']} รอบเต็ม</b></p>
        <p><b>พลังงานขับต่อรอบ</b> = {drive_per_trip:.2f} Wh จากโมเดล <b>{'Worst-case' if q['use_worst'] else 'Calculated'}</b></p>
        <p><b>{q['cycles']} รอบเต็ม</b> ใช้พลังงานขับรถ 72 V รวม = {q['Edrive']:.1f} Wh</p>
        <p><b>หมายเหตุ:</b> เวลายกถูกนำมาคิดเพื่อหาจำนวนรอบ แต่พลังงานวินช์ไม่รวมใน Main Battery เพราะวินช์ใช้แบต 12 V แยก</p>
        <p>บวก Auxiliary {q['Eaux']:.1f} Wh → <b>พลังงานรวมก่อนเผื่อแบต = {q['Eload']:.1f} Wh</b></p>
        <p>หลังเผื่อ DoD {q['dod']*100:.0f}% และ Reserve {q['reserve']*100:.0f}% →
        <b style='color:#b42318'>ต้องการประมาณ {q['Edesign']:.0f} Wh = {q['Ah']:.2f} Ah @ {q['V']:.0f} V</b></p>
        <p style='background:#fff8e9;padding:10px;border:1px solid #ead39a'>
        ถ้าต้องการดูเฉพาะ “รถวิ่งไป-กลับกินไฟเท่าไร” ให้ดูช่อง <b>พลังงานขับ / 1 รอบ</b>.
        ค่าเฉลี่ยรวม Auxiliary ต่อรอบเทียบเท่า ≈ {load_per_trip:.2f} Wh/รอบ แต่ Auxiliary เป็นโหลดตามเวลา ไม่ใช่โหลดตามระยะทางโดยตรง.
        </p>
        """)
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
        เวลารวมต่อรอบ = เวลาวิ่ง + เวลางานยก + เวลาหยุดอื่น;
        จำนวนรอบเต็ม = floor(เวลาทำงานทั้งหมด ÷ เวลารวมต่อรอบ)</p>
        <p><b>แทนค่า:</b> รถวิ่ง {q['drive_cycle_s']:.2f} s
        + งานยก {q['lift_round_s']:.2f} s
        + หยุดอื่น {q['other_stop_s']:.2f} s
        = <b>{q['cycle_total_s']:.2f} s/รอบ</b>.
        จำนวนรอบเชิงทฤษฎี = {q['cycles_theoretical']:.2f} รอบ
        และนับเฉพาะงานที่ทำครบ = <b>{q['cycles']} รอบ</b></p>
        <p>เวลายกมีผลต่อจำนวนรอบของรถ แต่พลังงานวินช์ 12 V คำนวณแยก ไม่ถูกนำมาบวกกับ Main Battery 72 V</p>
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
        <tr><td>Completed rounds</td><td><b>{q['cycles']}</b> (theory {q['cycles_theoretical']:.2f})</td></tr>
        <tr><td>Drive / Lift / Other per round</td><td>{q['drive_cycle_s']:.1f} / {q['lift_round_s']:.1f} / {q['other_stop_s']:.1f} s</td></tr>
        <tr><td>Total round time</td><td>{q['cycle_total_s']:.1f} s = {q['cycle_total_s']/60.0:.2f} min</td></tr>
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
        if hasattr(self,"batterySelectionView"):self.update_battery_selection()

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
        self.tm=ds(300,1,5000,1); self.tgrade=ds(19,0,45,2)
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
        w=QWidget();self.slopePage=w
        l=QVBoxLayout(w);l.setContentsMargins(14,14,14,14);l.setSpacing(10)

        geom=QGroupBox("RAMP GEOMETRY / คำนวณองศาและเปอร์เซ็นต์ความชันจากค่าที่วัดจริง")
        gl=QHBoxLayout(geom)
        gf=QFormLayout()
        self.rampRiseCm=spin(55,0,10000,.1,1)
        self.rampRunCm=spin(280,.1,100000,.1,1)
        self.rampMeasuredCm=spin(290,0,100000,.1,1)
        self.rampMass=spin(300,0,5000,1,1)
        self.rampUseMainMass=QCheckBox("ใช้มวลจาก Main Battery 72 V")
        self.rampUseMainMass.setChecked(True)
        for lab,q in [
            ("ความสูง h (cm)",self.rampRiseCm),
            ("ระยะราบ x (cm)",self.rampRunCm),
            ("ความยาวทางลาดที่วัดได้ (cm)",self.rampMeasuredCm),
            ("มวลสำหรับคำนวณ F_slope (kg)",self.rampMass),
        ]:
            q.setMinimumWidth(150);gf.addRow(lab,q)
        gf.addRow(self.rampUseMainMass)
        gl.addLayout(gf,1)

        self.rampGeomOut=QTextEdit();self.rampGeomOut.setReadOnly(True)
        self.rampGeomOut.setMinimumHeight(270)
        self.rampGeomOut.setStyleSheet("font-size:11pt;background:white")
        gl.addWidget(self.rampGeomOut,2)
        l.addWidget(geom)

        btnrow=QHBoxLayout()
        calcRamp=QPushButton("คำนวณ Ramp Geometry")
        calcRamp.setObjectName("primaryButton")
        calcRamp.clicked.connect(self.update_ramp_geometry)
        applyAngle=QPushButton("ใช้มุมนี้กับ Torque + Main Battery + Stability")
        applyAngle.clicked.connect(self.apply_ramp_angle_to_project)
        applyLength=QPushButton("ใช้ L ทฤษฎีกับ Slope Length ใน Main Battery")
        applyLength.clicked.connect(self.apply_ramp_length_to_battery)
        btnrow.addWidget(calcRamp);btnrow.addWidget(applyAngle);btnrow.addWidget(applyLength)
        l.addLayout(btnrow)

        g=QGroupBox("UPHILL DRIVING STABILITY / เสถียรภาพขณะรถวิ่งขึ้นทางลาด")
        f=QFormLayout(g)
        self.slope=spin(19,0,45,.01,2);self.hcg=spin(.55,.05,3,.05);self.acc=spin(.278,0,5,.05,3)
        for a,b in [
            ("Slope angle α / มุมทางลาด (deg)",self.slope),
            ("Combined CG height hCG / ความสูง CG รวม (m)",self.hcg),
            ("Acceleration a / ความเร่งรถ (m/s²)",self.acc)
        ]:
            f.addRow(a,b);b.valueChanged.connect(self.calc_all)
        l.addWidget(g)

        self.slopeout=QPlainTextEdit();self.slopeout.setReadOnly(True)
        self.slopeout.setStyleSheet("font-size:12px")
        l.addWidget(self.slopeout,1)

        for q in (self.rampRiseCm,self.rampRunCm,self.rampMeasuredCm,self.rampMass):
            q.valueChanged.connect(self.update_ramp_geometry)
        self.rampUseMainMass.toggled.connect(self.update_ramp_geometry)
        if hasattr(self,"emass"):
            self.emass.valueChanged.connect(self.update_ramp_geometry)

        self.tabs.addTab(w,"2. Driving / Slope / ทางลาด")
        self.update_ramp_geometry()

    def ramp_geometry_results(self):
        h=max(0.0,self.rampRiseCm.value())
        x=max(1e-9,self.rampRunCm.value())
        lm=max(0.0,self.rampMeasuredCm.value())
        mass=(self.emass.value() if self.rampUseMainMass.isChecked() and hasattr(self,"emass")
              else self.rampMass.value())
        L=math.hypot(x,h)
        angle=math.degrees(math.atan2(h,x))
        slope_pct=(h/x)*100.0
        ratio=(h/L) if L>0 else 0.0
        diff=(lm-L) if lm>0 else 0.0
        diff_abs=abs(diff)
        diff_pct=(diff_abs/L*100.0) if (lm>0 and L>0) else 0.0
        measured_angle=(math.degrees(math.asin(max(-1.0,min(1.0,h/lm))))
                        if lm>=h and lm>0 else None)
        f_slope=mass*G*math.sin(math.radians(angle))
        f_ratio=mass*G*ratio
        return dict(h=h,x=x,lm=lm,L=L,angle=angle,slope_pct=slope_pct,ratio=ratio,
                    diff=diff,diff_abs=diff_abs,diff_pct=diff_pct,
                    measured_angle=measured_angle,mass=mass,
                    f_slope=f_slope,f_ratio=f_ratio)

    def update_ramp_geometry(self,*_):
        if not hasattr(self,"rampGeomOut"):return
        r=self.ramp_geometry_results()
        measured_angle=("—" if r["measured_angle"] is None else f'{r["measured_angle"]:.2f}°')
        self.rampGeomOut.setHtml(f"""
        <h2 style='color:#17456b'>การคำนวณองศาและความชันของทางลาด</h2>
        <p><b>ค่าที่วัด:</b> h = {r['h']:.1f} cm • x = {r['x']:.1f} cm • L_measured = {r['lm']:.1f} cm</p>

        <h3>1) ความยาวทางลาดจากทฤษฎีพีทาโกรัส</h3>
        <p><b>L = √(x² + h²)</b><br>
        = √({r['x']:.1f}² + {r['h']:.1f}²)
        = <b>{r['L']:.2f} cm = {r['L']/100.0:.3f} m</b></p>
        <p>ค่าที่วัดได้ {r['lm']:.2f} cm → ต่างจากทฤษฎี <b>{r['diff_abs']:.2f} cm</b> ({r['diff_pct']:.2f}%)</p>

        <h3>2) มุมทางลาด</h3>
        <p><b>θ = tan⁻¹(h/x)</b><br>
        = tan⁻¹({r['h']:.1f}/{r['x']:.1f})
        = <b style='color:#176337'>{r['angle']:.2f}°</b></p>

        <h3>3) เปอร์เซ็นต์ความชัน</h3>
        <p><b>Slope (%) = (h/x) × 100</b><br>
        = ({r['h']:.1f}/{r['x']:.1f}) × 100
        = <b style='color:#176337'>{r['slope_pct']:.2f}%</b></p>

        <h3>4) ตรวจจากความยาวที่วัด</h3>
        <p>มุมจาก L_measured = <b>{measured_angle}</b></p>

        <h3>5) ค่าที่ใช้คำนวณแรงมอเตอร์</h3>
        <p><b>F_slope = m g sin(θ)</b><br>
        = {r['mass']:.1f} × 9.81 × sin({r['angle']:.2f}°)
        = <b>{r['f_slope']:.2f} N</b></p>
        <p>ตรวจซ้ำ: <b>F_slope = m g (h/L)</b> = {r['f_ratio']:.2f} N</p>

        <p style='background:#fff3e8;border:1px solid #efc19b;padding:9px'>
        <b>สำคัญ:</b> {r['slope_pct']:.2f}% คือเปอร์เซ็นต์ Slope ไม่ใช่ {r['slope_pct']:.2f}°.
        ในสูตร sin/cos ของมอเตอร์ให้ใช้ <b>{r['angle']:.2f}°</b>.
        </p>
        """)

    def apply_ramp_angle_to_project(self):
        r=self.ramp_geometry_results()
        angle=r["angle"]
        targets=[getattr(self,"slope",None),getattr(self,"tgrade",None),getattr(self,"eslopeDeg",None)]
        for q in targets:
            if q is None:continue
            old=q.blockSignals(True);q.setValue(angle);q.blockSignals(old)
        self.update_ramp_geometry()
        self.calc_all()
        if hasattr(self,"calc_torque"):self.calc_torque()
        if hasattr(self,"calc_electrical"):self.calc_electrical()
        self.statusBar().showMessage(
            f"ใช้มุมทางลาด {angle:.2f}° กับ Torque + Main Battery + Stability แล้ว",4000
        )

    def apply_ramp_length_to_battery(self):
        r=self.ramp_geometry_results()
        length_m=r["L"]/100.0
        if hasattr(self,"eslopeLen"):
            self.eslopeLen.setValue(length_m)
        if hasattr(self,"calc_electrical"):self.calc_electrical()
        self.statusBar().showMessage(
            f"ใช้ความยาวทางลาดทฤษฎี {length_m:.3f} m ใน Main Battery แล้ว",4000
        )


    def make_fbd(self):
        w=QWidget();self.fbdPage=w
        l=QVBoxLayout(w);l.setContentsMargins(14,14,14,14);l.setSpacing(10)

        guide=QLabel(
            "วิธีอ่าน FBD แบบง่าย:  1) หาจุดแดง Pivot  →  "
            "2) ดูแรงที่ทำให้คว่ำ  →  3) ดูแรงที่ช่วยต้าน  →  "
            "4) เปรียบเทียบ SF กับค่าที่ต้องการ"
        )
        guide.setWordWrap(True)
        guide.setStyleSheet(
            "background:#eef7ff;border:1px solid #b9d8f3;border-radius:10px;"
            "padding:10px;font-size:11pt;font-weight:700;color:#17456b"
        )
        l.addWidget(guide)

        top=QHBoxLayout()
        self.fbdModeCombo=QComboBox(); self.fbdModeCombo.addItems([
            "คว่ำซ้าย / Side Left",
            "คว่ำขวา / Side Right",
            "คว่ำหน้า / Front",
            "คว่ำหลัง / Rear",
            "รถบนทางลาด / Slope"
        ])
        self.fbdModeCombo.setMinimumWidth(190)

        self.fbdSimple=QCheckBox("โหมดง่ายมาก (แนะนำสำหรับนำเสนอ)")
        self.fbdSimple.setChecked(True)
        self.fbdSimple.setToolTip("เปิด = ลดข้อมูลบนรูป เหลือเฉพาะแรงหลัก Pivot และผล M_O / M_R / SF")

        self.fbdAuto=QCheckBox("Auto: เลือกทิศวิกฤตให้")
        self.fbdAuto.setChecked(False)
        self.fbdAuto.setToolTip("ถ้าเปิด โปรแกรมจะเลือก Side/Front/Rear ที่ SF ต่ำที่สุดตามมุมเครนปัจจุบัน")

        self.fbdCriticalLabel=QLabel("เลือกกรณีที่ต้องการดู")
        self.fbdCriticalLabel.setStyleSheet(
            "font-weight:700;color:#6542a5;background:#f5f1ff;padding:6px 10px;border-radius:8px"
        )

        top.addWidget(QLabel("กรณี:"))
        top.addWidget(self.fbdModeCombo)
        top.addWidget(self.fbdSimple)
        top.addWidget(self.fbdAuto)
        top.addStretch(1)
        top.addWidget(self.fbdCriticalLabel)
        l.addLayout(top)

        self.forceDiagram=ForceDiagram(self)
        self.forceDiagram.setSimpleMode(True)
        l.addWidget(self.forceDiagram,1)

        self.fbdExplain=QTextEdit()
        self.fbdExplain.setReadOnly(True)
        self.fbdExplain.setMaximumHeight(220)
        self.fbdExplain.setStyleSheet(
            "font-size:11pt;background:white;border:1px solid #d7e1eb;border-radius:10px;padding:6px"
        )
        l.addWidget(self.fbdExplain)

        self.fbdModeCombo.currentIndexChanged.connect(self._on_fbd_mode_changed)
        self.fbdSimple.toggled.connect(self._on_fbd_simple_changed)
        self.fbdAuto.toggled.connect(self.update_auto_fbd)
        self.tabs.addTab(w,"3. FBD / แผนภาพแรง")
        self.update_auto_fbd()
        self.update_fbd_explanation()

    def _on_fbd_mode_changed(self,i):
        if not self.fbdAuto.isChecked():
            self.forceDiagram.setCaseAngle(None)
            self.forceDiagram.setMode(i)
            self.fbdCriticalLabel.setText("Manual: "+self.fbdModeCombo.currentText())
        self.update_fbd_explanation()

    def _on_fbd_simple_changed(self,on):
        self.forceDiagram.setSimpleMode(on)
        self.fbdCriticalLabel.setText(
            ("โหมดเข้าใจง่าย • " if on else "โหมดรายละเอียดวิศวกรรม • ")
            + self.fbdModeCombo.currentText()
        )
        self.update_fbd_explanation()

    def update_auto_fbd(self):
        if not hasattr(self,"fbdAuto") or not hasattr(self,"forceDiagram"): return
        self.forceDiagram.setSimpleMode(
            self.fbdSimple.isChecked() if hasattr(self,"fbdSimple") else True
        )
        if not self.fbdAuto.isChecked():
            self.forceDiagram.setCaseAngle(None)
            self.forceDiagram.setMode(self.fbdModeCombo.currentIndex())
            self.fbdCriticalLabel.setText("Manual: "+self.fbdModeCombo.currentText())
            if hasattr(self,"fbdExplain"): self.update_fbd_explanation()
            return
        d=self.inputs();side=self.calc_side(d,theta=d["th"])[0];front,rear=self.longitudinal_sf_at(d,d["th"])
        side_mode=1 if d["th"]>=0 else 0
        side_name="Side Right / คว่ำขวา" if d["th"]>=0 else "Side Left / คว่ำซ้าย"
        vals=[(side_name,side,side_mode),("Front / คว่ำหน้า",front,2),("Rear / คว่ำหลัง",rear,3)]
        typ,val,mode=min(vals,key=lambda x:x[1])
        self.fbdModeCombo.blockSignals(True);self.fbdModeCombo.setCurrentIndex(mode);self.fbdModeCombo.blockSignals(False)
        self.forceDiagram.setCaseAngle(d["th"])
        self.forceDiagram.setMode(mode)
        self.fbdCriticalLabel.setText(
            f"Auto Critical @ θ={d['th']:.0f}°: {typ} | SF={'∞' if val>=999 else f'{val:.3f}'}"
        )
        if hasattr(self,"fbdExplain"): self.update_fbd_explanation()

    def update_fbd_explanation(self):
        if not hasattr(self,"fbdExplain") or not hasattr(self,"fbdModeCombo"): return
        d=self.inputs()
        mode=self.fbdModeCombo.currentIndex()

        def result_box(MO,MR,sf):
            sf_text="∞" if sf>=999 else f"{sf:.3f}"
            ok=sf>=d["req"]
            color="#176337" if ok else "#b42318"
            status="ผ่านเกณฑ์เบื้องต้น" if ok else "ไม่ผ่าน — ต้องปรับแบบ"
            return (
                f"<div style='background:#f8fafc;border:1px solid #d7e1eb;padding:10px;border-radius:8px'>"
                f"<b>ผล:</b> M_O = {MO:.1f} N·m &nbsp; | &nbsp; "
                f"M_R = {MR:.1f} N·m &nbsp; | &nbsp; "
                f"<span style='color:{color}'><b>SF = {sf_text} → {status}</b></span><br>"
                f"เกณฑ์ที่ตั้งไว้: SF ≥ {d['req']:.2f}"
                f"</div>"
            )

        if mode in (0,1):
            left=(mode==0);angle=-90 if left else 90
            sf,MO,MR=self.calc_side(d,theta=angle)
            side="ซ้าย" if left else "ขวา"
            html=f"""
            <h3 style='color:#17456b;margin:2px'>วิธีอ่าน: รถคว่ำด้าน{side}</h3>
            <ol>
              <li><b>Pivot (จุดแดง)</b> = ล้อด้าน{side}ที่รถจะหมุนรอบเมื่อเริ่มคว่ำ</li>
              <li><b>W โหลด + W แขนเครน</b> ที่ยื่นออกนอก Pivot จะสร้าง <span style='color:#b42318'><b>โมเมนต์ทำให้คว่ำ M_O</b></span></li>
              <li><b>น้ำหนักตัวรถ</b> ที่ยังอยู่ด้านในฐานล้อจะสร้าง <span style='color:#176337'><b>โมเมนต์ต้าน M_R</b></span></li>
              <li>เอา <b>M_R ÷ M_O</b> จะได้ Safety Factor</li>
            </ol>
            {result_box(MO,MR,sf)}
            <p><b>จำง่าย:</b> ถ้า M_R มากกว่า M_O มากพอ รถจะต้านการคว่ำได้ดีขึ้น</p>
            """
        elif mode in (2,3):
            front=(mode==2);direction="front" if front else "rear"
            label="หน้า" if front else "หลัง"
            angle=d["th"] if self.fbdAuto.isChecked() else d["th"]
            bal=self.longitudinal_moment_balance(d,angle,direction)
            html=f"""
            <h3 style='color:#17456b;margin:2px'>วิธีอ่าน: รถคว่ำด้าน{label}</h3>
            <ol>
              <li><b>Pivot (จุดแดง)</b> = แนวล้อ{label}ที่รถจะหมุนรอบ</li>
              <li>แรงน้ำหนักที่อยู่ <b>เลย Pivot ออกไป</b> จะช่วยทำให้คว่ำ</li>
              <li>แรงน้ำหนักที่อยู่ <b>ด้านในฐานล้อ</b> จะช่วยต้านการคว่ำ</li>
              <li>โปรแกรมรวมแรง × ระยะจาก Pivot เป็น M_O และ M_R</li>
            </ol>
            {result_box(bal['mo'],bal['mr'],bal['sf'])}
            <p>มุมเครนที่ใช้ในภาพ = <b>{angle:.0f}°</b> &nbsp; | &nbsp; Wheelbase = {d['WB']:.3f} m</p>
            """
        else:
            sr=self.slope_stability_results(d)
            alpha=math.radians(self.slope.value())
            MR=d["mt"]*G*math.cos(alpha)*max(0.0,sr["rear_arm"])
            MO=d["mt"]*max(0.0,sr["h"])*(G*math.sin(alpha)+max(0.0,sr["acc"]))
            html=f"""
            <h3 style='color:#17456b;margin:2px'>วิธีอ่าน: รถบนทางลาด</h3>
            <ol>
              <li><b>mg</b> = น้ำหนักรถ ชี้ลงแนวดิ่งเสมอ</li>
              <li><b>mg sinα</b> = ส่วนของน้ำหนักที่ดึงรถลงตามทางลาด</li>
              <li><b>N ≈ mg cosα</b> = แรงปฏิกิริยาตั้งฉากกับพื้น</li>
              <li><b>F_a = ma</b> = ผลจากการเร่งขึ้นลาด ซึ่งเพิ่มแนวโน้มคว่ำด้านหลัง</li>
            </ol>
            {result_box(MO,MR,sr['sf'])}
            <p><b>มุมทางลาด α = {self.slope.value():.2f}°</b> — ใช้องศาใน sin/cos ไม่ใช้ค่า Slope %</p>
            """
        self.fbdExplain.setHtml(html)

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

    def longitudinal_moment_balance(self,d,th,direction="front"):
        """Return SF, overturning/restoring moments and component moment arms."""
        rear=-d["WB"]/2; front=d["WB"]/2
        xc=rear+d["xC"]
        xload=xc+d["L"]*math.cos(math.radians(th))
        xboom=xc+(d["L"]/2)*math.cos(math.radians(th))
        mveh=max(0.0,d["mt"]-d["ml"]-d["mb"])
        front_case=str(direction).lower().startswith("f")
        pivot=front if front_case else rear
        sense=1.0 if front_case else -1.0

        mo=mr=0.0;components=[]
        for name,mass,x,is_payload in (
            ("Vehicle",mveh,d["xCG"],False),
            ("Payload",d["ml"],xload,True),
            ("Boom",d["mb"],xboom,False),
        ):
            signed=sense*(x-pivot)
            if signed>1e-12:
                factor=d["kd"] if is_payload else 1.0
                force=factor*mass*G;arm=signed;moment=force*arm
                mo+=moment;role="overturning"
            else:
                force=mass*G;arm=max(0.0,-signed);moment=force*arm
                mr+=moment;role="restoring"
            components.append(dict(name=name,mass=mass,x=x,force=force,arm=arm,moment=moment,role=role))
        sf=mr/mo if mo>1e-12 else 999
        return dict(sf=sf,mo=mo,mr=mr,pivot=pivot,rear=rear,front=front,xc=xc,
                    xload=xload,xboom=xboom,components=components,
                    direction=("front" if front_case else "rear"))

    def longitudinal_sf_at(self,d,th):
        front=self.longitudinal_moment_balance(d,th,"front")
        rear=self.longitudinal_moment_balance(d,th,"rear")
        return front["sf"],rear["sf"]

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


    def stability_fbd_cases(self,d=None):
        d=d or self.inputs()
        front_candidates=[]
        rear_candidates=[]
        for a in range(-90,91):
            sfF,sfR=self.longitudinal_sf_at(d,a)
            front_candidates.append((sfF,a))
            rear_candidates.append((sfR,a))
        front_angle=min(front_candidates,key=lambda x:x[0])[1]
        rear_angle=min(rear_candidates,key=lambda x:x[0])[1]
        side_sf_left=self.calc_side(d,theta=-90)[0]
        side_sf_right=self.calc_side(d,theta=90)[0]
        front_sf=self.longitudinal_sf_at(d,front_angle)[0]
        rear_sf=self.longitudinal_sf_at(d,rear_angle)[1]
        slope=self.slope_stability_results(d)
        return [
            {"key":"side_left","title":"SIDE TIPPING - LEFT","thai":"การคว่ำด้านซ้าย","mode":0,"angle":-90.0,"sf":side_sf_left},
            {"key":"side_right","title":"SIDE TIPPING - RIGHT","thai":"การคว่ำด้านขวา","mode":1,"angle":90.0,"sf":side_sf_right},
            {"key":"front","title":"FRONT TIPPING","thai":"การคว่ำด้านหน้า","mode":2,"angle":float(front_angle),"sf":front_sf},
            {"key":"rear","title":"REAR TIPPING","thai":"การคว่ำด้านหลัง","mode":3,"angle":float(rear_angle),"sf":rear_sf},
            {"key":"slope","title":"SLOPE STABILITY","thai":"เสถียรภาพบนทางลาด","mode":4,"angle":None,"sf":slope["sf"]},
        ]

    def _render_stability_fbd_png(self,mode,path,angle=None):
        fd=ForceDiagram(self)
        fd.resize(1100,720)
        fd.setSimpleMode(True)
        fd.setMode(mode)
        fd.setCaseAngle(angle)
        pix=QPixmap(fd.size())
        pix.fill(QColor("white"))
        fd.render(pix)
        ok=pix.save(str(path),"PNG")
        fd.deleteLater()
        if not ok:
            raise RuntimeError("Could not render FBD image")
        return path

    def stability_fbd_report_html(self,tmpdir,d=None):
        """Generate beginner-first FBD pages plus a technical appendix."""
        d=d or self.inputs()
        cases=self.stability_fbd_cases(d)
        rows=[];simple_pages=[];appendix_pages=[]

        for idx,case in enumerate(cases,1):
            key=case["key"];angle=case["angle"]
            sf=float(case["sf"])
            sf_text="∞" if sf>=999 else f"{sf:.3f}"
            ok=sf>=d["req"]
            status="ผ่านเกณฑ์" if ok else "ไม่ผ่าน — ต้องปรับแบบ"
            status_color="#176337" if ok else "#b42318"
            angle_text="-" if angle is None else f"{angle:.0f}°"
            fp=Path(tmpdir)/("fbd_"+key+".png")
            self._render_stability_fbd_png(case["mode"],fp,angle)

            if key in ("side_left","side_right"):
                _,MO,MR=self.calc_side(d,theta=angle)
                side_th="ซ้าย" if key=="side_left" else "ขวา"
                mveh=max(0.0,d["mt"]-d["ml"]-d["mb"])
                read_steps=[
                    f"<b>1.</b> จุดแดงที่ล้อ{side_th} = จุดที่รถจะเริ่มหมุนคว่ำ",
                    "<b>2.</b> ลูกศรสีแดง = น้ำหนักที่พยายามดึงรถให้คว่ำ",
                    "<b>3.</b> ลูกศรสีน้ำเงิน = น้ำหนักรถที่ช่วยต้านการคว่ำ",
                    "<b>4.</b> ดูกล่อง SF ด้านล่าง: ถ้า SF มากกว่าหรือเท่ากับค่าที่กำหนดถือว่าผ่านเบื้องต้น",
                ]
                meaning=(
                    f"กรณีนี้จำลองเครนยื่นไปด้าน{side_th}. "
                    f"รถจะเริ่มคว่ำรอบล้อด้าน{side_th}. "
                    "ล้อฝั่งตรงข้ามจะเริ่มยกจากพื้นและแรงปฏิกิริยาฝั่งนั้นจะลดลง."
                )
                technical=(
                    f"<p><b>Track width W</b> = {d['W']:.3f} m → W/2 = {d['W']/2:.3f} m</p>"
                    f"<p>W_vehicle = {mveh:.2f}×9.81 = {mveh*G:.2f} N<br>"
                    f"W_boom = {d['mb']:.2f}×9.81 = {d['mb']*G:.2f} N<br>"
                    f"W_payload = {d['ml']:.2f}×9.81 = {d['ml']*G:.2f} N</p>"
                    f"<p>F_payload,design = Kdyn×m_L×g = {d['kd']:.2f}×{d['ml']:.2f}×9.81 = "
                    f"{d['kd']*d['ml']*G:.2f} N เมื่อ Payload อยู่ฝั่งทำให้คว่ำ</p>"
                    f"<p><b>M_O = {MO:.2f} N·m</b><br><b>M_R = {MR:.2f} N·m</b><br>"
                    f"<b>SF = M_R/M_O = {sf_text}</b></p>"
                )

            elif key in ("front","rear"):
                bal=self.longitudinal_moment_balance(d,angle,key)
                MO=bal["mo"];MR=bal["mr"]
                dir_th="หน้า" if key=="front" else "หลัง"
                read_steps=[
                    f"<b>1.</b> จุดแดงที่แนวล้อ{dir_th} = จุดที่รถจะเริ่มหมุนคว่ำ",
                    "<b>2.</b> น้ำหนักที่อยู่เลยจุดแดงออกไป = ช่วยทำให้คว่ำ",
                    "<b>3.</b> น้ำหนักที่อยู่ด้านในช่วงล้อ = ช่วยต้านการคว่ำ",
                    "<b>4.</b> โปรแกรมรวม แรง × ระยะจากจุดแดง แล้วคำนวณ SF ให้",
                ]
                meaning=(
                    f"กรณีนี้ตรวจการคว่ำด้าน{dir_th}. "
                    f"Pivot อยู่ที่แนวล้อ{dir_th}. "
                    "ตำแหน่งของรถ แขนเครน และโหลดเมื่อเทียบกับ Pivot เป็นตัวกำหนดว่าแรงนั้นช่วยคว่ำหรือช่วยต้าน."
                )
                component_rows="".join(
                    f"<tr><td>{c['name']}</td><td>{c['force']:.2f}</td><td>{c['arm']:.3f}</td>"
                    f"<td>{c['moment']:.2f}</td><td>{'ทำให้คว่ำ' if c['role']=='overturning' else 'ช่วยต้าน'}</td></tr>"
                    for c in bal["components"]
                )
                technical=(
                    f"<p>Rear axle = {bal['rear']:.3f} m, Front axle = {bal['front']:.3f} m, "
                    f"Pivot = {bal['pivot']:.3f} m</p>"
                    f"<p>x_crane = {bal['xc']:.3f} m, x_boom = {bal['xboom']:.3f} m, "
                    f"x_load = {bal['xload']:.3f} m, x_CG = {d['xCG']:.3f} m</p>"
                    "<table border='1' cellspacing='0' cellpadding='5' style='border-collapse:collapse;width:100%'>"
                    "<tr><th>แรง</th><th>F (N)</th><th>ระยะแขน d (m)</th><th>M (N·m)</th><th>หน้าที่</th></tr>"
                    f"{component_rows}</table>"
                    f"<p><b>M_O = {MO:.2f} N·m</b><br><b>M_R = {MR:.2f} N·m</b><br>"
                    f"<b>SF = M_R/M_O = {sf_text}</b></p>"
                )

            else:
                sr=self.slope_stability_results(d)
                alpha=math.radians(self.slope.value())
                mass=d["mt"]
                MR=mass*G*math.cos(alpha)*max(0.0,sr["rear_arm"])
                MO=mass*max(0.0,sr["h"])*(G*math.sin(alpha)+max(0.0,sr["acc"]))
                read_steps=[
                    "<b>1.</b> จุดแดงด้านหลัง = จุดที่รถอาจหมุนคว่ำขณะขึ้นลาด",
                    "<b>2.</b> แรงสีแดง = ส่วนของน้ำหนักที่ดึงรถลงตามทางลาด",
                    "<b>3.</b> น้ำหนักรถและตำแหน่ง CG เป็นตัวช่วยต้านการคว่ำ",
                    "<b>4.</b> แรงจากการเร่งขึ้นลาดเพิ่มแนวโน้มคว่ำด้านหลัง",
                ]
                meaning=(
                    "บนทางลาด น้ำหนักรถยังชี้ลงแนวดิ่ง แต่สามารถแยกเป็นแรงตามทางลาดและแรงกดตั้งฉากกับทางลาด. "
                    "โปรแกรมใช้ตำแหน่ง CG, มุมลาด และความเร่งเพื่อคำนวณ SF_slope."
                )
                technical=(
                    f"<p>α = {self.slope.value():.2f}°, h_CG = {sr['h']:.3f} m, "
                    f"d_rear = {sr['rear_arm']:.3f} m, a = {sr['acc']:.3f} m/s²</p>"
                    f"<p>mg sinα = {mass*G*math.sin(alpha):.2f} N<br>"
                    f"mg cosα = {mass*G*math.cos(alpha):.2f} N<br>"
                    f"F_a = ma = {mass*sr['acc']:.2f} N</p>"
                    f"<p><b>M_R = {MR:.2f} N·m</b><br><b>M_O = {MO:.2f} N·m</b><br>"
                    f"<b>SF_slope = M_R/M_O = {sf_text}</b></p>"
                )

            rows.append(
                f"<tr><td>{idx}</td><td>{case['thai']}</td><td>{sf_text}</td>"
                f"<td style='color:{status_color}'><b>{status}</b></td></tr>"
            )

            simple_pages.append(f"""
            <div style='page-break-before:always'></div>
            <h1>FBD {idx}: {case['thai']}</h1>
            <p style='font-size:11pt'><b>{meaning}</b></p>

            <div style='background:#eef7ff;border:1px solid #b9d8f3;padding:10px;margin:8px 0'>
              <b>อ่านรูปนี้แค่ 4 อย่าง</b><br>
              {'<br>'.join(read_steps)}
            </div>

            <p style='text-align:center'><img src='{fp.as_uri()}' width='660'></p>

            <table border='1' cellspacing='0' cellpadding='8' style='border-collapse:collapse;width:100%'>
              <tr>
                <td style='background:#fff1f0'><b>ฝั่งพยายามทำให้คว่ำ</b><br><span style='font-size:15pt'>{MO:.1f} N·m</span></td>
                <td style='background:#eefaf4'><b>ฝั่งช่วยต้านการคว่ำ</b><br><span style='font-size:15pt'>{MR:.1f} N·m</span></td>
                <td style='background:{"#eefaf4" if ok else "#fff1f0"}'><b>คำตอบ</b><br><span style='font-size:15pt;color:{status_color}'>SF = {sf_text}<br>{status}</span></td>
              </tr>
            </table>

            <p style='background:#fff8e9;border:1px solid #ead39a;padding:9px'>
            <b>สูตรเดียวที่ต้องจำ:</b> Safety Factor = โมเมนต์ที่ช่วยต้าน ÷ โมเมนต์ที่พยายามทำให้คว่ำ<br>
            <b>SF = M_R / M_O</b> และโปรแกรมตั้งเกณฑ์ไว้ที่ <b>SF ≥ {d['req']:.2f}</b>
            </p>
            """)

            appendix_pages.append(f"""
            <div style='page-break-before:always'></div>
            <h2>รายละเอียดวิศวกรรม FBD {idx}: {case['title']}</h2>
            <p><b>Case angle:</b> {angle_text} &nbsp; | &nbsp; <b>Target SF:</b> {d['req']:.2f}</p>
            {technical}
            <p style='background:#f7fafc;border:1px solid #d7e1eb;padding:8px'>
            เมื่อแรงปฏิกิริยาของล้อฝั่งตรงข้าม Pivot ลดลงเข้าใกล้ 0 N รถกำลังเข้าใกล้จุดเริ่มคว่ำ.
            การคำนวณนี้เป็น Preliminary rigid-body stability calculation และต้องยืนยันด้วยมวล/CG จริง.
            </p>
            """)

        summary=f"""
        <h2>สรุป FBD การคว่ำทุกด้าน</h2>
        <div style='background:#eef7ff;border:1px solid #b9d8f3;padding:12px;margin:8px 0'>
        <b>ส่วนแรกของรายงานตั้งใจทำให้อ่านง่ายสำหรับนำเสนอ:</b><br>
        ดูเพียง 4 อย่าง — <b>จุดหมุนแดง → ฝั่งทำให้คว่ำ → ฝั่งช่วยต้าน → ค่า SF</b><br>
        รายละเอียดสูตรและตารางตัวเลขเต็มอยู่ใน <b>ภาคผนวกวิศวกรรม</b> หลัง FBD ทั้ง 5 รูป
        </div>
        <table border='1' cellspacing='0' cellpadding='7' style='border-collapse:collapse;width:100%'>
        <tr><th>#</th><th>กรณี</th><th>Safety Factor</th><th>ผล</th></tr>
        {''.join(rows)}
        </table>
        """
        appendix=(
            "<div style='page-break-before:always'></div>"
            "<h1>ภาคผนวกวิศวกรรม / ENGINEERING APPENDIX</h1>"
            "<p>ส่วนนี้เก็บสูตร ตัวแปร ระยะโมเมนต์ และตัวเลขสำหรับตรวจสอบโดยอาจารย์/วิศวกร. "
            "ถ้าต้องการดูภาพรวมอย่างเดียว สามารถอ่านเฉพาะ FBD 1–5 ก่อนหน้านี้ได้.</p>"
        )
        return summary+"".join(simple_pages)+appendix+"".join(appendix_pages)


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
            for name,widget in (("vehicle",getattr(self,"view",None)),("stability_map",getattr(self,"graph",None))):
                if widget is not None:
                    fp=tmpdir/f"{name}.png"
                    if widget.grab().save(str(fp)):
                        figures.append((name,fp.as_uri()))
            fig_html="".join(
                f"<h3>{name.replace('_',' ').title()}</h3><p><img src='{uri}' width='650'></p>"
                for name,uri in figures
            )
            fbd_html=self.stability_fbd_report_html(tmpdir,d)
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
                +"<div style='page-break-before:always'></div>"+fbd_html
                +"<div style='page-break-before:always'></div><h2>Other Figures / รูปประกอบเพิ่มเติม</h2>"+fig_html
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
    """Engineering FBD for side/front/rear tipping and slope stability."""
    def __init__(self,app):
        super().__init__()
        self.app=app
        self.mode=0
        self.caseAngle=None
        self.simpleMode=True
        self.setMinimumHeight(500)

    def setMode(self,i):
        self.mode=int(i)
        self.update()

    def setCaseAngle(self,angle):
        self.caseAngle=angle
        self.update()

    def setSimpleMode(self,on):
        self.simpleMode=bool(on)
        self.update()

    def _simple_text(self,p,x,y,label,size=11,bold=False,color="#17324d"):
        p.setPen(QPen(QColor(color)))
        f=p.font();f.setPointSize(size);f.setBold(bold);p.setFont(f)
        p.drawText(QPointF(x,y),label)

    def _simple_box(self,p,x,y,w,h,title,value,fill,border):
        p.setPen(QPen(QColor(border),2))
        p.setBrush(QColor(fill))
        p.drawRoundedRect(QRectF(x,y,w,h),12,12)
        self._simple_text(p,x+14,y+24,title,10,True,border)
        self._simple_text(p,x+14,y+50,value,13,True,"#17324d")

    def _simple_header(self,p,title,subtitle):
        self._simple_text(p,24,34,title,17,True,"#17324d")
        self._simple_text(p,24,58,subtitle,11,False,"#52606d")
        y=86
        self._simple_text(p,24,y,"อ่านรูปจากเลข 1 → 4",11,True,"#17324d")
        self._simple_text(p,205,y,"1 จุดแดง = จุดหมุนคว่ำ",10,True,"#b42318")
        self._simple_text(p,410,y,"2 สีแดง = ทำให้คว่ำ",10,True,"#b42318")
        self._simple_text(p,590,y,"3 สีน้ำเงิน = ช่วยต้าน",10,True,"#2459b3")
        self._simple_text(p,790,y,"4 สีเขียว = แรงจากพื้น",10,True,"#16803a")

    def _simple_side_view(self,p,d,left_case=True):
        side_th="ซ้าย" if left_case else "ขวา"
        side_en="LEFT" if left_case else "RIGHT"
        self._simple_header(
            p,
            f"FBD การคว่ำด้าน{side_th} / SIDE TIPPING - {side_en}",
            "ดู 3 อย่าง: จุดหมุนแดง → แรงที่อยู่นอกจุดหมุน → เปรียบเทียบ M_R กับ M_O"
        )
        ww,hh=self.width(),self.height()
        gy=hh*0.62
        xL=ww*0.30;xR=ww*0.70;cx=(xL+xR)/2
        deck=gy-80
        pivot_x=xL if left_case else xR
        other_x=xR if left_case else xL
        out_sign=-1 if left_case else 1

        p.setPen(QPen(QColor("#64748b"),4))
        p.drawLine(QPointF(80,gy),QPointF(ww-80,gy))
        p.setPen(QPen(QColor("#334155"),2));p.setBrush(QColor("#eef2f6"))
        p.drawRoundedRect(QRectF(xL-95,deck,xR-xL+190,55),12,12)
        for x in (xL,xR):
            p.setBrush(QColor("#1f2933"));p.setPen(QPen(QColor("#1f2933"),2))
            p.drawEllipse(QPointF(x,gy-3),27,27)

        # pivot and reactions
        self.pivot(p,QPointF(pivot_x,gy-1),"1) จุดหมุนคว่ำ")
        self.A(p,QPointF(pivot_x,gy+70),QPointF(pivot_x,gy-34),"#16803a","4) แรงจากพื้น",QPointF(10,-4))
        self._simple_text(p,other_x-80,gy+65,"ล้ออีกฝั่งเริ่มยก → แรงพื้นลดลง",9,False,"#7a8793")

        mast_x=cx;mast_top=deck-90
        tip=mast_x+out_sign*min(230,ww*0.27)
        p.setPen(QPen(QColor("#f28c28"),12,Qt.SolidLine,Qt.RoundCap))
        p.drawLine(QPointF(mast_x,deck),QPointF(mast_x,mast_top))
        p.drawLine(QPointF(mast_x,mast_top),QPointF(tip,mast_top))
        p.setPen(QPen(QColor("#475569"),2));p.setBrush(QColor("#dfe6ee"))
        p.drawRect(QRectF(tip-24,mast_top+18,48,40))

        mveh=max(0.0,d["mt"]-d["ml"]-d["mb"])
        Wv=mveh*G;Wb=d["mb"]*G;Wp=d["ml"]*G
        boom_cg=(mast_x+tip)/2
        self.A(p,QPointF(cx,deck-95),QPointF(cx,deck-8),"#2459b3",f"3) น้ำหนักรถช่วยต้าน = {Wv:.0f} N",QPointF(10,-6))
        self.A(p,QPointF(boom_cg,mast_top-65),QPointF(boom_cg,mast_top-8),"#b42318",f"2) น้ำหนักแขน = {Wb:.0f} N",QPointF(10,-6))
        self.A(p,QPointF(tip,mast_top-80),QPointF(tip,mast_top+14),"#b42318",f"2) น้ำหนักโหลด = {Wp:.0f} N",QPointF(10,-6))

        self.D(p,QPointF(xL,gy+88),QPointF(xR,gy+88),f"Track = {d['W']:.3f} m")

        sf,MO,MR=self.app.calc_side(d,theta=(-90 if left_case else 90))
        sf_text="∞" if sf>=999 else f"{sf:.3f}"
        status="ผ่าน" if sf>=d["req"] else "ไม่ผ่าน"
        bw=(ww-80)/3
        yb=hh-118
        self._simple_box(p,20,yb,bw-10,78,"ฝั่งพยายามทำให้คว่ำ",f"{MO:.1f} N·m","#fff1f0","#b42318")
        self._simple_box(p,20+bw,yb,bw-10,78,"ฝั่งช่วยต้านการคว่ำ",f"{MR:.1f} N·m","#eefaf4","#176337")
        sf_fill="#eefaf4" if sf>=d["req"] else "#fff1f0"
        sf_border="#176337" if sf>=d["req"] else "#b42318"
        self._simple_box(p,20+2*bw,yb,bw-10,78,"Safety Factor",f"SF = {sf_text} → {status}",sf_fill,sf_border)
        self._simple_text(p,24,hh-16,f"จำง่าย: SF = ฝั่งช่วยต้าน ÷ ฝั่งพยายามคว่ำ  |  ต้องได้ ≥ {d['req']:.2f}",11,True,"#17324d")

    def _simple_long_view(self,p,d,front_case=True):
        case_th="ด้านหน้า" if front_case else "ด้านหลัง"
        case_en="FRONT" if front_case else "REAR"
        self._simple_header(
            p,
            f"FBD การคว่ำ{case_th} / {case_en} TIPPING",
            "Pivot คือแนวล้อที่รถจะหมุนรอบ; แรงด้านนอก Pivot ทำให้คว่ำ แรงด้านในช่วยต้าน"
        )
        ww,hh=self.width(),self.height()
        gy=hh*0.62
        rear_px=ww*0.30;front_px=ww*0.70
        deck=gy-80
        pivot_px=front_px if front_case else rear_px
        other_px=rear_px if front_case else front_px

        p.setPen(QPen(QColor("#64748b"),4));p.drawLine(QPointF(80,gy),QPointF(ww-80,gy))
        p.setPen(QPen(QColor("#334155"),2));p.setBrush(QColor("#eef2f6"))
        p.drawRoundedRect(QRectF(rear_px-95,deck,front_px-rear_px+190,55),12,12)
        for x in (rear_px,front_px):
            p.setBrush(QColor("#1f2933"));p.setPen(QPen(QColor("#1f2933"),2));p.drawEllipse(QPointF(x,gy-3),27,27)
        self.pivot(p,QPointF(pivot_px,gy-1),"1) จุดหมุนคว่ำ")
        self.A(p,QPointF(pivot_px,gy+70),QPointF(pivot_px,gy-34),"#16803a","4) แรงจากพื้น",QPointF(10,-4))
        self._simple_text(p,other_px-78,gy+65,"ล้ออีกฝั่งเริ่มยก → แรงพื้นลดลง",9,False,"#7a8793")

        angle=self._case_angle(d["th"])
        bal=self.app.longitudinal_moment_balance(d,angle,("front" if front_case else "rear"))
        rear_m=-d["WB"]/2;front_m=d["WB"]/2
        px_per_m=(front_px-rear_px)/max(d["WB"],1e-9)
        def sx(x):
            raw=rear_px+(x-rear_m)*px_per_m
            return max(85,min(ww-85,raw))
        mast=sx(bal["xc"]);top=deck-105;tip=sx(bal["xload"]);bcg=sx(bal["xboom"]);vcg=sx(d["xCG"])
        p.setPen(QPen(QColor("#f28c28"),12,Qt.SolidLine,Qt.RoundCap))
        p.drawLine(QPointF(mast,deck),QPointF(mast,top));p.drawLine(QPointF(mast,top),QPointF(tip,top))
        p.setPen(QPen(QColor("#475569"),2));p.setBrush(QColor("#dfe6ee"));p.drawRect(QRectF(tip-23,top+18,46,40))

        comp={c["name"]:c for c in bal["components"]}
        for name,x,label,yy in (
            ("Vehicle",vcg,f"น้ำหนักรถ = {comp['Vehicle']['force']:.0f} N",deck-8),
            ("Boom",bcg,f"น้ำหนักแขน = {comp['Boom']['force']:.0f} N",top-8),
            ("Payload",tip,f"น้ำหนักโหลด = {comp['Payload']['force']:.0f} N",top+14),
        ):
            role=comp[name]["role"]
            color="#b42318" if role=="overturning" else "#2459b3"
            prefix="2) ทำให้คว่ำ: " if role=="overturning" else "3) ช่วยต้าน: "
            start_y=(deck-95 if name=="Vehicle" else top-70 if name=="Boom" else top-85)
            self.A(p,QPointF(x,start_y),QPointF(x,yy),color,prefix+label,QPointF(10,-6))

        self.D(p,QPointF(rear_px,gy+88),QPointF(front_px,gy+88),f"Wheelbase = {d['WB']:.3f} m")
        sf=bal["sf"];sf_text="∞" if sf>=999 else f"{sf:.3f}"
        status="ผ่าน" if sf>=d["req"] else "ไม่ผ่าน"
        bw=(ww-80)/3;yb=hh-118
        self._simple_box(p,20,yb,bw-10,78,"ฝั่งพยายามทำให้คว่ำ",f"{bal['mo']:.1f} N·m","#fff1f0","#b42318")
        self._simple_box(p,20+bw,yb,bw-10,78,"ฝั่งช่วยต้านการคว่ำ",f"{bal['mr']:.1f} N·m","#eefaf4","#176337")
        sf_fill="#eefaf4" if sf>=d["req"] else "#fff1f0";sf_border="#176337" if sf>=d["req"] else "#b42318"
        self._simple_box(p,20+2*bw,yb,bw-10,78,"Safety Factor",f"SF = {sf_text} → {status}",sf_fill,sf_border)
        self._simple_text(p,24,hh-16,f"มุมเครนในรูป = {angle:.0f}°  |  SF ต้อง ≥ {d['req']:.2f}",11,True,"#17324d")

    def _simple_slope_view(self,p,d):
        self._simple_header(
            p,
            "FBD รถบนทางลาด / STABILITY ON SLOPE",
            "น้ำหนัก mg แยกเป็นแรงตามทางลาด mg sinα และแรงกดพื้น mg cosα; ความเร่งขึ้นลาดเพิ่มแนวโน้มคว่ำ"
        )
        ww,hh=self.width(),self.height()
        alpha=math.radians(self.app.slope.value())
        x0,y0=120,hh*0.63;run=ww*0.68;x1=x0+run;y1=y0-run*math.tan(alpha)
        p.setPen(QPen(QColor("#64748b"),5));p.drawLine(QPointF(x0,y0),QPointF(x1,y1))
        cx,cy=(x0+x1)/2,(y0+y1)/2-50
        u=QPointF(math.cos(alpha),-math.sin(alpha));n=QPointF(-math.sin(alpha),-math.cos(alpha))
        pts=QPolygonF([
            QPointF(cx,cy)+u*(-110)+n*(-34),QPointF(cx,cy)+u*(110)+n*(-34),
            QPointF(cx,cy)+u*(110)+n*(34),QPointF(cx,cy)+u*(-110)+n*(34)
        ])
        p.setBrush(QColor("#eef2f6"));p.setPen(QPen(QColor("#334155"),2));p.drawPolygon(pts)
        p.setBrush(QColor("#111827"));p.drawEllipse(QPointF(cx,cy),7,7)
        self._simple_text(p,cx+10,cy-8,"CG",10,True)

        mass=d["mt"];W=mass*G;Wpar=W*math.sin(alpha);Wnorm=W*math.cos(alpha);Fa=mass*self.app.acc.value()
        self.A(p,QPointF(cx,cy-100),QPointF(cx,cy+100),"#2459b3",f"3) น้ำหนักรถ = {W:.0f} N",QPointF(10,-6))
        self.A(p,QPointF(cx,cy),QPointF(cx,cy)+u*(-150),"#b42318",f"2) แรงดึงลงตามลาด = {Wpar:.0f} N",QPointF(10,-6))
        self.A(p,QPointF(cx,cy)+n*(-25),QPointF(cx,cy)+n*(-135),"#16803a",f"4) แรงจากพื้น = {Wnorm:.0f} N",QPointF(10,-6))
        if Fa>0.5:
            self.A(p,QPointF(cx,cy)+QPointF(0,18),QPointF(cx,cy)+u*(-105)+QPointF(0,18),"#d97706",f"F_a = ma = {Fa:.0f} N",QPointF(10,18))
        pivot=QPointF(x0+run*.18,y0-run*.18*math.tan(alpha))
        self.pivot(p,pivot,"1) จุดหมุนด้านหลัง")
        self._simple_text(p,90,y0+34,f"มุมทางลาด α = {self.app.slope.value():.2f}°",11,True,"#17324d")

        sr=self.app.slope_stability_results(d)
        MR=mass*G*math.cos(alpha)*max(0.0,sr["rear_arm"])
        MO=mass*max(0.0,sr["h"])*(G*math.sin(alpha)+max(0.0,sr["acc"]))
        sf=sr["sf"];sf_text="∞" if sf>=999 else f"{sf:.3f}";status="ผ่าน" if sf>=d["req"] else "ไม่ผ่าน"
        bw=(ww-80)/3;yb=hh-118
        self._simple_box(p,20,yb,bw-10,78,"ฝั่งพยายามทำให้คว่ำ",f"{MO:.1f} N·m","#fff1f0","#b42318")
        self._simple_box(p,20+bw,yb,bw-10,78,"ฝั่งช่วยต้านการคว่ำ",f"{MR:.1f} N·m","#eefaf4","#176337")
        sf_fill="#eefaf4" if sf>=d["req"] else "#fff1f0";sf_border="#176337" if sf>=d["req"] else "#b42318"
        self._simple_box(p,20+2*bw,yb,bw-10,78,"Safety Factor",f"SF = {sf_text} → {status}",sf_fill,sf_border)
        self._simple_text(p,24,hh-16,"จำง่าย: mg sinα พยายามพารถไหล/คว่ำลงลาด ส่วน N ตั้งฉากกับพื้น",10,True,"#17324d")

    def A(self,p,a,b,c,label,off=QPointF(7,-7)):
        p.setPen(QPen(QColor(c),3,Qt.SolidLine,Qt.RoundCap))
        p.drawLine(a,b)
        ang=math.atan2(b.y()-a.y(),b.x()-a.x())
        for d in (2.55,-2.55):
            p.drawLine(b,QPointF(b.x()+12*math.cos(ang+d),b.y()+12*math.sin(ang+d)))
        p.setPen(QPen(QColor(c)))
        p.drawText(b+off,label)

    def D(self,p,a,b,label,vertical=False):
        pen=QPen(QColor("#52606d"),1,Qt.DashLine)
        p.setPen(pen)
        p.drawLine(a,b)
        if vertical:
            p.drawLine(a+QPointF(-5,0),a+QPointF(5,0))
            p.drawLine(b+QPointF(-5,0),b+QPointF(5,0))
            p.drawText((a+b)/2+QPointF(7,0),label)
        else:
            p.drawLine(a+QPointF(0,-5),a+QPointF(0,5))
            p.drawLine(b+QPointF(0,-5),b+QPointF(0,5))
            p.drawText((a+b)/2+QPointF(-35,-8),label)

    def title(self,p,t,sub):
        p.setPen(QPen(QColor("#17324d")))
        font=p.font()
        font.setBold(True)
        font.setPointSize(11)
        p.setFont(font)
        p.drawText(18,28,t)
        font.setBold(False)
        font.setPointSize(8)
        p.setFont(font)
        p.setPen(QPen(QColor("#52606d")))
        p.drawText(18,50,sub)

    def pivot(self,p,pt,label):
        p.setPen(QPen(QColor("#b42318"),2))
        p.setBrush(QColor("#ffe5e2"))
        p.drawEllipse(pt,8,8)
        p.drawText(pt+QPointF(10,-10),label)

    def moment_mark(self,p,center,text,color="#b42318"):
        p.setPen(QPen(QColor(color),3))
        r=31
        rect=QRectF(center.x()-r,center.y()-r,2*r,2*r)
        p.drawArc(rect,25*16,255*16)
        end=QPointF(center.x()+r*math.cos(math.radians(25)),
                    center.y()-r*math.sin(math.radians(25)))
        self.A(p,end+QPointF(-14,-3),end,QColor(color).name(),"")
        p.drawText(center+QPointF(-22,-42),text)

    def _case_angle(self,default):
        return float(default if self.caseAngle is None else self.caseAngle)

    def _side_view(self,p,d,left_case=True):
        side="LEFT" if left_case else "RIGHT"
        self.title(
            p,
            f"FREE BODY DIAGRAM - SIDE TIPPING ({side})",
            "Front view: weights act downward, ground reactions act upward, red point is the tipping pivot"
        )
        ww,hh=self.width(),self.height()
        gy=hh*.72
        xL=ww*.31
        xR=ww*.69
        cx=(xL+xR)/2
        deck=gy-115
        pivot_x=xL if left_case else xR
        out_sign=-1 if left_case else 1

        p.setPen(QPen(QColor("#64748b"),3))
        p.drawLine(QPointF(55,gy),QPointF(ww-55,gy))
        p.setPen(QPen(QColor("#334155"),2))
        p.setBrush(QColor("#e5e9ee"))
        p.drawRoundedRect(QRectF(xL-80,deck,xR-xL+160,60),10,10)

        for x,label in ((xL,"R_L"),(xR,"R_R")):
            p.setPen(QPen(QColor("#1f2933"),2))
            p.setBrush(QColor("#1f2933"))
            p.drawEllipse(QPointF(x,gy-8),27,27)
            self.A(p,QPointF(x,gy+70),QPointF(x,gy-38),"#16803a",label,QPointF(8,-5))

        self.pivot(p,QPointF(pivot_x,gy-3),"Pivot / Tipping axis")

        mast_x=cx
        mast_top=deck-105
        p.setPen(QPen(QColor("#f28c28"),11,Qt.SolidLine,Qt.RoundCap))
        p.drawLine(QPointF(mast_x,deck),QPointF(mast_x,mast_top))
        boom_tip_x=mast_x+out_sign*min(240,ww*.30)
        p.drawLine(QPointF(mast_x,mast_top),QPointF(boom_tip_x,mast_top))

        p.setPen(QPen(QColor("#475569"),2))
        p.setBrush(QColor("#d8dee7"))
        p.drawRect(QRectF(boom_tip_x-22,mast_top+20,44,38))
        p.drawLine(QPointF(boom_tip_x,mast_top),QPointF(boom_tip_x,mast_top+20))

        mveh=max(0.0,d["mt"]-d["ml"]-d["mb"])
        Wv=mveh*G
        Wb=d["mb"]*G
        Wp=d["ml"]*G
        self.A(p,QPointF(cx,deck-105),QPointF(cx,deck-8),"#2459b3",f"W_vehicle = {Wv:.0f} N")
        boom_cg=(mast_x+boom_tip_x)/2
        self.A(p,QPointF(boom_cg,mast_top-65),QPointF(boom_cg,mast_top-8),"#2459b3",f"W_boom = {Wb:.0f} N")
        self.A(p,QPointF(boom_tip_x,mast_top-82),QPointF(boom_tip_x,mast_top+18),"#d62828",f"W_payload = {Wp:.0f} N")

        self.D(p,QPointF(xL,gy+72),QPointF(xR,gy+72),f"Track W = {d['W']:.3f} m")
        self.D(p,QPointF(pivot_x,gy+105),QPointF(cx,gy+105),f"W/2 = {d['W']/2:.3f} m")

        sf,MO,MR=self.app.calc_side(d,theta=(-90 if left_case else 90))
        self.moment_mark(p,QPointF(pivot_x,gy-70),f"M_O = {MO:.0f} N.m","#b42318")
        p.setPen(QPen(QColor("#176337"),2))
        p.drawText(18,hh-88,f"M_R = {MR:.1f} N.m    M_O = {MO:.1f} N.m    SF = {'INF' if sf>=999 else f'{sf:.3f}'}")
        p.setPen(QPen(QColor("#52606d")))
        p.drawText(18,hh-60,"R_L/R_R = ground reactions. At incipient tipping, the reaction opposite the pivot tends to 0 N.")
        p.drawText(18,hh-36,f"Payload adverse design force uses F_L = Kdyn*m_L*g = {d['kd']*d['ml']*G:.1f} N when it creates overturning moment.")

    def _long_view(self,p,d,front_case=True):
        case="FRONT" if front_case else "REAR"
        self.title(
            p,
            f"FREE BODY DIAGRAM - {case} TIPPING",
            "Side view: longitudinal moment balance about the front or rear wheel-contact line"
        )
        ww,hh=self.width(),self.height()
        gy=hh*.74
        rear=ww*.30
        front=ww*.70
        deck=gy-100
        pivot_x=front if front_case else rear

        p.setPen(QPen(QColor("#64748b"),3))
        p.drawLine(QPointF(55,gy),QPointF(ww-55,gy))
        p.setPen(QPen(QColor("#334155"),2))
        p.setBrush(QColor("#e5e9ee"))
        p.drawRoundedRect(QRectF(rear-80,deck,front-rear+160,58),10,10)

        for x,label in ((rear,"R_rear"),(front,"R_front")):
            p.setPen(QPen(QColor("#1f2933"),2))
            p.setBrush(QColor("#1f2933"))
            p.drawEllipse(QPointF(x,gy-8),28,28)
            self.A(p,QPointF(x,gy+70),QPointF(x,gy-38),"#16803a",label,QPointF(8,-5))

        self.pivot(p,QPointF(pivot_x,gy-3),"Pivot / Tipping axis")

        angle=self._case_angle(d["th"])
        rear_m=-d["WB"]/2
        front_m=d["WB"]/2
        xc=rear_m+d["xC"]
        xload=xc+d["L"]*math.cos(math.radians(angle))
        xboom=xc+(d["L"]/2)*math.cos(math.radians(angle))
        def sx(x):
            return rear+(x-rear_m)/max(d["WB"],1e-9)*(front-rear)

        mast=sx(xc)
        top=deck-120
        p.setPen(QPen(QColor("#f28c28"),11,Qt.SolidLine,Qt.RoundCap))
        p.drawLine(QPointF(mast,deck),QPointF(mast,top))
        tip=sx(xload)
        p.drawLine(QPointF(mast,top),QPointF(tip,top))
        p.setPen(QPen(QColor("#475569"),2))
        p.setBrush(QColor("#d8dee7"))
        p.drawRect(QRectF(tip-21,top+20,42,36))
        p.drawLine(QPointF(tip,top),QPointF(tip,top+20))

        mveh=max(0.0,d["mt"]-d["ml"]-d["mb"])
        Wv=mveh*G
        Wb=d["mb"]*G
        Wp=d["ml"]*G
        vcg=sx(d["xCG"])
        bcg=sx(xboom)
        self.A(p,QPointF(vcg,deck-90),QPointF(vcg,deck-8),"#2459b3",f"W_vehicle = {Wv:.0f} N")
        self.A(p,QPointF(bcg,top-70),QPointF(bcg,top-8),"#2459b3",f"W_boom = {Wb:.0f} N")
        self.A(p,QPointF(tip,top-88),QPointF(tip,top+18),"#d62828",f"W_payload = {Wp:.0f} N")

        self.D(p,QPointF(rear,gy+76),QPointF(front,gy+76),f"Wheelbase WB = {d['WB']:.3f} m")

        bal=self.app.longitudinal_moment_balance(d,angle,("front" if front_case else "rear"))
        sf=bal["sf"]
        self.moment_mark(p,QPointF(pivot_x,gy-72),f"M_O={bal['mo']:.0f} N.m","#b42318")
        p.setPen(QPen(QColor("#176337"),2))
        p.drawText(18,hh-88,
                   f"M_R={bal['mr']:.1f} N.m    M_O={bal['mo']:.1f} N.m    "
                   f"SF_{case.lower()} = {'INF' if sf>=999 else f'{sf:.3f}'}")
        p.setPen(QPen(QColor("#52606d")))
        p.drawText(18,hh-60,f"Crane angle={angle:.0f} deg   x_CG={d['xCG']:.3f} m   x_boom={xboom:.3f} m   x_load={xload:.3f} m")
        p.drawText(18,hh-36,"Payload uses Kdyn only when it lies on the overturning side of the selected pivot.")

    def _slope_view(self,p,d):
        self.title(
            p,
            "FREE BODY DIAGRAM - DRIVING ON SLOPE",
            "Weight decomposition and uphill acceleration effect at the combined vehicle CG"
        )
        ww,hh=self.width(),self.height()
        alpha=math.radians(self.app.slope.value())
        x0,y0=90,hh*.78
        run=ww*.68
        x1=x0+run
        y1=y0-run*math.tan(alpha)
        p.setPen(QPen(QColor("#64748b"),5))
        p.drawLine(QPointF(x0,y0),QPointF(x1,y1))
        cx,cy=(x0+x1)/2,(y0+y1)/2-55
        u=QPointF(math.cos(alpha),-math.sin(alpha))
        n=QPointF(-math.sin(alpha),-math.cos(alpha))

        pts=QPolygonF([
            QPointF(cx,cy)+u*(-105)+n*(-30),
            QPointF(cx,cy)+u*(105)+n*(-30),
            QPointF(cx,cy)+u*(105)+n*(30),
            QPointF(cx,cy)+u*(-105)+n*(30)
        ])
        p.setBrush(QColor("#e5e9ee"))
        p.setPen(QPen(QColor("#334155"),2))
        p.drawPolygon(pts)
        p.setBrush(QColor("#111827"))
        p.drawEllipse(QPointF(cx,cy),6,6)
        p.setPen(QPen(QColor("#111827")))
        p.drawText(QPointF(cx+10,cy-8),"CG")

        mass=d["mt"]
        W=mass*G
        Wpar=W*math.sin(alpha)
        Wnorm=W*math.cos(alpha)
        Fa=mass*self.app.acc.value()
        self.A(p,QPointF(cx,cy-95),QPointF(cx,cy+105),"#d62828",f"W=mg = {W:.0f} N")
        self.A(p,QPointF(cx,cy),QPointF(cx,cy)+u*(-145),"#b42318",f"mg sin(alpha) = {Wpar:.0f} N")
        self.A(p,QPointF(cx,cy),QPointF(cx,cy)+n*(115),"#2459b3",f"mg cos(alpha) = {Wnorm:.0f} N")
        self.A(p,QPointF(cx,cy)+n*(-28),QPointF(cx,cy)+n*(-135),"#16803a","N (ground reaction)")
        self.A(p,QPointF(cx,cy)+QPointF(0,16),QPointF(cx,cy)+u*(-105)+QPointF(0,16),"#8a3ffc",f"F_a = ma = {Fa:.0f} N")

        sr=self.app.slope_stability_results(d)
        MR=mass*G*math.cos(alpha)*max(0.0,sr["rear_arm"])
        MO=mass*max(0.0,sr["h"])*(G*math.sin(alpha)+max(0.0,sr["acc"]))
        self.pivot(p,QPointF(x0+run*.18,y0-run*.18*math.tan(alpha)),"Rear tipping pivot")
        p.setPen(QPen(QColor("#176337"),2))
        sf_text="INF" if sr["sf"]>=999 else f"{sr['sf']:.3f}"
        p.drawText(18,hh-66,
                   f"M_R={MR:.1f} N.m    M_O={MO:.1f} N.m    SF_slope={sf_text}    alpha={self.app.slope.value():.2f} deg")
        p.setPen(QPen(QColor("#52606d")))
        p.drawText(18,hh-38,
                   f"h_CG={sr['h']:.3f} m   rear arm={sr['rear_arm']:.3f} m. Use mg sin(alpha) for grade force; F_a=ma adds tipping effect.")

    def paintEvent(self,e):
        p=QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        p.fillRect(self.rect(),QColor("#ffffff"))
        if not hasattr(self.app,"mt"):
            return
        d=self.app.inputs()
        if self.simpleMode:
            if self.mode==0:
                self._simple_side_view(p,d,True)
            elif self.mode==1:
                self._simple_side_view(p,d,False)
            elif self.mode==2:
                self._simple_long_view(p,d,True)
            elif self.mode==3:
                self._simple_long_view(p,d,False)
            else:
                self._simple_slope_view(p,d)
        else:
            if self.mode==0:
                self._side_view(p,d,True)
            elif self.mode==1:
                self._side_view(p,d,False)
            elif self.mode==2:
                self._long_view(p,d,True)
            elif self.mode==3:
                self._long_view(p,d,False)
            else:
                self._slope_view(p,d)

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

















































