import streamlit as st
import random

st.set_page_config(page_title="DEUS: Final Resistance", layout="wide")
st.title("⚔️ 国家間Game：1アクションの抵抗")

if 'state' not in st.session_state:
    st.session_state.state = {
        "p1": {"territory": 80.0, "military": 10.0, "colony": 0.0, "shield": False, "nuke_point": 0},
        "p2": {"territory": 200.0, "military": 100.0, "colony": 40.0, "shield": False},
        "turn": 1,
        "logs": ["SYSTEM: プレイヤーは1行動、AIは2行動。核開発を進め、起死回生を狙え。"],
        "wmd_charging": False
    }

s = st.session_state.state
p1, p2 = s["p1"], s["p2"]

# --- AI：2回行動の冷徹なロジック ---
def ai_logic_dual_action(player_last_action):
    for i in range(2):
        if p2["territory"] <= 0: break
        
        # 1. WMD発射判定（チャージ中なら発射）
        if s["wmd_charging"]:
            if player_last_action == "ATTACK" and random.random() < 0.4:
                s["logs"].insert(0, "✅ SYSTEM: 阻止成功！AIの兵器システムを一時ダウンさせました。")
                s["wmd_charging"] = False
            else:
                dmg = p1["territory"] * 0.5
                p1["territory"] -= dmg
                s["logs"].insert(0, f"☢️ AI: 兵器使用。あなたの領土の50%({dmg:.1f})が消滅。")
                s["wmd_charging"] = False
            continue

        # 2. WMDチャージ開始（AIのピンチ or プレイヤーの核が近い）
        elif not s["wmd_charging"] and (p2["territory"] < 70 or p1["nuke_point"] > 80):
            if random.random() < 0.4:
                s["wmd_charging"] = True
                s["logs"].insert(0, "⚠️ ALERT: DEUSが迎撃兵器をチャージ中！")
                continue

        # 3. 通常行動
        # 攻撃を受けた後の1手目は防御を優先、2手目は反撃
        if i == 0 and player_last_action == "ATTACK" and not p2["shield"]:
            p2["shield"] = True
            s["logs"].insert(0, "🔴 AI: 防御膜を展開。")
        elif p2["territory"] < 100:
            p2["territory"] += 15.0
            s["logs"].insert(0, "🔴 AI: 損傷個所を修復。")
        else:
            dmg = p2["military"] * 0.25
            if p1["shield"]: dmg *= 0.1
            p1["territory"] = max(0, p1["territory"] - dmg)
            s["logs"].insert(0, f"🔴 AI: 爆撃実行。領土に{dmg:.1f}のダメージ。")

def player_step(cmd):
    # プレイヤーは1アクションのみ実行
    if cmd == "MILITARY": 
        p1["military"] += 8
        p1["nuke_point"] += 10 
        s["logs"].insert(0, f"🔵 Player: 軍拡実行（核開発+10 / 現在:{p1['nuke_point']}）")
    elif cmd == "DEFEND": 
        p1["shield"] = True
        s["logs"].insert(0, "🔵 Player: 全面防衛。次ターンの被害を最小化。")
    elif cmd == "ATTACK":
        dmg = p1["military"] * 0.5
        if p2["shield"]: 
            p2["shield"] = False
            s["logs"].insert(0, "🔵 Player: 攻撃（AIのシールドを破壊）")
        else: 
            p2["territory"] -= dmg
            s["logs"].insert(0, f"🔵 Player: 攻撃（AI領土-{dmg:.1f}）")
    elif cmd == "OCCUPY":
        steal = min(p2["territory"] * 0.1, 15.0)
        p2["territory"] -= steal
        p1["colony"] += steal
        p1["territory"] += steal * 0.4
        s["logs"].insert(0, "🔵 Player: 領土奪還。資源を接収。")
    elif cmd == "NUKE":
        dmg = p2["territory"] * 0.8
        p2["territory"] -= dmg
        p1["nuke_point"] = 0
        s["logs"].insert(0, f"🚀 Player: 核兵器発射！！AI領土の80%({dmg:.1f})を破壊。")
    
    # AIの2回行動が始まる
    ai_logic_dual_action(cmd)
    
    s["turn"] += 1
    # プレイヤーのシールドは1回（AIの2アクション）耐えると解除
    p1["shield"] = False

# --- UIレイアウト ---
col1, col2 = st.columns(2)
with col1:
    st.header(f"Turn: {s['turn']}")
    st.subheader("🟦 Player (1 Action)")
    st.metric("領土 (Life)", f"{p1['territory']:.1f}")
    st.metric("核開発ポイント", f"{p1['nuke_point']}/100")
    st.progress(min(p1['nuke_point']/100, 1.0))
    st.caption(f"軍事力: {p1['military']:.1f}")

with col2:
    st.subheader("🟥 DEUS (2 Actions)")
    if s["wmd_charging"]: st.error("🚨 WMDチャージ中：阻止せよ")
    st.metric("領土", f"{p2['territory']:.1f}")
    st.metric("軍事力", f"{p2['military']:.1f}")
    st.caption("AIは常に2連続で行動します")

st.divider()

if p1["territory"] <= 0:
    st.error("【敗北】抵抗は鎮圧されました。")
    if st.button("もう一度挑む"): st.session_state.clear(); st.rerun()
elif p2["territory"] <= 0:
    st.success("【歴史的勝利】絶望的な状況からAIを壊滅させました！")
    if st.button("新たな歴史へ"): st.session_state.clear(); st.rerun()
else:
    c = st.columns(4)
    # 各ボタンは1ターン1回実行
    if c[0].button("軍拡(点+10)"): player_step("MILITARY"); st.rerun()
    if c[1].button("防衛"): player_step("DEFEND"); st.rerun()
    if c[2].button("攻撃"): player_step("ATTACK"); st.rerun()
    if c[3].button("占領"): player_step("OCCUPY"); st.rerun()
    
    if p1["nuke_point"] >= 100:
        if st.button("🚀 核兵器発射(AI領土80%滅)", use_container_width=True):
            player_step("NUKE"); st.rerun()

st.write("---")
for log in s["logs"][:8]: st.text(log)
