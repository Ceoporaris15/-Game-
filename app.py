import streamlit as st
import random

# --- ページ設定とダークテーマCSS ---
st.set_page_config(page_title="STRATEGY G-DEUS", layout="centered")

st.markdown("""
    <style>
    /* 全体の背景とテキスト */
    .main { background-color: #0b0e14; color: #00ffcc; }
    h1, h2, h3 { color: #00ffcc !important; font-family: 'Courier New', monospace; }
    
    /* 敵（DEUS）のコンテナ */
    .enemy-box {
        border: 2px solid #ff4b4b; background: rgba(255, 75, 75, 0.05);
        padding: 15px; border-radius: 5px; margin-bottom: 20px;
    }
    
    /* プレイヤーのコンテナ */
    .player-box {
        border: 2px solid #00ffcc; background: rgba(0, 255, 204, 0.05);
        padding: 15px; border-radius: 5px;
    }

    /* 核ターゲット演出 */
    .nuke-overlay {
        text-align: center; border: 3px double #ff0000;
        padding: 20px; background: rgba(255, 0, 0, 0.2); margin-bottom: 10px;
    }
    .target-scope {
        width: 80px; height: 80px; border: 2px solid #ff0000;
        border-radius: 50%; margin: 0 auto; position: relative;
    }
    .target-scope::before { content: ''; position: absolute; top: 50%; left: -10%; width: 120%; height: 2px; background: #ff0000; }
    .target-scope::after { content: ''; position: absolute; left: 50%; top: -10%; width: 2px; height: 120%; background: #ff0000; }
    
    /* ログ */
    .stText { font-family: 'Consolas', monospace; font-size: 0.85rem; }
    </style>
    """, unsafe_allow_html=True)

# --- 画像アセット ---
IMG_NUKE = "https://images.unsplash.com/photo-1515285761066-608677e5d263?auto=format&fit=crop&q=80&w=800"

if 'state' not in st.session_state:
    st.session_state.state = {
        "p1": {"territory": 100.0, "military": 0.0, "colony": 20.0, "shield": False, "nuke_point": 0},
        "p2": {"territory": 300.0, "military": 100.0, "colony": 50.0, "shield": False},
        "turn": 1, "logs": ["CONNECTING TO SERVER..."],
        "player_ap": 2, "wmd_charging": False, "ai_awakened": False,
        "difficulty": None, "effect": None
    }

s = st.session_state.state
p1, p2 = s["p1"], s["p2"]

# --- ロジック（変更なし） ---
def apply_damage_to_player(dmg, is_wmd=False):
    if p1["shield"]: dmg *= 0.6
    if p1["colony"] > 0:
        shield_amt = min(p1["colony"], dmg)
        p1["colony"] -= shield_amt; dmg -= shield_amt
    if dmg > 0: p1["territory"] = max(0, p1["territory"] - dmg)
    icon = "☢️" if is_wmd else "💥"
    s["logs"].insert(0, f"{icon} WARNING: DAMAGE RECEIVED - {dmg:.1f}")

def ai_logic():
    actions = 1 if s["difficulty"] == "小国 (Easy)" else 2
    for _ in range(actions):
        if p2["territory"] <= 0: break
        if s["wmd_charging"]:
            apply_damage_to_player(p1["territory"] * 0.5, is_wmd=True)
            s["wmd_charging"] = False
        else:
            wmd_chance = 0.4 if s["ai_awakened"] else 0.1
            if random.random() < wmd_chance:
                s["wmd_charging"] = True
                s["logs"].insert(0, "⚠️ ALERT: AI WMD CHARGING...")
            else: apply_damage_to_player(p2["military"] * 0.2)

def player_step(cmd):
    s["effect"] = None
    if cmd == "DEVELOP":
        p1["military"] += 25.0; p1["nuke_point"] += 20
        s["logs"].insert(0, "🛠️ LOG: MILITARY UPGRADED.")
    elif cmd == "DEFEND":
        p1["shield"] = True
        s["logs"].insert(0, "🛡️ LOG: DEFENSIVE PROTOCOL ACTIVE.")
    elif cmd == "MARCH":
        dmg = (p1["military"] * 0.5) + (p1["colony"] * 0.6)
        p2["territory"] -= dmg
        s["logs"].insert(0, f"⚔️ LOG: OFFENSIVE ATTACK - {dmg:.1f}")
    elif cmd == "OCCUPY":
        if p1["military"] >= 20:
            p1["military"] -= 20; steal = max(p2["territory"] * 0.2, 40.0)
            p2["territory"] -= steal; p1["colony"] += steal
            s["logs"].insert(0, "🚩 LOG: TERRITORY CAPTURED.")
    elif cmd == "NUKE":
        s["effect"] = "NUKE"
        p2["territory"] *= 0.2; p1["nuke_point"] = 0
        s["logs"].insert(0, "☢️ CRITICAL: NUCLEAR LAUNCH CONFIRMED.")

    s["player_ap"] -= 1
    if s["player_ap"] <= 0:
        ai_logic(); s["player_ap"], s["turn"], p1["shield"] = 2, s["turn"] + 1, False

# --- UI レイアウト ---
if s["difficulty"] is None:
    st.title("G-DEUS COMMAND")
    st.write("難易度を選択して、DEUSシステムにログインしてください。")
    cols = st.columns(3)
    if cols[0].button("EASY"): s["difficulty"] = "小国 (Easy)"; p2["territory"] = 150.0; st.rerun()
    if cols[1].button("NORMAL"): s["difficulty"] = "大国 (Normal)"; st.rerun()
    if cols[2].button("HARD"): s["difficulty"] = "超大国 (Hard)"; s["ai_awakened"] = True; st.rerun()
else:
    # 敵エリア
    st.markdown(f'<div class="enemy-box">', unsafe_allow_html=True)
    st.write(f"### 🔴 ENEMY: DEUS V3 [{s['difficulty']}]")
    st.progress(max(0.0, min(p2['territory']/500, 1.0)))
    col_e1, col_e2 = st.columns(2)
    col_e1.metric("INTEGRITY", f"{p2['territory']:.1f}")
    if s["wmd_charging"]: col_e2.error("⚠️ WMD CHARGED")
    st.markdown('</div>', unsafe_allow_html=True)

    # 核兵器発射演出（ここだけ画像と円周）
    if s["effect"] == "NUKE":
        st.markdown('<div class="nuke-overlay"><div class="target-scope"></div><h2 style="color:red">TARGET ELIMINATING...</h2></div>', unsafe_allow_html=True)
        st.image(IMG_NUKE, use_container_width=True)

    # プレイヤーエリア
    st.markdown(f'<div class="player-box">', unsafe_allow_html=True)
    st.write(f"### 🔵 COMMANDER: PLAYER [TURN {s['turn']}]")
    col_p1, col_p2, col_p3 = st.columns(3)
    col_p1.metric("HOME", f"{p1['territory']:.1f}")
    col_p2.metric("SHIELD", f"{p1['colony']:.1f}")
    col_p3.metric("AP", s["player_ap"])

    # 軍事力と核のゲージ
    c_m1, c_m2 = st.columns(2)
    c_m1.caption(f"MILITARY POWER: {p1['military']}/100")
    c_m1.progress(p1['military']/100)
    c_m2.caption(f"NUCLEAR CHARGE: {p1['nuke_point']}/200")
    c_m2.progress(min(p1['nuke_point']/200, 1.0))
    st.markdown('</div>', unsafe_allow_html=True)

    # 操作
    st.write("")
    if p1["territory"] <= 0 or p2["territory"] <= 0:
        if p1["territory"] <= 0: st.error("SYSTEM FAILURE: COMMANDER DEFEATED.")
        else: st.success("MISSION COMPLETE: DEUS TERMINATED.")
        if st.button("REBOOT SYSTEM"): st.session_state.clear(); st.rerun()
    else:
        if p1["nuke_point"] >= 200:
            if st.button("☢️ LAUNCH NUCLEAR WEAPON", type="primary", use_container_width=True): player_step("NUKE"); st.rerun()
        
        btn_cols = st.columns(4)
        if btn_cols[0].button("UPGRADE"): player_step("DEVELOP"); st.rerun()
        if btn_cols[1].button("DEFEND"): player_step("DEFEND"); st.rerun()
        if btn_cols[2].button("ATTACK"): player_step("MARCH"); st.rerun()
        if btn_cols[3].button("ANNEX"): player_step("OCCUPY"); st.rerun()

    # ログ表示（下部に配置して雰囲気重視）
    st.write("---")
    st.markdown("**COMMAND LOGS:**")
    for log in s["logs"][:4]: st.caption(log)
