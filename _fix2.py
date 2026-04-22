#!/usr/bin/env python3
path = '/Users/endoshinji/Desktop/valorant Analytics/murash_dashboard_v6.py'
with open(path, 'r', encoding='utf-8') as f:
    src = f.read()

# 1. YEAR フィルターを削除（df_f はリーグ選択のみで決まる）
old1 = """# 年度フィルター
st.sidebar.markdown(
    "<div style='color:#8899aa;font-size:10px;text-transform:uppercase;"
    "letter-spacing:1.2px;margin:8px 0 4px 0'>YEAR</div>",
    unsafe_allow_html=True
)
all_years = sorted([y for y in df_f['year'].dropna().unique().tolist()], reverse=True)
if all_years:
    sel_years = st.sidebar.multiselect("", all_years, default=all_years, label_visibility='collapsed')
    df_f = df_f[df_f['year'].isin(sel_years)] if sel_years else df_f"""
new1 = "# YEAR filter removed - league selection is the only global filter"

# 2. 選手個人レポートの選手選択: チームをfilterの前、年度削除
old2 = """    col_p, col_l, col_y = st.columns([2,1,1])
    with col_p:
        player = st.selectbox("選手", pr_players if pr_players else clean_sorted(df_f['player_name']))
    with col_l:
        p_leagues = clean_sorted(df_f[df_f['player_name']==player]['league'])
        sel_league = st.selectbox("リーグ", ["All"] + p_leagues)
    with col_y:
        p_years = sorted([y for y in df_f[df_f['player_name']==player]['year'].dropna().unique()], reverse=True)
        sel_year = st.selectbox("年度", ["All"] + [str(y) for y in p_years])

    p_df = df_f[df_f['player_name'] == player]
    if sel_league != "All":
        p_df = p_df[p_df['league'] == sel_league]
    if sel_year != "All":
        p_df = p_df[p_df['year'] == int(sel_year)]"""
new2 = """    player = st.selectbox("選手", pr_players if pr_players else clean_sorted(df_f['player_name']))

    p_df = df_f[df_f['player_name'] == player]"""

changed = 0
for old, new in [(old1, new1), (old2, new2)]:
    if old in src:
        src = src.replace(old, new, 1)
        changed += 1
        print(f"OK: replaced block {changed}")
    else:
        print(f"ERROR: block {changed+1} not found")

if changed == 2:
    with open(path, 'w', encoding='utf-8') as f:
        f.write(src)
    print("File saved.")
