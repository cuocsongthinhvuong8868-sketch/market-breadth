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
    'TDC', 'HAR', 'BWE', 'BMP', 'SKG', 'JVC', 'NHA', 'TSA', 'CDC', 'CMX',
    'SHB', 'HPG', 'MBB', 'SSI', 'VPB', 'HDB', 'CTG', 'ACB', 'FPT', 'VCB', 
    'TPB', 'STB', 'TCB', 'BID', 'PLX', 'VRE', 'VNM', 'MSN', 'GVR', 'VHM', 
    'MWG', 'VIB', 'VIC', 'DGC', 'GAS', 'SSB', 'SAB', 'BCM', 'LPB', 'VJC'
]

CACHE_FILE = r"C:\Users\ADMIN\Desktop\9999\market_breadth\market_breadth_cache.csv"

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
    start_date = (datetime.now() - timedelta(days=1825)).strftime('%Y-%m-%d')
    end_date = datetime.now().strftime('%Y-%m-%d')
    
    all_data = []
    
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    for i, symbol in enumerate(symbols):
        try:
            status_text.text(f"Đang tải dữ liệu: {symbol} ({i+1}/{len(symbols)})")
            
            quote = Quote(symbol=symbol, source='KBS')
            df = quote.history(start=start_date, end=end_date, interval='1D')
            
            if df is not None and not df.empty:
                df.columns = df.columns.str.lower()
                
                # CẬP NHẬT: Lấy cả giá đóng cửa và khối lượng
                df_temp = df[['time', 'close', 'volume']].copy()
                df_temp.rename(columns={'close': f'{symbol}_close', 'volume': f'{symbol}_volume'}, inplace=True)
                df_temp.set_index('time', inplace=True)
                all_data.append(df_temp)
            
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
df_merged = load_and_process_data(VNALLSHARE_LIST)

if df_merged is not None and not df_merged.empty:
    
    # Tách dataframe giá (close) và khối lượng (volume)
    df_prices = df_merged.filter(regex='_close$').rename(columns=lambda x: x.replace('_close', ''))
    df_volumes = df_merged.filter(regex='_volume$').rename(columns=lambda x: x.replace('_volume', ''))
    
    df_prices = df_prices.ffill()
    df_volumes = df_volumes.fillna(0) # Tránh lỗi NaN cho volume

    # Tính các đường MA
    ma20 = df_prices.rolling(window=20).mean()
    ma60 = df_prices.rolling(window=60).mean()
    ma125 = df_prices.rolling(window=125).mean()
    ma252 = df_prices.rolling(window=252).mean()

    # Tính Breadth (số lượng)
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

    if df_breadth.index.tz is not None:
        df_breadth.index = df_breadth.index.tz_localize(None)

    # ================= HISTORY MEASUREMENT (SIDEBAR) =================
    st.sidebar.header("⏱ History Measurement")
    
    min_date = df_breadth.index.min().date()
    max_date = df_breadth.index.max().date()
    
    default_start = max_date - timedelta(days=365)
    default_end = max_date

    start_date = st.sidebar.date_input("Từ ngày", value=default_start, min_value=min_date, max_value=max_date)
    end_date = st.sidebar.date_input("Đến ngày", value=default_end, min_value=min_date, max_value=max_date)

    if start_date > end_date:
        st.sidebar.error("Lỗi: 'Từ ngày' phải trước hoặc bằng 'Đến ngày'.")

    start_datetime = pd.to_datetime(start_date)
    end_datetime = pd.to_datetime(end_date)
    
    df_breadth_plot = df_breadth[(df_breadth.index >= start_datetime) & (df_breadth.index <= end_datetime)]

    # ================= VẼ BIỂU ĐỒ BẰNG PLOTLY =================
    if df_breadth_plot.empty:
        st.warning("Không có dữ liệu trong khoảng thời gian bạn đã chọn.")
    else:
        fig = go.Figure()
        colors = {'> MA20': '#1f77b4', '> MA60': '#ff7f0e', '> MA125': '#2ca02c', '> MA252': '#d62728'}
        
        for col in df_breadth_plot.columns:
            fig.add_trace(go.Scatter(
                x=df_breadth_plot.index, 
                y=df_breadth_plot[col], 
                mode='lines', 
                name=col,
                line=dict(width=2, color=colors[col])
            ))

        fig.update_layout(
            title=f"Số lượng cổ phiếu trên các đường MA ({start_date.strftime('%d/%m/%Y')} - {end_date.strftime('%d/%m/%Y')})",
            xaxis_title="Thời gian",
            yaxis_title="Số lượng cổ phiếu",
            hovermode="x unified",
            template="plotly_white",
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
            margin=dict(l=0, r=0, t=50, b=0)
        )

        st.plotly_chart(fig, use_container_width=True)

        # ================= HIỂN THỊ DỮ LIỆU HIỆN TẠI VÀ BẢNG TOP 10 =================
        latest_date = df_breadth_plot.index[-1]
        st.subheader(f"Dữ liệu Market Breadth cuối kỳ ({latest_date.strftime('%d/%m/%Y')})")
        
        latest_data = df_breadth_plot.iloc[-1]
        
        # Hàm trích xuất Top 10 Vol theo điều kiện MA
        def get_top_10_vol(ma_condition):
            # Lọc ra các cổ phiếu thỏa mãn điều kiện MA tại ngày cuối cùng
            valid_stocks = ma_condition[ma_condition].index
            if len(valid_stocks) == 0:
                return pd.DataFrame()
            
            # Lấy volume của các mã này
            vols = df_volumes.loc[latest_date, valid_stocks]
            top_10 = vols.sort_values(ascending=False).head(10)
            
            # Đóng gói thành DataFrame để hiển thị đẹp hơn
            df_top = pd.DataFrame({
                "Mã CP": top_10.index,
                "Khối lượng": top_10.values
            })
            df_top['Khối lượng'] = df_top['Khối lượng'].apply(lambda x: f"{int(x):,}")
            return df_top

        # Tạo mask (điều kiện) cho ngày cuối cùng
        mask_20 = df_prices.loc[latest_date] > ma20.loc[latest_date]
        mask_60 = df_prices.loc[latest_date] > ma60.loc[latest_date]
        mask_125 = df_prices.loc[latest_date] > ma125.loc[latest_date]
        mask_252 = df_prices.loc[latest_date] > ma252.loc[latest_date]

        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Cổ phiếu > MA20", f"{int(latest_data['> MA20'])}")
            with st.popover("📋 Xem Top 10 Khối Lượng"):
                st.dataframe(get_top_10_vol(mask_20), hide_index=True)
                
        with col2:
            st.metric("Cổ phiếu > MA60", f"{int(latest_data['> MA60'])}")
            with st.popover("📋 Xem Top 10 Khối Lượng"):
                st.dataframe(get_top_10_vol(mask_60), hide_index=True)
                
        with col3:
            st.metric("Cổ phiếu > MA125", f"{int(latest_data['> MA125'])}")
            with st.popover("📋 Xem Top 10 Khối Lượng"):
                st.dataframe(get_top_10_vol(mask_125), hide_index=True)
                
        with col4:
            st.metric("Cổ phiếu > MA252", f"{int(latest_data['> MA252'])}")
            with st.popover("📋 Xem Top 10 Khối Lượng"):
                st.dataframe(get_top_10_vol(mask_252), hide_index=True)

    # ================= NÚT XÓA CACHE CHỦ ĐỘNG =================
    st.markdown("---")
    if st.button("🔄 Cập nhật dữ liệu mới nhất từ API (Xóa Cache)"):
        if os.path.exists(CACHE_FILE):
            os.remove(CACHE_FILE) 
        st.cache_data.clear()     
        st.rerun()                

else:
    st.error("Không thể tải dữ liệu. Vui lòng kiểm tra lại kết nối mạng hoặc API Key.")
