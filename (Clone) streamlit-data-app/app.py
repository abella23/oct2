import streamlit as st
from datetime import datetime
import streamlit.components.v1 as components

# ----------- CONFIG -----------
st.set_page_config(
    page_title="Aircraft Maintenance Chatbot",
    page_icon="✈️",
    layout="wide",
    initial_sidebar_state="expanded"
)

iframe_source = "https://adb-693586493268953.13.azuredatabricks.net/embed/dashboardsv3/01f09253e17f1fedaa4546b07320cd03?o=693586493268953&f_2507a927%7Eeea239d3=now%252Fy%7Enow%252Fy"

# ----------- THEME CSS -----------
st.markdown("""
    <style>
    :root {
        --sidebar-bg: #223536;
        --page-bg: #062721;
        --text-color: #F2F5F4;
        --accent-light: #EEE4DC;
        --accent-green: #14F279;
    }

    /* Global background */
    .stApp {
        background-color: var(--page-bg);
        color: var(--text-color);
    }

    /* Sidebar */
    [data-testid="stSidebar"] {
        background-color: var(--sidebar-bg);
        color: var(--text-color);
    }
    [data-testid="stSidebar"] .stButton > button {
        background-color: transparent;
        color: var(--text-color);
        border: none;
        text-align: left !important;
        justify-content: flex-start !important;
        width: 100%; 
        padding: 12px 16px;
        font-size: 16px;
    }
    [data-testid="stSidebar"] .stButton > button:hover,
    [data-testid="stSidebar"] .stExpander div[role="button"]:hover {
        background-color: var(--accent-green) !important;
        color: var(--page-bg) !important;
    }

    /* Expander headers */
    [data-testid="stSidebar"] .stExpander div[role="button"] {
        background-color: transparent !important;
        color: var(--text-color) !important;
        border: none !important;
        text-align: left !important;
        justify-content: flex-start !important;
        width: 100% !important;
        padding: 12px 16px !important;
        font-size: 16px !important;
    }

    /* Chat container */
    .chat-container {
        background-color: #223536;
        border-radius: 12px;
        padding: 24px;
        min-height: 500px;
        margin-top: 20px;
    }

    .chat-header h1 {
        color: var(--accent-green);
        font-size: 28px;
        font-weight: 600;
        margin-bottom: 12px;
    }
    .chat-header p {
        font-size: 16px;
        line-height: 1.6;
        color: var(--accent-light);
    }

    /* Messages */
    .stChatMessage {
        background-color: rgba(255, 255, 255, 0.05);
        border-radius: 12px;
        padding: 12px;
        margin: 8px 0;
        color: var(--text-color);
    }

    /* Input */
    .stChatInputContainer {
        background-color: rgba(255, 255, 255, 0.1);
        border-radius: 8px;
    }

    /* Disclaimer */
    .disclaimer {
        background-color: #223536;
        color: var(--accent-light);
        padding: 12px 16px;
        border-radius: 8px;
        margin-top: 20px;
        font-size: 13px;
        line-height: 1.4;
    }

    /* Footer */
    .footer {
        text-align: center; 
        color: #9ca3af; 
        font-size: 12px;
        margin-top: 40px;
    }
    </style>
""", unsafe_allow_html=True)

# ----------- SESSION STATE -----------
if 'page' not in st.session_state:
    st.session_state.page = 'home'
if 'messages' not in st.session_state:
    st.session_state.messages = []

# ----------- SIDEBAR -----------
with st.sidebar:
    if st.button("🏠 Home"):
        st.session_state.page = 'home'
        st.rerun()

    with st.expander("🤖 Chatbot"):
        if st.button("➤ New Chat"):
            st.session_state.page = 'chat'
            st.rerun()
        if st.button("➤ Chat History"):
            st.session_state.page = 'chat_history'
            st.rerun()

    with st.expander("📊 Reports"):
        if st.button("➤ All Reports"):
            st.session_state.page = 'all_reports'
            st.rerun()
        if st.button("➤ Genie Space"):
            st.session_state.page = 'genie_space'
            st.rerun()

    # Show "Chat with KAT" details only in chat-related pages
    if st.session_state.page in ['chat', 'chat_history']:
        st.markdown("<h2 style='text-align:center; color: var(--text-color); font-size: 24px;'>Chat with KAT</h2>", unsafe_allow_html=True)
        st.markdown("<p style='text-align:center;'>Your virtual assistant for aircraft maintenance</p>", unsafe_allow_html=True)
        st.markdown("<div style='text-align:center; font-size:20px;'>❓      📞      ✉️</div>", unsafe_allow_html=True)

# ----------- PAGES -----------
def render_home():
    st.markdown(
        """
        <div>
            <h1 style='text-align:center; color: var(--text-color); font-size: 48px;'>Home</h1>
        </div>
        """,
        unsafe_allow_html=True
    )
###################
### GLOBAL VARS ###
###################
# tail number is how we identify which of the demo chats
# We are currently serving
if "tail_number" not in st.session_state:
    st.session_state["tail_number"] = ""

# Chat offset allows for messages to be sent before entering demo sequence
if "chat_offset" not in st.session_state:
    st.session_state["chat_offset"] = 0

# Demo responses
if "backup_response" not in st.session_state:
    with open(asset_path + "dummy.json", "r") as f:
        backup_response = json.load(f)
    st.session_state["backup_response"] = backup_response

# Initialize session state variables
if "messages" not in st.session_state:
    st.session_state.messages = []

if "question" not in st.session_state:
    st.session_state.question = None

if "chat_history" not in st.session_state:
    st.session_state.chat_history = {}  # Dictionary to store chat sessions
    st.markdown(disable_scroll_css, unsafe_allow_html=True) # disabling scroll initially

if "selected_chat" not in st.session_state:
    st.session_state.selected_chat = None

if "chat_history_lc" not in st.session_state:
    st.session_state.chat_history_lc = []
    
#############
### UTILS ###
#############
def save_chat():
    """
    Currently saves a chat with the datetime as a key
    TODO - convert to tail number key, could be trouble with
    duplication
    """
    if st.session_state.messages:
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        st.session_state.chat_history[timestamp] = list(st.session_state.messages)

def demo_chat_gen(prompt):
    """
    Used for demo chats only

    The actual working function here would likely live somewhere else
    and this could be replaced with an API call to the LLM

    FLOW:
    1) Check for tail number
    2) if doesn't exist, say we couldn't find a tail number
    3) if does exist, check the demo chat and return appropriate response
    4) if does exist and nothing in demo chat, return response with technical difficulties message
    """
     # Plane for scenario 1
    if "N1560KG" in prompt.upper():
        st.session_state["tail_number"] = "N1560KG"
        st.session_state["chat_offset"] = len(st.session_state.messages)
    # Plane for scenario 2
    elif "N2770KG" in prompt.upper():
        st.session_state["tail_number"] = "N2770KG"
        st.session_state["chat_offset"] = len(st.session_state.messages)
    # Plane for scenario 3
    elif "N3609KG" in prompt.upper():
        st.session_state["tail_number"] = "N3609KG"
        st.session_state["chat_offset"] = len(st.session_state.messages)

    chat_pos = len(st.session_state["messages"]) - st.session_state["chat_offset"]
    tail_number = st.session_state["tail_number"]

    if tail_number not in ["N1560KG", "N2770KG", "N3609KG"]:
        return [
            f"Sorry we couldn't find a valid tail number in your message, please try again"
        ]
    else:
        try:
            time.sleep(1)
            return st.session_state["backup_response"][tail_number][str(chat_pos)]
        except KeyError:
            time.sleep(2)
            return [
                "I'm sorry but we're having technical diffculties, please refresh the page and try again"
            ]

def typewriter(text: str, speed: int):
    """
    Function to type out intro message character by character
    """
    tokens = text.split()
    container = st.empty()
    for index in range(len(tokens) + 1):
        curr_full_text = " ".join(tokens[:index])
        container.markdown(f"<p style='white-space: pre-wrap;'>{curr_full_text}</p>", unsafe_allow_html=True)
        time.sleep(1 / speed)
    return ("")

def initial_message():
    """
    TODO There is a bug here where this shows again after the first message sent
    """
    if not st.session_state.messages:
        st.session_state.messages.append({"role": "assistant", "content": "*Disclaimer: KAT is a support tool and not a substitute for certified guidance. Technicians must verify all information against the official maintenance manuals and follow established procedures, including consulting Maintenance Control when required*", "type": "text"})
initial_message()

# def render_chat():

#     # Header
#     st.markdown(
#         """
#         <div class='chat-header'>
#             <h1>Aircraft Maintenance Chatbot</h1>
#             <p>Hi, I’m KAT - your on-the-ground maintenance assistant.
#             I’m trained on Aircraft Maintenance Manuals to help you find procedures, troubleshooting steps, and systems info fast.
#             Tell me what you’re working on, and I’ll get you what you need.
#         </div>
#         """,
#         unsafe_allow_html=True
#     )

#     # Messages
#     for message in st.session_state.messages:
#         with st.chat_message(message["role"]):
#             st.markdown(message["content"])

#     # Input
#     if prompt := st.chat_input("Enter your question."):
#         st.session_state.messages.append({"role": "user", "content": prompt})
#         with st.chat_message("user"):
#             st.markdown(prompt)

#         response = (
#             "⚠️ Disclaimer: KAT is a support tool and not a substitute for certified guidance. "
#             "Technicians must verify all information against maintenance manuals and follow "
#             "established procedures, including consulting Maintenance Control when required."
#         )
#         st.session_state.messages.append({"role": "assistant", "content": response})
#         with st.chat_message("assistant"):
#             st.markdown(response)
#         st.rerun()

#     # Disclaimer
#     st.markdown(
#         """
#         <div class='disclaimer'>
#             ⚠️ <strong>Disclaimer:</strong> KAT is a support tool and not a substitute for certified guidance. 
#             Technicians must verify all information against maintenance manuals and follow established procedures, 
#             including consulting Maintenance Control when required.
#         </div>
#         """,
#         unsafe_allow_html=True
#     )
#     st.markdown("</div>", unsafe_allow_html=True)

def render_reports():
    st.markdown("<h1 style='text-align: center; color: var(--accent-light);'>All Reports</h1>", unsafe_allow_html=True)
    components.iframe(src=iframe_source, height=1000, scrolling=True)

# ----------- ROUTING -----------
if st.session_state.page == 'home':
    render_home()
elif st.session_state.page == 'chat':
    render_chat()
elif st.session_state.page == 'all_reports':
    render_reports()

# ----------- FOOTER -----------
st.markdown("<div class='footer'>Aircraft Maintenance Chatbot © 2025 - Powered by Kubrick</div>", unsafe_allow_html=True)


