import streamlit as st
import openai
import replicate
import os
import requests
from PIL import Image
from io import BytesIO
import time

# Initialize session state
if 'output' not in st.session_state:
    st.session_state.output = {
        'game_design': '',
        'characters': '',
        'world': '',
        'stages': [],
        'stage_images': [],
        'main_image_url': ''
    }

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
    Provide details about your dream game, and the AI team will create:
    - **Game Design Document**
    - **Character Sheets**
    - **World Design**
    - **Concept Art**
    """)
    return provider, api_key, replicate_api_key, deepseek_api_key

def setup_main_ui():
    st.title("🎮 AI-Powered Game Design Studio")
    st.markdown("""
    Welcome to your AI-powered game design studio! Share your vision, and our AI team will craft a detailed game design document with characters, world design, and concept art.
    """)

def get_game_details():
    st.subheader("📝 Game Details")
    col1, col2 = st.columns(2)

    with col1:
        vibe = st.selectbox(
            "Game Vibe",
            ["Epic fantasy with dragons", "Post-apocalyptic wasteland", "Cyberpunk city", "Medieval kingdom", "Space exploration"]
        )
        genre = st.selectbox("Genre", ["RPG", "Action", "Adventure", "Puzzle", "Strategy", "Simulation", "Platform", "Horror"])
        audience = st.selectbox("Audience", ["Kids (7-12)", "Teens (13-17)", "Young Adults (18-25)", "Adults (26+)", "All Ages"])
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

    st.subheader("👥 Character Development")
    protagonist_traits = st.multiselect(
        "Protagonist Traits",
        ["Brave", "Clever", "Strong", "Mysterious", "Resourceful", "Wise", "Quick-witted", "Determined"]
    )
    
    villain_type = st.selectbox(
        "Main Villain Type",
        ["Evil Overlord", "Corrupt Corporation", "Ancient Evil", "Rival Hero", "Natural Disaster", "AI Gone Rogue", "Hidden Conspiracy"]
    )
    
    num_bosses = st.slider("Number of Boss Encounters", 1, 10, 3)
    num_npcs = st.slider("Number of Key NPCs", 1, 20, 5)

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
        "mechanics": mechanics,
        "mood": mood,
        "inspirations": inspirations,
        "unique_features": unique_features,
        "protagonist_traits": protagonist_traits,
        "villain_type": villain_type,
        "num_bosses": num_bosses,
        "num_npcs": num_npcs,
        "detail_level": detail_level
    }

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
            st.error(f"OpenAI API connection failed: {str(e)}")
            return False
    elif provider == "DeepSeek":
        try:
            # Replace with actual DeepSeek API test
            return True
        except Exception as e:
            st.error(f"DeepSeek API connection failed: {str(e)}")
            return False
    return False

def check_image_api_connection(replicate_api_key):
    try:
        os.environ["REPLICATE_API_TOKEN"] = replicate_api_key
        replicate.run(
            "bytedance/sdxl-lightning-4step:5599ed30703defd1d160a25a63321b4dec97101d98b4674bcc56e41f62f35637",
            input={"prompt": "Test connection", "num_outputs": 1}
        )
        return True
    except Exception as e:
        st.error(f"Replicate API connection failed: {str(e)}")
        return False

def generate_with_openai(prompt, api_key):
    openai.api_key = api_key
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=2000
    )
    return response.choices[0].message['content']

def generate_with_deepseek(prompt, api_key):
    # This is a placeholder that returns structured sample data
    return """
    Stage 1: The Awakening
    Environment: Ancient ruins emerging from morning mist
    Challenges: Basic movement and core mechanics tutorial
    Mechanics: Introduction to basic abilities
    Boss: Training Guardian
    Rewards: First ability unlock
    Story: Player awakens to their destiny
    Atmosphere: Mysterious and peaceful

    Stage 2: The Valley of Trials
    Environment: Lush valley with ancient structures
    Challenges: First combat encounters
    Mechanics: Combat basics
    Boss: Valley Keeper
    Rewards: Combat ability
    Story: First major challenge
    Atmosphere: Serene but dangerous

    Stage 3: The Deep Caverns
    Environment: Underground crystal caves
    Challenges: Puzzle solving
    Mechanics: Special abilities
    Boss: Cave Dweller
    Rewards: New power
    Story: Ancient secrets revealed
    Atmosphere: Mysterious

    Stage 4: The Skybridge
    Environment: Floating islands
    Challenges: Platform navigation
    Mechanics: Advanced movement
    Boss: Wind Rider
    Rewards: Movement upgrade
    Story: World expansion
    Atmosphere: Breathtaking

    Stage 5: The Dark Forest
    Environment: Twisted woods
    Challenges: Stealth sections
    Mechanics: Stealth abilities
    Boss: Shadow Hunter
    Rewards: Stealth power
    Story: Dark revelation
    Atmosphere: Tense

    Stage 6: The Frozen Peak
    Environment: Snow-covered mountains
    Challenges: Survival mechanics
    Mechanics: Environmental interaction
    Boss: Frost Giant
    Rewards: Resistance ability
    Story: Major plot twist
    Atmosphere: Harsh

    Stage 7: The Burning City
    Environment: Ruined metropolis
    Challenges: Complex combat
    Mechanics: All abilities combined
    Boss: City Guardian
    Rewards: Ultimate power
    Story: Final revelation
    Atmosphere: Intense

    Stage 8: The Final Tower
    Environment: Reality-bending tower
    Challenges: Ultimate test
    Mechanics: Mastery required
    Boss: Final Boss
    Rewards: Story conclusion
    Story: Final battle
    Atmosphere: Epic
    """

def generate_image_with_replicate(prompt, api_key):
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

def display_image_safely(image_url, caption):
    try:
        response = requests.get(image_url)
        if response.status_code == 200:
            image = Image.open(BytesIO(response.content))
            st.image(image, caption=caption)
        else:
            st.error(f"Failed to load image. Status code: {response.status_code}")
    except Exception as e:
        st.error(f"Error displaying image: {str(e)}")

def parse_stages(stages_text):
    stages = []
    current_stage = {}
    
    for line in stages_text.strip().split('\n'):
        line = line.strip()
        if not line:
            continue
            
        if line.startswith('Stage'):
            if current_stage:
                stages.append(current_stage)
            current_stage = {'name': line.split(':', 1)[1].strip()}
        elif ':' in line:
            key, value = line.split(':', 1)
            current_stage[key.strip().lower()] = value.strip()
            
    if current_stage:
        stages.append(current_stage)
        
    return stages

def generate_gdd_prompt(inputs):
    return f"""Create a detailed Game Design Document with:
    - Game Vibe: {inputs['vibe']}
    - Genre: {inputs['genre']}
    - Goal: {inputs['goal']}
    - Audience: {inputs['audience']}
    - Perspective: {inputs['perspective']}
    - Art Style: {inputs['art_style']}
    Include sections for story, characters, gameplay mechanics, and world design.
    """

def generate_stage_image_prompt(stage_data, inputs):
    return f"Game level concept art, {inputs['art_style']} style, {inputs['vibe']}, {stage_data.get('environment', '')}, atmospheric, detailed environment"

def main():
    provider, openai_api_key, replicate_api_key, deepseek_api_key = setup_sidebar()
    setup_main_ui()
    inputs = get_game_details()

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

    if not text_api_connected or not image_api_connected:
        return

    if st.button("🚀 Generate Game Design Document"):
        with st.spinner("🧠 AI team is crafting your game design document..."):
            try:
                # Generate GDD
                gdd_prompt = generate_gdd_prompt(inputs)
                
                if provider == "OpenAI":
                    st.session_state.output['game_design'] = generate_with_openai(gdd_prompt, openai_api_key)
                    stages_text = generate_with_openai("Create 8 game stages with environment, challenges, mechanics, boss, rewards, story, and atmosphere for each stage.", openai_api_key)
                else:
                    st.session_state.output['game_design'] = generate_with_deepseek(gdd_prompt, deepseek_api_key)
                    stages_text = generate_with_deepseek("Create 8 game stages", deepseek_api_key)

                # Parse stages
                st.session_state.output['stages'] = parse_stages(stages_text)

                # Display outputs
                st.success("🎉 Game Design Document generated successfully!")

                with st.expander("📖 Game Design Document", expanded=True):
                    st.markdown(st.session_state.output['game_design'])

                # Display stages with images
                st.subheader("🎮 Game Stages")
                for i, stage in enumerate(st.session_state.output['stages'], 1):
                    with st.expander(f"Stage {i}: {stage.get('name', 'Unnamed Stage')}", expanded=True):
                        col1, col2 = st.columns([2, 3])
                        
                        with col1:
                            for key, value in stage.items():
                                if key != 'name':
                                    st.markdown(f"**{key.title()}**: {value}")
                        
                        with col2:
                            with st.spinner(f"Generating concept art for Stage {i}..."):
                                image_prompt = generate_stage_image_prompt(stage, inputs)
                                stage_image = generate_image_with_replicate(image_prompt, replicate_api_key)
                                display_image_safely(stage_image, f"Concept Art for Stage {i}")
                                time.sleep(1)  # Prevent rate limiting
