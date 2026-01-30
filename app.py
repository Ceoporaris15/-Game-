import streamlit as st
import random

# --- 戦域設定 ---
st.set_page_config(page_title="DEUS: Tactical Console", layout="wide", initial_sidebar_state="collapsed")

# カスタムCSS：レイアウト維持、アニメーションを完全に排除
st.markdown("""
    <style>
    .main { background-color: #0e1111; color: #d3d3d3; font-family: 'Courier New', monospace; }
    .stButton>button { 
        width: 100%; border: 1px solid #4a4a4a; background-color: #1a1a1a; color: #00ff00;
        height: 3em; border-radius: 0px; font-weight: bold; font-size: 0.8rem;
    }
    /* 演出モニター：静止表示用 */
    .battle-scene {
        background-color: #000; border: 2px solid #333; height: 150px;
        position: relative; display: flex; align-items: center; justify-content: center;
        margin-bottom: 10px;
    }
    /* 核兵器使用時のターゲットマーク（静止） */
    .nuke-target {
        width: 120px; height: 120px; border-radius: 50%;
        border: 4px double #ff0000; position: relative;
    }
    .nuke-target::before {
        content: ''; position: absolute; top: 50%; left: 0; width: 100%; height: 2px; background: #ff0000;
    }
    .nuke-target::after {
        content: ''; position: absolute; left: 50%; top: 0; width: 2px; height: 100%; background: #ff0000;
    }
    
    .status-text { font-size: 0.7rem; color: #00ff00; text-transform: uppercase; padding: 2px 10px; }
    .unit-icon-static { font-size: 4rem; }
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
        "last_icon": "📡", "last_name": "STANDBY", "is_nuke_active": False
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
    s["is_nuke_active"] = False
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
        s["is_nuke_active"] = True

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
        st.markdown(f'<div class="status-text">SIGNAL: {s["last_name"]}</div>', unsafe_allow_html=True)
        if s["is_nuke_active"]:
            # 核使用時：警告マークと画像を重ねず、並べて表示（またはエリア内表示）
            st.markdown('<div class="battle-scene"><div class="nuke-target"></div></div>', unsafe_allow_html=True)
            st.image(IMG_NUKE, use_container_width=True)
        else:
            # 通常：アイコンを静止表示
            st.markdown(f'<div class="battle-scene"><div class="unit-icon-static">{s["last_icon"]}</div></div>', unsafe_allow_html=True)

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

    for log in s["logs"][:1]: st.caption(log)
