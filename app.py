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
    st.error("Secrets (SUPABASE_URL, SUPABASE_KEY) を設定してください。")
    st.stop()

def get_game(rid):
    try:
        res = supabase.table("games").select("*").eq("id", rid).execute()
        return res.data[0] if res.data else None
    except: return None

def sync(rid, updates):
    try: supabase.table("games").update(updates).eq("id", rid).execute()
    except: pass

# --- 2. 漆黒のタクティカルUI ---
st.set_page_config(page_title="DEUS ONLINE: FINAL", layout="centered")
st.markdown("""
    <style>
    html, body, [data-testid="stAppViewContainer"], .main {
        background-color: #000000 !important; color: #00ffcc !important;
        font-family: 'Hiragino Kaku Gothic Pro', sans-serif;
    }
    .stButton > button { 
        background-color: #111 !important; color: #00ffcc !important; 
        border: 2px solid #00ffcc !important; width: 100% !important; font-weight: bold !important;
    }
    .status-row { display: flex; align-items: center; margin-bottom: 6px; }
    .status-label { width: 100px; font-size: 0.75rem; font-weight: bold; }
    .bar-bg { background: #111; width: 100%; height: 14px; border: 1px solid #333; overflow: hidden; }
    .fill-hp { background: #00ffcc; height: 100%; }
    .fill-sh { background: #3498db; height: 100%; }
    .fill-nk { background: #9b59b6; height: 100%; }
    .fill-enemy { background: #ff4b4b; height: 100%; }
    .admin-panel { border: 3px double #ff4b4b; padding: 15px; margin-top: 20px; background: #200; border-radius: 10px; }
    .log-box { background: #050505; padding: 10px; border: 1px solid #333; height: 100px; font-size: 0.8rem; overflow-y: auto; }
    </style>
    """, unsafe_allow_html=True)

if 'room_id' not in st.session_state: st.session_state.room_id = None
if 'is_admin' not in st.session_state: st.session_state.is_admin = False

# --- 3. 接続画面 (認証欄を設置) ---
if not st.session_state.room_id:
    st.title("🛡️ DEUS ONLINE")
    st.subheader("📡 作戦海域への接続")
    
    rid = st.text_input("作戦コード (Room ID)", "7777")
    role = st.radio("役割を選択", ["p1", "p2"], horizontal=True)
    c_name = st.text_input("国名を入力", "帝國")
    
    st.markdown("---")
    # 💡 開発者認証コード入力欄
    st.write("🔧 **SYSTEM OVERRIDE (管理者専用)**")
    auth_input = st.text_input("認証パスコード", type="password", placeholder="コードを入力...")
    
    if st.button("サーバーへ接続"):
        # 認証チェック
        if auth_input == "admin-zero":
            st.session_state.is_admin = True
            st.toast("管理者認証に成功しました。")
        
        if role == "p1":
            init_data = {
                "id": rid, "p1_hp": 1000.0, "p2_hp": 1000.0, "p1_colony": 50.0, "p2_colony": 50.0, 
                "p1_nuke": 0.0, "p2_nuke": 0.0, "turn": "p1", "ap": 2, "chat": ["🛰️ システムオンライン。"],
                "p1_shield": 0, "p2_shield": 0, "p1_nuke_shield_count": 0, "p2_nuke_shield_count": 0,
                "neutral_owner": "none"
            }
            supabase.table("games").delete().eq("id", rid).execute()
            supabase.table("games").insert(init_data).execute()
        
        sync(rid, {f"{role}_country": c_name})
        st.session_state.room_id, st.session_state.role = rid, role
        st.rerun()

# --- 4. メインゲーム ---
else:
    data = get_game(st.session_state.room_id)
    if not data: st.rerun()
    me, opp = st.session_state.role, ("p2" if st.session_state.role == "p1" else "p1")
    my_name, enemy_name = data.get(f'{me}_country', '自国'), data.get(f'{opp}_country', '敵国')
    
    # 勝利条件
    if data[f"{me}_hp"] <= 0: st.error("【敗北】本土が陥落しました。"); st.stop()
    if data[f"{opp}_hp"] <= 0: st.success("【勝利】敵本土を制圧しました。"); st.stop()

    # 敵軍ステータス
    st.markdown(f"🚩 **ENEMY: {enemy_name}**")
    st.markdown(f'<div class="status-row"><div class="status-label">領土HP</div><div class="bar-bg"><div class="fill-enemy" style="width:{data[f"{opp}_hp"]/10}%"></div></div></div>', unsafe_allow_html=True)
    st.markdown(f'<div class="status-row"><div class="status-label">核開発</div><div class="bar-bg"><div class="fill-nk" style="width:{data[f"{opp}_nuke"]/2}%"></div></div></div>', unsafe_allow_html=True)
    st.caption(f"通常盾: {data[f'{opp}_shield']} | 核盾: {data[f'{opp}_nuke_shield_count']} | 植民地: {data[f'{opp}_colony']:.0f}")

    st.divider()

    # 自軍ステータス
    n_owner = data.get('neutral_owner', 'none')
    n_disp = "🏳️ 中立地帯: 未占領" if n_owner == 'none' else (f"🏳️ 中立地帯: {my_name} 支配" if n_owner == me else f"🏳️ 中立地帯: {enemy_name} 支配")
    st.info(n_disp)
    
    st.markdown(f"🛡️ **SELF: {my_name}**")
    st.markdown(f'<div class="status-row"><div class="status-label">本土HP</div><div class="bar-bg"><div class="fill-hp" style="width:{data[f"{me}_hp"]/10}%"></div></div></div>', unsafe_allow_html=True)
    st.markdown(f'<div class="status-row"><div class="status-label">植民地</div><div class="bar-bg"><div class="fill-sh" style="width:{data[f"{me}_colony"]}%"></div></div></div>', unsafe_allow_html=True)
    st.markdown(f'<div class="status-row"><div class="status-label">核開発</div><div class="bar-bg"><div class="fill-nk" style="width:{data[f"{me}_nuke"]/2}%"></div></div></div>', unsafe_allow_html=True)
    st.caption(f"自盾: {data[f'{me}_shield']} | 自核盾: {data[f'{me}_nuke_shield_count']}")

    # ログ
    logs = "".join([f"<div>{m}</div>" for m in data.get('chat', [])[-3:]])
    st.markdown(f'<div class="log-box">{logs}</div>', unsafe_allow_html=True)

    # 行動フェーズ
    if data['turn'] == me:
        # 中立地帯ボーナス
        if n_owner == me and data['ap'] == 2:
            sync(st.session_state.room_id, {f"{me}_nuke": min(200, data[f'{me}_nuke'] + 15)})

        c1, c2, c3, c4, c5 = st.columns(5)
        with c1: 
            if st.button("🛠️軍拡"): sync(st.session_state.room_id, {f"{me}_nuke": min(200, data[f'{me}_nuke']+40), "ap": data['ap']-1, "chat": data.get('chat', [])+[f"🛠️ {my_name}: 軍拡"]}); st.rerun()
        with c2: 
            if st.button("🛡️防衛"):
                if data[f'{me}_colony'] >= 20:
                    s1, s2 = (1 if random.random() < 0.25 else 0), (1 if random.random() < 0.06 else 0)
                    sync(st.session_state.room_id, {f"{me}_colony": data[f'{me}_colony']-20, f"{me}_shield": data[f"{me}_shield"]+s1, f"{me}_nuke_shield_count": data[f"{me}_nuke_shield_count"]+s2, "ap": data['ap']-1, "chat": data.get('chat', [])+[f"🛡️ {my_name}: 防衛構築"]}); st.rerun()
        with c3:
            if st.button("🕵️工作"):
                up = {"ap": data['ap']-1, "chat": data.get('chat', [])+[f"🕵️ {my_name}: 工作"]}
                if random.random() < 0.5: up[f"{opp}_nuke"] = max(0, data[f"{opp}_nuke"]-100)
                sync(st.session_state.room_id, up); st.rerun()
        with c4:
            target = st.radio("目標", ["敵国", "中立"], horizontal=True, label_visibility="collapsed")
            if st.button("⚔️進軍"):
                if target == "中立": sync(st.session_state.room_id, {"neutral_owner": me, "ap": data['ap']-1, "chat": data.get('chat', [])+[f"🏳️ {my_name}: 中立占領"]}); st.rerun()
                else:
                    if data[f"{opp}_shield"] > 0: sync(st.session_state.room_id, {f"{opp}_shield": data[f"{opp}_shield"]-1, "ap": data['ap']-1, "chat": data.get('chat', [])+[f"🛡️ {enemy_name}: 防御"]} ); st.rerun()
                    else:
                        dmg = 45 + (data[f'{me}_nuke']*0.53)
                        rem_col = data[f'{opp}_colony']
                        sync(st.session_state.room_id, {f"{opp}_colony": max(0, rem_col-dmg), f"{opp}_hp": max(0, data[f'{opp}_hp']-max(0, dmg-rem_col)), "ap": data['ap']-1, "chat": data.get('chat', [])+[f"⚔️ {my_name}: 攻撃"]}); st.rerun()
        with c5:
            if st.button("🚩占領"): sync(st.session_state.room_id, {f"{me}_colony": data[f'{me}_colony']+55, "ap": data['ap']-1, "chat": data.get('chat', [])+[f"🚩 {my_name}: 占領"]}); st.rerun()

        # 特殊攻撃
        if data[f"{me}_hp"] <= 200:
            if st.button("🏮 神風", type="primary"): sync(st.session_state.room_id, {f"{opp}_hp": max(0, data[f"{opp}_hp"]-400), f"{me}_colony": 0, f"{me}_hp": data[f"{me}_hp"]*0.1, "ap": 0, "chat": data.get('chat', [])+[f"🏮 {my_name}: 神風特攻"]}); st.rerun()
        if data[f'{me}_nuke'] >= 200:
            if st.button("🚨 核兵器", type="primary"): 
                if data[f"{opp}_nuke_shield_count"] > 0: sync(st.session_state.room_id, {f"{opp}_nuke_shield_count": data[f"{opp}_nuke_shield_count"]-1, f"{me}_nuke": 0, "ap": 0, "chat": data.get('chat', [])+[f"☢️ {enemy_name}: 核迎撃"]}); st.rerun()
                else: sync(st.session_state.room_id, {f"{opp}_hp": data[f"{opp}_hp"]*0.2, f"{opp}_colony": data[f"{opp}_colony"]*0.2, f"{me}_nuke": 0, "ap": 0, "chat": data.get('chat', [])+[f"☢️ {my_name}: 核爆発"]}); st.rerun()

        if data['ap'] <= 0: sync(st.session_state.room_id, {"turn": opp, "ap": 2}); st.rerun()
    else:
        st.info("敵国の作戦待機中...")
        time.sleep(4); st.rerun()

    # --- 🛠️ 管理者パネル (is_adminがTrueの場合のみ出現) ---
    if st.session_state.is_admin:
        st.markdown('<div class="admin-panel">', unsafe_allow_html=True)
        st.error("🚨 ADMIN OVERRIDE PANEL")
        ca, cb, cc = st.columns(3)
        with ca:
            if st.button("☢️ 即時殲滅 (敵HP 0)"):
                sync(st.session_state.room_id, {f"{opp}_hp": 0, "chat": data['chat']+[f"🚨 {my_name}: 衛星軌道上より管理者攻撃"]}); st.rerun()
        with cb:
            if st.button("🔧 領土修復"):
                sync(st.session_state.room_id, {f"{me}_hp": 1000, f"{me}_colony": 100}); st.rerun()
        with cc:
            if st.button("⚡ 核チャージMAX"):
                sync(st.session_state.room_id, {f"{me}_nuke": 200}); st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    with st.form("chat_form", clear_on_submit=True):
        msg = st.text_input("通信文")
        if st.form_submit_button("送信"):
            sync(st.session_state.room_id, {"chat": data['chat'] + [f"💬 {my_name}: {msg}"]}); st.rerun()
