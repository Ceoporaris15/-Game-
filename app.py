import streamlit as st
import random
import base64

# --- 1. 極限コンパクト・レイアウト ---
st.set_page_config(page_title="DEUS", layout="centered")

st.markdown("""
    <style>
    html, body, [data-testid="stAppViewContainer"] {
        background-color: #000; color: #FFF; overflow: hidden;
    }
    .stAudio { display: none; } 
    /* 敵軍：さらにタイトに */
    .enemy-banner {
        background-color: #200; border-bottom: 1px solid #F00;
        padding: 4px; text-align: center; margin: -55px -15px 5px -15px;
    }
    .enemy-text { color: #F00; font-weight: bold; font-size: 1rem; letter-spacing: 3px; }
    /* ステータス：1行に凝縮 */
    .status-row {
        display: flex; justify-content: space-around;
        background: #111; border: 1px solid #d4af37;
        padding: 3px; margin-bottom: 5px; border-radius: 4px;
    }
    .stat-label { font-size: 0.6rem; color: #888; margin-right: 5px; }
    .stat-val { color: #d4af37; font-weight: bold; font-size: 0.9rem; }
    /* ボタン：極小サイズ化 */
    div[data-testid="column"] button, div[data-testid="stVerticalBlock"] button {
        height: 32px !important; font-size: 0.75rem !important;
        padding: 0px !important; margin-bottom: -10px !important;
        background-color: #1a1a1a !important; color: #d4af37 !important;
        border: 1px solid #d4af37 !important; border-radius: 2px !important;
    }
    /* 核ゲージ */
    .stProgress { height: 10px !important; margin-bottom: 5px !important; }
    .stProgress > div > div > div > div { background-color: #007BFF; }
    .nuke-title { color: #007BFF; font-weight: bold; font-size: 0.7rem; margin: 2px 0; }
    
    /* ログ：フォントサイズを下げて視認性確保 */
    .log-box {
        background: #000; border-left: 2px solid #d4af37;
        padding: 5px; height: 75px; font-size: 0.75rem; color: #CCC; line-height: 1.2;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 2. 確定BGM同期プロトコル ---
def setup_audio_engine():
    try:
        with open('Vidnoz_AIMusic.mp3', 'rb') as f:
            data = f.read()
            b64 = base64.b64encode(data).decode()
            # JSで再生を強制
            audio_html = f"""
                <audio id="bgm" loop>
                    <source src="data:audio/mp3;base64,{b64}" type="audio/mp3">
                </audio>
                <script>
                    var audio = document.getElementById('bgm');
                    audio.volume = 0.5;
                    window.parent.document.addEventListener('touchstart', function() {{
                        audio.play();
                    }}, {{once: true}});
                    window.parent.document.addEventListener('click', function() {{
                        audio.play();
                    }}, {{once: true}});
                </script>
            """
            st.components.v1.html(audio_html, height=0)
    except:
        st.sidebar.error("BGM ERROR")

# --- 3. システム初期化 ---
if 'state' not in st.session_state:
    st.session_state.state = {
        "p1": {"territory": 150.0, "military": 0.0, "colony": 30.0, "nuke_point": 0, "shield_active": False},
        "p2": {"territory": 600.0}, # 大国情報修正済み
        "turn": 1, "logs": ["SYSTEM READY. 画面タップでBGM開始。"],
        "player_ap": 2, "max_ap": 2, "difficulty": None, "faction": None, "started": False
    }

s = st.session_state.state
p1, p2 = s["p1"], s["p2"]

# --- 4. ロジック ---
def player_step(cmd):
    mul_exp = 2.0 if s["faction"] == "社会主義国" else 1.0
    mul_mar = 2.0 if s["faction"] in ["枢軸国", "社会主義国"] else 1.0
    mul_nuk = 2.0 if s["faction"] == "連合国" else 1.0

    if cmd == "EXP":
        p1["military"] += 25.0 * mul_exp; p1["nuke_point"] += 20 * mul_nuk
        s["logs"].insert(0, f"🛠軍拡: 核P+{20*mul_nuk}")
    elif cmd == "DEF": p1["shield_active"] = True; s["logs"].insert(0, "🛡防衛: シールド展開")
    elif cmd == "MAR":
        dmg = ((p1["military"] * 0.5) + (p1["colony"] * 0.6)) * mul_mar
        if s["difficulty"] == "超大国": dmg *= 0.1
        p2["territory"] -= dmg; s["logs"].insert(0, f"⚔️進軍: 敵に{dmg:.0f}ダメ")
    elif cmd == "OCC":
        if p1["military"] >= 20:
            p1["military"] -= 20; steal = max(p2["territory"] * 0.2, 40.0)
            p2["territory"] -= steal; p1["colony"] += steal; s["logs"].insert(0, "🚩占領: 緩衝地拡大")
    elif cmd == "NUK":
        p2["territory"] *= 0.15; p1["nuke_point"] = 0; s["logs"].insert(0, "☢️核執行: 敵地消滅")

    s["player_ap"] -= 1
    if s["player_ap"] <= 0:
        dmg_to_p1 = (p2["territory"] * 0.08) if s["difficulty"] == "超大国" else 12.0
        if p1["shield_active"]: dmg_to_p1 *= 0.5
        p1["territory"] -= dmg_to_p1
        s["logs"].insert(0, f"⚠️反撃: 本国-{dmg_to_p1:.0f}")
        s["player_ap"], s["turn"], p1["shield_active"] = s["max_ap"], s["turn"] + 1, False

# --- 5. インターフェース ---
setup_audio_engine()

if s["difficulty"] is None:
    st.title("難易度選択")
    if st.button("小国", use_container_width=True): s["difficulty"] = "小国"; p2["territory"] = 200.0; st.rerun()
    if st.button("大国", use_container_width=True): s["difficulty"] = "大国"; p2["territory"] = 650.0; st.rerun()
    if st.button("超大国", use_container_width=True): s["difficulty"] = "超大国"; p2["territory"] = 3500.0; st.rerun()
elif s["faction"] is None:
    st.title("陣営プロトコル")
    if st.button("連合国", use_container_width=True): s["faction"] = "連合国"; st.rerun()
    if st.button("枢軸国", use_container_width=True): s["faction"] = "枢軸国"; st.rerun()
    if st.button("社会主義国", use_container_width=True): s["faction"] = "社会主義国"; s["player_ap"] = 1; s["max_ap"] = 1; st.rerun()
else:
    # 敵軍
    st.markdown(f'<div class="enemy-banner"><span class="enemy-text">DEUS: {p2["territory"]:.0f}</span></div>', unsafe_allow_html=True)
    # 自軍
    st.markdown(f'<div class="status-row"><div><span class="stat-label">本国</span><span class="stat-val">{p1["territory"]:.0f}</span></div><div><span class="stat-label">緩衝</span><span class="stat-val">{p1["colony"]:.0f}</span></div></div>', unsafe_allow_html=True)
    
    # 核
    st.markdown('<p class="nuke-title">☢️ 核開発進行状況</p>', unsafe_allow_html=True)
    st.progress(min(p1['nuke_point']/200.0, 1.0))

    if p1["territory"] <= 0:
        st.error("【敗北】次はもっと冷酷に。")
        if st.button("REBOOT", use_container_width=True): st.session_state.clear(); st.rerun()
    elif p2["territory"] <= 0:
        st.success("【勝利】世界は貴公のもの。")
        if st.button("REBOOT", use_container_width=True): st.session_state.clear(); st.rerun()
    else:
        st.caption(f"T-{s['turn']} | AP: {s['player_ap']}")
        
        if p1["nuke_point"] >= 200:
            if st.button("☢️ 最終宣告執行", type="primary", use_container_width=True): player_step("NUK"); st.rerun()
        
        # 極小ボタン配置
        c1, c2 = st.columns(2)
        if c1.button("🛠軍拡", use_container_width=True): player_step("EXP"); st.rerun()
        if c2.button("🛡防衛", use_container_width=True): player_step("DEF"); st.rerun()
        if c1.button("⚔️進軍", use_container_width=True): player_step("MAR"); st.rerun()
        if c2.button("🚩占領", use_container_width=True): player_step("OCC"); st.rerun()

    # ログ
    st.write("---")
    log_html = "".join([f'<div>{log}</div>' for log in s["logs"][:3]])
    st.markdown(f'<div class="log-box">{log_html}</div>', unsafe_allow_html=True)
