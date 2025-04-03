from autogen import AssistantAgent
from utils.gemini_utils import generate_text_gemini

class WriterAgent(AssistantAgent):
    def __init__(self, name="Writer",
        system_message="You are a creative writer. Please respond in professional and creative style.",
        **kwargs):
        super().__init__(
            name=name,
            system_message=system_message,
            **kwargs
        )

    def generate_story(self, prompt):
        print(f"WriterAgent.generate_story called with prompt: {prompt[:50]}...")  # Debugging
        story_prompt = f"Write a creative short story based on this prompt: {prompt}"
        return generate_text_gemini(story_prompt)