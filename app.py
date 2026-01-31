import streamlit as st
import random

# --- 最終戦術ダッシュボード ---
st.set_page_config(page_title="DEUS: ARMS RACE", layout="centered")

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
    /* 軍拡ボタンの特殊強調 */
    div[data-testid="column"]:nth-child(1) button {
        background-color: #332b00 !important; border-color: #ffd700 !important;
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
        "turn": 1, "logs": ["軍拡指令を受信。国家を要塞化せよ。"],
        "player_ap": 2, "wmd_charging": False, "difficulty": None
    }

s = st.session_state.state
p1, p2 = s["p1"], s["p2"]

def apply_damage_to_player(dmg):
    # 防御（成功率30%）
    if p1["shield_active"]:
        if random.random() < 0.3:
            dmg = max(0, dmg - 40); s["logs"].insert(0, "🛡️ 防衛成功: 被害を一部相殺")
        else: s["logs"].insert(0, "❌ 防衛失敗: 直撃を受けた")
    
    # AIはまず占領地から削る
    if p1["colony"] > 0:
        shield_amt = min(p1["colony"], dmg)
        p1["colony"] -= shield_amt; dmg -= shield_amt
    if dmg > 0: p1["territory"] = max(0, p1["territory"] - dmg)
    s["logs"].insert(0, f"💥 本国被害: -{dmg:.1f}")

def ai_logic():
    # 超大国の圧倒的行動数
    actions = 1 if s["difficulty"] == "小国" else (2 if s["difficulty"] == "大国" else 6)
    for _ in range(actions):
        if p2["territory"] <= 0: break
        
        choice = random.random()
        # 1. AIのスパイ工作
        if choice < 0.25 and p1["nuke_point"] > 30:
            p1["nuke_point"] = max(0, p1["nuke_point"] - 50); s["logs"].insert(0, "🕵️ DEUS工作: 核回路をハック")
            continue
        
        # 2. AIの植民地支配 (超大国のみHP回復)
        if choice < 0.4 and s["difficulty"] == "超大国":
            p2["territory"] += 40; s["logs"].insert(0, "🏭 DEUS: 占領地を再編、領土修復")
            continue

        # 3. 攻撃
        if s["wmd_charging"]:
            nuke_dmg = p1["territory"] * (0.95 if s["difficulty"] == "超大国" else 0.5)
            apply_damage_to_player(nuke_dmg); s["wmd_charging"] = False
        else:
            if random.random() < (0.7 if s["difficulty"] == "超大国" else 0.2):
                s["wmd_charging"] = True; s["logs"].insert(0, "🚨 DEUS: 核充填を確認")
            else:
                p2_power = 2.5 if s["difficulty"] == "超大国" else 1.0
                apply_damage_to_player(p2["military"] * 0.2 * p2_power)

def player_step(cmd):
    if cmd == "EXPAND": # 旧開発
        p1["military"] += 25.0; p1["nuke_point"] += 20; s["logs"].insert(0, "🛠 軍拡: 総動員体制に移行")
    elif cmd == "DEFEND": p1["shield_active"] = True; s["logs"].insert(0, "🛡 防衛: 限定的迎撃態勢")
    elif cmd == "MARCH":
        dmg = (p1["military"] * 0.5) + (p1["colony"] * 0.6)
        if s["difficulty"] == "超大国": dmg *= 0.1 # 超大国にはほぼ無力
        p2["territory"] -= dmg; s["logs"].insert(0, f"⚔️ 進軍: 敵地を打撃 -{dmg:.1f}")
    elif cmd == "OCCUPY":
        if p1["military"] >= 20:
            p1["military"] -= 20; steal = max(p2["territory"] * 0.2, 40.0)
            p2["territory"] -= steal; p1["colony"] += steal; s["logs"].insert(0, "🚩 占領: 緩衝地帯を接収")
    elif cmd == "SPY":
        if random.random() < 0.25: # 1/4の成功率
            if s["wmd_charging"]:
                s["wmd_charging"] = False; s["logs"].insert(0, "🕵️ 潜入: 【成功】敵核を緊急停止")
            else:
                p1["nuke_point"] += 40; p2["territory"] -= 20; s["logs"].insert(0, "🕵️ 潜入: 【成功】技術奪取")
        else: s["logs"].insert(0, "🕵️ 潜入: 【失敗】工作員が消失")
    elif cmd == "NUKE":
        p2["territory"] *= 0.15; p1["nuke_point"] = 0; s["logs"].insert(0, "☢️ 最終宣告: 核執行")

    s["player_ap"] -= 1
    if s["player_ap"] <= 0:
        ai_logic(); s["player_ap"], s["turn"], p1["shield_active"] = 2, s["turn"] + 1, False

# --- UI表示 ---
if s["difficulty"] is None:
    st.title("🚩 ARMS RACE: COMMAND")
    if st.button("小国"): s["difficulty"] = "小国"; p2["territory"] = 150.0; st.rerun()
    if st.button("大国"): s["difficulty"] = "大国"; st.rerun()
    if st.button("超大国（絶望）"): s["difficulty"] = "超大国"; p2["territory"] = 2500.0; st.rerun()
else:
    st.markdown(f'<div class="enemy-banner"><span class="enemy-text">DEUS: {p2["territory"]:.0f}pts</span></div>', unsafe_allow_html=True)
    if s["wmd_charging"]: st.error("🚨 Strategic Weapon Armed")
    
    st.markdown(f'<div class="status-row"><div>本国: <span class="stat-val">{p1["territory"]:.0f}</span></div><div>緩衝: <span class="stat-val">{p1["colony"]:.0f}</span></div></div>', unsafe_allow_html=True)
    
    st.progress(min(p1['nuke_point']/200.0, 1.0))
    if p1["territory"] <= 0 or p2["territory"] <= 0:
        st.write("### 作戦完了: " + ("人類勝利" if p2["territory"] <= 0 else "国家崩壊"))
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
