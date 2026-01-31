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
    .briefing-card { background: #111; border: 1px solid #333; padding: 15px; border-radius: 5px; margin-bottom: 10px; }
    .briefing-title { color: #d4af37; font-weight: bold; font-size: 1.1rem; }
    .briefing-text { font-size: 0.85rem; color: #CCC; }
    div[data-testid="column"] button, div[data-testid="stVerticalBlock"] button {
        height: 30px !important; font-size: 0.8rem !important;
        background-color: #1a1a1a !important; color: #d4af37 !important;
        border: 1px solid #d4af37 !important;
    }
    .log-box { background: #000; border-top: 1px solid #333; padding: 4px 8px; height: 60px; font-size: 0.75rem; color: #CCC; line-height: 1.2; margin-top: 15px; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. BGMエンジン ---
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

# --- 3. 初期化 ---
if 'state' not in st.session_state:
    st.session_state.state = {
        "p1": {"territory": 150.0, "military": 0.0, "colony": 50.0, "nuke_point": 0, "shield": False, "nuke_lock": 0},
        "p2": {"territory": 800.0, "military": 0.0, "stun": 0}, 
        "turn": 1, "logs": ["SYSTEM ONLINE. 警告：本土への貫通ダメージを確認。"],
        "player_ap": 2, "max_ap": 2, "difficulty": None, "faction": None,
        "phase": "DIFFICULTY"
    }

s = st.session_state.state
p1, p2 = s["p1"], s["p2"]

setup_audio_engine()

def player_step(cmd):
    mul_pwr = 0.25 if s["faction"] == "社会主義国" else 1.0
    mul_nuk = 2.0 if s["faction"] == "連合国" else 1.0
    spy_prob = 0.60 if s["faction"] == "連合国" else 0.33
    shield_eff = 0.8 if s["faction"] == "枢軸国" else 0.5 

    if cmd == "EXP":
        p1["military"] += 25.0 * mul_pwr
        if p1["nuke_lock"] <= 0: p1["nuke_point"] += 20 * mul_nuk
        s["logs"].insert(0, "🛠軍拡: 戦力増強を優先。")
    elif cmd == "DEF": 
        p1["shield"] = True; s["logs"].insert(0, "🛡防衛: 全ラインの警戒を強化。")
    elif cmd == "MAR":
        dmg = max(((p1["military"] * 0.5) + (p1["colony"] * 0.6)) * mul_pwr + 10.0, 10.0)
        if p2["stun"] <= 0 and random.random() < 0.30:
            dmg *= 0.5; p2["territory"] -= dmg; s["logs"].insert(0, f"🛡敵防衛: 被害を{dmg:.0f}に抑えられた。")
        else:
            p2["territory"] -= dmg; s["logs"].insert(0, f"⚔️進軍: {dmg:.0f}の戦果。")
    elif cmd == "OCC":
        # --- 占領の下方修正 (従来の半分へ) ---
        cost = max(15.0 * mul_pwr, 5.0)
        if p1["military"] >= cost:
            p1["military"] -= cost
            # 吸収率 30% -> 15% / 固定値 20 -> 10 に半減
            steal = (max(p2["territory"] * 0.15, 25.0) * mul_pwr) + 10.0
            p2["territory"] -= steal; p1["colony"] += steal
            s["logs"].insert(0, f"🚩占領: 限定的な領土獲得 (+{steal:.0f})。")
    elif cmd == "SPY":
        if random.random() < spy_prob:
            p2["stun"] = 2; s["logs"].insert(0, "🕵️工作成功: 敵防御を一時停止。")
        else: s["logs"].insert(0, "🕵️工作失敗: 敵に察知された。")
    elif cmd == "NUK":
        p2["territory"] *= 0.15; p1["nuke_point"] = 0; s["logs"].insert(0, "☢️最終審判。")

    s["player_ap"] -= 1
    if s["player_ap"] <= 0:
        if p1["nuke_lock"] > 0: p1["nuke_lock"] -= 1
        if p2["stun"] > 0:
            p2["stun"] -= 1; s["logs"].insert(0, f"⏳敵再起動中({p2['stun']}T)")
        else:
            p2["military"] += 20.0
            total_e_dmg = max((p2["military"] * 0.4) + 20.0, 20.0)
            if s["difficulty"] == "超大国": total_e_dmg *= 1.2
            if p1["shield"]: total_e_dmg *= shield_eff
            
            # --- ダメージ分散ロジック (植民地 80% / 本土 20%) ---
            if p1["colony"] > 0:
                colony_dmg = total_e_dmg * 0.8
                homeland_dmg = total_e_dmg * 0.2
                p1["colony"] -= colony_dmg
                p1["territory"] -= homeland_dmg
                if p1["colony"] < 0:
                    # 植民地不足分は本土へ貫通
                    p1["territory"] += p1["colony"]
                    p1["colony"] = 0
                s["logs"].insert(0, f"🚨警告: 被弾！(本土:{homeland_dmg:.0f} / 緩衝:{colony_dmg:.0f})")
            else:
                p1["territory"] -= total_e_dmg
                s["logs"].insert(0, f"🚨直撃: 本土へ{total_e_dmg:.0f}の壊滅的打撃！")
        
        s["player_ap"] = s["max_ap"]; s["turn"] += 1; p1["shield"] = False

# --- UI (各フェーズ) ---
if s["phase"] == "DIFFICULTY":
    st.title("難易度設定")
    if st.button("小国", use_container_width=True): s["difficulty"] = "小国"; p2["territory"] = 200.0; s["phase"] = "BRIEFING"; st.rerun()
    if st.button("大国", use_container_width=True): s["difficulty"] = "大国"; p2["territory"] = 950.0; s["phase"] = "BRIEFING"; st.rerun()
    if st.button("超大国", use_container_width=True): s["difficulty"] = "超大国"; p2["territory"] = 1200.0; s["phase"] = "BRIEFING"; st.rerun()

elif s["phase"] == "BRIEFING":
    st.title("🛡️ 作戦ブリーフィング")
    st.markdown('<div class="briefing-card"><span class="briefing-title">【防衛ドクトリンの変更】</span><br>'
                '<span class="briefing-text">・緩衝地帯があっても<b>ダメージの20%は本土へ貫通</b>します。<br>'
                '・占領による領土拡大効率が<b>50%低下</b>しました。</span></div>', unsafe_allow_html=True)
    if st.button("次へ", use_container_width=True): s["phase"] = "FACTION"; st.rerun()

elif s["phase"] == "FACTION":
    st.title("陣営プロトコル")
    c1, c2, c3 = st.columns(3)
    if c1.button("連合国", use_container_width=True): s["faction"] = "連合国"; s["phase"] = "GAME"; st.rerun()
    if c2.button("枢軸国", use_container_width=True): s["faction"] = "枢軸国"; s["phase"] = "GAME"; st.rerun()
    if c3.button("社会主義国", use_container_width=True): 
        s["faction"] = "社会主義国"; p1["territory"] = 200.0; s["player_ap"] = 3; s["max_ap"] = 3; s["phase"] = "GAME"; st.rerun()

elif s["phase"] == "GAME":
    st.markdown(f'<div class="enemy-banner"><span class="enemy-text">DEUS: {p2["territory"]:.0f}</span></div>', unsafe_allow_html=True)
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
