from autogen import AssistantAgent
from utils.gemini_utils import generate_text_gemini

class EditorAgent(AssistantAgent):
    def __init__(self, name="Editor",
        system_message="You are a professional editor. You give feedback on content. Focus on grammar, clarity, and style.",
        **kwargs):
        super().__init__(
            name=name,
            system_message=system_message,
            **kwargs
        )

    def provide_feedback(self, text):
        print(f"EditorAgent.provide_feedback called with text length: {len(text)}")  # Debugging
        feedback_prompt = f"""Please provide detailed editorial feedback on the following text, focusing on:
1. Grammar and punctuation
2. Clarity and readability
3. Style and tone
4. Suggestions for improvement

Here is the text:
{text}"""
        return generate_text_gemini(feedback_prompt)