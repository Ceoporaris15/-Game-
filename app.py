import streamlit as st
import random

# --- ゲームの基本設定 ---
st.set_page_config(page_title="国家間Game会改", layout="wide")
st.title("🌏 国家間Game会改 - 皇帝への挑戦")

# セッション状態（データの保持）の初期化
if 'turn' not in st.session_state:
    st.session_state.turn = 1
    st.session_state.p1 = {"name": "あなた", "power": 10.0, "territory": 10.0, "military": 10.0, "colonies": 0.0, "defending": False}
    st.session_state.p2 = {"name": "皇帝AI", "power": 10.0, "territory": 10.0, "military": 10.0, "colonies": 0.0, "defending": False}
    st.session_state.log = ["ゲーム開始！あなたのターンです。"]
    st.session_state.ap = 2

def update_status(player):
    income = (player["military"] * player["territory"]) / 10
    player["power"] += income
    return income

# --- 画面レイアウト ---
col1, col2 = st.columns(2)

with col1:
    st.subheader(f"👤 {st.session_state.p1['name']}")
    st.metric("国力 (目標100)", f"{st.session_state.p1['power']:.1f}")
    st.write(f"領土: {st.session_state.p1['territory']:.1f} / 軍事: {st.session_state.p1['military']:.1f}")
    st.write(f"AP: {st.session_state.ap}")

with col2:
    st.subheader(f"👑 {st.session_state.p2['name']}")
    st.metric("国力", f"{st.session_state.p2['power']:.1f}")
    st.write(f"領土: {st.session_state.p2['territory']:.1f} / 軍事: {st.session_state.p2['military']:.1f}")

st.divider()

# --- アクションボタン ---
st.write("### 📜 命令を下してください")
cols = st.columns(6)

def run_action(cmd):
    p, target = st.session_state.p1, st.session_state.p2
    if cmd == "1": p["military"] += 3; msg = "軍拡を行いました。"
    elif cmd == "2": p["territory"] += 1; msg = "内政を整えました。"
    elif cmd == "3": p["power"] += 5; msg = "軍縮で経済を回しました。"
    elif cmd == "4": p["defending"] = True; msg = "防衛体制を敷きました。"
    elif cmd == "5":
        dmg = p["military"] / 5
        if target["defending"]: dmg /= 2
        target["territory"] -= dmg; p["colonies"] += dmg
        msg = f"攻撃！敵領土を{dmg:.1f}削りました。"
    
    st.session_state.log.insert(0, f"【あなた】{msg}")
    st.session_state.ap -= 1
    
    # APが切れたらAIのターンへ
    if st.session_state.ap <= 0:
        ai_turn()

def ai_turn():
    # 簡易AIロジック
    p, target = st.session_state.p2, st.session_state.p1
    update_status(p)
    # AIは2回行動
    for _ in range(2):
        p["military"] += 3 # 皇帝は常に軍拡する強気設定
    st.session_state.log.insert(0, "【皇帝】軍備を大幅に増強した！")
    
    # 自分のターンに戻る準備
    st.session_state.turn += 1
    update_status(target)
    st.session_state.ap = 2 + int(target["colonies"] // 5)
    target["defending"] = False

# ボタンの設置
if cols[0].button("軍拡"): run_action("1")
if cols[1].button("内政"): run_action("2")
if cols[2].button("軍縮"): run_action("3")
if cols[3].button("防衛"): run_action("4")
if cols[4].button("攻撃"): run_action("5")
if cols[5].button("リセット"): st.session_state.clear(); st.rerun()

# --- 実況ログ ---
st.write("### 📢 戦況ログ")
for l in st.session_state.log[:5]:
    st.write(l)
