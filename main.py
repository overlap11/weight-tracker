import streamlit as st
import pandas as pd
from datetime import datetime, date, timedelta
import plotly.graph_objects as go
import plotly.express as px
from database import WeightDatabase

import sys
import os
import warnings

# Plotlyの警告を無視
warnings.filterwarnings("ignore", message="The behavior of DatetimeProperties.to_pydatetime is deprecated")

# ページ設定
st.set_page_config(
    page_title="体重トラッカー",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# カスタムCSS
st.markdown("""
<style>
.main-header {
    font-size: 2.0rem;
    font-weight: bold;
    color: #1f77b4;
    text-align: center;
    margin-bottom: 2rem;
}

.metric-card {
    background-color: #f0f2f6;
    border: 1px solid #e0e0e0;
    border-radius: 10px;
    padding: 1rem;
    margin: 0.5rem 0;
}

.success-message {
    background-color: #d4edda;
    color: #155724;
    padding: 1rem;
    border-radius: 5px;
    border: 1px solid #c3e6cb;
    margin: 1rem 0;
}

.error-message {
    background-color: #f8d7da;
    color: #721c24;
    padding: 1rem;
    border-radius: 5px;
    border: 1px solid #f5c6cb;
    margin: 1rem 0;
}

.graph-container {
    background-color: #ffffff;
    border: 1px solid #e0e0e0;
    border-radius: 10px;
    padding: 1rem;
    margin: 1rem 0;
}



/* 見出し（subheader）のサイズを小さくする */
.stApp h3 {
    font-size: 1.3rem !important;
    margin-top: 1rem !important;
    margin-bottom: 0.5rem !important;
}

/* データ項目名のヘッダーサイズも調整 */
h3[data-testid="stHeader"] {
    font-size: 1.3rem !important;
}

/* ブロック全体の上側余白を縮める */
section.main > div.block-container{
    padding-top: 1.5rem;
}

/* 見出し直下の余白を縮小 */
.main-header{
    margin-bottom: 0.8rem;
    line-height: 1.2;
}

/* サブヘッダ全般も少し詰める */
h2, .stMarkdown h2{
    margin-top: 0.8rem;
    margin-bottom: 0.4rem;
}

/* メトリックカードのスタイル */
.metric-card{
    background:#f7f9fc;
    border:1px solid #e3e8ef;
    border-radius:8px;
    padding:0.8rem 0.6rem;
    text-align:center;
    box-shadow:0 1px 3px rgba(0,0,0,0.04);
    width: 100%;
    margin-bottom: 0.5rem;
}
/* ラベルと値を太さ＆サイズで差別化 */
.metric-label{
    font-size:0.75rem;
    color:#555;
    margin-bottom:0.2rem;
    font-weight:600;
}
.metric-value{
    font-size:1.3rem;
    font-weight:700;
    color:#1f2937;
}
</style>
""", unsafe_allow_html=True)

# 色設定
COLOR_SCHEME = {
    'primary': '#1f77b4',      # 体重ライン
    'secondary': '#ff7f0e',    # 体脂肪率ライン
    'accent': '#2ca02c',       # 移動平均ライン
    'background': '#ffffff',   # 背景色
    'text': '#333333',         # テキスト色
    'success': '#28a745',      # 成功メッセージ
    'error': '#dc3545',        # エラーメッセージ
    'warning': '#ffc107'       # 警告メッセージ
}

def init_database():
    """データベースの初期化"""
    try:
        db = WeightDatabase()
        return db
    except Exception as e:
        st.error(f"データベース初期化エラー: {str(e)}")
        st.stop()

def validate_weight(weight: float) -> tuple[bool, str]:
    """体重の妥当性チェック"""
    if weight < 10.0 or weight > 300.0:
        return False, "体重は10kg～300kgの範囲で入力してください"
    return True, ""

def validate_body_fat(body_fat: float) -> tuple[bool, str]:
    """体脂肪率の妥当性チェック"""
    if body_fat is not None and (body_fat < 0.0 or body_fat > 100.0):
        return False, "体脂肪率は0%～100%の範囲で入力してください"
    return True, ""

def validate_date(input_date: date) -> tuple[bool, str]:
    """日付の妥当性チェック"""
    # 現在の日付を毎回取得
    today = datetime.now().date()
    if input_date > today:
        return False, "未来の日付は入力できません"
    return True, ""

def get_simple_recommendations(db):
    """推奨値の簡単な算出"""
    try:
        # 過去7日間のデータを取得
        recent_data = db.get_measurements(7)
        if recent_data.empty:
            return {}
        
        # 平均値を推奨値として算出
        recommendations = {
            'weight': round(recent_data['weight'].mean(), 1)
        }
        
        # 体脂肪率の平均も算出（データがある場合）
        if recent_data['body_fat'].notna().any():
            recommendations['body_fat'] = round(recent_data['body_fat'].mean(), 1)
        
        return recommendations
    except Exception:
        return {}

def calculate_moving_average(df: pd.DataFrame, window: int = 7) -> pd.DataFrame:
    """移動平均を計算"""
    df_sorted = df.sort_values('date').copy()
    df_sorted['weight_ma'] = df_sorted['weight'].rolling(window=window, min_periods=1).mean()
    if 'body_fat' in df_sorted.columns:
        df_sorted['body_fat_ma'] = df_sorted['body_fat'].rolling(window=window, min_periods=1).mean()
    return df_sorted

def create_weight_graph(df: pd.DataFrame, period_days: int = None, target_weight: float = None) -> go.Figure:
    """体重グラフの作成"""
    if df.empty:
        # データが空の場合のプレースホルダー
        fig = go.Figure()
        fig.add_annotation(
            text="データがありません<br>左側のフォームから記録を追加してください",
            xref="paper", yref="paper",
            x=0.5, y=0.5, xanchor='center', yanchor='middle',
            showarrow=False,
            font=dict(size=16, color="#666666")
        )
        fig.update_layout(
            title="体重推移グラフ",
            xaxis_title="日付",
            yaxis_title="体重 (kg)",
            height=400
        )
        return fig
    
    # データの前処理
    df_with_ma = calculate_moving_average(df)
    
    # 図の作成
    fig = go.Figure()
    
    # 体重ライン（メイン）
    fig.add_trace(go.Scatter(
        x=df_with_ma['date'],
        y=df_with_ma['weight'],
        mode='lines',
        name='体重',
        line=dict(color=COLOR_SCHEME['primary'], width=2),
        hovertemplate='<b>%{fullData.name}</b><br>' +
                     '日付: %{x}<br>' +
                     '体重: %{y:.1f}kg<br>' +
                     '<extra></extra>'
    ))
    
    # 7日移動平均ライン
    if len(df_with_ma) >= 3:  # 最低3つのデータポイントがある場合のみ
        fig.add_trace(go.Scatter(
            x=df_with_ma['date'],
            y=df_with_ma['weight_ma'],
            mode='lines',
            name='7日移動平均',
            line=dict(color=COLOR_SCHEME['primary'], width=2, dash='dash'),
            hovertemplate='<b>%{fullData.name}</b><br>' +
                         '日付: %{x}<br>' +
                         '移動平均: %{y:.1f}kg<br>' +
                         '<extra></extra>'
        ))
    
    # 体脂肪率ライン（データがある場合）
    has_body_fat = 'body_fat' in df_with_ma.columns and df_with_ma['body_fat'].notna().any()
    if has_body_fat:
        fig.add_trace(go.Scatter(
            x=df_with_ma['date'],
            y=df_with_ma['body_fat'],
            mode='lines',
            name='体脂肪率',
            line=dict(color=COLOR_SCHEME['secondary'], width=2),
            marker=dict(size=6, color=COLOR_SCHEME['secondary']),
            yaxis='y2',
            hovertemplate='<b>%{fullData.name}</b><br>' +
                         '日付: %{x}<br>' +
                         '体脂肪率: %{y:.1f}%<br>' +
                         '<extra></extra>'
        ))
    
    # 目標体重の参照線（設定されている場合）
    if target_weight is not None:
        fig.add_hline(
            y=target_weight,
            line=dict(color='red', width=2),
            annotation_text=f"目標体重: {target_weight:.1f}kg",
            annotation_position="top left",
            annotation=dict(
                bgcolor="rgba(255, 255, 255, 0.8)",
                bordercolor="red",
                borderwidth=1
            )
        )
        

    
    # レイアウト設定
    title = f"体重推移グラフ"
    if period_days:
        title += f" (過去{period_days}日間)"
    
    layout_config = {
        'title': {
            'text': title,
            'font': {'size': 20, 'color': COLOR_SCHEME['text']},
            'x': 0.5
        },
        'xaxis': {
            'title': '日付',
            'type': 'date',
            'tickformat': '%Y-%m-%d',
            'tickangle': -45,
            'gridcolor': '#E0E0E0',
            'showgrid': True
        },
        'yaxis': {
            'title': '体重 (kg)',
            'gridcolor': '#E0E0E0',
            'showgrid': True,
            'zeroline': False
        },
        'plot_bgcolor': COLOR_SCHEME['background'],
        'paper_bgcolor': COLOR_SCHEME['background'],
        'height': 500,
        'hovermode': 'x unified',
        'legend': {
            'orientation': 'h',
            'yanchor': 'bottom',
            'y': 1.02,
            'xanchor': 'right',
            'x': 1
        }
    }
    
    # 体脂肪率がある場合は右側Y軸を追加
    if has_body_fat:
        layout_config['yaxis2'] = {
            'title': '体脂肪率 (%)',
            'overlaying': 'y',
            'side': 'right',
            'gridcolor': '#E0E0E0',
            'showgrid': False,
            'zeroline': False
        }
    
    fig.update_layout(**layout_config)
    
    return fig

def filter_data_by_period(df: pd.DataFrame, period_days: int) -> pd.DataFrame:
    """期間でデータをフィルタリング"""
    if df.empty or period_days is None:
        return df
    
    # 最新の日付から指定日数分を取得
    end_date = df['date'].max()
    start_date = end_date - pd.Timedelta(days=period_days - 1)
    
    return df[df['date'] >= start_date]

def main():
    """メインアプリケーション"""
    
    # データベース初期化
    db = init_database()
    
    # メインヘッダー
    st.markdown('<h1 class="main-header">⚖️ 体重トラッカー</h1>', unsafe_allow_html=True)
    
    # 左サイドバー（入力・設定エリア）
    with st.sidebar:
        # 1. 体重記録セクション
        st.header("📝 体重記録")
        
        # 推奨値の表示
        if st.button("💡 推奨値を取得", key="get_recommendations"):
            try:
                recommendations = get_simple_recommendations(db)
                
                if recommendations:
                    st.session_state.recommended_weight = recommendations.get('weight', 70.0)
                    st.session_state.recommended_body_fat = recommendations.get('body_fat', None)
                    st.success("📈 推奨値を取得しました！")
                else:
                    st.info("📊 推奨値を算出するための履歴データが不足しています")
            except Exception as e:
                st.error(f"推奨値の取得に失敗しました: {str(e)}")
        
        # 入力フォーム
        with st.form("weight_form"):
            # 日付入力
            today = datetime.now().date()
            input_date = st.date_input(
                "日付",
                value=today,
                max_value=today,
                help="測定日を選択してください（未来の日付は選択できません）"
            )
            
            # 体重入力
            default_weight = st.session_state.get('recommended_weight', 70.0)
            weight = st.number_input(
                "体重 (kg)",
                min_value=10.0,
                max_value=300.0,
                value=default_weight,
                step=0.1,
                format="%.1f",
                help="10kg～300kgの範囲で入力してください"
            )
            
            # 体脂肪率入力
            default_body_fat = st.session_state.get('recommended_body_fat', None)
            body_fat = st.number_input(
                "体脂肪率 (%) - 任意",
                min_value=0.0,
                max_value=100.0,
                value=default_body_fat,
                step=0.1,
                format="%.1f",
                help="0%～100%の範囲で入力してください（空欄可）"
            )
            
            # 送信ボタン
            submitted = st.form_submit_button("記録する", type="primary")
        
        # フォーム送信処理
        if submitted:
            # 基本バリデーション
            date_valid, date_error = validate_date(input_date)
            weight_valid, weight_error = validate_weight(weight)
            body_fat_valid, body_fat_error = validate_body_fat(body_fat)
            
            errors = []
            if not date_valid:
                errors.append(date_error)
            if not weight_valid:
                errors.append(weight_error)
            if not body_fat_valid:
                errors.append(body_fat_error)
            
            if errors:
                for error in errors:
                    st.error(error)
            else:
                # データベースに保存
                try:
                    date_str = input_date.strftime("%Y-%m-%d")
                    
                    # 既存データチェック
                    existing_data = db.get_measurement_by_date(date_str)
                    if existing_data:
                        # セッション状態に保存
                        st.session_state.pending_data = {
                            'date': date_str,
                            'weight': weight,
                            'body_fat': body_fat
                        }
                        st.warning(f"⚠️ {date_str}のデータが既に存在します。")
                        st.info(f"既存データ: 体重 {existing_data['weight']:.1f}kg, 体脂肪率 {existing_data['body_fat']:.1f}%" if existing_data['body_fat'] else f"既存データ: 体重 {existing_data['weight']:.1f}kg")
                        
                    else:
                        # 新規データ追加
                        success = db.add_measurement(date_str, weight, body_fat)
                        if success:
                            st.success("✅ データを保存しました！")
                            st.rerun()
                        else:
                            st.error("❌ データの保存に失敗しました")
                
                except Exception as e:
                    st.error(f"❌ エラーが発生しました: {str(e)}")
        
        # 上書き確認処理
        if 'pending_data' in st.session_state:
            col_yes, col_no = st.columns(2)
            
            with col_yes:
                if st.button("🔄 上書きする", type="primary", key="overwrite_yes"):
                    pending = st.session_state.pending_data
                    success = db.add_measurement(pending['date'], pending['weight'], pending['body_fat'])
                    if success:
                        st.success("✅ データを更新しました！")
                        del st.session_state.pending_data
                        st.rerun()
                    else:
                        st.error("❌ データの更新に失敗しました")
            
            with col_no:
                if st.button("❌ キャンセル", key="overwrite_no"):
                    del st.session_state.pending_data
                    st.rerun()
        
        # 区切り線
        st.markdown("---")
        
        # 2. 目標体重設定セクション
        st.header("🎯 目標体重設定")
        
        try:
            # 現在の目標体重を取得
            current_target = db.get_setting('target_weight')
            if current_target is None:
                current_target = 70.0
            
            # 目標体重入力フォーム
            with st.form("target_weight_form"):
                target_weight = st.number_input(
                    "目標体重 (kg)",
                    min_value=10.0,
                    max_value=300.0,
                    value=current_target,
                    step=0.1,
                    format="%.1f",
                    help="目標とする体重を設定してください"
                )
                
                if st.form_submit_button("🎯 目標設定", type="primary"):
                    try:
                        success = db.set_setting('target_weight', target_weight)
                        if success:
                            st.success("✅ 目標体重を設定しました！")
                            st.rerun()
                        else:
                            st.error("❌ 目標体重の設定に失敗しました")
                    except Exception as e:
                        st.error(f"❌ エラー: {str(e)}")
            
            # 進捗バー表示
            try:
                # 最新の体重データを取得
                recent_data = db.get_measurements(1)
                if not recent_data.empty:
                    current_weight = recent_data.iloc[0]['weight']
                    
                    # 進捗計算
                    weight_diff = current_weight - target_weight
                    
                    # 進捗バーの表示
                    st.subheader("📈 目標達成進捗")
                    
                    # 目標達成状況の表示
                    if abs(weight_diff) <= 0.5:  # 0.5kg以内の誤差を許容
                        st.success(f"🎉 目標達成！ 現在: {current_weight:.1f}kg")
                        st.balloons()
                    else:
                        if weight_diff > 0:
                            st.warning(f"📉 目標まで {abs(weight_diff):.1f}kg減量が必要")
                        else:
                            st.info(f"📈 目標まで {abs(weight_diff):.1f}kg増量が必要")
                    
                    # 進捗バーの計算と表示
                    # 開始体重を30日前のデータまたは初回データから取得
                    all_data = db.get_measurements()
                    if not all_data.empty:
                        # 30日前のデータを取得（期間フィルタリング）
                        start_data = filter_data_by_period(all_data, 30)
                        if not start_data.empty:
                            start_weight = start_data.iloc[0]['weight']  # 最も古いデータ
                        
                        # 進捗率計算
                        if start_weight != target_weight:
                            progress = (start_weight - current_weight) / (start_weight - target_weight)
                            progress = max(0, min(1, progress))  # 0-1の範囲に制限
                            
                            st.progress(progress)
                            st.caption(f"開始: {start_weight:.1f}kg → 現在: {current_weight:.1f}kg → 目標: {target_weight:.1f}kg")
                        else:
                            st.progress(1.0)
                            st.caption(f"現在: {current_weight:.1f}kg = 目標: {target_weight:.1f}kg")
                
                else:
                    st.info("📝 データがありません。体重を記録してください。")
                    
            except Exception as e:
                st.error(f"進捗計算エラー: {str(e)}")
                
        except Exception as e:
            st.error(f"目標体重設定エラー: {str(e)}")
        
        # 区切り線
        st.markdown("---")
        
        # 3. データ管理セクション
        st.header("📁 データ管理")
        
        # CSVエクスポート
        st.subheader("📤 データエクスポート")
        
        try:
            # 全データをCSV形式で取得
            df_export = db.export_to_csv()
            
            if not df_export.empty:
                # CSVファイルとして出力
                csv_data = df_export.to_csv(index=False)
                
                # 現在の日付をファイル名に含める
                current_date = datetime.now().strftime("%Y%m%d")
                filename = f"weight_data_{current_date}.csv"
                
                st.download_button(
                    label="📥 CSVファイルをダウンロード",
                    data=csv_data,
                    file_name=filename,
                    mime="text/csv",
                    key="download_csv",
                    help=f"{len(df_export)}件のデータをダウンロード"
                )
                
                st.info(f"💾 ダウンロード可能: {len(df_export)}件のデータ")
            else:
                st.warning("⚠️ エクスポートするデータがありません")
                
        except Exception as e:
            st.error(f"❌ エクスポートの準備に失敗しました: {str(e)}")
        
        # CSVインポート
        st.subheader("📤 データインポート")
        
        uploaded_file = st.file_uploader(
            "CSVファイルを選択",
            type=['csv'],
            help="体重データのCSVファイルを選択してください。必須: date, weight"
        )
        
        if uploaded_file is not None:
            try:
                # CSVファイルを読み込み
                df_import = pd.read_csv(uploaded_file)
                
                # データの確認
                st.write("**プレビュー（最初の5行）:**")
                st.dataframe(df_import.head())
                
                # 必要なカラムの確認
                required_columns = ['date', 'weight']
                missing_columns = [col for col in required_columns if col not in df_import.columns]
                
                if missing_columns:
                    st.error(f"❌ 必要なカラムが不足しています: {missing_columns}")
                    st.info("💡 CSVファイルには少なくとも 'date' と 'weight' のカラムが必要です")
                else:
                    # データのバリデーション
                    valid_rows = []
                    invalid_rows = []
                    
                    for idx, row in df_import.iterrows():
                        try:
                            # 日付のバリデーション
                            date_str = str(row['date']).strip()
                            if not date_str or date_str.lower() in ['nan', 'none', '']:
                                invalid_rows.append(f"行{idx+2}: 日付が空です")
                                continue
                            
                            # 体重のバリデーション
                            weight_val = row['weight']
                            if pd.isna(weight_val) or weight_val == '':
                                invalid_rows.append(f"行{idx+2}: 体重が空です")
                                continue
                            
                            weight = float(weight_val)
                            if not (10.0 <= weight <= 300.0):
                                invalid_rows.append(f"行{idx+2}: 体重が範囲外です ({weight}kg)")
                                continue
                            
                            # 体脂肪率のバリデーション（任意）
                            body_fat = None
                            if 'body_fat' in row and pd.notna(row['body_fat']) and str(row['body_fat']).strip():
                                body_fat_val = float(row['body_fat'])
                                if not (0.0 <= body_fat_val <= 100.0):
                                    invalid_rows.append(f"行{idx+2}: 体脂肪率が範囲外です ({body_fat_val}%)")
                                    continue
                                body_fat = body_fat_val
                            
                            valid_rows.append({
                                'date': date_str,
                                'weight': weight,
                                'body_fat': body_fat,
                                'row_num': idx + 2
                            })
                            
                        except (ValueError, TypeError) as e:
                            invalid_rows.append(f"行{idx+2}: データ変換エラー ({str(e)})")
                    
                    # バリデーション結果の表示
                    if invalid_rows:
                        st.warning(f"⚠️ {len(invalid_rows)}件の無効なデータがあります:")
                        for error in invalid_rows[:5]:  # 最初の5件のみ表示
                            st.text(f"  • {error}")
                        if len(invalid_rows) > 5:
                            st.text(f"  ... 他 {len(invalid_rows)-5}件")
                    
                    if not valid_rows:
                        st.error("❌ 有効なデータがありません")
                    else:
                        st.info(f"✅ {len(valid_rows)}件の有効なデータが見つかりました")
                        
                        # 重複データの確認
                        existing_data = db.get_measurements()
                        existing_dates = set()
                        if not existing_data.empty:
                            existing_dates = set(existing_data['date'].dt.strftime('%Y-%m-%d').tolist())
                        
                        duplicate_dates = []
                        for row_data in valid_rows:
                            if row_data['date'] in existing_dates:
                                duplicate_dates.append(row_data['date'])
                        
                        if duplicate_dates:
                            unique_duplicates = list(set(duplicate_dates))
                            st.warning(f"⚠️ 重複する日付が{len(unique_duplicates)}件見つかりました")
                            st.write("重複する日付:", unique_duplicates[:10])
                            
                            # 重複データの処理方法を選択
                            duplicate_action = st.radio(
                                "重複データの処理方法",
                                options=["スキップ", "上書き"],
                                help="スキップ: 重複データを無視, 上書き: 既存データを新しいデータで置き換え",
                                key="duplicate_action"
                            )
                        else:
                            duplicate_action = "スキップ"
                            st.success("✅ 重複データはありません")
                        
                        # インポート実行ボタン
                        if st.button("📤 データをインポート", key="csv_import"):
                            try:
                                success_count = 0
                                error_count = 0
                                skipped_count = 0
                                
                                # プログレスバー
                                progress_bar = st.progress(0)
                                status_text = st.empty()
                                
                                for i, row_data in enumerate(valid_rows):
                                    try:
                                        date_str = row_data['date']
                                        weight = row_data['weight']
                                        body_fat = row_data['body_fat']
                                        
                                        # 重複チェック
                                        if date_str in existing_dates:
                                            if duplicate_action == "スキップ":
                                                skipped_count += 1
                                                continue
                                            elif duplicate_action == "上書き":
                                                # 既存データを削除
                                                matching_record = existing_data[existing_data['date'].dt.strftime('%Y-%m-%d') == date_str]
                                                if not matching_record.empty:
                                                    record_id = int(matching_record.iloc[0]['id'])
                                                    db.delete_measurement(record_id)
                                        
                                        # 新しいデータを挿入
                                        if db.add_measurement(date_str, weight, body_fat):
                                            success_count += 1
                                            existing_dates.add(date_str)
                                        else:
                                            error_count += 1
                                        
                                        # プログレス更新
                                        progress = (i + 1) / len(valid_rows)
                                        progress_bar.progress(progress)
                                        status_text.text(f"処理中... {i+1}/{len(valid_rows)}")
                                        
                                    except Exception as row_error:
                                        st.error(f"行{row_data['row_num']}のエラー: {str(row_error)}")
                                        error_count += 1
                                
                                # 結果表示
                                progress_bar.empty()
                                status_text.empty()
                                
                                if success_count > 0:
                                    st.success(f"✅ {success_count}件のデータをインポートしました")
                                    
                                if skipped_count > 0:
                                    st.info(f"ℹ️ {skipped_count}件のデータをスキップしました（重複のため）")
                                    
                                if error_count > 0:
                                    st.warning(f"⚠️ {error_count}件のデータでエラーが発生しました")
                                
                                if success_count > 0:
                                    st.rerun()
                                elif success_count == 0 and error_count == 0:
                                    st.info("📝 インポートする新しいデータがありませんでした")
                                
                            except Exception as e:
                                st.error(f"❌ インポートエラー: {str(e)}")
                            
            except Exception as e:
                st.error(f"❌ ファイルの読み込みに失敗しました: {str(e)}")
                st.info("💡 CSVファイルが正しい形式であることを確認してください")
    
    # 右メインコンテンツ（表示・分析エリア）
    # 1. 統計情報セクション（最上部）
    st.subheader("📊 統計情報")
    
    try:
        # 基本統計情報を取得
        df_all = db.get_measurements()
        if not df_all.empty:
            # 最新のデータを取得
            latest_data = df_all.iloc[-1]  # 最新データ
            
            # 7日移動平均を計算
            df_with_ma = calculate_moving_average(df_all, 7)
            latest_ma = df_with_ma.iloc[-1]['weight_ma'] if not df_with_ma.empty else None
            
            # 目標体重を取得
            target_weight = db.get_setting('target_weight')
            
            # 目標差分の計算
            goal_diff = latest_data['weight'] - target_weight if target_weight is not None else None
            
            # 統計情報をカード風で表示
            metrics = [
                ("データ数", f"{len(df_all)}件"),
                ("直近体重", f"{latest_data['weight']:.1f}kg"),
                ("7日移動平均", f"{latest_ma:.1f}kg" if latest_ma is not None else "N/A"),
                ("目標差分", f"{goal_diff:+.1f}kg" if goal_diff is not None else "未設定"),
                ("直近体脂肪率", f"{latest_data['body_fat']:.1f}%" if pd.notna(latest_data['body_fat']) else "未記録")
            ]
            
            # st.columns を使って統計情報カードを横並びにする
            col_list = st.columns(len(metrics))
            for col, (label, value) in zip(col_list, metrics):
                col.markdown(
                    f"""
                    <div class="metric-card">
                      <div class="metric-label">{label}</div>
                      <div class="metric-value">{value}</div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
        else:
            st.info("📝 データがありません。左側のフォームから記録を追加してください。")
    
    except Exception as e:
        st.error(f"統計情報の取得に失敗しました: {str(e)}")
    
    # 2. 期間選択セクション
    st.subheader("📅 期間選択")
    
    # 期間選択用のラジオボタン
    period_options = {
        "7日間": 7,
        "30日間": 30,
        "90日間": 90,
        "全期間": None
    }
    
    selected_period = st.radio(
        "表示期間を選択してください",
        options=list(period_options.keys()),
        index=1,  # デフォルトは30日間
        horizontal=True,
        key="period_filter"
    )
    
    period_days = period_options[selected_period]
    
    # 3. グラフセクション
    st.subheader("📈 体重推移グラフ")
    
    try:
        # データ取得（全データを取得）
        df = db.get_measurements()
        
        if not df.empty:
            # 期間でフィルタリング
            if period_days:
                df = filter_data_by_period(df, period_days)
            
            # 目標体重を取得
            target_weight = db.get_setting('target_weight')
            
            # グラフ作成・表示
            fig = create_weight_graph(df, period_days, target_weight)
            st.plotly_chart(fig, use_container_width=True)
        else:
            # データがない場合
            target_weight = db.get_setting('target_weight')
            fig = create_weight_graph(pd.DataFrame(), period_days, target_weight)
            st.plotly_chart(fig, use_container_width=True)
    
    except Exception as e:
        st.error(f"グラフの表示に失敗しました: {str(e)}")
    
    # 4. データ編集セクション
    st.subheader("📋 データ編集・削除")
    
    try:
        df_recent = db.get_measurements()  # 全件数を取得
        
        if not df_recent.empty:
            # 編集用データフレームの準備
            edit_df = df_recent.copy()
            edit_df['date'] = edit_df['date'].dt.strftime('%Y-%m-%d')
            edit_df = edit_df.sort_values('date', ascending=False)
            
            # 表示用にカラム名を日本語に変更
            edit_df = edit_df.rename(columns={
                'date': '日付',
                'weight': '体重(kg)',
                'body_fat': '体脂肪率(%)'
            })
            
            # 編集可能なデータエディタ
            st.info(f"💡 データをダブルクリックで編集できます。行を削除するには、行の左端にあるゴミ箱アイコンをクリックしてください。（全データ：{len(edit_df)}件表示中）")
            
            edited_df = st.data_editor(
                edit_df[['日付', '体重(kg)', '体脂肪率(%)']],
                use_container_width=True,
                hide_index=True,
                num_rows="dynamic",  # 動的な行数（削除・追加可能）
                column_config={
                    "日付": st.column_config.TextColumn(
                        "日付",
                        help="YYYY-MM-DD形式",
                        disabled=True,  # 日付は編集不可
                    ),
                    "体重(kg)": st.column_config.NumberColumn(
                        "体重(kg)",
                        help="体重をkg単位で入力",
                        min_value=10.0,
                        max_value=300.0,
                        step=0.1,
                        format="%.1f",
                    ),
                    "体脂肪率(%)": st.column_config.NumberColumn(
                        "体脂肪率(%)",
                        help="体脂肪率を%単位で入力",
                        min_value=0.0,
                        max_value=100.0,
                        step=0.1,
                        format="%.1f",
                    ),
                },
                key="data_editor"
            )
            
            # 変更の検知と処理
            if st.button("💾 変更を保存", type="primary", key="save_changes"):
                try:
                    # 変更されたデータをデータベースに反映
                    changes_made = False
                    deletions_made = False
                    
                    # 削除された行の検知
                    if len(edited_df) < len(edit_df):
                        st.warning("⚠️ 削除された行が検出されました。データベースから削除します。")
                        
                        # 削除された行を特定
                        original_dates = set(edit_df['日付'].tolist())
                        edited_dates = set(edited_df['日付'].tolist())
                        deleted_dates = original_dates - edited_dates
                        
                        for deleted_date in deleted_dates:
                            # 日付をキーにしてdf_recentから対応するレコードを検索
                            matching_records = df_recent[df_recent['date'].dt.strftime('%Y-%m-%d') == deleted_date]
                            
                            if not matching_records.empty:
                                record_id = int(matching_records.iloc[0]['id'])
                                
                                # データベースから削除
                                success = db.delete_measurement(record_id)
                                if success:
                                    st.success(f"✅ {deleted_date}のデータを削除しました")
                                    deletions_made = True
                                else:
                                    st.error(f"❌ {deleted_date}のデータ削除に失敗しました")
                            else:
                                st.error(f"❌ {deleted_date}のレコードが見つかりません")
                    
                    # 編集された行の検知
                    for i in range(len(edited_df)):
                        # 編集されたデータフレームの日付でマッチング
                        edited_row = edited_df.iloc[i]
                        edited_date = edited_row['日付']
                        
                        # 元データから対応する行を探す
                        original_matching = edit_df[edit_df['日付'] == edited_date]
                        if not original_matching.empty:
                            original_row = original_matching.iloc[0]
                            
                            # 変更があったかチェック
                            if (original_row['体重(kg)'] != edited_row['体重(kg)'] or 
                                original_row['体脂肪率(%)'] != edited_row['体脂肪率(%)']):
                                
                                # 日付をキーにしてdf_recentから対応するレコードを検索
                                matching_records = df_recent[df_recent['date'].dt.strftime('%Y-%m-%d') == edited_date]
                                
                                if not matching_records.empty:
                                    record_id = int(matching_records.iloc[0]['id'])
                                    success = db.update_measurement(
                                        record_id,
                                        float(edited_row['体重(kg)']),
                                        float(edited_row['体脂肪率(%)']) if pd.notna(edited_row['体脂肪率(%)']) else None
                                    )
                                    
                                    if success:
                                        changes_made = True
                                        st.success(f"✅ {edited_row['日付']}のデータを更新しました")
                                    else:
                                        st.error(f"❌ {edited_row['日付']}のデータ更新に失敗しました")
                                else:
                                    st.error(f"❌ {edited_date}のレコードが見つかりません")
                    
                    if changes_made or deletions_made:
                        st.success("✅ 変更を保存しました！")
                        st.rerun()
                    else:
                        st.info("📝 変更はありませんでした")
                        
                except Exception as e:
                    st.error(f"❌ データの保存に失敗しました: {str(e)}")
            
        else:
            st.info("📝 編集可能なデータがありません。")
    
    except Exception as e:
        st.error(f"データ編集機能の読み込みに失敗しました: {str(e)}")


if __name__ == "__main__":
    main() 