import streamlit as st
import random
import base64

# --- 1. レイアウト設定 ---
st.set_page_config(page_title="DEUS", layout="centered")

st.markdown("""
    <style>
    html, body, [data-testid="stAppViewContainer"] { background-color: #000; color: #FFF; }
    .enemy-banner { background-color: #200; border-bottom: 1px solid #F00; padding: 4px; text-align: center; margin: -55px -15px 5px -15px; }
    .enemy-text { color: #F00; font-weight: bold; font-size: 1rem; letter-spacing: 3px; }
    .status-row { display: flex; justify-content: space-around; background: #111; border: 1px solid #d4af37; padding: 2px; margin-bottom: 5px; border-radius: 4px; }
    .stat-label { font-size: 0.6rem; color: #888; margin-right: 4px; }
    .stat-val { color: #d4af37; font-weight: bold; font-size: 0.9rem; }
    .briefing-card { background: #111; border: 1px solid #333; padding: 12px; border-radius: 5px; margin-bottom: 10px; }
    .briefing-title { color: #d4af37; font-weight: bold; font-size: 0.9rem; border-bottom: 1px solid #444; margin-bottom: 5px; padding-bottom: 3px;}
    .briefing-text { font-size: 0.7rem; color: #CCC; line-height: 1.4; }
    div[data-testid="column"] button, div[data-testid="stVerticalBlock"] button {
        height: 35px !important; background-color: #1a1a1a !important; color: #d4af37 !important; border: 1px solid #d4af37 !important;
    }
    .log-box { background: #000; border-top: 1px solid #333; padding: 4px 8px; height: 60px; font-size: 0.75rem; color: #CCC; margin-top: 15px; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. 究極音響エンジン (強制アクティベーション) ---
def trigger_audio(audio_type):
    # ユーザーのクリック直後にAudioContextをレジュームさせるJS
    js_audio = {
        "soft": "playTone(220, 'sine', 0.1);",
        "sharp": "playTone(880, 'square', 0.1);",
        "mute": "stopBGM();"
    }
    st.components.v1.html(f"""
        <script>
        function playTone(freq, type, dur) {{
            const ctx = new (window.AudioContext || window.webkitAudioContext)();
            const osc = ctx.createOscillator();
            const gain = ctx.createGain();
            osc.type = type;
            osc.frequency.setValueAtTime(freq, ctx.currentTime);
            gain.gain.setValueAtTime(0.1, ctx.currentTime);
            gain.gain.exponentialRampToValueAtTime(0.0001, ctx.currentTime + dur);
            osc.connect(gain);
            gain.connect(ctx.destination);
            osc.start();
            osc.stop(ctx.currentTime + dur);
        }}
        function stopBGM() {{
            const bgm = window.parent.document.getElementById('bgm_player');
            if(bgm) {{ bgm.pause(); setTimeout(() => bgm.play(), 5000); }}
        }}
        {js_audio.get(audio_type, '')}
        </script>
    """, height=0)

def setup_bgm():
    try:
        with open('Vidnoz_AIMusic.mp3', 'rb') as f:
            b64 = base64.b64encode(f.read()).decode()
            st.components.v1.html(f"""
                <audio id="bgm_player" loop><source src="data:audio/mp3;base64,{b64}" type="audio/mp3"></audio>
                <script>
                const player = document.getElementById('bgm_player');
                // 親ウィンドウ含めどこをクリックしても再生開始
                const startAudio = () => {{
                    player.play().then(() => {{
                        console.log('BGM Started');
                        window.removeEventListener('click', startAudio);
                    }}).catch(e => console.log('Wait for click'));
                }};
                window.parent.document.addEventListener('click', startAudio);
                window.addEventListener('click', startAudio);
                </script>
            """, height=0)
    except:
        st.error("BGMファイルが見つかりません。")

# --- 3. ステート管理 ---
if 'state' not in st.session_state:
    st.session_state.state = {
        "p1": {"territory": 150.0, "military": 0.0, "colony": 50.0, "nuke_point": 0, "shield": False},
        "p2": {"territory": 800.0, "military": 0.0, "nuke_point": 0, "stun": 0}, 
        "turn": 1, "logs": ["SYSTEM ONLINE. 画面を一度クリックして音響を有効化してください。"],
        "player_ap": 2, "max_ap": 2, "difficulty": None, "faction": None, "phase": "DIFFICULTY"
    }

s = st.session_state.state
p1, p2 = s["p1"], s["p2"]
setup_bgm()

# --- 4. ロジック ---
def player_step(cmd):
    # 陣営補正
    if s["faction"] == "連合国": a, d, o, n, sp = 1.0, 1.0, 1.0, 2.0, 0.60
    elif s["faction"] == "枢軸國": a, d, o, n, sp = 1.5, 0.8, 1.2, 1.0, 0.33
    else: a, d, o, n, sp = 0.5, 0.8, 1.0, 1.0, 0.33

    if cmd == "EXP":
        trigger_audio("soft"); p1["military"] += 25.0 * a; p1["nuke_point"] += 20 * n
        s["logs"].insert(0, f"🛠軍拡: 軍備+{25.0*a:.0f}")
    elif cmd == "DEF":
        trigger_audio("soft"); p1["shield"] = True; s["logs"].insert(0, "🛡防衛: シールド展開。")
    elif cmd == "MAR":
        trigger_audio("sharp"); dmg = max(((p1["military"] * 0.5) + (p1["colony"] * 0.6)) * a + 10.0, 10.0)
        p2["territory"] -= dmg; s["logs"].insert(0, f"⚔️進軍: 敵領土ダメージ。")
    elif cmd == "OCC":
        trigger_audio("soft"); steal = min(((max(p2["territory"] * 0.15, 25.0)) + 10.0) * o, 50.0)
        p1["colony"] += steal; s["logs"].insert(0, f"🚩占領: 緩衝地帯拡張。敵ダメージなし。")
    elif cmd == "SPY":
        trigger_audio("sharp")
        if random.random() < sp:
            p2["stun"] = 2; p2["nuke_point"] = max(0, p2["nuke_point"] - 50)
            s["logs"].insert(0, "🕵️スパイ成功: 核妨害。")
        else: s["logs"].insert(0, "🕵️スパイ失敗。")
    elif cmd == "NUK":
        trigger_audio("mute"); p2["territory"] *= 0.15; p1["nuke_point"] = 0; s["logs"].insert(0, "☢️最終宣告執行。")

    s["player_ap"] -= 1
    if s["player_ap"] <= 0:
        p2["nuke_point"] += (25.0 + (10.0 if s["difficulty"] == "超大国" else 0))
        if p2["stun"] > 0: p2["stun"] -= 1
        else:
            if p2["nuke_point"] >= 200: p1["territory"] *= 0.3; p2["nuke_point"] = 0
            else:
                p2["military"] += 20.0; e_dmg = (max((p2["military"] * 0.4) + 20.0, 20.0) * (1.2 if s["difficulty"] == "超大国" else 1.0)) * (1.0 / d)
                if p1["shield"]: e_dmg *= 0.5
                if p1["colony"] > 0: p1["colony"] -= e_dmg * 0.8; p1["territory"] -= e_dmg * 0.2
                else: p1["territory"] -= e_dmg
        s["player_ap"] = s["max_ap"]; s["turn"] += 1; p1["shield"] = False

# --- 5. UI ---
if s["phase"] == "DIFFICULTY":
    st.title("DEUS: 戦域選択")
    for d in ["小国", "大国", "超大国"]:
        if st.button(d, use_container_width=True):
            s["difficulty"] = d; p2["territory"] = {"小国":200.0, "大国":950.0, "超大国":1200.0}[d]; s["phase"] = "BRIEFING"; st.rerun()

elif s["phase"] == "BRIEFING":
    st.title("🛡️ DEUS 作戦マニュアル")
    st.markdown('<div class="briefing-card"><span class="briefing-title">【アクション説明】</span><div class="briefing-text">'
                '・🛠軍拡: 軍備・核P増加。<br>・🛡防衛: ダメージ50%カット。<br>・⚔️進軍: 敵領土を攻撃。<br>'
                '・🚩占領: 盾(緩衝地帯)を拡張。<b>敵にダメージなし</b>。<br>・🕵️スパイ: 敵核妨害。<br>・☢️核: 敵領土激減。使用時のみ無音化。</div></div>', unsafe_allow_html=True)
    if st.button("進む", use_container_width=True): s["phase"] = "FACTION"; st.rerun()

elif s["phase"] == "FACTION":
    st.title("陣営プロトコル")
    c1, c2, c3 = st.columns(3)
    if c1.button("連合国", use_container_width=True): s["faction"]="連合国"; s["phase"]="GAME"; st.rerun()
    if c2.button("枢軸國", use_container_width=True): s["faction"]="枢軸國"; s["phase"]="GAME"; st.rerun()
    if c3.button("社会主義国", use_container_width=True): 
        s["faction"]="社会主義国"; p1["territory"]=200.0; s["player_ap"]=3; s["max_ap"]=3; s["phase"]="GAME"; st.rerun()

elif s["phase"] == "GAME":
    st.markdown(f'<div class="enemy-banner"><span class="enemy-text">敵領土: {p2["territory"]:.0f} | 敵核: {p2["nuke_point"]:.0f}/200</span></div>', unsafe_allow_html=True)
    st.markdown(f'<div class="status-row"><div><span class="stat-label">本土</span><span class="stat-val">{p1["territory"]:.0f}</span></div><div><span class="stat-label">緩衝</span><span class="stat-val">{p1["colony"]:.0f}</span></div></div>', unsafe_allow_html=True)
    st.progress(min(p1['nuke_point']/200.0, 1.0))
    
    if p1["territory"] <= 0 or p2["territory"] <= 0:
        st.success("VICTORY" if p2["territory"] <= 0 else "DEFEAT")
        if st.button("REBOOT", use_container_width=True): st.session_state.clear(); st.rerun()
    else:
        if p1["nuke_point"] >= 200:
            if st.button("☢️ 最終宣告執行", type="primary", use_container_width=True): player_step("NUK"); st.rerun()
        c1, c2, c3 = st.columns(3); c4, c5 = st.columns(2)
        if c1.button("🛠軍拡", use_container_width=True): player_step("EXP"); st.rerun()
        if c2.button("🛡防衛", use_container_width=True): player_step("DEF"); st.rerun()
        if c3.button("🕵️スパイ", use_container_width=True): player_step("SPY"); st.rerun()
        if c4.button("⚔️進軍", use_container_width=True): player_step("MAR"); st.rerun()
        if c5.button("🚩占領", use_container_width=True): player_step("OCC"); st.rerun()
    st.markdown(f'<div class="log-box">{"".join([f"<div>{l}</div>" for l in s["logs"][:2]])}</div>', unsafe_allow_html=True)
