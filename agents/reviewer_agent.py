from autogen import AssistantAgent
from utils.gemini_utils import generate_text_gemini

class ReviewerAgent(AssistantAgent):
    def __init__(self, name="Reviewer",
        system_message="You are a literary reviewer who analyzes themes, character development, and overall impact.",
        **kwargs):
        super().__init__(
            name=name,
            system_message=system_message,
            **kwargs
        )

    def provide_analysis(self, text):
        print(f"ReviewerAgent.provide_analysis called with text length: {len(text)}")  # Debugging
        analysis_prompt = f"""Please provide a thoughtful literary analysis of the following story, focusing on:
1. Main themes and motifs
2. Character development
3. Narrative structure
4. Overall impact and emotional resonance
5. Literary merit

Here is the story:
{text}"""
        return generate_text_gemini(analysis_prompt) 