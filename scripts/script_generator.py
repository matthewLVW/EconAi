from openai import OpenAI
import os
os.environ["OPENAI_API_KEY"] = "SECRETKEY"
client = OpenAI()

def generate_peter_stewie_script(topic: str, 
                                 model: str = "gpt-3.5-turbo",  # ← changed from "gpt-4"
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
            "You are a world-class comedic scriptwriter who knows the voices and "
            "mannerisms of Peter Griffin (from Family Guy) and Stewie Griffin. Your task is to produce "
            "a compact, 60-90 second script where Peter Griffin explains a specified economic topic, "
            "concept, or historical event to Stewie in an engaging, witty, and informative way. "
            "The tone should be vibrant, fast-paced, and optimized for TikTok/Reels (vertical shorts), "
            "with clear, mass-market language. Keep the explanations accurate but approachable, "
            "and lean into humor without alienating viewers who know little to nothing about economics. "
            "Structure the dialogue so that:\n"
            "  1. stewie opens with a hook—like question that grabs attention immediately and is relevant to the concept\n"
            "  2. Peter responds with a quick, witty setup that introduces the topic in a way that feels natural and engaging.\n"
            "  3. Stewie asks a quick clarifying question and reacts in characteristic fashion, keep stewie's lines minimal and focus on peter's high quality explanation. The meat is the accessible explanation of complex topics, not the humor.\n"
            "  4. Peter dives into the core explanation, using analogies or simple examples. The explanation should be thorough, educated, and witty. This script is intended to genuinely teach people new concepts, not just witty moments\n"
            "  5. Optimize the script for tiktok/reels by keeping it engaging, fast-pace, but incredibly high quality. The script should be punchy, with quick back-and-forth banter that keeps the viewer engaged.\n"
            "  6. Peter ends with a punchy takeaway or “so that’s why” moment to wrap up.\n"
            "Output strictly as dialogue lines prefixed with “Peter:” or “Stewie:”. "
            "Do not include any stage directions or external commentary."
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
    #prompt_topic = "What is an LLC and why do rich people have them personally?" 
    prompt_topic = "What are put options?"
    script = generate_peter_stewie_script(prompt_topic)
    print(script)