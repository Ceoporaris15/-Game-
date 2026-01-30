import streamlit as st
import random

# --- 戦域設定 ---
st.set_page_config(page_title="STRATEGIC CHESS", layout="centered", initial_sidebar_state="collapsed")

# スマホ最適化CSS：スクロールを排除し、盤面を1画面に収める
st.markdown("""
    <style>
    .main { background-color: #0e1111; color: #d3d3d3; font-family: 'Courier New', monospace; }
    .stButton>button { 
        width: 100%; border: 1px solid #4a4a4a; background-color: #1a1a1a; color: #00ff00;
        font-weight: bold; height: 3.5em; border-radius: 0px; font-size: 0.8rem;
    }
    .stProgress > div > div > div > div { background-color: #ff0000; }
    .status-box { background-color: #001100; border: 1px solid #00ff00; padding: 10px; text-align: center; }
    .battle-field { 
        background-color: #111; border: 2px dashed #444; padding: 20px; 
        text-align: center; font-size: 2rem; margin: 10px 0;
    }
    .metric-val { color: #00ff00; font-size: 1.5rem; font-weight: bold; }
    .metric-label { font-size: 0.7rem; text-transform: uppercase; }
    </style>
    """, unsafe_allow_html=True)

if 'state' not in st.session_state:
    st.session_state.state = {
        "p1": {"land": 100.0, "milit": 0.0, "buffer": 20.0, "shield": False, "atom": 0},
        "p2": {"land": 350.0, "milit": 60.0},
        "turn": 1, "ap": 2, "wmd": False, "hard_mode": False,
        "mode_selected": False, "last_action": "READY", "board_icon": "🚩"
    }

s = st.session_state.state
p1, p2 = s["p1"], s["p2"]

# --- 司令部ロジック ---
def apply_strike(dmg):
    if p1["shield"]: dmg *= 0.6
    if p1["buffer"] > 0:
        blocked = min(p1["buffer"], dmg)
        p1["buffer"] -= blocked
        dmg -= blocked
    if dmg > 0: p1["land"] = max(0, p1["land"] - dmg)

def enemy_action():
    acts = 2 if s["hard_mode"] else 1
    for _ in range(acts):
        if p2["land"] <= 0: break
        if s["wmd"]:
            apply_strike(p1["land"] * 0.4)
            s["wmd"] = False
        else:
            if random.random() < (0.2 if s["hard_mode"] else 0.1): s["wmd"] = True
            else: apply_strike(p2["milit"] * 0.2)

def exec_op(cmd):
    if cmd == "DEV":
        p1["milit"] += 25.0; p1["atom"] += 20
        s.update({"last_action": "RESEARCHING", "board_icon": "🧪"})
    elif cmd == "DEF":
        p1["shield"] = True
        s.update({"last_action": "DEFENDING", "board_icon": "🛡️"})
    elif cmd == "ATK":
        p2["land"] -= (p1["milit"] * 0.5) + (p1["buffer"] * 0.6)
        s.update({"last_action": "MARCHING", "board_icon": "🚜"}) # 戦車
    elif cmd == "OCC":
        if p1["milit"] >= 20:
            p1["milit"] -= 20
            stolen = max(p2["land"] * 0.2, 40.0)
            p2["land"] -= stolen; p1["buffer"] += stolen
            s.update({"last_action": "OCCUPYING", "board_icon": "🛰️"}) # ミサイル/衛星
    elif cmd == "NUKE":
        p2["land"] *= 0.2; p1["atom"] = 0
        s.update({"last_action": "JUDGEMENT", "board_icon": "☢️"})

    s["ap"] -= 1
    if s["ap"] <= 0:
        enemy_action()
        s["ap"], s["turn"], p1["shield"] = 2, s["turn"] + 1, False

# --- インターフェース ---
if not s["mode_selected"]:
    st.title("🛡️ STRATEGIC COMMAND")
    if st.button("作戦開始"): s["mode_selected"] = True; st.rerun()
    if st.button("非常事態 (HARD)"): s["hard_mode"] = True; s["mode_selected"] = True; st.rerun()
else:
    # 1. 敵軍エリア (将棋の敵陣)
    st.markdown(f"""
    <div class="status-box">
        <div class="metric-label">ENEMY TERRITORY</div>
        <div class="metric-val">{p2['land']:.0f}</div>
        <small>{'⚠️ WMD DETECTED' if s['wmd'] else 'STATUS: STABLE'}</small>
    </div>
    """, unsafe_allow_html=True)
    st.progress(max(0.0, min(p2['land']/500, 1.0)))

    # 2. 中央戦域 (盤面)
    # ここにアクションに応じたアイコンがリアルタイムで表示される
    st.markdown(f"""
    <div class="battle-field">
        <div>{s['board_icon']}</div>
        <div style="font-size: 0.8rem; color: #888;">{s['last_action']}</div>
    </div>
    """, unsafe_allow_html=True)

    # 3. 自軍エリア (将棋の自陣)
    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f'<div class="metric-label">HOME</div><div class="metric-val">{p1["land"]:.0f}</div>', unsafe_allow_html=True)
    with col2:
        st.markdown(f'<div class="metric-label">BUFFER</div><div class="metric-val">{p1["buffer"]:.0f}</div>', unsafe_allow_html=True)
    
    # 4. 操作パネル (駒を打つ感覚で)
    if p1["land"] <= 0:
        st.error("落城")
        if st.button("RETRY"): st.session_state.clear(); st.rerun()
    elif p2["land"] <= 0:
        st.success("制覇")
        if st.button("RETRY"): st.session_state.clear(); st.rerun()
    else:
        st.write(f"TURN: {s['turn']} | AP: {s['ap']}")
        
        # 核兵器ボタン
        if p1["atom"] >= 200:
            if st.button("☢️ 核兵器投入", type="primary"): exec_op("NUKE"); st.rerun()
        
        btn_c1, btn_c2 = st.columns(2)
        if btn_c1.button("🛠 開発 (DEV)"): exec_op("DEV"); st.rerun()
        if btn_c2.button("🛡 防衛 (DEF)"): exec_op("DEF"); st.rerun()
        if btn_c1.button("🚜 進軍 (ATK)"): exec_op("ATK"); st.rerun()
        if btn_c2.button("🛰 占領 (OCC)"): exec_op("OCC"); st.rerun()

    # 5. ステータスバー
    st.caption(f"MILITARY: {p1['milit']:.0f}/100 | SPECIAL: {p1['atom']:.0f}/200")
