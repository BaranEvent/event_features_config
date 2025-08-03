import streamlit as st
import json
import uuid
from typing import List, Dict, Any
from pyairtable import Api
from datetime import datetime
import urllib.parse

# Page configuration
st.set_page_config(
    page_title="Event Features Management",
    page_icon="⚙️",
    layout="wide"
)

# Initialize session state
if 'selected_features' not in st.session_state:
    st.session_state.selected_features = {}
if 'event_id' not in st.session_state:
    st.session_state.event_id = None
if 'redirect_url' not in st.session_state:
    st.session_state.redirect_url = None

# Airtable configuration
AIRTABLE_CONFIG = {
    "base_id": "applJyRTlJLvUEDJs",
    "api_key": "patJHZQyID8nmSaxh.1bcf08f100bd723fd85d67eff8534a19f951b75883d0e0ae4cc49743a9fb3131"
}

# Feature definitions
FEATURES = {
    "registration_form": {
        "name": "Kayıt Formu",
        "description": "Etkinliğiniz için özelleştirilebilir kayıt formu oluşturun. Katılımcıların bilgilerini toplayın ve yönetin.",
        "category": "before_event"
    }
    # Future features can be added here:
    # "live_polling": {
    #     "name": "Canlı Anket",
    #     "description": "Etkinlik sırasında katılımcılarla canlı anket yapın.",
    #     "category": "during_event"
    # },
    # "feedback_survey": {
    #     "name": "Geri Bildirim Anketi",
    #     "description": "Etkinlik sonrası katılımcılardan geri bildirim toplayın.",
    #     "category": "after_event"
    # }
}

def get_airtable_api():
    """Get Airtable API instance"""
    return Api(AIRTABLE_CONFIG["api_key"])

def get_airtable_table(table_name):
    """Get Airtable table instance"""
    api = get_airtable_api()
    return api.table(AIRTABLE_CONFIG["base_id"], table_name)

def load_event_features(event_id):
    """Load existing features for an event"""
    try:
        table = get_airtable_table("event_features")
        records = table.all(formula=f"{{event_id}} = {event_id}")
        
        features = {}
        for record in records:
            feature_key = record['fields'].get('feature_key', '')
            if feature_key:
                features[feature_key] = {
                    'id': record['id'],
                    'enabled': record['fields'].get('enabled', False)
                }
        
        return features
    except Exception as e:
        st.error(f"Özellikler yüklenirken hata oluştu: {str(e)}")
        return {}

def get_event_id_from_params():
    """Get event_id from URL parameters or default to 0"""
    try:
        # Try to get event_id from query parameters
        params = st.experimental_get_query_params()
        event_id = params.get("event_id", [None])[0]
        
        if event_id is not None:
            return int(event_id)
        else:
            return 0
    except:
        return 0

def redirect_to_hostquestions(event_id, feature_key):
    """Create redirect link to hostquestions.streamlit.app with event_id"""
    base_url = "https://hostquestions.streamlit.app"
    params = urllib.parse.urlencode({"event_id": event_id, "feature": feature_key})
    redirect_url = f"{base_url}?{params}"
    
    # Show the redirect link
    st.markdown(f"""
    <div style="text-align: center; padding: 20px; background-color: #f0f2f6; border-radius: 10px; margin: 20px 0;">
        <h3>Yapılandırma Sayfasına Yönlendiriliyorsunuz</h3>
        <p>Otomatik yönlendirme çalışmadıysa aşağıdaki linke tıklayın:</p>
        <a href="{redirect_url}" target="_blank" style="
            display: inline-block;
            background-color: #ff4b4b;
            color: white;
            padding: 10px 20px;
            text-decoration: none;
            border-radius: 5px;
            font-weight: bold;
        ">⚙️ Yapılandırma Sayfasını Aç</a>
    </div>
    """, unsafe_allow_html=True)
    
    # Try to redirect using JavaScript as fallback
    st.markdown(f"""
    <script>
        setTimeout(function() {{
            window.open('{redirect_url}', '_blank');
        }}, 1000);
    </script>
    """, unsafe_allow_html=True)

def render_feature_section(title, features, category, event_id):
    """Render a section of features"""
    st.header(f"📋 {title}")
    
    if not features:
        st.info("Bu kategoride henüz özellik bulunmuyor.")
        return
    
    for feature_key, feature_info in features.items():
        with st.container():
            st.markdown("---")
            
            col1, col2 = st.columns([1, 4])
            
            with col1:
                if st.button(
                    "⚙️ Yapılandır",
                    key=f"config_{feature_key}",
                    help=f"{feature_info['name']} özelliğini yapılandır"
                ):
                    redirect_to_hostquestions(event_id, feature_key)
            
            with col2:
                st.markdown(f"**{feature_info['name']}**")
                st.markdown(f"*{feature_info['description']}*")
                
                # Check if feature is enabled for this event
                existing_features = load_event_features(event_id)
                if feature_key in existing_features and existing_features[feature_key]['enabled']:
                    st.success("✅ Bu özellik etkinliğiniz için aktif")
                else:
                    st.info("ℹ️ Bu özellik henüz yapılandırılmamış")

def main():
    st.title("⚙️ Etkinlik Özellikleri Yönetimi")
    st.markdown("Etkinliğiniz için hangi özellikleri yapılandırmak istediğinizi seçin.")
    
    # Get event_id from parameters or default to 0
    event_id = get_event_id_from_params()
    
    if event_id == 0:
        st.warning("⚠️ Event ID belirtilmedi. Varsayılan olarak 0 kullanılıyor.")
    
    st.info(f"**Etkinlik ID:** {event_id}")
    
    # Load existing features
    existing_features = load_event_features(event_id)
    
    # Update session state with existing features
    for feature_key, feature_data in existing_features.items():
        st.session_state.selected_features[feature_key] = feature_data['enabled']
    
    st.markdown("---")
    
    # Before Event Features
    before_event_features = {k: v for k, v in FEATURES.items() if v['category'] == 'before_event'}
    render_feature_section("Etkinlik Öncesi Özellikler", before_event_features, "before_event", event_id)
    
    # During Event Features
    during_event_features = {k: v for k, v in FEATURES.items() if v['category'] == 'during_event'}
    render_feature_section("Etkinlik Sırası Özellikler", during_event_features, "during_event", event_id)
    
    # After Event Features
    after_event_features = {k: v for k, v in FEATURES.items() if v['category'] == 'after_event'}
    render_feature_section("Etkinlik Sonrası Özellikler", after_event_features, "after_event", event_id)
    
    # Summary
    st.markdown("---")
    st.header("📊 Özet")
    
    active_features = [k for k, v in existing_features.items() if v['enabled']]
    
    if active_features:
        st.success(f"**{len(active_features)}** özellik aktif:")
        for feature_key in active_features:
            if feature_key in FEATURES:
                st.markdown(f"• {FEATURES[feature_key]['name']}")
    else:
        st.warning("Henüz hiç özellik aktif edilmedi.")
    
    # Refresh button
    st.markdown("---")
    
    if st.button("🔄 Sayfayı Yenile", type="secondary", use_container_width=True):
        st.rerun()

if __name__ == "__main__":
    main() 