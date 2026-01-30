import streamlit as st
import random
import time

# --- 戦域設定 ---
st.set_page_config(page_title="DEUS: Tactical Console", layout="wide", initial_sidebar_state="collapsed")

# カスタムCSS：アニメーションとレイアウト調整
st.markdown("""
    <style>
    .main { background-color: #0e1111; color: #d3d3d3; font-family: 'Courier New', monospace; }
    .stButton>button { 
        width: 100%; border: 1px solid #4a4a4a; background-color: #1a1a1a; color: #00ff00;
        height: 3em; border-radius: 0px; font-weight: bold; font-size: 0.8rem;
    }
    /* 戦況表示エリア（右側演出） */
    .battle-scene {
        background-color: #000; border: 1px solid #00ff00; height: 180px;
        position: relative; overflow: hidden; display: flex; align-items: center; justify-content: center;
        font-size: 3rem; margin-bottom: 10px;
    }
    @keyframes move-unit {
        0% { transform: translateX(-150%); opacity: 0; }
        50% { opacity: 1; }
        100% { transform: translateX(150%); opacity: 0; }
    }
    .unit-anim { animation: move-unit 1.5s ease-in-out; }
    .status-text { font-size: 0.7rem; color: #00ff00; text-transform: uppercase; }
    </style>
    """, unsafe_allow_html=True)

if 'state' not in st.session_state:
    st.session_state.state = {
        "p1": {"territory": 100.0, "military": 0.0, "colony": 20.0, "shield": False, "nuke_point": 0},
        "p2": {"territory": 300.0, "military": 100.0, "colony": 50.0, "shield": False},
        "turn": 1, "player_ap": 2, "logs": ["SYSTEM: 難易度を選択して開始せよ。"],
        "wmd_charging": False, "ai_awakened": False, "difficulty": None,
        "last_action_icon": "📡", "last_action_name": "WAITING"
    }

s = st.session_state.state
p1, p2 = s["p1"], s["p2"]

# --- ロジック関数 (既存ロジックを継承) ---
def apply_damage_to_player(dmg, is_wmd=False):
    if p1["shield"]: dmg *= 0.6
    if p1["colony"] > 0:
        shield_amt = min(p1["colony"], dmg)
        p1["colony"] -= shield_amt
        dmg -= shield_amt
    if dmg > 0: p1["territory"] = max(0, p1["territory"] - dmg)

def ai_logic():
    actions = 1 if s["difficulty"] == "小国 (Easy)" else 2
    if s["difficulty"] == "大国 (Normal)" and not s["ai_awakened"]:
        if p1["military"] > 80 or p2["territory"] < 150: s["ai_awakened"] = True
    for _ in range(actions):
        if p2["territory"] <= 0: break
        if s["wmd_charging"]:
            apply_damage_to_player(p1["territory"] * 0.5, True)
            s["wmd_charging"] = False
        else:
            if random.random() < (0.4 if s["ai_awakened"] else 0.1): s["wmd_charging"] = True
            else: apply_damage_to_player(p2["military"] * 0.25 * (1.6 if s["ai_awakened"] else 0.8))

def player_step(cmd):
    # アクションに応じたマーク（ユニット）の設定
    if cmd == "DEVELOP":
        p1["military"] += 25.0; p1["nuke_point"] += 20
        s["last_action_icon"], s["last_action_name"] = "🏗️", "DEVELOPING"
    elif cmd == "DEFEND":
        p1["shield"] = True
        s["last_action_icon"], s["last_action_name"] = "🛡️", "DEFENDING"
    elif cmd == "MARCH":
        dmg = (p1["military"] * 0.5) + (p1["colony"] * 0.6)
        p2["territory"] -= dmg
        s["last_action_icon"], s["last_action_name"] = "🚜", "MARCHING" # 戦車
    elif cmd == "OCCUPY":
        if p1["military"] >= 20:
            p1["military"] -= 20; steal = max(p2["territory"] * 0.2, 40.0)
            p2["territory"] -= steal; p1["colony"] += steal
            s["last_action_icon"], s["last_action_name"] = "🚁", "OCCUPYING" # ヘリ/ミサイル
    elif cmd == "NUKE":
        p2["territory"] *= 0.2; p1["nuke_point"] = 0
        s["last_action_icon"], s["last_action_name"] = "🚀", "NUCLEAR STRIKE" # ミサイル

    s["player_ap"] -= 1
    if s["player_ap"] <= 0:
        ai_logic(); s["player_ap"], s["turn"], p1["shield"] = 2, s["turn"] + 1, False

# --- メインインターフェース ---
if s["difficulty"] is None:
    st.subheader("🌐 難易度を選択してください")
    cols = st.columns(3)
    if cols[0].button("小国 (Easy)"): s["difficulty"] = "小国 (Easy)"; p2["territory"], p2["military"] = 150.0, 30.0; st.rerun()
    if cols[1].button("大国 (Normal)"): s["difficulty"] = "大国 (Normal)"; st.rerun()
    if cols[2].button("超大国 (Hard)"): s["difficulty"] = "超大国 (Hard)"; p2["territory"], p2["military"], s["ai_awakened"] = 500.0, 100.0, True; st.rerun()
else:
    # スマホでも並ぶようにカラムを分割
    col_info, col_visual = st.columns([1.2, 1])

    with col_info:
        st.caption(f"TURN {s['turn']} | {s['difficulty']}")
        st.write(f"🟥 AI: {p2['territory']:.1f}")
        st.progress(max(0.0, min(p2['territory']/500, 1.0)))
        if s["wmd_charging"]: st.error("🚨 WMD DETECTED")
        
        st.write(f"🟦 YOU: {p1['territory']:.1f}")
        st.progress(max(0.0, min(p1['territory']/200, 1.0)))

    with col_visual:
        # 右側の視覚演出エリア：マークが飛び交う
        st.markdown(f"""
            <div class="status-text">{s['last_action_name']}</div>
            <div class="battle-scene">
                <div class="unit-anim">{s['last_action_icon']}</div>
            </div>
            """, unsafe_allow_html=True)

    # ステータス・操作エリア
    st.divider()
    m1, m2, m3 = st.columns(3)
    m1.metric("COLONY", f"{p1['colony']:.0f}")
    m2.metric("MILIT", f"{p1['military']:.0f}/100")
    m3.metric("AP", f"{s['player_ap']}")

    if p1["territory"] <= 0 or p2["territory"] <= 0:
        if p1["territory"] <= 0: st.error("COMMANDER, WE LOST.")
        else: st.success("COMMANDER, VICTORY IS OURS.")
        if st.button("REBOOT"): st.session_state.clear(); st.rerun()
    else:
        if p1["nuke_point"] >= 200:
            if st.button("☢️ EXECUTE JUDGEMENT", type="primary"): player_step("NUKE"); st.rerun()
        
        c = st.columns(2)
        if c[0].button("🛠 開発 (DEV)"): player_step("DEVELOP"); st.rerun()
        if c[1].button("🛡 防衛 (DEF)"): player_step("DEFEND"); st.rerun()
        if c[0].button("🚜 進軍 (ATK)"): player_step("MARCH"); st.rerun()
        if c[1].button("🚁 占領 (OCC)"): player_step("OCCUPY"); st.rerun()

    st.caption("LOGS")
    for log in s["logs"][:2]: st.text(log)
