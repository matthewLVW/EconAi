from openai import OpenAI
import os
from dotenv import load_dotenv
load_dotenv()
client = OpenAI()

def generate_peter_stewie_script(topic: str, 
                                 model: str = "gpt-4.1",  # ← changed from "gpt-4"
                                 max_tokens: int = 500, 
                                 temperature: float = 0.8) -> str:
    """
    Given an economic topic, concept, or historical event (e.g., "What happened to cause the 2008 financial collapse"),
    constructs a structured, high-energy LLM prompt and invokes the OpenAI API to produce a short (30–60 second)
    script in which Peter Griffin explains that topic to Stewie. The output is formatted as a dialogue, 
    optimized for TikTok/Reels and designed to be lively, witty, and accessible but still read as quite formal and educational.

    Requirements:
      • Assumes `openai.api_key` is set in your environment (e.g., export OPENAI_API_KEY="…").
      • Adjust `model`, `max_tokens`, and `temperature` as needed.

    Returns:
      A string containing the generated script.
    """
    # 1. Build a “system” message that frames the overall style and format:
    system_message = {
    "role": "system",
    "content": (
        "You are a world-class economist, orator, and scriptwriter for AI voice bots. "
        "You specialize in writing scripts that can be fed into AI voice models to produce smooth, natural-sounding dialogue. "
        
        "Write the script with pacing and intonation in mind. Keep sentences medium-length and structurally similar between speakers. "
        "Avoid short, choppy sentences or overly long ones. Use commas to signal slight pauses, and end most lines with periods. "
        "This will help maintain a natural, even cadence when spoken by AI.\n\n"

        "Maintain consistent emotional tone and speech rhythm across the entire conversation. "
        "Avoid any sudden tonal shifts or overly dramatic phrases that would make each line sound disconnected when voiced separately.\n\n"

        "Make sure Stewie and Peter sound like they're part of a continuous conversation, not like separate narrators. "
        "Use repetition of certain words, parallel sentence structures, and shared phrasing cues to glue the dialogue together.\n\n"

        "You are familiar with the mannerisms of Peter Griffin and Stewie Griffin from Family Guy. "
        "Your task is to produce a 75–90 second script where Peter Griffin explains a specified economic topic thoroughly. "
        "The tone should be vibrant, educated, and optimized for TikTok/Reels. Use clear, mass-market language to bring elite financial knowledge to the general public.\n\n"

        "Avoid excessive punctuation like ellipses. Avoid stage directions. Only output dialogue lines prefixed with 'Peter:' or 'Stewie:'.\n\n"

        "Structure the dialogue so that:\n"
        "  1. Stewie opens with a question that hooks the audience and introduces the topic.\n"
        "  2. Peter gives a quick, witty setup that introduces the theme clearly.\n"
        "  3. The explanation unfolds mainly through Peter's detailed and relatable answers, while Stewie offers brief clarifying questions to guide the flow.\n"
        "  4. Peter ends with a clean takeaway or 'so that’s why' moment to leave the viewer smarter.\n"
    )
}
 

    # 2. Build a “user” message that inserts the specific topic:
    user_message = {
        "role": "user",
        "content": (
            f"I want a script where Stewie Griffin asks Peter Griffin  to explain: “{topic}”. "
            "Ensure it fits into a 60–90 second short, with energy and humor suited for TikTok/Reels. "
            "Focus on making complex ideas simple, lively, and memorable. "
            "Use Family Guy–style banter. Keep the dialogue punchy but focus on informative aswell."
        )
    }

    # 3. Call the OpenAI ChatCompletion endpoint:
    response = client.chat.completions.create(model=model,
    messages=[system_message, user_message],
    max_tokens=max_tokens,
    temperature=temperature)

    # 4. Extract and return the script text:
    script_text = response.choices[0].message.content.strip()
    return script_text


# Example usage:
if __name__ == "__main__":
    # Example: “What happened to cause the 2008 financial collapse”
    prompt_topic = "What is an LLC and why do rich people have them personally?" 
    #prompt_topic = "What are put options?"
    script = generate_peter_stewie_script(prompt_topic)
    print(script)