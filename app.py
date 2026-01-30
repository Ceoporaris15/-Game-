import streamlit as st
import random

st.set_page_config(page_title="DEUS: Strategic Balance", layout="wide")
st.title("⚔️ 国家間Game：殲滅の50年（戦略的均衡）")

if 'state' not in st.session_state:
    st.session_state.state = {
        "p1": {"territory": 60.0, "military": 10.0, "colony": 0.0, "shield": False},
        "p2": {"territory": 150.0, "military": 80.0, "colony": 30.0, "shield": False},
        "turn": 1,
        "logs": ["SYSTEM: 戦略的均衡を確認。AIは極限状態でのみ特殊兵器を解放します。"],
        "player_ap": 2,
        "ai_ap": 4,
        "wmd_charging": False
    }

s = st.session_state.state
p1, p2 = s["p1"], s["p2"]

def get_max_ap(player, is_ai=False):
    if is_ai:
        if player["territory"] > 220: return 2
        if player["territory"] > 130: return 3
        return 4
    return 2 + int(player["colony"] / 20)

# --- AI：抑制されたWMD運用ロジック ---
def ai_logic_controlled_wmd(player_last_action):
    if s["ai_ap"] <= 0:
        s["ai_ap"] = get_max_ap(p2, True)
        p2["shield"] = False

    # 1. WMD発射判定
    if s["wmd_charging"]:
        if player_last_action == "ATTACK" and random.random() < 0.4:
            s["logs"].insert(0, "✅ SYSTEM: 決死の反撃により、WMD発射回路の破壊に成功！")
            s["wmd_charging"] = False
        else:
            dmg = p1["territory"] * 0.5
            p1["territory"] -= dmg
            s["logs"].insert(0, f"☢️ AI: 戦術核使用。あなたの領土の50%({dmg:.1f})が灰燼に帰しました。")
            s["wmd_charging"] = False
        s["ai_ap"] -= 1

    # 2. WMDチャージ開始条件（最小限に抑制）
    # 条件A: AIの領土が60以下（壊滅の危機）
    # 条件B: プレイヤーの軍事がAIの半分を超えた（出鼻をくじく牽制）
    elif not s["wmd_charging"] and ((p2["territory"] < 60) or (p1["military"] > p2["military"] * 0.5)):
        if random.random() < 0.3: # 条件を満たしても即発動せず「ため」を作る
            s["wmd_charging"] = True
            s["logs"].insert(0, "⚠️ ALERT: DEUSが最終防衛ラインを突破。特殊兵器のチャージを開始。")
            s["ai_ap"] -= 1
        else:
            execute_normal_action(player_last_action)
    else:
        execute_normal_action(player_last_action)

def execute_normal_action(player_last_action):
    if s["turn"] >= 50:
        action = "MARKET_OPEN"
    elif player_last_action == "ATTACK" and not p2["shield"]:
        action = "DEFEND"
    elif p2["territory"] < 100:
        action = "RECOVER"
    else:
        action = "ATTACK"

    if action == "MARKET_OPEN":
        steal = p1["territory"] * 0.25
        p1["territory"] -= steal; p2["territory"] += steal; s["ai_ap"] -= 1
        s["logs"].insert(0, f"🔴 AI: 市場開放。構造的な領土接収。")
    elif action == "DEFEND":
        p2["shield"] = True; s["ai_ap"] -= 1
        s["logs"].insert(0, "🔴 AI: 緊急防衛。あなたの攻撃を予測。")
    elif action == "RECOVER":
        p2["territory"] += 12.0; s["ai_ap"] -= 1
        s["logs"].insert(0, "🔴 AI: 国土復興。崩壊した基盤を修復中。")
    elif action == "ATTACK":
        dmg = p2["military"] * 0.2
        if p1["shield"]: dmg *= 0.1
        p1["territory"] = max(0, p1["territory"] - dmg)
        s["ai_ap"] -= 1
        s["logs"].insert(0, f"🔴 AI: 通常爆撃。領土に{dmg:.1f}の被害。")

def player_step(cmd):
    if cmd == "MILITARY": p1["military"] += 7; s["logs"].insert(0, "🔵 You: 軍備を拡張。均衡を崩しにかかります。")
    elif cmd == "DEFEND": p1["shield"] = True; s["logs"].insert(0, "🔵 You: 全面防衛。AIの爆撃に備えます。")
    elif cmd == "ATTACK":
        dmg = p1["military"] * 0.5
        if p2["shield"]: p2["shield"] = False; s["logs"].insert(0, "🔵 You: 猛攻（AIの防壁を粉砕）")
        else: p2["territory"] -= dmg; s["logs"].insert(0, f"🔵 You: 攻撃（AI領土-{dmg:.1f}）")
    elif cmd == "OCCUPY":
        steal = min(p2["territory"] * 0.12, 18.0)
        p2["territory"] -= steal; p1["colony"] += steal; p1["territory"] += steal * 0.4
        s["logs"].insert(0, "🔵 You: 占領。じわじわと支配圏を奪います。")
    
    s["player_ap"] -= 2 if cmd == "OCCUPY" else 1
    ai_logic_controlled_wmd(cmd)
    
    if s["player_ap"] <= 0:
        s["player_ap"] = get_max_ap(p1)
        s["turn"] += 1; p1["shield"] = False

# --- UI ---
col1, col2 = st.columns(2)
with col1:
    st.header(f"Turn: {s['turn']}")
    st.subheader("🟦 Player")
    st.metric("領土", f"{p1['territory']:.1f}")
    st.metric("軍事力", f"{p1['military']:.1f}")
    st.caption(f"AP: {s['player_ap']} | 🚩 植民地: {p1['colony']:.1f}")

with col2:
    st.subheader("🟥 DEUS")
    if s["wmd_charging"]: st.error("🚨 特殊兵器チャージ中")
    st.metric("領土", f"{p2['territory']:.1f}")
    st.metric("軍事力", f"{p2['military']:.1f}")
    st.caption(f"AI AP: {s['ai_ap']}")

st.divider()

if p1["territory"] <= 0:
    st.error("【敗北】あなたは歴史の闇に消えました。")
    if st.button("再起動"): st.session_state.clear(); st.rerun()
elif p2["territory"] <= 0:
    st.success("【勝利】巨人を倒し、新たな秩序を築きました！")
    if st.button("再起動"): st.session_state.clear(); st.rerun()
else:
    c = st.columns(4)
    if c[0].button("軍拡(1)"): player_step("MILITARY"); st.rerun()
    if c[1].button("防衛(1)"): player_step("DEFEND"); st.rerun()
    if c[2].button("攻撃(1)"): player_step("ATTACK"); st.rerun()
    if s["player_ap"] >= 2:
        if c[3].button("占領(2)"): player_step("OCCUPY"); st.rerun()

st.write("---")
for log in s["logs"][:8]: st.text(log)
