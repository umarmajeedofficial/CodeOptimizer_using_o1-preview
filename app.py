import streamlit as st
from together import Together
from openai import OpenAI

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

st.title("Optimized Code Generator")
st.subheader("Enter a programming question, select a programming language, and get optimized code with explanations.")

# Input fields
user_question = st.text_input("Enter your question:", placeholder="Type your question here...")
language = st.selectbox("Select Programming Language:", options=languages, index=0)

# Submit button
if st.button("Submit"):
    with st.spinner("Thinking..."):
        code = generate_code(user_question, language)
        explanation = explain_code(code)  # Get explanation using O1 model
        
        # Display the results
        st.subheader("Generated Code:")
        st.code(code, language=language.lower())
        
        st.subheader("Code Explanation:")
        st.text_area("Explanation:", value=explanation, height=200)

# Add some custom CSS to enhance UI
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
    .stTextInput, .stSelectbox {
        width: 100%;
        border-radius: 5px;
        padding: 10px;
        margin-bottom: 10px;
    }
</style>
""", unsafe_allow_html=True)

