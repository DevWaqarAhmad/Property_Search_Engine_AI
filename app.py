import streamlit as st
import time
from datetime import datetime
import pandas as pd
import json

from backend import search_all_properties

st.set_page_config(page_title="Property Seek", page_icon="🏠", layout="wide")

if 'search_history' not in st.session_state:
    st.session_state.search_history = []
if 'last_results' not in st.session_state:
    st.session_state.last_results = []

st.markdown("""
<style>
    /* Main container styling */
    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
        max-width: 1200px;
    }
    
    /* Professional header styling */
    .main-header {
        background: linear-gradient(135deg, #059669, #10b981);
        color: white;
        padding: 2rem;
        border-radius: 12px;
        text-align: center;
        margin-bottom: 2rem;
        box-shadow: 0 4px 20px rgba(59, 130, 246, 0.3);
    }
    
    .main-header h1 {
        margin: 0;
        font-size: 2.5rem;
        font-weight: 700;
        text-shadow: 0 2px 4px rgba(0,0,0,0.3);
    }
    
    .main-header p {
        margin: 0.5rem 0 0 0;
        font-size: 1.1rem;
        opacity: 0.9;
    }
    
    /* Search input styling */
    .stTextInput > div > div > input {
        border: 2px solid #e5e7eb;
        border-radius: 8px;
        padding: 0.75rem 1rem;
        font-size: 1rem;
        transition: border-color 0.3s ease;
        background-color: #ffffff;
        color: #1f2937 !important;
    }
    
    .stTextInput > div > div > input:focus {
        border-color: #3b82f6;
        box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
    }
    
    /* Search button styling */
    .stButton > button {
        background: linear-gradient(135deg, #059669, #10b981);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 0.75rem 2rem;
        font-weight: 600;
        font-size: 1rem;
        transition: all 0.3s ease;
        width: 100%;
    }
    
    .stButton > button:hover {
        background: linear-gradient(135deg, #047857, #059669);
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(16, 185, 129, 0.4);
    }
    
    /* Quick search buttons */
    .quick-search-btn {
        background: linear-gradient(135deg, #6366f1, #8b5cf6);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 0.6rem 1rem;
        font-weight: 500;
        font-size: 0.9rem;
        transition: all 0.3s ease;
        width: 100%;
        margin-bottom: 0.5rem;
    }
    
    /* Property card styling */
    .property-card {
        background: #ffffff;
        border: 1px solid #e5e7eb;
        border-radius: 12px;
        padding: 1.5rem;
        margin: 1rem 0;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        transition: all 0.3s ease;
    }
    
    .property-card:hover {
        transform: translateY(-4px);
        box-shadow: 0 8px 25px rgba(0,0,0,0.15);
        border-color: #3b82f6;
    }
    
    .property-title {
        color: #F6F6F4 !important;
        font-size: 1.25rem;
        font-weight: 600;
        margin-bottom: 0.5rem;
    }
    
    .property-details {
        color: #374151;
        font-size: 1rem;
        margin-bottom: 0.75rem;
    }
    
    .property-price {
        color: #08B255;
        font-weight: 700;
    }
    
    .property-location {
        color: #f5f5f5;
    }
    
    /* Sidebar styling */
    .css-1d391kg {
        background-color: #f8fafc;
    }
    
    /* Metrics styling */
    .metric-container {
        background: linear-gradient(135deg, #f1f5f9, #e2e8f0);
        border-radius: 8px;
        padding: 1rem;
        text-align: center;
        border: 1px solid #cbd5e1;
    }
    
    /* Success/Error message styling */
    .stSuccess {
        background-color: #ecfdf5;
        border: 1px solid #10b981;
        border-radius: 8px;
    }
    
    .stError {
        background-color: #fef2f2;
        border: 1px solid #ef4444;
        border-radius: 8px;
    }
    
    .stInfo {
        background-color: #eff6ff;
        border: 1px solid #3b82f6;
        border-radius: 8px;
    }
    
    /* Download button styling */
    .stDownloadButton > button {
        background: linear-gradient(135deg, #7c3aed, #a855f7);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 0.5rem 1rem;
        font-weight: 500;
    }
</style>
""", unsafe_allow_html=True)

# Sidebar with filters
# with st.sidebar:
#     st.markdown("### 🎯 Advanced Filters")
    
#     price_range = st.selectbox("💰 Price Range", [
#         "Any", "Under 50,000", "50,000 - 100,000", "100,000 - 200,000", 
#         "200,000 - 500,000", "Above 500,000"
#     ])
    
#     property_type = st.multiselect("🏠 Property Type", [
#         "Apartment", "Villa", "Studio", "Penthouse", "Townhouse", "Office"
#     ])
    
#     areas = st.multiselect("📍 Preferred Areas", [
#         "Dubai Marina", "Downtown Dubai", "Business Bay", "JLT", "DIFC", 
#         "Palm Jumeirah", "Arabian Ranches", "Motor City"
#     ])
    
#     bedrooms = st.selectbox("🛏️ Bedrooms", [
#         "Any", "Studio", "1 BR", "2 BR", "3 BR", "4 BR", "5+ BR"
#     ])

# Main header
st.markdown("""
<div class="main-header">
    <h1>Property Seek </h1>
    <p>Search properties • AI Assistant • Real-time Results</p>
</div>
""", unsafe_allow_html=True)

col1, col2 = st.columns([4, 1])
with col1:
    query = st.text_input(
        "🔎 Enter your property search query:",
        placeholder="Try: '2 bedroom villa in Dubai Marina' or 'affordable apartments downtown'",
        key="search_input"
    )
with col2:
    st.markdown("<br>", unsafe_allow_html=True)  
    search_clicked = st.button("🚀 Search", use_container_width=True)

st.markdown("#### ⚡ Quick Searches")
col1, col2, col3, col4 = st.columns(4)

with col1:
    if st.button("🏢 Dubai Apartments", use_container_width=True):
        st.session_state.current_query = "apartments for rent in dubai"
        st.rerun()

with col2:
    if st.button("🏖️ Marina Villas", use_container_width=True):
        st.session_state.current_query = "villas in dubai marina"
        st.rerun()

with col3:
    if st.button("🏙️ Downtown Properties", use_container_width=True):
        st.session_state.current_query = "properties in downtown dubai"
        st.rerun()

with col4:
    if st.button("💼 Office Spaces", use_container_width=True):
        st.session_state.current_query = "office spaces for rent"
        st.rerun()

if 'current_query' in st.session_state:
    query = st.session_state.current_query
    del st.session_state.current_query
    
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
    st.session_state.search_history.append((timestamp, query))
    
    if len(st.session_state.search_history) > 10:
        st.session_state.search_history = st.session_state.search_history[-10:]

    with st.spinner("🔍 Searching properties..."):
        time.sleep(1)
        results = search_all_properties(query)
        st.session_state.last_results = results
    
    
    if not results:
        st.error("❌ No properties found matching your criteria. Try adjusting your search terms.")
    else:
        first_result = results[0]
        
        if first_result.get("source") == "AI Assistant":
            st.info(f"🤖 AI Assistant: {first_result['description']}")
        else:
            total_properties = len(results)
            st.success(f"🎉 Found {total_properties} properties matching your search!")

            sources_count = {}
            for prop in results:
                source = prop.get("source", "Unknown")
                sources_count[source] = sources_count.get(source, 0) + 1

            col1, col2, col3 = st.columns(3)
            with col1:
                st.markdown('<div class="metric-container">', unsafe_allow_html=True)
                st.metric("Total Properties", total_properties)
                st.markdown('</div>', unsafe_allow_html=True)
            
            with col2:
                st.markdown('<div class="metric-container">', unsafe_allow_html=True)
                st.metric("Property Finder", sources_count.get("Property Finder", 0))
                st.markdown('</div>', unsafe_allow_html=True)
            
            with col3:
                st.markdown('<div class="metric-container">', unsafe_allow_html=True)
                st.metric("Find Properties", sources_count.get("Find Properties", 0))
                st.markdown('</div>', unsafe_allow_html=True)

            if results:
                df = pd.DataFrame(results)
                csv_data = df.to_csv(index=False)
                st.download_button(
                    "📋 Download Results as CSV",
                    csv_data,
                    "property_search_results.csv",
                    "text/csv",
                    use_container_width=True
                )

            st.markdown("---")
            st.markdown("### 🏠 Property Listings")
            
            for prop in results:
                #st.markdown('<div class="property-card">', unsafe_allow_html=True)
                #st.markdown('<div class="property-card">')
                st.markdown(f'<div class="property-title">{prop["title"]}</div>', unsafe_allow_html=True)
                st.markdown(f'''
                <div class="property-details">
                    <span class="property-price">{prop["price"]}</span> • 
                    <span class="property-location">{prop["location"]}</span>
                </div>
                ''', unsafe_allow_html=True)
                
                if prop.get('link') and prop['link'] != '#':
                    st.markdown(f"🔗 [View Property Details]({prop['link']})")
                
                if prop.get('description'):
                    description = prop['description']
                    if len(description) > 200:
                        description = description[:200] + "..."
                    st.markdown(f"📝 **Description:** {description}")
                
                if prop.get('source'):
                    st.markdown(f"🏷️ **Source:** {prop['source']}")
                
                st.markdown('</div>', unsafe_allow_html=True)
                st.markdown("<br>", unsafe_allow_html=True)

if search_clicked and query:
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
    st.session_state.search_history.append((timestamp, query))
    
    if len(st.session_state.search_history) > 10:
        st.session_state.search_history = st.session_state.search_history[-10:]

    with st.spinner("🔍 Searching properties..."):
        time.sleep(1)  
        results = search_all_properties(query)
        st.session_state.last_results = results

    if not results:
        st.error("❌ No properties found matching your criteria. Try adjusting your search terms.")
    else:
        first_result = results[0]
        
        if first_result.get("source") == "AI Assistant":
            
            st.info(f"🤖 AI Assistant: {first_result['description']}")
        else:
        
            total_properties = len(results)
            st.success(f"🎉 Found {total_properties} properties matching your search!")

            
            sources_count = {}
            for prop in results:
                source = prop.get("source", "Unknown")
                sources_count[source] = sources_count.get(source, 0) + 1

            col1, col2, col3 = st.columns(3)
            with col1:
                st.markdown('<div class="metric-container">', unsafe_allow_html=True)
                st.metric("Total Properties", total_properties)
                st.markdown('</div>', unsafe_allow_html=True)
            
            with col2:
                st.markdown('<div class="metric-container">', unsafe_allow_html=True)
                st.metric("Property Finder", sources_count.get("Property Finder", 0))
                st.markdown('</div>', unsafe_allow_html=True)
            
            with col3:
                st.markdown('<div class="metric-container">', unsafe_allow_html=True)
                st.metric("Find Properties", sources_count.get("Find Properties", 0))
                st.markdown('</div>', unsafe_allow_html=True)

            if results:
                df = pd.DataFrame(results)
                csv_data = df.to_csv(index=False)
                st.download_button(
                    "📋 Download Results as CSV",
                    csv_data,
                    "property_search_results.csv",
                    "text/csv",
                    use_container_width=True
                )

            st.markdown("---")
            st.markdown("### 🏠 Property Listings")
            
            for prop in results:
                st.markdown('<div class="property-card">', unsafe_allow_html=True)
                
                st.markdown(f'<div class="property-title">{prop["title"]}</div>', unsafe_allow_html=True)
                
                st.markdown(f'''
                <div class="property-details">
                    <span class="property-price">{prop["price"]}</span> • 
                    <span class="property-location">{prop["location"]}</span>
                </div>
                ''', unsafe_allow_html=True)
                
                if prop.get('link') and prop['link'] != '#':
                    st.markdown(f"🔗 [View Property Details]({prop['link']})")
                
                if prop.get('description'):
                    description = prop['description']
                    if len(description) > 200:
                        description = description[:200] + "..."
                    st.markdown(f"📝 **Description:** {description}")
            
                if prop.get('source'):
                    st.markdown(f"🏷️ **Source:** {prop['source']}")
                
                st.markdown('</div>', unsafe_allow_html=True)
                st.markdown("<br>", unsafe_allow_html=True)

elif search_clicked:
    st.warning("⚠️ Please enter a search query to find properties")

# Search history section
# if st.session_state.search_history:
#     with st.expander("📜 Recent Searches"):
#         for timestamp, search_query in reversed(st.session_state.search_history):
#             st.text(f"{timestamp} - {search_query}")


st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #6b7280; padding: 1rem;">
    Property Seek Pro • Powered by AI • Find your perfect property
</div>
""", unsafe_allow_html=True)