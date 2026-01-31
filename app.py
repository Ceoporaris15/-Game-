import streamlit as st
import random
import base64

# --- 1. 極限のデザイン・スタイル定義 ---
st.set_page_config(page_title="DEUS", layout="centered")

st.markdown("""
    <style>
    html, body, [data-testid="stAppViewContainer"] {
        background-color: #000; color: #FFF; font-family: 'Courier New', monospace;
    }
    .stAudio { display: none; } 
    /* 敵軍ステータス */
    .enemy-banner {
        border-bottom: 1px solid #F00; padding: 10px; text-align: center; margin: -50px -15px 20px -15px;
    }
    .enemy-text { color: #F00; font-weight: bold; font-size: 1.2rem; letter-spacing: 5px; }
    /* 自軍ステータス */
    .status-row {
        display: flex; justify-content: space-around; padding: 10px; margin-bottom: 15px;
    }
    .stat-label { font-size: 0.7rem; color: #888; letter-spacing: 1px; }
    .stat-val { color: #d4af37; font-weight: bold; font-size: 1.3rem; display: block; }
    /* ボタン：装飾を削ぎ落とした無機質な黒 */
    div[data-testid="column"] button, div[data-testid="stVerticalBlock"] button {
        height: 50px !important; background-color: #000 !important; color: #d4af37 !important;
        border: 1px solid #d4af37 !important; border-radius: 0px !important;
        font-weight: bold !important; letter-spacing: 2px !important;
    }
    div[data-testid="column"] button:hover { background-color: #d4af37 !important; color: #000 !important; }
    /* プログレスバー：核兵器を象徴する青 */
    .stProgress > div > div > div > div { background-color: #007BFF; }
    .nuke-label { font-size: 0.75rem; color: #007BFF; letter-spacing: 2px; margin-bottom: 5px; font-weight: bold;}
    
    .log-box {
        background: #000; border-top: 1px solid #333;
        padding: 10px; height: 100px; font-size: 0.8rem; color: #666;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 2. 隠しオーディオ・プロトコル ---
try:
    with open('Vidnoz_AIMusic.mp3', 'rb') as f:
        st.sidebar.markdown("### SYSTEM BGM")
        st.sidebar.audio(f.read(), format='audio/mp3', loop=True)
        st.sidebar.caption("TAP TO ACTIVATE AUDIO")
except:
    st.sidebar.error("BGM ERROR")

# --- 3. システムステート管理 ---
if 'state' not in st.session_state:
    st.session_state.state = {
        "p1": {"territory": 100.0, "military": 0.0, "colony": 20.0, "nuke_point": 0, "shield_active": False},
        "p2": {"territory": 300.0, "military": 100.0},
        "turn": 1, "logs": ["SYSTEM ONLINE."],
        "player_ap": 2, "max_ap": 2, "difficulty": None, "faction": None
    }

s = st.session_state.state
p1, p2 = s["p1"], s["p2"]

# --- 4. タクティカル・ロジック ---
def player_step(cmd):
    # 陣営別補正（社会主義=SOVIET, 枢軸=AXIS, 連合=ALLIES）
    expand_mul = 2.0 if s["faction"] == "SOVIET" else 1.0
    march_mul = 2.0 if s["faction"] in ["AXIS", "SOVIET"] else 1.0
    nuke_mul = 2.0 if s["faction"] == "ALLIES" else 1.0

    if cmd == "EXPAND":
        p1["military"] += 25.0 * expand_mul; p1["nuke_point"] += 20 * nuke_mul
        s["logs"].insert(0, ">> FORCE EXPANDED.")
    elif cmd == "DEFEND": p1["shield_active"] = True; s["logs"].insert(0, ">> SHIELD DEPLOYED.")
    elif cmd == "MARCH":
        dmg = ((p1["military"] * 0.5) + (p1["colony"] * 0.6)) * march_mul
        if s["difficulty"] == "DEUS": dmg *= 0.1
        p2["territory"] -= dmg; s["logs"].insert(0, f">> MARCHED: -{dmg:.1f}")
    elif cmd == "OCCUPY":
        if p1["military"] >= 20:
            p1["military"] -= 20; steal = max(p2["territory"] * 0.2, 40.0)
            p2["territory"] -= steal; p1["colony"] += steal; s["logs"].insert(0, ">> AREA OCCUPIED.")
    elif cmd == "NUKE":
        p2["territory"] *= 0.15; p1["nuke_point"] = 0; s["logs"].insert(0, ">> NUKE EXECUTED.")

    s["player_ap"] -= 1
    if s["player_ap"] <= 0:
        # 敵AIの反撃
        dmg_to_p1 = (p2["territory"] * 0.1) if s["difficulty"] == "DEUS" else 15.0
        if p1["shield_active"]: dmg_to_p1 *= 0.5
        p1["territory"] -= dmg_to_p1
        s["logs"].insert(0, f"<< ENEMY ATTACK: -{dmg_to_p1:.1f}")
        s["player_ap"], s["turn"], p1["shield_active"] = s["max_ap"], s["turn"] + 1, False

# --- 5. インターフェース ---
if s["difficulty"] is None:
    st.title("LEVEL SELECT")
    if st.button("MINOR", use_container_width=True): s["difficulty"] = "MINOR"; p2["territory"] = 150.0; st.rerun()
    if st.button("MAJOR", use_container_width=True): s["difficulty"] = "MAJOR"; st.rerun()
    if st.button("DEUS", use_container_width=True): s["difficulty"] = "DEUS"; p2["territory"] = 2500.0; st.rerun()
elif s["faction"] is None:
    st.title("FACTION SELECT")
    if st.button("ALLIES", use_container_width=True): s["faction"] = "ALLIES"; st.rerun()
    if st.button("AXIS", use_container_width=True): s["faction"] = "AXIS"; st.rerun()
    if st.button("SOVIET", use_container_width=True): s["faction"] = "SOVIET"; s["player_ap"] = 1; s["max_ap"] = 1; st.rerun()
else:
    # 敵軍情報
    st.markdown(f'<div class="enemy-banner"><span class="enemy-text">DEUS: {p2["territory"]:.0f}</span></div>', unsafe_allow_html=True)
    
    # 自軍情報
    st.markdown(f'<div class="status-row"><div><span class="stat-label">MAIN</span><span class="stat-val">{p1["territory"]:.0f}</span></div><div><span class="stat-label">COLONY</span><span class="stat-val">{p1["colony"]:.0f}</span></div></div>', unsafe_allow_html=True)
    
    # 核兵器開発進行状況（青色ゲージ）
    st.markdown('<p class="nuke-label">NUCLEAR DEVELOPMENT PROGRESS</p>', unsafe_allow_html=True)
    st.progress(min(p1['nuke_point']/200.0, 1.0))

    if p1["territory"] <= 0:
        st.error("DEFEATED. NEXT TIME, BE RUTHLESS.")
        if st.button("REBOOT", use_container_width=True): st.session_state.clear(); st.rerun()
    elif p2["territory"] <= 0:
        st.success("VICTORY. THE WORLD IS YOURS.")
        if st.button("REBOOT", use_container_width=True): st.session_state.clear(); st.rerun()
    else:
        st.write(f"TURN: {s['turn']} | AP: {s['player_ap']}")
        
        # 核攻撃コマンド（チャージ完了時のみ）
        if p1["nuke_point"] >= 200:
            if st.button("☢️ EXECUTE NUKE", type="primary", use_container_width=True): player_step("NUKE"); st.rerun()
        
        # 基本コマンド
        c1, c2 = st.columns(2)
        if c1.button("EXPAND", use_container_width=True): player_step("EXPAND"); st.rerun()
        if c2.button("DEFEND", use_container_width=True): player_step("DEFEND"); st.rerun()
        if c1.button("MARCH", use_container_width=True): player_step("MARCH"); st.rerun()
        if c2.button("OCCUPY", use_container_width=True): player_step("OCCUPY"); st.rerun()

    # ログ
    st.write("---")
    log_html = "".join([f'<div>{log}</div>' for log in s["logs"][:2]])
    st.markdown(f'<div class="log-box">{log_html}</div>', unsafe_allow_html=True)
