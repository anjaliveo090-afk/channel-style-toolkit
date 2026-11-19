// TOBY, 3D: "This noob is the reason Roblox has a leave button", rebuilt as a toy-world 3D film.
// Timing comes from timeline.json (the voice's sentence times, same beats as the 2D version), so every
// picture lands on its word and the 2D mix (voice + music + SFX) lines up.
// RULE: every frame is a pure function of t. Nothing is carried over between frames.
// All characters, worlds and UI are original generic designs (no real game's logo, avatar or interface).
import * as THREE from 'three';
import { FullScreenQuad } from 'three/addons/postprocessing/Pass.js';
import { UnrealBloomPass } from 'three/addons/postprocessing/UnrealBloomPass.js';
import { RoundedBoxGeometry } from 'three/addons/geometries/RoundedBoxGeometry.js';
import { W, H, clamp, lerp, seg, smooth, easeOut, easeInOut, backOut, spring, halton, hash } from './lib.js';

// ---------------------------------------------------------------- timeline + fonts (loaded before __ready)
const TL = await (await fetch('./timeline.json')).json();
for (const [fam, file, wt] of [['Caveat Brush', 'CaveatBrush-Regular.ttf', '400'], ['Kalam', 'Kalam-Bold.ttf', '700'], ['Kalam', 'Kalam-Regular.ttf', '400']]) {
  const f = new FontFace(fam, `url(./fonts/${file})`, { weight: wt }); await f.load(); document.fonts.add(f);
}
export const total = TL.total;
const B = TL.beats;
// time a word is said inside beat i (same rule as the 2D engine: proportional to its position in the sentence)
function wt(i, word) {
  const w = word.toLowerCase();
  for (const s of B[i].sents) { const k = s.text.toLowerCase().indexOf(w); if (k >= 0) return s.start + (s.end - s.start) * k / Math.max(1, s.text.length); }
  return 1e9;
}
const talking = (i, who, t) => B[i].sents.some((s) => s.speaker === who && s.start <= t && t <= s.end);
const SHUTTER = 0.5 / 24;
const V = (x, y, z) => new THREE.Vector3(x, y, z);
const C = (h) => new THREE.Color(h);

// ---------------------------------------------------------------- renderer
const stage = document.getElementById('stage');
const renderer = new THREE.WebGLRenderer({ canvas: stage, antialias: false, preserveDrawingBuffer: true, powerPreference: 'high-performance' });
renderer.setPixelRatio(1); renderer.setSize(W, H, false);
renderer.toneMapping = THREE.NoToneMapping; renderer.outputColorSpace = THREE.LinearSRGBColorSpace;
renderer.shadowMap.enabled = true; renderer.shadowMap.type = THREE.PCFShadowMap;
const rt = new THREE.WebGLRenderTarget(W, H, { type: THREE.HalfFloatType, samples: 4 });
const accum = new THREE.WebGLRenderTarget(W, H, { type: THREE.HalfFloatType, depthBuffer: false });
const scene = new THREE.Scene();

// ---------------------------------------------------------------- materials + small builders
const mats = new Map();
const mat = (hex, rough = 0.55, extra = {}) => {
  const key = hex + rough + JSON.stringify(extra);
  if (!mats.has(key)) mats.set(key, new THREE.MeshStandardMaterial({ color: C(hex), roughness: rough, metalness: 0, ...extra }));
  return mats.get(key);
};
const glowMat = (r, g, b) => new THREE.MeshBasicMaterial({ color: new THREE.Color(r, g, b) });
function mesh(geo, material, x = 0, y = 0, z = 0, parent = null, shadow = true) {
  const m = new THREE.Mesh(geo, material); m.position.set(x, y, z); m.castShadow = shadow; m.receiveShadow = true;
  if (parent) parent.add(m); return m;
}
const rbox = (w, h, d, r = 0.06) => new RoundedBoxGeometry(w, h, d, 3, Math.min(r, w / 2.01, h / 2.01, d / 2.01));
function canvasTex(w, h, draw) {
  const cv = Object.assign(document.createElement('canvas'), { width: w, height: h }); const g = cv.getContext('2d'); draw(g, w, h);
  const tx = new THREE.CanvasTexture(cv); tx.colorSpace = THREE.SRGBColorSpace; tx.anisotropy = 8; return tx;
}
function textPlane(w, h, px, draw, glow = 1.0) {
  const tx = canvasTex(px, Math.round(px * h / w), draw);
  const m = new THREE.Mesh(new THREE.PlaneGeometry(w, h), new THREE.MeshBasicMaterial({ map: tx, transparent: true, color: new THREE.Color(glow, glow, glow) }));
  return m;
}
const COLS = ['#e5483c', '#3b82d6', '#f2c230', '#4cb050', '#9b59d0', '#f28b2c', '#ff7ab8'];

// sky: a big inward sphere with a vertical gradient + soft sun
const skyTex = canvasTex(16, 512, (g, w, h) => { const gr = g.createLinearGradient(0, 0, 0, h); gr.addColorStop(0, '#3f8fe0'); gr.addColorStop(0.45, '#8cc8f2'); gr.addColorStop(0.55, '#dff2ff'); gr.addColorStop(1, '#dff2ff'); g.fillStyle = gr; g.fillRect(0, 0, w, h); });
const sky = new THREE.Mesh(new THREE.SphereGeometry(400, 32, 16), new THREE.MeshBasicMaterial({ map: skyTex, side: THREE.BackSide, color: new THREE.Color(1.05, 1.05, 1.05), fog: false }));
scene.add(sky);
function cloud(x, y, z, s, parent) {
  const g = new THREE.Group(); g.position.set(x, y, z); g.scale.setScalar(s); parent.add(g);
  for (const [dx, dy, r] of [[-1.4, 0, 1.1], [-0.3, 0.5, 1.5], [1.0, 0.2, 1.3], [2.0, -0.1, 0.9]]) mesh(new THREE.SphereGeometry(r, 16, 12), mat('#ffffff', 0.9), dx, dy, 0, g, false).scale.y = 0.75;
  return g;
}

// ---------------------------------------------------------------- toy figures
const FACE_W = 256, FACE_H = 200;
const faceCache = new Map();
function faceTex(expr, open, blush) {
  const key = expr + open + blush;
  if (faceCache.has(key)) return faceCache.get(key);
  const tx = canvasTex(FACE_W, FACE_H, (g) => {
    g.lineCap = 'round'; g.lineJoin = 'round';
    const eye = (x, y, sx = 1, sy = 1) => { g.fillStyle = '#2a1608'; g.beginPath(); g.ellipse(x, y, 13 * sx, 21 * sy, 0, 0, 7); g.fill(); g.fillStyle = '#fff'; g.beginPath(); g.arc(x - 4, y - 8, 5, 0, 7); g.fill(); };
    const brow = (x, y, a) => { g.strokeStyle = '#2a1608'; g.lineWidth = 7; g.beginPath(); g.moveTo(x - 22, y + a); g.lineTo(x + 22, y - a); g.stroke(); };
    const ex = 128, ey = 82;
    if (expr === 'laugh' || expr === 'happyClosed') {
      g.strokeStyle = '#2a1608'; g.lineWidth = 9; for (const sd of [-1, 1]) { g.beginPath(); g.arc(ex + sd * 48, ey + 8, 16, Math.PI * 1.1, Math.PI * 1.9); g.stroke(); }
    } else if (expr === 'shock') { eye(ex - 48, ey, 1.25, 1.25); eye(ex + 48, ey, 1.25, 1.25); brow(ex - 48, ey - 40, 0); brow(ex + 48, ey - 40, 0); }
    else { eye(ex - 48, ey); eye(ex + 48, ey); }
    if (expr === 'angry') { brow(ex - 48, ey - 32, -8); brow(ex + 48, ey - 32, 8); }
    if (expr === 'sad' || expr === 'worried') { brow(ex - 48, ey - 34, 7); brow(ex + 48, ey - 34, -7); }
    if (expr === 'neutral' || expr === 'happy' || expr === 'smirk') { brow(ex - 48, ey - 36, 2); brow(ex + 48, ey - 36, -2); }
    if (blush) { g.fillStyle = 'rgba(240,90,90,0.45)'; for (const sd of [-1, 1]) { g.beginPath(); g.ellipse(ex + sd * 74, ey + 40, 20, 11, 0, 0, 7); g.fill(); } }
    g.strokeStyle = '#2a1608'; g.lineWidth = 8; g.fillStyle = '#7a1e1e';
    const my = 150;
    if (open || expr === 'laugh' || expr === 'shock') {
      const h = expr === 'shock' ? 26 : open ? 20 : 24;
      g.beginPath(); g.ellipse(ex, my - 4, expr === 'shock' ? 20 : 30, h, 0, 0, 7); g.fill(); g.stroke();
      if (expr === 'laugh') { g.fillStyle = '#ff8a8a'; g.beginPath(); g.ellipse(ex, my + 8, 16, 8, 0, 0, 7); g.fill(); }
    } else if (expr === 'happy' || expr === 'happyClosed') { g.beginPath(); g.arc(ex, my - 26, 34, 0.3, Math.PI - 0.3); g.stroke(); }
    else if (expr === 'smirk') { g.beginPath(); g.moveTo(ex - 26, my - 2); g.quadraticCurveTo(ex + 6, my + 8, ex + 30, my - 12); g.stroke(); }
    else if (expr === 'sad' || expr === 'worried') { g.beginPath(); g.arc(ex, my + 24, 26, Math.PI + 0.5, -0.5); g.stroke(); }
    else if (expr === 'angry') { g.beginPath(); g.moveTo(ex - 26, my + 4); g.lineTo(ex + 26, my - 2); g.stroke(); }
    else { g.beginPath(); g.moveTo(ex - 18, my); g.lineTo(ex + 18, my); g.stroke(); }
  });
  faceCache.set(key, tx); return tx;
}

const SKIN = '#f6c48a';
function figure({ shirt, pants = '#2a2f3a', hair = '#2a1a10', hairStyle = 'cap', hat = false, shades = false, badge = null, blush = false, tie = null }) {
  const root = new THREE.Group(); scene.add(root);
  const body = new THREE.Group(); root.add(body);                       // everything above the feet (bob / lean)
  const legs = [];
  for (const sd of [-1, 1]) {
    const hip = new THREE.Group(); hip.position.set(sd * 0.15, 0.66, 0); body.add(hip);
    mesh(rbox(0.26, 0.64, 0.3, 0.05), mat(pants, 0.6), 0, -0.32, 0, hip);
    mesh(rbox(0.28, 0.12, 0.36, 0.04), mat('#2a2220', 0.5), 0, -0.6, 0.03, hip);
    legs.push(hip);
  }
  const torso = mesh(rbox(0.66, 0.74, 0.4, 0.09), mat(shirt, 0.55), 0, 1.02, 0, body);
  if (tie) mesh(rbox(0.1, 0.42, 0.02, 0.01), mat(tie), 0, 1.12, 0.205, body);
  if (badge) { const bd = mesh(new THREE.CylinderGeometry(0.07, 0.07, 0.03, 20), mat(badge, 0.3, { metalness: 0.6 }), 0.17, 1.22, 0.21, body); bd.rotation.x = Math.PI / 2; }
  const arms = [];
  for (const sd of [-1, 1]) {
    const sh = new THREE.Group(); sh.position.set(sd * 0.43, 1.32, 0); body.add(sh);
    mesh(rbox(0.2, 0.62, 0.24, 0.07), mat(shirt, 0.55), 0, -0.28, 0, sh);
    mesh(new THREE.SphereGeometry(0.1, 16, 12), mat(SKIN, 0.5), 0, -0.62, 0, sh);
    const hand = new THREE.Group(); hand.position.set(0, -0.66, 0); sh.add(hand);
    arms.push({ sh, hand, sd });
  }
  const head = new THREE.Group(); head.position.set(0, 1.72, 0); body.add(head);
  mesh(rbox(0.66, 0.6, 0.58, 0.16), mat(SKIN, 0.5), 0, 0, 0, head);
  const face = new THREE.Mesh(new THREE.PlaneGeometry(0.56, 0.44), new THREE.MeshStandardMaterial({ map: faceTex('neutral', false, blush), transparent: true, roughness: 0.6 }));
  face.position.set(0, -0.02, 0.292); head.add(face);
  if (hairStyle === 'cap') { mesh(rbox(0.7, 0.2, 0.62, 0.08), mat(hair, 0.7), 0, 0.27, -0.01, head); mesh(rbox(0.7, 0.42, 0.18, 0.06), mat(hair, 0.7), 0, 0.08, -0.23, head); }
  if (hairStyle === 'bun') { mesh(rbox(0.7, 0.2, 0.62, 0.08), mat(hair, 0.7), 0, 0.27, -0.01, head); mesh(new THREE.SphereGeometry(0.17, 16, 12), mat(hair, 0.7), 0, 0.42, -0.12, head); }
  if (hairStyle === 'spiky') for (let i = 0; i < 5; i++) { const s = mesh(new THREE.ConeGeometry(0.1, 0.26, 4), mat(hair, 0.7), -0.24 + i * 0.12, 0.38, -0.02, head); s.rotation.z = (i - 2) * 0.18; }
  if (hairStyle === 'long') { mesh(rbox(0.72, 0.2, 0.64, 0.08), mat(hair, 0.7), 0, 0.27, -0.01, head); mesh(rbox(0.74, 0.7, 0.2, 0.06), mat(hair, 0.7), 0, -0.05, -0.24, head); }
  if (hairStyle === 'grey') mesh(rbox(0.7, 0.14, 0.62, 0.06), mat(hair, 0.7), 0, 0.27, -0.01, head);
  if (shades) { mesh(rbox(0.5, 0.11, 0.04, 0.02), mat('#111', 0.2), 0, 0.05, 0.31, head); }
  if (hat) {
    const hatTex = canvasTex(256, 256, (g) => { g.fillStyle = '#3b82d6'; g.fillRect(0, 0, 256, 256); g.fillStyle = '#f2c230'; for (let i = 0; i < 4; i++) g.fillRect(0, 40 + i * 60, 256, 22); });
    const cone = mesh(new THREE.ConeGeometry(0.24, 0.62, 32), new THREE.MeshStandardMaterial({ map: hatTex, roughness: 0.5 }), 0.06, 0.62, 0, head);
    cone.rotation.z = -0.18;
    mesh(new THREE.SphereGeometry(0.08, 16, 12), mat('#e5483c', 0.5), 0.12, 0.94, 0, head);
  }
  return { root, body, legs, arms, head, face, blush };
}

const FIG = {
  TOBY: figure({ shirt: '#f28b2c', pants: '#2a5fa8', hair: '#6a3a1a', hat: true, blush: true }),
  P1: figure({ shirt: '#3b82d6', hair: '#1d1716', hairStyle: 'spiky' }),
  P2: figure({ shirt: '#9b59d0', hair: '#e0a23a', hairStyle: 'long' }),
  P3: figure({ shirt: '#4cb050', hair: '#3a2a20', hairStyle: 'cap' }),
  P4: figure({ shirt: '#e5483c', hair: '#1d1716', hairStyle: 'bun' }),
  MOD: figure({ shirt: '#26303f', hair: '#1d1716', shades: true, badge: '#f2c230' }),
  ADMIN: figure({ shirt: '#c8312c', pants: '#1b1b22', hair: '#d8d2c8', hairStyle: 'grey', badge: '#f2c230', tie: '#1b1b22' }),
  DEV1: figure({ shirt: '#3a3a42', hair: '#1d1716', hairStyle: 'cap' }),
  DEV2: figure({ shirt: '#2f7a4f', hair: '#6e2a18', hairStyle: 'bun' }),
};
const SPEAKER = { TOBY: 'TOBY' };

// arm presets: [shoulder z (outward raise), shoulder x (forward)] for the screen-left (-1) and screen-right (+1) arm
const ARMS = {
  rest: [[0.08, 0], [0.08, 0]], cheer: [[2.6, 0], [2.6, 0]], wave: [[0.1, 0], [2.6, 0]], raiseR: [[0.1, 0], [2.5, 0]],
  hold: [[0.2, -1.1], [0.2, -1.1]], presentL: [[1.0, -0.9], [0.1, 0]], presentR: [[0.1, 0], [1.0, -0.9]],
  pointR: [[0.1, 0], [1.55, -0.2]], hips: [[0.55, 0], [0.55, 0]], chin: [[0.1, 0], [0.4, -2.3]], beg: [[0.3, -1.6], [0.3, -1.6]],
};
// pose one figure at time t. o: {x, z, rot, walk (phase or null), arms, expr, talk, bob, lean, visible, y, look}
function pose(f, t, o) {
  f.root.visible = o.visible !== false;
  if (!f.root.visible) return;
  f.root.position.set(o.x || 0, o.y || 0, o.z || 0);
  f.root.rotation.set(0, o.rot || 0, 0);
  const walk = o.walk ?? null;
  const breathe = 0.012 * Math.sin(t * 2.3 + (o.x || 0));
  f.body.position.y = (walk !== null ? Math.abs(Math.sin(walk)) * 0.06 : 0) + breathe + (o.bob || 0);
  f.body.rotation.z = o.lean || 0;
  f.legs.forEach((l, i) => { l.rotation.x = walk !== null ? Math.sin(walk + i * Math.PI) * 0.6 : 0; });
  const A = typeof o.arms === 'string' || !o.arms ? ARMS[o.arms || 'rest'] : o.arms;
  f.arms.forEach((a, i) => {
    const [z, x] = A[i];
    const wob = o.arms === 'wave' && i === 1 ? 0.25 * Math.sin(t * 9) : walk !== null && (o.arms || 'rest') === 'rest' ? 0.4 * Math.sin(walk + i * Math.PI) : 0;
    a.sh.rotation.set(x + (o.arms === 'rest' || !o.arms ? wob : 0), 0, a.sd * (z + (o.arms === 'wave' ? wob : 0)));
  });
  f.head.rotation.set(0, (o.look || 0) * 0.5, 0);
  const open = o.talk && Math.floor(t * 9) % 2 === 0;
  f.face.material.map = faceTex(o.expr || 'neutral', open, f.blush);
}

// ---------------------------------------------------------------- props
function balloonBunch(n, seed, parent) {
  const g = new THREE.Group(); parent.add(g); const items = [];
  for (let i = 0; i < n; i++) {
    const col = COLS[(i + seed) % COLS.length];
    const top = V((hash(i + seed * 7) - 0.5) * 0.9, 1.3 + hash(i * 3 + seed) * 0.6, (hash(i * 5 + seed) - 0.5) * 0.5);
    const b = mesh(new THREE.SphereGeometry(0.2, 20, 14), mat(col, 0.25), 0, 0, 0, g); b.scale.set(1, 1.18, 1);
    const line = new THREE.Line(new THREE.BufferGeometry().setFromPoints([V(0, 0, 0), V(0, 0, 0)]), new THREE.LineBasicMaterial({ color: 0x333333 }));
    g.add(line); items.push({ b, line, top, i });
  }
  return { g, items };
}
// k = seconds since the bunch appeared (pop-in), sway from t
function poseBunch(bb, t, k, stagger = 0.05) {
  bb.g.visible = k > 0;
  for (const it of bb.items) {
    const s = clamp((k - it.i * stagger) / 0.15) > 0 ? (k - it.i * stagger < 0.15 ? 1.1 * easeOut((k - it.i * stagger) / 0.15) : 1 + 0.1 * Math.exp(-(k - it.i * stagger - 0.15) * 25)) : 0;
    const p = it.top.clone(); p.x += 0.08 * Math.sin(t * 2 + it.i); p.y *= Math.max(0.01, Math.min(1, s));
    it.b.position.copy(p); it.b.scale.set(s, s * 1.18, s); it.b.visible = s > 0.01;
    it.line.geometry.setFromPoints([V(0, 0, 0), V(p.x, p.y - 0.22 * s, p.z)]); it.line.visible = s > 0.01;
  }
}
function puff(parent) {
  const g = new THREE.Group(); parent.add(g); const ps = [];
  for (let i = 0; i < 10; i++) { const m = mesh(new THREE.SphereGeometry(0.3, 14, 10), new THREE.MeshStandardMaterial({ color: 0xffffff, roughness: 0.9, transparent: true }), 0, 0, 0, g, false); ps.push(m); }
  return { g, ps };
}
function posePuff(p, k, pos, r = 1.0, dur = 0.5) {
  p.g.visible = k >= 0 && k <= dur;
  if (!p.g.visible) return;
  p.g.position.copy(pos);
  const q = k / dur;
  p.ps.forEach((m, i) => {
    const a = i * 2 * Math.PI / 10 + 0.4, d = r * (0.3 + 0.9 * easeOut(q));
    m.position.set(Math.cos(a) * d, Math.sin(a) * d * 0.8 + 0.2 * q, (hash(i) - 0.5) * 0.4);
    m.scale.setScalar(r * (0.6 + 0.8 * Math.sin(Math.PI * Math.min(1, q * 1.3))) * (1 - q * 0.5));
    m.material.opacity = 1 - q * q;
  });
}
// confetti: one instanced mesh, burst from a point (k = s since the burst)
const CONF_N = 220;
const confetti = new THREE.InstancedMesh(new THREE.PlaneGeometry(0.09, 0.05), new THREE.MeshBasicMaterial({ side: THREE.DoubleSide }), CONF_N);
for (let i = 0; i < CONF_N; i++) confetti.setColorAt(i, C(COLS[i % COLS.length]).multiplyScalar(1.3));
scene.add(confetti);
const _m4 = new THREE.Matrix4(), _q = new THREE.Quaternion(), _e = new THREE.Euler(), _s = V(1, 1, 1), _p = V(0, 0, 0);
function poseConfetti(k, at) {
  confetti.visible = k > 0 && k < 3;
  if (!confetti.visible) return;
  for (let i = 0; i < CONF_N; i++) {
    const a = hash(i) * 6.28, el = 0.3 + hash(i + 50) * 1.1, v = 3 + hash(i + 9) * 4, kk = Math.min(k, 0.7);
    _p.set(at.x + Math.cos(a) * Math.cos(el) * v * kk, at.y + Math.sin(el) * v * kk - 1.6 * k * k, at.z + Math.sin(a) * Math.cos(el) * v * kk * 0.6);
    _e.set(k * 7 + i, k * 5 + i * 2, 0); _q.setFromEuler(_e); _m4.compose(_p, _q, _s); confetti.setMatrixAt(i, _m4);
  }
  confetti.instanceMatrix.needsUpdate = true;
}

// ---------------------------------------------------------------- SET: park (hide and seek), origin
const PARK = new THREE.Group(); scene.add(PARK);
mesh(new THREE.PlaneGeometry(200, 200), mat('#6cc04e', 0.95), 0, 0, 0, PARK).rotation.x = -Math.PI / 2;
function house(x, z, wall, roof, parent) {
  const g = new THREE.Group(); g.position.set(x, 0, z); parent.add(g);
  mesh(rbox(3, 2.4, 2.6, 0.05), mat(wall, 0.7), 0, 1.2, 0, g);
  const r = mesh(new THREE.ConeGeometry(2.4, 1.5, 4), mat(roof, 0.6), 0, 3.15, 0, g); r.rotation.y = Math.PI / 4; r.scale.z = 0.85;
  mesh(rbox(0.7, 1.3, 0.1, 0.03), mat('#7a4a2a'), 0, 0.65, 1.31, g);
  for (const dx of [-0.95, 0.95]) mesh(rbox(0.6, 0.55, 0.06, 0.02), new THREE.MeshStandardMaterial({ color: C('#bfe3ff'), emissive: C('#6aa8d8'), emissiveIntensity: 0.4 }), dx, 1.55, 1.31, g);
  return g;
}
house(-6.5, -6, '#f2c230', '#c8312c', PARK); house(6.8, -6.5, '#3b82d6', '#4a3a8a', PARK); house(14, -9, '#f6efe0', '#4cb050', PARK); house(-14, -9, '#ff9ab8', '#7a4a2a', PARK);
{ const tr = new THREE.Group(); tr.position.set(1.2, 0, -7.5); PARK.add(tr); mesh(new THREE.CylinderGeometry(0.25, 0.3, 2.6, 12), mat('#7a4a2a'), 0, 1.3, 0, tr);
  mesh(rbox(2.6, 1.2, 2.4, 0.2), mat('#3f9a4a', 0.8), 0, 2.9, 0, tr); mesh(rbox(1.8, 0.9, 1.8, 0.2), mat('#4cb050', 0.8), 0, 3.85, 0, tr); }
const HIDE = [V(-4.2, 0, -1.2), V(-1.3, 0, -1.8), V(1.6, 0, -1.4), V(4.4, 0, -1.6)];
function bush(p, s, parent) {
  const g = new THREE.Group(); g.position.copy(p); g.scale.setScalar(s); parent.add(g);
  for (const [dx, dy, dz, r] of [[-0.5, 0.45, 0, 0.55], [0.1, 0.65, 0.05, 0.7], [0.6, 0.45, 0, 0.55], [0, 0.35, 0.35, 0.55]]) mesh(new THREE.SphereGeometry(r, 18, 14), mat(dy > 0.5 ? '#3f9a4a' : '#358a3e', 0.85), dx, dy, dz, g);
  return g;
}
HIDE.forEach((p) => bush(p, 1.15, PARK));
for (const [x, z, s] of [[-8.5, 1, 1.2], [8.8, 0.5, 1.3], [-2.8, -4.4, 0.9], [3.2, -4.6, 0.9]]) bush(V(x, 0, z), s, PARK);
for (const [x, z] of [[-2.9, -0.6], [3.0, -0.4]]) mesh(rbox(0.7, 0.7, 0.7, 0.04), mat('#c08a4a', 0.7), x, 0.35, z, PARK);
const parkClouds = new THREE.Group(); PARK.add(parkClouds);
[[-20, 14, -60, 2], [5, 18, -70, 2.6], [28, 12, -55, 2], [-40, 20, -80, 3]].forEach(([x, y, z, s]) => cloud(x, y, z, s, parkClouds));
// the doorbell post (shots 27-28)
const BELL = new THREE.Group(); PARK.add(BELL); BELL.position.set(2.2, 0, 0.4);
mesh(new THREE.CylinderGeometry(0.07, 0.07, 1.6, 12), mat('#8a5a32'), 0, 0.8, 0, BELL);
mesh(rbox(1.0, 1.2, 0.16, 0.06), mat('#1a2030', 0.4), 0, 2.0, 0, BELL);
const bellBtn = mesh(new THREE.CylinderGeometry(0.26, 0.26, 0.12, 32), new THREE.MeshStandardMaterial({ color: C('#e0352b'), emissive: C('#ff3a2a'), emissiveIntensity: 0.6, roughness: 0.3 }), 0, 2.15, 0.1, BELL);
bellBtn.rotation.x = Math.PI / 2;
{ const lab = textPlane(0.9, 0.3, 256, (g, w, h) => { g.fillStyle = '#fff'; g.font = '700 46px Kalam'; g.textAlign = 'center'; g.fillText('LEAVE GAME', w / 2, h * 0.72); }, 1.3); lab.position.set(0, 1.62, 0.085); BELL.add(lab); }

// ---------------------------------------------------------------- SET: obby, x = 100
const OBBY = new THREE.Group(); OBBY.position.x = 100; scene.add(OBBY);
const lavaTex = canvasTex(256, 256, (g) => { g.fillStyle = '#ff7a1a'; g.fillRect(0, 0, 256, 256); for (let i = 0; i < 40; i++) { g.fillStyle = i % 2 ? 'rgba(255,220,80,0.5)' : 'rgba(200,40,10,0.45)'; g.beginPath(); g.ellipse(hash(i) * 256, hash(i + 9) * 256, 10 + hash(i + 3) * 30, 6 + hash(i + 4) * 14, 0, 0, 7); g.fill(); } });
lavaTex.wrapS = lavaTex.wrapT = THREE.RepeatWrapping; lavaTex.repeat.set(12, 12);
const lava = mesh(new THREE.PlaneGeometry(200, 200), new THREE.MeshBasicMaterial({ map: lavaTex, color: new THREE.Color(1.9, 1.15, 0.8) }), 0, -1.2, 0, OBBY, false);
lava.rotation.x = -Math.PI / 2;
const lavaLight = new THREE.PointLight(0xff6a20, 25, 14, 1.6); lavaLight.position.set(3, -0.6, 1); OBBY.add(lavaLight);
mesh(rbox(5, 1.6, 6, 0.08), mat('#8a9aa8', 0.7), -3.5, -0.8, 0, OBBY);                     // spawn pad, top at y = 0
mesh(new THREE.CylinderGeometry(0.6, 0.6, 0.08, 32), new THREE.MeshStandardMaterial({ color: C('#4cb050'), emissive: C('#2a8a3a'), emissiveIntensity: 0.6 }), -4.4, 0.04, 0.8, OBBY);
const PLAT = [[0.6, -0.1, 0.2, '#e5483c'], [2.3, 0.5, -0.4, '#3b82d6'], [4.1, 0.1, 0.3, '#f2c230'], [5.9, 0.8, -0.3, '#4cb050'], [7.7, 0.3, 0.2, '#9b59d0'], [9.5, 1.0, -0.2, '#e5483c'], [11.4, 0.6, 0.1, '#3b82d6']];
const platMeshes = PLAT.map(([x, y, z, c]) => mesh(rbox(1.3, 0.4, 1.3, 0.06), mat(c, 0.45), x, y, z, OBBY));
{ const pole = mesh(new THREE.CylinderGeometry(0.05, 0.05, 2.4, 12), mat('#222'), 13.2, 1.8, 0, OBBY);
  const flag = textPlane(1.0, 0.7, 128, (g, w, h) => { for (let r = 0; r < 4; r++) for (let k = 0; k < 6; k++) { g.fillStyle = (r + k) % 2 ? '#111' : '#f4f4f4'; g.fillRect(k * w / 6, r * h / 4, w / 6, h / 4); } });
  flag.position.set(13.7, 2.6, 0); OBBY.add(flag); void pole; }
[[-6, 4, -14, 1.2], [6, 6, -18, 1.6], [16, 3, -12, 1.1], [-14, 7, -22, 1.8]].forEach(([x, y, z, s]) => cloud(x, y, z, s, OBBY));
for (const [x, y, z] of [[-9, 2.2, -10], [10, 3.5, -12], [2, 4.2, -16]]) mesh(rbox(1.6, 0.4, 1.6, 0.05), mat('#8cb7d8', 0.6), x, y, z, OBBY);
// the giant welcome sign
const SIGN = new THREE.Group(); OBBY.add(SIGN);
{ for (const dx of [-2.6, 2.6]) mesh(new THREE.CylinderGeometry(0.14, 0.14, 4.6, 12), mat('#8a5a32'), dx, -0.8, 0, SIGN);
  mesh(rbox(7.2, 3.2, 0.3, 0.12), mat('#fff4d6', 0.6), 0, 2.4, 0, SIGN);
  const face = textPlane(6.8, 2.8, 1024, (g, w, h) => {
    g.fillStyle = '#ffe08a'; g.fillRect(0, 0, w, h);
    g.font = '230px "Caveat Brush"'; g.textAlign = 'left'; const txt = 'WELCOME!!!'; let x = (w - g.measureText(txt).width) / 2;
    for (let i = 0; i < txt.length; i++) { g.fillStyle = COLS[i % 6]; g.strokeStyle = '#200a00'; g.lineWidth = 8; g.strokeText(txt[i], x, 255 + 10 * Math.sin(i)); g.fillText(txt[i], x, 255 + 10 * Math.sin(i)); x += g.measureText(txt[i]).width; }
    g.font = '90px "Caveat Brush"'; g.textAlign = 'center'; g.fillStyle = '#c8312c'; g.fillText('EVERYONE!  :)', w / 2, 380);
  });
  face.position.set(0, 2.4, 0.16); SIGN.add(face);
  for (let i = 0; i < 12; i++) { const bulb = mesh(new THREE.SphereGeometry(0.08, 10, 8), glowMat(2.4, 2.0, 0.9), -3.4 + i * 0.62, 4.05, 0.12, SIGN, false); void bulb; } }

// ---------------------------------------------------------------- SET: race track, x = 200
const RACE = new THREE.Group(); RACE.position.x = 200; scene.add(RACE);
mesh(new THREE.PlaneGeometry(200, 200), mat('#58b04e', 0.95), 0, -0.01, 0, RACE).rotation.x = -Math.PI / 2;
{ const asph = mesh(new THREE.PlaneGeometry(200, 6), mat('#3e3e46', 0.9), 0, 0.005, -1, RACE); asph.rotation.x = -Math.PI / 2;
  const dash = new THREE.InstancedMesh(new THREE.PlaneGeometry(1.2, 0.14), mat('#f4f4f4', 0.8), 60); dash.receiveShadow = true;
  for (let i = 0; i < 60; i++) { _m4.makeRotationX(-Math.PI / 2); _m4.setPosition(-60 + i * 2.2, 0.01, -1); dash.setMatrixAt(i, _m4); } RACE.add(dash);
  const curb = new THREE.InstancedMesh(new THREE.BoxGeometry(0.8, 0.12, 0.35), new THREE.MeshStandardMaterial({ roughness: 0.6 }), 300); curb.receiveShadow = true;
  for (let i = 0; i < 300; i++) { const side = i < 150 ? -4.1 : 2.1; _m4.makeTranslation(-60 + (i % 150) * 0.8, 0.06, side); curb.setMatrixAt(i, _m4); curb.setColorAt(i, C(i % 2 ? '#d8312a' : '#f4f4f4')); } RACE.add(curb);
  const chk = textPlane(1.2, 6, 64, (g, w, h) => { for (let r = 0; r < 20; r++) for (let k = 0; k < 4; k++) { g.fillStyle = (r + k) % 2 ? '#111' : '#f4f4f4'; g.fillRect(k * w / 4, r * h / 20, w / 4, h / 20); } });
  chk.rotation.x = -Math.PI / 2; chk.position.set(-7, 0.012, -1); RACE.add(chk);
  // grandstand with a block crowd
  mesh(rbox(80, 4, 3, 0.1), mat('#7d8794', 0.8), 0, 2, -9, RACE);
  const crowd = new THREE.InstancedMesh(rbox(0.38, 0.5, 0.38, 0.06), new THREE.MeshStandardMaterial({ roughness: 0.6 }), 600); crowd.castShadow = false;
  for (let i = 0; i < 600; i++) { const r = Math.floor(i / 150), c = i % 150; _m4.makeTranslation(-38 + c * 0.52, 2.0 + r * 0.7, -8.5 + r * 0.35 - 0.4); crowd.setMatrixAt(i, _m4); crowd.setColorAt(i, C(COLS[Math.floor(hash(i) * 7)])); }
  RACE.add(crowd); RACE.userData.crowd = crowd;
  for (let i = 0; i < 40; i++) { const f = mesh(new THREE.ConeGeometry(0.25, 0.5, 3), mat(COLS[i % 6]), -38 + i * 2, 5.2, -7.4, RACE, false); f.rotation.z = Math.PI; } }
[[-10, 9, -40, 2], [12, 12, -50, 2.4], [30, 8, -40, 1.8]].forEach(([x, y, z, s]) => cloud(x, y, z, s, RACE));
function car(col, num) {
  const g = new THREE.Group(); RACE.add(g);
  mesh(rbox(2.4, 0.5, 1.1, 0.12), mat(col, 0.35), 0, 0.45, 0, g);
  mesh(rbox(0.9, 0.42, 0.8, 0.12), mat('#bfe3ff', 0.15), -0.1, 0.86, 0, g);
  mesh(rbox(0.25, 0.5, 1.2, 0.04), mat(col, 0.35), -1.15, 0.85, 0, g);
  for (const [x, z] of [[-0.8, 0.55], [0.8, 0.55], [-0.8, -0.55], [0.8, -0.55]]) { const w = mesh(new THREE.CylinderGeometry(0.28, 0.28, 0.22, 20), mat('#1c1c20', 0.7), x, 0.28, z, g); w.rotation.x = Math.PI / 2; }
  const n = textPlane(0.42, 0.42, 128, (gg, w, h) => { gg.fillStyle = '#fff'; gg.beginPath(); gg.arc(w / 2, h / 2, w / 2 - 2, 0, 7); gg.fill(); gg.fillStyle = '#111'; gg.font = '700 80px Kalam'; gg.textAlign = 'center'; gg.fillText(num, w / 2, h * 0.75); });
  n.position.set(0.35, 0.47, 0.56); g.add(n);
  return g;
}
const CARS = ['#e5483c', '#3b82d6', '#4cb050', '#9b59d0', '#f2c230', '#3b82d6'].map((c, i) => car(c, String(7 + i)));
// pizza stand
const STAND = new THREE.Group(); RACE.add(STAND); STAND.position.set(3.4, 0, 3.2);
function pizzaMesh(parent, r = 0.32) {
  const tx = canvasTex(256, 256, (g) => { g.fillStyle = '#e8a64a'; g.beginPath(); g.arc(128, 128, 126, 0, 7); g.fill(); g.fillStyle = '#f6d266'; g.beginPath(); g.arc(128, 128, 104, 0, 7); g.fill();
    g.fillStyle = '#c8312c'; for (let i = 0; i < 7; i++) { const a = i * 0.9; g.beginPath(); g.arc(128 + 60 * Math.cos(a), 128 + 60 * Math.sin(a), 16, 0, 7); g.fill(); } });
  const m = mesh(new THREE.CylinderGeometry(r, r, 0.05, 32), [mat('#e8a64a'), new THREE.MeshStandardMaterial({ map: tx, roughness: 0.6 }), mat('#e8a64a')], 0, 0, 0, parent);
  return m;
}
{ mesh(rbox(2.8, 1.0, 1.0, 0.06), mat('#f2c230', 0.5), 0, 0.5, 0, STAND);
  for (const dx of [-1.3, 1.3]) mesh(new THREE.CylinderGeometry(0.06, 0.06, 2.4, 10), mat('#8a5a32'), dx, 1.2, -0.3, STAND);
  const awnTex = canvasTex(256, 64, (g, w, h) => { for (let i = 0; i < 8; i++) { g.fillStyle = i % 2 ? '#e5483c' : '#fff4d6'; g.fillRect(i * w / 8, 0, w / 8, h); } });
  const awn = mesh(new THREE.BoxGeometry(3.0, 0.08, 1.4), [mat('#e5483c'), mat('#e5483c'), new THREE.MeshStandardMaterial({ map: awnTex }), mat('#e5483c'), new THREE.MeshStandardMaterial({ map: awnTex }), mat('#e5483c')], 0, 2.4, 0.1, STAND);
  awn.rotation.x = 0.25;
  const sg = textPlane(2.0, 0.55, 512, (g, w, h) => { g.fillStyle = '#fff4d6'; g.fillRect(0, 0, w, h); g.strokeStyle = '#200a00'; g.lineWidth = 8; g.strokeRect(4, 4, w - 8, h - 8); g.fillStyle = '#c8312c'; g.font = '100px "Caveat Brush"'; g.textAlign = 'center'; g.fillText('FREE PIZZA!', w / 2, h * 0.75); });
  sg.position.set(0, 2.95, -0.2); STAND.add(sg);
  for (const dx of [-0.9, 0, 0.9]) pizzaMesh(STAND).position.set(dx, 1.03, 0.1); }
const heldPizza = new THREE.Group(); scene.add(heldPizza); pizzaMesh(heldPizza, 0.36).rotation.x = Math.PI / 2;
const megaphone = new THREE.Group(); scene.add(megaphone);
{ const cone = mesh(new THREE.CylinderGeometry(0.28, 0.08, 0.6, 24, 1, true), new THREE.MeshStandardMaterial({ color: C('#f2f2f2'), roughness: 0.4, side: THREE.DoubleSide }), 0, 0.3, 0, megaphone); void cone;
  mesh(new THREE.CylinderGeometry(0.06, 0.06, 0.25, 12), mat('#c8312c'), 0, -0.05, 0, megaphone); }

// ---------------------------------------------------------------- SET: developers' office, x = 300
const OFFICE = new THREE.Group(); OFFICE.position.x = 300; scene.add(OFFICE);
mesh(new THREE.PlaneGeometry(60, 60), mat('#c9b48e', 0.8), 0, 0, 0, OFFICE).rotation.x = -Math.PI / 2;
mesh(new THREE.PlaneGeometry(60, 12), mat('#b9a98c', 0.9), 0, 6, -5, OFFICE);
for (let i = 0; i < 4; i++) mesh(rbox(2.4, 3, 0.1, 0.03), new THREE.MeshStandardMaterial({ color: C('#d8ecff'), emissive: C('#cfe6ff'), emissiveIntensity: 0.35 }), -6 + i * 4, 3.3, -4.94, OFFICE, false);
mesh(rbox(5.2, 0.12, 2.0, 0.03), mat('#8a6a48', 0.5), 0, 1.0, -0.6, OFFICE);
for (const dx of [-2.4, 2.4]) mesh(rbox(0.12, 1.0, 1.8, 0.02), mat('#5a4a38'), dx, 0.5, -0.6, OFFICE);
const monCv = Object.assign(document.createElement('canvas'), { width: 640, height: 384 }), monG = monCv.getContext('2d');
const monTex = new THREE.CanvasTexture(monCv); monTex.colorSpace = THREE.SRGBColorSpace;
const monScreen = new THREE.Mesh(new THREE.PlaneGeometry(2.6, 1.56), new THREE.MeshBasicMaterial({ map: monTex, color: new THREE.Color(1.5, 1.5, 1.5) }));
{ mesh(rbox(2.85, 1.8, 0.12, 0.05), mat('#202026', 0.4), 0, 2.2, -1.1, OFFICE); monScreen.position.set(0, 2.2, -1.03); OFFICE.add(monScreen);
  mesh(new THREE.CylinderGeometry(0.06, 0.06, 0.5, 10), mat('#333'), 0, 1.3, -1.15, OFFICE);
  const plant = new THREE.Group(); plant.position.set(-3.6, 0, -2.5); OFFICE.add(plant); mesh(new THREE.CylinderGeometry(0.3, 0.24, 0.6, 16), mat('#c66a3a'), 0, 0.3, 0, plant);
  for (let i = 0; i < 7; i++) { const l = mesh(new THREE.SphereGeometry(0.4, 12, 8), mat('#3a8a4a', 0.7), Math.cos(i) * 0.25, 0.9 + (i % 3) * 0.2, Math.sin(i) * 0.25, plant); l.scale.set(0.5, 1, 0.3); l.rotation.z = (i - 3) * 0.3; }
  const wb = textPlane(4, 2, 512, (g, w, h) => { g.fillStyle = '#fbfbf8'; g.fillRect(0, 0, w, h); g.strokeStyle = '#999'; g.lineWidth = 8; g.strokeRect(0, 0, w, h); g.fillStyle = '#2a4fa0'; g.font = '48px "Caveat Brush"'; g.fillText('BUG: TOBY', 30, 70); g.fillText('FIX: ???', 30, 140); });
  wb.position.set(8.6, 3.2, -4.9); OFFICE.add(wb); }
function drawMonitor(t, mode) {
  const g = monG, w = 640, h = 384;
  if (mode === 'off') { g.fillStyle = '#050507'; g.fillRect(0, 0, w, h); monTex.needsUpdate = true; return; }
  const gr = g.createLinearGradient(0, 0, 0, h); gr.addColorStop(0, '#6fbdf5'); gr.addColorStop(1, '#d8f1ff'); g.fillStyle = gr; g.fillRect(0, 0, w, h);
  g.fillStyle = '#5cb04e'; g.fillRect(0, h * 0.62, w, h);
  for (let i = 0; i < 24; i++) { g.fillStyle = COLS[i % 7]; g.beginPath(); g.ellipse(30 + (i * 53) % (w - 50), 40 + (i * 37) % (h * 0.5) + 6 * Math.sin(t * 3 + i), 18, 22, 0, 0, 7); g.fill(); }
  g.fillStyle = '#f6c48a'; g.fillRect(w / 2 - 22, h * 0.45, 44, 40); g.fillStyle = '#f28b2c'; g.fillRect(w / 2 - 26, h * 0.45 + 40, 52, 60);
  g.fillStyle = '#3b82d6'; g.beginPath(); g.moveTo(w / 2 - 20, h * 0.45); g.lineTo(w / 2, h * 0.45 - 40); g.lineTo(w / 2 + 20, h * 0.45); g.fill();
  if (mode === 'pizza') { g.fillStyle = 'rgba(0,0,0,0.6)'; g.fillRect(0, 0, w, 64); g.fillStyle = '#fff'; g.font = '700 40px Kalam'; g.textAlign = 'center'; g.fillText('Toby: DID SOMEBODY ORDER PIZZA?', w / 2, 46); }
  monTex.needsUpdate = true;
}

// ---------------------------------------------------------------- dynamic props pool
const bunches = [0, 1, 2, 3, 4, 5].map((i) => balloonBunch(6, i, scene));
const handBunch = balloonBunch(6, 3, scene);
const puffs = [0, 1, 2, 3].map(() => puff(scene));

// ---------------------------------------------------------------- lights
const sun = new THREE.DirectionalLight(0xfff0d8, 3.2); scene.add(sun, sun.target);
sun.castShadow = true; sun.shadow.mapSize.set(2048, 2048); sun.shadow.bias = -0.0004; sun.shadow.normalBias = 0.02;
Object.assign(sun.shadow.camera, { left: -14, right: 14, top: 14, bottom: -14, near: 1, far: 80 });
const hemi = new THREE.HemisphereLight(0xbfe0ff, 0x6a8a50, 1.25); scene.add(hemi);
const fill = new THREE.DirectionalLight(0xbcd8ff, 0.6); scene.add(fill, fill.target);

// ---------------------------------------------------------------- 2D overlay (labels, UI, cards) on a canvas, composited in the grade
const ovCanvas = Object.assign(document.createElement('canvas'), { width: W, height: H }), og = ovCanvas.getContext('2d');
const ovTex = new THREE.CanvasTexture(ovCanvas); ovTex.colorSpace = THREE.SRGBColorSpace;
const pop = (k, dur = 0.15) => (k <= 0 ? 0 : k < dur ? 1.1 * easeOut(k / dur) : 1 + 0.1 * Math.exp(-(k - dur) * 25));
const SCRIPT = '"Caveat Brush"';
function rr(x, y, w, h, r) { og.beginPath(); og.roundRect(x, y, w, h, r); }
function popLabel(text, x, y, k, col = '#f2d23a', size = 60, ang = -0.06) {
  if (k <= 0) return;
  const sc = (1 + 0.35 * Math.exp(-k * 9) * Math.cos(k * 22)) * Math.min(1, k / 0.08);
  og.save(); og.translate(x, y); og.rotate(ang); og.scale(sc, sc); og.transform(1, 0, -0.22, 1, 0, 0);
  og.font = `${size}px ${SCRIPT}`; og.textAlign = 'center'; og.textBaseline = 'middle';
  og.lineJoin = 'round'; og.strokeStyle = '#200a00'; og.lineWidth = size * 0.16; og.strokeText(text, 0, 0);
  og.fillStyle = col; og.fillText(text, 0, 0); og.restore();
}
function nameTag(text, x, y, w, h, k, accent = '#f2c230', sub = null) {
  if (k <= 0) return;
  const a = Math.min(1, k / 0.15);
  og.save(); og.globalAlpha = a; rr(x, y, w, h, 6); og.fillStyle = 'rgba(23,15,13,0.86)'; og.fill(); og.fillStyle = accent; og.fillRect(x, y, 9, h);
  const n = Math.floor(Math.max(0, k - 0.15) / 0.35 * 1.4 * text.length / 1.0 * 0.7) + 1;
  og.font = `${h * 0.55}px ${SCRIPT}`; og.textBaseline = 'middle'; og.fillStyle = '#f4efe4'; og.transform(1, 0, -0.2, 1, 0, 0);
  og.fillText(text.slice(0, Math.min(text.length, n)), x + 34 + y * 0.2, y + h / 2 + 2);
  if (sub) { og.font = `26px ${SCRIPT}`; og.fillText(sub.slice(0, Math.max(0, Math.floor((k - 0.6) * 10))), x + 34 + (y + h + 30) * 0.2, y + h + 30); }
  og.restore();
}
function stamp(text, x, y, k, col = '#d0302a', size = 80, ang = -0.14) {
  if (k <= 0) return;
  const p = Math.min(1, k / 0.12), sc = 1.8 - 0.8 * p;
  og.save(); og.translate(x, y); og.rotate(ang); og.scale(sc, sc); og.globalAlpha = 0.35 + 0.65 * p;
  og.font = `${size}px ${SCRIPT}`; og.textAlign = 'center'; og.textBaseline = 'middle';
  const w = og.measureText(text).width + size * 0.6;
  og.strokeStyle = col; og.lineWidth = size * 0.09; rr(-w / 2, -size * 0.62, w, size * 1.24, size * 0.18); og.stroke();
  og.fillStyle = col; og.fillText(text, 0, size * 0.04); og.restore();
}
function ui(text, x, y, size, col = '#fff', align = 'center', bold = true) { og.font = `${bold ? 700 : 400} ${size}px Kalam`; og.textAlign = align; og.textBaseline = 'alphabetic'; og.fillStyle = col; og.fillText(text, x, y); }
function panel(x, y, w, h, a = 0.92) { rr(x, y, w, h, 22); og.fillStyle = `rgba(20,25,40,${a})`; og.fill(); og.strokeStyle = 'rgba(255,255,255,0.25)'; og.lineWidth = 3; og.stroke(); }
function gameMenu(cx, cy, k, glowK = -1, presses = [], t = 0, s = 1) {
  const p = pop(k); if (p <= 0) return;
  og.save(); og.translate(cx, cy); og.scale(p * s, p * s);
  panel(-280, -230, 560, 460); ui('GAME MENU', 0, -170, 44);
  ['Resume', 'Settings'].forEach((l, i) => { rr(-200, -130 + i * 80, 400, 62, 14); og.fillStyle = 'rgba(255,255,255,0.14)'; og.fill(); ui(l, 0, -88 + i * 80, 32, '#d8e0f2', 'center', false); });
  const press = presses.some((pt) => t - pt >= 0 && t - pt < 0.12), bs = press ? 0.94 : 1;
  og.save(); og.translate(0, 110); og.scale(bs, bs);
  if (glowK > 0) { og.shadowColor = '#ff5a4a'; og.shadowBlur = 40 + 20 * Math.sin(glowK * 10); }
  rr(-230, -48, 460, 96, 20); og.fillStyle = press ? '#b8241c' : '#e0352b'; og.fill(); og.shadowBlur = 0; og.strokeStyle = '#200a00'; og.lineWidth = 5; og.stroke();
  rr(-222, -42, 444, 30, 14); og.fillStyle = 'rgba(255,255,255,0.22)'; og.fill(); ui('LEAVE GAME', 0, 18, 50);
  og.restore(); og.restore();
}
function cursor(x, y, pressed) {
  og.save(); og.translate(x, y); const s = pressed ? 0.9 : 1; og.scale(s, s);
  og.beginPath(); og.moveTo(0, 0); og.lineTo(0, 62); og.lineTo(16, 48); og.lineTo(28, 74); og.lineTo(40, 68); og.lineTo(28, 43); og.lineTo(48, 42); og.closePath();
  og.fillStyle = '#fff'; og.fill(); og.strokeStyle = '#200a00'; og.lineWidth = 4; og.stroke();
  if (pressed) { og.strokeStyle = '#f2c230'; for (let i = 0; i < 6; i++) { const a = i * Math.PI / 3; og.beginPath(); og.moveTo(14 * Math.cos(a), 14 * Math.sin(a)); og.lineTo(30 * Math.cos(a), 30 * Math.sin(a)); og.stroke(); } }
  og.restore();
}
const NAMES = ['BlockyBen', 'SkyJumper', 'LavaLuke', 'Pixel_Pam', 'SpeedySam', 'HideMaster', 'CoolCat99', 'ZoomZoe', 'BuilderBo', 'NinjaNia', 'JumpyJo', 'Toby_Welcome'];
function playerList(x, y, t, leaves) {
  const n = leaves.filter((l) => l === null || t < l).length;
  og.save(); og.translate(x, y); panel(-230, -300, 460, 600); ui(`PLAYERS  ${n}/12`, 0, -250, 38);
  og.beginPath(); og.rect(-230, -300, 460, 600); og.clip();
  let row = 0;
  NAMES.forEach((nm, i) => {
    const l = leaves[i]; if (l !== null && t >= l + 0.25) return;
    const q = l === null || t < l ? 0 : easeOut((t - l) / 0.25), yy = -200 + row * 42, toby = nm.startsWith('Toby');
    og.save(); og.translate(-q * 460, 0); rr(-205, yy - 18, 410, 36, 10); og.fillStyle = toby ? 'rgba(242,194,48,0.25)' : 'rgba(255,255,255,0.1)'; og.fill();
    og.fillStyle = COLS[i % 7]; og.beginPath(); og.arc(-180, yy, 12, 0, 7); og.fill(); ui(nm, -158, yy + 10, 26, '#fff', 'left', toby); og.restore(); row++;
  });
  og.restore();
}
function chatBox(x, y, t, msgs, w = 520) {
  const shown = msgs.filter((m) => t >= m[0]); if (!shown.length) return;
  rr(x, y, w, 50 + 40 * shown.length, 14); og.fillStyle = 'rgba(12,15,25,0.72)'; og.fill(); ui('CHAT', x + 20, y + 34, 24, '#b3bfd8', 'left');
  shown.forEach(([tm, nm, tx, col], i) => { const yy = y + 74 + i * 40; ui(nm + ':', x + 20, yy, 24, col, 'left'); const nw = og.measureText(nm + ':').width; ui(tx.slice(0, Math.floor((t - tm) * 40)), x + 30 + nw, yy, 24, '#fff', 'left', false); });
}
function kickDialog(cx, cy, k) {
  const p = pop(k); if (p <= 0) return;
  og.save(); og.translate(cx, cy); og.scale(p, p); rr(-300, -170, 600, 340, 22); og.fillStyle = '#f4f4f6'; og.fill(); og.strokeStyle = '#200a00'; og.lineWidth = 5; og.stroke();
  og.save(); rr(-300, -170, 600, 340, 22); og.clip(); og.fillStyle = '#e0352b'; og.fillRect(-300, -170, 600, 80); og.restore();
  ui('DISCONNECTED', 0, -115, 40); ui('You were kicked', 0, -20, 34, '#262633', 'center', false); ui('from this server.', 0, 24, 34, '#262633', 'center', false);
  rr(-90, 90, 180, 56, 14); og.fillStyle = '#3b82d6'; og.fill(); ui('OK', 0, 130, 32); og.restore();
}
function joinToast(x, y, k, text) {
  if (k <= 0 || k > 2.6) return;
  const q = easeOut(k / 0.25) * (1 - easeOut((k - 2.3) / 0.3));
  og.save(); og.globalAlpha = q; rr(x - 230, y - 80 + 80 * q, 460, 60, 14); og.fillStyle = 'rgba(12,15,25,0.85)'; og.fill();
  og.fillStyle = '#4cb050'; og.beginPath(); og.arc(x - 200, y - 50 + 80 * q, 10, 0, 7); og.fill(); ui(text, x - 180, y - 40 + 80 * q, 26, '#fff', 'left'); og.restore();
}
function counterBox(x, y, k, target, prefix, sub, dur, w = 300) {
  const p = pop(k); if (p <= 0) return;
  og.save(); og.translate(x, y); og.scale(p, p); rr(-w / 2, -43, w, 86, 14); og.fillStyle = '#0f3a24'; og.fill(); og.strokeStyle = '#200a00'; og.lineWidth = 4; og.stroke();
  const v = Math.round(target * easeOut(Math.min(1, k / dur)));
  og.shadowColor = '#6aff9a'; og.shadowBlur = 16; ui(prefix + v, 0, 14, 52, '#b8ffcf'); og.shadowBlur = 0; ui(sub, 0, 36, 16, '#8fd8a8', 'center', false); og.restore();
}
function card(text, t, t0, t1) {
  og.fillStyle = '#000'; og.fillRect(0, 0, W, H);
  const cps = text.length / Math.max(0.6, (t1 - t0 - 0.2) * 0.9), n = Math.floor(Math.max(0, t - t0 - 0.04) * cps) + 1;
  og.save(); og.font = `64px ${SCRIPT}`; og.textAlign = 'left'; og.textBaseline = 'middle'; og.fillStyle = '#fafafa';
  const fullW = og.measureText(text).width; og.translate(W / 2 - fullW / 2, H / 2); og.transform(1, 0, -0.25, 1, 0, 0); og.fillText(text.slice(0, n), 0, 0); og.restore();
}

// ---------------------------------------------------------------- shots: set, camera rail, action, overlay
// cam: [eyeA, eyeB, lookA, lookB, fov]; positions are local to the set (set origin added below)
const SETS = { park: [PARK, V(0, 0, 0)], obby: [OBBY, V(100, 0, 0)], race: [RACE, V(200, 0, 0)], office: [OFFICE, V(300, 0, 0)] };
const hideAll = () => { Object.values(FIG).forEach((f) => (f.root.visible = false)); bunches.forEach((b) => (b.g.visible = false)); handBunch.g.visible = false; puffs.forEach((p) => (p.g.visible = false));
  heldPizza.visible = false; megaphone.visible = false; confetti.visible = false; SIGN.visible = false; CARS.forEach((c) => (c.visible = false)); STAND.visible = false; BELL.visible = false; };
const at = (setName, x, y, z) => SETS[setName][1].clone().add(V(x, y, z));
// put a prop in a figure's screen-right hand (arm index 1)
function inHand(f, obj, off = V(0, -0.1, 0.1), counter = true) {
  f.root.updateMatrixWorld(true); const a = f.arms[1]; a.hand.getWorldPosition(_p); obj.position.copy(_p).add(off);
  obj.rotation.set(0, 0, counter ? 0 : a.sh.rotation.z); obj.visible = true;
}
function bunchInHand(f, bb, t, k = 9) { f.root.updateMatrixWorld(true); f.arms[1].hand.getWorldPosition(_p); bb.g.position.copy(_p); poseBunch(bb, t, k); }
function crouchedPlayers(t, set = 'park') {
  ['P1', 'P2', 'P3', 'P4'].forEach((nm, i) => { const h = HIDE[i]; pose(FIG[nm], t, { x: h.x + 0.25, z: h.z - 0.55, y: -0.95 + 0.06 * Math.sin(t * 2 + i), look: i % 2 ? 0.6 : -0.6, expr: i % 2 ? 'smirk' : 'neutral' }); FIG[nm].root.position.add(SETS[set][1]); });
}
function P(nm, set, t, o) { pose(FIG[nm], t, o); FIG[nm].root.position.add(SETS[set][1]); return FIG[nm]; }

const S = [];   // one entry per beat in timeline.json, same order
// 0 hook: the noob, and the button he caused
S.push({ set: 'park', cam: [V(0.8, 1.9, 8.8), V(0.2, 1.7, 6.6), V(0, 1.5, 0), V(0, 1.6, 0), 40], act(t, i) {
  P('P1', 'park', t, { x: -2.6, z: 0.6, rot: 0.4, arms: 'hips', expr: 'angry' });
  const tb = P('TOBY', 'park', t, { x: 0, z: 1, arms: 'wave', expr: 'happy', talk: talking(i, 'TOBY', t) });
  P('P2', 'park', t, { x: 2.6, z: 0.5, rot: -0.4, expr: 'smirk' });
  bunches[0].g.position.copy(at('park', -0.9, 0.9, 1.1)); poseBunch(bunches[0], t, t - B[i].t0 - 0.2); void tb;
}, ov(t, i) { popLabel('THIS NOOB', 640, 110, t - wt(i, 'noob'), '#f2d23a', 64); gameMenu(1060, 300, t - wt(i, 'leave button'), t - wt(i, 'leave button'), [], t, 0.42); } });
// 1 name tag close-up on the obby spawn
S.push({ set: 'obby', cam: [V(-2.4, 2.2, 4.9), V(-2.8, 2.15, 4.4), V(-4.0, 1.75, 0.3), V(-4.0, 1.75, 0.3), 34], act(t, i) {
  P('TOBY', 'obby', t, { x: -4.0, z: 0.3, rot: 0.25, expr: 'happy', look: 0.2, talk: talking(i, 'TOBY', t) });
}, ov(t, i) { nameTag('TOBY', 765, 532, 415, 108, (t - B[i].t0 - 0.12) / 0.35, '#f28b2c', 'LEVEL 1 NOOB'); popLabel('ONE DREAM', 1010, 180, t - wt(i, 'dream'), '#b8ff6a', 56); } });
// 2 make every player feel welcome
S.push({ set: 'park', cam: [V(-2.4, 1.4, 6.2), V(-1.8, 1.6, 5.4), V(-1.2, 1.8, 0.5), V(-1.0, 1.9, 0.5), 40], act(t, i) {
  P('TOBY', 'park', t, { x: -1.2, z: 0.6, arms: 'cheer', expr: 'happy', look: 0.4 });
  poseConfetti(t - wt(i, 'welcome'), at('park', -1.2, 2.6, 0.8));
}, ov(t, i) { popLabel('MAKE EVERY PLAYER', 880, 250, t - wt(i, 'every player'), '#f2d23a', 54); popLabel('FEEL WELCOME', 880, 340, t - wt(i, 'welcome'), '#3dff7a', 58); } });
// 3 the obby: Toby walks onto the spawn
S.push({ set: 'obby', cam: [V(-1.6, 2.0, 8.6), V(-2.2, 1.9, 7.8), V(-3.8, 1.1, 0.3), V(-3.2, 1.1, 0.3), 42], act(t, i) {
  const k = clamp((t - B[i].t0) / 1.2);
  P('P1', 'obby', t, { x: -5.2, z: -0.6, rot: 0.6, expr: 'neutral' });
  P('TOBY', 'obby', t, { x: -7.5 + 4.6 * k, z: 0.8, rot: Math.PI / 2 * (1 - k) * 0.9, walk: k < 1 ? (t - B[i].t0) * 9 : null, expr: 'happy' });
}, ov(t, i) { nameTag('OBBY', 60, 600, 220, 76, (t - wt(i, 'obby')) / 0.35); } });
// 4 the giant welcome sign drops over the first jump
S.push({ set: 'obby', cam: [V(0.5, 2.6, 11.5), V(0.2, 2.9, 13.0), V(1.2, 1.4, 0), V(1.0, 1.6, 0), 44], act(t, i) {
  P('P1', 'obby', t, { x: -5.2, z: -0.6, rot: 0.6, expr: t > wt(i, 'giant') + 0.3 ? 'shock' : 'neutral' });
  P('TOBY', 'obby', t, { x: -2.9, z: 0.8, rot: 0.3, arms: 'cheer', expr: 'happy' });
  const k = t - wt(i, 'giant');
  SIGN.visible = k > 0; const drop = 1 - easeOut(clamp(k / 0.32)), bounce = 0.25 * Math.exp(-Math.max(0, k - 0.32) * 9) * Math.sin(Math.max(0, k - 0.32) * 26);
  SIGN.position.set(1.6, 9 * drop - bounce, -0.1);
}, ov(t, i) { popLabel('THE FIRST JUMP', 640, 660, t - wt(i, 'first jump'), '#f2d23a', 52); } });
// 5 "You're welcome!" close-up
S.push({ set: 'obby', cam: [V(-1.6, 2.0, 4.7), V(-1.8, 2.0, 4.2), V(-2.9, 1.7, 0.8), V(-2.9, 1.7, 0.8), 34], act(t, i) {
  P('TOBY', 'obby', t, { x: -2.9, z: 0.8, rot: 0.35, arms: 'cheer', expr: 'happy', talk: talking(i, 'TOBY', t) });
  SIGN.visible = true; SIGN.position.set(1.6, 0, -0.1);
}, ov(t, i) { stamp("YOU'RE WELCOME!", 900, 330, t - B[i].t0 - 0.06, '#2f9a3a', 66); } });
// 6 nobody could see the platforms: two players walk off into the lava
S.push({ set: 'obby', cam: [V(-1.4, 2.8, 11.0), V(-0.8, 2.6, 10.2), V(-0.6, 1.4, 0), V(-0.4, 1.3, 0), 42], act(t, i) {
  SIGN.visible = true; SIGN.position.set(1.6, 0, -0.1);
  P('TOBY', 'obby', t, { x: -5.4, z: 1.2, rot: 0.3, arms: 'cheer', expr: 'happy' });
  [['P1', 0.7, 0.2], ['P2', 1.25, -0.4]].forEach(([nm, tf, z], j) => {
    const lt = t - B[i].t0, x = -4.6 + 3.8 * clamp(lt / tf), fall = Math.max(0, lt - tf);
    P(nm, 'obby', t, { x, z, rot: Math.PI / 2, walk: lt * 9, y: -9 * fall * fall, expr: fall > 0 ? 'shock' : 'neutral', visible: fall < 0.6 });
    posePuff(puffs[j], lt - tf - 0.45, at('obby', -0.6, -1.0, z), 1.0);
  });
}, ov(t, i) { popLabel("WHERE'S THE JUMP?", 640, 660, t - B[i].t0 - 0.3, '#ff5a4a', 50); } });
// 7 racing game: cars zoom past the free pizza stand
const lane = (t, j, speed = 26, n = 4) => ((t * speed + j * 60 / n) % 60) - 30;
S.push({ set: 'race', cam: [V(-3.0, 2.2, 11.0), V(-1.8, 2.0, 10.0), V(0.5, 1.0, 0), V(1.2, 1.2, 0.5), 40], act(t, i) {
  STAND.visible = true;
  for (let j = 0; j < 4; j++) { CARS[j + 1].visible = true; CARS[j + 1].position.set(lane(t, j), 0, -1 + (j % 2 ? 1.2 : -1.2)); CARS[j + 1].rotation.y = 0; }
  P('TOBY', 'race', t, { x: 1.3, z: 3.6, rot: -0.2, arms: 'wave', expr: 'happy' });
}, ov(t, i) { nameTag('RACING GAME', 60, 600, 330, 76, (t - wt(i, 'racing')) / 0.35); } });
// 8 every time a car passed
S.push({ set: 'race', cam: [V(-2.6, 1.7, 9.0), V(-2.0, 1.7, 8.3), V(1.0, 1.2, 1.8), V(1.2, 1.2, 1.8), 40], act(t, i) {
  STAND.visible = true;
  for (let j = 0; j < 3; j++) { CARS[j + 2].visible = true; CARS[j + 2].position.set(lane(t, j, 32, 3), 0, -1 + (j % 2 ? 1.2 : -1.2)); }
  const tb = P('TOBY', 'race', t, { x: 1.3, z: 3.6, rot: -0.5, arms: 'presentL', expr: 'happy', look: -0.4 }); void tb;
  FIG.TOBY.root.updateMatrixWorld(true); FIG.TOBY.arms[0].hand.getWorldPosition(_p); heldPizza.position.copy(_p).add(V(0, 0.05, 0.1)); heldPizza.rotation.set(0, 0, 0); heldPizza.visible = true;
} });
// 9 Toby stops a car: pepperoni or cheese?
S.push({ set: 'race', cam: [V(-2.8, 1.8, 7.8), V(-2.2, 1.7, 7.0), V(0.9, 1.1, 1.0), V(1.0, 1.2, 1.0), 40], act(t, i) {
  STAND.visible = true;
  const k = easeOut(clamp((t - B[i].t0 + 0.4) / 0.75));
  CARS[0].visible = true; CARS[0].position.set(-16 + 16.2 * k, 0, 0.2); CARS[0].rotation.set(0, 0, -0.06 * Math.exp(-Math.max(0, t - B[i].t0 - 0.35) * 8) * (t > B[i].t0 + 0.35));
  P('TOBY', 'race', t, { x: 1.9, z: 2.2, rot: -0.6, arms: 'presentL', expr: 'happy', look: -0.5 });
  FIG.TOBY.root.updateMatrixWorld(true); FIG.TOBY.arms[0].hand.getWorldPosition(_p); heldPizza.position.copy(_p).add(V(0, 0.05, 0.1)); heldPizza.visible = true;
}, ov(t, i) { popLabel('PEPPERONI', 640, 100, t - wt(i, 'pepperoni'), '#ff5a4a', 62); popLabel('OR CHEESE?', 700, 185, t - wt(i, 'cheese'), '#f2d23a', 62); } });
// 10 traffic jam
S.push({ set: 'race', cam: [V(-6.0, 4.5, 9.5), V(-4.5, 4.0, 8.8), V(-3.0, 0.6, -0.5), V(-2.0, 0.6, -0.5), 42], act(t, i) {
  STAND.visible = true;
  CARS.forEach((c, j) => { const bump = t > wt(i, 'traffic') + j * 0.1 ? 0.05 * Math.sin(t * 20 + j) * Math.exp(-(t - wt(i, 'traffic') - j * 0.1) * 4) : 0;
    c.visible = true; c.position.set(0.2 - j * 2.75 + bump, 0, 0.2); c.rotation.set(0, 0, 0); });
  P('TOBY', 'race', t, { x: 1.9, z: 2.2, rot: -0.6, arms: 'presentL', expr: 'happy', look: -0.5 });
  FIG.TOBY.root.updateMatrixWorld(true); FIG.TOBY.arms[0].hand.getWorldPosition(_p); heldPizza.position.copy(_p).add(V(0, 0.05, 0.1)); heldPizza.visible = true;
}, ov(t, i) { popLabel('TRAFFIC JAM', 640, 110, t - wt(i, 'traffic'), '#ff5a4a', 66); [300, 540, 780, 1000].forEach((x, j) => popLabel('BEEP!', x, 300 + (j % 2) * 40, t - B[i].t0 - 0.3 - j * 0.18, '#f2d23a', 36)); } });
// 11 card
S.push({ card: true });
// 12 hide and seek: surprise party
S.push({ set: 'park', cam: [V(0, 3.0, 10.5), V(0.4, 2.6, 9.2), V(0, 0.9, -1), V(0.4, 1.0, -0.5), 42], act(t, i) {
  crouchedPlayers(t);
  const k = clamp((t - B[i].t0) / 1.0);
  P('TOBY', 'park', t, { x: 7 - 5.8 * k, z: 1.6, rot: -Math.PI / 2 * (1 - k) * 0.8, walk: k < 1 ? (t - B[i].t0) * 9 : null, arms: t > wt(i, 'surprise') ? 'cheer' : 'rest', expr: 'happy' });
  poseConfetti(t - wt(i, 'surprise'), at('park', 1.2, 2.8, 1.6));
}, ov(t, i) { popLabel('SURPRISE PARTY!', 640, 110, t - wt(i, 'surprise'), '#f2d23a', 60); nameTag('HIDE & SEEK', 60, 600, 320, 76, (t - wt(i, 'hide')) / 0.35); } });
// 13 balloons over every hiding spot
S.push({ set: 'park', cam: [V(-1.0, 2.2, 8.0), V(0.6, 2.4, 7.6), V(0, 1.2, -1.5), V(0, 1.4, -1.5), 44], act(t, i) {
  crouchedPlayers(t);
  HIDE.forEach((h, j) => { bunches[j].g.position.copy(at('park', h.x, 0.9, h.z + 0.3)); poseBunch(bunches[j], t, t - wt(i, 'balloons') - j * 0.3); });
}, ov(t, i) { popLabel('EVERY HIDING SPOT', 640, 100, t - wt(i, 'every hiding'), '#f2d23a', 56); } });
// 14 names through a megaphone
S.push({ set: 'park', cam: [V(-2.8, 2.0, 6.0), V(-2.5, 2.1, 5.4), V(0.0, 1.8, 0.6), V(0.1, 1.8, 0.6), 38], act(t, i) {
  P('TOBY', 'park', t, { x: -1.2, z: 0.6, rot: 0.5, arms: 'raiseR', expr: 'happy', talk: true });
  inHand(FIG.TOBY, megaphone, V(0.05, 0.1, 0.1), false); megaphone.rotation.set(0, 0, -1.2);
}, ov(t, i) { [['BLOCKYBEN!', 960, 150, '#f2d23a'], ['PIXEL_PAM!', 1040, 260, '#3dff7a'], ['LAVALUKE!', 930, 370, '#ff5a4a'], ['HIDEMASTER!', 1060, 480, '#f2d23a']].forEach(([n, x, y, c], j) => popLabel(n, x, y, t - wt(i, 'names') - j * 0.35, c, 42)); } });
// 15 "Found you!"
S.push({ set: 'park', cam: [V(-1.9, 2.0, 4.6), V(-1.9, 2.0, 4.1), V(-1.2, 1.7, 0.6), V(-1.2, 1.7, 0.6), 34], act(t, i) {
  P('TOBY', 'park', t, { x: -1.2, z: 0.6, rot: 0.25, arms: 'cheer', expr: 'happy', talk: talking(i, 'TOBY', t) });
}, ov(t, i) { stamp('FOUND YOU!', 920, 330, t - B[i].t0 - 0.05, '#e5483c', 84); } });
// 16 "Happy birthday!"
S.push({ set: 'park', cam: [V(0.2, 1.9, 4.5), V(0.1, 1.9, 4.0), V(-1.2, 1.7, 0.6), V(-1.2, 1.7, 0.6), 34], act(t, i) {
  P('TOBY', 'park', t, { x: -1.2, z: 0.6, rot: -0.35, arms: 'cheer', expr: 'laugh', talk: talking(i, 'TOBY', t) });
  poseConfetti(t - B[i].t0, at('park', -1.2, 3.2, 0.6));
}, ov(t, i) { stamp('HAPPY BIRTHDAY!', 360, 330, t - B[i].t0 - 0.05, '#9b59d0', 62); } });
// 17 players beg the moderators
S.push({ set: 'park', cam: [V(3.4, 1.9, 7.6), V(3.0, 1.8, 6.8), V(2.2, 1.4, 0.5), V(2.2, 1.5, 0.5), 40], act(t, i) {
  P('P1', 'park', t, { x: 0.6, z: 0.6, rot: 0.5, arms: 'beg', expr: 'angry' });
  P('P2', 'park', t, { x: 2.0, z: 0.9, rot: 0.4, arms: 'cheer', expr: 'sad' });
  P('MOD', 'park', t, { x: 4.0, z: 0.4, rot: -0.6, arms: 'hips', expr: 'neutral' });
}, ov(t, i) { const t0 = B[i].t0; chatBox(40, 120, t, [[t0 + 0.1, 'BlockyBen', 'pls remove him', '#6aa8ff'], [t0 + 0.5, 'Pixel_Pam', 'MODS HELP!!', '#c99bff'], [t0 + 0.9, 'HideMaster', 'he found me 9 times', '#7ad07a'], [t0 + 1.3, 'LavaLuke', "i'm begging u", '#ff8a7a']]);
  nameTag('MODERATOR', 840, 620, 300, 70, (t - wt(i, 'moderators')) / 0.35, '#2a4fa0'); } });
// 18 an admin kicks Toby out
S.push({ set: 'park', cam: [V(0.2, 2.0, 8.4), V(0.5, 2.0, 7.6), V(0.2, 1.4, 0.5), V(0.4, 1.5, 0.5), 40], act(t, i) {
  P('ADMIN', 'park', t, { x: -2.2, z: 0.5, rot: 0.6, arms: t > wt(i, 'kicked') - 0.2 ? 'pointR' : 'hips', expr: 'angry' });
  const gone = t >= wt(i, 'kicked');
  P('TOBY', 'park', t, { x: 2.2, z: 0.6, rot: -0.5, arms: 'raiseR', expr: 'happy', visible: !gone });
  if (!gone) bunchInHand(FIG.TOBY, handBunch, t);
  posePuff(puffs[0], t - wt(i, 'kicked'), at('park', 2.2, 1.4, 0.6), 1.3);
}, ov(t, i) { nameTag('ADMIN', 60, 600, 220, 76, (t - wt(i, 'admin')) / 0.35, '#c8312c'); kickDialog(900, 330, t - wt(i, 'kicked') - 0.2); } });
// 19 he rejoins with twice as many balloons
S.push({ set: 'park', cam: [V(1.0, 1.7, 7.2), V(1.4, 1.9, 6.6), V(1.2, 1.7, 0.5), V(1.4, 1.9, 0.5), 40], act(t, i) {
  P('P1', 'park', t, { x: -1.6, z: 0.5, rot: 0.5, expr: t > B[i].t0 + 0.3 ? 'shock' : 'neutral' });
  P('TOBY', 'park', t, { x: 2.2, z: 0.6, rot: -0.2, arms: 'cheer', expr: 'laugh', visible: t > B[i].t0 + 0.25 });
  posePuff(puffs[0], t - B[i].t0 - 0.1, at('park', 2.2, 1.4, 0.6), 1.3);
  bunches[0].g.position.copy(at('park', 1.5, 2.6, 0.5)); poseBunch(bunches[0], t, t - B[i].t0 - 0.3);
  bunches[1].g.position.copy(at('park', 2.9, 2.6, 0.5)); poseBunch(bunches[1], t, t - wt(i, 'twice'));
}, ov(t, i) { joinToast(640, 90, t - B[i].t0 - 0.2, 'Toby_Welcome joined the server'); popLabel('x2 BALLOONS', 1060, 640, t - wt(i, 'twice'), '#f2d23a', 54); } });
// 20 the developers
S.push({ set: 'office', mon: 'party', cam: [V(0, 2.0, 7.8), V(0, 2.1, 6.8), V(0, 1.8, -0.8), V(0, 1.9, -0.8), 42], act(t, i) {
  P('DEV1', 'office', t, { x: -2.6, z: 0.6, rot: 0.6, arms: 'chin', expr: 'worried', look: 0.4 });
  P('DEV2', 'office', t, { x: 2.6, z: 0.6, rot: -0.6, arms: 'hips', expr: 'angry', look: -0.4 });
}, ov(t, i) { nameTag('THE DEVELOPERS', 60, 600, 380, 76, (t - wt(i, 'developers')) / 0.35, '#2a4fa0'); } });
// 21 a brand new button (menu over the dimmed office)
S.push({ set: 'office', mon: 'party', dim: 0.45, cam: [V(-1.2, 2.2, 6.0), V(-0.8, 2.2, 5.6), V(0, 2.0, -1), V(0, 2.0, -1), 42], act(t, i) {
  P('DEV1', 'office', t, { x: -2.6, z: 0.6, rot: 0.6, arms: 'presentR', expr: 'happy' });
  P('DEV2', 'office', t, { x: 2.6, z: 0.6, rot: -0.6, arms: 'hips', expr: 'smirk' });
}, ov(t, i) { gameMenu(640, 390, t - wt(i, 'button'), t - wt(i, 'escape'), [], t); popLabel('ESCAPE ANY SERVER', 640, 85, t - wt(i, 'escape'), '#f2d23a', 54); popLabel('INSTANTLY', 1060, 650, t - wt(i, 'instantly'), '#f2d23a', 54); } });
// 22 "Leave game!"
S.push({ set: 'park', dim: 0.4, cam: [V(0, 1.6, 6), V(0, 1.6, 5.4), V(0, 1.5, 0), V(0, 1.5, 0), 42], act(t, i) {
  crouchedPlayers(t); ['P1', 'P2', 'P3', 'P4'].forEach((n, j) => { FIG[n].root.position.y += 0.95; FIG[n].root.position.z += 1.2; });
}, ov(t, i) { const z = 1 + 0.15 * easeOut(clamp((t - B[i].t0) / 0.3)); gameMenu(640, 360, 9, t - B[i].t0, [], t, z); } });
// 23 players clicked it
S.push({ set: 'park', dim: 0.4, cam: [V(0, 1.6, 5.4), V(0, 1.6, 5.2), V(0, 1.5, 0), V(0, 1.5, 0), 42], act(t, i) {
  crouchedPlayers(t); ['P1', 'P2', 'P3', 'P4'].forEach((n) => { FIG[n].root.position.y += 0.95; FIG[n].root.position.z += 1.2; });
}, ov(t, i) { const t0 = B[i].t0, pr = [0, 1, 2, 3, 4].map((j) => t0 + 0.25 + j * 0.16); gameMenu(640, 360, 9, 1, pr, t, 1.15);
  [[-150, 10], [120, -20], [-40, 30], [170, 25], [-200, -10]].forEach(([dx, dy], j) => { const q = 1 - smooth(clamp((t - t0 - j * 0.16) / 0.25)); cursor(640 + dx + q * dx * 3, 490 + dy + q * dy * 3, t - pr[j] >= 0 && t - pr[j] < 0.12); }); } });
// 24 one by one the server emptied (the players vanish in the park, the list empties)
const LEAVES = (t0) => [...Array(11)].map((_, j) => t0 + 0.15 + j * 0.14).concat([null]);
S.push({ set: 'park', dim: 0.25, cam: [V(-1.0, 3.0, 10), V(-0.4, 2.8, 9.2), V(0, 1.0, 0), V(0, 1.0, 0), 44], act(t, i) {
  const L = LEAVES(B[i].t0);
  [['P1', -3.4, 0.4], ['P2', -1.8, 1.2], ['P3', 1.6, 1.0], ['P4', 3.2, 0.3]].forEach(([n, x, z], j) => { const lt = L[j * 3]; P(n, 'park', t, { x, z, expr: 'happy', arms: 'wave', visible: t < lt }); posePuff(puffs[j], t - lt, at('park', x, 1.3, z), 1.0, 0.4); });
  P('TOBY', 'park', t, { x: 0, z: 0.5, arms: 'raiseR', expr: 'happy' }); bunchInHand(FIG.TOBY, handBunch, t);
}, ov(t, i) { playerList(1010, 370, t, LEAVES(B[i].t0)); } });
// 25 finally, Toby was alone
S.push({ set: 'park', cam: [V(0, 6.5, 16), V(0, 5.8, 14.5), V(0, 0.8, 0), V(0, 0.9, 0), 40], act(t, i) {
  P('TOBY', 'park', t, { x: 0, z: 0.5, arms: 'raiseR', expr: 'happy', look: 0.5 * Math.sin((t - B[i].t0) * 2.2) }); bunchInHand(FIG.TOBY, handBunch, t);
}, ov(t, i) { popLabel('1/12', 1120, 90, t - wt(i, 'alone'), '#f2d23a', 60); } });
// 26 card
S.push({ card: true });
// 27 the button looks like a doorbell
S.push({ set: 'park', cam: [V(-1.2, 2.1, 6.4), V(-0.6, 2.2, 5.8), V(0.6, 1.7, 0.4), V(1.0, 1.8, 0.4), 40], act(t, i) {
  BELL.visible = true; bellBtn.position.z = 0.1;
  P('TOBY', 'park', t, { x: -0.6, z: 0.6, rot: 0.5, arms: t < wt(i, 'doorbell') ? 'chin' : 'cheer', expr: t > wt(i, 'doorbell') ? 'happy' : 'neutral', look: 0.5 });
}, ov(t, i) { popLabel('DING DONG?', 420, 110, t - wt(i, 'doorbell'), '#f2d23a', 60); } });
// 28 he clicked it 20 times (each click: gone and back)
const CLICKS = [...Array(20)].map((_, j) => j * 0.135);
S.push({ set: 'park', cam: [V(0.8, 2.0, 5.6), V(0.9, 2.0, 5.0), V(1.2, 1.7, 0.4), V(1.3, 1.7, 0.4), 40], act(t, i) {
  BELL.visible = true; const c0 = wt(i, 'clicked');
  const press = CLICKS.some((p) => t - c0 - p >= 0 && t - c0 - p < 0.07); bellBtn.position.z = press ? 0.03 : 0.1;
  const gone = CLICKS.some((p) => t - c0 - p >= 0.05 && t - c0 - p < 0.1);
  P('TOBY', 'park', t, { x: 0.9, z: 0.9, rot: 0.6, arms: 'pointR', expr: 'laugh', visible: !gone });
  const last = CLICKS.filter((p) => t - c0 - p >= 0.05).pop();
  if (last !== undefined) posePuff(puffs[0], t - c0 - last - 0.05, at('park', 0.9, 1.3, 0.9), 0.45, 0.12);
}, ov(t, i) { counterBox(290, 120, t - wt(i, 'clicked'), 20, 'x', 'CLICKS', CLICKS[19]); } });
// 29 "did somebody order pizza?"
S.push({ set: 'park', cam: [V(-1.2, 2.0, 5.4), V(-1.0, 2.0, 4.8), V(0.9, 1.6, 0.6), V(0.9, 1.6, 0.6), 36], act(t, i) {
  P('TOBY', 'park', t, { x: 0.6, z: 0.6, rot: 0.2, arms: 'presentR', expr: 'laugh' });
  inHand(FIG.TOBY, heldPizza, V(0, 0.05, 0.1)); heldPizza.rotation.set(0, 0, 0);
  posePuff(puffs[0], t - B[i].t0, at('park', 0.6, 1.4, 0.6), 1.4);
}, ov(t, i) { popLabel('DID SOMEBODY', 920, 220, t - wt(i, 'did somebody'), '#f2d23a', 58); popLabel('ORDER PIZZA?', 940, 315, t - wt(i, 'pizza'), '#ff5a4a', 62); joinToast(640, 90, t - B[i].t0, 'Toby_Welcome joined the server'); } });
// 30 the developers log off
S.push({ set: 'office', mon: 'pizza', cam: [V(0, 2.4, 9.0), V(0, 2.3, 7.6), V(0, 1.8, -0.8), V(0, 1.9, -0.8), 42], act(t, i) {
  const lo = wt(i, 'logged off');
  P('DEV1', 'office', t, { x: -2.6, z: 0.6, rot: 0.5, expr: 'sad', arms: 'chin', visible: t < lo });
  P('DEV2', 'office', t, { x: 2.6, z: 0.6, rot: -0.5, expr: 'neutral', visible: t < lo + 0.15 });
  posePuff(puffs[0], t - lo, at('office', -2.6, 1.3, 0.6), 1.2); posePuff(puffs[1], t - lo - 0.15, at('office', 2.6, 1.3, 0.6), 1.2);
  this.monMode = t > lo ? 'off' : 'pizza';
}, ov(t, i) { stamp('LOGGED OFF', 640, 120, t - wt(i, 'logged off') - 0.3, '#2a4fa0', 84); } });
if (S.length !== B.length) throw new Error(`shots ${S.length} != beats ${B.length}`);

// ---------------------------------------------------------------- camera (one rail per shot, eased, slight curve)
const camera = new THREE.PerspectiveCamera(40, W / H, 0.05, 900);
const eye = V(0, 0, 0), look = V(0, 0, 0), right = V(0, 0, 0), up = V(0, 0, 0);
function shoot(sh, i, ts, k, n) {
  const p = easeInOut(clamp((ts - B[i].t0) / Math.max(0.6, B[i].t1 - B[i].t0)));
  const [eA, eB, lA, lB, fov] = sh.cam, o = SETS[sh.set][1];
  const mid = eA.clone().lerp(eB, 0.5).add(V(0.25 * (eB.z - eA.z), 0, -0.25 * (eB.x - eA.x)));   // a gentle arc, not a straight slide
  eye.copy(eA).multiplyScalar((1 - p) * (1 - p)).addScaledVector(mid, 2 * p * (1 - p)).addScaledVector(eB, p * p).add(o);
  look.copy(lA).lerp(lB, p).add(o);
  camera.fov = fov; camera.position.copy(eye); camera.up.set(0, 1, 0); camera.lookAt(look); camera.updateMatrixWorld(); camera.updateProjectionMatrix();
  if (n === 1) return;
  const F = eye.distanceTo(look), lens = 0.025;
  const a = Math.sqrt(halton(k + 1, 2)) * lens, b = halton(k + 1, 3) * Math.PI * 2, lx = Math.cos(b) * a, ly = Math.sin(b) * a;
  right.setFromMatrixColumn(camera.matrixWorld, 0); up.setFromMatrixColumn(camera.matrixWorld, 1);
  camera.position.addScaledVector(right, lx).addScaledVector(up, ly); camera.updateMatrixWorld();
  const e = camera.projectionMatrix.elements, jx = halton(k + 1, 5) - 0.5, jy = halton(k + 1, 7) - 0.5;
  e[8] += -e[0] * lx / F + 2 * jx / W; e[9] += -e[5] * ly / F + 2 * jy / H;
  camera.projectionMatrixInverse.copy(camera.projectionMatrix).invert();
}
function lights(sh, k, n) {
  const o = SETS[sh.set][1], s = n > 1 ? 0.6 : 0;
  sun.position.set(o.x - 9 + (halton(k + 1, 11) - 0.5) * s, 16 + (halton(k + 1, 13) - 0.5) * s, 10 + (halton(k + 1, 17) - 0.5) * s);
  sun.target.position.set(o.x, 0, 0);
  fill.position.set(o.x + 8, 6, 8); fill.target.position.set(o.x, 1, 0);
  sun.intensity = sh.set === 'office' ? 1.4 : 3.2; hemi.intensity = sh.set === 'office' ? 0.8 : 1.25;
}

// ---------------------------------------------------------------- post: sub-frames, bloom, one grade (+ overlay)
const vert = 'varying vec2 vUv; void main() { vUv = uv; gl_Position = vec4(position.xy, 0.0, 1.0); }';
const addPass = new FullScreenQuad(new THREE.ShaderMaterial({ uniforms: { tex: { value: null }, w: { value: 1 } }, vertexShader: vert,
  fragmentShader: 'uniform sampler2D tex; uniform float w; varying vec2 vUv; void main() { gl_FragColor = vec4(texture2D(tex, vUv).rgb * w, 1.0); }',
  blending: THREE.CustomBlending, blendSrc: THREE.OneFactor, blendDst: THREE.OneFactor, blendEquation: THREE.AddEquation, depthTest: false, depthWrite: false, transparent: true }));
const bloom = new UnrealBloomPass(new THREE.Vector2(W, H), 0.25, 0.4, 0.92);
const grade = new FullScreenQuad(new THREE.ShaderMaterial({ uniforms: { tex: { value: accum.texture }, cap: { value: ovTex }, seed: { value: 0 }, exposure: { value: 1 }, dim: { value: 0 } }, vertexShader: vert,
  fragmentShader: `uniform sampler2D tex, cap; uniform float seed, exposure, dim; varying vec2 vUv;
    float h(vec2 p) { return fract(sin(dot(p, vec2(12.9898, 78.233)) + seed) * 43758.5453); }
    vec3 aces(vec3 x) { return clamp(x * (2.51 * x + 0.03) / (x * (2.43 * x + 0.59) + 0.14), 0.0, 1.0); }
    vec3 srgb(vec3 c) { return mix(c * 12.92, 1.055 * pow(max(c, vec3(0.0)), vec3(1.0 / 2.4)) - 0.055, step(0.0031308, c)); }
    void main() {
      vec2 d = vUv - 0.5; float ca = dot(d, d) * 0.006;
      vec3 c = vec3(texture2D(tex, vUv + d * ca).r, texture2D(tex, vUv).g, texture2D(tex, vUv - d * ca).b) * exposure;
      c = aces(c * 1.05);
      c *= mix(1.0, 0.72, smoothstep(0.4, 1.0, length(d * vec2(1.0, 0.8)) * 1.45));
      c = srgb(c) * (1.0 - dim);
      c += (h(vUv * 1000.0) - 0.5) * 0.025 * (1.0 - 0.55 * dot(c, vec3(0.33)));
      vec4 k = texture2D(cap, vUv); c = c * (1.0 - k.a) + k.rgb;
      gl_FragColor = vec4(c, 1.0); }`, depthTest: false, depthWrite: false }));

function shotAt(t) { let i = 0; while (i + 1 < B.length && B[i + 1].t0 <= t) i++; return i; }

export function renderAt(t, n = 1) {
  const i = shotAt(t), sh = S[i];
  og.clearRect(0, 0, W, H);
  renderer.setRenderTarget(accum); renderer.setClearColor(0x000000, 1); renderer.clear();
  if (sh.card) {
    card(B[i].sents[0].text, t, B[i].t0, B[i].t1);
  } else {
    Object.entries(SETS).forEach(([k, [g]]) => (g.visible = k === sh.set));
    sky.position.copy(SETS[sh.set][1]);
    for (let k = 0; k < n; k++) {
      let ts = n === 1 ? t : t + ((k + 0.5) / n - 0.5) * SHUTTER;
      ts = clamp(ts, B[i].t0, B[i].t1 - 1e-4);                          // never blur across a cut
      hideAll(); sh.monMode = sh.mon; sh.act.call(sh, ts, i);
      PLAT.forEach(([, y], j) => (platMeshes[j].position.y = y + 0.08 * Math.sin(ts * 1.6 + j)));
      lava.material.map.offset.set(ts * 0.01, ts * 0.006);
      if (sh.set === 'office') drawMonitor(ts, sh.monMode || 'party');
      shoot(sh, i, ts, k, n); lights(sh, k, n);
      renderer.setRenderTarget(rt); renderer.render(scene, camera);
      addPass.material.uniforms.tex.value = rt.texture; addPass.material.uniforms.w.value = 1 / n;
      renderer.setRenderTarget(accum); renderer.autoClear = false; addPass.render(renderer); renderer.autoClear = true;
    }
    bloom.render(renderer, accum, accum, 0, false);
    if (sh.ov) sh.ov(t, i);
  }
  ovTex.needsUpdate = true;
  grade.material.uniforms.seed.value = (t * 24) % 97;
  grade.material.uniforms.dim.value = sh.dim || 0;
  grade.material.uniforms.exposure.value = sh.card ? 0 : smooth(seg(t, 0, 0.25)) * (1 - smooth(seg(t, total - 0.6, total)));
  renderer.setRenderTarget(null); grade.render(renderer);
}
window.renderAt = renderAt; window.total = total;
