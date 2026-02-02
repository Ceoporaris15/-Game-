import streamlit as st
from supabase import create_client
import time
import random

# --- 1. 接続設定 ---
try:
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    supabase = create_client(url, key)
except:
    st.error("Secrets設定を確認してください。")
    st.stop()

def get_game(rid):
    try:
        res = supabase.table("games").select("*").eq("id", rid).execute()
        return res.data[0] if res.data else None
    except: return None

def sync(rid, updates):
    try: supabase.table("games").update(updates).eq("id", rid).execute()
    except: pass

# --- 2. 最終決戦用UI ---
st.set_page_config(page_title="DEUS ONLINE: LAST STAND", layout="centered")
st.markdown("""
    <style>
    html, body, [data-testid="stAppViewContainer"], .main {
        background-color: #050505 !important; color: #00ffcc !important;
        font-family: 'Hiragino Kaku Gothic Pro', sans-serif;
    }
    .stButton > button { 
        background-color: #111 !important; color: #00ffcc !important; 
        border: 2px solid #00ffcc !important; width: 100% !important; font-weight: bold !important;
    }
    .status-row { display: flex; align-items: center; margin-bottom: 6px; }
    .status-label { width: 100px; font-size: 0.75rem; }
    .bar-bg { background: #222; width: 100%; height: 16px; border: 1px solid #444; border-radius: 3px; overflow: hidden; }
    .fill-hp { background: linear-gradient(90deg, #008877, #00ffcc); height: 100%; }
    .fill-nk { background: linear-gradient(90deg, #552277, #9b59b6); height: 100%; }
    .fill-enemy { background: linear-gradient(90deg, #771111, #ff4b4b); height: 100%; }
    .log-box { background: #000; padding: 10px; border: 1px solid #00ffcc; height: 120px; font-size: 0.85rem; overflow-y: auto; color: #00ffcc; }
    </style>
    """, unsafe_allow_html=True)

if 'room_id' not in st.session_state: st.session_state.room_id = None

# --- 3. 接続フェーズ ---
if not st.session_state.room_id:
    st.title("🛡️ DEUS ONLINE: LAST STAND")
    rid = st.text_input("作戦コード", "7777")
    role = st.radio("役割", ["p1", "p2"], horizontal=True)
    c_name = st.text_input("国名", "帝國")
    if st.button("最終サーバーへ接続"):
        if role == "p1":
            init_data = {
                "id": rid, "p1_hp": 1000.0, "p2_hp": 1000.0, "p1_colony": 50.0, "p2_colony": 50.0, 
                "p1_nuke": 0.0, "p2_nuke": 0.0, "turn": "p1", "ap": 2, "chat": ["🛰️ システム最終起動。"],
                "p1_shield": 0, "p2_shield": 0, "p1_nuke_shield_count": 0, "p2_nuke_shield_count": 0,
                "neutral_owner": "none"
            }
            supabase.table("games").delete().eq("id", rid).execute()
            supabase.table("games").insert(init_data).execute()
        sync(rid, {f"{role}_country": c_name})
        st.session_state.room_id, st.session_state.role = rid, role
        st.rerun()

# --- 4. ゲーム本編 ---
else:
    data = get_game(st.session_state.room_id)
    if not data: st.rerun()
    me, opp = st.session_state.role, ("p2" if st.session_state.role == "p1" else "p1")
    my_name, enemy_name = data.get(f'{me}_country', '自国'), data.get(f'{opp}_country', '敵国')

    # 勝利判定
    if data[f"{me}_hp"] <= 0: st.error("【 敗北 】 領土全域が陥落しました。"); st.stop()
    if data[f"{opp}_hp"] <= 0: st.success("【 勝利 】 敵国を完全に制圧しました。"); st.stop()

    # 情報表示
    st.markdown(f"### 🚩 ENEMY: {enemy_name}")
    st.markdown(f'<div class="status-row"><div class="status-label">領土(HP)</div><div class="bar-bg"><div class="fill-enemy" style="width:{data[f"{opp}_hp"]/10}%"></div></div></div>', unsafe_allow_html=True)
    st.markdown(f'<div class="status-row"><div class="status-label">核開発</div><div class="bar-bg"><div class="fill-nk" style="width:{data[f"{opp}_nuke"]/2}%"></div></div></div>', unsafe_allow_html=True)
    st.caption(f"防衛盾: {data[f'{opp}_shield']} | 対核盾: {data[f'{opp}_nuke_shield_count']} | 植民地: {data[f'{opp}_colony']:.0f}")

    st.divider()

    n_owner = data.get('neutral_owner', 'none')
    n_disp = "🏳️ 中立地帯: 未占領" if n_owner == 'none' else (f"🏳️ 中立地帯: {my_name} 支配" if n_owner == me else f"🏳️ 中立地帯: {enemy_name} 支配")
    st.info(n_disp)
    
    st.markdown(f"### 🛡️ SELF: {my_name}")
    st.markdown(f'<div class="status-row"><div class="status-label">領土(HP)</div><div class="bar-bg"><div class="fill-hp" style="width:{data[f"{me}_hp"]/10}%"></div></div></div>', unsafe_allow_html=True)
    st.markdown(f'<div class="status-row"><div class="status-label">核開発</div><div class="bar-bg"><div class="fill-nk" style="width:{data[f"{me}_nuke"]/2}%"></div></div></div>', unsafe_allow_html=True)
    st.caption(f"盾: {data[f'{me}_shield']} | 対核盾: {data[f'{me}_nuke_shield_count']} | 植民地: {data[f'{me}_colony']:.0f}")

    logs = "".join([f"<div>{m}</div>" for m in data.get('chat', [])[-4:]])
    st.markdown(f'<div class="log-box">{logs}</div>', unsafe_allow_html=True)

    # ターン行動
    if data['turn'] == me:
        if n_owner == me and data['ap'] == 2:
            sync(st.session_state.room_id, {f"{me}_nuke": min(200, data[f'{me}_nuke'] + 15)})

        st.write(f"作戦行動を選択してください（AP: {data['ap']}）")
        c1, c2, c3, c4, c5 = st.columns(5)
        
        with c1:
            if st.button("🛠️軍拡"):
                sync(st.session_state.room_id, {f"{me}_nuke": min(200, data[f'{me}_nuke']+40), "ap": data['ap']-1, "chat": data.get('chat', [])+[f"🛠️ {my_name}: 軍拡"]}); st.rerun()
        with c2:
            if st.button("🛡️防衛"):
                if data[f'{me}_colony'] >= 20:
                    s1 = 1 if random.random() < 0.25 else 0
                    s2 = 1 if random.random() < 0.05 else 0
                    sync(st.session_state.room_id, {f"{me}_colony": data[f'{me}_colony']-20, f"{me}_shield": data[f"{me}_shield"]+s1, f"{me}_nuke_shield_count": data[f"{me}_nuke_shield_count"]+s2, "ap": data['ap']-1, "chat": data.get('chat', [])+[f"🛡️ {my_name}: 防衛網構築"]}); st.rerun()
        with c3:
            if st.button("🕵️工作"):
                sn = (random.random() < 0.4)
                up = {"ap": data['ap']-1, "chat": data.get('chat', [])+[f"🕵️ {my_name}: 工作員派遣"]}
                if sn: up[f"{opp}_nuke"] = max(0, data[f"{opp}_nuke"]-80)
                sync(st.session_state.room_id, up); st.rerun()
        with c4:
            target = st.radio("目標", ["敵国", "中立"], horizontal=True, label_visibility="collapsed")
            if st.button("⚔️進軍"):
                if target == "中立":
                    sync(st.session_state.room_id, {"neutral_owner": me, "ap": data['ap']-1, "chat": data.get('chat', [])+[f"🏳️ {my_name}: 中立支配"]}); st.rerun()
                else:
                    if data[f"{opp}_shield"] > 0:
                        sync(st.session_state.room_id, {f"{opp}_shield": data[f"{opp}_shield"]-1, "ap": data['ap']-1, "chat": data.get('chat', [])+[f"🛡️ {enemy_name}: 防御"]} ); st.rerun()
                    else:
                        dmg = (45 + (data[f'{me}_nuke']*0.5)) + random.randint(-5, 5)
                        new_col = max(0, data[f'{opp}_colony'] - dmg)
                        hp_dmg = max(0, dmg - data[f'{opp}_colony'])
                        sync(st.session_state.room_id, {f"{opp}_colony": new_col, f"{opp}_hp": max(0, data[f'{opp}_hp'] - hp_dmg), "ap": data['ap']-1, "chat": data.get('chat', [])+[f"⚔️ {my_name}: 本土攻撃"]}); st.rerun()
        with c5:
            if st.button("🚩占領"):
                sync(st.session_state.room_id, {f"{me}_colony": data[f'{me}_colony']+50, "ap": data['ap']-1, "chat": data.get('chat', [])+[f"🚩 {my_name}: 植民地拡大"]}); st.rerun()

        # 特殊
        if data[f"{me}_hp"] <= 200:
            if st.button("🏮 神風", type="primary"):
                sync(st.session_state.room_id, {f"{opp}_hp": max(0, data[f"{opp}_hp"]-400), f"{me}_colony": 0, f"{me}_hp": data[f"{me}_hp"]*0.1, "ap": 0, "chat": data.get('chat', [])+[f"🏮 {my_name}: 神風特攻"]}); st.rerun()
        if data[f'{me}_nuke'] >= 200:
            if st.button("🚨 核兵器", type="primary"):
                if data[f"{opp}_nuke_shield_count"] > 0:
                    sync(st.session_state.room_id, {f"{opp}_nuke_shield_count": data[f"{opp}_nuke_shield_count"]-1, f"{me}_nuke": 0, "ap": 0, "chat": data.get('chat', [])+[f"☢️ {enemy_name}: 核迎撃"]}); st.rerun()
                else:
                    sync(st.session_state.room_id, {f"{opp}_hp": data[f"{opp}_hp"]*0.2, f"{opp}_colony": data[f"{opp}_colony"]*0.1, f"{me}_nuke": 0, "ap": 0, "chat": data.get('chat', [])+[f"☢️ {my_name}: 核直撃"]}); st.rerun()

        if data['ap'] <= 0:
            sync(st.session_state.room_id, {"turn": opp, "ap": 2})
            st.rerun()
    else:
        st.info("敵国のターンです。待機中...")
        time.sleep(3)
        st.rerun()

    # チャット（純粋な通信機能）
    with st.form("chat_form", clear_on_submit=True):
        msg = st.text_input("通信文", label_visibility="collapsed", placeholder="メッセージ送信...")
        if st.form_submit_button("送信"):
            # コマンド判定ロジックを完全排除し、すべてを文字列として扱う
            sync(st.session_state.room_id, {"chat": data['chat'] + [f"💬 {my_name}: {msg}"]})
            st.rerun()
