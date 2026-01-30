import streamlit as st
import random

st.set_page_config(page_title="DEUS: Develop & Occupy", layout="wide")
st.title("⚔️ 国家間Game：開発の成果と占領の代償")

if 'state' not in st.session_state:
    st.session_state.state = {
        "p1": {"territory": 100.0, "military": 0.0, "colony": 20.0, "shield": False, "nuke_point": 0},
        "p2": {"territory": 300.0, "military": 100.0, "colony": 50.0, "shield": False},
        "turn": 1,
        "logs": ["SYSTEM: 開発で軍事と核を強化せよ。占領には軍事力20が必要となる。"],
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
            s["logs"].insert(0, f"🛡️ 占領地が防壁となり {shield_amt:.1f} の被害を吸収。")
    if dmg > 0:
        p1["territory"] = max(0, p1["territory"] - dmg)
        s["logs"].insert(0, f"💥 本国領土が直接攻撃を受け {dmg:.1f} 喪失。")

# --- AIロジック ---
def ai_logic_overload(player_last_action):
    if not s["ai_awakened"] and (p1["military"] > 80 or p2["territory"] < 180 or player_last_action == "NUKE"):
        s["ai_awakened"] = True
        s["logs"].insert(0, "🔴 WARNING: DEUS覚醒。軍事エネルギーを最大固定。")

    for i in range(2):
        if p2["territory"] <= 0: break
        if p2["military"] < 100: p2["military"] = 100 

        if s["wmd_charging"]:
            if player_last_action == "MARCH" and random.random() < 0.4:
                s["logs"].insert(0, "✅ SYSTEM: 進軍によりWMD発射阻止！")
                s["wmd_charging"] = False
            else:
                apply_damage_to_player(p1["territory"] * 0.5)
                s["wmd_charging"] = False
            continue

        if i == 0 and player_last_action == "MARCH" and not p2["shield"]:
            p2["shield"] = True
            s["logs"].insert(0, "🔴 AI: 防御展開。")
        elif not s["wmd_charging"] and s["ai_awakened"] and random.random() < 0.2:
            s["wmd_charging"] = True
            s["logs"].insert(0, "⚠️ ALERT: DEUSが最終兵器をチャージ中。")
        else:
            power_mult = 1.6 if s["ai_awakened"] else 0.8
            dmg = p2["military"] * 0.25 * power_mult
            if p1["shield"]: dmg *= 0.1
            apply_damage_to_player(dmg)

def player_step(cmd):
    if cmd == "DEVELOP": 
        p1["military"] += 25.0
        p1["nuke_point"] += 15 
        s["logs"].insert(0, f"🔵 Player: 開発（軍拡+25 / 核開発Pt+15）")
    elif cmd == "DEFEND": 
        p1["shield"] = True
        s["logs"].insert(0, "🔵 Player: 本国防衛。")
    elif cmd == "MARCH":
        # 軍事力と占領地の合計値でダメージ
        dmg = (p1["military"] * 0.5) + (p1["colony"] * 0.6)
        if p2["shield"]: 
            p2["shield"] = False
            s["logs"].insert(0, "🔵 Player: 進軍（AIの盾を粉砕）")
        else: 
            p2["territory"] -= dmg
            s["logs"].insert(0, f"🔵 Player: 進軍（AI領土に {dmg:.1f} ダメージ）")
    elif cmd == "OCCUPY":
        if p1["military"] >= 20:
            p1["military"] -= 20
            # 奪える領土を強化 (AIの領土の20%または固定値の高い方)
            steal = max(p2["territory"] * 0.20, 40.0)
            p2["territory"] -= steal
            p1["colony"] += steal
            s["logs"].insert(0, f"🔵 Player: 強制的占領！軍事力20を消費し、広大な盾({steal:.1f})を確保。")
        else:
            s["logs"].insert(0, "❌ SYSTEM: 軍事力が不足しているため占領作戦を行えません。")
            return # 行動を消費させない
    elif cmd == "SPY":
        if random.random() < 0.1:
            p2["territory"] *= 0.5
            s["logs"].insert(0, "🕵️‍♂️ SPY SUCCESS!!")
        else:
            s["logs"].insert(0, "🕵️‍♂️ SPY FAIL.")
    elif cmd == "NUKE":
        p2["territory"] *= 0.2
        p1["nuke_point"] = 0
        s["logs"].insert(0, "🚀 Player: 核兵器発射。")

    # 軍事力100で自動バースト
    if p1["military"] >= 100:
        burst_dmg = 100.0 + (p1["colony"] * 0.3)
        p2["territory"] -= burst_dmg
        p1["military"] = 0
        s["logs"].insert(0, f"💥 BURST!! 開発の集大成による総進軍で {burst_dmg:.1f} ダメージを与え、軍事力リセット。")
    
    ai_logic_overload(cmd)
    s["turn"] += 1
    p1["shield"] = False

# --- UI ---
col1, col2 = st.columns(2)
with col1:
    st.header(f"Turn: {s['turn']}")
    st.subheader("🟦 Player (1 Action)")
    st.metric("本国領土", f"{p1['territory']:.1f}")
    st.metric("占領地 (盾 & 火力源)", f"{p1['colony']:.1f}")
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
    st.error("【敗北】本国は滅びました。")
    if st.button("再試動"): st.session_state.clear(); st.rerun()
elif p2["territory"] <= 0:
    st.success("【完全勝利】帝国の支配を終わらせました。")
    if st.button("再試動"): st.session_state.clear(); st.rerun()
else:
    c = st.columns(5)
    if c[0].button("開発(1)"): player_step("DEVELOP"); st.rerun()
    if c[1].button("防衛(1)"): player_step("DEFEND"); st.rerun()
    if c[2].button("進軍(1)"): player_step("MARCH"); st.rerun()
    if c[3].button("占領(軍事20)"): player_step("OCCUPY"); st.rerun()
    if c[4].button("スパイ(1)"): player_step("SPY"); st.rerun()
    
    if p1["nuke_point"] >= 100:
        st.button("🚀 核兵器発射", type="primary", use_container_width=True, on_click=player_step, args=("NUKE",))

st.write("---")
for log in s["logs"][:8]: st.text(log)
