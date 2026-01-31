import streamlit as st
import random
import base64

# --- 1. 画面構成・スマホ最適化スタイル ---
st.set_page_config(page_title="DEUS: COMMANDER", layout="centered")

st.markdown("""
    <style>
    html, body, [data-testid="stAppViewContainer"] {
        background-color: #000; color: #FFF;
    }
    .stAudio { display: none; } 
    /* 敵ステータス */
    .enemy-banner {
        background-color: #300; border: 2px solid #F00;
        padding: 10px; text-align: center; margin: -50px -15px 15px -15px;
    }
    .enemy-text { color: #F00; font-weight: bold; font-size: 1.2rem; }
    /* 本国ステータス */
    .status-row {
        display: flex; justify-content: space-around;
        background: #111; border: 1px solid #d4af37;
        padding: 10px; margin-bottom: 10px; border-radius: 8px;
    }
    .stat-val { color: #d4af37; font-weight: bold; font-size: 1.1rem; }
    /* ボタン内テキストの調整 */
    div[data-testid="column"] button, div[data-testid="stVerticalBlock"] button {
        height: auto !important; padding: 10px !important;
        background-color: #1a1a1a !important; color: #FFF !important;
        border: 1px solid #d4af37 !important; border-radius: 8px !important;
        white-space: normal !important; word-wrap: break-word !important;
        text-align: left !important;
    }
    .btn-desc { font-size: 0.7rem; color: #aaa; display: block; margin-top: 4px; }
    /* メッセージ */
    .victory-msg { color: #ffd700; font-size: 1.5rem; font-weight: bold; text-align: center; border: 3px double #ffd700; padding: 20px; background: rgba(255, 215, 0, 0.1); }
    .defeat-msg { color: #ff0000; font-size: 1.3rem; font-weight: bold; text-align: center; border: 3px double #ff0000; padding: 20px; background: rgba(255, 0, 0, 0.1); }
    </style>
    """, unsafe_allow_html=True)

# --- 2. BGM再生システム (サイドバー固定) ---
try:
    with open('Vidnoz_AIMusic.mp3', 'rb') as f:
        st.sidebar.title("🎵 AUDIO CONTROL")
        st.sidebar.audio(f.read(), format='audio/mp3', loop=True)
        st.sidebar.caption("※スマホは上の再生ボタンをタップして起動")
except:
    st.sidebar.error("BGMファイル未検出")

# --- 3. システム初期化 ---
if 'state' not in st.session_state:
    st.session_state.state = {
        "p1": {"territory": 100.0, "military": 0.0, "colony": 20.0, "nuke_point": 0, "shield_active": False},
        "p2": {"territory": 300.0, "military": 100.0},
        "turn": 1, "logs": ["作戦開始。難易度と陣営を選んでください。"],
        "player_ap": 2, "max_ap": 2, "difficulty": None, "faction": None
    }

s = st.session_state.state
p1, p2 = s["p1"], s["p2"]

# --- 4. ゲームロジック ---
def player_step(cmd):
    expand_mul = 2.0 if s["faction"] == "社会主義国" else 1.0
    march_mul = 2.0 if s["faction"] in ["枢軸国", "社会主義国"] else 1.0
    nuke_mul = 2.0 if s["faction"] == "連合国" else 1.0

    if cmd == "EXPAND":
        p1["military"] += 25.0 * expand_mul; p1["nuke_point"] += 20 * nuke_mul
        s["logs"].insert(0, f"🛠 軍拡：戦力UP & 核開発進行")
    elif cmd == "DEFEND": p1["shield_active"] = True; s["logs"].insert(0, "🛡 防衛：次の敵攻撃を半減")
    elif cmd == "MARCH":
        dmg = ((p1["military"] * 0.5) + (p1["colony"] * 0.6)) * march_mul
        if s["difficulty"] == "超大国": dmg *= 0.1
        p2["territory"] -= dmg; s["logs"].insert(0, f"⚔️ 進軍：敵に{dmg:.1f}のダメージ")
    elif cmd == "OCCUPY":
        if p1["military"] >= 20:
            p1["military"] -= 20; steal = max(p2["territory"] * 0.2, 40.0)
            p2["territory"] -= steal; p1["colony"] += steal; s["logs"].insert(0, "🚩 占領：敵地を奪い緩衝材にする")
    elif cmd == "NUKE":
        p2["territory"] *= 0.15; p1["nuke_point"] = 0; s["logs"].insert(0, "☢️ 核執行：敵領土の85%を壊滅")

    s["player_ap"] -= 1
    if s["player_ap"] <= 0:
        dmg_to_p1 = (p2["territory"] * 0.1) if s["difficulty"] == "超大国" else 15.0
        if p1["shield_active"]: dmg_to_p1 *= 0.5
        p1["territory"] -= dmg_to_p1
        s["logs"].insert(0, f"⚠️ 敵反撃：本国に{dmg_to_p1:.1f}の被害")
        s["player_ap"], s["turn"], p1["shield_active"] = s["max_ap"], s["turn"] + 1, False

# --- 5. UI構築 ---
# A. 難易度選択 (隠さないようにリスト表示)
if s["difficulty"] is None:
    st.title("🚩 難易度（国力規模）選択")
    if st.button("【小国】 難易度：低\n敵の領土が少なく、初心者向けの作戦規模です。", use_container_width=True):
        s["difficulty"] = "小国"; p2["territory"] = 150.0; st.rerun()
    if st.button("【大国】 難易度：中\n標準的な敵国規模。戦略的な資源管理が求められます。", use_container_width=True):
        s["difficulty"] = "大国"; st.rerun()
    if st.button("【超大国】 難易度：絶望\nDEUSの本体。正面突破はほぼ不可能、核と諜報が鍵です。", use_container_width=True):
        s["difficulty"] = "超大国"; p2["territory"] = 2500.0; st.rerun()

# B. 陣営選択
elif s["faction"] is None:
    st.title("🛡️ 陣営プロトコル選択")
    if st.button("【連合国】\n核兵器開発速度が2倍。圧倒的な科学力で終焉をもたらす。", use_container_width=True):
        s["faction"] = "連合国"; st.rerun()
    if st.button("【枢軸国】\n進軍ダメージが2倍。電撃作戦で敵領土を直接削り取る。", use_container_width=True):
        s["faction"] = "枢軸国"; st.rerun()
    if st.button("【社会主義国】\n全行動の効果が2倍。ただし1ターンに1回しか行動できない。", use_container_width=True):
        s["faction"] = "社会主義国"; s["player_ap"] = 1; s["max_ap"] = 1; st.rerun()

# C. メインゲーム画面
else:
    st.markdown(f'<div class="enemy-banner"><span class="enemy-text">敵対AI [DEUS]: {p2["territory"]:.0f} pts</span></div>', unsafe_allow_html=True)
    st.markdown(f'<div class="status-row"><div>{s["faction"]} 本国: <span class="stat-val">{p1["territory"]:.0f}</span></div><div>緩衝地: <span class="stat-val">{p1["colony"]:.0f}</span></div></div>', unsafe_allow_html=True)
    
    # 青いゲージ：核兵器開発進行状況
    st.write(f"☢️ 核兵器開発進行状況: {p1['nuke_point']}/200")
    st.progress(min(p1['nuke_point']/200.0, 1.0))

    if p1["territory"] <= 0:
        st.markdown('<div class="defeat-msg">【国家崩壊】<br>司令官、あなたの意志は受け継がれる…<br>次はもっと、冷酷になれるはずだ。</div>', unsafe_allow_html=True)
        if st.button("雪辱を果たす (REBOOT)", use_container_width=True): st.session_state.clear(); st.rerun()
    elif p2["territory"] <= 0:
        st.markdown('<div class="victory-msg">【DEUS殲滅】<br>世界は我らの掌にある！<br>略奪と勝利の凱歌を響かせよ！</div>', unsafe_allow_html=True)
        if st.button("さらなる支配へ (REBOOT)", use_container_width=True): st.session_state.clear(); st.rerun()
    else:
        st.write(f"**Turn {s['turn']} | 残り行動数: {s['player_ap']}**")
        
        # 核使用ボタン（ポイントが溜まった時だけ出現）
        if p1["nuke_point"] >= 200:
            if st.button("☢️ 最終宣告執行\n【核攻撃】敵領土の85%を即座に消滅させる。", type="primary", use_container_width=True):
                player_step("NUKE"); st.rerun()
        
        # 各アクションボタンと説明文
        if st.button("🛠 軍拡\n戦力値を大幅にアップし、核開発ポイントを貯める。", use_container_width=True):
            player_step("EXPAND"); st.rerun()
        if st.button("🛡 防衛\n迎撃体制を整え、次のターンの敵の攻撃ダメージを半減させる。", use_container_width=True):
            player_step("DEFEND"); st.rerun()
        if st.button("⚔️ 進軍\n現在の戦力と緩衝地の規模に応じて敵領土にダメージを与える。", use_container_width=True):
            player_step("MARCH"); st.rerun()
        if st.button("🚩 占領\n戦力を消費して敵領土を奪い、自軍の「緩衝地」に変換する。", use_container_width=True):
            player_step("OCCUPY"); st.rerun()

    st.write("---")
    log_html = "".join([f'<div>{log}</div>' for log in s["logs"][:3]])
    st.markdown(f'<div class="log-box">{log_html}</div>', unsafe_allow_html=True)
