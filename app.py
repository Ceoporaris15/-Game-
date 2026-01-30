import streamlit as st
import random

# ページ設定
st.set_page_config(page_title="国家間Game会改：即時反応", layout="wide")
st.title("🌏 国家間Game会改：カウンターバトル")

# 初期化（目標国力100）
if 'state' not in st.session_state:
    st.session_state.state = {
        "p1": {"name": "Player", "power": 10.0, "territory": 10.0, "military": 10.0, "colony": 0.0, "shield": False},
        "p2": {"name": "AI", "power": 10.0, "territory": 10.0, "military": 10.0, "colony": 0.0, "shield": False},
        "turn": 1,
        "logs": ["システム起動。1アクションごとにAIが即座に応答します。"],
        "player_ap": 2,
        "ai_ap": 2
    }

s = st.session_state.state
p1, p2 = s["p1"], s["p2"]

# 計算ロジック
def get_income(player):
    return (player["military"] * player["territory"]) * 0.15

def get_max_ap(player):
    return 2 + int(player["colony"] * 0.1)

# --- AIの即時応答ルーチン ---
def ai_response():
    # AIの基礎リソース更新（ターンの概念をアクション単位に分割）
    if s["ai_ap"] <= 0:
        p2["power"] += get_income(p2)
        s["ai_ap"] = get_max_ap(p2)
        p2["shield"] = False

    # AIの思考：プレイヤーの直前の行動に対する「最適解」を選択
    if p2["power"] >= 95: action = "ECONOMY"
    elif p2["military"] * 0.5 >= p1["territory"]: action = "ATTACK"
    elif p1["military"] > p2["military"] + 3 and not p2["shield"]: action = "DEFEND"
    elif p1["territory"] > 12 and s["ai_ap"] >= 2: action = "OCCUPY"
    elif p2["military"] < 20: action = "MILITARY"
    else: action = "ATTACK"

    # 実行
    if action == "MILITARY":
        p2["military"] += 4; s["ai_ap"] -= 1
        s["logs"].insert(0, "🤖 AI：軍拡。戦力を上乗せしてきた。")
    elif action == "ECONOMY":
        p2["power"] += 5; s["ai_ap"] -= 1
        s["logs"].insert(0, "🤖 AI：軍縮。勝利を確定させようとしている。")
    elif action == "DEFEND":
        p2["shield"] = True; p2["military"] = max(0, p2["military"]-2); s["ai_ap"] -= 1
        s["logs"].insert(0, "🤖 AI：防衛。こちらの追撃を封じに来た。")
    elif action == "ATTACK":
        dmg = p2["military"] * 0.4
        if p1["shield"]: p1["shield"] = False; s["logs"].insert(0, "🤖 AI：攻撃！あなたの盾で防いだ。")
        else: p1["territory"] -= dmg; s["logs"].insert(0, f"🤖 AI：攻撃！領土を{dmg:.1f}削られた。")
        s["ai_ap"] -= 1
    elif action == "OCCUPY":
        steal = p1["territory"] * 0.2; p1["territory"] -= steal; p2["colony"] += steal; s["ai_ap"] -= 2
        s["logs"].insert(0, f"🤖 AI：占領。あなたのリソースが奪われた。")

# --- プレイヤーのアクション処理 ---
def player_action(cmd):
    if cmd == "MILITARY": p1["military"] += 4; s["logs"].insert(0, "👤 あなた：軍拡。")
    elif cmd == "ECONOMY": p1["power"] += 5; s["logs"].insert(0, "👤 あなた：軍縮。")
    elif cmd == "DEFEND": p1["shield"] = True; p1["military"] = max(0, p1["military"]-2); s["logs"].insert(0, "👤 あなた：防衛。")
    elif cmd == "ATTACK":
        dmg = p1["military"] * 0.4
        if p2["shield"]: p2["shield"] = False; s["logs"].insert(0, "👤 あなた：攻撃！AIの盾に阻まれた。")
        else: p2["territory"] -= dmg; s["logs"].insert(0, f"👤 あなた：攻撃！AIの領土に{dmg:.1f}の損害。")
    elif cmd == "OCCUPY":
        steal = p2["territory"] * 0.2; p2["territory"] -= steal; p1["colony"] += steal; s["logs"].insert(0, "👤 あなた：占領。")
    
    s["player_ap"] -= 2 if cmd == "OCCUPY" else 1
    
    # プレイヤーが1回動くごとにAIも1回反応する
    ai_response()
    
    # プレイヤーのAPが切れたらリセット（ターン進行）
    if s["player_ap"] <= 0:
        p1["power"] += get_income(p1)
        s["player_ap"] = get_max_ap(p1)
        s["turn"] += 1
        p1["shield"] = False

# --- メイン表示 ---


col1, col2 = st.columns(2)
with col1:
    st.subheader("🟦 Player")
    st.progress(min(p1['power']/100, 1.0), text=f"国力: {p1['power']:.1f}/100")
    st.metric("領土", f"{p1['territory']:.1f}", f"軍事:{p1['military']:.1f}")
    st.write(f"残りAP: {s['player_ap']} | 🚩 植民地: {p1['colony']:.1f}")

with col2:
    st.subheader("🟥 AI")
    st.progress(min(p2['power']/100, 1.0), text=f"国力: {p2['power']:.1f}/100")
    st.metric("領土", f"{p2['territory']:.1f}", f"軍事:{p2['military']:.1f}")
    st.write(f"AI待機AP: {s['ai_ap']} | 🚩 植民地: {p2['colony']:.1f}")

st.divider()

if p1["power"] >= 100 or p1["territory"] <= 0 or p2["power"] >= 100 or p2["territory"] <= 0:
    winner = "Player" if (p1["power"] >= 100 or p2["territory"] <= 0) else "AI"
    st.header(f"【終局】勝者：{winner}")
    if st.button("リスタート"): st.session_state.clear(); st.rerun()
else:
    c = st.columns(5)
    if c[0].button("軍拡"): player_action("MILITARY"); st.rerun()
    if c[1].button("軍縮"): player_action("ECONOMY"); st.rerun()
    if c[2].button("防衛"): player_action("DEFEND"); st.rerun()
    if c[3].button("攻撃"): player_action("ATTACK"); st.rerun()
    if s["player_ap"] >= 2:
        if c[4].button("占領"): player_action("OCCUPY"); st.rerun()

st.write("### 📜 最新ログ")
for log in s["logs"][:5]: st.text(log)
