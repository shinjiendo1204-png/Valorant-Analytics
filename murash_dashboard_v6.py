"""
- League カテゴリー対応 (VCT / VCJ / 他リーグ横断)
- hs_pct (ヘッドショット率) 追加
- クラッチ詳細分析強化
- 複数CSV結合対応
"""

import os
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import numpy as np

# ─── ページ設定 ────────────────────────────────────────────
st.set_page_config(
    layout="wide",
    page_title="VCJ Analytics Dashboard",
    page_icon="📊",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
/* ========= BASE ========= */
.main, [data-testid="stAppViewContainer"] { background-color: #0e1117; }
[data-testid="stSidebar"] { background-color: #0e1117; border-right: 1px solid #1e2333; }
/* Streamlit top header: match app background */
[data-testid="stHeader"] { background-color: #0e1117 !important; }
[data-testid="stToolbar"] { background-color: #0e1117 !important; }
header[data-testid="stHeader"] { background: #0e1117 !important; border-bottom: 1px solid #1e2333; }
/* sidebar text */
[data-testid="stSidebar"] label, [data-testid="stSidebar"] span,
[data-testid="stSidebar"] p, [data-testid="stSidebar"] div { color: #ddd !important; }
/* tabs: keep contrast, don't force all spans white */
[data-testid="stTabs"] [role="tab"] { color: #8899aa !important; font-size:13px; }
[data-testid="stTabs"] [role="tab"]:hover { color: #ccc !important; }
[data-testid="stTabs"] [role="tab"][aria-selected="true"] { color: white !important; border-bottom: 2px solid #e63946 !important; }
[data-testid="stTabsContent"] { color: white; }
/* general body text */
[data-testid="stMarkdownContainer"] p { color: white; }
[data-testid="stWidgetLabel"] p { color: #ccc !important; }
.stSelectbox label, .stMultiSelect label, .stTextInput label { color: #ccc !important; font-size: 13px; }
/* caption */
[data-testid="stCaptionContainer"] { color: #8899aa !important; }
/* alert boxes */
[data-testid="stAlert"] div { color: white !important; }

/* ========= METRICS ========= */
[data-testid="stMetric"] {
    background: linear-gradient(135deg, #111827, #1a2235);
    border-radius: 10px; padding: 16px 20px;
    border: 1px solid #1e2d45;
    border-left: 3px solid #e63946;
}
[data-testid="stMetricValue"] { color: white !important; font-size: 1.8rem !important; font-weight: 700 !important; letter-spacing: -0.5px; }
[data-testid="stMetricLabel"] { color: #8899aa !important; font-size: 0.75rem !important; text-transform: uppercase; letter-spacing: 1px; }
[data-testid="stMetricDelta"] { color: #2ecc71 !important; }

/* ========= PLAYER CARD ========= */
.player-card {
    background: linear-gradient(160deg, #111827 0%, #0d1520 100%);
    border-radius: 12px; padding: 18px;
    border: 1px solid #1e2d45;
    margin: 6px 0;
    box-shadow: 0 4px 20px rgba(0,0,0,0.4);
}
.player-card h3 { font-size: 1.1rem; letter-spacing: 0.5px; }

/* ========= STAT TABLE (custom HTML) ========= */
.stat-table { width:100%; border-collapse:collapse; font-size:13px; }
.stat-table th {
    background:#131b2a; color:#8899aa;
    text-transform:uppercase; font-size:10px; letter-spacing:1.2px;
    padding:5px 10px; text-align:left; border-bottom:1px solid #1e2d45;
}
.stat-table td { padding:5px 10px; border-bottom:1px solid #141c2c; color:white; }
.stat-table tr:last-child td { border-bottom:none; }
.stat-table tr:hover td { background:rgba(230,57,70,0.07); }
.stat-table td.rank { color:#8899aa; font-size:11px; width:28px; }
.stat-table td.player { font-weight:600; color:white; }
.stat-table td.team { color:#8899aa; font-size:12px; }
.stat-table td.role-d { color:#e63946; font-size:11px; font-weight:600; }
.stat-table td.role-i { color:#457b9d; font-size:11px; font-weight:600; }
.stat-table td.role-c { color:#2ecc71; font-size:11px; font-weight:600; }
.stat-table td.role-s { color:#f1c40f; font-size:11px; font-weight:600; }
.stat-table td.num { font-variant-numeric:tabular-nums; font-weight:500; }
.stat-table td.num-hi { font-variant-numeric:tabular-nums; font-weight:700; color:white; }
.stat-table td.num-riv { font-variant-numeric:tabular-nums; font-weight:700; color:white; }

/* ========= SECTION TITLE ========= */
.section-title {
    color: white; font-size: 18px; font-weight: 700;
    letter-spacing: 0.5px;
    border-bottom: 2px solid #e63946;
    padding-bottom: 10px; margin: 20px 0 14px 0;
    text-transform: uppercase;
}
.sub-title {
    color: #8899aa; font-size: 11px; text-transform: uppercase;
    letter-spacing: 1.5px; margin: 16px 0 8px 0;
}

/* ========= RANK BADGE ========= */
.rank-badge {
    background: #e63946; color: white;
    border-radius: 4px; padding: 2px 8px;
    font-size: 11px; font-weight: 700; letter-spacing: 0.5px;
}
.rank-badge-gold { background:#b8860b; }
.rank-badge-silver { background:#6c757d; }

/* ========= MAP BADGE ========= */
.map-best { display:inline-block; background:rgba(46,204,113,0.15); color:#2ecc71;
    border:1px solid #2ecc71; border-radius:6px; padding:4px 10px; font-size:12px; font-weight:600; }
.map-worst { display:inline-block; background:rgba(230,57,70,0.15); color:#e63946;
    border:1px solid #e63946; border-radius:6px; padding:4px 10px; font-size:12px; font-weight:600; }

/* ========= HIDE STREAMLIT DEFAULTS ========= */
[data-testid="stDataFrame"] { display:none; }
div[data-testid="stDataFrameResizable"] { display:none; }
footer { visibility:hidden; }
#MainMenu { visibility:hidden; }
</style>
""", unsafe_allow_html=True)


# ─── HTMLテーブルヘルパー ─────────────────────────────────────
def role_class(role: str) -> str:
    return {'Duelist':'role-d','Initiator':'role-i','Controller':'role-c','Sentinel':'role-s'}.get(role,'team')

def role_td(role: str) -> str:
    """role列用: CSSクラス + カタカナ表示"""
    rc = role_class(role)
    return f'<td class="{rc}">{rja(role)}</td>'

def html_table(rows: list[dict], cols: list[tuple], max_rows: int = 50) -> str:
    """rows: list of dicts, cols: list of (key, label, css_class, fmt)"""
    ths = ''.join(f'<th>{label}</th>' for _, label, _, _ in cols)
    trs = ''
    for row in rows[:max_rows]:
        tds = ''
        for key, _, css, fmt in cols:
            val = row.get(key, '')
            if key == 'role':
                tds += role_td(str(val))
                continue
            if key == 'agent':
                tds += f'<td class="player">{aja(str(val))}</td>'
                continue
            try:
                display = fmt.format(val) if fmt and val != '' and val is not None and not (isinstance(val, float) and np.isnan(val)) else (str(val) if val != '' else '-')
            except Exception:
                display = str(val)
            tds += f'<td class="{css}">{display}</td>'
        trs += f'<tr>{tds}</tr>'
    return f'<div style="overflow-x:auto"><table class="stat-table"><thead><tr>{ths}</tr></thead><tbody>{trs}</tbody></table></div>'


# ══════════════════════════════════════════════════════════
# データ前処理
# ══════════════════════════════════════════════════════════
# --- Agent->Role mapping (must be defined before process_data) ---
AGENT_ROLES = {
    'Jett':'Duelist','Reyna':'Duelist','Raze':'Duelist','Phoenix':'Duelist',
    'Yoru':'Duelist','Neon':'Duelist','Iso':'Duelist','Waylay':'Duelist',
    'Sova':'Initiator','Breach':'Initiator','Skye':'Initiator',
    'KAYO':'Initiator','KAY/O':'Initiator','Kay/O':'Initiator','Fade':'Initiator',
    'Gekko':'Initiator','Vyse':'Initiator','Tejo':'Initiator',
    'Miks':'Controller',
    'Brimstone':'Controller','Viper':'Controller','Omen':'Controller',
    'Astra':'Controller','Harbor':'Controller','Clove':'Controller',
    'Killjoy':'Sentinel','Cypher':'Sentinel','Sage':'Sentinel',
    'Chamber':'Sentinel','Deadlock':'Sentinel','Veto':'Sentinel',
}
ROLE_COLORS = {
    'Duelist':'#e63946','Initiator':'#457b9d',
    'Controller':'#2ecc71','Sentinel':'#f1c40f','Unknown':'#888888'
}
ROLE_JA = {
    'Duelist':    'デュエリスト',
    'Initiator':  'イニシエーター',
    'Controller': 'コントローラー',
    'Sentinel':   'センチネル',
    'Unknown':    '不明',
}
AGENT_JA = {
    # Duelist
    'Jett':     'ジェット',
    'Reyna':    'レイナ',
    'Raze':     'レイズ',
    'Phoenix':  'フィニックス',
    'Yoru':     'ヨル',
    'Neon':     'ネオン',
    'Iso':      'アイソ',
    'Waylay':   'ウェイレイ',
    # Initiator
    'Sova':     'ソーヴァ',
    'Breach':   'ブリーチ',
    'Skye':     'スカイ',
    'KAYO':     'KAY/O',
    'KAY/O':    'KAY/O',
    'Kay/O':    'KAY/O',
    'Fade':     'フェイド',
    'Gekko':    'ゲッコー',
    'Vyse':     'ヴァイス',
    'Tejo':     'テホ',
    # Controller
    'Brimstone': 'ブリムストーン',
    'Viper':    'ヴァイパー',
    'Omen':     'オーメン',
    'Astra':    'アストラ',
    'Harbor':   'ハーバー',
    'Clove':    'クローブ',
    'Miks':     'ミクス',
    # Sentinel
    'Killjoy':  'キルジョイ',
    'Cypher':   'サイファー',
    'Sage':     'セージ',
    'Chamber':  'チェンバー',
    'Deadlock': 'デッドロック',
    'Veto':     'ヴィトー',
}

def rja(role: str) -> str:
    """ロールをカタカナ表示名に変換"""
    return ROLE_JA.get(role, role)

def aja(agent: str) -> str:
    """エージェントをカタカナ表示名に変換"""
    return AGENT_JA.get(agent, agent)

def get_primary_role(agents_str: str) -> str:
    if not agents_str or str(agents_str) in ('', 'nan', 'None'):
        return 'Unknown'
    first = str(agents_str).split('|')[0].strip()
    return AGENT_ROLES.get(first, 'Unknown')

def count_matches(sub_df: pd.DataFrame) -> int:
    if 'game_id' in sub_df.columns:
        return sub_df['game_id'].nunique()
    if 'match_id' in sub_df.columns:
        return sub_df['match_id'].nunique()
    return len(sub_df)


@st.cache_data
def process_data(df_raw: pd.DataFrame) -> pd.DataFrame:
    df = df_raw.copy()

    # --- 日付・年度 ---
    if 'Date' in df.columns:
        df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
        df['year'] = df['Date'].dt.year.astype('Int64')
    elif 'year' not in df.columns:
        df['year'] = pd.NA

    # --- League カラムが無ければ空文字で作成 ---
    if 'league' not in df.columns:
        df['league'] = ''

    # --- game_idがない場合は match_id + map_name で生成 ---
    if 'game_id' not in df.columns and 'match_id' in df.columns:
        map_col = df['map_name'].astype(str) if 'map_name' in df.columns else pd.Series([''] * len(df), index=df.index)
        df['game_id'] = df['match_id'].astype(str) + '_' + map_col.str.strip()

    # --- Dateがない場合は yearから代用日付を作成 ---
    if 'Date' not in df.columns and 'year' in df.columns:
        df['Date'] = pd.to_datetime(df['year'].astype(str) + '-01-01', errors='coerce')

    # --- 文字列カラム クリーニング ---
    str_cols = ['player_name', 'team1_name', 'team2_name', 'map_name',
                'agents', 'player_team', 'league', 'stage', 'phase']
    for col in str_cols:
        if col in df.columns:
            df[col] = df[col].astype(str).str.strip().replace({'nan': '', 'None': '', 'NaN': ''})

    df = df[df['player_name'].notna() & (df['player_name'] != '') & (df['player_name'] != 'nan')]

    # --- パーセンタイル ---
    pct_cols = ['RIV', 'rating', 'acs', 'adr', 'kast', 'first_kills', 'hs_pct', 'fkfd_ratio']
    for col in pct_cols:
        if col in df.columns:
            df[f'{col}_pct'] = df[col].rank(pct=True) * 100

    # --- クラッチ合計 ---
    clutch_cols = [c for c in df.columns if c.startswith('clutch_1v')]
    if clutch_cols:
        df['clutch_total'] = df[clutch_cols].sum(axis=1)

    # --- FK/FD比 ---
    if 'first_kills' in df.columns and 'first_deaths' in df.columns:
        df['fkfd_ratio'] = (df['first_kills'] / df['first_deaths'].replace(0, 0.5)).round(2)

    return df


# ══════════════════════════════════════════════════════════
# CSV ロード（ローカル自動検出 + アップロード + 複数ファイル結合）
# ══════════════════════════════════════════════════════════
WORKSPACE = os.path.dirname(os.path.abspath(__file__))

def find_local_csvs():
    pass  # replaced by discover_leagues


def discover_leagues() -> dict:
    """CSVをスキャンし {league_name: [path, ...]} を返す"""
    result = {}
    for fname in sorted(os.listdir(WORKSPACE)):
        if not fname.endswith('.csv') or fname.startswith('.'):
            continue
        path = os.path.join(WORKSPACE, fname)
        try:
            sample = pd.read_csv(path, nrows=1)
            lname = str(sample['league'].iloc[0]).strip() if 'league' in sample.columns else ''
            if not lname or lname in ('nan', ''):
                lname = fname.replace('.csv', '')
        except Exception:
            lname = fname.replace('.csv', '')
        result.setdefault(lname, []).append(path)
    return result


def load_csv(path: str) -> pd.DataFrame:
    df = pd.read_csv(path)
    if 'league' not in df.columns or df['league'].astype(str).str.strip().eq('').all():
        df['league'] = os.path.basename(path).replace('.csv', '')
    return df


# ── Sidebar ──────────────────────────────────────────────
st.sidebar.markdown("""
<div style='padding:12px 0 8px 0'>
    <div style='font-size:10px;color:#8899aa;text-transform:uppercase;
                letter-spacing:2px;margin-bottom:2px'>Valorant</div>
    <div style='font-size:18px;font-weight:700;color:white'>Analytics for VCJ</div>
</div>
""", unsafe_allow_html=True)
st.sidebar.markdown("---")

league_dict = discover_leagues()
if not league_dict:
    st.markdown("""<div style='background:#1a1d26;border-radius:10px;padding:40px;text-align:center;'>
    <h2 style='color:white'>CSVが見つかりません</h2>
    <p style='color:#888'>ダッシュボードと同じフォルダにCSVを配置してください</p></div>""",
                  unsafe_allow_html=True)
    st.stop()

all_league_names = sorted(league_dict.keys())
st.sidebar.markdown(
    "<div style='color:#8899aa;font-size:10px;text-transform:uppercase;"
    "letter-spacing:1.2px;margin-bottom:4px'>LEAGUE</div>",
    unsafe_allow_html=True
)
selected_league_names = st.sidebar.multiselect(
    "",
    options=all_league_names,
    default=all_league_names,
    label_visibility='collapsed'
)

frames = []
for lname in selected_league_names:
    for path in league_dict[lname]:
        frames.append(load_csv(path))

if not frames:
    st.markdown("""<div style='background:#1a1d26;border-radius:10px;padding:40px;text-align:center;'>
    <h2 style='color:white'>リーグを選択してください</h2>
    <p style='color:#888'>サイドバーの LEAGUE から選択してください</p></div>""",
                  unsafe_allow_html=True)
    st.stop()

raw_df = pd.concat(frames, ignore_index=True)
df = process_data(raw_df)
# role列を附与
if 'agents' in df.columns:
    df['role'] = df['agents'].apply(get_primary_role)


# リーグは上部の選択で決まっているので、dfに對応する行のみを使用
df_f = df[df['league'].isin(selected_league_names)] if selected_league_names else df

# YEAR filter removed - league selection is the only global filter

# consistency_scoreが df_f になければ常に追加
if 'consistency_score' in df.columns and 'consistency_score' not in df_f.columns:
    df_f = df_f.merge(
        df[['player_name','consistency_score','consistency_pct']].drop_duplicates('player_name'),
        on='player_name', how='left'
    )

st.sidebar.markdown("---")
st.sidebar.markdown(
    f"<div style='color:#8899aa;font-size:11px'>"
    f"{df_f['player_name'].nunique()} 選手 &nbsp;|&nbsp; "
    f"{df_f['league'].nunique()} リーグ</div>",
    unsafe_allow_html=True
)

# ─── ナビゲーション ───────────────────────────────────────
st.sidebar.markdown("")
menu = st.sidebar.radio("", [
    "🔍 スカウティング比較",
    "👤 選手個人レポート",
    "🗺️ マップ別分析",
    "📈 スタッツ別選手ランキング",
], label_visibility='collapsed')


# ══════════════════════════════════════════════════════════
# ヘルパー
# ══════════════════════════════════════════════════════════
def pct_color(pct):
    if pct >= 80: return "#2ecc71"
    elif pct >= 60: return "#f1c40f"
    elif pct >= 40: return "#e67e22"
    return "#e74c3c"

def consistency_score(values):
    vals = [v for v in values if pd.notna(v)]
    if len(vals) < 2: return 50
    cv = np.std(vals) / (np.mean(vals) + 1e-9)
    return max(0, min(100, 100 - cv * 100))

def clean_sorted(series):
    return sorted([v for v in series.unique() if v and str(v) not in ('', 'nan', 'None')])

# ─── 表示名小辞典（全体共通） ──────────────────────────────────────────
STAT_LABELS = {
    'rating':            'Rating',
    'RIV':               'RIV',
    'kast':              'KAST',
    'acs':               'ACS',
    'adr':               'ADR',
    'hs_pct':            'HS%',
    'fkfd_ratio':        'FK/FD',
    'first_kills':       'FK',
    'first_deaths':      'FD',
    'kills':             'K',
    'deaths':            'D',
    'assists':           'A',
    'clutch_total':      'Clutch',
    'consistency_score': '安定性',
    'player_name':       'PLAYER',
    'player_team':       'TEAM',
    'map_name':          'MAP',
    'role':              'ROLE',
    'agents':            'AGENT',
    '試合数':           'GP',
}

def slabel(col: str) -> str:
    """カラム名 -> 表示名"""
    return STAT_LABELS.get(col, col)

CHART_LAYOUT = dict(
    paper_bgcolor='#0e1117', plot_bgcolor='#1a1d26',
    font=dict(color='white'),
    title_font=dict(color='white', size=14),
    xaxis=dict(gridcolor='#2d3142', title_font=dict(color='white'), tickfont=dict(color='white')),
    yaxis=dict(gridcolor='#2d3142', title_font=dict(color='white'), tickfont=dict(color='white')),
    legend=dict(bgcolor='#1a1d26', font=dict(color='white')),
    margin=dict(t=50, b=30),
)
COLORS = ['#e63946', '#457b9d', '#2ecc71', '#f1c40f', '#9b59b6']

def radar_chart(players_stats: dict, labels: list, title: str):
    fig = go.Figure()
    # close average polygon too
    avg_labels_closed = list(labels) + [labels[0]]
    avg_r_closed = [50] * len(labels) + [50]
    fig.add_trace(go.Scatterpolar(
        r=avg_r_closed, theta=avg_labels_closed, fill='toself',
        name='リーグ平均', line_color='gray', opacity=0.2,
        fillcolor='rgba(128,128,128,0.1)'
    ))
    for i, (name, stats) in enumerate(players_stats.items()):
        c = COLORS[i % len(COLORS)]
        r, g, b = int(c[1:3],16), int(c[3:5],16), int(c[5:7],16)
        # close polygon explicitly (append first point) to avoid gap
        closed_r     = list(stats)  + [stats[0]]
        closed_theta = list(labels) + [labels[0]]
        fig.add_trace(go.Scatterpolar(
            r=closed_r, theta=closed_theta, fill='toself', name=name,
            line_color=c, fillcolor=f'rgba({r},{g},{b},0.15)'
        ))
    fig.update_layout(
        polar=dict(
            radialaxis=dict(visible=True, range=[0,100], gridcolor='#2d3142', tickfont=dict(color='#888')),
            bgcolor='#1a1d26', angularaxis=dict(gridcolor='#2d3142')
        ),
        title=dict(text=title, font=dict(color='white', size=14)),
        **{k:v for k,v in CHART_LAYOUT.items() if k not in ('xaxis','yaxis','margin')},
        margin=dict(t=60, b=20)
    )
    return fig


# ══════════════════════════════════════════════════════════
# 1. スカウティング比較
# ══════════════════════════════════════════════════════════
# consistency_score is now defined above; compute per-player scores here
# consistency_scoreはフィルター前の df で計算し、df_fにも反映させる
if 'rating' in df.columns and 'consistency_score' not in df.columns:
    _cons_map = df.groupby('player_name')['rating'].apply(
        lambda x: consistency_score(x.dropna().tolist())
    ).rename('consistency_score')
    df = df.merge(_cons_map, on='player_name', how='left')
    df['consistency_pct'] = df['consistency_score'].rank(pct=True) * 100
    # df_fにも反映（フィルター後だがカラム追加）
    if 'consistency_score' not in df_f.columns:
        df_f = df_f.merge(
            df[['player_name','consistency_score','consistency_pct']].drop_duplicates('player_name'),
            on='player_name', how='left'
        )

if menu == "🔍 スカウティング比較":
    st.markdown('<div class="section-title">スカウティング比較</div>', unsafe_allow_html=True)

    # -- team / role filter --
    f_col1, f_col2 = st.columns(2)
    with f_col1:
        team_opts = ["All"] + (clean_sorted(df_f['player_team']) if 'player_team' in df_f.columns else [])
        f_team = st.selectbox("\U0001f535 \u30c1\u30fc\u30e0\u3067\u7d5e\u308a\u8fbc\u307f", team_opts)
    with f_col2:
        role_opts = ["All"] + (['Duelist','Initiator','Controller','Sentinel'] if 'role' in df_f.columns else [])
        f_role = st.selectbox("\U0001f3ad \u30ed\u30fc\u30eb\u3067\u7d5e\u308a\u8fbc\u307f", role_opts, format_func=lambda x: rja(x) if x != 'All' else 'All')
    filtered_pool = df_f.copy()
    if f_team != "All" and 'player_team' in filtered_pool.columns:
        filtered_pool = filtered_pool[filtered_pool['player_team'] == f_team]
    if f_role != "All" and 'role' in filtered_pool.columns:
        filtered_pool = filtered_pool[filtered_pool['role'] == f_role]
    pool_players = clean_sorted(filtered_pool['player_name'])
    st.caption(f"\u8a66\u5408\u6570\u30fb\u30ea\u30fc\u30b0\u30d5\u30a3\u30eb\u30bf\u30fc\u5f8c\u306e\u8a72\u5f53\u9078\u624b: {len(pool_players)}\u540d")
    selected_players = st.multiselect("比較する選手を選択（最大5名）", pool_players, max_selections=5)

    if not selected_players:
        st.markdown("""<div style="background:#1a1d26;border-radius:10px;padding:30px;text-align:center;color:#888;">
        <h3>比較したい選手を選んでください</h3>
        <p>チーム・ロールで絞り込んでから選ぶと便利です</p></div>""", unsafe_allow_html=True)
        st.stop()


    st.markdown("<h3 style='color:white'>総合スコアカード</h3>", unsafe_allow_html=True)
    stat_cols_ui = st.columns(len(selected_players))
    player_radar_data = {}
    # 6-axis radar: KAST, Rating, RIV, ACS, FK/FD, HS%
    radar_labels = ['Rating', 'RIV', 'KAST', 'ACS', 'FK/FD', 'HS%']  # radar order fixed
    # note: bar comparison uses separate stat list below

    for i, player in enumerate(selected_players):
        p_df = df_f[df_f['player_name'] == player]
        leagues = ', '.join(p_df['league'].replace('','－').unique()[:3])

        rtng  = p_df['rating'].mean()        if 'rating'       in p_df.columns else 0
        riv   = p_df['RIV'].mean()           if 'RIV'          in p_df.columns else None
        acs   = p_df['acs'].mean()           if 'acs'          in p_df.columns else 0
        adr   = p_df['adr'].mean()           if 'adr'          in p_df.columns else 0
        kast  = p_df['kast'].mean()          if 'kast'         in p_df.columns else 0
        hs    = p_df['hs_pct'].mean()        if 'hs_pct'       in p_df.columns else 0
        fkfd  = p_df['fkfd_ratio'].mean()    if 'fkfd_ratio'   in p_df.columns else 0
        games = count_matches(p_df)
        cons  = consistency_score(p_df['rating'].dropna().tolist() if 'rating' in p_df.columns else [])

        # team
        team_str = ''
        if 'player_team' in p_df.columns:
            tm = p_df['player_team'].dropna()
            tm = tm[tm.astype(str).str.strip() != '']
            if len(tm) > 0:
                team_str = tm.mode()[0]

        # roles: all used roles with counts
        if 'role' in p_df.columns:
            role_counts = p_df['role'].value_counts()
            role_str = ' / '.join([f"{rja(r)}({c})" for r, c in role_counts.items() if r not in ('','nan')])
        else:
            role_str = ''

        # agents: all agents with usage counts from agents column
        agent_lines = ''
        if 'agents' in p_df.columns:
            from collections import Counter
            all_first_agents = []
            for a in p_df['agents'].dropna():
                first = str(a).split('|')[0].strip()
                if first and first not in ('', 'nan'):
                    all_first_agents.append(first)
            agent_counts = Counter(all_first_agents).most_common()
            agent_chips = ''.join(
                f"<span style='display:inline-block;background:#1e2d45;border:1px solid #2d3d55;"
                f"border-radius:6px;padding:3px 8px;margin:2px 3px 2px 0;font-size:11px;color:white;white-space:nowrap'>"
                f"<b>{aja(ag)}</b><span style='color:#8899aa;margin-left:4px'>{cnt}G</span></span>"
                for ag, cnt in agent_counts
            )
            agent_lines = f"<div style='display:flex;flex-wrap:wrap;margin:2px 0 4px 0'>{agent_chips}</div>"

        # 各指標のリーグ内順位を計算
        def rank_in_league(col, val):
            if col not in df_f.columns or val is None or (isinstance(val, float) and np.isnan(val)):
                return '-'
            ranks = df_f.groupby('player_name')[col].mean().rank(ascending=False, method='min')
            r = ranks.get(player, None)
            return f"#{int(r)}" if r is not None else '-'

        with stat_cols_ui[i]:
            riv_str   = f"{riv:.2f}"  if riv is not None else '-'
            riv_rank  = rank_in_league('RIV', riv)
            rtng_rank = rank_in_league('rating', rtng)
            acs_rank  = rank_in_league('acs', acs)
            kast_rank = rank_in_league('kast', kast)
            fkfd_rank = rank_in_league('fkfd_ratio', fkfd)
            hs_rank   = rank_in_league('hs_pct', hs)
            cons_rank = rank_in_league('consistency_score', cons) if 'consistency_score' in df_f.columns else '-'
            st.markdown(f"""
            <div class="player-card">
                <h3 style="color:white;margin:0 0 2px 0">{player}</h3>
                <div style="color:#e63946;font-size:13px;font-weight:600;margin-bottom:2px">{team_str}</div>
                <div style="color:#aaa;font-size:11px;margin-bottom:2px">{leagues}</div>
                <div style="color:#ccc;font-size:12px;margin-bottom:6px">{role_str}</div>
                <hr style="border-color:#2d3142;margin:6px 0">
                <p style="color:white;margin:2px 0;font-size:12px;text-transform:uppercase;letter-spacing:1px">使用エージェント</p>
                {agent_lines}
                <hr style="border-color:#2d3142;margin:6px 0">
                <p style="color:#8899aa;margin:3px 0;font-size:12px">試合数: <b style="color:white">{games}</b></p>
                <p style="color:#8899aa;margin:3px 0;font-size:12px">Rating: <b style="color:white">{rtng:.2f}</b> <span style='color:#aaa;font-size:11px'>{rtng_rank}</span></p>
                <p style="color:#8899aa;margin:3px 0;font-size:12px">RIV: <b style="color:white">{riv_str}</b> <span style='color:#aaa;font-size:11px'>{riv_rank}</span></p>
                <p style="color:#8899aa;margin:3px 0;font-size:12px">KAST: <b style="color:white">{kast:.0f}%</b> <span style='color:#aaa;font-size:11px'>{kast_rank}</span></p>
                <p style="color:#8899aa;margin:3px 0;font-size:12px">ACS: <b style="color:white">{acs:.0f}</b> <span style='color:#aaa;font-size:11px'>{acs_rank}</span></p>
                <p style="color:#8899aa;margin:3px 0;font-size:12px">HS%: <b style="color:white">{hs:.1f}%</b> <span style='color:#aaa;font-size:11px'>{hs_rank}</span></p>
                <p style="color:#8899aa;margin:3px 0;font-size:12px">FK/FD: <b style="color:white">{fkfd:.2f}</b> <span style='color:#aaa;font-size:11px'>{fkfd_rank}</span></p>
                <p style="color:#8899aa;margin:3px 0;font-size:12px">安定性: <b style="color:white">{cons:.0f}/100</b> <span style='color:#aaa;font-size:11px'>{cons_rank}</span></p>
            </div>""", unsafe_allow_html=True)

        # radar: fixed 6 axes, missing -> 50
        radar_vals = [p_df[v].mean() if v in p_df.columns else 50 for v in
                      ['kast_pct','rating_pct','RIV_pct','acs_pct','fkfd_ratio_pct','hs_pct_pct']]
        player_radar_data[player] = radar_vals

    st.markdown("---")
    # radar full-width
    fig_r = radar_chart(player_radar_data, radar_labels, "能力値パーセンタイル比較（リーグ内相対評価）")
    st.plotly_chart(fig_r, use_container_width=True)

    # bar comparison below
    avail_stats = [c for c in ['rating','RIV','kast','acs','adr','hs_pct','fkfd_ratio','first_kills'] if c in df_f.columns]
    cmp_stat = st.selectbox("比較指標", avail_stats, format_func=slabel)
    bar_data = [{'選手': p, cmp_stat: df_f[df_f['player_name']==p][cmp_stat].mean()} for p in selected_players]
    bar_df = pd.DataFrame(bar_data).sort_values(cmp_stat, ascending=False)
    fig_bar = px.bar(bar_df, x='選手', y=cmp_stat, color='選手',
                     color_discrete_sequence=COLORS, title=f"{slabel(cmp_stat)} 比較",
                     labels={cmp_stat: slabel(cmp_stat)})
    fig_bar.update_layout(**CHART_LAYOUT, showlegend=False)
    st.plotly_chart(fig_bar, use_container_width=True)

    # リーグ別比較（複数リーグ時のみ）
    if df_f['league'].nunique() > 1 and len(selected_players) == 1:
        st.markdown("---")
        st.markdown("### リーグ別パフォーマンス")
        p = selected_players[0]
        lg_df = df[df['player_name'] == p].groupby('league')[['rating','acs','adr','kast','hs_pct']].mean().reset_index()
        lg_melted = lg_df.melt(id_vars='league')
        lg_melted['variable'] = lg_melted['variable'].apply(slabel)
        fig_lg = px.bar(lg_melted, x='league', y='value', color='variable',
                        barmode='group', title=f"{p} のリーグ別平均スタッツ",
                        color_discrete_sequence=COLORS,
                        labels={'variable': '指標', 'value': '値', 'league': 'リーグ'})
        fig_lg.update_layout(**CHART_LAYOUT)
        st.plotly_chart(fig_lg, use_container_width=True)

    # ── ロール分析タブ ──
    st.markdown("---")
    st.markdown("<h3 style='color:white'>ロール分析</h3>", unsafe_allow_html=True)
    if 'role' in df_f.columns and 'agents' in df_f.columns:
        role_tab_players = [p for p in selected_players]
        for player in role_tab_players:
            p_df_r = df_f[df_f['player_name'] == player]
            st.markdown(f"**{player}**")
            col_role1, col_role2 = st.columns(2)

            # エージェント出場数
            with col_role1:
                ag_rows = []
                for _, row in p_df_r.iterrows():
                    for ag in str(row.get('agents','')).split('|'):
                        ag = ag.strip()
                        if ag and ag not in ('','nan'):
                            role_name = AGENT_ROLES.get(ag, 'Unknown')
                            ag_rows.append({'agent': ag, 'role': role_name,
                                            'rating': row.get('rating', np.nan),
                                            'acs': row.get('acs', np.nan)})
                if ag_rows:
                    ag_df_r = pd.DataFrame(ag_rows)
                    ag_cnt = ag_df_r.groupby(['agent','role']).agg(
                        出場数=('agent','count'),
                        Rating=('rating','mean')
                    ).reset_index().sort_values('出場数', ascending=False)
                    # ロール色で塗り
                    role_color_list = [ROLE_COLORS.get(r, '#888') for r in ag_cnt['role']]
                    fig_ag_r = go.Figure(go.Bar(
                        x=ag_cnt['agent'].apply(aja), y=ag_cnt['出場数'],
                        marker_color=role_color_list,
                        text=ag_cnt['role'].apply(rja), textposition='outside',
                        textfont=dict(color='white')
                    ))
                    fig_ag_r.update_layout(
                        **CHART_LAYOUT,
                        title=dict(text=f"{player} エージェント出場数", font=dict(color='white', size=14))
                    )
                    st.plotly_chart(fig_ag_r, use_container_width=True)

            # ロール別集計
            with col_role2:
                if 'role' in p_df_r.columns:
                    role_stat_cols = [c for c in ['rating','RIV'] if c in p_df_r.columns]
                    if role_stat_cols:
                        role_agg = p_df_r[p_df_r['role'].notna() & (p_df_r['role'] != '')].groupby('role')[role_stat_cols].mean().reset_index()
                        role_agg_melted = role_agg.melt(id_vars='role', value_vars=role_stat_cols)
                        role_agg_melted['variable'] = role_agg_melted['variable'].apply(slabel)
                        role_agg_melted['role'] = role_agg_melted['role'].apply(rja)
                        fig_role = px.bar(
                            role_agg_melted,
                            x='role', y='value', color='variable', barmode='group',
                            title=f"{player} ロール別平均スタッツ",
                            color_discrete_sequence=COLORS,
                            labels={'role': 'ロール', 'value': '値', 'variable': '指標'}
                        )
                        fig_role.update_layout(
                            **CHART_LAYOUT,
                            title=dict(text=f"{player} ロール別平均スタッツ (Rating/RIV)", font=dict(color='white', size=14))
                        )
                        st.plotly_chart(fig_role, use_container_width=True)
    else:
        st.info("agentsカラムが必要です")


# ══════════════════════════════════════════════════════════
# 2. 選手個人レポート
# ══════════════════════════════════════════════════════════
elif menu == "👤 選手個人レポート":
    st.markdown('<div class="section-title">選手個人詳細レポート</div>', unsafe_allow_html=True)

    # ── チーム / ロールフィルターで候補を絞り込む ──
    pf_col1, pf_col2 = st.columns(2)
    with pf_col1:
        pr_teams = ["All"] + (clean_sorted(df_f['player_team']) if 'player_team' in df_f.columns else [])
        pr_team = st.selectbox("チームで絞り込み", pr_teams, key='pr_team')
    with pf_col2:
        pr_roles = ["All"] + (['Duelist','Initiator','Controller','Sentinel'] if 'role' in df_f.columns else [])
        pr_role = st.selectbox("ロールで絞り込み", pr_roles, key='pr_role', format_func=lambda x: rja(x) if x != 'All' else 'All')

    pr_pool = df_f.copy()
    if pr_team != "All" and 'player_team' in pr_pool.columns:
        pr_pool = pr_pool[pr_pool['player_team'] == pr_team]
    if pr_role != "All" and 'role' in pr_pool.columns:
        pr_pool = pr_pool[pr_pool['role'] == pr_role]
    pr_players = clean_sorted(pr_pool['player_name'])

    st.caption(f"該当選手: {len(pr_players)}名")

    player = st.selectbox("選手", pr_players if pr_players else clean_sorted(df_f['player_name']))

    p_df = df_f[df_f['player_name'] == player]

    if p_df.empty:
        st.warning("データがありません"); st.stop()

    # KPI
    kpi_defs = [
        ("Rating",   'rating',      "{:.2f}"),
        ("RIV",      'RIV',         "{:.2f}"),
        ("KAST",     'kast',        "{:.0f}"),
        ("ACS",      'acs',         "{:.0f}"),
        ("ADR",      'adr',         "{:.0f}"),
        ("HS%",      'hs_pct',      "{:.1f}"),
        ("FK/FD",    'fkfd_ratio',  "{:.2f}"),
    ]
    avail_kpi = [(l,k,f) for l,k,f in kpi_defs if k in p_df.columns]
    # KPI ブロック: HTMLスタット形式
    kpi_html = '<div style="display:flex;gap:12px;flex-wrap:wrap;margin-bottom:16px">'
    for label, key, fmt in avail_kpi:
        val = fmt.format(p_df[key].mean())
        kpi_html += f"""
        <div style="background:linear-gradient(135deg,#111827,#1a2235);border:1px solid #1e2d45;
                    border-top:2px solid #1e2d45;border-radius:10px;padding:14px 20px;min-width:90px;flex:1">
            <div style="color:#8899aa;font-size:10px;text-transform:uppercase;letter-spacing:1.2px;margin-bottom:4px">{label}</div>
            <div style="color:white;font-size:1.6rem;font-weight:700;letter-spacing:-0.5px">{val}</div>
        </div>"""
    kpi_html += '</div>'
    st.markdown(kpi_html, unsafe_allow_html=True)

    st.markdown("---")
    # 6-axis radar full-width (all 6 axes always shown; missing = 50)
    RADAR_AXES = [
        ('KAST',  'kast_pct'),
        ('Rating','rating_pct'),
        ('RIV',   'RIV_pct'),
        ('ACS',   'acs_pct'),
        ('FK/FD', 'fkfd_ratio_pct'),
        ('HS%',   'hs_pct_pct'),
    ]
    radar_vals_p = [p_df[v].mean() if v in p_df.columns else 50 for _, v in RADAR_AXES]
    fig_rp = radar_chart(
        {player: radar_vals_p},
        [k for k,_ in RADAR_AXES],
        f"{player} 能力値（パーセンタイル）"
    )
    st.plotly_chart(fig_rp, use_container_width=True)

    # ── ロール & エージェント分析 ──
    st.markdown("---")
    st.markdown("<h3 style='color:white'>ロール & エージェントプール</h3>", unsafe_allow_html=True)
    if 'agents' in p_df.columns:
        ag_rows = []
        for _, row in p_df.iterrows():
            for ag in str(row.get('agents','')).split('|'):
                ag = ag.strip()
                if ag and ag not in ('','nan'):
                    ag_rows.append({
                        'agent': ag,
                        'role': AGENT_ROLES.get(ag, 'Unknown'),
                        'rating': row.get('rating', np.nan),
                        'acs': row.get('acs', np.nan),
                        'hs_pct': row.get('hs_pct', np.nan),
                    })
        if ag_rows:
            ag_df = pd.DataFrame(ag_rows)
            agg_spec2 = {'出場数': ('agent','count')}
            for c in ['rating','acs','hs_pct']:
                if c in ag_df.columns: agg_spec2[c] = (c,'mean')
            ag_summary = ag_df.groupby(['agent','role']).agg(**agg_spec2).reset_index().sort_values('出場数', ascending=False)

            col_a1, col_a2 = st.columns(2)
            with col_a1:
                role_colors_list = [ROLE_COLORS.get(r,'#888') for r in ag_summary['role']]
                fig_ag = go.Figure(go.Bar(
                    x=ag_summary['agent'].apply(aja), y=ag_summary['出場数'],
                    marker_color=role_colors_list,

                ))
                fig_ag.update_layout(
                    **CHART_LAYOUT,
                    title=dict(text="エージェント出場数", font=dict(color='white', size=14))
                )
                st.plotly_chart(fig_ag, use_container_width=True)

            with col_a2:
                # ロール別出場割合
                role_pie = ag_df.groupby('role').size().reset_index(name='出場数')
                role_pie['role_ja'] = role_pie['role'].apply(rja)
                fig_pie = px.pie(role_pie, names='role_ja', values='出場数',
                                 color='role', color_discrete_map=ROLE_COLORS,
                                 title="ロール別割合")
                fig_pie.update_layout(
                    paper_bgcolor='#0e1117',
                    title=dict(text="ロール別割合", font=dict(color='white', size=14)),
                    font=dict(color='white'),
                    legend=dict(bgcolor='#1a1d26', font=dict(color='white'))
                )
                st.plotly_chart(fig_pie, use_container_width=True)

            # エージェント別スタッツテーブル (HTML)
            ag_cols = [
                ('agent',   'AGENT',   'player', '{}'),  # aja() applied in html_table
                ('role',    'ROLE',    '',       '{}'),  # role_td() applied in html_table
                ('出場数', '試合数',    'num',    '{:.0f}'),
                ('rating',  'Rating',  'num',    '{:.2f}'),
                ('RIV',     'RIV',     'num',    '{:.2f}'),
                ('acs',     'ACS',     'num',    '{:.0f}'),
                ('hs_pct',  'HS%',     'num',    '{:.1f}'),
            ]
            ag_cols = [(k,l,c,f) for k,l,c,f in ag_cols if k in ag_summary.columns]
            ag_rows = ag_summary.to_dict('records')
            ths_ag = ''.join(f'<th>{l}</th>' for _,l,_,_ in ag_cols)
            trs_ag = ''
            for row in ag_rows:
                tds = ''
                for key, _, css, fmt_str in ag_cols:
                    val = row.get(key, '')
                    if key == 'role':
                        tds += role_td(str(val))
                    elif key == 'agent':
                        tds += f'<td class="player">{aja(str(val))}</td>'
                    else:
                        try:
                            disp = fmt_str.format(val) if fmt_str and val != '' and not (isinstance(val, float) and np.isnan(val)) else '-'
                        except Exception:
                            disp = str(val)
                        tds += f'<td class="{css}">{disp}</td>'
                trs_ag += f'<tr>{tds}</tr>'
            st.markdown(
                f'<div style="overflow-x:auto"><table class="stat-table"><thead><tr>{ths_ag}</tr></thead><tbody>{trs_ag}</tbody></table></div>',
                unsafe_allow_html=True
            )
    else:
        st.info("agentsカラムが必要です")

    # ── 安定性分析 ──
    st.markdown("---")
    st.markdown("<h3 style='color:white'>パフォーマンス安定性</h3>", unsafe_allow_html=True)
    stability_metrics = [c for c in ['rating','RIV','acs','adr','kast','hs_pct','fkfd_ratio'] if c in p_df.columns]
    if stability_metrics and len(p_df) >= 3:
        stab_tabs = st.tabs([slabel(c) for c in stability_metrics])
        for stab_tab, sm in zip(stab_tabs, stability_metrics):
            with stab_tab:
                cons_s = consistency_score(p_df[sm].dropna().tolist())
                avg_s  = p_df[sm].mean()
                if sm in ('RIV','rating','fkfd_ratio'):
                    avg_label = f"平均: {avg_s:.2f}"
                elif sm == 'hs_pct':
                    avg_label = f"平均: {avg_s:.1f}"
                else:
                    avg_label = f"平均: {avg_s:.0f}"
                fig_d = go.Figure()
                fig_d.add_trace(go.Histogram(
                    x=p_df[sm].dropna(), nbinsx=20,
                    marker_color='#e63946', opacity=0.8, name=sm
                ))
                fig_d.add_vline(
                    x=avg_s, line_color='white', line_dash='dash',
                    annotation_text=avg_label,
                    annotation_font_color='white'
                )
                fig_d.update_layout(
                    **CHART_LAYOUT,
                    title=dict(text=f"{slabel(sm)} 分布（安定性: {cons_s:.0f}/100）", font=dict(color='white', size=14))
                )
                st.plotly_chart(fig_d, use_container_width=True)


# ══════════════════════════════════════════════════════════
# 3. マップ別分析
# ══════════════════════════════════════════════════════════
elif menu == "🗺️ マップ別分析":
    st.markdown('<div class="section-title">マップ別パフォーマンス分析</div>', unsafe_allow_html=True)

    if 'map_name' not in df_f.columns:
        st.warning("map_nameカラムが見つかりません"); st.stop()

    tab_ov, tab_player = st.tabs(["全体マップ統計", "選手別得意・苦手マップ"])

    with tab_ov:
        # 試合数は game_id または match_id でカウント（行数でない）
        id_col = 'game_id' if 'game_id' in df_f.columns else ('match_id' if 'match_id' in df_f.columns else None)
        map_base = df_f[df_f['map_name'] != '']

        agg_spec = {}
        if id_col:
            # マップごとのユニーク試合数
            map_game_cnt = map_base.groupby('map_name')[id_col].nunique().rename('試合数')
        for c in ['rating','RIV','kast','acs','adr','hs_pct']:
            if c in map_base.columns:
                agg_spec[c] = (c, 'mean')
        map_sum = map_base.groupby('map_name').agg(**agg_spec).reset_index()
        if id_col:
            map_sum = map_sum.merge(map_game_cnt, on='map_name')
        else:
            map_sum['試合数'] = map_base.groupby('map_name').size().values

        # 列順: 試合数, RIV, rating, kast, acs, adr, hs_pct
        ordered_cols = ['試合数'] + [c for c in ['rating','RIV','kast','acs','adr','hs_pct'] if c in map_sum.columns]
        map_sum = map_sum[['map_name'] + ordered_cols].sort_values('試合数', ascending=False)

        fmt = {'試合数': '{:.0f}'}
        for c in ['rating','RIV','kast','acs','adr','hs_pct']:
            if c in map_sum.columns:
                fmt[c] = '{:.2f}' if c in ('RIV','rating') else ('{:.1f}' if c == 'hs_pct' else '{:.0f}')
        # HTMLテーブル
        map_rows = map_sum.to_dict('records')
        map_disp_cols = [('map_name','MAP','player','{}'),('試合数','GP','num','{:.0f}')] + \
            [(c, slabel(c), 'num-hi' if c=='RIV' else 'num', '{:.2f}' if c in ('RIV','rating') else ('{:.1f}' if c=='hs_pct' else '{:.0f}'))
             for c in ['rating','RIV','kast','acs','adr','hs_pct'] if c in map_sum.columns]
        st.markdown(html_table(map_rows, map_disp_cols), unsafe_allow_html=True)

        # tab per metric
        map_chart_metrics = [c for c in ['rating','kast','acs','adr','hs_pct','RIV'] if c in map_sum.columns]
        if map_chart_metrics:
            map_tabs = st.tabs([slabel(c) for c in map_chart_metrics])
            for tab_m, metric in zip(map_tabs, map_chart_metrics):
                with tab_m:
                    fig_mt = px.bar(
                        map_sum.sort_values(metric, ascending=False),
                        x='map_name', y=metric, color=metric,
                        color_continuous_scale='RdYlGn',
                        text='試合数',
                        title=f"マップ別 {slabel(metric)}",
                        labels={metric: slabel(metric), 'map_name': 'MAP', 'color': slabel(metric)}
                    )
                    fig_mt.update_layout(**CHART_LAYOUT)
                    st.plotly_chart(fig_mt, use_container_width=True)

    with tab_player:
        # チーム / ロールフィルター
        mp_f1, mp_f2 = st.columns(2)
        with mp_f1:
            mp_team_opts = ["All"] + (clean_sorted(df_f['player_team']) if 'player_team' in df_f.columns else [])
            mp_team = st.selectbox("チーム", mp_team_opts, key='mp_team')
        with mp_f2:
            mp_role_opts = ["All"] + (['Duelist','Initiator','Controller','Sentinel'] if 'role' in df_f.columns else [])
            mp_role = st.selectbox("ロール", mp_role_opts, key='mp_role', format_func=lambda x: rja(x) if x != 'All' else 'All')
        mp_pool = df_f.copy()
        if mp_team != "All" and 'player_team' in mp_pool.columns:
            mp_pool = mp_pool[mp_pool['player_team'] == mp_team]
        if mp_role != "All" and 'role' in mp_pool.columns:
            mp_pool = mp_pool[mp_pool['role'] == mp_role]
        mp_players = clean_sorted(mp_pool['player_name'])
        st.caption(f"該当選手: {len(mp_players)}名")

        sel_p_map = st.selectbox("選手", mp_players if mp_players else clean_sorted(df_f['player_name']), key='sel_p_map')
        p_map_df = df_f[(df_f['player_name'] == sel_p_map) & (df_f['map_name'] != '')]

        id_col_p = 'game_id' if 'game_id' in p_map_df.columns else ('match_id' if 'match_id' in p_map_df.columns else None)
        min_games = 2
        game_cnt = p_map_df[id_col_p].nunique() if id_col_p else len(p_map_df)
        if game_cnt < min_games:
            st.info(f"データが少ないため表示できません（{min_games}マップ以上必要）")
        else:
            map_agg_spec = {}
            for c in ['RIV','rating','kast','acs','adr','hs_pct']:
                if c in p_map_df.columns:
                    map_agg_spec[c] = (c, 'mean')
            p_map_stats = p_map_df.groupby('map_name').agg(**map_agg_spec).reset_index()
            if id_col_p:
                map_gcnt = p_map_df.groupby('map_name')[id_col_p].nunique().rename('試合数')
                p_map_stats = p_map_stats.merge(map_gcnt, on='map_name')
            else:
                p_map_stats['試合数'] = p_map_df.groupby('map_name').size().values

            # 複合スコア（各指標のパーセンタイル平均）で得意・苦手を判定
            score_cols = [c for c in ['rating','RIV','kast','acs','adr'] if c in p_map_stats.columns]
            if score_cols:
                for sc in score_cols:
                    p_map_stats[f'_{sc}_pct'] = p_map_stats[sc].rank(pct=True) * 100
                p_map_stats['_composite'] = p_map_stats[[f'_{sc}_pct' for sc in score_cols]].mean(axis=1)
                sort_col = '_composite'
            else:
                sort_col = '試合数'
            p_map_stats = p_map_stats.sort_values(sort_col, ascending=False)

            # 列順: 試合数, RIV, rating, kast, acs, adr, hs_pct
            ord_cols = ['試合数'] + [c for c in ['rating','RIV','kast','acs','adr','hs_pct'] if c in p_map_stats.columns]
            pmap_rows = p_map_stats[['map_name'] + ord_cols].to_dict('records')
            pmap_disp = [('map_name','MAP','player','{}'),('試合数','GP','num','{:.0f}')] + \
                [(c, slabel(c), 'num-hi' if c=='RIV' else 'num', '{:.2f}' if c in ('RIV','rating') else ('{:.1f}' if c=='hs_pct' else '{:.0f}'))
                 for c in ['rating','RIV','kast','acs','adr','hs_pct'] if c in p_map_stats.columns]
            st.markdown(html_table(pmap_rows, pmap_disp), unsafe_allow_html=True)

            if len(p_map_stats) >= 2:
                best = p_map_stats.iloc[0]
                worst = p_map_stats.iloc[-1]
                # 表示用に複数指標の平均値を使う
                def map_summary_str(row):
                    parts = [f"{c}: {row[c]:.2f}" if c in ('RIV','rating') else f"{c}: {row[c]:.0f}" for c in score_cols if c in row]
                    return ' / '.join(parts[:3])
                c1, c2 = st.columns(2)
                c1.success(f"✅ 得意: **{best['map_name']}**  {map_summary_str(best)}")
                c2.error(f"⚠️ 苦手: **{worst['map_name']}**  {map_summary_str(worst)}")

            # tabs per metric
            player_map_metrics = [c for c in ['rating','kast','acs','adr','hs_pct','RIV'] if c in p_map_stats.columns]
            if player_map_metrics:
                ptabs = st.tabs([slabel(c) for c in player_map_metrics])
                for ptab, metric in zip(ptabs, player_map_metrics):
                    with ptab:
                        fig_pt = px.bar(
                            p_map_stats.sort_values(metric, ascending=False),
                            x='map_name', y=metric, color=metric,
                            color_continuous_scale='RdYlGn', text='試合数',
                            title=f"{sel_p_map} マップ別 {slabel(metric)}",
                            labels={metric: slabel(metric), 'map_name': 'MAP', 'color': slabel(metric)}
                        )
                        fig_pt.update_layout(**CHART_LAYOUT)
                        st.plotly_chart(fig_pt, use_container_width=True)


# ══════════════════════════════════════════════════════════
# 4. クラッチ & マルチキル
# ══════════════════════════════════════════════════════════
elif menu == "💥 クラッチ & マルチキル":
    st.markdown('<div class="section-title">💥 クラッチ & マルチキル分析</div>', unsafe_allow_html=True)

    tab_cl, tab_mk, tab_hs = st.tabs(["クラッチ分析", "マルチキル", "ヘッドショット率"])

    # ─ クラッチ ─
    with tab_cl:
        cl_cols = [c for c in ['clutch_1v1','clutch_1v2','clutch_1v3','clutch_1v4','clutch_1v5'] if c in df_f.columns]
        if not cl_cols:
            st.info("clutchデータがありません")
        else:
            # 選手別クラッチ合計ランキング
            cl_agg = df_f.groupby('player_name')[cl_cols + (['clutch_total'] if 'clutch_total' in df_f.columns else [])].sum().reset_index()
            if 'clutch_total' in cl_agg.columns:
                cl_agg = cl_agg.sort_values('clutch_total', ascending=False)

            st.markdown("#### 🏆 クラッチ成功数ランキング TOP20")
            top_cl = cl_agg.head(20)
            fig_cl_rank = px.bar(top_cl, x='player_name', y='clutch_total' if 'clutch_total' in top_cl.columns else cl_cols[0],
                                 color='clutch_total' if 'clutch_total' in top_cl.columns else cl_cols[0],
                                 color_continuous_scale='Reds', title="累計クラッチ成功数")
            fig_cl_rank.update_layout(**CHART_LAYOUT, xaxis_tickangle=-45)
            st.plotly_chart(fig_cl_rank, use_container_width=True)

            st.markdown("#### 📊 クラッチ種別内訳（選手比較）")
            sel_cl_players = st.multiselect("選手を選択", clean_sorted(df_f['player_name']), max_selections=5, key='cl_players')
            if sel_cl_players:
                cl_detail = []
                for p in sel_cl_players:
                    p_cl = df_f[df_f['player_name']==p][cl_cols].sum()
                    for col in cl_cols:
                        cl_detail.append({'選手':p, '種別':col.replace('clutch_',''), '成功数':p_cl[col]})
                cl_det_df = pd.DataFrame(cl_detail)
                fig_cl_det = px.bar(cl_det_df, x='種別', y='成功数', color='選手', barmode='group',
                                    color_discrete_sequence=COLORS, title="クラッチ種別比較")
                fig_cl_det.update_layout(**CHART_LAYOUT)
                st.plotly_chart(fig_cl_det, use_container_width=True)

            # 生データ
            st.dataframe(cl_agg.head(30).style.format({c:'{:.0f}' for c in cl_cols + (['clutch_total'] if 'clutch_total' in cl_agg.columns else [])}),
                         use_container_width=True, hide_index=True)

    # ─ マルチキル ─
    with tab_mk:
        mk_cols = [c for c in ['k2','k3','k4','k5'] if c in df_f.columns]
        if not mk_cols:
            st.info("k2/k3/k4/k5データがありません")
        else:
            mk_agg = df_f.groupby('player_name')[mk_cols].sum().reset_index()
            if 'k4' in mk_agg.columns:
                mk_agg = mk_agg.sort_values('k4', ascending=False)

            st.markdown("#### 🏆 マルチキルランキング TOP20")
            fig_mk = px.bar(mk_agg.head(20).melt(id_vars='player_name', value_vars=mk_cols),
                            x='player_name', y='value', color='variable', barmode='stack',
                            color_discrete_sequence=COLORS, title="マルチキル積み上げ（TOP20）",
                            labels={'value':'回数','variable':'種別'})
            fig_mk.update_layout(**CHART_LAYOUT, xaxis_tickangle=-45)
            st.plotly_chart(fig_mk, use_container_width=True)

            sel_mk_players = st.multiselect("詳細比較", clean_sorted(df_f['player_name']), max_selections=5, key='mk_players')
            if sel_mk_players:
                mk_det = []
                for p in sel_mk_players:
                    p_mk = df_f[df_f['player_name']==p][mk_cols].sum()
                    for col in mk_cols:
                        mk_det.append({'選手':p, '種別':col.upper(), '回数':p_mk[col]})
                fig_mk_det = px.bar(pd.DataFrame(mk_det), x='種別', y='回数', color='選手', barmode='group',
                                    color_discrete_sequence=COLORS, title="マルチキル種別比較")
                fig_mk_det.update_layout(**CHART_LAYOUT)
                st.plotly_chart(fig_mk_det, use_container_width=True)

    # ─ ヘッドショット率 ─
    with tab_hs:
        if 'hs_pct' not in df_f.columns:
            st.info("hs_pctデータがありません")
        else:
            hs_agg = df_f.groupby('player_name')['hs_pct'].agg(['mean','std','count']).reset_index()
            hs_agg.columns = ['player_name','HS%平均','HS%標準偏差','試合数']
            hs_agg = hs_agg[hs_agg['試合数'] >= 3].sort_values('HS%平均', ascending=False)

            st.markdown("#### 🎯 HS%ランキング TOP20（3試合以上）")
            fig_hs = px.bar(hs_agg.head(20), x='player_name', y='HS%平均',
                            error_y='HS%標準偏差', color='HS%平均',
                            color_continuous_scale='RdYlGn', title="平均HS%（エラーバー: 標準偏差）")
            fig_hs.update_layout(**CHART_LAYOUT, xaxis_tickangle=-45)
            st.plotly_chart(fig_hs, use_container_width=True)

            # HS% vs Rating 散布図
            st.markdown("#### 📈 HS% vs Rating 相関")
            scatter_df = df_f.groupby('player_name')[['hs_pct','rating','acs']].mean().reset_index().dropna()
            fig_sc = px.scatter(scatter_df, x='hs_pct', y='rating', hover_name='player_name',
                                size='acs', color='acs', color_continuous_scale='RdYlGn',
                                title="HS% vs Rating（バブルサイズ: ACS）",
                                labels={'hs_pct':'HS%','rating':'Rating'})
            fig_sc.update_layout(**CHART_LAYOUT)
            st.plotly_chart(fig_sc, use_container_width=True)


# ══════════════════════════════════════════════════════════
# 5. スタッツ別選手ランキング
# ══════════════════════════════════════════════════════════
elif menu == "📈 スタッツ別選手ランキング":
    st.markdown('<div class="section-title">スタッツ別選手ランキング</div>', unsafe_allow_html=True)

    rank_avail = [c for c in ['rating','RIV','kast','acs','adr','hs_pct','fkfd_ratio','first_kills','clutch_total','consistency_score'] if c in df_f.columns]

    # リーグ / ロール フィルター
    rk_col1, rk_col2 = st.columns(2)
    with rk_col1:
        rk_league = st.selectbox("リーグ", ["All"] + clean_sorted(df_f['league']))
    with rk_col2:
        rk_role = st.selectbox("ロール", ["All"] + (['Duelist','Initiator','Controller','Sentinel'] if 'role' in df_f.columns else []), format_func=lambda x: rja(x) if x != 'All' else 'All')
    rk_df_base = df_f.copy()
    if rk_league != "All":
        rk_df_base = rk_df_base[rk_df_base['league'] == rk_league]
    if rk_role != "All" and 'role' in rk_df_base.columns:
        rk_df_base = rk_df_base[rk_df_base['role'] == rk_role]

    # 試合数足切り
    id_col_rk = 'game_id' if 'game_id' in rk_df_base.columns else ('match_id' if 'match_id' in rk_df_base.columns else None)
    if id_col_rk:
        max_gp = int(rk_df_base.groupby('player_name')[id_col_rk].nunique().max())
    else:
        max_gp = int(rk_df_base.groupby('player_name').size().max())
    min_gp = st.slider(
        "最小試合数",
        min_value=1, max_value=max(max_gp, 1),
        value=min(3, max_gp),
        step=1,
        help="指定試合数未満の選手を隠す"
    )

    # 全指標タブ
    rank_tabs = st.tabs([STAT_LABELS.get(c, c) for c in rank_avail])
    # 累計系指標は sum、平均系は mean
    SUM_STATS = {'clutch_total','clutch_1v1','clutch_1v2','clutch_1v3','clutch_1v4','clutch_1v5',
                 'first_kills','kills','deaths','assists','k2','k3','k4','k5'}

    for rtab, rank_stat in zip(rank_tabs, rank_avail):
        with rtab:
            agg_func = 'sum' if rank_stat in SUM_STATS else 'mean'
            rank_df = rk_df_base.groupby('player_name').agg(
                **{rank_stat: (rank_stat, agg_func), '試合数': ('player_name','count')}
            ).reset_index()
            # GP足切り
            rank_df = rank_df[rank_df['試合数'] >= min_gp]
            if 'role' in rk_df_base.columns:
                role_map = rk_df_base.groupby('player_name')['role'].agg(lambda x: x.mode()[0] if len(x)>0 else '')
                rank_df = rank_df.merge(role_map.rename('role'), on='player_name', how='left')
            if 'player_team' in rk_df_base.columns:
                team_map = rk_df_base.groupby('player_name')['player_team'].agg(lambda x: x.mode()[0] if len(x)>0 else '')
                rank_df = rank_df.merge(team_map.rename('team'), on='player_name', how='left')

            rank_df = rank_df.sort_values(rank_stat, ascending=False).reset_index(drop=True)
            rank_df.insert(0, '#', range(1, len(rank_df)+1))

            fmt_r = '{:.2f}' if rank_stat in ('RIV','rating','fkfd_ratio','consistency_score') else ('{:.1f}' if rank_stat == 'hs_pct' else '{:.0f}')

            rk_col_defs = [
                ('#',         '#',              'rank',   '{}'),
                ('player_name','PLAYER',         'player', '{}'),
                ('team',      'TEAM',            'team',   '{}'),
                ('role',      'ROLE',            '',       '{}'),
                (rank_stat,   STAT_LABELS.get(rank_stat, rank_stat), 'num-hi', fmt_r),
                ('試合数',     'GP',             'num',    '{:.0f}'),
            ]
            rk_col_defs = [(k,l,c,f) for k,l,c,f in rk_col_defs if k in rank_df.columns]

            def render_rk_table(rows):
                ths = ''.join(f'<th>{l}</th>' for _,l,_,_ in rk_col_defs)
                trs = ''
                for row in rows:
                    tds = ''
                    for key, _, css, fmt_str in rk_col_defs:
                        val = row.get(key, '')
                        if key == 'role':
                            tds += role_td(str(val))
                        else:
                            try:
                                disp = fmt_str.format(val) if fmt_str and val != '' and not (isinstance(val, float) and np.isnan(val)) else str(val)
                            except Exception:
                                disp = str(val)
                            tds += f'<td class="{css}">{disp}</td>'
                    trs += f'<tr>{tds}</tr>'
                return f'<div style="overflow-x:auto"><table class="stat-table"><thead><tr>{ths}</tr></thead><tbody>{trs}</tbody></table></div>'

            # TOP10表示
            top10 = rank_df.head(10).to_dict('records')
            col_rk1, col_rk2 = st.columns([1,1])
            with col_rk1:
                st.markdown(render_rk_table(top10), unsafe_allow_html=True)
            with col_rk2:
                fig_rk = px.bar(
                    rank_df.head(10), x='player_name', y=rank_stat,
                    color=rank_stat, color_continuous_scale='Reds',
                    text='試合数', title=f"{slabel(rank_stat)} TOP 10",
                    labels={rank_stat: slabel(rank_stat), 'player_name': 'PLAYER'}
                )
                fig_rk.update_layout(**CHART_LAYOUT, xaxis_tickangle=-45)
                st.plotly_chart(fig_rk, use_container_width=True)

            # ページタブ（11位以降）
            remaining = rank_df.iloc[10:].to_dict('records')
            if remaining:
                pages = [remaining[i:i+10] for i in range(0, len(remaining), 10)]
                page_labels = [f"{i*10+11} - {min((i+1)*10+10, len(remaining)+10)}" for i in range(len(pages))]
                page_tabs = st.tabs(page_labels)
                for ptab, page_rows in zip(page_tabs, pages):
                    with ptab:
                        st.markdown(render_rk_table(page_rows), unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════
# 6. 試合ライブラリ
# ══════════════════════════════════════════════════════════
elif menu == "🎮 試合ライブラリ":
    st.markdown('<div class="section-title">🎮 試合アーカイブ</div>', unsafe_allow_html=True)

    # ── フィルター ──
    col_f1, col_f2, col_f3 = st.columns(3)
    with col_f1:
        years = sorted([y for y in df_f['year'].dropna().unique()], reverse=True)
        s_year = st.selectbox("年度", years)
    with col_f2:
        leagues_y = clean_sorted(df_f[df_f['year']==s_year]['league'])
        s_league = st.selectbox("リーグ", ["All"] + leagues_y)
    with col_f3:
        y_df = df_f[df_f['year']==s_year].copy()
        if s_league != "All":
            y_df = y_df[y_df['league']==s_league]
        opponents = clean_sorted(y_df['team2_name']) if 'team2_name' in y_df.columns else []
        s_opp = st.selectbox("対戦チーム", ["All"] + opponents)

    if s_opp != "All" and 'team2_name' in y_df.columns:
        y_df = y_df[y_df['team2_name'] == s_opp]

    # ── game_idで一試合一マップを特定 ──
    id_col_lib = 'game_id' if 'game_id' in y_df.columns else ('match_id' if 'match_id' in y_df.columns else None)
    if id_col_lib is None:
        st.warning("match_id または game_id カラムが必要です")
        st.stop()

    label_parts = y_df.copy()
    date_str = label_parts['Date'].dt.strftime('%Y/%m/%d') if 'Date' in label_parts.columns else pd.Series([''] * len(label_parts), index=label_parts.index)
    map_str  = label_parts['map_name']   if 'map_name'   in label_parts.columns else pd.Series([''] * len(label_parts), index=label_parts.index)
    t1_str   = label_parts['team1_name'] if 'team1_name' in label_parts.columns else pd.Series([''] * len(label_parts), index=label_parts.index)
    t2_str   = label_parts['team2_name'] if 'team2_name' in label_parts.columns else pd.Series([''] * len(label_parts), index=label_parts.index)
    label_parts['_label'] = date_str + " [" + map_str + "] " + t1_str + " vs " + t2_str
    label_parts['_gid']   = label_parts[id_col_lib].astype(str)

    gid_label_map = (
        label_parts[['_gid','_label']].drop_duplicates('_gid')
        .set_index('_gid')['_label'].to_dict()
    )
    # 新しい試合順
    sorted_gids = sorted(
        gid_label_map.keys(),
        key=lambda g: label_parts[label_parts['_gid']==g]['Date'].min() if 'Date' in label_parts.columns else g,
        reverse=True
    )
    sorted_labels = [gid_label_map[g] for g in sorted_gids]

    if not sorted_labels:
        st.info("試合データがありません")
        st.stop()

    sel_label = st.selectbox("📌 試合を選択", sorted_labels)
    sel_gid   = sorted_gids[sorted_labels.index(sel_label)]
    match_data = y_df[y_df[id_col_lib].astype(str) == sel_gid].copy()

    # ── 試合ヘッダー (HTMLバナー風) ──
    if not match_data.empty:
        row0 = match_data.iloc[0]
        t1 = row0.get('team1_name', '－')
        t2 = row0.get('team2_name', '－')
        s1 = int(row0['team1_score']) if 'team1_score' in row0 and pd.notna(row0.get('team1_score')) else '－'
        s2 = int(row0['team2_score']) if 'team2_score' in row0 and pd.notna(row0.get('team2_score')) else '－'
        map_n  = row0.get('map_name','－')
        league_n = row0.get('league','－')
        st.markdown(f"""
        <div style="background:linear-gradient(135deg,#111827,#0d1520);border:1px solid #1e2d45;
                    border-radius:12px;padding:20px 24px;margin-bottom:16px">
            <div style="display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:12px">
                <div>
                    <div style="color:#8899aa;font-size:10px;text-transform:uppercase;letter-spacing:1.2px">🗺️ MAP</div>
                    <div style="color:white;font-size:1.3rem;font-weight:700">{map_n}</div>
                    <div style="color:#8899aa;font-size:12px">{league_n}</div>
                </div>
                <div style="text-align:center">
                    <div style="color:#8899aa;font-size:10px;text-transform:uppercase;letter-spacing:1px">SCORE</div>
                    <div style="font-size:2rem;font-weight:900;color:white;letter-spacing:2px">{s1} — {s2}</div>
                    <div style="color:#ccc;font-size:13px">{t1} <span style='color:#8899aa'>vs</span> {t2}</div>
                </div>
                <div style="text-align:right">
                    <div style="color:#8899aa;font-size:10px;text-transform:uppercase;letter-spacing:1px">DATE</div>
                    <div style="color:white;font-size:1rem">{row0['Date'].strftime('%Y/%m/%d') if 'Date' in row0 and pd.notna(row0.get('Date')) else '－'}</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    # ── 全選手スタッツ（チーム分割） ──
    st.markdown("---")
    st.markdown("### 📋 全選手スタッツ")
    disp_candidates = [
        'player_name','role','agents',
        'rating','acs','adr','kast','kills','deaths','assists',
        'first_kills','first_deaths','hs_pct','clutch_total','k2','k3','k4','k5'
    ]
    disp_cols = [c for c in disp_candidates if c in match_data.columns]
    fmt_d = {}
    for k, v in {
        'rating':'{:.2f}','acs':'{:.0f}','adr':'{:.0f}','kast':'{:.0f}',
        'kills':'{:.0f}','deaths':'{:.0f}','assists':'{:.0f}',
        'first_kills':'{:.0f}','first_deaths':'{:.0f}',
        'hs_pct':'{:.1f}','clutch_total':'{:.0f}',
        'k2':'{:.0f}','k3':'{:.0f}','k4':'{:.0f}','k5':'{:.0f}'
    }.items():
        if k in match_data.columns:
            fmt_d[k] = v
    sort_by = 'rating' if 'rating' in match_data.columns else disp_cols[0]

    match_stat_cols = [
        ('player_name', 'PLAYER',  'player', '{}'),
        ('role',        'ROLE',    '',       '{}'),
        ('agents',      'AGENT',   'team',   '{}'),
        ('rating',      'Rating',  'num-hi', '{:.2f}'),
        ('RIV',         'RIV',     'num',    '{:.2f}'),
        ('kast',        'KAST',    'num',    '{:.0f}'),
        ('acs',         'ACS',     'num',    '{:.0f}'),
        ('adr',         'ADR',     'num',    '{:.0f}'),
        ('hs_pct',      'HS%',     'num',    '{:.1f}'),
        ('kills',       'K',       'num',    '{:.0f}'),
        ('deaths',      'D',       'num',    '{:.0f}'),
        ('assists',     'A',       'num',    '{:.0f}'),
        ('first_kills', 'FK',      'num',    '{:.0f}'),
        ('clutch_total','Clutch',  'num',    '{:.0f}'),
    ]
    match_stat_cols = [(k,l,c,f) for k,l,c,f in match_stat_cols if k in match_data.columns]

    if 'player_team' in match_data.columns:
        for team in [t for t in match_data['player_team'].unique() if t]:
            t_df = match_data[match_data['player_team']==team].sort_values(sort_by, ascending=False)
            st.markdown(f"<div class='sub-title'>🔵 {team}</div>", unsafe_allow_html=True)
            rows_m = t_df.to_dict('records')
            ths_m = ''.join(f'<th>{l}</th>' for _,l,_,_ in match_stat_cols)
            trs_m = ''
            for row in rows_m:
                tds = ''
                for key, _, css, fmt_str in match_stat_cols:
                    val = row.get(key,'')
                    if key == 'role':
                        tds += role_td(str(val))
                    elif key == 'agents':
                        ag_short = str(val).split('|')[0].strip() if val else '-'
                        tds += f'<td class="team">{aja(ag_short)}</td>'
                    else:
                        try:
                            disp = fmt_str.format(val) if fmt_str and val != '' and not (isinstance(val, float) and np.isnan(val)) else '-'
                        except Exception:
                            disp = str(val)
                        tds += f'<td class="{css}">{disp}</td>'
                trs_m += f'<tr>{tds}</tr>'
            st.markdown(
                f'<div style="overflow-x:auto"><table class="stat-table"><thead><tr>{ths_m}</tr></thead><tbody>{trs_m}</tbody></table></div>',
                unsafe_allow_html=True
            )
    else:
        rows_m = match_data.sort_values(sort_by, ascending=False).to_dict('records')
        st.markdown(html_table(rows_m, match_stat_cols), unsafe_allow_html=True)

    # ── ラダーチャート比較 ──
    st.markdown("---")
    st.markdown("### 📊 この試合の能力値（リーグ内パーセンタイル）")
    radar_avail = {k:v for k,v in {
        'Rating':'rating_pct','KAST':'kast_pct','ACS':'acs_pct',
        'ADR':'adr_pct','FK':'first_kills_pct','HS%':'hs_pct_pct'
    }.items() if v in match_data.columns}
    if radar_avail:
        players_in_match = [p for p in match_data['player_name'].unique() if p]
        radar_data_match = {p: [match_data[match_data['player_name']==p][v].mean() for v in radar_avail.values()]
                            for p in players_in_match}
        fig_mr = radar_chart(radar_data_match, list(radar_avail.keys()), "試合内パーセンタイル比較")
        st.plotly_chart(fig_mr, use_container_width=True)

    # ── YouTube ──
    st.markdown("---")
    col_yt, col_note = st.columns([3, 1])
    with col_yt:
        yt_url = st.text_input("📺 YouTube URL")
        if yt_url:
            st.video(yt_url)
    with col_note:
        st.markdown("**📝 試合メモ**")
        st.text_area("気になったポイントを記録", height=150)
