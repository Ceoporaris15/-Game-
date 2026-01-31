import streamlit as st
import random
import base64

# --- 1. レイアウト・コンパクト化スタイル ---
st.set_page_config(page_title="DEUS: COMMANDER", layout="centered")

st.markdown("""
    <style>
    html, body, [data-testid="stAppViewContainer"] {
        background-color: #000; color: #FFF;
    }
    .stAudio { display: none; } 
    /* 敵軍ステータス：高さを抑える */
    .enemy-banner {
        background-color: #300; border-bottom: 2px solid #F00;
        padding: 5px; text-align: center; margin: -50px -15px 10px -15px;
    }
    .enemy-text { color: #F00; font-weight: bold; font-size: 1.1rem; }
    /* ステータス行のコンパクト化 */
    .status-row {
        display: flex; justify-content: space-around;
        background: #111; border: 1px solid #d4af37;
        padding: 5px; margin-bottom: 5px; border-radius: 5px;
    }
    .stat-label { font-size: 0.7rem; color: #aaa; }
    .stat-val { color: #d4af37; font-weight: bold; font-size: 1.1rem; }
    /* ボタン：サイズを縮小し、1画面に収める */
    div[data-testid="column"] button, div[data-testid="stVerticalBlock"] button {
        height: 42px !important; font-size: 0.9rem !important;
        padding: 0px !important; margin-bottom: -5px !important;
        background-color: #1a1a1a !important; color: #FFF !important;
        border: 1px solid #d4af37 !important;
    }
    /* プログレスバー */
    .stProgress { height: 15px !important; }
    .stProgress > div > div > div > div { background-color: #007BFF; }
    .nuke-title { color: #007BFF; font-weight: bold; font-size: 0.8rem; margin: 5px 0 2px 0; }
    
    /* ログボックス：高さを固定してスクロールを防ぐ */
    .log-box {
        background: #050505; border-left: 2px solid #d4af37;
        padding: 8px; height: 85px; font-size: 0.8rem; color: #EEE; overflow: hidden;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 2. 確定BGMシステム ---
def setup_audio():
    try:
        with open('Vidnoz_AIMusic.mp3', 'rb') as f:
            data = f.read()
            st.sidebar.title("🎵 BGM制御")
            st.sidebar.audio(data, format='audio/mp3', loop=True)
            # 初回起動時のみメイン画面に再生案内を出す
            if 'audio_started' not in st.session_state:
                if st.button("🔈 BGMを起動して作戦開始", use_container_width=True):
                    st.session_state.audio_started = True
                    st.rerun()
    except:
        st.sidebar.error("BGMファイル未検出")

setup_audio()

# --- 3. システム初期化 ---
if 'state' not in st.session_state:
    st.session_state.state = {
        "p1": {"territory": 150.0, "military": 0.0, "colony": 30.0, "nuke_point": 0, "shield_active": False},
        "p2": {"territory": 500.0, "military": 100.0}, # 大国の領土を300→500へ情報修正
        "turn": 1, "logs": ["システム起動。BGMをオンにしてください。"],
        "player_ap": 2, "max_ap": 2, "difficulty": None, "faction": None
    }

s = st.session_state.state
p1, p2 = s["p1"], s["p2"]

# --- 4. ロジック ---
def player_step(cmd):
    expand_mul = 2.0 if s["faction"] == "社会主義国" else 1.0
    march_mul = 2.0 if s["faction"] in ["枢軸国", "社会主義国"] else 1.0
    nuke_mul = 2.0 if s["faction"] == "連合国" else 1.0

    if cmd == "EXPAND":
        p1["military"] += 25.0 * expand_mul; p1["nuke_point"] += 20 * nuke_mul
        s["logs"].insert(0, f"🛠 軍拡：核承認P +{20*nuke_mul}")
    elif cmd == "DEFEND": p1["shield_active"] = True; s["logs"].insert(0, "🛡 防衛：迎撃態勢。")
    elif cmd == "MARCH":
        dmg = ((p1["military"] * 0.5) + (p1["colony"] * 0.6)) * march_mul
        if s["difficulty"] == "超大国": dmg *= 0.1
        p2["territory"] -= dmg; s["logs"].insert(0, f"⚔️ 進軍：敵に{dmg:.1f}の打撃。")
    elif cmd == "OCCUPY":
        if p1["military"] >= 20:
            p1["military"] -= 20; steal = max(p2["territory"] * 0.2, 40.0)
            p2["territory"] -= steal; p1["colony"] += steal; s["logs"].insert(0, "🚩 占領：緩衝地拡大。")
    elif cmd == "NUKE":
        p2["territory"] *= 0.15; p1["nuke_point"] = 0; s["logs"].insert(0, "☢️ 核執行：敵地消滅。")

    s["player_ap"] -= 1
    if s["player_ap"] <= 0:
        dmg_to_p1 = (p2["territory"] * 0.1) if s["difficulty"] == "超大国" else 15.0
        if p1["shield_active"]: dmg_to_p1 *= 0.5
        p1["territory"] -= dmg_to_p1
        s["logs"].insert(0, f"⚠️ 反撃：本国-{dmg_to_p1:.1f}")
        s["player_ap"], s["turn"], p1["shield_active"] = s["max_ap"], s["turn"] + 1, False

# --- 5. UI構築 ---
if s["difficulty"] is None:
    st.title("🚩 難易度選択")
    if st.button("小国 (Easy)", use_container_width=True): s["difficulty"] = "小国"; p2["territory"] = 200.0; st.rerun()
    if st.button("大国 (Normal)", use_container_width=True): s["difficulty"] = "大国"; p2["territory"] = 600.0; st.rerun()
    if st.button("超大国 (Despair)", use_container_width=True): s["difficulty"] = "超大国"; p2["territory"] = 3000.0; st.rerun()
elif s["faction"] is None:
    st.title("🛡️ 陣営選択")
    if st.button("連合国 (核開発特化)", use_container_width=True): s["faction"] = "連合国"; st.rerun()
    if st.button("枢軸国 (軍事特化)", use_container_width=True): s["faction"] = "枢軸国"; st.rerun()
    if st.button("社会主義国 (生産特化)", use_container_width=True): s["faction"] = "社会主義国"; s["player_ap"] = 1; s["max_ap"] = 1; st.rerun()
else:
    # メイン画面
    st.markdown(f'<div class="enemy-banner"><span class="enemy-text">敵対AI [DEUS]: {p2["territory"]:.0f} pts</span></div>', unsafe_allow_html=True)
    st.markdown(f'<div class="status-row"><div><span class="stat-label">本国</span><br><span class="stat-val">{p1["territory"]:.0f}</span></div><div><span class="stat-label">緩衝地</span><br><span class="stat-val">{p1["colony"]:.0f}</span></div></div>', unsafe_allow_html=True)
    
    st.markdown('<p class="nuke-title">☢️ 核兵器開発進行状況</p>', unsafe_allow_html=True)
    st.progress(min(p1['nuke_point']/200.0, 1.0))

    if p1["territory"] <= 0:
        st.error("【敗北】 次はもっと冷酷になれ…")
        if st.button("REBOOT", use_container_width=True): st.session_state.clear(); st.rerun()
    elif p2["territory"] <= 0:
        st.success("【勝利】 世界は貴公のものだ！")
        if st.button("REBOOT", use_container_width=True): st.session_state.clear(); st.rerun()
    else:
        st.write(f"**Turn {s['turn']} | AP: {s['player_ap']}**")
        
        # 核使用
        if p1["nuke_point"] >= 200:
            if st.button("☢️ 最終宣告執行 (核攻撃)", type="primary", use_container_width=True): player_step("NUKE"); st.rerun()
        
        # アクション（コンパクト配置）
        c1, c2 = st.columns(2)
        if c1.button("🛠 軍拡", use_container_width=True): player_step("EXPAND"); st.rerun()
        if c2.button("🛡 防衛", use_container_width=True): player_step("DEFEND"); st.rerun()
        if c1.button("⚔️ 進軍", use_container_width=True): player_step("MARCH"); st.rerun()
        if c2.button("🚩 占領", use_container_width=True): player_step("OCCUPY"); st.rerun()

    # ログ（スクロール不要なコンパクト表示）
    st.write("---")
    log_html = "".join([f'<div>{log}</div>' for log in s["logs"][:2]])
    st.markdown(f'<div class="log-box">{log_html}</div>', unsafe_allow_html=True)
