import streamlit as st
import random
import time

# --- 戦域設定 ---
st.set_page_config(page_title="DEUS: Tactical Console", layout="wide", initial_sidebar_state="collapsed")

# カスタムCSS：マリオのような動き（放物線ジャンプやスライド）を実装
st.markdown("""
    <style>
    .main { background-color: #0e1111; color: #d3d3d3; font-family: 'Courier New', monospace; }
    .stButton>button { 
        width: 100%; border: 1px solid #4a4a4a; background-color: #1a1a1a; color: #00ff00;
        height: 3em; border-radius: 0px; font-weight: bold; font-size: 0.8rem;
    }
    /* 演出モニター：マリオ風アニメーション */
    .battle-scene {
        background-color: #000; border: 2px solid #333; height: 150px;
        position: relative; overflow: hidden; margin-bottom: 10px;
        background-image: linear-gradient(to bottom, #000 80%, #222 80%); /* 地面風のライン */
    }
    
    @keyframes mario-march {
        0% { left: -10%; bottom: 10px; }
        25% { bottom: 50px; } /* ジャンプ */
        50% { bottom: 10px; }
        75% { bottom: 50px; } /* ジャンプ */
        100% { left: 110%; bottom: 10px; }
    }
    
    @keyframes mario-nuke {
        0% { top: -20%; left: 50%; transform: translateX(-50%); }
        100% { top: 60%; left: 50%; transform: translateX(-50%); }
    }

    .unit-mario { 
        position: absolute; font-size: 3rem; 
        animation: mario-march 1.2s linear; 
    }
    .unit-drop { 
        position: absolute; font-size: 4rem; 
        animation: mario-nuke 0.8s ease-in; 
    }
    
    .status-text { font-size: 0.7rem; color: #00ff00; text-transform: uppercase; padding: 2px 10px; }
    </style>
    """, unsafe_allow_html=True)

if 'state' not in st.session_state:
    st.session_state.state = {
        "p1": {"territory": 100.0, "military": 0.0, "colony": 20.0, "shield": False, "nuke_point": 0},
        "p2": {"territory": 300.0, "military": 100.0, "colony": 50.0, "shield": False},
        "turn": 1, "player_ap": 2, "logs": ["SYSTEM: 難易度を選択して開始せよ。"],
        "wmd_charging": False, "ai_awakened": False, "difficulty": None,
        "anim_type": "march", "last_icon": "🛰️", "last_name": "STANDBY"
    }

s = st.session_state.state
p1, p2 = s["p1"], s["p2"]

# --- ロジック関数 (変更なし) ---
def apply_damage_to_player(dmg):
    if p1["shield"]: dmg *= 0.6
    if p1["colony"] > 0:
        shield_amt = min(p1["colony"], dmg)
        p1["colony"] -= shield_amt
        dmg -= shield_amt
    if dmg > 0: p1["territory"] = max(0, p1["territory"] - dmg)

def ai_logic():
    actions = 1 if s["difficulty"] == "小国 (Easy)" else 2
    for _ in range(actions):
        if p2["territory"] <= 0: break
        if s["wmd_charging"]:
            apply_damage_to_player(p1["territory"] * 0.5); s["wmd_charging"] = False
        else:
            if random.random() < (0.4 if s["ai_awakened"] else 0.1): s["wmd_charging"] = True
            else: apply_damage_to_player(p2["military"] * 0.2 * (1.5 if s["ai_awakened"] else 1.0))

def player_step(cmd):
    s["anim_type"] = "march" # 基本は横移動
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
        s["last_icon"], s["last_name"] = "🚀", "DROP"
        s["anim_type"] = "drop" # 核は上から降る

    s["player_ap"] -= 1
    if s["player_ap"] <= 0:
        ai_logic(); s["player_ap"], s["turn"], p1["shield"] = 2, s["turn"] + 1, False

# --- メインインターフェース ---
if s["difficulty"] is None:
    st.subheader("🌐 SELECT DIFFICULTY")
    cols = st.columns(3)
    if cols[0].button("EASY"): s["difficulty"] = "小国 (Easy)"; p2["territory"] = 150.0; st.rerun()
    if cols[1].button("NORMAL"): s["difficulty"] = "大国 (Normal)"; st.rerun()
    if cols[2].button("HARD"): s["difficulty"] = "超大国 (Hard)"; s["ai_awakened"] = True; st.rerun()
else:
    # 既存画面レイアウトを維持
    col_info, col_visual = st.columns([1.2, 1])

    with col_info:
        st.caption(f"TURN {s['turn']} | {s['difficulty']}")
        st.write(f"🟥 AI: {p2['territory']:.1f}")
        st.progress(max(0.0, min(p2['territory']/500, 1.0)))
        st.write(f"🟦 YOU: {p1['territory']:.1f}")
        st.progress(max(0.0, min(p1['territory']/200, 1.0)))

    with col_visual:
        # マリオ風アニメーションモニター
        anim_class = "unit-mario" if s["anim_type"] == "march" else "unit-drop"
        st.markdown(f"""
            <div class="status-text">SIGNAL: {s['last_name']}</div>
            <div class="battle-scene">
                <div class="{anim_class}">{s['last_icon']}</div>
            </div>
            """, unsafe_allow_html=True)

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
            if st.button("🚀 EXECUTE JUDGEMENT", type="primary"): player_step("NUKE"); st.rerun()
        c = st.columns(2)
        if c[0].button("🛠 開発"): player_step("DEVELOP"); st.rerun()
        if c[1].button("🛡 防衛"): player_step("DEFEND"); st.rerun()
        if c[0].button("⚔️ 進軍"): player_step("MARCH"); st.rerun()
        if c[1].button("🚩 占領"): player_step("OCCUPY"); st.rerun()

    for log in s["logs"][:1]: st.caption(log)
