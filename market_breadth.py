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
    'AAA', 'AAM', 'AAT', 'ABS', 'ABT', 'ACB', 'ACC', 'ACG', 'ACL', 'ADG', 
    'ADS', 'AGG', 'AGR', 'AMD', 'ANV', 'APC', 'APG', 'ASG', 'ASM', 'ASP', 
    'AST', 'BAF', 'BCE', 'BCG', 'BCM', 'BFC', 'BHN', 'BIC', 'BID', 'BKG', 
    'BMC', 'BMI', 'BMP', 'BRC', 'BSI', 'BTP', 'BTT', 'BVH', 'BWE', 'C32', 
    'C47', 'CAV', 'CCI', 'CCL', 'CDC', 'CEV', 'CII', 'CKG', 'CLC', 'CLL', 
    'CLW', 'CMG', 'CMV', 'CNG', 'COM', 'CRC', 'CRE', 'CSM', 'CSV', 'CTD', 
    'CTF', 'CTG', 'CTI', 'CTS', 'CVT', 'D2D', 'DAG', 'DAH', 'DAT', 'DBC', 
    'DBD', 'DBT', 'DC4', 'DCM', 'DGC', 'DGW', 'DHA', 'DHC', 'DHG', 'DHM', 
    'DIG', 'DLG', 'DMC', 'DPG', 'DPM', 'DPR', 'DRC', 'DRL', 'DS3', 'DSN', 
    'DTA', 'DTL', 'DTT', 'DVP', 'DXG', 'DXS', 'EIB', 'ELC', 'EVF', 'EVG', 
    'FCN', 'FDC', 'FIR', 'FIT', 'FMC', 'FPT', 'FRT', 'FTS', 'GAS', 'GDT', 
    'GEG', 'GEX', 'GIL', 'GMC', 'GMD', 'GSP', 'GTA', 'GVR', 'HAG', 'HAH', 
    'HAI', 'HAP', 'HAR', 'HAS', 'HAX', 'HBC', 'HCM', 'HDB', 'HDC', 'HDG', 
    'HQC', 'HRC', 'HSG', 'HSL', 'HT1', 'HTI', 'HTL', 'HTN', 'HTV', 'HU1', 
    'HU3', 'HUB', 'HVH', 'HVN', 'HVX', 'ICT', 'IDI', 'IJC', 'ILB', 'IMP', 
    'ITA', 'ITC', 'ITD', 'JVC', 'KBC', 'KDC', 'KDH', 'KMR', 'KOS', 'KPF', 
    'KSB', 'L10', 'LIX', 'LM8', 'LPB', 'LSS', 'MBB', 'MCP', 'MDG', 'MHC', 
    'MIG', 'MSB', 'MSH', 'MSN', 'MWG', 'NAF', 'NAV', 'NBB', 'NCT', 'NHA', 
    'NHH', 'NKG', 'NLG', 'NNC', 'NSC', 'NT2', 'NTL', 'NVL', 'OCB', 'OPC', 
    'ORS', 'PAC', 'PAN', 'PC1', 'PDN', 'PDR', 'PET', 'PGC', 'PGD', 'PGI', 
    'PHC', 'PHR', 'PLX', 'PNJ', 'POM', 'POW', 'PPC', 'PRC', 'PSH', 'PTB', 
    'PTC', 'PVD', 'PVT', 'QBS', 'QCG', 'RAL', 'REE', 'ROS', 'SAB', 'SAM', 
    'SBA', 'SBT', 'SBV', 'SC5', 'SCD', 'SCR', 'SCS', 'SFC', 'SFI', 'SFG', 
    'SGN', 'SGR', 'SHA', 'SHB', 'SHI', 'SHP', 'SII', 'SJD', 'SJF', 'SJS', 
    'SKG', 'SMA', 'SMC', 'SPM', 'SRC', 'SRF', 'SSB', 'SSC', 'SSI', 'ST8', 
    'STB', 'STG', 'STK', 'SVC', 'SVD', 'SVI', 'SVT', 'SZC', 'SZL', 'TBC', 
    'TCB', 'TCD', 'TCH', 'TCL', 'TCM', 'TCO', 'TCR', 'TCT', 'TDC', 'TDG', 
    'TDH', 'TDM', 'TDP', 'TDW', 'TEG', 'THG', 'TIP', 'TIX', 'TLG', 'TLH', 
    'TMP', 'TMS', 'TMT', 'TN1', 'TNA', 'TNC', 'TNH', 'TNI', 'TNT', 'TPB', 
    'TPC', 'TRA', 'TRC', 'TV2', 'TVB', 'TVS', 'TVT', 'TYA', 'UDC', 'UIC', 
    'VAF', 'VCA', 'VCB', 'VCF', 'VCG', 'VCI', 'VCP', 'VDS', 'VFG', 'VGC', 
    'VHC', 'VHM', 'VIB', 'VIC', 'VID', 'VIP', 'VIX', 'VJC', 'VMD', 'VND', 
    'VNE', 'VNG', 'VNL', 'VNM', 'VNS', 'VOS', 'VPB', 'VPD', 'VPG', 'VPH', 
    'VPI', 'VPS', 'VRC', 'VRE', 'VSC', 'VSH', 'VSI', 'VTB', 'VTO', 'YBM', 
    'YEG'
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
    two_years_ago = pd.to_datetime(datetime.now() - timedelta(days=730))
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