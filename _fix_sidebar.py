#!/usr/bin/env python3
path = '/Users/endoshinji/Desktop/valorant Analytics/murash_dashboard_v6.py'
with open(path, 'r', encoding='utf-8') as f:
    src = f.read()

# Replace sidebar caption + navigation block
old = '''st.sidebar.markdown("---")
st.sidebar.caption(f"📊 {len(df_f):,} 行 | {df_f['player_name'].nunique()} 選手 | {df_f['league'].nunique()} リーグ")

# ─── ナビゲーション ───────────────────────────────────────
menu = st.sidebar.radio("メニュー", [
    "🔍 スカウティング比較",
    "👤 選手個人レポート",
    "🗺️ マップ別分析",
    "📈 スタッツ別選手ランキング",
])'''

new = '''st.sidebar.markdown("---")
st.sidebar.markdown(
    f"<div style='color:#8899aa;font-size:11px'>"
    f"{df_f['player_name'].nunique()} 選手 &nbsp;|&nbsp; "
    f"{df_f['league'].nunique()} リーグ</div>",
    unsafe_allow_html=True
)
st.sidebar.markdown("")
menu = st.sidebar.radio("", [
    "🔍 スカウティング比較",
    "👤 選手個人レポート",
    "🗺️ マップ別分析",
    "📈 スタッツ別選手ランキング",
], label_visibility='collapsed')'''

if old in src:
    src = src.replace(old, new, 1)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(src)
    print("OK: sidebar updated")
else:
    print("ERROR: pattern not found")
    # show context
    idx = src.find('st.sidebar.caption')
    print(repr(src[idx-5:idx+200]))
