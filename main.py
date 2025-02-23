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
        'image_urls': [],
        'characters': [],
        'gdd': ''
    }

# Sidebar for API keys and settings
def setup_sidebar():
    st.sidebar.title("🔑 API Keys and Settings")
    
    # Select text generation provider; default now set to DeepSeek
    provider = st.sidebar.selectbox(
        "Select Text Generation Provider", 
        ["DeepSeek", "OpenAI"],
        index=0  # Default to DeepSeek
    )
    
    # API key inputs based on provider
    if provider == "DeepSeek":
        deepseek_api_key = st.sidebar.text_input("Enter your DeepSeek API Key", type="password")
        openai_api_key = None
    else:
        openai_api_key = st.sidebar.text_input("Enter your OpenAI API Key", type="password")
        deepseek_api_key = None

    replicate_api_key = st.sidebar.text_input("Enter your Replicate API Key", type="password")
    
    # Dropdown for image generation model selection
    img_model_choice = st.sidebar.selectbox(
        "Select Image Generation Model",
        ["ByteDance SDXL Lightning 4Step", "Any ComfyUI Workflow"],
        index=0
    )
    if img_model_choice == "ByteDance SDXL Lightning 4Step":
        image_model_id = "bytedance/sdxl-lightning-4step:5599ed30703defd1d160a25a63321b4dec97101d98b4674bcc56e41f62f35637"
    else:
        image_model_id = "any-comfyui-workflow:ac793ee8fe34411d9cb3b0b3138152b6da8f7ebd178defaebe4b910ea3b16703"
        
    st.sidebar.markdown("""
    ### 🚀 Getting Started
    Provide details about your dream game.
    """)
    
    return provider, openai_api_key, replicate_api_key, deepseek_api_key, image_model_id

# Check text API connection
def check_text_api_connection(provider, api_key, deepseek_api_key):
    if provider == "OpenAI":
        try:
            openai.api_key = api_key
            openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": "Test connection"}],
                max_tokens=5
            )
            return True
        except Exception as e:
            st.error(f"OpenAI API connection failed: {e}")
            return False
    elif provider == "DeepSeek":
        try:
            # Placeholder test call for DeepSeek
            return True
        except Exception as e:
            st.error(f"DeepSeek API connection failed: {e}")
            return False

# Check image API connection
def check_image_api_connection(replicate_api_key, image_model_id):
    try:
        os.environ["REPLICATE_API_TOKEN"] = replicate_api_key
        replicate.run(
            image_model_id,
            input={"prompt": "Test connection", "num_outputs": 1}
        )
        return True
    except Exception as e:
        st.error(f"Replicate API connection failed: {e}")
        return False

# Main UI
def setup_main_ui():
    st.title("🎮 AI-Powered Game Design Studio")
    st.markdown("Welcome! Share your game ideas and get a complete concept.")

# Collect game details from the user
def get_game_details():
    st.subheader("📝 Game Details")
    col1, col2 = st.columns(2)
    with col1:
        vibe = st.selectbox("Game Vibe", [
            "Epic fantasy with dragons",
            "Post-apocalyptic wasteland",
            "Cyberpunk city",
            "Medieval kingdom",
            "Space exploration"
        ])
        genre = st.selectbox("Genre", [
            "RPG", "Action", "Adventure", "Puzzle",
            "Strategy", "Simulation", "Platform", "Horror"
        ])
        audience = st.selectbox("Audience", [
            "Young Adults (18-25)", "Adults (26+)", "All Ages"
        ])
        perspective = st.selectbox("Perspective", [
            "First Person", "Third Person", "Top Down", "Side View", "Isometric"
        ])
        multiplayer = st.selectbox("Multiplayer", [
            "Single Player", "Local Co-op", "Online Multiplayer", "Both Local and Online"
        ])
    with col2:
        goal = st.selectbox("Game Goal", [
            "Save the kingdom from eternal winter",
            "Defeat the evil empire",
            "Explore uncharted planets",
            "Build and manage a thriving city",
            "Survive in a post-apocalyptic world",
            "Solve ancient mysteries",
            "Become the greatest hero of all time"
        ])
        art_style = st.selectbox("Art Style", [
            "Realistic", "Cartoon", "Pixel Art", "Stylized", "Low Poly", "Anime", "Hand-drawn"
        ])
        platforms = st.multiselect("Platforms", [
            "PC", "Mobile", "PlayStation", "Xbox", "Nintendo Switch", "Web Browser"
        ])
        dev_time = st.slider("Development Time (months)", 1, 36, 12)
        num_stages = st.number_input("Number of Stages/Levels", min_value=1, max_value=20, value=8)
    st.subheader("🎨 Additional Preferences")
    col3, col4 = st.columns(2)
    with col3:
        mechanics = st.multiselect("Core Mechanics", [
            "Combat", "Exploration", "Puzzle Solving", "Resource Management",
            "Base Building", "Stealth", "Racing", "Crafting"
        ])
        mood = st.multiselect("Mood/Atmosphere", [
            "Epic", "Mysterious", "Peaceful", "Tense", "Humorous",
            "Dark", "Whimsical", "Scary"
        ])
    with col4:
        inspirations = st.text_area("Inspirations (comma-separated)", "")
        unique_features = st.text_area("Unique Features", "")
    detail_level = st.selectbox("Detail Level", ["Low", "Medium", "High"])
    
    return {
        "vibe": vibe,
        "genre": genre,
        "goal": goal,
        "audience": audience,
        "perspective": perspective,
        "multiplayer": multiplayer,
        "art_style": art_style,
        "platforms": platforms,
        "dev_time": dev_time,
        "num_stages": num_stages,
        "mechanics": mechanics,
        "mood": mood,
        "inspirations": inspirations,
        "unique_features": unique_features,
        "detail_level": detail_level
    }

# Text generation functions
def generate_with_openai(prompt, api_key):
    try:
        openai.api_key = api_key
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=1000
        )
        return response.choices[0].message['content']
    except Exception as e:
        st.error(f"OpenAI text generation failed: {e}")
        return f"Fallback Text for prompt: {prompt}"

def generate_with_deepseek(prompt, api_key):
    # DeepSeek placeholder function; in production replace with actual API call.
    return f"DeepSeek response for: {prompt}"

# Image generation function
def generate_image_with_replicate(prompt, api_key, image_model_id):
    try:
        os.environ["REPLICATE_API_TOKEN"] = api_key
        output = replicate.run(
            image_model_id,
            input={
                "prompt": prompt,
                "num_outputs": 1,
                "width": 1024,
                "height": 1024,
                "scheduler": "K_EULER",
                "num_inference_steps": 4
            }
        )
        return output[0]
    except Exception as e:
        st.error(f"Image generation failed: {e}")
        return f"Stage Description: {prompt}"

# Display image (or fallback text)
def display_image(image_data):
    if image_data.startswith("http"):
        try:
            response = requests.get(image_data)
            response.raise_for_status()
            img = Image.open(BytesIO(response.content))
            st.image(img, caption="Generated Game Art")
        except Exception as e:
            st.error(f"Failed to load image: {e}")
    else:
        st.markdown(f"**{image_data}**")

# Main function
def main():
    provider, openai_api_key, replicate_api_key, deepseek_api_key, image_model_id = setup_sidebar()
    setup_main_ui()
    inputs = get_game_details()
    
    if st.sidebar.button("🔍 Check API Connections"):
        text_connected = check_text_api_connection(provider, openai_api_key, deepseek_api_key)
        image_connected = check_image_api_connection(replicate_api_key, image_model_id)
        if text_connected:
            st.sidebar.success("✅ Text API Connected")
        else:
            st.sidebar.error("❌ Text API Not Connected")
        if image_connected:
            st.sidebar.success("✅ Image API Connected")
        else:
            st.sidebar.error("❌ Image API Not Connected")
            
    if st.button("🚀 Generate Game Concept"):
        with st.spinner("Generating your game concept..."):
            # Generate Story
            prompt_story = f"""Create a game concept with:
- Vibe: {inputs['vibe']}
- Genre: {inputs['genre']}
- Goal: {inputs['goal']}
- Audience: {inputs['audience']}
- Perspective: {inputs['perspective']}
- Multiplayer: {inputs['multiplayer']}
- Art Style: {inputs['art_style']}
- Platforms: {', '.join(inputs['platforms'])}
- Development Time: {inputs['dev_time']} months
- Number of Stages: {inputs['num_stages']}
- Mechanics: {', '.join(inputs['mechanics'])}
- Mood: {', '.join(inputs['mood'])}
- Inspirations: {inputs['inspirations']}
- Unique Features: {inputs['unique_features']}
- Detail Level: {inputs['detail_level']}
"""
            if provider == "OpenAI":
                story_text = generate_with_openai(prompt_story, openai_api_key)
            else:
                story_text = generate_with_deepseek(prompt_story, deepseek_api_key)
            st.session_state.output['story'] = story_text
            
            # Generate images for game levels
            stage_images = []
            for i in range(inputs['num_stages']):
                prompt_stage = f"{inputs['vibe']}, {inputs['art_style']}, {', '.join(inputs['mood'])}, Level {i+1}"
                stage_img = generate_image_with_replicate(prompt_stage, replicate_api_key, image_model_id)
                stage_images.append(stage_img)
            st.session_state.output['image_urls'] = stage_images
            
            # Generate main character descriptions
            characters = []
            for i in range(3):
                prompt_char = f"Create a main character for a {inputs['genre']} game with a {inputs['vibe']} vibe."
                if provider == "OpenAI":
                    char_text = generate_with_openai(prompt_char, openai_api_key)
                else:
                    char_text = generate_with_deepseek(prompt_char, deepseek_api_key)
                characters.append(char_text)
            st.session_state.output['characters'] = characters
            
            # Generate Game Design Document (GDD)
            prompt_gdd = f"Create a Game Design Document (GDD) for a {inputs['genre']} game with a {inputs['vibe']} vibe."
            if provider == "OpenAI":
                gdd_text = generate_with_openai(prompt_gdd, openai_api_key)
            else:
                gdd_text = generate_with_deepseek(prompt_gdd, deepseek_api_key)
            st.session_state.output['gdd'] = gdd_text
        
        st.success("Game concept generated!")
        
        tab1, tab2, tab3, tab4 = st.tabs(["Story Design", "Game Levels", "Main Characters", "GDD"])
        with tab1:
            st.subheader("📖 Story Design")
            st.markdown(st.session_state.output['story'] or "No story generated.")
        with tab2:
            st.subheader("🎮 Game Levels")
            for idx, img_data in enumerate(st.session_state.output['image_urls']):
                st.markdown(f"### Level {idx+1}")
                display_image(img_data)
        with tab3:
            st.subheader("👤 Main Characters")
            for idx, char_text in enumerate(st.session_state.output['characters']):
                st.markdown(f"### Character {idx+1}")
                st.markdown(char_text)
        with tab4:
            st.subheader("📄 Game Design Document (GDD)")
            st.markdown(st.session_state.output['gdd'] or "No GDD generated.")

if __name__ == "__main__":
    main()
