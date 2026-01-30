import streamlit as st
import random

st.set_page_config(page_title="DEUS: Nuclear Decision", layout="wide")
st.title("☮️ 国家間Game")

if 'state' not in st.session_state:
    st.session_state.state = {
        "p1": {"territory": 100.0, "military": 0.0, "colony": 20.0, "shield": False, "nuke_point": 0},
        "p2": {"territory": 300.0, "military": 100.0, "colony": 50.0, "shield": False},
        "turn": 1,
        "logs": ["SYSTEM: 核兵器の仕様：Player(80%消滅) / AI(50%消滅)"],
        "player_ap": 2, 
        "wmd_charging": False,
        "ai_awakened": False 
    }

s = st.session_state.state
p1, p2 = s["p1"], s["p2"]

# --- ダメージ処理（占領地が肩代わり） ---
def apply_damage_to_player(dmg, is_wmd=False):
    if p1["colony"] > 0:
        shield_amt = min(p1["colony"], dmg)
        p1["colony"] -= shield_amt
        dmg -= shield_amt
        if shield_amt > 0:
            s["logs"].insert(0, f"🛡️ 占領地が身代わりとなり {shield_amt:.1f} の被害を吸収。")
    
    if dmg > 0:
        p1["territory"] = max(0, p1["territory"] - dmg)
        type_str = "☢️ AI核攻撃" if is_wmd else "🚀 通常攻撃"
        s["logs"].insert(0, f"{type_str}: 本国領土が {dmg:.1f} の被害を受けました。")

# --- AIロジック (2回行動) ---
def ai_logic_dual(player_last_action):
    if not s["ai_awakened"] and (p1["military"] > 80 or p2["territory"] < 180 or p1["nuke_point"] > 150):
        s["ai_awakened"] = True
        s["logs"].insert(0, "🔴 WARNING: DEUSが生存圏の危機を検知。覚醒。")

    for _ in range(2):
        if p2["territory"] <= 0: break
        if p2["military"] < 100: p2["military"] = 100 

        # AIの核兵器(WMD)発射判定
        if s["wmd_charging"]:
            if player_last_action == "MARCH" and random.random() < 0.4:
                s["logs"].insert(0, "✅ SYSTEM: 進軍による強襲でWMD発射阻止に成功！")
                s["wmd_charging"] = False
            else:
                # AI核：プレイヤー領土の50%を破壊
                nuke_dmg = p1["territory"] * 0.5
                apply_damage_to_player(nuke_dmg, is_wmd=True)
                s["wmd_charging"] = False
            continue

        choice = random.random()
        if choice < 0.2 and not p2["shield"]:
            p2["shield"] = True
            s["logs"].insert(0, "🔴 AI: 防壁を展開。")
        elif choice < 0.3 and not s["wmd_charging"] and s["ai_awakened"]:
            s["wmd_charging"] = True
            s["logs"].insert(0, "⚠️ ALERT: AIがWMD(50%破壊)の充填を開始！")
        else:
            power_mult = 1.6 if s["ai_awakened"] else 0.8
            dmg = p2["military"] * 0.25 * power_mult
            if p1["shield"]: dmg *= 0.1
            apply_damage_to_player(dmg)

def player_step(cmd):
    if cmd == "DEVELOP": 
        p1["military"] += 25.0
        p1["nuke_point"] += 20 
        s["logs"].insert(0, f"🔵 Player: 開発（軍拡+25 / 核Pt+20）")
    elif cmd == "DEFEND": 
        p1["shield"] = True
        s["logs"].insert(0, "🔵 Player: 本国防衛態勢。")
    elif cmd == "MARCH":
        dmg = (p1["military"] * 0.5) + (p1["colony"] * 0.6)
        if p2["shield"]: 
            p2["shield"] = False
            s["logs"].insert(0, "🔵 Player: 進軍（AIのシールドを粉砕）")
        else: 
            p2["territory"] -= dmg
            s["logs"].insert(0, f"🔵 Player: 進軍（AI領土-{dmg:.1f}）")
    elif cmd == "OCCUPY":
        if p1["military"] >= 20:
            p1["military"] -= 20
            steal = max(p2["territory"] * 0.20, 40.0)
            p2["territory"] -= steal
            p1["colony"] += steal
            s["logs"].insert(0, f"🔵 Player: 占領（軍事-20 / 占領地+{steal:.1f}）")
        else:
            s["logs"].insert(0, "❌ SYSTEM: 軍事力不足。")
            return
    elif cmd == "SPY":
        if random.random() < 0.1:
            p2["territory"] *= 0.5
            s["logs"].insert(0, "🕵️‍♂️ SPY SUCCESS!! AI領土を半減。")
        else:
            s["logs"].insert(0, "🕵️‍♂️ SPY FAIL.")
    elif cmd == "NUKE":
        # プレイヤー核：AI領土の80%を破壊
        nuke_dmg = p2["territory"] * 0.8
        p2["territory"] -= nuke_dmg
        p1["nuke_point"] = 0
        s["logs"].insert(0, f"☢️ FINAL JUDGEMENT: 核兵器によりAI領土の80%({nuke_dmg:.1f})を消滅！")

    # バースト判定
    if p1["military"] >= 100:
        burst_dmg = 100.0 + (p1["colony"] * 0.3)
        p2["territory"] -= burst_dmg
        p1["military"] = 0
        s["logs"].insert(0, f"💥 BURST!! 総進軍で {burst_dmg:.1f} の致命打。")

    s["player_ap"] -= 1
    if s["player_ap"] <= 0:
        ai_logic_dual(cmd)
        s["player_ap"] = 2
        s["turn"] += 1
        p1["shield"] = False

# --- UI ---
col1, col2 = st.columns(2)
with col1:
    st.header(f"Turn: {s['turn']}")
    st.subheader(f"🟦 Player (AP: {s['player_ap']})")
    st.metric("本国領土", f"{p1['territory']:.1f}")
    st.metric("占領地 (盾)", f"{p1['colony']:.1f}")
    st.write(f"軍事: {p1['military']}/100 | 核Pt: {p1['nuke_point']}/200")
    st.progress(min(p1['nuke_point']/200, 1.0))

with col2:
    status = "👿 AWAKENED" if s["ai_awakened"] else "😴 SLEEPING"
    st.subheader(f"🟥 DEUS ({status})")
    st.metric("AI領土", f"{p2['territory']:.1f}")
    st.metric("AI軍事力", f"{p2['military']:.1f}")
    if s["wmd_charging"]: st.error("🚨 AIが核攻撃(50%)を準備中！")

st.divider()

if p1["territory"] <= 0:
    st.error("【敗北】本国は消滅しました。")
    if st.button("リスタート"): st.session_state.clear(); st.rerun()
elif p2["territory"] <= 0:
    st.success("【勝利】AI帝国の支配は終わりました。")
    if st.button("リスタート"): st.session_state.clear(); st.rerun()
else:
    # 200ポイントで核ボタン出現
    if p1["nuke_point"] >= 200:
        if st.button("☣ 核兵器発射 (AI領土80%壊滅)", type="primary", use_container_width=True):
            player_step("NUKE"); st.rerun()
    
    c = st.columns(5)
    if c[0].button("開発"): player_step("DEVELOP"); st.rerun()
    if c[1].button("防衛"): player_step("DEFEND"); st.rerun()
    if c[2].button("進軍"): player_step("MARCH"); st.rerun()
    if c[3].button("占領"): player_step("OCCUPY"); st.rerun()
    if c[4].button("スパイ"): player_step("SPY"); st.rerun()

st.write("---")
for log in s["logs"][:10]: st.text(log)
