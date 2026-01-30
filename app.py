import streamlit as st
import random

st.set_page_config(page_title="DEUS: 100 Cap War", layout="wide")
st.title("⚔️ 国家間Game：100の均衡")

if 'state' not in st.session_state:
    st.session_state.state = {
        "p1": {"territory": 80.0, "military": 10.0, "colony": 0.0, "shield": False, "nuke_point": 0},
        "p2": {"territory": 200.0, "military": 50.0, "colony": 40.0, "shield": False},
        "turn": 1,
        "logs": ["SYSTEM: 軍事力リミッター(100)作動。技術的特異点に到達せよ。"],
        "wmd_charging": False,
        "ai_awakened": False 
    }

s = st.session_state.state
p1, p2 = s["p1"], s["p2"]

# --- AI：リミッター対応ロジック ---
def ai_logic_capped(player_last_action):
    # 覚醒判定
    if not s["ai_awakened"]:
        if p1["military"] > 40 or p1["territory"] > 120 or player_last_action == "NUKE":
            s["ai_awakened"] = True
            s["logs"].insert(0, "🔴 WARNING: DEUS覚醒。軍拡および殲滅体制へ移行。")

    for i in range(2):
        if p2["territory"] <= 0: break
        
        # 1. WMD発射判定
        if s["wmd_charging"]:
            if player_last_action == "ATTACK" and random.random() < 0.4:
                s["logs"].insert(0, "✅ SYSTEM: 阻止成功！AIのWMDを妨害しました。")
                s["wmd_charging"] = False
            else:
                dmg = p1["territory"] * 0.5
                p1["territory"] -= dmg
                s["logs"].insert(0, f"☢️ AI: WMD使用。領土の50%({dmg:.1f})を喪失。")
                s["wmd_charging"] = False
            continue

        # 2. 覚醒時の軍拡（上限100）
        if s["ai_awakened"] and p2["military"] < 100:
            gain = min(20, 100 - p2["military"])
            p2["military"] += gain
            if gain > 0:
                s["logs"].insert(0, f"🔴 AI: 軍拡。軍事力が限界値({p2['military']})に接近。")
                continue

        # 3. 通常の戦略
        if i == 0 and player_last_action == "ATTACK" and not p2["shield"]:
            p2["shield"] = True
            s["logs"].insert(0, "🔴 AI: 防御シールド展開。")
        elif p2["territory"] < 80:
            p2["territory"] += 20.0
            s["logs"].insert(0, "🔴 AI: ナノマシンによる国土修復。")
        elif not s["wmd_charging"] and s["ai_awakened"] and random.random() < 0.2:
            s["wmd_charging"] = True
            s["logs"].insert(0, "⚠️ ALERT: DEUSがWMDをチャージ中。")
        else:
            # 軍事力100が最大威力
            power_mult = 1.8 if s["ai_awakened"] else 0.7
            dmg = p2["military"] * 0.25 * power_mult
            if p1["shield"]: dmg *= 0.1
            p1["territory"] = max(0, p1["territory"] - dmg)
            s["logs"].insert(0, f"🔴 AI: 爆撃。ダメージ {dmg:.1f}")

def player_step(cmd):
    if cmd == "MILITARY": 
        # 軍事力上限100、ポイントは貯まる
        p1["military"] = min(100.0, p1["military"] + 8.0)
        p1["nuke_point"] += 10 
        s["logs"].insert(0, f"🔵 Player: 軍拡（軍事:{p1['military']} / 核Pt:{p1['nuke_point']}）")
    elif cmd == "DEFEND": 
        p1["shield"] = True
        s["logs"].insert(0, "🔵 Player: 全面防衛。")
    elif cmd == "ATTACK":
        dmg = p1["military"] * 0.6 # 最大軍事力100なら一撃60ダメージ
        if p2["shield"]: 
            p2["shield"] = False
            s["logs"].insert(0, "🔵 Player: 攻撃（AIの盾を粉砕）")
        else: 
            p2["territory"] -= dmg
            s["logs"].insert(0, f"🔵 Player: 攻撃（AI領土-{dmg:.1f}）")
    elif cmd == "OCCUPY":
        steal = min(p2["territory"] * 0.1, 15.0)
        p2["territory"] -= steal
        p1["colony"] += steal
        p1["territory"] += steal * 0.4
        s["logs"].insert(0, "🔵 Player: 占領による領土奪還。")
    elif cmd == "SPY":
        if random.random() < 0.1:
            dmg = p2["territory"] * 0.5
            p2["territory"] -= dmg
            s["logs"].insert(0, f"🕵️‍♂️ SPY SUCCESS!! AIの領土を半分({dmg:.1f})破壊。")
        else:
            s["logs"].insert(0, "🕵️‍♂️ SPY FAIL: 潜入に失敗しました。")
    elif cmd == "NUKE":
        dmg = p2["territory"] * 0.8
        p2["territory"] -= dmg
        p1["nuke_point"] = 0
        s["logs"].insert(0, f"🚀 Player: 核兵器発射！！AI領土を壊滅({dmg:.1f})。")
    
    ai_logic_capped(cmd)
    s["turn"] += 1
    p1["shield"] = False

# --- UI ---
col1, col2 = st.columns(2)
with col1:
    st.header(f"Turn: {s['turn']}")
    st.subheader("🟦 Player")
    st.metric("領土", f"{p1['territory']:.1f}")
    st.metric("軍事力 (MAX 100)", f"{p1['military']:.1f}")
    st.metric("核開発", f"{p1['nuke_point']}/100")
    st.progress(min(p1['nuke_point']/100, 1.0))

with col2:
    status_text = "👿 AWAKENED" if s["ai_awakened"] else "😴 SLEEPING"
    st.subheader(f"🟥 DEUS ({status_text})")
    if s["wmd_charging"]: st.error("🚨 WMDチャージ中")
    st.metric("領土", f"{p2['territory']:.1f}")
    st.metric("軍事力 (MAX 100)", f"{p2['military']:.1f}")
    st.caption("AIは1ターンに2回連続で行動します")

st.divider()

if p1["territory"] <= 0:
    st.error("【敗北】あなたは地図から消滅しました。")
    if st.button("再起動"): st.session_state.clear(); st.rerun()
elif p2["territory"] <= 0:
    st.success("【完全勝利】均衡を破り、超大国を打倒しました！")
    if st.button("再起動"): st.session_state.clear(); st.rerun()
else:
    c = st.columns(5)
    if c[0].button("軍拡(1)"): player_step("MILITARY"); st.rerun()
    if c[1].button("防衛(1)"): player_step("DEFEND"); st.rerun()
    if c[2].button("攻撃(1)"): player_step("ATTACK"); st.rerun()
    if c[3].button("占領(1)"): player_step("OCCUPY"); st.rerun()
    if c[4].button("🕵️‍♂️ スパイ(1)"): player_step("SPY"); st.rerun()
    
    if p1["nuke_point"] >= 100:
        st.button("🚀 核兵器発射 (AI領土8割滅)", type="primary", use_container_width=True, on_click=player_step, args=("NUKE",))

st.write("---")
for log in s["logs"][:8]: st.text(log)
