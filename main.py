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
        'image_urls': [],
        'characters': [],
        'stages': [],
        'gdd': ''
    }

# Sidebar for API keys and provider selection
def setup_sidebar():
    st.sidebar.title("🔑 API Keys")
    
    # Dropdown to select OpenAI or DeepSeek
    provider = st.sidebar.selectbox(
        "Select Text Generation Provider",
        ["DeepSeek", "OpenAI"],
        index=0  # Default to DeepSeek
    )
    
    # API key inputs
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

# Check API connection for text generation
def check_text_api_connection(provider, api_key):
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
            # Replace with an actual DeepSeek test call if available
            return True
        except Exception as e:
            st.error(f"DeepSeek API connection failed: {e}")
            return False
    return False

# Check API connection for image generation
def check_image_api_connection(replicate_api_key):
    try:
        os.environ["REPLICATE_API_TOKEN"] = replicate_api_key
        replicate.run(
            "bytedance/sdxl-lightning-4step:5599ed30703defd1d160a25a63321b4dec97101d98b4674bcc56e41f62f35637",
            input={"prompt": "Test connection", "num_outputs": 1}
        )
        return True
    except Exception as e:
        st.error(f"Replicate API connection failed: {e}")
        return False

# Main app UI
def setup_main_ui():
    st.title("🎮 AI-Powered Game Design Studio")
    st.markdown("""
    Welcome to your AI-powered game design studio! Share your ideas, and our team of AI specialists will craft a detailed game concept for you.
    """)

# Collect user inputs
def get_game_details():
    st.subheader("📝 Game Details")
    col1, col2 = st.columns(2)

    with col1:
        vibe = st.selectbox(
            "Game Vibe",
            ["Epic fantasy with dragons", "Post-apocalyptic wasteland", "Cyberpunk city", "Medieval kingdom", "Space exploration"]
        )
        genre = st.selectbox("Genre", ["RPG", "Action", "Adventure", "Puzzle", "Strategy", "Simulation", "Platform", "Horror"])
        audience = st.selectbox("Audience", ["Teens (13-17)", "Young Adults (18-25)", "Adults (26+)", "All Ages"])
        perspective = st.selectbox("Perspective", ["First Person", "Third Person", "Top Down", "Side View", "Isometric"])
        multiplayer = st.selectbox("Multiplayer", ["Single Player", "Local Co-op", "Online Multiplayer", "Both Local and Online"])

    with col2:
        goal = st.selectbox(
            "Game Goal",
            [
                "Save the kingdom from eternal winter",
                "Defeat the evil empire",
                "Explore uncharted planets",
                "Build and manage a thriving city",
                "Survive in a post-apocalyptic world",
                "Solve ancient mysteries",
                "Become the greatest hero of all time"
            ]
        )
        art_style = st.selectbox("Art Style", ["Realistic", "Cartoon", "Pixel Art", "Stylized", "Low Poly", "Anime", "Hand-drawn"])
        platforms = st.multiselect("Platforms", ["PC", "Mobile", "PlayStation", "Xbox", "Nintendo Switch", "Web Browser"])
        dev_time = st.slider("Development Time (months)", 1, 36, 12)
        num_stages = st.number_input("Number of Stages/Levels", min_value=1, max_value=20, value=8)

    st.subheader("🎨 Additional Preferences")
    col3, col4 = st.columns(2)

    with col3:
        mechanics = st.multiselect(
            "Core Mechanics",
            ["Combat", "Exploration", "Puzzle Solving", "Resource Management", "Base Building", "Stealth", "Racing", "Crafting"]
        )
        mood = st.multiselect(
            "Mood/Atmosphere",
            ["Epic", "Mysterious", "Peaceful", "Tense", "Humorous", "Dark", "Whimsical", "Scary"]
        )

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

# Generate text using OpenAI
def generate_with_openai(prompt, api_key):
    openai.api_key = api_key
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=1000
    )
    return response.choices[0].message['content']

# Generate text using DeepSeek
def generate_with_deepseek(prompt, api_key):
    # Replace with actual DeepSeek API call
    return f"DeepSeek response for: {prompt}"

# Generate image using Replicate (ByteDance SDXL-Lightning-4Step)
def generate_image_with_replicate(prompt, api_key):
    try:
        os.environ["REPLICATE_API_TOKEN"] = api_key
        output = replicate.run(
            "bytedance/sdxl-lightning-4step:5599ed30703defd1d160a25a63321b4dec97101d98b4674bcc56e41f62f35637",
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
        return None

# Validate and display the image
def display_image(image_url):
    if image_url is None:
        st.error("No image URL provided.")
        return
    try:
        response = requests.get(image_url)
        response.raise_for_status()  # Raise an error for bad responses
        image = Image.open(BytesIO(response.content))
        st.image(image, caption="Generated Game Art")
    except Exception as e:
        st.error(f"Failed to load image: {e}")

# Main function
def main():
    provider, openai_api_key, replicate_api_key, deepseek_api_key = setup_sidebar()
    setup_main_ui()
    inputs = get_game_details()

    # API Check Button
    if st.sidebar.button("🔍 Check API Connections"):
        text_api_connected = check_text_api_connection(provider, openai_api_key if provider == "OpenAI" else deepseek_api_key)
        image_api_connected = check_image_api_connection(replicate_api_key)
        if text_api_connected:
            st.sidebar.success("✅ Text API Connected")
        else:
            st.sidebar.error("❌ Text API Not Connected")
        if image_api_connected:
            st.sidebar.success("✅ Image API Connected")
        else:
            st.sidebar.error("❌ Image API Not Connected")

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
            - Number of Stages: {inputs['num_stages']}
            - Mechanics: {', '.join(inputs['mechanics'])}
            - Mood: {', '.join(inputs['mood'])}
            - Inspirations: {inputs['inspirations']}
            - Unique Features: {inputs['unique_features']}
            - Detail Level: {inputs['detail_level']}
            """
            if provider == "OpenAI":
                st.session_state.output['story'] = generate_with_openai(prompt, openai_api_key)
            else:
                st.session_state.output['story'] = generate_with_deepseek(prompt, deepseek_api_key)

            # Generate images for game levels
            st.session_state.output['image_urls'] = []
            for i in range(inputs['num_stages']):
                image_prompt = f"{inputs['vibe']}, {inputs['art_style']}, {', '.join(inputs['mood'])}, Level {i+1}"
                image_url = generate_image_with_replicate(image_prompt, replicate_api_key)
                if image_url:
                    st.session_state.output['image_urls'].append(image_url)

            # Generate main character sheets
            st.session_state.output['characters'] = []
            for i in range(3):  # Generate 3 main characters
                character_prompt = f"Create a main character for a {inputs['genre']} game with a {inputs['vibe']} vibe."
                if provider == "OpenAI":
                    character_sheet = generate_with_openai(character_prompt, openai_api_key)
                else:
                    character_sheet = generate_with_deepseek(character_prompt, deepseek_api_key)
                st.session_state.output['characters'].append(character_sheet)

            # Generate Game Design Document (GDD)
            gdd_prompt = f"Create a Game Design Document (GDD) for a {inputs['genre']} game with a {inputs['vibe']} vibe."
            if provider == "OpenAI":
                st.session_state.output['gdd'] = generate_with_openai(gdd_prompt, openai_api_key)
            else:
                st.session_state.output['gdd'] = generate_with_deepseek(gdd_prompt, deepseek_api_key)

        st.success("🎉 Game concept generated successfully!")

        # Display outputs in tabs
        tab1, tab2, tab3, tab4 = st.tabs(["Story Design", "Game Levels", "Main Characters", "GDD"])

        with tab1:
            st.subheader("📖 Story Design")
            st.markdown(st.session_state.output['story'])

        with tab2:
            st.subheader("🎮 Game Levels")
            for i, image_url in enumerate(st.session_state.output['image_urls']):
                st.markdown(f"### Level {i+1}")
                display_image(image_url)

        with tab3:
            st.subheader("👤 Main Characters")
            for i, character_sheet in enumerate(st.session_state.output['characters']):
                st.markdown(f"### Character {i+1}")
                st.markdown(character_sheet)

        with tab4:
            st.subheader("📄 Game Design Document (GDD)")
            st.markdown(st.session_state.output['gdd'])

if __name__ == "__main__":
    main()
