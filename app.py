import streamlit as st
import random

# --- 1. レイアウト設定 ---
st.set_page_config(page_title="DEUS", layout="centered")

st.markdown("""
    <style>
    html, body, [data-testid="stAppViewContainer"] { background-color: #000; color: #FFF; overflow: hidden; }
    .enemy-banner { background-color: #200; border-bottom: 1px solid #F00; padding: 5px; text-align: center; margin: -60px -15px 10px -15px; }
    .enemy-text { color: #F00; font-weight: bold; font-size: 0.9rem; letter-spacing: 2px; }
    
    .stat-section { display: flex; gap: 8px; margin-bottom: 8px; }
    .stat-card { flex: 1; background: #111; border: 1px solid #333; padding: 6px; border-radius: 4px; }
    .bar-label { font-size: 0.7rem; color: #AAA; margin-bottom: 2px; display: flex; justify-content: space-between; }
    .hp-bar-bg { background: #222; width: 100%; height: 8px; border-radius: 4px; overflow: hidden; margin-bottom: 4px; border: 1px solid #333; }
    .hp-bar-fill { background: linear-gradient(90deg, #d4af37, #f1c40f); height: 100%; transition: width 0.5s; }
    .shield-bar-fill { background: linear-gradient(90deg, #3498db, #2980b9); height: 100%; transition: width 0.5s; }
    .enemy-bar-fill { background: linear-gradient(90deg, #c0392b, #e74c3c); height: 100%; transition: width 0.5s; }
    .nuke-bar-fill { background: linear-gradient(90deg, #9b59b6, #8e44ad); height: 100%; transition: width 0.5s; }
    
    .briefing-card { background: #111; border: 1px solid #333; padding: 10px; border-radius: 5px; margin-bottom: 10px; }
    .briefing-title { color: #d4af37; font-weight: bold; font-size: 0.9rem; border-bottom: 1px solid #444; margin-bottom: 5px; }
    .briefing-text { font-size: 0.75rem; color: #CCC; line-height: 1.5; }
    
    .log-box { background: #000; border-top: 1px solid #333; padding: 4px 8px; height: 50px; font-size: 0.75rem; color: #CCC; margin-top: 10px; font-family: monospace; }
    
    /* カスタムボタンのスタイル */
    .se-button {
        width: 100%; height: 38px; background: #1a1a1a; color: #d4af37;
        border: 1px solid #d4af37; border-radius: 4px; font-size: 0.8rem;
        cursor: pointer; font-weight: bold;
    }
    .se-button:active { background: #333; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. 音響ボタン生成関数 ---
def sound_button(label, key, freq=400, type='sine'):
    """
    クリックした瞬間に確実に音を出すためのHTMLボタン
    """
    button_html = f"""
        <button class="se-button" onclick="play()">{label}</button>
        <script>
        function play() {{
            try {{
                const ctx = new (window.AudioContext || window.webkitAudioContext)();
                const o = ctx.createOscillator();
                const g = ctx.createGain();
                o.type = '{type}';
                o.frequency.setValueAtTime({freq}, ctx.currentTime);
                g.gain.setValueAtTime(0.1, ctx.currentTime);
                g.gain.exponentialRampToValueAtTime(0.01, ctx.currentTime + 0.2);
                o.connect(g);
                g.connect(ctx.destination);
                o.start();
                o.stop(ctx.currentTime + 0.2);
            }} catch(e) {{}}
            // Streamlit側にクリックを通知
            window.parent.postMessage({{type: 'streamlit:setComponentValue', value: true, key: '{key}'}}, '*');
        }}
        </script>
    """
    return st.components.v1.html(button_html, height=45)

# --- 3. ステート管理 ---
if 'state' not in st.session_state:
    st.session_state.state = {
        "p1": {"territory": 150.0, "max_territory": 150.0, "military": 0.0, "colony": 50.0, "nuke_point": 0, "shield": False},
        "p2": {"territory": 800.0, "max_territory": 800.0, "military": 0.0, "nuke_point": 0, "stun": 0}, 
        "turn": 1, "logs": ["システム待機中。ボタン操作で音響が同期されます。"],
        "player_ap": 2, "max_ap": 2, "difficulty": None, "faction": None, "phase": "DIFFICULTY"
    }

s = st.session_state.state
p1, p2 = s["p1"], s["p2"]

# --- 4. ロジック ---
def player_step(cmd):
    if s["faction"] == "連合国": a, d, o, n, sp = 1.0, 1.0, 1.0, 2.0, 0.60
    elif s["faction"] == "枢軸國": a, d, o, n, sp = 1.5, 0.8, 1.2, 1.0, 0.33
    else: a, d, o, n, sp = 0.5, 0.8, 1.0, 1.0, 0.33

    if cmd == "EXP":
        p1["military"] += 25.0 * a; p1["nuke_point"] += 20 * n
        s["logs"].insert(0, f"🛠軍拡: 軍備+{25.0*a:.0f}")
    elif cmd == "DEF":
        p1["shield"] = True; s["logs"].insert(0, "🛡防衛: シールド展開。")
    elif cmd == "MAR":
        dmg = max(((p1["military"] * 0.5) + (p1["colony"] * 0.6)) * a + 10.0, 10.0)
        p2["territory"] -= dmg; s["logs"].insert(0, f"⚔️進軍: 敵へ{dmg:.0f}の打撃。")
    elif cmd == "OCC":
        steal = min(((max(p2["territory"] * 0.15, 25.0)) + 10.0) * o, 50.0)
        p1["colony"] += steal; s["logs"].insert(0, f"🚩占領: 緩衝地帯拡張。")
    elif cmd == "SPY":
        if random.random() < sp:
            p2["stun"] = 2; p2["nuke_point"] = max(0, p2["nuke_point"] - 50); s["logs"].insert(0, "🕵️スパイ成功。")
        else: s["logs"].insert(0, "🕵️スパイ失敗。")
    elif cmd == "NUK":
        p2["territory"] *= 0.15; p1["nuke_point"] = 0; s["logs"].insert(0, "☢️最終宣告執行。")

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
    st.rerun()

# --- 5. UI ---
if s["phase"] == "DIFFICULTY":
    st.title("DEUS: 戦域選択")
    for d in ["小国", "大国", "超大国"]:
        if st.button(d, use_container_width=True):
            s["difficulty"] = d; p2["territory"] = {"小国":200.0, "大国":950.0, "超大国":1200.0}[d]; p2["max_territory"] = p2["territory"]; s["phase"] = "BRIEFING"; st.rerun()

elif s["phase"] == "BRIEFING":
    st.title("🛡️ 作戦説明書")
    st.markdown('<div class="briefing-card"><div class="briefing-title">【アクション規定】</div><div class="briefing-text">'
                '・🛠<b>軍拡</b>: 軍備と核Pを増加。<br>・🛡<b>防衛</b>: 次の被害を50%軽減。<br>・⚔️<b>進軍</b>: 敵領土を攻撃。<br>'
                '・🚩<b>占領</b>: 緩衝地帯(盾)を拡張。<br>・🕵️<b>スパイ</b>: 敵核開発を妨害。<br>・☢️<b>核兵器</b>: 200Pで敵領土を85%破壊。</div></div>', unsafe_allow_html=True)
    st.markdown('<div class="briefing-card"><div class="briefing-title">【国家特性】</div><div class="briefing-text">'
                '・<b>連合国</b>: 核速度2倍。スパイ60%。<br>・<b>枢軸國</b>: 攻撃1.5倍。防御弱。<br>・<b>社会主義国</b>: 行動回数AP3。</div></div>', unsafe_allow_html=True)
    if st.button("次へ進む", use_container_width=True): s["phase"] = "FACTION"; st.rerun()

elif s["phase"] == "FACTION":
    st.title("陣営プロトコル選択")
    c1, c2, c3 = st.columns(3)
    if c1.button("連合国", use_container_width=True): s["faction"]="連合国"; s["phase"]="GAME"; st.rerun()
    if c2.button("枢軸國", use_container_width=True): s["faction"]="枢軸國"; s["phase"]="GAME"; st.rerun()
    if c3.button("社会主義国", use_container_width=True): s["faction"]="社会主義国"; p1["territory"]=200.0; p1["max_territory"]=200.0; s["player_ap"]=3; s["max_ap"]=3; s["phase"]="GAME"; st.rerun()

elif s["phase"] == "GAME":
    p1_hp_pct = max(p1["territory"] / p1["max_territory"] * 100, 0)
    p2_hp_pct = max(p2["territory"] / p2["max_territory"] * 100, 0)
    colony_pct = max(min(p1["colony"] / 100 * 100, 100), 0)
    p1_nuke_pct = min(p1['nuke_point']/2, 100)
    p2_nuke_pct = min(p2['nuke_point']/2, 100)

    st.markdown(f"""
    <div class="enemy-banner"><span class="enemy-text">第 {s['turn']} ターン (AP:{s['player_ap']})</span></div>
    <div class="stat-section">
        <div class="stat-card">
            <div class="bar-label"><span>自国本土</span><span>{p1['territory']:.0f}</span></div>
            <div class="hp-bar-bg"><div class="hp-bar-fill" style="width: {p1_hp_pct}%;"></div></div>
            <div class="bar-label"><span>緩衝地帯</span><span>{p1['colony']:.0f}</span></div>
            <div class="hp-bar-bg"><div class="shield-bar-fill" style="width: {colony_pct}%;"></div></div>
            <div class="bar-label"><span>自国核開発</span><span>{p1['nuke_point']:.0f}/200</span></div>
            <div class="hp-bar-bg"><div class="nuke-bar-fill" style="width: {p1_nuke_pct}%;"></div></div>
        </div>
        <div class="stat-card">
            <div class="bar-label"><span>敵軍領土</span><span>{p2['territory']:.0f}</span></div>
            <div class="hp-bar-bg"><div class="enemy-bar-fill" style="width: {p2_hp_pct}%;"></div></div>
            <div class="bar-label"><span>敵軍核開発</span><span>{p2['nuke_point']:.0f}/200</span></div>
            <div class="hp-bar-bg"><div class="enemy-bar-fill" style="width: {p2_nuke_pct}%; opacity: 0.5;"></div></div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    if p1["territory"] <= 0 or p2["territory"] <= 0:
        st.success("勝利" if p2["territory"] <= 0 else "敗北")
        if st.button("システム再起動", use_container_width=True): st.session_state.clear(); st.rerun()
    else:
        if p1["nuke_point"] >= 200:
            if sound_button("☢️ 最終宣告執行", "nuk_btn", 150, 'sawtooth'): player_step("NUK")
        
        c1, c2, c3 = st.columns(3); c4, c5 = st.columns(2)
        with c1: 
            if sound_button("🛠軍拡", "exp_btn", 300): player_step("EXP")
        with c2: 
            if sound_button("🛡防衛", "def_btn", 350): player_step("DEF")
        with c3: 
            if sound_button("🕵️スパイ", "spy_btn", 500, 'square'): player_step("SPY")
        with c4: 
            if sound_button("⚔️進軍", "mar_btn", 450, 'square'): player_step("MAR")
        with c5: 
            if sound_button("🚩占領", "occ_btn", 400): player_step("OCC")
        
    st.markdown(f'<div class="log-box">{"".join([f"<div>>> {l}</div>" for l in s["logs"][:2]])}</div>', unsafe_allow_html=True)
