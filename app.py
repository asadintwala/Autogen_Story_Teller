import streamlit as st
import autogen
from agents.writer_agent import WriterAgent
from agents.editor_agent import EditorAgent
from agents.reviewer_agent import ReviewerAgent
from utils.gemini_utils import load_config

# Add a function to check API configuration
def check_api_configuration():
    try:
        config = load_config()
        api_key = config.get('api_key', '')
        model_name = config.get('model_name', '')
        
        if not api_key or api_key == "YOUR_API_KEY_HERE":
            return False, "API key is missing or appears to be a placeholder."
        
        if not model_name:
            return False, "Model name is missing in the configuration."
            
        return True, "Configuration appears valid."
    except Exception as e:
        return False, f"Error checking configuration: {str(e)}"

# Streamlit UI
st.title("AutoGen Multi-Agent Story Writer")

# Check configuration first
config_valid, config_message = check_api_configuration()
if not config_valid:
    st.error(f"Configuration Error: {config_message}")
    st.info("Please update your config/config.toml file with valid API key and model name.")
    # Show a sample config
    st.code("""
    # config/config.toml
    api_key = "YOUR_GEMINI_API_KEY"
    model_name = "gemini-2.0-flash"
    """)
    st.stop()

# If configuration is valid, continue with the app
try:
    @st.cache_resource
    def create_agents():
        # 1. Create Writer Agent
        writer_agent = WriterAgent(
            name="Writer",
            system_message="You are a creative writer. You should respond in a creative and professional style"
        )

        # 2. Create Editor Agent
        editor_agent = EditorAgent(
            name="Editor",
            system_message="You are a skilled editor."
        )
        
        # 3. Create Reviewer Agent
        reviewer_agent = ReviewerAgent(
            name="Reviewer",
            system_message="You are a literary reviewer who analyzes themes, character development, and overall impact."
        )
        
        return writer_agent, editor_agent, reviewer_agent

    # Get the agents
    writer_agent, editor_agent, reviewer_agent = create_agents()

    # Auto Gen related
    config = load_config()
    llm_config = {"config_list": [{"model": config['model_name']}], "seed": 42}

    user_proxy = autogen.UserProxyAgent(
        name="User_proxy",
        human_input_mode="NEVER",
        max_consecutive_auto_reply=10,
        is_termination_msg=lambda x: x.get("content", "").rstrip().endswith("TERMINATE"),
        code_execution_config={"work_dir": "coding", "use_docker": False},
        system_message="""Reply TERMINATE if the task has been solved at full satisfaction.
    Otherwise, reply CONTINUE, or the reason why the task is not solved.
    """
    )

    prompt = st.text_area("Enter your story prompt:", "Write a short story about a dog who learns to fly.")

    if st.button("Generate Story"):
        with st.spinner("Generating story..."):
            try:
                # Use the writer_agent's generate_story method directly
                story = writer_agent.generate_story(prompt)
                
                if story and not story.startswith("Error:") and not story.startswith("I apologize"):
                    st.write("## Generated Story:")
                    st.write(story)
                    st.session_state.generated_story = story
                    print(f"Generated story: {story[:100]}...")  # Print just the beginning for debugging
                else:
                    st.error(f"Failed to generate story: {story}")
                    st.info("Please check your API key and model configuration.")
            except Exception as e:
                st.error(f"An error occurred: {str(e)}")
                import traceback
                st.error(traceback.format_exc())

    if "generated_story" in st.session_state:
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("Get Editor Feedback"):
                with st.spinner("Getting feedback from the editor..."):
                    try:
                        feedback = editor_agent.provide_feedback(st.session_state.generated_story)
                        if feedback and not feedback.startswith("Error:") and not feedback.startswith("I apologize"):
                            st.write("## Editor Feedback:")
                            st.write(feedback)
                        else:
                            st.error(f"Failed to get editor feedback: {feedback}")
                    except Exception as e:
                        st.error(f"An error occurred: {str(e)}")
        
        with col2:
            if st.button("Get Reviewer Analysis"):
                with st.spinner("Getting analysis from the reviewer..."):
                    try:
                        analysis = reviewer_agent.provide_analysis(st.session_state.generated_story)
                        if analysis and not analysis.startswith("Error:") and not analysis.startswith("I apologize"):
                            st.write("## Reviewer Analysis:")
                            st.write(analysis)
                        else:
                            st.error(f"Failed to get reviewer analysis: {analysis}")
                    except Exception as e:
                        st.error(f"An error occurred: {str(e)}")
except Exception as e:
    st.error(f"Application Error: {str(e)}")
    import traceback
    st.error(traceback.format_exc())