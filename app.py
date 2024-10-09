import streamlit as st
from together import Together
from openai import OpenAI
from PIL import Image

# Initialize the clients for the models with API keys from Streamlit secrets
together_client = Together(base_url="https://api.aimlapi.com/v1", api_key=st.secrets["together"]["api_key"])
openai_client = OpenAI(api_key=st.secrets["openai"]["api_key"], base_url="https://api.aimlapi.com")

def generate_code(user_question, language):
    # Step 1: Use Llama model to get the processed question
    response = together_client.chat.completions.create(
        model="meta-llama/Llama-3.2-11B-Vision-Instruct-Turbo",
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": user_question,
                    }
                ],
            }
        ],
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

def explain_code(code):
    # Step 1: Use OpenAI o1 model to explain the generated code line by line
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

# Sidebar inputs
language = st.sidebar.selectbox("Select Programming Language:", options=languages, index=0)

# Main area for generated code
st.subheader("Generated Code:")
code_container = st.empty()  # Placeholder for generated code

# Container for the main content to enable scrolling
with st.container():
    # Add a spacer for layout adjustment
    st.write("")  # This adds a little space before the code output

    # Display the generated code
    code_display = code_container.code("", language="python")  # Initialize with empty code

    # Input field and submit button at the bottom
    user_question = st.text_area("Enter your question:", placeholder="Type your question here...", height=150, 
                                  max_chars=500)  # Set max characters if desired

    # Button to submit the question
    col1, col2 = st.columns([4, 1])  # Create two columns for the button
    with col1:
        # Reduce the width of the text area
        st.text_area(" ", value=user_question, height=150, placeholder="Type your question here...", key="input_area", max_chars=500)

    with col2:
        # Round button with icon (using a placeholder image for the icon)
        submit_button = st.button("", key="submit_button", help="Submit your question", 
                                   on_click=None)
        if submit_button:
            with st.spinner("Thinking..."):
                code = generate_code(user_question, language)
                explanation = explain_code(code)  # Get explanation using O1 model
                
                # Display the generated code and explanation
                code_container.code(code, language=language.lower())
                st.sidebar.text_area("Code Explanation:", value=explanation, height=200)

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
        border-radius: 50%; /* Make button round */
        padding: 10px 20px; /* Adjust padding for roundness */
        text-align: center;
        text-decoration: none;
        display: inline-block;
        font-size: 16px;
        margin: 4px 2px;
        cursor: pointer;
    }
    .stTextInput, .stSelectbox, .stTextArea {
        width: 80%; /* Shorter width for the input field */
        border-radius: 5px;
        padding: 10px;
        margin-bottom: 10px;
    }
</style>
""", unsafe_allow_html=True)

# Adding an icon to the button using an image
image = Image.open("path_to_your_icon.png")  # Replace with your icon image path
st.image(image, caption="", use_column_width=True)  # Display the icon above the button if needed
