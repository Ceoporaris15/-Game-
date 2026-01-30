import streamlit as st
import random
import time

# --- 戦域設定 ---
st.set_page_config(page_title="DEUS: Tactical Console", layout="wide", initial_sidebar_state="collapsed")

# カスタムCSS：マリオ風アニメと核使用時の円周警告演出
st.markdown("""
    <style>
    .main { background-color: #0e1111; color: #d3d3d3; font-family: 'Courier New', monospace; }
    .stButton>button { 
        width: 100%; border: 1px solid #4a4a4a; background-color: #1a1a1a; color: #00ff00;
        height: 3em; border-radius: 0px; font-weight: bold; font-size: 0.8rem;
    }
    
    /* 演出モニター */
    .battle-scene {
        background-color: #000; border: 2px solid #333; height: 150px;
        position: relative; overflow: hidden; margin-bottom: 10px;
        background-image: linear-gradient(to bottom, #000 85%, #222 85%);
    }

    /* 核使用時の円周警告アニメーション */
    @keyframes circle-pulse {
        0% { transform: translate(-50%, -50%) scale(0.1); opacity: 1; border: 10px solid #ff0000; }
        100% { transform: translate(-50%, -50%) scale(2); opacity: 0; border: 2px solid #ff0000; }
    }
    .nuke-circle {
        position: absolute; top: 50%; left: 50%;
        width: 100px; height: 100px; border-radius: 50%;
        animation: circle-pulse 0.8s infinite;
        z-index: 10;
    }

    /* マリオ風アニメ */
    @keyframes mario-march {
        0% { left: -10%; bottom: 10px; }
        25% { bottom: 40px; }
        50% { bottom: 10px; }
        75% { bottom: 40px; }
        100% { left: 110%; bottom: 10px; }
    }
    .unit-mario { position: absolute; font-size: 3rem; animation: mario-march 1s linear; }
    
    .status-text { font-size: 0.7rem; color: #00ff00; text-transform: uppercase; padding: 2px 10px; }
    </style>
    """, unsafe_allow_html=True)

# --- 画像アセット ---
IMG_NUKE = "https://images.unsplash.com/photo-1515285761066-608677e5d263?auto=format&fit=crop&q=80&w=800"

if 'state' not in st.session_state:
    st.session_state.state = {
        "p1": {"territory": 100.0, "military": 0.0, "colony": 20.0, "shield": False, "nuke_point": 0},
        "p2": {"territory": 300.0, "military": 100.0, "colony": 50.0},
        "turn": 1, "player_ap": 2, "logs": ["SYSTEM: 難易度を選択せよ。"],
        "wmd_charging": False, "ai_awakened": False, "difficulty": None,
        "last_icon": "📡", "last_name": "STANDBY", "is_nuke_effect": False
    }

s = st.session_state.state
p1, p2 = s["p1"], s["p2"]

# --- ロジック ---
def apply_damage_to_player(dmg):
    if p1["shield"]: dmg *= 0.6
    if p1["colony"] > 0:
        shield_amt = min(p1["colony"], dmg)
        p1["colony"] -= shield_amt; dmg -= shield_amt
    if dmg > 0: p1["territory"] = max(0, p1["territory"] - dmg)

def ai_logic():
    actions = 1 if s["difficulty"] == "小国 (Easy)" else 2
    for _ in range(actions):
        if p2["territory"] <= 0: break
        if s["wmd_charging"]:
            apply_damage_to_player(p1["territory"] * 0.5); s["wmd_charging"] = False
        else:
            if random.random() < (0.4 if s["ai_awakened"] else 0.1): s["wmd_charging"] = True
            else: apply_damage_to_player(p2["military"] * 0.2)

def player_step(cmd):
    s["is_nuke_effect"] = False
    if cmd == "DEVELOP":
        p1["military"] += 25.0; p1["nuke_point"] += 20
        s["last_icon"], s["last_name"] = "🛠️", "UPGRADING"
    elif cmd == "DEFEND":
        p1["shield"] = True
        s["last_icon"], s["last_name"] = "🛡️", "SHIELD ON"
    elif cmd == "MARCH":
        p2["territory"] -= (p1["military"] * 0.5) + (p1["colony"] * 0.6)
        s["last_icon"], s["last_name"] = "🚜", "ATTACK"
    elif cmd == "OCCUPY":
        if p1["military"] >= 20:
            p1["military"] -= 20; stl = max(p2["territory"] * 0.2, 40.0)
            p2["territory"] -= stl; p1["colony"] += stl
            s["last_icon"], s["last_name"] = "🚩", "OCCUPY"
    elif cmd == "NUKE":
        p2["territory"] *= 0.2; p1["nuke_point"] = 0
        s["last_icon"], s["last_name"] = "☢️", "CRITICAL"
        s["is_nuke_effect"] = True # 核演出フラグON

    s["player_ap"] -= 1
    if s["player_ap"] <= 0:
        ai_logic(); s["player_ap"], s["turn"], p1["shield"] = 2, s["turn"] + 1, False

# --- UI ---
if s["difficulty"] is None:
    st.subheader("🌐 SELECT DIFFICULTY")
    cols = st.columns(3)
    if cols[0].button("EASY"): s["difficulty"] = "小国 (Easy)"; p2["territory"] = 150.0; st.rerun()
    if cols[1].button("NORMAL"): s["difficulty"] = "大国 (Normal)"; st.rerun()
    if cols[2].button("HARD"): s["difficulty"] = "超大国 (Hard)"; s["ai_awakened"] = True; st.rerun()
else:
    col_info, col_visual = st.columns([1.2, 1])
    with col_info:
        st.write(f"🟥 AI: {p2['territory']:.1f}")
        st.progress(max(0.0, min(p2['territory']/500, 1.0)))
        st.write(f"🟦 YOU: {p1['territory']:.1f}")
        st.progress(max(0.0, min(p1['territory']/200, 1.0)))

    with col_visual:
        # 演出モニター
        st.markdown(f'<div class="status-text">SIGNAL: {s["last_name"]}</div>', unsafe_allow_html=True)
        if s["is_nuke_effect"]:
            # 核使用時の円周演出 + キノコ雲
            st.markdown('<div class="battle-scene"><div class="nuke-circle"></div><div class="nuke-circle" style="animation-delay:0.4s"></div></div>', unsafe_allow_html=True)
            st.image(IMG_NUKE, use_container_width=True)
        else:
            # 通常のマリオ風アニメ
            st.markdown(f'<div class="battle-scene"><div class="unit-mario">{s["last_icon"]}</div></div>', unsafe_allow_html=True)

    st.divider()
    m1, m2, m3 = st.columns(3)
    m1.metric("COLONY", f"{p1['colony']:.0f}")
    m2.metric("MILIT", f"{p1['military']:.0f}")
    m3.metric("AP", f"{s['player_ap']}")

    if p1["territory"] <= 0 or p2["territory"] <= 0:
        st.write("### MISSION OVER")
        if st.button("REBOOT"): st.session_state.clear(); st.rerun()
    else:
        if p1["nuke_point"] >= 200:
            if st.button("🚀 EXECUTE FINAL JUDGEMENT", type="primary"): player_step("NUKE"); st.rerun()
        c = st.columns(2)
        if c[0].button("🛠 開発"): player_step("DEVELOP"); st.rerun()
        if c[1].button("🛡 防衛"): player_step("DEFEND"); st.rerun()
        if c[0].button("⚔️ 進軍"): player_step("MARCH"); st.rerun()
        if c[1].button("🚩 占領"): player_step("OCCUPY"); st.rerun()
