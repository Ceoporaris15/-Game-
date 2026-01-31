import streamlit as st
import random
import base64

# --- 1. レイアウト設定 ---
st.set_page_config(page_title="DEUS", layout="centered")

st.markdown("""
    <style>
    html, body, [data-testid="stAppViewContainer"] { background-color: #000; color: #FFF; }
    .enemy-banner { background-color: #200; border-bottom: 1px solid #F00; padding: 10px; text-align: center; margin: -55px -15px 15px -15px; }
    .enemy-text { color: #F00; font-weight: bold; font-size: 1.2rem; letter-spacing: 5px; }
    
    /* ステータスバーの視覚化 */
    .stat-container { background: #111; border: 1px solid #333; padding: 10px; border-radius: 8px; margin-bottom: 10px; }
    .bar-label { font-size: 0.8rem; color: #888; margin-bottom: 2px; }
    .hp-bar-bg { background: #222; width: 100%; height: 12px; border-radius: 6px; overflow: hidden; margin-bottom: 8px; border: 1px solid #444; }
    .hp-bar-fill { background: linear-gradient(90deg, #d4af37, #f1c40f); height: 100%; transition: width 0.5s; }
    .shield-bar-fill { background: linear-gradient(90deg, #3498db, #2980b9); height: 100%; transition: width 0.5s; }
    
    .briefing-card { background: #111; border: 1px solid #333; padding: 12px; border-radius: 5px; margin-bottom: 10px; }
    .briefing-title { color: #d4af37; font-weight: bold; font-size: 0.9rem; border-bottom: 1px solid #444; margin-bottom: 5px; padding-bottom: 3px;}
    .briefing-text { font-size: 0.7rem; color: #CCC; line-height: 1.4; }
    
    div[data-testid="column"] button, div[data-testid="stVerticalBlock"] button {
        height: 45px !important; background-color: #1a1a1a !important; color: #d4af37 !important; border: 1px solid #d4af37 !important; font-weight: bold !important;
    }
    .log-box { background: #000; border-top: 1px solid #333; padding: 4px 8px; height: 60px; font-size: 0.8rem; color: #CCC; margin-top: 15px; font-family: monospace; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. 確定音響エンジン ---
def play_tone(tone_type):
    # JavaScriptによる直接合成音
    scripts = {
        "soft": "const c=new AudioContext();const o=c.createOscillator();const g=c.createGain();o.type='sine';o.frequency.value=350;g.gain.setValueAtTime(0.1,c.currentTime);g.gain.exponentialRampToValueAtTime(0.001,c.currentTime+0.3);o.connect(g);g.connect(c.destination);o.start();o.stop(c.currentTime+0.3);",
        "sharp": "const c=new AudioContext();const o=c.createOscillator();const g=c.createGain();o.type='square';o.frequency.value=440;g.gain.setValueAtTime(0.05,c.currentTime);g.gain.exponentialRampToValueAtTime(0.001,c.currentTime+0.1);o.connect(g);g.connect(c.destination);o.start();o.stop(c.currentTime+0.1);",
        "mute": "const b=window.parent.document.querySelector('audio'); if(b){b.pause(); setTimeout(()=>b.play(), 5000);}"
    }
    st.components.v1.html(f"<script>{scripts[tone_type]}</script>", height=0)

def setup_bgm():
    try:
        with open('Vidnoz_AIMusic.mp3', 'rb') as f:
            b64 = base64.b64encode(f.read()).decode()
            st.components.v1.html(f"""
                <audio id="bgm" loop><source src="data:audio/mp3;base64,{b64}" type="audio/mp3"></audio>
                <script>
                const a = document.getElementById('bgm');
                const startAudio = () => {{ if(a.paused) a.play(); }};
                window.parent.document.addEventListener('mousedown', startAudio);
                window.addEventListener('mousedown', startAudio);
                </script>
            """, height=0)
    except: pass

# --- 3. ステート管理 ---
if 'state' not in st.session_state:
    st.session_state.state = {
        "p1": {"territory": 150.0, "max_territory": 150.0, "military": 0.0, "colony": 50.0, "max_colony": 100.0, "nuke_point": 0, "shield": False},
        "p2": {"territory": 800.0, "military": 0.0, "nuke_point": 0, "stun": 0}, 
        "turn": 1, "logs": ["SYSTEM ONLINE. 本土防衛を開始せよ。"],
        "player_ap": 2, "max_ap": 2, "difficulty": None, "faction": None, "phase": "DIFFICULTY"
    }

s = st.session_state.state
p1, p2 = s["p1"], s["p2"]
setup_bgm()

# --- 4. ロジック ---
def player_step(cmd):
    if s["faction"] == "連合国": a_mul, d_mul, o_mul, n_mul, spy_prob = 1.0, 1.0, 1.0, 2.0, 0.60
    elif s["faction"] == "枢軸國": a_mul, d_mul, o_mul, n_mul, spy_prob = 1.5, 0.8, 1.2, 1.0, 0.33
    else: a_mul, d_mul, o_mul, n_mul, spy_prob = 0.5, 0.8, 1.0, 1.0, 0.33

    if cmd == "EXP":
        play_tone("soft"); p1["military"] += 25.0 * a_mul; p1["nuke_point"] += 20 * n_mul
        s["logs"].insert(0, f"🛠軍拡: 軍備+{25.0*a_mul:.0f}")
    elif cmd == "DEF":
        play_tone("soft"); p1["shield"] = True; s["logs"].insert(0, "🛡防衛: 防御態勢を展開。")
    elif cmd == "MAR":
        play_tone("sharp"); dmg = max(((p1["military"] * 0.5) + (p1["colony"] * 0.6)) * a_mul + 10.0, 10.0)
        p2["territory"] -= dmg; s["logs"].insert(0, f"⚔️進軍: 敵領土へ{dmg:.0f}の打撃。")
    elif cmd == "OCC":
        play_tone("soft"); steal = min(((max(p2["territory"] * 0.15, 25.0)) + 10.0) * o_mul, 50.0)
        p1["colony"] = min(p1["colony"] + steal, 200.0); s["logs"].insert(0, f"🚩占領: 緩衝地帯拡張。")
    elif cmd == "SPY":
        play_tone("sharp")
        if random.random() < spy_prob:
            p2["stun"] = 2; p2["nuke_point"] = max(0, p2["nuke_point"] - 50); s["logs"].insert(0, "🕵️スパイ成功: 核開発を妨害。")
        else: s["logs"].insert(0, "🕵️スパイ失敗。")
    elif cmd == "NUK":
        play_tone("mute"); p2["territory"] *= 0.15; p1["nuke_point"] = 0; s["logs"].insert(0, "☢️最終宣告。世界が静まり返る。")

    s["player_ap"] -= 1
    if s["player_ap"] <= 0:
        p2["nuke_point"] += (25.0 + (10.0 if s["difficulty"] == "超大国" else 0))
        if p2["stun"] > 0: p2["stun"] -= 1
        else:
            if p2["nuke_point"] >= 200: p1["territory"] *= 0.3; p2["nuke_point"] = 0
            else:
                p2["military"] += 20.0; e_dmg = (max((p2["military"] * 0.4) + 20.0, 20.0) * (1.2 if s["difficulty"] == "超大国" else 1.0)) * (1.0 / d_mul)
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
    st.title("🛡️ DEUS 作戦要綱")
    st.markdown('<div class="briefing-card"><span class="briefing-title">【アクション規定】</span><div class="briefing-text">'
                '・🛠軍拡: 軍備・核P増加。<br>・🛡防衛: 被弾50%カット。<br>・⚔️進軍: 敵領土への直接攻撃。<br>'
                '・🚩占領: 緩衝地帯を拡張。敵損害なし。<br>・🕵️スパイ: 敵核妨害。<br>・☢️核: 敵領土激減。使用時のみ無音化。</div></div>', unsafe_allow_html=True)
    if st.button("進む", use_container_width=True): s["phase"] = "FACTION"; st.rerun()

elif s["phase"] == "FACTION":
    st.title("陣営プロトコル")
    c1, c2, c3 = st.columns(3)
    if c1.button("連合国", use_container_width=True): s["faction"]="連合国"; s["phase"]="GAME"; st.rerun()
    if c2.button("枢軸國", use_container_width=True): s["faction"]="枢軸國"; s["phase"]="GAME"; st.rerun()
    if c3.button("社会主義国", use_container_width=True): 
        s["faction"]="社会主義国"; p1["territory"]=200.0; p1["max_territory"]=200.0; s["player_ap"]=3; s["max_ap"]=3; s["phase"]="GAME"; st.rerun()

elif s["phase"] == "GAME":
    # 敵情報
    st.markdown(f'<div class="enemy-banner"><span class="enemy-text">ENEMY TERRITORY: {p2["territory"]:.0f}</span></div>', unsafe_allow_html=True)
    
    # 自国情報（視覚化）
    hp_pct = max(p1["territory"] / p1["max_territory"] * 100, 0)
    colony_pct = max(min(p1["colony"] / 100 * 100, 100), 0)
    
    st.markdown(f"""
    <div class="stat-container">
        <div class="bar-label">MAINLAND (本土生命線): {p1['territory']:.0f}</div>
        <div class="hp-bar-bg"><div class="hp-bar-fill" style="width: {hp_pct}%;"></div></div>
        <div class="bar-label">BUFFER ZONE (緩衝地帯): {p1['colony']:.0f}</div>
        <div class="hp-bar-bg"><div class="shield-bar-fill" style="width: {colony_pct}%;"></div></div>
    </div>
    """, unsafe_allow_html=True)
    
    st.caption(f"核開発進捗: {p1['nuke_point']}/200")
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
        
    st.markdown(f'<div class="log-box">{"".join([f"<div>>> {l}</div>" for l in s["logs"][:2]])}</div>', unsafe_allow_html=True)
