import streamlit as st
import random

st.set_page_config(page_title="DEUS: Dual Action", layout="wide")
st.title("⚔️ 国家間Game：2アクションの激突")

if 'state' not in st.session_state:
    st.session_state.state = {
        "p1": {"territory": 100.0, "military": 0.0, "colony": 20.0, "shield": False, "nuke_point": 0},
        "p2": {"territory": 300.0, "military": 100.0, "colony": 50.0, "shield": False},
        "turn": 1,
        "logs": ["SYSTEM: 双方が2回行動。コンボを駆使して敵を殲滅せよ。"],
        "player_ap": 2, # プレイヤーの残り行動回数
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

# --- AIロジック (2回行動) ---
def ai_logic_dual(player_last_action):
    if not s["ai_awakened"] and (p1["military"] > 80 or p2["territory"] < 180 or player_last_action == "NUKE"):
        s["ai_awakened"] = True
        s["logs"].insert(0, "🔴 WARNING: DEUS覚醒。軍事エネルギーを最大固定。")

    for _ in range(2):
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

        # AIの行動選択
        choice = random.random()
        if choice < 0.2 and not p2["shield"]:
            p2["shield"] = True
            s["logs"].insert(0, "🔴 AI: 防御展開。")
        elif choice < 0.4 and p2["territory"] < 100:
            p2["territory"] += 20.0
            s["logs"].insert(0, "🔴 AI: 国土修復。")
        elif choice < 0.5 and not s["wmd_charging"] and s["ai_awakened"]:
            s["wmd_charging"] = True
            s["logs"].insert(0, "⚠️ ALERT: DEUSがWMDをチャージ中。")
        else:
            power_mult = 1.6 if s["ai_awakened"] else 0.8
            dmg = p2["military"] * 0.25 * power_mult
            if p1["shield"]: dmg *= 0.1
            apply_damage_to_player(dmg)

def player_step(cmd):
    # 行動実行
    if cmd == "DEVELOP": 
        p1["military"] += 25.0
        p1["nuke_point"] += 15 
        s["logs"].insert(0, f"🔵 Player: 開発（軍拡+25 / 核Pt+15）")
    elif cmd == "DEFEND": 
        p1["shield"] = True
        s["logs"].insert(0, "🔵 Player: 本国防衛。")
    elif cmd == "MARCH":
        dmg = (p1["military"] * 0.5) + (p1["colony"] * 0.6)
        if p2["shield"]: 
            p2["shield"] = False
            s["logs"].insert(0, "🔵 Player: 進軍（AIの盾を粉砕）")
        else: 
            p2["territory"] -= dmg
            s["logs"].insert(0, f"🔵 Player: 進軍（AI領土-{dmg:.1f}）")
    elif cmd == "OCCUPY":
        if p1["military"] >= 20:
            p1["military"] -= 20
            steal = max(p2["territory"] * 0.20, 40.0)
            p2["territory"] -= steal
            p1["colony"] += steal
            s["logs"].insert(0, f"🔵 Player: 占領成功（軍事-20 / 盾+{steal:.1f}）")
        else:
            s["logs"].insert(0, "❌ SYSTEM: 軍事力が不足しています。")
            return
    elif cmd == "SPY":
        if random.random() < 0.1:
            p2["territory"] *= 0.5
            s["logs"].insert(0, "🕵️‍♂️ SPY SUCCESS!! AI領土を半減。")
        else:
            s["logs"].insert(0, "🕵️‍♂️ SPY FAIL.")
    elif cmd == "NUKE":
        p2["territory"] *= 0.2
        p1["nuke_point"] = 0
        s["logs"].insert(0, "🚀 Player: 核兵器発射！！")

    # バースト判定
    if p1["military"] >= 100:
        burst_dmg = 100.0 + (p1["colony"] * 0.3)
        p2["territory"] -= burst_dmg
        p1["military"] = 0
        s["logs"].insert(0, f"💥 BURST!! 総進軍で {burst_dmg:.1f} ダメージ。")

    s["player_ap"] -= 1

    # プレイヤーの全AP終了時にAIが行動
    if s["player_ap"] <= 0:
        ai_logic_dual(cmd)
        s["player_ap"] = 2 # リセット
        s["turn"] += 1
        p1["shield"] = False

# --- UI ---
col1, col2 = st.columns(2)
with col1:
    st.header(f"Turn: {s['turn']}")
    st.subheader(f"🟦 Player (残りAP: {s['player_ap']})")
    st.metric("本国領土", f"{p1['territory']:.1f}")
    st.metric("占領地 (盾&威力)", f"{p1['colony']:.1f}")
    st.write(f"軍事: {p1['military']}/100 | 核Pt: {p1['nuke_point']}/100")
    st.progress(min(p1['military']/100, 1.0))

with col2:
    status = "👿 AWAKENED" if s["ai_awakened"] else "😴 SLEEPING"
    st.subheader(f"🟥 DEUS ({status})")
    st.metric("AI領土", f"{p2['territory']:.1f}")
    st.metric("AI軍事力", f"{p2['military']:.1f}")
    if s["wmd_charging"]: st.error("🚨 WMDチャージ中")

st.divider()

if p1["territory"] <= 0:
    st.error("【滅亡】")
    if st.button("再試動"): st.session_state.clear(); st.rerun()
elif p2["territory"] <= 0:
    st.success("【勝利】")
    if st.button("再試動"): st.session_state.clear(); st.rerun()
else:
    c = st.columns(5)
    if c[0].button("開発"): player_step("DEVELOP"); st.rerun()
    if c[1].button("防衛"): player_step("DEFEND"); st.rerun()
    if c[2].button("進軍"): player_step("MARCH"); st.rerun()
    if c[3].button("占領(軍事20)"): player_step("OCCUPY"); st.rerun()
    if c[4].button("スパイ"): player_step("SPY"); st.rerun()
    
    if p1["nuke_point"] >= 100:
        st.button("🚀 核兵器発射", type="primary", use_container_width=True, on_click=player_step, args=("NUKE",))

st.write("---")
for log in s["logs"][:10]: st.text(log)
