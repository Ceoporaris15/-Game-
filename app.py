import streamlit as st
import random
import base64

# --- 1. 画面構成・モバイル最適化 ---
st.set_page_config(page_title="DEUS: FINAL CONSOLE", layout="centered")

st.markdown("""
    <style>
    html, body, [data-testid="stAppViewContainer"] {
        background-color: #000; color: #FFF;
    }
    /* 再生バーを隠し、UIをタイトに */
    .stAudio { display: none; } 
    .enemy-banner {
        background-color: #300; border: 2px solid #F00;
        padding: 8px; text-align: center; margin: -50px -15px 10px -15px;
    }
    .enemy-text { color: #F00; font-weight: bold; font-size: 1.2rem; text-shadow: 0 0 10px #F00; }
    .status-row {
        display: flex; justify-content: space-around;
        background: #111; border: 1px solid #d4af37;
        padding: 5px; margin-bottom: 5px; border-radius: 5px;
    }
    .stat-val { color: #d4af37; font-weight: bold; }
    /* スマホでも押しやすい大きなボタン */
    div[data-testid="column"] button {
        height: 55px !important; font-size: 0.8rem !important;
        font-weight: 900 !important; background-color: #222 !important;
        color: #FFF !important; border: 1px solid #d4af37 !important;
        box-shadow: 0 0 5px #d4af37;
    }
    .stProgress > div > div > div > div { background-color: #007BFF; }
    .log-box {
        background: #050505; border-left: 3px solid #d4af37;
        padding: 8px; height: 110px; font-size: 0.8rem; color: #EEE; overflow-y: auto;
    }
    /* 勝利・敗北メッセージの特別装飾 */
    .victory-msg { color: #ffd700; font-size: 1.5rem; font-weight: bold; text-align: center; padding: 20px; border: 2px solid #ffd700; background: #221a00; }
    .defeat-msg { color: #ff0000; font-size: 1.3rem; font-weight: bold; text-align: center; padding: 20px; border: 2px solid #ff0000; background: #1a0000; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. スマホ対応ステルスBGMエンジン ---
def play_bgm_mobile():
    try:
        with open('Vidnoz_AIMusic.mp3', 'rb') as f:
            data = f.read()
            b64 = base64.b64encode(data).decode()
            # スマホの「タップで再生」制限を突破するためのJS
            md = f"""
                <audio loop id="bgm-player" preload="auto">
                    <source src="data:audio/mp3;base64,{b64}" type="audio/mp3">
                </audio>
                <script>
                    var audio = document.getElementById('bgm-player');
                    audio.volume = 0.5;
                    // スマホ・PC共通：最初のクリック/タップで再生開始
                    document.addEventListener('click', function() {{
                        audio.play();
                    }}, {{ once: true }});
                    // すでに許可されている場合用
                    audio.play().catch(function(e) {{ console.log("Autoplay blocked, waiting for touch."); }});
                </script>
                """
            st.components.v1.html(md, height=0)
    except FileNotFoundError:
        st.info("🎵 BGM未検出: GitHubにファイルを置いてください。")

play_bgm_mobile()

# --- 3. システムステート ---
if 'state' not in st.session_state:
    st.session_state.state = {
        "p1": {"territory": 100.0, "military": 0.0, "colony": 20.0, "nuke_point": 0, "shield_active": False},
        "p2": {"territory": 300.0, "military": 100.0, "colony": 50.0},
        "turn": 1, "logs": ["システム待機中... 難易度を選択して起動してください。"],
        "player_ap": 2, "max_ap": 2, "wmd_charging": False,
        "difficulty": None, "faction": None
    }

s = st.session_state.state
p1, p2 = s["p1"], s["p2"]

# --- 4. ロジック ---
def apply_damage_to_player(dmg):
    success_rate = 0.15 if s["faction"] == "枢軸国" else 0.3
    if p1["shield_active"]:
        if random.random() < success_rate:
            dmg = max(0, dmg - 40); s["logs"].insert(0, "🛡️ 防衛成功: 最小限の被害")
        else: s["logs"].insert(0, "❌ 防衛失敗: 深刻な打撃")
    if p1["colony"] > 0:
        shield_amt = min(p1["colony"], dmg); p1["colony"] -= shield_amt; dmg -= shield_amt
    if dmg > 0: p1["territory"] = max(0, p1["territory"] - dmg)
    s["logs"].insert(0, f"💥 警告: 本国被弾 -{dmg:.1f}pts")

def ai_logic():
    actions = 1 if s["difficulty"] == "小国" else (2 if s["difficulty"] == "大国" else 6)
    for _ in range(actions):
        if p2["territory"] <= 0: break
        if random.random() < 0.25 and p1["nuke_point"] > 30:
            p1["nuke_point"] = max(0, p1["nuke_point"] - 50); s["logs"].insert(0, "🕵️ DEUS工作: 核承認回路をハック")
            continue
        if s["wmd_charging"]:
            nuke_dmg = p1["territory"] * (0.95 if s["difficulty"] == "超大国" else 0.5)
            apply_damage_to_player(nuke_dmg); s["wmd_charging"] = False
        else:
            if random.random() < (0.7 if s["difficulty"] == "超大国" else 0.2):
                s["wmd_charging"] = True; s["logs"].insert(0, "🚨 DEUS: 戦略核充填を確認")
            else:
                p2_power = 2.5 if s["difficulty"] == "超大国" else 1.0
                apply_damage_to_player(p2["military"] * 0.2 * p2_power)

def player_step(cmd):
    expand_mul = 2.0 if s["faction"] == "社会主義国" else 1.0
    march_mul = 2.0 if s["faction"] in ["枢軸国", "社会主義国"] else 1.0
    nuke_mul = 2.0 if s["faction"] == "連合国" else 1.0
    spy_success_base = 0.5 if s["faction"] == "社会主義国" else (0.1 if s["faction"] == "連合国" else 0.25)

    if cmd == "EXPAND":
        p1["military"] += 25.0 * expand_mul; p1["nuke_point"] += 20 * nuke_mul
        s["logs"].insert(0, f"🛠 軍拡: 国家機能を闘争へ最適化")
    elif cmd == "DEFEND": p1["shield_active"] = True; s["logs"].insert(0, "🛡 防衛: 迎撃ミサイル展開")
    elif cmd == "MARCH":
        dmg = ((p1["military"] * 0.5) + (p1["colony"] * 0.6)) * march_mul
        if s["difficulty"] == "超大国": dmg *= 0.1
        p2["territory"] -= dmg; s["logs"].insert(0, f"⚔️ 進軍: DEUSの防壁を粉砕 -{dmg:.1f}")
    elif cmd == "OCCUPY":
        if p1["military"] >= 20:
            p1["military"] -= 20; steal = max(p2["territory"] * 0.2, 40.0)
            p2["territory"] -= steal; p1["colony"] += steal; s["logs"].insert(0, "🚩 占領: 敵領土を支配下に置く")
    elif cmd == "SPY":
        if random.random() < spy_success_base:
            if s["wmd_charging"]: s["wmd_charging"] = False; s["logs"].insert(0, "🕵️ 潜入成功: DEUSの核を停止")
            else: p1["nuke_point"] += 40; p2["territory"] -= 20; s["logs"].insert(0, "🕵️ 諜報成功: 技術奪取")
        else: s["logs"].insert(0, "🕵️ 潜入失敗: 工作員との通信途絶")
    elif cmd == "NUKE":
        p2["territory"] *= 0.15; p1["nuke_point"] = 0; s["logs"].insert(0, "☢️ 最終宣告: 世界が白光に包まれる")

    s["player_ap"] -= 1
    if s["player_ap"] <= 0:
        ai_logic(); s["player_ap"], s["turn"], p1["shield_active"] = s["max_ap"], s["turn"] + 1, False

# --- 5. UI ---
if s["difficulty"] is None:
    st.title("🚩 STRATEGIC SYSTEM")
    st.write("ボタンをタップしてシステムを起動してください。")
    if st.button("小国（難易度：低）", use_container_width=True): s["difficulty"] = "小国"; p2["territory"] = 150.0; st.rerun()
    if st.button("大国（難易度：中）", use_container_width=True): s["difficulty"] = "大国"; st.rerun()
    if st.button("超大国（難易度：絶望）", use_container_width=True): s["difficulty"] = "超大国"; p2["territory"] = 2500.0; st.rerun()
elif s["faction"] is None:
    st.title("🛡️ 陣営選択")
    if st.button("連合国 (核2倍 / スパイ弱)", use_container_width=True): s["faction"] = "連合国"; st.rerun()
    if st.button("枢軸国 (進軍2倍 / 防御弱)", use_container_width=True): s["faction"] = "枢軸国"; st.rerun()
    if st.button("社会主義国 (全2倍 / 1回行動)", use_container_width=True): 
        s["faction"] = "社会主義国"; s["player_ap"] = 1; s["max_ap"] = 1; st.rerun()
else:
    st.markdown(f'<div class="enemy-banner"><span class="enemy-text">敵対AI [DEUS]: {p2["territory"]:.0f} pts</span></div>', unsafe_allow_html=True)
    st.markdown(f'<div class="status-row"><div>{s["faction"]} 本国: <span class="stat-val">{p1["territory"]:.0f}</span></div><div>緩衝地: <span class="stat-val">{p1["colony"]:.0f}</span></div></div>', unsafe_allow_html=True)
    
    st.caption("☢️ 核開発進行状態")
    st.progress(min(p1['nuke_point']/200.0, 1.0))

    if p1["territory"] <= 0:
        st.markdown('<div class="defeat-msg">【国家崩壊】<br>司令官、あなたの意志は受け継がれる…<br>次はもっと、冷酷になれるはずだ。</div>', unsafe_allow_html=True)
        if st.button("雪辱を果たす (REBOOT)", use_container_width=True): st.session_state.clear(); st.rerun()
    elif p2["territory"] <= 0:
        st.markdown('<div class="victory-msg">【DEUS殲滅】<br>世界は我らの掌にある！<br>略奪と勝利の凱歌を響かせよ！</div>', unsafe_allow_html=True)
        if st.button("さらなる支配へ (REBOOT)", use_container_width=True): st.session_state.clear(); st.rerun()
    else:
        st.write(f"**Turn {s['turn']} | 残り行動数: {s['player_ap']}**")
        if p1["nuke_point"] >= 200:
            if st.button("☢️ 最終宣告執行", type="primary", use_container_width=True): player_step("NUKE"); st.rerun()
        
        cols = st.columns(3)
        if cols[0].button("🛠軍拡"): player_step("EXPAND"); st.rerun()
        if cols[1].button("🛡防衛"): player_step("DEFEND"); st.rerun()
        if cols[2].button("⚔️進軍"): player_step("MARCH"); st.rerun()
        cols2 = st.columns(2)
        if cols2[0].button("🚩占領"): player_step("OCCUPY"); st.rerun()
        if cols2[1].button("🕵️潜入"): player_step("SPY"); st.rerun()
    
    st.write("---")
    log_html = "".join([f'<div>{log}</div>' for log in s["logs"][:3]])
    st.markdown(f'<div class="log-box">{log_html}</div>', unsafe_allow_html=True)
