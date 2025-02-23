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

# Previous functions remain the same until generate_gdd_prompt

def generate_stages_prompt(inputs):
    return f"""Create 8 distinct game stages for a {inputs['genre']} game set in a {inputs['vibe']} world with {inputs['art_style']} art style.
    For each stage, provide:
    1. Stage name
    2. Environmental description
    3. Key challenges
    4. Unique mechanics
    5. Boss or main challenge
    6. Rewards/progression
    7. Connection to main story
    8. Atmosphere and mood

    The stages should progress in difficulty and complexity, building up to an epic finale.
    Consider the {inputs['perspective']} perspective and incorporate the following mechanics: {', '.join(inputs['mechanics']) if inputs['mechanics'] else 'basic gameplay'}.
    Target audience: {inputs['audience']}
    Overall mood: {', '.join(inputs['mood']) if inputs['mood'] else 'atmospheric'}
    """

def generate_stage_image_prompt(stage_data, inputs):
    return f"Game level concept art, {inputs['art_style']} style, {inputs['vibe']}, {stage_data['name']}, {stage_data['environment']}, {', '.join(inputs['mood']) if inputs['mood'] else 'atmospheric'}, detailed environment, game level, highly detailed"

def generate_with_openai(prompt, api_key):
    openai.api_key = api_key
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=2000
    )
    return response.choices[0].message['content']

def generate_with_deepseek(prompt, api_key):
    # Placeholder for DeepSeek API implementation
    # For now, let's create a more structured response
    return f"""
    Stage 1: The Awakening
    - Environment: Ancient ruins emerging from morning mist
    - Challenges: Basic movement and core mechanics tutorial
    - Mechanics: Introduction to basic abilities
    - Boss: Training Guardian
    - Rewards: First basic ability unlock
    - Story: Player character awakens to their destiny
    - Atmosphere: Mysterious and peaceful

    Stage 2: The Forgotten Valley
    - Environment: Overgrown valley with abandoned structures
    - Challenges: First real combat encounters
    - Mechanics: Combat basics and exploration
    - Boss: Valley Keeper
    - Rewards: Enhanced movement ability
    - Story: Discovering the world's history
    - Atmosphere: Serene but dangerous

    Stage 3: The Underground Network
    - Environment: Ancient technological ruins
    - Challenges: Complex platforming and puzzles
    - Mechanics: New puzzle-solving abilities
    - Boss: Security System Alpha
    - Rewards: Puzzle-solving tool
    - Story: Uncovering ancient technology
    - Atmosphere: Dark and mysterious

    Stage 4: The Storm Plains
    - Environment: Lightning-struck wastelands
    - Challenges: Environmental hazards
    - Mechanics: Weather interaction abilities
    - Boss: Storm Elemental
    - Rewards: Weather control power
    - Story: Learning about the world's corruption
    - Atmosphere: Wild and electric

    Stage 5: The Crystal Caverns
    - Environment: Massive crystalline cave system
    - Challenges: Light-based puzzles
    - Mechanics: Crystal manipulation
    - Boss: Crystal Colossus
    - Rewards: Light bending ability
    - Story: Finding the source of power
    - Atmosphere: Beautiful but treacherous

    Stage 6: The Sky Citadel
    - Environment: Floating ruins in the clouds
    - Challenges: Vertical traversal and flying enemies
    - Mechanics: Advanced movement abilities
    - Boss: Wind Dragon
    - Rewards: Flight capability
    - Story: Approaching the main antagonist's domain
    - Atmosphere: Majestic and dangerous

    Stage 7: The Corruption Core
    - Environment: Twisted landscape of corruption
    - Challenges: Survival and corruption mechanics
    - Mechanics: Corruption resistance abilities
    - Boss: Corrupted Guardian
    - Rewards: Final power upgrade
    - Story: Direct confrontation with evil
    - Atmosphere: Dark and oppressive

    Stage 8: The Final Ascent
    - Environment: Reality-bending final area
    - Challenges: Using all learned abilities
    - Mechanics: Combination of all previous mechanics
    - Boss: Final Boss with multiple phases
    - Rewards: Game completion
    - Story: Final battle and resolution
    - Atmosphere: Epic and climactic
    """

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
    lines = stages_text.strip().split('\n')
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
            
        if line.startswith('Stage'):
            if current_stage:
                stages.append(current_stage)
            current_stage = {'name': line.split(':', 1)[1].strip()}
        elif line.startswith('-'):
            key, value = line[1:].split(':', 1)
            current_stage[key.strip().lower()] = value.strip()
            
    if current_stage:
        stages.append(current_stage)
        
    return stages

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
                stages_prompt = generate_stages_prompt(inputs)
                
                if provider == "OpenAI":
                    st.session_state.output['game_design'] = generate_with_openai(gdd_prompt, openai_api_key)
                    stages_text = generate_with_openai(stages_prompt, openai_api_key)
                else:
                    st.session_state.output['game_design'] = generate_with_deepseek(gdd_prompt, deepseek_api_key)
                    stages_text = generate_with_deepseek(stages_prompt, deepseek_api_key)

                # Parse stages
                st.session_state.output['stages'] = parse_stages(stages_text)

                # Generate main concept art
                image_prompt = f"{inputs['vibe']}, {inputs['art_style']}, {', '.join(inputs['mood']) if inputs['mood'] else 'atmospheric'}"
                st.session_state.output['main_image_url'] = generate_image_with_replicate(image_prompt, replicate_api_key)
                
                st.success("🎉 Game Design Document generated successfully!")

                # Display outputs
                with st.expander("📖 Game Design Document", expanded=True):
                    st.markdown(st.session_state.output['game_design'])

                with st.expander("🖼️ Main Concept Art"):
                    if st.session_state.output['main_image_url']:
                        display_image_safely(st.session_state.output['main_image_url'], "Main Game Concept Art")

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
                        
            except Exception as e:
                st.error(f"An error occurred: {str(e)}")

if __name__ == "__main__":
    main()
