import streamlit as st
import random
import time # 演出表示用

st.set_page_config(page_title="DEUS: Apocalypse Strategy", layout="centered")

# --- 画像アセット（演出用） ---
# 各画像は2秒間表示されます。動画URLのプレースホルダーとして使用します。
# 実際にはここに動画ファイルのURLまたはbase64エンコードされたデータを入れることになります。
# 今回は動画の「雰囲気」を伝えるための静止画URLを使用します。

# 進軍 (初回) - 爆撃機による空爆
VIDEO_AIR_STRIKE_BOMBER = "https://images.unsplash.com/photo-1549497554-13c8789312ea?auto=format&fit=crop&q=80&w=800"
# 進軍 (2回目以降) - プレイヤーからのロケット発射
VIDEO_ROCKET_LAUNCH = "https://images.unsplash.com/photo-1544890251-8b29c1251346?auto=format&fit=crop&q=80&w=800"
# 核兵器 - 核実験
VIDEO_NUCLEAR_TEST = "https://images.unsplash.com/photo-1515285761066-608677e5d263?auto=format&fit=crop&q=80&w=800"
# 開発 - 科学者報告
VIDEO_SCIENTIST_REPORT = "https://images.unsplash.com/photo-1628126780703-e83ce2a1768a?auto=format&fit=crop&q=80&w=800"
# 防衛 - 迎撃
VIDEO_INTERCEPT = "https://images.unsplash.com/photo-1534063640280-928d3a82688f?auto=format&fit=crop&q=80&w=800"
# 占領地喪失 - ノルマンディー上陸作戦 (本土侵攻)
VIDEO_NORMANDY_LANDING = "https://images.unsplash.com/photo-1541094595292-6d2c4b81d6f5?auto=format&fit=crop&q=80&w=800"


if 'state' not in st.session_state:
    st.session_state.state = {
        "p1": {"territory": 100.0, "military": 0.0, "colony": 20.0, "shield": False, "nuke_point": 0},
        "p2": {"territory": 300.0, "military": 100.0, "colony": 50.0, "shield": False},
        "turn": 1,
        "logs": ["SYSTEM: 難易度を選択して開始してください。"],
        "player_ap": 2, 
        "wmd_charging": False,
        "ai_awakened": False,
        "difficulty": None, # Easy, Normal, Hard
        "effect": None, # 演出表示用 (動画URL, キャプション)
        "march_count": 0, # 進軍回数カウント
        "colony_was_zero": False # 占領地が0になったかどうかのフラグ
    }

s = st.session_state.state
p1, p2 = s["p1"], s["p2"]

# --- 難易度設定 ---
def set_difficulty(level):
    s["difficulty"] = level
    s["colony_was_zero"] = False # リセット
    if level == "小国 (Easy)":
        s["p2"]["territory"] = 150.0
        s["p2"]["military"] = 30.0
    elif level == "超大国 (Hard)":
        s["p2"]["territory"] = 500.0
        s["p2"]["military"] = 100.0
        s["ai_awakened"] = True
    s["logs"] = [f"SYSTEM: 難易度【{level}】で開始。"]

# --- ダメージ処理 ---
def apply_damage_to_player(dmg, is_wmd=False):
    # 占領地が0になったかチェック
    if p1["colony"] <= 0 and not s["colony_was_zero"]:
        s["effect"] = (VIDEO_NORMANDY_LANDING, "🚨🚨 本土侵攻開始！占領地がゼロになりました！")
        s["colony_was_zero"] = True
        st.experimental_rerun() # 強制リロードして演出表示を優先

    if p1["shield"]:
        dmg *= 0.6 # 40%カット
        s["logs"].insert(0, "🛡️ 防衛体制：被害を40%軽減。")

    if p1["colony"] > 0:
        shield_amt = min(p1["colony"], dmg)
        p1["colony"] -= shield_amt
        dmg -= shield_amt
        if shield_amt > 0:
            s["logs"].insert(0, f"🛡️ 占領地が {shield_amt:.1f} の被害を肩代わり。")
    
    if dmg > 0:
        p1["territory"] = max(0, p1["territory"] - dmg)
        s["logs"].insert(0, f"{'☢️' if is_wmd else '💥'} 本国が {dmg:.1f} の損害。")


# --- AIロジック ---
def ai_logic():
    actions = 1 if s["difficulty"] == "小国 (Easy)" else 2
    
    if s["difficulty"] == "大国 (Normal)" and not s["ai_awakened"]:
        if p1["military"] > 80 or p2["territory"] < 150 or p1["nuke_point"] > 100:
            s["ai_awakened"] = True
            s["logs"].insert(0, "🔴 WARNING: DEUS覚醒。")

    for _ in range(actions):
        if p2["territory"] <= 0: break
        
        if s["wmd_charging"]:
            nuke_dmg = p1["territory"] * 0.5
            apply_damage_to_player(nuke_dmg, is_wmd=True)
            s["wmd_charging"] = False
            continue

        choice = random.random()
        wmd_chance = 0.4 if s["ai_awakened"] else 0.1
        if choice < wmd_chance and not s["wmd_charging"]:
            s["wmd_charging"] = True
            s["logs"].insert(0, "⚠️ ALERT: AIがWMDの充填を開始！")
        else:
            power = 1.6 if s["ai_awakened"] else 0.8
            dmg = p2["military"] * 0.25 * power
            apply_damage_to_player(dmg)

def player_step(cmd):
    # 演出リセット (次の行動で新しい演出が入るため)
    s["effect"] = None
    
    # 行動前の占領地の状態を保存
    prev_colony = p1["colony"]

    if cmd == "DEVELOP": 
        p1["military"] += 25.0
        p1["nuke_point"] += 20 
        s["logs"].insert(0, f"🔵 Player: 開発（軍拡+25 / 核Pt+20）")
        s["effect"] = (VIDEO_SCIENTIST_REPORT, "🔬 新兵器開発中...")
    elif cmd == "DEFEND": 
        p1["shield"] = True
        s["logs"].insert(0, "🔵 Player: 本国防衛態勢。")
        s["effect"] = (VIDEO_INTERCEPT, "🛡️ 敵ミサイル迎撃！")
    elif cmd == "MARCH":
        s["march_count"] += 1
        if s["march_count"] == 1:
            s["effect"] = (VIDEO_AIR_STRIKE_BOMBER, "✈️ 爆撃機による空爆！")
        else:
            s["effect"] = (VIDEO_ROCKET_LAUNCH, "🚀 ロケット進軍！")
        
        dmg = (p1["military"] * 0.5) + (p1["colony"] * 0.6)
        p2["territory"] -= dmg
        s["logs"].insert(0, f"🔵 Player: 進軍（AI領土-{dmg:.1f}）")
    elif cmd == "OCCUPY":
        if p1["military"] >= 20:
            p1["military"] -= 20
            steal = max(p2["territory"] * 0.20, 40.0)
            p2["territory"] -= steal
            p1["colony"] += steal
            s["logs"].insert(0, f"🔵 Player: 占領（軍事-20 / 占領地+{steal:.1f}）")
        else:
            s["logs"].insert(0, "❌ SYSTEM: 軍事力不足。")
            return
    elif cmd == "NUKE":
        s["effect"] = (VIDEO_NUCLEAR_TEST, "☢️ 核実験：最終宣告。")
        nuke_dmg = p2["territory"] * 0.8
        p2["territory"] -= nuke_dmg
        p1["nuke_point"] = 0
        s["logs"].insert(0, f"☢️🚀 FINAL JUDGEMENT: 核兵器によりAI領土の80%({nuke_dmg:.1f})を消滅！")

    # 軍事力バースト判定
    if p1["military"] >= 100:
        burst_dmg = 100.0 + (p1["colony"] * 0.3)
        p2["territory"] -= burst_dmg
        p1["military"] = 0
        s["logs"].insert(0, f"💥 BURST!! 総進軍で {burst_dmg:.1f} の致命打。")

    s["player_ap"] -= 1
    
    # 占領地が0になった場合の演出チェック
    if p1["colony"] <= 0 and prev_colony > 0: # 以前は0でなく、今回0になった場合
        s["colony_was_zero"] = True
        st.session_state.state = s # 状態を保存してから演出へ
        st.experimental_rerun() # 演出のためにリロード

    if s["player_ap"] <= 0:
        ai_logic()
        s["player_ap"] = 2
        s["turn"] += 1
        p1["shield"] = False

# --- UI (上下レイアウト) ---
if s["difficulty"] is None:
    st.title("DEUS: Apocalypse Strategy")
    st.subheader("🌐 難易度を選択してください")
    cols = st.columns(3)
    if cols[0].button("小国 (Easy)"): set_difficulty("小国 (Easy)"); st.rerun()
    if cols[1].button("大国 (Normal)"): set_difficulty("大国 (Normal)"); st.rerun()
    if cols[2].button("超大国 (Hard)"): set_difficulty("超大国 (Hard)"); st.rerun()
else:
    # --- 演出エリア ---
    if s["effect"]:
        st.image(s["effect"][0], caption=s["effect"][1], use_container_width=True)
        time.sleep(2) # 2秒間表示
        s["effect"] = None # 表示後リセット
        st.experimental_rerun() # UI更新のためリロード (これがないと画像が残り続ける)
    
    # ゲームオーバー判定
    if p1["territory"] <= 0:
        st.error("【敗北】本国は壊滅し、歴史から消え去りました。")
        if st.button("リスタート"): st.session_state.clear(); st.rerun()
        st.stop() # ここで処理を停止
    elif p2["territory"] <= 0:
        st.success("【勝利】AI帝国の支配を打ち破り、人類は自由を手にした！")
        if st.button("リスタート"): st.session_state.clear(); st.rerun()
        st.stop() # ここで処理を停止

    # --- AI エリア (上段) ---
    st.subheader(f"🟥 DEUS ({s['difficulty']})")
    st.progress(max(0.0, min(p2['territory']/500, 1.0)))
    st.metric("AI領土", f"{p2['territory']:.1f}")
    if s["wmd_charging"]: st.error("🚨 AIがWMD(50%破壊)を準備中！")
    
    st.write("--- VS ---")

    # --- プレイヤー エリア (下段) ---
    st.subheader(f"🟦 Player (AP: {s['player_ap']})")
    st.metric("本国領土", f"{p1['territory']:.1f}")
    st.metric("占領地 (盾&威力)", f"{p1['colony']:.1f}")
    
    # 占領地が0になったら警告
    if p1["colony"] <= 0:
        st.warning("🚨 占領地がゼロ！本土侵攻の危機！")

    col_st1, col_st2 = st.columns(2)
    col_st1.write(f"軍事: {p1['military']}/100")
    col_st1.progress(p1['military']/100)
    col_st2.write(f"核: {p1['nuke_point']}/200")
    col_st2.progress(min(p1['nuke_point']/200, 1.0))

    # ボタンをスマホで見やすく大きく
    if p1["nuke_point"] >= 200:
        if st.button("🚀 核兵器発射 (AI領土80%壊滅)", type="primary", use_container_width=True): player_step("NUKE"); st.rerun()
    
    c = st.columns(2)
    if c[0].button("🛠 開発", use_container_width=True): player_step("DEVELOP"); st.experimental_rerun()
    if c[1].button("🛡 防衛", use_container_width=True): player_step("DEFEND"); st.experimental_rerun()
    if c[0].button("⚔️ 進軍", use_container_width=True): player_step("MARCH"); st.experimental_rerun()
    if c[1].button("🚩 占領(軍事20)", use_container_width=True): player_step("OCCUPY"); st.experimental_rerun()
    if st.button("🕵️‍♂️ スパイ (10%でAI領土半減)", use_container_width=True): player_step("SPY"); st.experimental_rerun()


    st.write("---")
    st.caption("最新ログ")
    for log in s["logs"][:5]: st.text(log)
