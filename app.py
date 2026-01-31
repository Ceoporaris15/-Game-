import streamlit as st
import random

# --- 最終戦術ダッシュボード：陣営選択版 ---
st.set_page_config(page_title="DEUS: IDEOLOGY", layout="centered")

st.markdown("""
    <style>
    html, body, [data-testid="stAppViewContainer"] {
        overflow: hidden; background-color: #000; color: #FFF;
    }
    .enemy-banner {
        background-color: #300; border: 2px solid #F00;
        padding: 5px; text-align: center; margin: -50px -15px 10px -15px;
    }
    .enemy-text { color: #F00; font-weight: bold; font-size: 1.1rem; }
    .status-row {
        display: flex; justify-content: space-around;
        background: #111; border: 1px solid #d4af37;
        padding: 5px; margin-bottom: 5px;
    }
    .stat-val { color: #d4af37; font-weight: bold; }
    div[data-testid="column"] button {
        height: 42px !important; font-size: 0.7rem !important;
        font-weight: 900 !important; background-color: #222 !important;
        color: #FFF !important; border: 1px solid #d4af37 !important;
    }
    .log-box {
        background: #050505; border-left: 3px solid #d4af37;
        padding: 5px; height: 100px; font-size: 0.75rem; color: #EEE; overflow: hidden;
    }
    </style>
    """, unsafe_allow_html=True)

if 'state' not in st.session_state:
    st.session_state.state = {
        "p1": {"territory": 100.0, "military": 0.0, "colony": 20.0, "nuke_point": 0, "shield_active": False},
        "p2": {"territory": 300.0, "military": 100.0, "colony": 50.0},
        "turn": 1, "logs": ["陣営を選択してください。"],
        "player_ap": 2, "max_ap": 2, "wmd_charging": False,
        "difficulty": None, "faction": None
    }

s = st.session_state.state
p1, p2 = s["p1"], s["p2"]

# --- 戦術演算 ---
def apply_damage_to_player(dmg):
    # 防御システム：陣営による下方修正
    success_rate = 0.3
    if s["faction"] == "枢軸国": success_rate = 0.15 # 枢軸は防御がさらに困難
    
    if p1["shield_active"]:
        if random.random() < success_rate:
            dmg = max(0, dmg - 40); s["logs"].insert(0, "🛡️ 防衛成功")
        else: s["logs"].insert(0, "❌ 防衛失敗")
    
    if p1["colony"] > 0:
        shield_amt = min(p1["colony"], dmg)
        p1["colony"] -= shield_amt; dmg -= shield_amt
    if dmg > 0: p1["territory"] = max(0, p1["territory"] - dmg)
    s["logs"].insert(0, f"💥 本国被害: -{dmg:.1f}")

def ai_logic():
    actions = 1 if s["difficulty"] == "小国" else (2 if s["difficulty"] == "大国" else 6)
    for _ in range(actions):
        if p2["territory"] <= 0: break
        choice = random.random()
        if choice < 0.25 and p1["nuke_point"] > 30:
            p1["nuke_point"] = max(0, p1["nuke_point"] - 50); s["logs"].insert(0, "🕵️ DEUS工作: 核回路妨害")
            continue
        if s["wmd_charging"]:
            nuke_dmg = p1["territory"] * (0.95 if s["difficulty"] == "超大国" else 0.5)
            apply_damage_to_player(nuke_dmg); s["wmd_charging"] = False
        else:
            if random.random() < (0.7 if s["difficulty"] == "超大国" else 0.2):
                s["wmd_charging"] = True; s["logs"].insert(0, "🚨 DEUS: 核充填開始")
            else:
                p2_power = 2.5 if s["difficulty"] == "超大国" else 1.0
                apply_damage_to_player(p2["military"] * 0.2 * p2_power)

def player_step(cmd):
    # 陣営補正係数
    expand_mul = 2.0 if s["faction"] == "社会主義国" else 1.0
    march_mul = 2.0 if s["faction"] in ["枢軸国", "社会主義国"] else 1.0
    nuke_mul = 2.0 if s["faction"] == "連合国" else 1.0
    spy_success_base = 0.25
    if s["faction"] == "社会主義国": spy_success_base = 0.5
    if s["faction"] == "連合国": spy_success_base = 0.1 # 連合は裏切り（失敗）が多い

    if cmd == "EXPAND":
        p1["military"] += 25.0 * expand_mul
        p1["nuke_point"] += 20 * nuke_mul
        s["logs"].insert(0, f"🛠 軍拡: 軍事+{25*expand_mul}")
    elif cmd == "DEFEND":
        p1["shield_active"] = True; s["logs"].insert(0, "🛡 防衛態勢")
    elif cmd == "MARCH":
        dmg = ((p1["military"] * 0.5) + (p1["colony"] * 0.6)) * march_mul
        if s["difficulty"] == "超大国": dmg *= 0.1
        p2["territory"] -= dmg; s["logs"].insert(0, f"⚔️ 進軍: -{dmg:.1f}")
    elif cmd == "OCCUPY":
        if p1["military"] >= 20:
            p1["military"] -= 20; steal = max(p2["territory"] * 0.2, 40.0)
            p2["territory"] -= steal; p1["colony"] += steal; s["logs"].insert(0, "🚩 占領成功")
    elif cmd == "SPY":
        if random.random() < spy_success_base:
            if s["wmd_charging"]: s["wmd_charging"] = False; s["logs"].insert(0, "🕵️ 潜入: 【成功】核停止")
            else: p1["nuke_point"] += 40; p2["territory"] -= 20; s["logs"].insert(0, "🕵️ 潜入: 【成功】奪取")
        else: s["logs"].insert(0, "🕵️ 潜入: 【失敗】裏切り/捕縛")
    elif cmd == "NUKE":
        p2["territory"] *= 0.15; p1["nuke_point"] = 0; s["logs"].insert(0, "☢️ 最終宣告執行")

    s["player_ap"] -= 1
    if s["player_ap"] <= 0:
        ai_logic(); s["player_ap"], s["turn"], p1["shield_active"] = s["max_ap"], s["turn"] + 1, False

# --- UI構築 ---
if s["difficulty"] is None:
    st.title("🚩 DEUS: CHOOSE DIFFICULTY")
    cols = st.columns(3)
    if cols[0].button("小国"): s["difficulty"] = "小国"; p2["territory"] = 150.0; st.rerun()
    if cols[1].button("大国"): s["difficulty"] = "大国"; st.rerun()
    if cols[2].button("超大国"): s["difficulty"] = "超大国"; p2["territory"] = 2500.0; st.rerun()
elif s["faction"] is None:
    st.title("🛡️ CHOOSE FACTION")
    if st.button("連合国 (核開発2倍 / スパイ低確率)"):
        s["faction"] = "連合国"; st.rerun()
    if st.button("枢軸国 (進軍2倍 / 防御下方修正)"):
        s["faction"] = "枢軸国"; st.rerun()
    if st.button("社会主義国 (全能力2倍 / ターン行動1回)"):
        s["faction"] = "社会主義国"; s["player_ap"] = 1; s["max_ap"] = 1; st.rerun()
else:
    st.markdown(f'<div class="enemy-banner"><span class="enemy-text">DEUS: {p2["territory"]:.0f}pts</span></div>', unsafe_allow_html=True)
    st.markdown(f'<div class="status-row"><div>{s["faction"]} | 本国: <span class="stat-val">{p1["territory"]:.0f}</span></div><div>緩衝: <span class="stat-val">{p1["colony"]:.0f}</span></div></div>', unsafe_allow_html=True)
    st.progress(min(p1['nuke_point']/200.0, 1.0))

    if p1["territory"] <= 0 or p2["territory"] <= 0:
        st.write("### 作戦完了: " + ("勝利" if p2["territory"] <= 0 else "敗北"))
        if st.button("REBOOT"): st.session_state.clear(); st.rerun()
    else:
        st.write(f"**T-{s['turn']} | AP: {s['player_ap']}**")
        if p1["nuke_point"] >= 200:
            if st.button("☢️ 最終宣告執行", type="primary", use_container_width=True): player_step("NUKE"); st.rerun()
        cols = st.columns(5)
        if cols[0].button("🛠軍拡"): player_step("EXPAND"); st.rerun()
        if cols[1].button("🛡防衛"): player_step("DEFEND"); st.rerun()
        if cols[2].button("⚔️進軍"): player_step("MARCH"); st.rerun()
        if cols[3].button("🚩占領"): player_step("OCCUPY"); st.rerun()
        if cols[4].button("🕵️潜入"): player_step("SPY"); st.rerun()
    st.write("---")
    log_html = "".join([f'<div>{log}</div>' for log in s["logs"][:4]])
    st.markdown(f'<div class="log-box">{log_html}</div>', unsafe_allow_html=True)
