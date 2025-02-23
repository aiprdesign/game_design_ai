import streamlit as st
import openai
import replicate
import os
import requests
from PIL import Image
from io import BytesIO

# Initialize session state
if 'output' not in st.session_state:
    st.session_state.output = {
        'story': '', 
        'gameplay': '', 
        'visuals': '', 
        'tech': '',
        'image_url': ''
    }

# Sidebar for API keys and provider selection
def setup_sidebar():
    st.sidebar.title("🔑 API Keys")
    
    provider = st.sidebar.selectbox(
        "Select Text Generation Provider",
        ["DeepSeek", "OpenAI"],
        index=0
    )
    
    if provider == "OpenAI":
        api_key = st.sidebar.text_input("Enter your OpenAI API Key", type="password")
        replicate_api_key = st.sidebar.text_input("Enter your Replicate API Key", type="password")
        deepseek_api_key = None
    else:
        deepseek_api_key = st.sidebar.text_input("Enter your DeepSeek API Key", type="password")
        replicate_api_key = st.sidebar.text_input("Enter your Replicate API Key", type="password")
        api_key = None

    st.sidebar.markdown("""
    ### 🚀 Getting Started
    Provide details about your dream game, and the AI team will create a concept for you. Think about:
    - **Setting and vibe**
    - **Gameplay mechanics**
    - **Art style and visuals**
    - **Technical requirements**
    """)
    return provider, api_key, replicate_api_key, deepseek_api_key

def display_image_safely(image_url):
    """Safely display an image from a URL in Streamlit"""
    try:
        response = requests.get(image_url)
        if response.status_code == 200:
            image = Image.open(BytesIO(response.content))
            st.image(image, caption="Generated Game Art")
        else:
            st.error(f"Failed to load image. Status code: {response.status_code}")
    except Exception as e:
        st.error(f"Error displaying image: {str(e)}")

# The rest of your functions remain the same until the main() function

def main():
    provider, openai_api_key, replicate_api_key, deepseek_api_key = setup_sidebar()
    setup_main_ui()
    inputs = get_game_details()

    # Check API connections
    text_api_connected = check_text_api_connection(provider, openai_api_key if provider == "OpenAI" else deepseek_api_key)
    image_api_connected = check_image_api_connection(replicate_api_key)

    # Display connection status
    if text_api_connected:
        st.sidebar.success("✅ Text API Connected")
    else:
        st.sidebar.error("❌ Text API Not Connected")

    if image_api_connected:
        st.sidebar.success("✅ Image API Connected")
    else:
        st.sidebar.error("❌ Image API Not Connected")

    if not text_api_connected or not image_api_connected:
        return

    if st.button("🚀 Generate Game Concept"):
        with st.spinner("🧠 AI team is brainstorming your game concept..."):
            # Generate game concept
            prompt = f"""
            Create a game concept with:
            - Vibe: {inputs['vibe']}
            - Genre: {inputs['genre']}
            - Goal: {inputs['goal']}
            - Audience: {inputs['audience']}
            - Perspective: {inputs['perspective']}
            - Multiplayer: {inputs['multiplayer']}
            - Art Style: {inputs['art_style']}
            - Platforms: {', '.join(inputs['platforms'])}
            - Development Time: {inputs['dev_time']} months
            - Budget: ${inputs['budget']:,}
            - Mechanics: {', '.join(inputs['mechanics'])}
            - Mood: {', '.join(inputs['mood'])}
            - Inspirations: {inputs['inspirations']}
            - Unique Features: {inputs['unique_features']}
            - Detail Level: {inputs['detail_level']}
            """
            
            try:
                if provider == "OpenAI":
                    st.session_state.output['story'] = generate_with_openai(prompt, openai_api_key)
                else:
                    st.session_state.output['story'] = generate_with_deepseek(prompt, deepseek_api_key)

                # Generate image using Replicate
                image_prompt = f"{inputs['vibe']}, {inputs['art_style']}, {inputs['mood']}"
                st.session_state.output['image_url'] = generate_image_with_replicate(image_prompt, replicate_api_key)
                
                st.success("🎉 Game concept generated successfully!")

                # Display outputs
                with st.expander("📖 Story Design"):
                    st.markdown(st.session_state.output['story'])

                with st.expander("🖼️ Generated Image"):
                    if st.session_state.output['image_url']:
                        display_image_safely(st.session_state.output['image_url'])
                    else:
                        st.error("Failed to generate image. Please check your Replicate API key.")
                        
            except Exception as e:
                st.error(f"An error occurred: {str(e)}")

if __name__ == "__main__":
    main()
