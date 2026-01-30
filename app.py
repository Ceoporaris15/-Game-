import streamlit as st
import random
import time

# --- ページ設定：スマホ向けに余白を極限までカット ---
st.set_page_config(page_title="COMMAND", layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
    <style>
    /* 全体背景と文字色 */
    .main { background-color: #050805; color: #00ff41; font-family: 'Courier New', monospace; }
    /* 余白の排除 */
    .block-container { padding-top: 1rem; padding-bottom: 0rem; }
    /* ボタンデザイン：軍用スイッチ風 */
    .stButton>button { 
        width: 100%; border: 2px solid #004400; background-color: #001100; color: #00ff41;
        font-size: 0.8rem; height: 2.5rem; border-radius: 0px; margin-bottom: -10px;
    }
    .stButton>button:hover { border: 2px solid #00ff41; background-color: #002200; }
    /* メトリック（数値）の装飾 */
    [data-testid="stMetricValue"] { font-size: 1.2rem !important; color: #00ff41 !important; }
    [data-testid="stMetricLabel"] { font-size: 0.7rem !important; color: #008800 !important; }
    /* プログレスバー */
    .stProgress > div > div > div > div { background-color: #00ff41; }
    /* ログの装飾 */
    .log-text { font-size: 0.7rem; color: #00aa00; background: #000a00; border-left: 2px solid #00ff41; padding: 2px 5px; margin-top: 2px; }
    </style>
    """, unsafe_allow_html=True)

# --- 戦況モニター用映像（安定性の高いGIF形式を推奨） ---
MONITOR_FILES = {
    "STANDBY": "https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExOHp1eXFqYnZidG94bmZ6eTR4bmZ6eTR4bmZ6eTR4bmZ6eTR4bmZ6eSZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/3o7TKVUn7iM8FMEU24/giphy.gif",
    "DEV": "https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExNnZ6amR6amZ6amZ6amZ6amZ6amZ6amZ6amZ6amZ6amZ6amZ6amZ6JmVwPXYxX2ludGVybmFsX2dpZl9ieV9pZCZjdD1n/l41lTfuxNqHMeE8Ni/giphy.gif",
    "ATK": "https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExNHRxeG56NmR6bm96amIxeHl6amR6amZ6amZ6amZ6amZ6amZ6amZ6JmVwPXYxX2ludGVybmFsX2dpZl9ieV9pZCZjdD1n/CE2xyYy6W7S9O/giphy.gif",
    "DEF": "https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExNHpxeG56NmR6bm96amIxeHl6amR6amZ6amZ6amZ6amZ6amZ6amZ6JmVwPXYxX2ludGVybmFsX2dpZl9ieV9pZCZjdD1n/l0IxYD16MqcAdpWF2/giphy.gif",
    "NUKE": "https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExNm5xeG56NmR6bm96amIxeHl6amR6amZ6amZ6amZ6amZ6amZ6amZ6JmVwPXYxX2ludGVybmFsX2dpZl9ieV9pZCZjdD1n/HhTXt43pk1I1W/giphy.gif",
    "LOST": "https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExOXNxeG56NmR6bm96amIxeHl6amR6amZ6amZ6amZ6amZ6amZ6amZ6JmVwPXYxX2ludGVybmFsX2dpZl9ieV9pZCZjdD1n/3o7TKVUn7iM8FMEU24/giphy.gif"
}

if 'state' not in st.session_state:
    st.session_state.state = {
        "p1": {"land": 100.0, "milit": 0.0, "buffer": 20.0, "atom": 0},
        "p2": {"land": 350.0, "milit": 60.0},
        "turn": 1, "ap": 2, "wmd": False, "hard": False, "start": False,
        "video": MONITOR_FILES["STANDBY"], "logs": ["SYSTEM: 司令部待機中"]
    }

s = st.session_state.state
p1, p2 = s["p1"], s["p2"]

def exec_step(cmd):
    if cmd == "DEV":
        p1["milit"] += 25; p1["atom"] += 20; s["video"] = MONITOR_FILES["DEV"]
    elif cmd == "DEF":
        s["video"] = MONITOR_FILES["DEF"]; s["logs"].insert(0, "🛡️ 防衛圏を強化")
    elif cmd == "ATK":
        dmg = (p1["milit"] * 0.4) + (p1["buffer"] * 0.5)
        p2["land"] -= dmg; s["video"] = MONITOR_FILES["ATK"]
    elif cmd == "OCC":
        if p1["milit"] >= 20:
            p1["milit"] -= 20; stolen = max(p2["land"] * 0.2, 40.0)
            p2["land"] -= stolen; p1["buffer"] += stolen
    elif cmd == "NUKE":
        p2["land"] *= 0.2; p1["atom"] = 0; s["video"] = MONITOR_FILES["NUKE"]

    s["ap"] -= 1
    if s["ap"] <= 0:
        if p2["land"] > 0:
            enemy_dmg = (p2["milit"] * 0.2)
            if p1["buffer"] > 0:
                p1["buffer"] -= enemy_dmg
                if p1["buffer"] <= 0: s["video"] = MONITOR_FILES["LOST"]
            else: p1["land"] -= enemy_dmg
        s["ap"], s["turn"] = 2, s["turn"] + 1

# --- 司令画面 ---
if not s["start"]:
    st.subheader("STRATEGIC COMMAND")
    if st.button("標準戦域 (Normal)"): s["start"] = True; st.rerun()
    if st.button("絶望戦域 (Hard)"): s["hard"] = True; s["p2"]["land"]=500; s["start"] = True; st.rerun()
else:
    # 1. 敵軍ステータス (最小限)
    st.markdown(f"🚩 **対抗勢力領域: {p2['land']:.1f}**")
    st.progress(max(0.0, min(p2['land']/500, 1.0)))

    # 2. メインモニター (映像をここに固定)
    st.image(s["video"], use_container_width=True)

    # 3. 自軍ステータス (横並び)
    c1, c2, c3 = st.columns(3)
    c1.metric("本国", f"{p1['land']:.1f}")
    c2.metric("緩衝", f"{p1['buffer']:.1f}")
    c3.metric("AP", f"{s['ap']}")

    st.progress(p1['milit']/100) # 軍事Ptバー
    
    # 4. 指令スイッチ
    if p1["atom"] >= 200:
        if st.button("☢️ 最終兵器投下", type="primary"): exec_step("NUKE"); st.rerun()

    ctrl1, ctrl2 = st.columns(2)
    if ctrl1.button("🛠開発"): exec_step("DEV"); st.rerun()
    if ctrl2.button("🛡防衛"): exec_step("DEF"); st.rerun()
    if ctrl1.button("⚔️進軍"): exec_step("ATK"); st.rerun()
    if ctrl2.button("🚩占領"): exec_step("OCC"); st.rerun()

    # 5. 通信ログ (1行のみ表示)
    st.markdown(f'<div class="log-text">{s["logs"][0]}</div>', unsafe_allow_html=True)

    if p1["land"] <= 0 or p2["land"] <= 0:
        st.error("作戦終了")
        if st.button("REBOOT"): st.session_state.clear(); st.rerun()
