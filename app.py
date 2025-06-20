import os
import streamlit as st
from langchain_openai import ChatOpenAI
from langchain.schema import HumanMessage, SystemMessage
from langchain.callbacks.base import BaseCallbackHandler
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
default_api_key = os.getenv("SUTRA_API_KEY")


st.markdown(
    """
    <div style="text-align: center;">
        <h1 style="color: #4CAF50; font-size: 2.5em;">
            <img src="https://framerusercontent.com/images/9vH8BcjXKRcC5OrSfkohhSyDgX0.png" width="60" style="vertical-align: middle; margin-right: 10px;" />
        </h1>
    </div>
    """,
    unsafe_allow_html=True
)


# Supported languages with native scripts
languages = [
    "English", 
    "Hindi (हिन्दी)", 
    "Gujarati (ગુજરાતી)", 
    "Bengali (বাংলা)", 
    "Tamil (தமிழ்)", 
    "Telugu (తెలుగు)", 
    "Kannada (ಕನ್ನಡ)", 
    "Malayalam (മലയാളം)", 
    "Punjabi (ਪੰਜਾਬੀ)", 
    "Marathi (मराठी)", 
    "Urdu (اردو)",
    "Assamese (অসমীয়া)", 
    "Odia (ଓଡ଼ିଆ)"
]

# Detailed agricultural categories
ag_categories = {
    "🌱 Crop Management": [
        "Seed selection and sowing", "Crop rotation practices", "Intercropping techniques",
        "Plant spacing guidelines", "Harvesting best practices"
    ],
    "💧 Irrigation": [
        "Drip irrigation setup", "Sprinkler systems", "Water conservation methods",
        "Watering schedules", "Rainwater harvesting"
    ],
    "🐛 Pest Management": [
        "Organic pest control", "Common pest identification", "Integrated pest management",
        "Natural predators", "Preventive measures"
    ],
    "🌿 Organic Farming": [
        "Compost preparation", "Natural fertilizers", "Organic certification",
        "Crop rotation for organic farms", "Soil health management"
    ],
    "🧪 Soil Health": [
        "Soil testing methods", "pH balancing", "Nutrient management",
        "Soil conservation", "Fertilizer selection"
    ],
    "💲 Farm Economics": [
        "Cost reduction strategies", "Market rates information", "Government schemes",
        "Crop insurance", "Marketing strategies"
    ],
    "🚜 Farm Equipment": [
        "Equipment selection", "Maintenance tips", "Modern farming tools",
        "Cost-effective alternatives", "Equipment sharing models"
    ],
    "🌧️ Weather Advisory": [
        "Seasonal forecasts", "Weather-based planting", "Drought management",
        "Flood preparedness", "Climate-resilient farming"
    ]
}

# Streaming callback handler
class StreamHandler(BaseCallbackHandler):
    def __init__(self, container, initial_text=""):
        self.container = container
        self.text = initial_text

    def on_llm_new_token(self, token: str, **kwargs):
        self.text += token
        self.container.markdown(self.text)

# Sidebar
st.sidebar.image(
    "https://blog.agribegri.com/public/blog_images/smart-farming-the-power-of-ai-in-modern-farming-600x400.JPG",
    use_container_width=True
)

with st.sidebar:
    st.title("🌾 Krishi Mitra (कृषि मित्र)")
    
    # API Key Input
    st.markdown("### 🔑 API Key")
    api_input = st.text_input(
        "Enter your SUTRA API Key:",
        value=default_api_key or "",
        type="password",
        help="Paste your SUTRA API key here. You can get one from the link below."
    )
    api_key = api_input or default_api_key

    st.markdown(
        "<small>🔗 <a href='https://www.two.ai/sutra/api' target='_blank'>Get your free SUTRA API key here</a></small>",
        unsafe_allow_html=True
    )

    st.divider()
    selected_language = st.selectbox("Select language / भाषा चुनें:", languages)
    selected_language_simple = selected_language.split(" ")[0]
    
    selected_main_category = st.selectbox("Select Category / श्रेणी चुनें:", list(ag_categories.keys()))
    selected_subcategory = st.selectbox("Select Specific Topic / विशिष्ट विषय चुनें:", ag_categories[selected_main_category])
    
    st.divider()

    with st.expander("Advanced Options / उन्नत विकल्प", expanded=False):
        response_length = st.slider(
            "Response Detail Level / विस्तार स्तर",
            min_value=1, max_value=5, value=3,
            help="1: Very brief, 5: Very detailed"
        )
        include_local_practices = st.checkbox(
            "Include local farming practices / स्थानीय कृषि प्रथाओं को शामिल करें", value=True
        )
        include_scientific_info = st.checkbox(
            "Include scientific information / वैज्ञानिक जानकारी शामिल करें", value=True
        )

    st.divider()

    st.markdown(
        f"""
        <div style='background-color: rgba(76, 175, 80, 0.2); padding: 10px; border-radius: 5px; border: 1px solid #4CAF50;'>
            <p style='color: #FFFFFF; margin: 0;'>🗣️ <b>Language:</b> {selected_language}</p>
            <p style='color: #FFFFFF; margin: 0;'>📚 <b>Topic:</b> {selected_subcategory}</p>
        </div>
        """,
        unsafe_allow_html=True
    )

# Header
st.markdown(
    f'<h1 style="color: #4CAF50;"><img src="https://framerusercontent.com/images/9vH8BcjXKRcC5OrSfkohhSyDgX0.png" width="50"/> Krishi Mitra (कृषि मित्र)🌾🧑‍🌾</h1>',
    unsafe_allow_html=True
)

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])

# Chat input
chat_placeholder = f"Ask about {selected_subcategory}..."
user_input = st.chat_input(chat_placeholder)

# Base model instance cache
@st.cache_resource
def get_base_chat_model(api_key):
    return ChatOpenAI(
        api_key=api_key,
        base_url="https://api.two.ai/v2",
        model="sutra-v2",
        temperature=0.7,
    )

# Streaming model with callback
def get_streaming_chat_model(api_key, callback_handler=None):
    return ChatOpenAI(
        api_key=api_key,
        base_url="https://api.two.ai/v2",
        model="sutra-v2",
        temperature=0.7,
        streaming=True,
        callbacks=[callback_handler] if callback_handler else None
    )

# Handle user input
if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})
    
    with st.chat_message("user"):
        st.write(user_input)
    
    try:
        with st.chat_message("assistant"):
            response_placeholder = st.empty()
            stream_handler = StreamHandler(response_placeholder)
            chat = get_streaming_chat_model(api_key, stream_handler)

            system_message = f"""You are Krishi Mitra (कृषि मित्र), a specialized farming assistant for agricultural advice.
            The farmer is asking about: {selected_main_category} > {selected_subcategory}.

            Please provide:
            - {'Concise' if response_length <= 2 else 'Detailed' if response_length >= 4 else 'Balanced'} advice on the topic
            - {'Include traditional farming wisdom and local practices. ' if include_local_practices else ''}
            - {'Include scientific explanations and research-based information. ' if include_scientific_info else ''}
            - Practical, actionable steps the farmer can take
            - If discussing chemicals or treatments, always mention safety precautions
            - When appropriate, mention low-cost alternatives and sustainable practices
            - Format your response clearly with short paragraphs and bullet points for easy reading

            Please respond in {selected_language_simple}.
            """

            messages = [
                SystemMessage(content=system_message),
                HumanMessage(content=user_input)
            ]

            response = chat.invoke(messages)
            answer = response.content

            st.session_state.messages.append({"role": "assistant", "content": answer})
    
    except Exception as e:
        st.error(f"Error: {str(e)}")
        if "API key" in str(e):
            st.error("Please check your SUTRA API key in the environment variables or sidebar.")
