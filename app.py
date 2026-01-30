import streamlit as st
import random
import time

# --- 司令部：環境設定 ---
st.set_page_config(page_title="STRATEGIC CONSOLE", layout="wide", initial_sidebar_state="collapsed")

# カスタムCSS：ダークモードに映えるミニマルで上品な軍事UI
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@100;400&display=swap');
    .main { background-color: #050505; color: #e0e0e0; font-family: 'JetBrains Mono', monospace; }
    .block-container { padding: 1rem 1rem; }
    
    /* ボタン：ガラスモーフィズムと洗練された境界線 */
    .stButton>button {
        width: 100%; border: 1px solid #333; background: rgba(255, 255, 255, 0.05);
        color: #aaa; font-size: 0.85rem; height: 3.5rem; border-radius: 4px;
        transition: 0.3s;
    }
    .stButton>button:hover { border: 1px solid #00d4ff; color: #00d4ff; background: rgba(0, 212, 255, 0.1); }
    
    /* メトリック：上品な発光 */
    [data-testid="stMetricValue"] { font-size: 1.5rem !important; color: #00d4ff !important; font-weight: 100 !important; }
    [data-testid="stMetricLabel"] { font-size: 0.75rem !important; color: #666 !important; }
    
    /* ログ：システム端末風 */
    .terminal-log {
        font-size: 0.75rem; color: #00d4ff; background: rgba(0, 212, 255, 0.05);
        border-left: 2px solid #00d4ff; padding: 10px; margin-top: 10px; border-radius: 0 4px 4px 0;
    }
    
    /* プログレスバー：細身でモダン */
    .stProgress > div > div > div > div { background-image: linear-gradient(to right, #004e92, #00d4ff); }
    </style>
    """, unsafe_allow_html=True)

if 'state' not in st.session_state:
    st.session_state.state = {
        "p1": {"land": 100.0, "milit": 0.0, "buffer": 20.0, "atom": 0},
        "p2": {"land": 300.0, "milit": 50.0},
        "turn": 1, "ap": 2, "start": False,
        "visual": "SCANNING", "logs": ["SYSTEM READY. STANDBY FOR COMMAND."]
    }

s = st.session_state.state
p1, p2 = s["p1"], s["p2"]

def update_state(cmd):
    s["visual"] = cmd
    if cmd == "DEVELOP":
        p1["milit"] += 25; p1["atom"] += 20
        s["logs"].insert(0, "REPORT: NEW STRATEGIC TECH INTEGRATED.")
    elif cmd == "STRIKE":
        dmg = (p1["milit"] * 0.45) + (p1["buffer"] * 0.55)
        p2["land"] -= dmg
        s["logs"].insert(0, f"STRIKE SUCCESSFUL. IMPACT: {dmg:.1f}")
    elif cmd == "FORTIFY":
        s["logs"].insert(0, "AIR DEFENSE PARAMETERS OPTIMIZED.")
    elif cmd == "ANNEX":
        if p1["milit"] >= 20:
            p1["milit"] -= 20; area = max(p2["land"] * 0.15, 30.0)
            p2["land"] -= area; p1["buffer"] += area
            s["logs"].insert(0, f"BUFFER ZONE EXPANDED BY {area:.1f}.")
    elif cmd == "FINAL":
        p2["land"] *= 0.2; p1["atom"] = 0
        s["logs"].insert(0, "FINAL DETERRENT EXECUTED. AREA NEUTRALIZED.")

    s["ap"] -= 1
    if s["ap"] <= 0:
        # AIターン
        enemy_dmg = (p2["milit"] * 0.22)
        if p1["buffer"] > 0:
            p1["buffer"] = max(0, p1["buffer"] - enemy_dmg)
        else:
            p1["land"] = max(0, p1["land"] - enemy_dmg)
        s["ap"], s["turn"] = 2, s["turn"] + 1

# --- インターフェース ---
if not s["start"]:
    st.title("NOCTURNE COMMAND")
    st.write("上品かつ静かなる戦略を。")
    if st.button("INITIALIZE SYSTEM"): s["start"] = True; st.rerun()
else:
    # 1. 敵情視察バー（最小限）
    st.write(f"OPPONENT INTEGRITY: {p2['land']:.1f}")
    st.progress(max(0.0, min(p2['land']/400, 1.0)))

    # 2. 戦況モニター（画像に頼らず、抽象的なスタイリッシュ演出）
    # 代わりに、美しく加工された「公共の科学・技術写真」を使用
    mon_img = {
        "SCANNING": "https://images.unsplash.com/photo-1451187580459-43490279c0fa?q=80&w=800", # 地球/データ
        "DEVELOP": "https://images.unsplash.com/photo-1518770660439-4636190af475?q=80&w=800", # 回路
        "STRIKE": "https://images.unsplash.com/photo-1534063640280-928d3a82688f?q=80&w=800",  # 追跡
        "FORTIFY": "https://images.unsplash.com/photo-1478760329108-5c3ed9d495a0?q=80&w=800", # ノイズ/防御
        "ANNEX": "https://images.unsplash.com/photo-1506774518161-b710d10e2733?q=80&w=800",   # 地図
        "FINAL": "https://images.unsplash.com/photo-1446776811953-b23d57bd21aa?q=80&w=800"    # 宇宙からの視点
    }
    st.image(mon_img.get(s["visual"], mon_img["SCANNING"]), use_container_width=True)

    # 3. 自軍ステータス（スマホ1画面に収まるようコンパクトに）
    c1, c2, c3 = st.columns(3)
    c1.metric("HOME", f"{p1['land']:.1f}")
    c2.metric("ZONE", f"{p1['buffer']:.1f}")
    c3.metric("AP", f"{s['ap']}")

    # 4. 指令操作（美しく整列されたパネル）
    if p1["atom"] >= 200:
        if st.button("EXECUTE FINAL DETERRENT", type="primary"): update_state("FINAL"); st.rerun()

    ctrl1, ctrl2 = st.columns(2)
    if ctrl1.button("TECH DEV"): update_state("DEVELOP"); st.rerun()
    if ctrl2.button("AIR DEF"): update_state("FORTIFY"); st.rerun()
    if ctrl1.button("STRIKE"): update_state("STRIKE"); st.rerun()
    if ctrl2.button("ANNEX"): update_state("ANNEX"); st.rerun()

    # 5. システムログ
    st.markdown(f'<div class="terminal-log">{s["logs"][0]}</div>', unsafe_allow_html=True)

    # 終局判定
    if p1["land"] <= 0 or p2["land"] <= 0:
        st.write("--- MISSION CONCLUDED ---")
        if st.button("REINITIALIZE"): st.session_state.clear(); st.rerun()
