"""Scène 3D interactive (fichier HTML autonome, sans dépendance, sans réseau).

Les coordonnées exactes sont converties en flottants UNIQUEMENT ici, pour
l'affichage. Souris : glisser = tourner, molette = zoom. Repère : z vers le haut.
"""
from __future__ import annotations

import json
import math

import sympy as sp

from .core import _v, Line, Plane, Sphere, cross, norm, dot

PALETTE = ["#2563eb", "#dc2626", "#059669", "#d97706", "#7c3aed", "#0891b2", "#be185d"]


def _f(p):
    return [float(sp.N(c, 15)) for c in _v(p)]


class Scene:
    def __init__(self, title="Scène 3D", axes=True):
        self.title, self.axes = title, axes
        self.points, self.segments, self.polygons = [], [], []
        self.vectors, self.spheres, self.polylines = [], [], []
        self._i = 0

    def _color(self, color):
        if color:
            return color
        c = PALETTE[self._i % len(PALETTE)]
        self._i += 1
        return c

    # -- éléments -----------------------------------------------------------
    def add_point(self, name, P, color="#111827"):
        self.points.append({"name": name, "p": _f(P), "color": color})

    def add_segment(self, A, B, color="#374151", dashed=False, label=None, thick=False):
        self.segments.append({"a": _f(A), "b": _f(B), "color": color,
                              "dashed": dashed, "label": label, "thick": thick})

    def add_polygon(self, *points, color=None, alpha=0.18, label=None):
        self.polygons.append({"pts": [_f(p) for p in points], "color": self._color(color),
                              "alpha": alpha, "label": label})

    def add_vector(self, A, B, color=None, label=None):
        self.vectors.append({"a": _f(A), "b": _f(B), "color": self._color(color), "label": label})

    def add_line(self, L: Line, extent=3, color=None, label=None):
        """Droite dessinée sur t in [-extent, extent] (u normalisé)."""
        c = self._color(color)
        u = L.u / norm(L.u)
        self.segments.append({"a": _f(L.A - extent * u), "b": _f(L.A + extent * u),
                              "color": c, "dashed": False, "label": label, "thick": True})

    def add_plane(self, plane: Plane, around=None, size=2, color=None, alpha=0.16, label=None):
        """Carré de côté 2*size dans le plan, centré sur la projection de `around`
        (par défaut le point de définition du plan)."""
        c = plane.project(around) if around is not None else plane.A
        n = plane.n
        ref = _v([1, 0, 0]) if abs(float(n[0])) < 0.9 * float(norm(n)) else _v([0, 1, 0])
        e1 = cross(n, ref); e1 = e1 / norm(e1)
        e2 = cross(n, e1); e2 = e2 / norm(e2)
        s = sp.nsimplify(size)
        pts = [c + s * (a * e1 + b * e2) for a, b in ((-1, -1), (1, -1), (1, 1), (-1, 1))]
        self.add_polygon(*pts, color=color, alpha=alpha, label=label)

    def add_sphere(self, S: Sphere, color=None, label=None):
        self.spheres.append({"c": _f(S.c), "r": float(sp.N(S.r)), "color": self._color(color),
                             "label": label})

    def add_circle(self, center, normal, radius, color=None, label=None, n=96):
        """Cercle de centre/normale/rayon donnés (ex. section sphère ∩ plan)."""
        col = self._color(color)
        nrm = _v(normal)
        ref = _v([1, 0, 0]) if abs(float(nrm[0])) < 0.9 * float(norm(nrm)) else _v([0, 1, 0])
        e1 = cross(nrm, ref); e1 = e1 / norm(e1)
        e2 = cross(nrm, e1); e2 = e2 / norm(e2)
        c, r = _f(center), float(sp.N(radius))
        f1, f2 = _f(e1), _f(e2)
        pts = [[c[k] + r * (math.cos(2 * math.pi * i / n) * f1[k] + math.sin(2 * math.pi * i / n) * f2[k])
                for k in range(3)] for i in range(n + 1)]
        self.polylines.append({"pts": pts, "color": col, "label": label})

    def add_solid(self, solid, labels=True, face_alpha=0.07):
        """Sommets (avec noms), arêtes et faces d'un Solid."""
        for name, P in solid.v.items():
            self.add_point(name, P)
        for e in solid.edges:
            self.add_segment(solid.v[e[0]], solid.v[e[1]])
        for f in solid.faces:
            self.add_polygon(*[solid.v[ch] for ch in f], color="#64748b", alpha=face_alpha)

    # -- sortie -------------------------------------------------------------
    def data(self):
        return {"title": self.title, "axes": self.axes, "points": self.points,
                "segments": self.segments, "polygons": self.polygons, "vectors": self.vectors,
                "spheres": self.spheres, "polylines": self.polylines}

    def save(self, path):
        html = _TEMPLATE.replace("__TITLE__", self.title).replace(
            "__DATA__", json.dumps(self.data()).replace("</", "<\\/"))
        with open(path, "w", encoding="utf-8") as fh:
            fh.write(html)
        return path


_TEMPLATE = r"""<!doctype html>
<html lang="fr"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>__TITLE__</title>
<style>
:root{--bg:#f8fafc;--fg:#0f172a;--mut:#64748b;--card:#fff;--bd:#e2e8f0}
@media (prefers-color-scheme:dark){:root{--bg:#0b1220;--fg:#e5e7eb;--mut:#94a3b8;--card:#111827;--bd:#1f2937}}
html,body{margin:0;height:100%;background:var(--bg);color:var(--fg);font:14px system-ui,sans-serif}
#wrap{display:flex;flex-direction:column;height:100%}
header{padding:10px 16px;display:flex;gap:12px;align-items:center;flex-wrap:wrap;border-bottom:1px solid var(--bd)}
h1{font-size:15px;margin:0;font-weight:600}
button{background:var(--card);color:var(--fg);border:1px solid var(--bd);border-radius:6px;padding:4px 10px;cursor:pointer}
#legend{display:flex;gap:12px;flex-wrap:wrap;color:var(--mut);font-size:12px}
#legend i{display:inline-block;width:10px;height:10px;border-radius:2px;margin-right:4px;vertical-align:-1px}
canvas{flex:1;width:100%;touch-action:none;cursor:grab}
</style></head><body><div id="wrap">
<header><h1>__TITLE__</h1><button id="reset">Réinitialiser</button><button id="top">Dessus</button>
<button id="front">Face</button><span id="legend"></span></header>
<canvas id="c"></canvas></div>
<script>
const D=__DATA__;
const cv=document.getElementById('c'),ctx=cv.getContext('2d');
const css=n=>getComputedStyle(document.documentElement).getPropertyValue(n).trim();
// centre et rayon de la scène
let all=[];D.points.forEach(p=>all.push(p.p));D.segments.forEach(s=>{all.push(s.a,s.b)});
D.polygons.forEach(g=>g.pts.forEach(p=>all.push(p)));D.vectors.forEach(v=>all.push(v.a,v.b));
D.polylines.forEach(l=>l.pts.forEach(p=>all.push(p)));
D.spheres.forEach(s=>{for(const k of [0,1,2]){let a=[...s.c],b=[...s.c];a[k]-=s.r;b[k]+=s.r;all.push(a,b)}});
if(!all.length)all=[[0,0,0]];
const lo=[0,1,2].map(k=>Math.min(...all.map(p=>p[k]))),hi=[0,1,2].map(k=>Math.max(...all.map(p=>p[k])));
const C=lo.map((l,k)=>(l+hi[k])/2);
const R=Math.max(1e-6,...all.map(p=>Math.hypot(p[0]-C[0],p[1]-C[1],p[2]-C[2])));
const V0={yaw:-0.7,pitch:0.45,zoom:1};let V={...V0};
function proj(p){let x=p[0]-C[0],y=p[1]-C[1],z=p[2]-C[2];
 const c=Math.cos(V.yaw),s=Math.sin(V.yaw);const x1=c*x-s*y,y1=s*x+c*y;
 const cp=Math.cos(V.pitch),sp=Math.sin(V.pitch);
 const up=z*cp+y1*sp,dep=y1*cp-z*sp;const Dd=4*R,f=Dd/(Dd+dep);
 const S=Math.min(W,H)/(2.5*R)*V.zoom;return [W/2+x1*f*S,H/2-up*f*S,dep,f*S]}
let W=0,H=0;
function resize(){const r=cv.getBoundingClientRect(),d=devicePixelRatio||1;
 cv.width=r.width*d;cv.height=r.height*d;ctx.setTransform(d,0,0,d,0,0);W=r.width;H=r.height;draw()}
function hexA(h,a){const n=parseInt(h.slice(1),16);return `rgba(${n>>16},${(n>>8)&255},${n&255},${a})`}
function line(a,b,col,w,dash){const A=proj(a),B=proj(b);ctx.beginPath();ctx.moveTo(A[0],A[1]);ctx.lineTo(B[0],B[1]);
 ctx.strokeStyle=col;ctx.lineWidth=w;ctx.setLineDash(dash?[6,5]:[]);ctx.stroke();ctx.setLineDash([])}
function text(t,p,col,off=[6,-6]){const P=proj(p);ctx.fillStyle=col;ctx.font='600 13px system-ui';ctx.fillText(t,P[0]+off[0],P[1]+off[1])}
function draw(){ctx.clearRect(0,0,W,H);const fg=css('--fg');
 if(D.axes){const L=R*1.1,o=[0,0,0];[['x',[L,0,0],'#ef4444'],['y',[0,L,0],'#22c55e'],['z',[0,0,L],'#3b82f6']].forEach(([n,e,c])=>{
  line(o,e,hexA(c,.55),1,true);text(n,e,c)})}
 const polys=D.polygons.map(g=>({g,d:g.pts.reduce((s,p)=>s+proj(p)[2],0)/g.pts.length})).sort((a,b)=>b.d-a.d);
 polys.forEach(({g})=>{ctx.beginPath();g.pts.forEach((p,i)=>{const P=proj(p);i?ctx.lineTo(P[0],P[1]):ctx.moveTo(P[0],P[1])});
  ctx.closePath();ctx.fillStyle=hexA(g.color,g.alpha);ctx.fill();ctx.strokeStyle=hexA(g.color,.55);ctx.lineWidth=1;ctx.stroke()});
 D.spheres.forEach(s=>{const P=proj(s.c);ctx.beginPath();ctx.arc(P[0],P[1],s.r*P[3],0,7);
  ctx.fillStyle=hexA(s.color,.07);ctx.fill();ctx.strokeStyle=hexA(s.color,.8);ctx.lineWidth=1.5;ctx.stroke();
  for(const k of [0,1,2]){ctx.beginPath();for(let i=0;i<=72;i++){const t=i/72*6.2832,q=[...s.c];
   const a=(k+1)%3,b=(k+2)%3;q[a]+=s.r*Math.cos(t);q[b]+=s.r*Math.sin(t);const Q=proj(q);i?ctx.lineTo(Q[0],Q[1]):ctx.moveTo(Q[0],Q[1])}
   ctx.strokeStyle=hexA(s.color,.3);ctx.lineWidth=1;ctx.stroke()}});
 D.polylines.forEach(l=>{ctx.beginPath();l.pts.forEach((p,i)=>{const P=proj(p);i?ctx.lineTo(P[0],P[1]):ctx.moveTo(P[0],P[1])});
  ctx.strokeStyle=l.color;ctx.lineWidth=2.5;ctx.stroke()});
 D.segments.forEach(s=>line(s.a,s.b,s.color==='#374151'?fg:s.color,s.thick?2.5:1.6,s.dashed));
 D.vectors.forEach(v=>{line(v.a,v.b,v.color,2.2);const A=proj(v.a),B=proj(v.b),a=Math.atan2(B[1]-A[1],B[0]-A[0]);
  ctx.beginPath();ctx.moveTo(B[0],B[1]);ctx.lineTo(B[0]-10*Math.cos(a-.4),B[1]-10*Math.sin(a-.4));
  ctx.lineTo(B[0]-10*Math.cos(a+.4),B[1]-10*Math.sin(a+.4));ctx.closePath();ctx.fillStyle=v.color;ctx.fill();
  if(v.label)text(v.label,v.b,v.color)});
 D.points.forEach(p=>{const P=proj(p.p);ctx.beginPath();ctx.arc(P[0],P[1],3.5,0,7);ctx.fillStyle=p.color==='#111827'?fg:p.color;ctx.fill();
  if(p.name)text(p.name,p.p,p.color==='#111827'?fg:p.color)})}
// légende
const lg=document.getElementById('legend');const items=[];
[...D.polygons,...D.segments,...D.vectors,...D.spheres,...D.polylines].forEach(o=>{if(o.label)items.push(o)});
lg.innerHTML=items.map(o=>`<span><i style="background:${o.color}"></i>${o.label}</span>`).join('');
// interaction
let drag=null;
cv.addEventListener('pointerdown',e=>{drag=[e.clientX,e.clientY];cv.setPointerCapture(e.pointerId);cv.style.cursor='grabbing'});
cv.addEventListener('pointerup',()=>{drag=null;cv.style.cursor='grab'});
cv.addEventListener('pointermove',e=>{if(!drag)return;V.yaw+=(e.clientX-drag[0])*0.008;
 V.pitch=Math.max(-1.55,Math.min(1.55,V.pitch+(e.clientY-drag[1])*0.008));drag=[e.clientX,e.clientY];draw()});
cv.addEventListener('wheel',e=>{e.preventDefault();V.zoom=Math.max(.2,Math.min(8,V.zoom*Math.exp(-e.deltaY*0.001)));draw()},{passive:false});
document.getElementById('reset').onclick=()=>{V={...V0};draw()};
document.getElementById('top').onclick=()=>{V={yaw:0,pitch:1.5707,zoom:1};draw()};
document.getElementById('front').onclick=()=>{V={yaw:0,pitch:0,zoom:1};draw()};
addEventListener('resize',resize);resize();
</script></body></html>
"""
