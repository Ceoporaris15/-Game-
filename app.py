import streamlit as st
import random

st.set_page_config(page_title="DEUS: Overload War", layout="wide")
st.title("⚔️ 国家間Game：100の衝撃と占領の盾")

if 'state' not in st.session_state:
    st.session_state.state = {
        "p1": {"territory": 100.0, "military": 0.0, "colony": 20.0, "shield": False, "nuke_point": 0},
        "p2": {"territory": 300.0, "military": 100.0, "colony": 50.0, "shield": False},
        "turn": 1,
        "logs": ["SYSTEM: 占領地を盾にせよ。軍事力100でバーストが発動する。"],
        "wmd_charging": False,
        "ai_awakened": False 
    }

s = st.session_state.state
p1, p2 = s["p1"], s["p2"]

# --- ダメージ処理（占領地が肩代わり） ---
def apply_damage_to_player(dmg):
    if p1["colony"] > 0:
        shield_amt = min(p1["colony"], dmg)
        p1["colony"] -= shield_amt
        dmg -= shield_amt
        if shield_amt > 0:
            s["logs"].insert(0, f"🛡️ 占領地が身代わりになり {shield_amt:.1f} のダメージを吸収！")
    
    if dmg > 0:
        p1["territory"] = max(0, p1["territory"] - dmg)
        s["logs"].insert(0, f"💥 本国領土に {dmg:.1f} の直接ダメージ！")

# --- AI：圧倒的物量と即時復旧 ---
def ai_logic_overload(player_last_action):
    # 覚醒判定
    if not s["ai_awakened"] and (p1["military"] > 80 or p2["territory"] < 200 or player_last_action == "NUKE"):
        s["ai_awakened"] = True
        s["logs"].insert(0, "🔴 WARNING: DEUS覚醒。軍事エネルギーを常時最大値に固定。")

    for i in range(2):
        if p2["territory"] <= 0: break
        
        # AIは常に高い軍事力を維持（即チャージ）
        if p2["military"] < 100:
            p2["military"] = 100
            s["logs"].insert(0, "🔴 AI: 軍事エネルギーを即座に再充填。")

        # 1. WMD発射判定
        if s["wmd_charging"]:
            if player_last_action == "ATTACK" and random.random() < 0.4:
                s["logs"].insert(0, "✅ SYSTEM: 阻止成功！")
                s["wmd_charging"] = False
            else:
                apply_damage_to_player(p1["territory"] * 0.5)
                s["wmd_charging"] = False
            continue

        # 2. 戦略行動
        if i == 0 and player_last_action == "ATTACK" and not p2["shield"]:
            p2["shield"] = True
            s["logs"].insert(0, "🔴 AI: 防御展開。")
        elif not s["wmd_charging"] and s["ai_awakened"] and random.random() < 0.2:
            s["wmd_charging"] = True
            s["logs"].insert(0, "⚠️ ALERT: DEUSがWMDをチャージ中。")
        else:
            power_mult = 1.5 if s["ai_awakened"] else 0.8
            dmg = p2["military"] * 0.25 * power_mult
            if p1["shield"]: dmg *= 0.1
            apply_damage_to_player(dmg)

def player_step(cmd):
    # 軍事力バースト判定
    burst_happened = False
    
    if cmd == "MILITARY": 
        p1["military"] += 25.0 # チャージ量アップ
        p1["nuke_point"] += 15 
        s["logs"].insert(0, f"🔵 Player: エネルギー充填（軍事:{p1['military']}）")
    elif cmd == "DEFEND": 
        p1["shield"] = True
        s["logs"].insert(0, "🔵 Player: 本国防衛。")
    elif cmd == "ATTACK":
        dmg = (p1["military"] * 0.4) + 10
        if p2["shield"]: 
            p2["shield"] = False
            s["logs"].insert(0, "🔵 Player: 攻撃（盾粉砕）")
        else: 
            p2["territory"] -= dmg
            s["logs"].insert(0, f"🔵 Player: 通常攻撃（AI領土-{dmg:.1f}）")
    elif cmd == "OCCUPY":
        steal = min(p2["territory"] * 0.15, 30.0)
        p2["territory"] -= steal
        p1["colony"] += steal # これが盾になる
        s["logs"].insert(0, f"🔵 Player: 占領成功！盾（占領地）を {steal:.1f} 確保。")
    elif cmd == "SPY":
        if random.random() < 0.1:
            p2["territory"] *= 0.5
            s["logs"].insert(0, "🕵️‍♂️ SPY SUCCESS!! AI領土を半減。")
        else:
            s["logs"].insert(0, "🕵️‍♂️ SPY FAIL: 潜入失敗。")
    elif cmd == "NUKE":
        p2["territory"] *= 0.2
        p1["nuke_point"] = 0
        s["logs"].insert(0, "🚀 Player: 核兵器発射！！世界を震撼させました。")

    # 軍事力100で自動バースト
    if p1["military"] >= 100:
        burst_dmg = 80.0
        p2["territory"] -= burst_dmg
        p1["military"] = 0
        burst_happened = True
        s["logs"].insert(0, f"💥 FULL CHARGE BURST!! AIに {burst_dmg} の致命打を与え、軍事力リセット。")
    
    ai_logic_overload(cmd)
    s["turn"] += 1
    p1["shield"] = False

# --- UI ---
col1, col2 = st.columns(2)
with col1:
    st.header(f"Turn: {s['turn']}")
    st.subheader("🟦 Player (1 Action)")
    st.metric("本国領土 (Life)", f"{p1['territory']:.1f}")
    st.metric("占領地 (Shield)", f"{p1['colony']:.1f}", delta="身代わりHP")
    st.write(f"軍事エネルギー: {p1['military']}/100")
    st.progress(min(p1['military']/100, 1.0))
    st.caption(f"核開発Pt: {p1['nuke_point']}/100")

with col2:
    status = "👿 AWAKENED" if s["ai_awakened"] else "😴 SLEEPING"
    st.subheader(f"🟥 DEUS ({status})")
    st.metric("AI領土", f"{p2['territory']:.1f}")
    st.metric("AI軍事力", f"{p2['military']:.1f}")
    if s["wmd_charging"]: st.error("🚨 WMDチャージ中")

st.divider()

if p1["territory"] <= 0:
    st.error("【敗北】本国が陥落しました。")
    if st.button("再始動"): st.session_state.clear(); st.rerun()
elif p2["territory"] <= 0:
    st.success("【完全勝利】超大国を滅ぼしました！")
    if st.button("再始動"): st.session_state.clear(); st.rerun()
else:
    c = st.columns(5)
    if c[0].button("チャージ(軍拡)"): player_step("MILITARY"); st.rerun()
    if c[1].button("防衛"): player_step("DEFEND"); st.rerun()
    if c[2].button("通常攻撃"): player_step("ATTACK"); st.rerun()
    if c[3].button("占領(盾確保)"): player_step("OCCUPY"); st.rerun()
    if c[4].button("スパイ"): player_step("SPY"); st.rerun()
    
    if p1["nuke_point"] >= 100:
        st.button("🚀 核兵器発射", type="primary", use_container_width=True, on_click=player_step, args=("NUKE",))

st.write("---")
for log in s["logs"][:8]: st.text(log)
