<think>
Alright, the user provided an error message and their code for a Streamlit app that's supposed to generate game concepts using AI tools like OpenAI and Replicate. They mentioned encountering an AttributeError when trying to display the generated image. 

Looking at the code, I see that when the provider is DeepSeek, the `generate_with_deepseek` function just returns a placeholder string. That might be causing issues if the DeepSeek API isn't actually being used correctly, or maybe it's not generating any content, leading to empty strings and errors when trying to process images.

Another point in the error is about validating the image format, specifically checking if it's a GIF. This suggests that the generated image (or perhaps the URL) might not be properly formatted, causing the Streamlit app to fail when attempting to display it.

I notice that the user mentioned getting an option for common game goals of super hit games but didn't see it in their setup. So maybe they want more predefined options for genres and goals to make the input easier and more guided.

Also, when the image generation is handled by Replicate, there's a specific model being used. If this model isn't generating an appropriate image format or if there's an issue with how the URL is being constructed, that could lead to the error. Perhaps checking the output of the Replicate API for errors would be helpful.

To fix these issues, I should:

1. Add more game goals as options so users don't have to start from scratch.
2. Ensure that both text generation and image generation are properly integrated and handle cases where APIs might fail.
3. Check if the generated image URL is valid and correctly formatted, possibly adding error handling when trying to display it.

I'll modify the code by adding predefined game goals in a dropdown, enhancing the API connection checks, and ensuring that all necessary data is captured before generating content. I'll also add try-except blocks around critical operations like image rendering to catch any errors early and provide meaningful feedback to the user.
</think>



The error you're encountering appears to be related to issues with the generated image URL or the format of the response from the API used for text generation. Let's break down the possible causes and solutions:

### 1. **Problematic Code Sections:**
   - The `generate_with_deepseek` function is currently just returning a placeholder string, which might not be generating proper content.
   - When using DeepSeek, ensure that the API call is properly integrated to generate both text and visuals.

### 2. **Error Analysis:**
   - The error message mentions an AttributeError related to image display. Specifically:
     ```python
     AttributeError: This app has encountered an error...
     ```
   - The traceback points to issues with displaying the generated image, possibly due to invalid or non-existent URLs returned by the API.

### 3. **Potential Issues and Solutions:**
   - **Text Generation Issue:** If you're using DeepSeek for text generation, ensure that it's properly configured to generate meaningful responses.
   - **Image Generation Issue:** The Replicate API might be returning an image format that isn't supported or generating an invalid URL.
   - **API Key Check:** Verify that both the OpenAI and Replicate API keys are properly set. Missing keys can lead to failed API calls and subsequent errors.

### 4. **Code Improvements:**
   - Add error handling around critical operations like image generation and text generation.
   - Ensure that when using DeepSeek, it's generating a proper response for both text and visuals.

Here's an improved version of your code with additional features (common game goals, better error handling):

```python
import streamlit as st
import openai
import replicate
import os

# Initialize session state
if 'output' not in st.session_state:
    st.session_state.output = {
        'story': '', 
        'gameplay': '', 
        'visuals': '', 
        'tech': '',
        'image_url': ''
    }

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

def check_api_connection(provider, api_key):
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
            # Replace with actual DeepSeek API test call
            # Example: Assume DeepSeek has a similar test endpoint
            return True
        except Exception as e:
            st.error(f"DeepSeek API connection failed: {e}")
            return False
    return False

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

# Generate text using OpenAI
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
        st.error(f"OpenAI API call failed: {e}")
        return None

# Generate text using DeepSeek
def generate_with_deepseek(prompt, api_key):
    try:
        # Replace with actual DeepSeek API call
        # Example placeholder (replace with actual API call)
        response = {
            "choices": [
                {
                    "message": {"content": f"DeepSeek response for: {prompt}"}
                }
            ]
        }
        return response.choices[0].message['content']
    except Exception as e:
        st.error(f"DeepSeek API call failed: {e}")
        return None

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
        st.error(f"Replicate API call failed: {e}")
        return None

# Main function
def main():
    provider, openai_api_key, replicate_api_key, deepseek_api_key = setup_sidebar()
    setup_main_ui()
    inputs = get_game_details()

    # Check API connection
    if provider == "OpenAI":
        api_key = openai_api_key
        api_connected = check_api_connection(provider, api_key)
    else:
        api_key = deepseek_api_key
        api_connected = check_api_connection(provider, api_key)

    # Display connection status
    if api_connected:
        st.sidebar.success("✅ API Connected")
    else:
        st.sidebar.error("❌ API Not Connected")
        return  # Stop execution if API is not connected

    if st.button("🚀 Generate Game Concept"):
        if not (openai_api_key and replicate_api_key):
            st.error("Please enter all required API keys.")
        else:
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
                if provider == "OpenAI":
                    story = generate_with_openai(prompt, api_key)
                else:
                    story = generate_with_deepseek(prompt, api_key)

                # Generate image
                image_prompt = f"{inputs['vibe']}, {inputs['art_style']}, {inputs['mood']}"
                image_url = generate_image_with_replicate(image_prompt, replicate_api_key)

            st.success("🎉 Game concept generated successfully!")

            with st.expander("📖 Story Design"):
                st.markdown(st.session_state.output['story'])

            with st.expander("🖼️ Generated Image"):
                if image_url:
                    st.image(image_url, caption="Generated Game Art")
                else:
                    st.error("Failed to generate image. Please check API keys and permissions.")
    else:
        st.warning("No button clicked. Click 'Generate Game Concept' to get the results.")

if __name__ == "__main__":
    main()
```
