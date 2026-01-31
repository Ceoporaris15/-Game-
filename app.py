import streamlit as st
import random
import base64

# --- 1. レイアウト設定 ---
st.set_page_config(page_title="DEUS", layout="centered")

st.markdown("""
    <style>
    html, body, [data-testid="stAppViewContainer"] { background-color: #000; color: #FFF; overflow: hidden; }
    .enemy-banner { background-color: #200; border-bottom: 1px solid #F00; padding: 4px; text-align: center; margin: -55px -15px 5px -15px; }
    .enemy-text { color: #F00; font-weight: bold; font-size: 1rem; letter-spacing: 3px; }
    .status-row { display: flex; justify-content: space-around; background: #111; border: 1px solid #d4af37; padding: 2px; margin-bottom: 5px; border-radius: 4px; }
    .stat-label { font-size: 0.6rem; color: #888; margin-right: 4px; }
    .stat-val { color: #d4af37; font-weight: bold; font-size: 0.9rem; }
    .stProgress { height: 6px !important; margin-bottom: 2px !important; }
    .briefing-card { background: #111; border: 1px solid #333; padding: 12px; border-radius: 5px; margin-bottom: 10px; }
    .briefing-title { color: #d4af37; font-weight: bold; font-size: 1rem; border-bottom: 1px solid #444; margin-bottom: 5px; padding-bottom: 3px;}
    .briefing-text { font-size: 0.75rem; color: #CCC; line-height: 1.5; }
    div[data-testid="column"] button, div[data-testid="stVerticalBlock"] button {
        height: 30px !important; font-size: 0.8rem !important;
        background-color: #1a1a1a !important; color: #d4af37 !important;
        border: 1px solid #d4af37 !important;
    }
    .log-box { background: #000; border-top: 1px solid #333; padding: 4px 8px; height: 60px; font-size: 0.75rem; color: #CCC; line-height: 1.2; margin-top: 15px; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. BGM設定 ---
def setup_audio_engine():
    try:
        with open('Vidnoz_AIMusic.mp3', 'rb') as f:
            data = f.read()
            b64 = base64.b64encode(data).decode()
            audio_html = f"""<audio id="bgm" loop><source src="data:audio/mp3;base64,{b64}" type="audio/mp3"></audio>
            <script>
                var audio = window.parent.document.getElementById('bgm');
                if (!audio) {{ audio = document.getElementById('bgm'); }}
                window.parent.document.addEventListener('click', function() {{
                    if (audio.paused) {{ audio.play(); }}
                }}, {{once: false}});
            </script>"""
            st.components.v1.html(audio_html, height=0)
    except: pass

# --- 3. ステート管理 ---
if 'state' not in st.session_state:
    st.session_state.state = {
        "p1": {"territory": 150.0, "military": 0.0, "colony": 50.0, "nuke_point": 0, "shield": False},
        "p2": {"territory": 800.0, "military": 0.0, "nuke_point": 0, "stun": 0}, 
        "turn": 1, "logs": ["SYSTEM ONLINE. 占領/攻撃の分離完了。"],
        "player_ap": 2, "max_ap": 2, "difficulty": None, "faction": None,
        "phase": "DIFFICULTY"
    }

s = st.session_state.state
p1, p2 = s["p1"], s["p2"]
setup_audio_engine()

# --- 4. コマンド・ロジック ---
def player_step(cmd):
    # 陣営パラメータ
    if s["faction"] == "連合国": a_mul, d_mul, o_mul, n_mul, spy_prob = 1.0, 1.0, 1.0, 2.0, 0.60
    elif s["faction"] == "枢軸国": a_mul, d_mul, o_mul, n_mul, spy_prob = 1.5, 0.8, 1.2, 1.0, 0.33
    else: a_mul, d_mul, o_mul, n_mul, spy_prob = 0.5, 0.8, 1.0, 1.0, 0.33

    if cmd == "EXP":
        p1["military"] += 25.0 * a_mul
        p1["nuke_point"] += 20 * n_mul
        s["logs"].insert(0, f"🛠軍拡: 軍備+{25.0*a_mul:.0f}。核開発加速。")
    elif cmd == "DEF": 
        p1["shield"] = True; s["logs"].insert(0, "🛡防衛: 次の被ダメージを大幅軽減。")
    elif cmd == "MAR":
        dmg = max(((p1["military"] * 0.5) + (p1["colony"] * 0.6)) * a_mul + 10.0, 10.0)
        if p2["stun"] <= 0 and random.random() < 0.30:
            dmg *= 0.5; p2["territory"] -= dmg; s["logs"].insert(0, f"🛡敵防衛: 打撃を{dmg:.0f}に抑えられた。")
        else:
            p2["territory"] -= dmg; s["logs"].insert(0, f"⚔️進軍: 敵領土へ{dmg:.0f}の打撃。")
    elif cmd == "OCC":
        # 敵領土は減らさず、植民地のみを増加（盾の構築）
        calc_steal = ((max(p2["territory"] * 0.15, 25.0)) + 10.0) * o_mul
        steal = min(calc_steal, 50.0)
        p1["colony"] += steal
        s["logs"].insert(0, f"🚩占領: 緩衝地帯を+{steal:.0f}拡張(敵被害なし)。")
    elif cmd == "SPY":
        if random.random() < spy_prob:
            p2["stun"] = 2; p2["nuke_point"] = max(0, p2["nuke_point"] - 50)
            s["logs"].insert(0, "🕵️工作成功: 敵核開発妨害(-50) & 麻痺。")
        else: s["logs"].insert(0, "🕵️工作失敗: 工作員との通信途絶。")
    elif cmd == "NUK":
        p2["territory"] *= 0.15; p1["nuke_point"] = 0; s["logs"].insert(0, "☢️最終宣告執行。")

    s["player_ap"] -= 1
    if s["player_ap"] <= 0:
        # AIの核開発加速
        ai_nuke_gain = 25.0 + (10.0 if s["difficulty"] == "超大国" else 0)
        p2["nuke_point"] += ai_nuke_gain
        
        if p2["stun"] > 0:
            p2["stun"] -= 1; s["logs"].insert(0, f"⏳敵再起動中({p2['stun']}T)")
        else:
            if p2["nuke_point"] >= 200:
                p1["territory"] *= 0.3; p2["nuke_point"] = 0
                s["logs"].insert(0, "☢️敵最終宣告: 本土が大破。")
            else:
                p2["military"] += 20.0
                total_e_dmg = (max((p2["military"] * 0.4) + 20.0, 20.0) * (1.2 if s["difficulty"] == "超大国" else 1.0)) * (1.0 / d_mul)
                if p1["shield"]: total_e_dmg *= 0.5
                if p1["colony"] > 0:
                    col_dmg, home_dmg = total_e_dmg * 0.8, total_e_dmg * 0.2
                    p1["colony"] -= col_dmg; p1["territory"] -= home_dmg
                    if p1["colony"] < 0: p1["territory"] += p1["colony"]; p1["colony"] = 0
                    s["logs"].insert(0, f"⚠️被弾: 本土-{home_dmg:.0f} / 緩衝-{col_dmg:.0f}")
                else:
                    p1["territory"] -= total_e_dmg
                    s["logs"].insert(0, f"🚨警告: 本土へ{total_e_dmg:.0f}の直撃！")
        
        s["player_ap"] = s["max_ap"]; s["turn"] += 1; p1["shield"] = False

# --- 5. UIフェーズ ---
if s["phase"] == "DIFFICULTY":
    st.title("DEUS: 戦域選択")
    if st.button("小国 (Easy)", use_container_width=True): s["difficulty"] = "小国"; p2["territory"] = 200.0; s["phase"] = "BRIEFING"; st.rerun()
    if st.button("大国 (Normal)", use_container_width=True): s["difficulty"] = "大国"; p2["territory"] = 950.0; s["phase"] = "BRIEFING"; st.rerun()
    if st.button("超大国 (Hard)", use_container_width=True): s["difficulty"] = "超大国"; p2["territory"] = 1200.0; s["phase"] = "BRIEFING"; st.rerun()

elif s["phase"] == "BRIEFING":
    st.title("🛡️ DEUS 作戦要綱")
    st.markdown('<div class="briefing-card"><span class="briefing-title">【アクション規定】</span><br>'
                '<div class="briefing-text">・<b>🚩占領</b>: 緩衝地帯(盾)を増やします。敵にダメージは与えません。<br>'
                '・<b>⚔️進軍</b>: 敵領土を直接破壊する唯一の通常手段です。<br>'
                '・<b>🕵️スパイ</b>: 敵の核開発を-50ポイント妨害し、2ターン麻痺させます。</div></div>', unsafe_allow_html=True)
    st.markdown('<div class="briefing-card"><span class="briefing-title">【国家ドクトリン】</span><br>'
                '<div class="briefing-text">・<b>🔵連合国</b>: 核開発2倍、スパイ成功率60%。核による早期終結向け。<br>'
                '・<b>🔴枢軸国</b>: 攻撃1.5倍、占領1.2倍の高火力。ただし防御0.8倍と脆い。<br>'
                '・<b>🛠社会主義国</b>: 3回行動(AP3)が可能。長期的な物量作戦向け。</div></div>', unsafe_allow_html=True)
    if st.button("陣営選択へ進む", use_container_width=True): s["phase"] = "FACTION"; st.rerun()

elif s["phase"] == "FACTION":
    st.title("陣営プロトコル")
    c1, c2, c3 = st.columns(3)
    if c1.button("連合国", use_container_width=True): s["faction"] = "連合国"; s["phase"] = "GAME"; st.rerun()
    if c2.button("枢軸国", use_container_width=True): s["faction"] = "枢軸国"; s["phase"] = "GAME"; st.rerun()
    if c3.button("社会主義国", use_container_width=True): 
        s["faction"] = "社会主義国"; p1["territory"] = 200.0; s["player_ap"] = 3; s["max_ap"] = 3; s["phase"] = "GAME"; st.rerun()

elif s["phase"] == "GAME":
    st.markdown(f'<div class="enemy-banner"><span class="enemy-text">敵領土: {p2["territory"]:.0f} | 敵核: {p2["nuke_point"]:.0f}/200</span></div>', unsafe_allow_html=True)
    st.markdown(f'<div class="status-row"><div><span class="stat-label">本土</span><span class="stat-val">{p1["territory"]:.0f}</span></div><div><span class="stat-label">緩衝</span><span class="stat-val">{p1["colony"]:.0f}</span></div></div>', unsafe_allow_html=True)
    st.progress(min(p1['nuke_point']/200.0, 1.0))

    if p1["territory"] <= 0 or p2["territory"] <= 0:
        st.success("VICTORY" if p2["territory"] <= 0 else "DEFEAT")
        if st.button("REBOOT", use_container_width=True): st.session_state.clear(); st.rerun()
    else:
        st.caption(f"T-{s['turn']} | AP: {s['player_ap']} | {s['faction']}")
        if p1["nuke_point"] >= 200:
            if st.button("☢️ 最終宣告執行", type="primary", use_container_width=True): player_step("NUK"); st.rerun()
        c1, c2, c3 = st.columns(3)
        if c1.button("🛠軍拡", use_container_width=True): player_step("EXP"); st.rerun()
        if c2.button("🛡防衛", use_container_width=True): player_step("DEF"); st.rerun()
        if c3.button("🕵️スパイ", use_container_width=True): player_step("SPY"); st.rerun()
        c4, c5 = st.columns(2)
        if c4.button("⚔️進軍", use_container_width=True): player_step("MAR"); st.rerun()
        if c5.button("🚩占領", use_container_width=True): player_step("OCC"); st.rerun()
    log_html = "".join([f'<div>{log}</div>' for log in s["logs"][:2]])
    st.markdown(f'<div class="log-box">{log_html}</div>', unsafe_allow_html=True)
