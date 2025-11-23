import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import os

# =============================================================================
# PAGE CONFIG
# =============================================================================
st.set_page_config(
    page_title="The Supercharged Archipelago",
    page_icon="🌀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =============================================================================
# DATA LOADING (with fallback for missing files)
# =============================================================================
@st.cache_data
def load_csv_safe(filepath):
    """Safely load CSV, return None if not found"""
    try:
        return pd.read_csv(filepath)
    except FileNotFoundError:
        return None

@st.cache_data
def load_all_data():
    """Load all datasets"""
    base_path = 'data/processed'
    
    return {
        'kpi': load_csv_safe(f'{base_path}/emdat_kpi_data.csv'),
        'yearly_storms': load_csv_safe(f'{base_path}/emdat_yearly_storms.csv'),
        'decade_summary': load_csv_safe(f'{base_path}/emdat_decade_summary.csv'),
        'super_typhoons': load_csv_safe(f'{base_path}/emdat_super_typhoons.csv'),
        'europe_comparison': load_csv_safe(f'{base_path}/emdat_europe_comparison.csv'),
        'frequency_intensity': load_csv_safe(f'{base_path}/ibtracs_frequency_vs_intensity.csv'),
        'mindanao': load_csv_safe(f'{base_path}/ibtracs_mindanao_storms.csv'),
        'era_comparison': load_csv_safe(f'{base_path}/ibtracs_era_comparison.csv'),
    }

data = load_all_data()

# =============================================================================
# SIDEBAR
# =============================================================================
st.sidebar.markdown("## 🌀 Navigation")

page = st.sidebar.radio(
    "Section",
    ["🏠 Overview", "📈 The Paradox", "🗺️ Mindanao", "⚡ Spotlight", "🌍 Comparison", "📊 Data"],
    label_visibility="collapsed"
)

st.sidebar.markdown("---")
decades = ['All', '1980s', '1990s', '2000s', '2010s', '2020s']
selected_decade = st.sidebar.selectbox("Filter by Decade", decades)

# =============================================================================
# OVERVIEW PAGE
# =============================================================================
if page == "🏠 Overview":
    st.title("🌀 The Supercharged Archipelago")
    st.markdown("**Philippine Typhoons 1980-2024: A Data-Driven Narrative**")
    st.markdown("---")
    
    # KPIs
    if data['kpi'] is not None:
        df = data['kpi']
        if selected_decade != 'All':
            df = df[df['decade'] == selected_decade]
        
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("🌀 Storms", f"{len(df):,}")
        c2.metric("💔 Deaths", f"{int(df['deaths'].sum()):,}")
        c3.metric("👥 Displaced", f"{df['affected'].sum()/1e6:.2f}M")
        c4.metric("💰 Damage", f"${df['damage_usd'].sum()/1e9:.1f}B")
    
    st.markdown("---")
    
    # Quick chart
    if data['frequency_intensity'] is not None:
        st.subheader("Frequency vs Intensity Trend")
        
        df_fi = data['frequency_intensity']
        
        fig = make_subplots(specs=[[{"secondary_y": True}]])
        
        fig.add_trace(
            go.Bar(x=df_fi['year'], y=df_fi['storm_count'], 
                   name="Storms", marker_color='steelblue', opacity=0.7),
            secondary_y=False
        )
        
        fig.add_trace(
            go.Scatter(x=df_fi['year'], y=df_fi['avg_intensity_per_storm'],
                       name="Avg Intensity", line=dict(color='firebrick', width=2)),
            secondary_y=True
        )
        
        fig.add_trace(
            go.Scatter(x=df_fi['year'], y=df_fi['avg_intensity_trend'],
                       name="Intensity Trend", line=dict(color='darkred', dash='dash')),
            secondary_y=True
        )
        
        fig.update_layout(height=400, legend=dict(orientation="h", y=1.1))
        fig.update_yaxes(title_text="Storm Count", secondary_y=False)
        fig.update_yaxes(title_text="Intensity", secondary_y=True)
        
        st.plotly_chart(fig, use_container_width=True)
    
    # Key insights
    st.markdown("### Key Findings")
    col1, col2 = st.columns(2)
    
    with col1:
        st.info("**The Paradox:** Storm frequency is STABLE, but intensity is INCREASING")
    with col2:
        st.warning("**Vanishing Shield:** Mindanao now faces regular super typhoon strikes")

# =============================================================================
# THE PARADOX PAGE
# =============================================================================
elif page == "📈 The Paradox":
    st.title("📈 It's Not the Frequency, It's the Ferocity")
    st.markdown("---")
    
    if data['frequency_intensity'] is not None:
        df = data['frequency_intensity']
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Storm Count (Stable)")
            fig1 = px.bar(df, x='year', y='storm_count', color_discrete_sequence=['steelblue'])
            fig1.add_scatter(x=df['year'], y=df['storm_count_trend'], mode='lines',
                            name='Trend', line=dict(color='darkblue', dash='dash'))
            fig1.update_layout(height=350, showlegend=True)
            st.plotly_chart(fig1, use_container_width=True)
        
        with col2:
            st.subheader("Avg Intensity per Storm (Increasing)")
            fig2 = px.bar(df, x='year', y='avg_intensity_per_storm', color_discrete_sequence=['firebrick'])
            fig2.add_scatter(x=df['year'], y=df['avg_intensity_trend'], mode='lines',
                            name='Trend', line=dict(color='darkred', dash='dash'))
            fig2.update_layout(height=350, showlegend=True)
            st.plotly_chart(fig2, use_container_width=True)
        
        # Era comparison
        if data['era_comparison'] is not None:
            st.markdown("---")
            st.subheader("Era Comparison: 1980-2009 vs 2010-2024")
            
            era = data['era_comparison']
            c1, c2, c3 = st.columns(3)
            
            c1.metric("Storms/Year", f"{era.iloc[1]['storms_per_year']:.1f}",
                     f"{((era.iloc[1]['storms_per_year']/era.iloc[0]['storms_per_year'])-1)*100:+.1f}%")
            c2.metric("Cat 5/Year", f"{era.iloc[1]['cat5_per_year']:.2f}",
                     f"{((era.iloc[1]['cat5_per_year']/era.iloc[0]['cat5_per_year'])-1)*100:+.1f}%")
            c3.metric("Avg Intensity", f"{era.iloc[1]['avg_intensity_per_storm']:.3f}",
                     f"{((era.iloc[1]['avg_intensity_per_storm']/era.iloc[0]['avg_intensity_per_storm'])-1)*100:+.1f}%")

# =============================================================================
# MINDANAO PAGE
# =============================================================================
elif page == "🗺️ Mindanao":
    st.title("🗺️ The Vanishing Shield")
    st.markdown("*How Mindanao Became a Typhoon Alley*")
    st.markdown("---")
    
    if data['mindanao'] is not None:
        df = data['mindanao']
        
        pre = df[df['year'] < 2010]
        post = df[df['year'] >= 2010]
        
        c1, c2, c3 = st.columns(3)
        c1.metric("Pre-2010 (30 yrs)", f"{len(pre)} storms", f"{len(pre)/30:.1f}/year")
        c2.metric("Post-2010 (15 yrs)", f"{len(post)} storms", f"{len(post)/15:.1f}/year")
        c3.metric("Change", f"{((len(post)/15)/(len(pre)/30)-1)*100:+.1f}%", "More exposure")
        
        st.markdown("---")
        
        # By decade
        df['decade'] = ((df['year'] // 10) * 10).astype(str) + 's'
        decade_count = df.groupby('decade').size().reset_index(name='storms')
        
        fig = px.bar(decade_count, x='decade', y='storms', 
                    color='storms', color_continuous_scale=['steelblue', 'firebrick'])
        fig.update_layout(height=350, title="Mindanao Storms by Decade")
        st.plotly_chart(fig, use_container_width=True)
        
        # Cat 5 list
        st.subheader("Category 5 Storms in Mindanao")
        cat5 = df[df['category'] == 'Cat 5'][['name', 'year', 'max_wind_kt']]
        if len(cat5) > 0:
            st.dataframe(cat5.sort_values('year', ascending=False), hide_index=True)
        else:
            st.info("No Category 5 storms in filtered data")

# =============================================================================
# SPOTLIGHT PAGE
# =============================================================================
elif page == "⚡ Spotlight":
    st.title("⚡ Storm Spotlight")
    st.markdown("---")
    
    if data['super_typhoons'] is not None:
        df = data['super_typhoons']
        
        storm = st.selectbox("Select Storm", df['storm_name'].tolist())
        row = df[df['storm_name'] == storm].iloc[0]
        
        c1, c2 = st.columns([1, 2])
        
        with c1:
            st.subheader(row['storm_name'])
            st.write(f"**Year:** {int(row['year'])}")
            st.write(f"**Category:** {row['category']}")
            st.metric("Peak Winds", f"{int(row['peak_winds_kmh'])} km/h")
            if pd.notna(row.get('deaths')):
                st.metric("Deaths", f"{int(row['deaths']):,}")
        
        with c2:
            st.info(f"**Notable:** {row['notable']}")
            
            # Comparison chart
            fig = px.bar(df.nlargest(5, 'peak_winds_kmh'), 
                        x='storm_name', y='peak_winds_kmh',
                        color='peak_winds_kmh', color_continuous_scale=['steelblue', 'firebrick'],
                        title="Top 5 by Wind Speed")
            fig.update_layout(height=300)
            st.plotly_chart(fig, use_container_width=True)

# =============================================================================
# COMPARISON PAGE
# =============================================================================
elif page == "🌍 Comparison":
    st.title("🌍 A Catastrophe in Europe is Annual in the Philippines")
    st.markdown("---")
    
    if data['europe_comparison'] is not None:
        df = data['europe_comparison']
        
        c1, c2 = st.columns(2)
        
        with c1:
            st.subheader("Rainfall (mm/24h)")
            fig1 = px.bar(df, x='event', y='rainfall_mm_24h', color='region',
                         color_discrete_map={'Germany': 'steelblue', 'Europe': 'steelblue', 'Philippines': 'firebrick'})
            fig1.update_layout(height=350)
            st.plotly_chart(fig1, use_container_width=True)
        
        with c2:
            st.subheader("GDP Impact (%)")
            fig2 = px.bar(df, x='event', y='gdp_percent', color='region',
                         color_discrete_map={'Germany': 'steelblue', 'Europe': 'steelblue', 'Philippines': 'firebrick'})
            fig2.update_layout(height=350)
            st.plotly_chart(fig2, use_container_width=True)
        
        st.info("**Key insight:** Typhoon Ketsana dropped 3x the rainfall of Germany's 1-in-500-year flood")

# =============================================================================
# DATA PAGE
# =============================================================================
elif page == "📊 Data":
    st.title("📊 Data Explorer")
    st.markdown("---")
    
    available = {k: v for k, v in data.items() if v is not None}
    
    if available:
        dataset = st.selectbox("Select Dataset", list(available.keys()))
        df = available[dataset]
        
        c1, c2 = st.columns(2)
        c1.metric("Rows", len(df))
        c2.metric("Columns", len(df.columns))
        
        st.dataframe(df, use_container_width=True, height=400)
        
        st.download_button("📥 Download CSV", df.to_csv(index=False), f"{dataset}.csv", "text/csv")
    else:
        st.warning("No data files found. Run the preparation notebooks first.")

# =============================================================================
# FOOTER
# =============================================================================
st.markdown("---")
st.caption("🌀 The Supercharged Archipelago | Data: EM-DAT, IBTrACS | Vennel Chenfoo")