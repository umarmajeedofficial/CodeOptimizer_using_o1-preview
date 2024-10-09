import streamlit as st
from together import Together
from openai import OpenAI

# Initialize the clients for the models with API keys from Streamlit secrets
together_client = Together(base_url="https://api.aimlapi.com/v1", api_key=st.secrets["together"]["api_key"])
openai_client = OpenAI(api_key=st.secrets["openai"]["api_key"], base_url="https://api.aimlapi.com")

# Function to generate code based on user question
def generate_code(messages, language):
    # Step 1: Use Llama model to process the conversation
    response = together_client.chat.completions.create(
        model="meta-llama/Llama-3.2-11B-Vision-Instruct-Turbo",
        messages=messages,
        max_tokens=10000,
    )
    
    llama_response = response.choices[0].message.content.strip()
    
    # Remove quotes and make it a single string
    processed_string = llama_response.replace('"', '').replace("'", '').replace('\n', ' ')

    # Step 2: Use OpenAI o1 model to generate optimized code
    instruction = (
        f"As a highly skilled software engineer, please analyze the following question thoroughly and provide optimized "
        f"{language} code for the problem: {processed_string}. Make sure to give only code."
    )
    
    openai_response = openai_client.chat.completions.create(
        model="o1-preview",
        messages=[
            {
                "role": "user",
                "content": instruction
            },
        ],
        max_tokens=10000,
    )

    code = openai_response.choices[0].message.content.strip()
    return code

# Function to explain the generated code
def explain_code(code):
    instruction = (
        f"As a highly skilled software engineer, please provide a detailed line-by-line explanation of the following code:\n\n"
        f"{code}\n\nMake sure to explain what each line does and why it is used."
    )
    
    openai_response = openai_client.chat.completions.create(
        model="o1-preview",
        messages=[
            {
                "role": "user",
                "content": instruction
            }
        ],
        max_tokens=10000,
    )

    explanation = openai_response.choices[0].message.content.strip()
    return explanation

# Dropdown menu for programming languages
languages = ["Python", "Java", "C++", "JavaScript", "Go", "Ruby", "Swift"]

# Create the Streamlit interface
st.set_page_config(page_title="Optimized Code Generator", layout="wide")

# Create a sidebar layout for inputs
st.sidebar.title("Input Section")

# Button to start a new chat at the top of the sidebar
if st.sidebar.button("Start New Chat"):
    # Clear the chat history and input field
    st.session_state.messages = []  
    st.session_state.user_question = ""  # Clear the input field

# Sidebar inputs
language = st.sidebar.selectbox("Select Programming Language:", options=languages, index=0)

# Create a session state to maintain chat history
if "messages" not in st.session_state:
    st.session_state.messages = []
if "user_question" not in st.session_state:
    st.session_state.user_question = ""  # Initialize user_question state

# Main area for generated code and question input
st.subheader("Chat History:")
chat_container = st.empty()  # Placeholder for chat history

# Display chat messages
for msg in st.session_state.messages:
    st.markdown(f"**{msg['role'].capitalize()}:** {msg['content']}")

# Create a container for user input
with st.container():
    # User input field
    user_question = st.text_area("Enter your question:", 
                                  value=st.session_state.user_question, 
                                  placeholder="Type your question here...", 
                                  height=150)

    # Update session state when user types
    if user_question != st.session_state.user_question:
        st.session_state.user_question = user_question
    
    # Submit button to send the question
    if st.button("Submit"):
        # Add user's message to session state
        st.session_state.messages.append({"role": "user", "content": user_question})
        
        with st.spinner("Thinking..."):
            # Generate code and explanation
            code = generate_code(st.session_state.messages, language)
            explanation = explain_code(code)
            
            # Add model responses to session state
            st.session_state.messages.append({"role": "assistant", "content": code})
            st.session_state.messages.append({"role": "assistant", "content": explanation})
        
        # Clear the input field after submission
        st.session_state.user_question = ""  # Clear the input after submitting
        # Update chat history display
        chat_container.empty()  # Clear previous chat
        for msg in st.session_state.messages:
            st.markdown(f"**{msg['role'].capitalize()}:** {msg['content']}")

# Custom CSS to enhance the UI
st.markdown("""
<style>
    .streamlit-expanderHeader {
        font-size: 18px;
        font-weight: bold;
    }
    .stButton>button {
        background-color: #4CAF50; /* Green */
        color: white;
        border: none;
        border-radius: 5px;
        padding: 10px 20px;
        text-align: center;
        text-decoration: none;
        display: inline-block;
        font-size: 16px;
        margin: 4px 2px;
        cursor: pointer;
    }
    .stTextInput, .stSelectbox, .stTextArea {
        width: 100%;
        border-radius: 5px;
        padding: 10px;
        margin-bottom: 10px;
    }
</style>
""", unsafe_allow_html=True)
