import streamlit as st
from autogen import (
    SwarmAgent,
    SwarmResult,
    initiate_swarm_chat,
    OpenAIWrapper,
    AFTER_WORK,
    UPDATE_SYSTEM_MESSAGE
)

# Initialize session state
if 'output' not in st.session_state:
    st.session_state.output = {
        'story': '', 
        'gameplay': '', 
        'visuals': '', 
        'tech': ''
    }

# Sidebar for API key and instructions
def setup_sidebar():
    st.sidebar.title("🔑 API Key")
    api_key = st.sidebar.text_input("Enter your OpenAI API Key", type="password")
    
    st.sidebar.markdown("""
    ### 🚀 Getting Started
    Provide details about your dream game, and the AI team will create a concept for you. Think about:
    - **Setting and vibe**
    - **Gameplay mechanics**
    - **Art style and visuals**
    - **Technical requirements**
    """)
    return api_key

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
        vibe = st.text_input("Game Vibe", "Epic fantasy with dragons")
        genre = st.selectbox("Genre", ["RPG", "Action", "Adventure", "Puzzle", "Strategy", "Simulation", "Platform", "Horror"])
        audience = st.selectbox("Audience", ["Kids (7-12)", "Teens (13-17)", "Young Adults (18-25)", "Adults (26+)", "All Ages"])
        perspective = st.selectbox("Perspective", ["First Person", "Third Person", "Top Down", "Side View", "Isometric"])
        multiplayer = st.selectbox("Multiplayer", ["Single Player", "Local Co-op", "Online Multiplayer", "Both Local and Online"])

    with col2:
        goal = st.text_input("Game Goal", "Save the kingdom from eternal winter")
        art_style = st.selectbox("Art Style", ["Realistic", "Cartoon", "Pixel Art", "Stylized", "Low Poly", "Anime", "Hand-drawn"])
        platforms = st.multiselect("Platforms", ["PC", "Mobile", "PlayStation", "Xbox", "Nintendo Switch", "Web Browser"])
        dev_time = st.slider("Development Time (months)", 1, 36, 12)
        budget = st.number_input("Budget (USD)", min_value=0, value=10000, step=5000)

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
        "budget": budget,
        "mechanics": mechanics,
        "mood": mood,
        "inspirations": inspirations,
        "unique_features": unique_features,
        "detail_level": detail_level
    }

# Define agent roles and tasks
def get_agent_tasks():
    return {
        "story_agent": """
        You are a narrative designer. Create a story that fits the game's vibe, genre, and audience. Include:
        - A compelling plot
        - Memorable characters
        - A rich world with history and culture
        """,
        "gameplay_agent": """
        You are a gameplay designer. Design mechanics and systems that align with the game's genre and goals. Include:
        - Core gameplay loops
        - Progression systems
        - Player interactions
        """,
        "visuals_agent": """
        You are an art director. Define the visual and audio style of the game. Include:
        - Art direction
        - Character and environment design
        - Sound and music concepts
        """,
        "tech_agent": """
        You are a technical director. Plan the technical aspects of the game. Include:
        - Engine and tools
        - Platform-specific requirements
        - Development pipeline
        """
    }

# Initialize agents dynamically
def setup_agents(llm_config, tasks):
    agents = {}
    for name, task in tasks.items():
        agents[name] = SwarmAgent(
            name=name,
            llm_config=llm_config,
            system_message=task,
            update_agent_state_before_reply=[UPDATE_SYSTEM_MESSAGE(lambda agent, _: agent.system_message)]
        )
    return agents

# Main function
def main():
    api_key = setup_sidebar()
    setup_main_ui()
    inputs = get_game_details()

    if st.button("🚀 Generate Game Concept"):
        if not api_key:
            st.error("Please enter your OpenAI API key.")
        else:
            with st.spinner("🧠 AI team is brainstorming your game concept..."):
                task = f"""
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

                llm_config = {"config_list": [{"model": "gpt-4", "api_key": api_key}]}
                tasks = get_agent_tasks()
                agents = setup_agents(llm_config, tasks)

                # Link agents in a workflow
                agents["story_agent"].register_hand_off(AFTER_WORK(agents["gameplay_agent"]))
                agents["gameplay_agent"].register_hand_off(AFTER_WORK(agents["visuals_agent"]))
                agents["visuals_agent"].register_hand_off(AFTER_WORK(agents["tech_agent"]))
                agents["tech_agent"].register_hand_off(AFTER_WORK(agents["story_agent"]))

                result, _, _ = initiate_swarm_chat(
                    initial_agent=agents["story_agent"],
                    agents=list(agents.values()),
                    user_agent=None,
                    messages=task,
                    max_rounds=12,
                )

                st.session_state.output = {
                    'story': result.chat_history[-4]['content'],
                    'gameplay': result.chat_history[-3]['content'],
                    'visuals': result.chat_history[-2]['content'],
                    'tech': result.chat_history[-1]['content']
                }

            st.success("🎉 Game concept generated successfully!")

            with st.expander("📖 Story Design"):
                st.markdown(st.session_state.output['story'])

            with st.expander("🎮 Gameplay Mechanics"):
                st.markdown(st.session_state.output['gameplay'])

            with st.expander("🎨 Visual and Audio Design"):
                st.markdown(st.session_state.output['visuals'])

            with st.expander("⚙️ Technical Recommendations"):
                st.markdown(st.session_state.output['tech'])

if __name__ == "__main__":
    main()
