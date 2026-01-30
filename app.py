import streamlit as st
import random
import time

st.set_page_config(page_title="DEUS: Archive Strategy", layout="centered")

# --- 教育用・歴史的記録映像のリスト ---
# PexelsやPixabayなどのロイヤリティフリーかつ教育・記録に適した直接動画リンクを使用
# (YouTubeの埋め込みブロックを避けるため、直接MP4形式などのリンクを推奨)
VIDEO_ASSETS = {
    "AIR": "https://max-dist.com/video/bomber_flight.mp4", # 飛行記録（サンプルURL）
    "ROCKET": "https://max-dist.com/video/rocket_launch.mp4", 
    "NUKE": "https://max-dist.com/video/atomic_test_archive.mp4", 
    "LAB": "https://max-dist.com/video/research_lab.mp4", 
    "DEFENSE": "https://max-dist.com/video/anti_air.mp4",
    "INVASION": "https://max-dist.com/video/landing_operation.mp4"
}

# リンク切れ対策：万が一動画が再生できない場合でもゲームを止めないための予備画像
IMAGE_BACKUP = "https://images.unsplash.com/photo-1518709268805-4e9042af9f23?q=80&w=1000"

if 'state' not in st.session_state:
    st.session_state.state = {
        "p1": {"territory": 100.0, "military": 0.0, "colony": 20.0, "shield": False, "nuke_point": 0},
        "p2": {"territory": 300.0, "military": 50.0, "colony": 50.0, "shield": False},
        "turn": 1,
        "logs": ["SYSTEM: 難易度を選択してください。"],
        "player_ap": 2, 
        "wmd_charging": False,
        "ai_awakened": False,
        "difficulty": None,
        "effect": None,
        "march_count": 0,
        "colony_was_zero": False
    }

s = st.session_state.state
p1, p2 = s["p1"], s["p2"]

# --- ロジック関数群 ---
def apply_damage_to_player(dmg, is_wmd=False):
    if p1["shield"]: dmg *= 0.6
    if p1["colony"] > 0:
        shield_amt = min(p1["colony"], dmg)
        p1["colony"] -= shield_amt
        dmg -= shield_amt
        if p1["colony"] <= 0 and not s["colony_was_zero"]:
            s["effect"] = (VIDEO_ASSETS["INVASION"], "🚨 警告：占領地が陥落しました。本土侵攻の記録映像を確認中。")
            s["colony_was_zero"] = True
    if dmg > 0:
        p1["territory"] = max(0, p1["territory"] - dmg)
        s["logs"].insert(0, f"💥 本国被弾: {dmg:.1f}")

def ai_logic():
    actions = 1 if s["difficulty"] == "小国 (Easy)" else 2
    for _ in range(actions):
        if p2["territory"] <= 0: break
        if s["wmd_charging"]:
            apply_damage_to_player(p1["territory"] * 0.5, is_wmd=True)
            s["wmd_charging"] = False
        else:
            wmd_chance = 0.4 if s["ai_awakened"] else 0.1
            if random.random() < wmd_chance:
                s["wmd_charging"] = True
                s["logs"].insert(0, "⚠️ AIが戦略兵器の稼働準備をしています。")
            else:
                apply_damage_to_player(p2["military"] * 0.25)

def player_step(cmd):
    s["effect"] = None
    if cmd == "DEVELOP":
        p1["military"] += 25.0
        p1["nuke_point"] += 20
        s["effect"] = (VIDEO_ASSETS["LAB"], "🔬 教育資料：戦時下の技術開発プロセス。")
    elif cmd == "DEFEND":
        p1["shield"] = True
        s["effect"] = (VIDEO_ASSETS["DEFENSE"], "🛡️ 教育資料：防空システムの歴史。")
    elif cmd == "MARCH":
        s["march_count"] += 1
        url = VIDEO_ASSETS["AIR"] if s["march_count"] == 1 else VIDEO_ASSETS["ROCKET"]
        cap = "✈️ 航空作戦の記録" if s["march_count"] == 1 else "🚀 遠距離攻撃の記録"
        s["effect"] = (url, cap)
        p2["territory"] -= (p1["military"] * 0.5) + (p1["colony"] * 0.6)
    elif cmd == "OCCUPY":
        if p1["military"] >= 20:
            p1["military"] -= 20
            steal = max(p2["territory"] * 0.20, 40.0)
            p2["territory"] -= steal
            p1["colony"] += steal
    elif cmd == "NUKE":
        s["effect"] = (VIDEO_ASSETS["NUKE"], "☢️ 記録映像：核実験による衝撃波の測定。")
        p2["territory"] *= 0.2
        p1["nuke_point"] = 0

    if p1["military"] >= 100:
        p2["territory"] -= 100.0
        p1["military"] = 0
        s["logs"].insert(0, "💥 総進軍。")

    s["player_ap"] -= 1
    if s["player_ap"] <= 0:
        ai_logic()
        s["player_ap"], s["turn"], p1["shield"] = 2, s["turn"] + 1, False

# --- UIレイアウト ---
if s["difficulty"] is None:
    st.title("DEUS: Archive Strategy")
    st.info("教育的な歴史記録に基づく戦略シミュレーション")
    cols = st.columns(3)
    if cols[0].button("小国 (Easy)"): s["difficulty"]="小国 (Easy)"; st.rerun()
    if cols[1].button("大国 (Normal)"): s["difficulty"]="大国 (Normal)"; st.rerun()
    if cols[2].button("超大国 (Hard)"): s["p2"]["territory"]=500.0; s["ai_awakened"]=True; s["difficulty"]="超大国 (Hard)"; st.rerun()
else:
    # 演出表示
    if s["effect"]:
        try:
            st.video(s["effect"][0]) 
        except:
            st.image(IMAGE_BACKUP, caption="（映像読み込みエラー：代替画像を表示中）")
        st.write(f"### {s['effect'][1]}")
        time.sleep(3)
        s["effect"] = None
        st.rerun()

    # AIステータス
    st.subheader(f"🟥 AI帝国領土: {p2['territory']:.1f}")
    st.progress(max(0.0, min(p2['territory']/500, 1.0)))
    
    st.divider()

    # プレイヤーステータス
    st.subheader(f"🟦 プレイヤー | AP: {s['player_ap']}")
    st.metric("本国領土", f"{p1['territory']:.1f}", f"占領地:{p1['colony']:.1f}")
    
    c1, c2 = st.columns(2)
    c1.progress(p1['military']/100, f"軍事Pt: {p1['military']}/100")
    c2.progress(min(p1['nuke_point']/200, 1.0), f"開発Pt: {p1['nuke_point']}/200")

    if p1["territory"] <= 0:
        st.error("戦況悪化：本国機能が停止しました。")
        if st.button("再起動"): st.session_state.clear(); st.rerun()
    elif p2["territory"] <= 0:
        st.success("作戦成功：平和が維持されました。")
        if st.button("再起動"): st.session_state.clear(); st.rerun()
    else:
        if p1["nuke_point"] >= 200:
            if st.button("🚀 戦略抑止兵器 使用", type="primary", use_container_width=True): player_step("NUKE"); st.rerun()
        
        bc1, bc2 = st.columns(2)
        if bc1.button("🛠 開発", use_container_width=True): player_step("DEVELOP"); st.rerun()
        if bc2.button("🛡 防衛", use_container_width=True): player_step("DEFEND"); st.rerun()
        if bc1.button("⚔️ 進軍", use_container_width=True): player_step("MARCH"); st.rerun()
        if bc2.button("🚩 占領", use_container_width=True): player_step("OCCUPY"); st.rerun()

    st.divider()
    for log in s["logs"][:3]: st.caption(log)
