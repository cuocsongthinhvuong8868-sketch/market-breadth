import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import os
import time
from datetime import datetime, timedelta

# --- CẤU HÌNH API KEY ---
os.environ['VNSTOCK_API_KEY'] = 'vnstock_17b56a86b930db526e25e8de447a0bfd'

try:
    from vnstock import Quote
except ImportError:
    st.error("Vui lòng cài đặt thư viện: pip install -U vnstock")
    st.stop()

# Cấu hình trang Streamlit
st.set_page_config(page_title="Market Breadth", layout="wide")

st.title("📊 Market Breadth - Chỉ báo Độ Rộng Thị Trường")
st.markdown("Đo lường số lượng cổ phiếu VNAllShare nằm trên các đường MA20, MA60, MA125 và MA252.")

# ================= CẤU HÌNH DANH SÁCH MÃ =================
VNALLSHARE_LIST = [
    'VIX', 'BSR', 'HCM', 'POW', 'KHG', 'DXG', 'CII', 'VND', 'VCI', 'EIB', 
    'DIG', 'GEX', 'VSC', 'PVD', 'PDR', 'VCG', 'DPM', 'HAG', 'NVL', 'DBC', 
    'PC1', 'TCH', 'GEL', 'EVF', 'PVT', 'KDH', 'KBC', 'NKG', 'MSB', 'DLG', 
    'DCM', 'HHV', 'HQC', 'HSG', 'DGW', 'HDC', 'NLG', 'BAF', 'IJC', 'VCK', 
    'PNJ', 'TCX', 'PET', 'SCR', 'VOS', 'GMD', 'LCG', 'DXS', 'HDG', 'HAH', 
    'ANV', 'ORS', 'VGC', 'OCB', 'HHS', 'HVN', 'VHC', 'HPX', 'ELC', 'NT2', 
    'VPI', 'TCM', 'YEG', 'LDG', 'SZC', 'AAA', 'VDS', 'NAB', 'KSB', 'BVH', 
    'FTS', 'TTF', 'AGR', 'PAN', 'DRH', 'VTP', 'HHP', 'CRC', 'NTL', 'PHR', 
    'CTR', 'DPR', 'VAB', 'DPG', 'VPX', 'CTS', 'CSV', 'FCN', 'HID', 'CTD', 
    'MSH', 'EVG', 'NAF', 'SIP', 'HT1', 'KLB', 'VPL', 'FRT', 'DHC', 'OGC', 
    'CTI', 'TV2', 'REE', 'BMI', 'BSI', 'QCG', 'HAX', 'FIT', 'GEE', 'CMG', 
    'IDI', 'SBT', 'DCL', 'DRC', 'MIG', 'SHI', 'ASM', 'RYG', 'HPA', 'PVP', 
    'SMC', 'GEG', 'CSM', 'TAL', 'TCO', 'KOS', 'AGG', 'SCS', 'DSE', 'BFC', 
    'PAC', 'VIP', 'VTO', 'CTF', 'CRE', 'APG', 'DC4', 'TLG', 'GIL', 'PPC', 
    'TDP', 'KDC', 'HII', 'VPG', 'TSC', 'APH', 'HSL', 'BIC', 'FIR', 'TTA', 
    'TLH', 'HTN', 'SAM', 'VNE', 'MCH', 'TLD', 'TVS', 'PTB', 'VVS', 'LSS', 
    'TDC', 'HAR', 'BWE', 'BMP', 'SKG', 'JVC', 'NHA', 'TSA', 'CDC', 'CMX','SHB', 'HPG', 'MBB', 'SSI', 'VPB', 'HDB', 'CTG', 'ACB', 'FPT', 'VCB', 
    'TPB', 'STB', 'TCB', 'BID', 'PLX', 'VRE', 'VNM', 'MSN', 'GVR', 'VHM', 
    'MWG', 'VIB', 'VIC', 'DGC', 'GAS', 'SSB', 'SAB', 'BCM', 'LPB', 'VJC'
]

CACHE_FILE = "market_breadth_cache.csv"

# ================= HÀM TẢI VÀ XỬ LÝ DỮ LIỆU =================
@st.cache_data(ttl=86400)
def load_and_process_data(symbols):
    if os.path.exists(CACHE_FILE):
        file_mod_time = datetime.fromtimestamp(os.path.getmtime(CACHE_FILE))
        if file_mod_time.date() == datetime.now().date():
            st.success(f"⚡ Đang tải dữ liệu từ file CSV Cache (cập nhật lúc {file_mod_time.strftime('%H:%M:%S')})")
            df_merged = pd.read_csv(CACHE_FILE, index_col=0, parse_dates=True)
            return df_merged

    st.info("🔄 Không tìm thấy Cache của ngày hôm nay. Bắt đầu tải dữ liệu mới từ API...")
    # SỬA Ở ĐÂY: Tải 3 năm (1095 ngày) để có vùng đệm tính MA252
    start_date = (datetime.now() - timedelta(days=1095)).strftime('%Y-%m-%d')
    end_date = datetime.now().strftime('%Y-%m-%d')
    
    all_data = []
    
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    for i, symbol in enumerate(symbols):
        try:
            status_text.text(f"Đang tải dữ liệu: {symbol} ({i+1}/{len(symbols)})")
            
            quote = Quote(symbol=symbol, source='VCI')
            df = quote.history(start=start_date, end=end_date, interval='1D')
            
            if df is not None and not df.empty:
                df.columns = df.columns.str.lower()
                df_close = df[['time', 'close']].copy()
                df_close.rename(columns={'close': symbol}, inplace=True)
                df_close.set_index('time', inplace=True)
                all_data.append(df_close)
            
            time.sleep(1) 
            
        except Exception as e:
            continue
            
        progress_bar.progress((i + 1) / len(symbols))
        
    status_text.text("Tải dữ liệu hoàn tất! Đang lưu Cache và tính toán...")
    progress_bar.empty()
    
    if not all_data:
        return None
        
    df_merged = pd.concat(all_data, axis=1)
    df_merged.index = pd.to_datetime(df_merged.index)
    df_merged.sort_index(inplace=True)
    
    df_merged.to_csv(CACHE_FILE)
    st.success("✅ Đã tải dữ liệu mới và lưu thành file CSV Cache.")
    
    return df_merged

# ================= TÍNH TOÁN MARKET BREADTH =================
df_prices = load_and_process_data(VNALLSHARE_LIST)

if df_prices is not None and not df_prices.empty:
    
    df_prices = df_prices.ffill()

    ma20 = df_prices.rolling(window=20).mean()
    ma60 = df_prices.rolling(window=60).mean()
    ma125 = df_prices.rolling(window=125).mean()
    ma252 = df_prices.rolling(window=252).mean()

    breadth_20 = (df_prices > ma20).sum(axis=1)
    breadth_60 = (df_prices > ma60).sum(axis=1)
    breadth_125 = (df_prices > ma125).sum(axis=1)
    breadth_252 = (df_prices > ma252).sum(axis=1)

    df_breadth = pd.DataFrame({
        '> MA20': breadth_20,
        '> MA60': breadth_60,
        '> MA125': breadth_125,
        '> MA252': breadth_252
    })
    
    df_breadth.dropna(inplace=True)

    # SỬA Ở ĐÂY: Ép dữ liệu chỉ hiển thị đúng 2 năm gần nhất (730 ngày)
    two_years_ago = pd.to_datetime(datetime.now() - timedelta(days=365))
    # Chuyển index của df_breadth về tz-naive nếu bị lệch múi giờ
    if df_breadth.index.tz is not None:
        df_breadth.index = df_breadth.index.tz_localize(None)
        
    df_breadth_plot = df_breadth[df_breadth.index >= two_years_ago]

    # ================= VẼ BIỂU ĐỒ BẰNG PLOTLY =================
    fig = go.Figure()

    colors = {'> MA20': '#1f77b4', '> MA60': '#ff7f0e', '> MA125': '#2ca02c', '> MA252': '#d62728'}
    
    # Dùng df_breadth_plot để vẽ thay vì df_breadth nguyên bản
    for col in df_breadth_plot.columns:
        fig.add_trace(go.Scatter(
            x=df_breadth_plot.index, 
            y=df_breadth_plot[col], 
            mode='lines', 
            name=col,
            line=dict(width=2, color=colors[col])
        ))

    fig.update_layout(
        title="Số lượng cổ phiếu nằm trên các đường Trung bình động (MA) - 2 Năm gần nhất",
        xaxis_title="Thời gian",
        yaxis_title="Số lượng cổ phiếu",
        hovermode="x unified",
        template="plotly_white",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        margin=dict(l=0, r=0, t=50, b=0)
    )

    st.plotly_chart(fig, use_container_width=True)

    # ================= HIỂN THỊ DỮ LIỆU HIỆN TẠI =================
    st.subheader(f"Dữ liệu Market Breadth hiện tại ({df_breadth_plot.index[-1].strftime('%d/%m/%Y')})")
    latest_data = df_breadth_plot.iloc[-1]
    
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Cổ phiếu > MA20", f"{int(latest_data['> MA20'])}")
    col2.metric("Cổ phiếu > MA60", f"{int(latest_data['> MA60'])}")
    col3.metric("Cổ phiếu > MA125", f"{int(latest_data['> MA125'])}")
    col4.metric("Cổ phiếu > MA252", f"{int(latest_data['> MA252'])}")

    # ================= NÚT XÓA CACHE CHỦ ĐỘNG =================
    st.markdown("---")
    if st.button("🔄 Cập nhật dữ liệu mới nhất từ API (Xóa Cache)"):
        if os.path.exists(CACHE_FILE):
            os.remove(CACHE_FILE) 
        st.cache_data.clear()     
        st.rerun()                

else:
    st.error("Không thể tải dữ liệu. Vui lòng kiểm tra lại kết nối mạng hoặc API Key.")
