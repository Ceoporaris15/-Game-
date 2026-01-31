import streamlit as st
import random
import base64

# --- 1. 画面構成・モバイル最適化 ---
st.set_page_config(page_title="DEUS: COMMANDER", layout="centered")

st.markdown("""
    <style>
    html, body, [data-testid="stAppViewContainer"] {
        background-color: #000; color: #FFF;
    }
    .enemy-banner {
        background-color: #300; border: 2px solid #F00;
        padding: 10px; text-align: center; margin: -50px -15px 15px -15px;
    }
    .enemy-text { color: #F00; font-weight: bold; font-size: 1.2rem; letter-spacing: 2px; }
    .status-row {
        display: flex; justify-content: space-around;
        background: #111; border: 1px solid #d4af37;
        padding: 8px; margin-bottom: 10px; border-radius: 5px;
    }
    .stat-val { color: #d4af37; font-weight: bold; }
    /* ボタンデザイン */
    div[data-testid="column"] button {
        height: 60px !important; font-size: 0.85rem !important;
        background-color: #1a1a1a !important; color: #FFF !important;
        border: 1px solid #d4af37 !important; border-radius: 8px !important;
    }
    .stProgress > div > div > div > div { background-color: #007BFF; }
    .log-box {
        background: #050505; border-left: 3px solid #d4af37;
        padding: 10px; height: 120px; font-size: 0.85rem; color: #EEE; overflow-y: auto;
    }
    /* メッセージ装飾 */
    .victory-msg { color: #ffd700; font-size: 1.6rem; font-weight: bold; text-align: center; border: 3px double #ffd700; padding: 20px; background: rgba(255, 215, 0, 0.1); }
    .defeat-msg { color: #ff0000; font-size: 1.4rem; font-weight: bold; text-align: center; border: 3px double #ff0000; padding: 20px; background: rgba(255, 0, 0, 0.1); }
    </style>
    """, unsafe_allow_html=True)

# --- 2. 確実なBGM再生システム ---
def setup_audio():
    try:
        with open('Vidnoz_AIMusic.mp3', 'rb') as f:
            data = f.read()
            # 操作バーをあえて出し、ユーザーに一度だけ再生ボタンを押させるのが最も確実です。
            # しかし、デザインを損なわないよう「BGM制御」セクションにまとめます。
            st.sidebar.title("🎵 AUDIO CONTROL")
            st.sidebar.audio(data, format='audio/mp3', loop=True)
            st.sidebar.caption("※スマホで音が鳴らない場合は、上の再生ボタンを一度タップしてください。")
    except FileNotFoundError:
        st.error("❗ Vidnoz_AIMusic.mp3 が見つかりません。GitHubのファイル名を確認してください。")

setup_audio()

# --- 3. システム初期化 ---
if 'state' not in st.session_state:
    st.session_state.state = {
        "p1": {"territory": 100.0, "military": 0.0, "colony": 20.0, "nuke_point": 0, "shield_active": False},
        "p2": {"territory": 300.0, "military": 100.0, "colony": 50.0},
        "turn": 1, "logs": ["システム待機中... 難易度を選択して作戦を開始せよ。"],
        "player_ap": 2, "max_ap": 2, "difficulty": None, "faction": None
    }

s = st.session_state.state
p1, p2 = s["p1"], s["p2"]

# --- 4. ゲームロジック ---
def player_step(cmd):
    # 陣営補正
    expand_mul = 2.0 if s["faction"] == "社会主義国" else 1.0
    march_mul = 2.0 if s["faction"] in ["枢軸国", "社会主義国"] else 1.0
    nuke_mul = 2.0 if s["faction"] == "連合国" else 1.0

    if cmd == "EXPAND":
        p1["military"] += 25.0 * expand_mul; p1["nuke_point"] += 20 * nuke_mul
        s["logs"].insert(0, f"🛠 軍拡：戦力を増強。核承認ポイント +{20*nuke_mul}")
    elif cmd == "DEFEND": p1["shield_active"] = True; s["logs"].insert(0, "🛡 防衛：迎撃態勢に移行。")
    elif cmd == "MARCH":
        dmg = ((p1["military"] * 0.5) + (p1["colony"] * 0.6)) * march_mul
        if s["difficulty"] == "超大国": dmg *= 0.1
        p2["territory"] -= dmg; s["logs"].insert(0, f"⚔️ 進軍：敵拠点を強襲、{dmg:.1f}のダメージ。")
    elif cmd == "OCCUPY":
        if p1["military"] >= 20:
            p1["military"] -= 20; steal = max(p2["territory"] * 0.2, 40.0)
            p2["territory"] -= steal; p1["colony"] += steal; s["logs"].insert(0, "🚩 占領：敵の資源を奪取し、緩衝地帯を拡大。")
    elif cmd == "NUKE":
        p2["territory"] *= 0.15; p1["nuke_point"] = 0; s["logs"].insert(0, "☢️ 核執行：DEUSの演算回路が蒸発。")

    s["player_ap"] -= 1
    if s["player_ap"] <= 0:
        # 簡易的なAIターン
        dmg_to_p1 = (p2["territory"] * 0.1) if s["difficulty"] == "超大国" else 15.0
        if p1["shield_active"]: dmg_to_p1 *= 0.5
        p1["territory"] -= dmg_to_p1
        s["logs"].insert(0, f"⚠️ DEUS反撃：本国が{dmg_to_p1:.1f}の打撃を感知。")
        s["player_ap"], s["turn"], p1["shield_active"] = s["max_ap"], s["turn"] + 1, False

# --- 5. UI構築 ---
if s["difficulty"] is None:
    st.title("🚩 OPERATION DEUS")
    st.info("※BGMを流すには、左側のメニューにある再生ボタンを一度押してください。")
    cols = st.columns(3)
    if cols[0].button("小国"): s["difficulty"] = "小国"; p2["territory"] = 150.0; st.rerun()
    if cols[1].button("大国"): s["difficulty"] = "大国"; st.rerun()
    if cols[2].button("超大国"): s["difficulty"] = "超大国"; p2["territory"] = 2500.0; st.rerun()
elif s["faction"] is None:
    st.title("🛡️ FACTION SELECT")
    if st.button("連合国", use_container_width=True): s["faction"] = "連合国"; st.rerun()
    if st.button("枢軸国", use_container_width=True): s["faction"] = "枢軸国"; st.rerun()
    if st.button("社会主義国", use_container_width=True): s["faction"] = "社会主義国"; s["player_ap"] = 1; s["max_ap"] = 1; st.rerun()
else:
    st.markdown(f'<div class="enemy-banner"><span class="enemy-text">DEUS: {p2["territory"]:.0f} pts</span></div>', unsafe_allow_html=True)
    st.markdown(f'<div class="status-row"><div>{s["faction"]} 本国: <span class="stat-val">{p1["territory"]:.0f}</span></div><div>緩衝: <span class="stat-val">{p1["colony"]:.0f}</span></div></div>', unsafe_allow_html=True)
    
    st.progress(min(p1['nuke_point']/200.0, 1.0))

    if p1["territory"] <= 0:
        st.markdown('<div class="defeat-msg">【国家崩壊】<br>司令官、あなたの意志は受け継がれる…<br>次はもっと、冷酷になれるはずだ。</div>', unsafe_allow_html=True)
        if st.button("雪辱を果たす (REBOOT)", use_container_width=True): st.session_state.clear(); st.rerun()
    elif p2["territory"] <= 0:
        st.markdown('<div class="victory-msg">【DEUS殲滅】<br>世界は我らの掌にある！<br>略奪と勝利の凱歌を響かせよ！</div>', unsafe_allow_html=True)
        if st.button("さらなる支配へ (REBOOT)", use_container_width=True): st.session_state.clear(); st.rerun()
    else:
        st.write(f"**Turn {s['turn']} | AP: {s['player_ap']}**")
        if p1["nuke_point"] >= 200:
            if st.button("☢️ 最終宣告執行", type="primary", use_container_width=True): player_step("NUKE"); st.rerun()
        
        c = st.columns(3)
        if c[0].button("🛠軍拡"): player_step("EXPAND"); st.rerun()
        if c[1].button("🛡防衛"): player_step("DEFEND"); st.rerun()
        if c[2].button("⚔️進軍"): player_step("MARCH"); st.rerun()
        if st.button("🚩 敵領土を占領", use_container_width=True): player_step("OCCUPY"); st.rerun()
    
    st.write("---")
    log_html = "".join([f'<div>{log}</div>' for log in s["logs"][:3]])
    st.markdown(f'<div class="log-box">{log_html}</div>', unsafe_allow_html=True)
