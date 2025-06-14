import json
import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
client = OpenAI()


def build_user_message(topic: str):
    return {
    "role": "user",
    "content": (
        f"Write a script where Stewie Griffin asks Peter Griffin to explain: “{topic}”.\n"
        "Make sure Stewie's **first line is sharp, modern, and question-driven** — no weird references or rambling setups. "
        "It should immediately make the viewer curious or feel like they’re overhearing something valuable.\n\n"
        "The script should be no longer than 45 seconds when spoken aloud. Use humor, pop-culture analogies, and everyday phrasing. "
        "Keep it engaging but focused. Format as plain dialogue only, ready to be spoken by voice models."
        "Stewie’s opening line MUST be a single, urgent question — no slow intros, no filler I.E. peter, what is x, Peter why does Y, Peter what caused Z but do not paraphrase the users question, it should be a bare bones expression of the question. "
        "The script should be under 45 seconds spoken. "
    )
}

def build_system_message():
    return {
    "role": "system",
    "content": (
        "You write short, engaging scripts between Stewie and Peter Griffin, optimized for TikTok/Reels. "
        "The goal is to teach a concept quickly while sounding like a real, fluid conversation between AI voices.\n\n"

        "Hook structure:\n"
        "1. Hook (0–3s): Stewie asks a *direct*, attention-grabbing question related to the topic — no fluff, no weird metaphors. "
        "Avoid unrelated jokes. Make the viewer think, 'Wait, I want to know this.'\n"
        "+ Stewie opens with a *single*, sharp, question, avoid humor, follow the user prompt"
        "+ Do NOT use phrases like “why do people say” or “what is X and why Y”. Just ask one urgent question."
        "+ Assume the audience has 2 seconds to be convinced this is worth watching."
        "2. Explanation + Banter (3–35s): Peter explains clearly with humor. Stewie adds brief interruptions or snark. Peter simplifies.\n"
        "3. Callback/Punchline (35–45s): Peter or Stewie ends with a clever twist, callback, or funny summation that reinforces the core idea.\n\n"

        "Scriptwriting rules:\n"
        "• Use medium-length sentences that flow when spoken.\n"
        "• Match emotional tone and rhythm between speakers.\n"
        "• Avoid monologues. Alternate lines every 1–2 beats.\n"
        "• Stewie is curious, sharp, and impatient. Peter is casual, confident, and metaphor-heavy — but not random.\n"
        "• Do not use ellipses, stage directions, or narration. Only output dialogue in this format:\n"
        "   Stewie: [his line]\n"
        "   Peter: [his line]\n\n"

        "Keep the energy tight and the value clear. You're not just entertaining — you're hijacking a scroll to *teach something cool fast*."
    )
}

def generate_variants(topic: str, count: int = 5):
    system_msg = build_system_message()
    user_msg = build_user_message(topic)
    scripts = []
    for i in range(count):
        response = client.chat.completions.create(
            model="gpt-4.1",
            messages=[system_msg, user_msg],
            max_tokens=500,
            temperature=0.7 + i * 0.05
        )
        script = response.choices[0].message.content.strip()
        scripts.append(script)
    return scripts


def evaluate_scripts(topic: str, scripts: list[str]) -> int:
    eval_prompt = [
        {
            "role": "system",
            "content": (
                "You are a short-form video strategist. Your task is to review multiple script versions for a TikTok. "
                "You must choose the **single best script** — the one most likely to go viral based on hook strength, clarity, pacing, and entertainment value.\n\n"
                "Return ONLY a JSON object in this format:\n"
                "{\n  \"selected_index\": [number from 1–5],\n  \"reason\": \"Short explanation here.\"\n}"
            )
        },
        {
            "role": "user",
            "content": (
                f"Here are 5 TikTok scripts for the topic: \"{topic}\"\n\n"
                + "\n\n---\n\n".join([f"Script {i+1}:\n{script}" for i, script in enumerate(scripts)])
            )
        }
    ]
    
    response = client.chat.completions.create(
        model="gpt-4.1",
        messages=eval_prompt,
        max_tokens=500,
        temperature=0.5
    )

    raw = response.choices[0].message.content.strip()

    # Try parsing the JSON response
    try:
        result = json.loads(raw)
        best_index = result.get("selected_index", 1)
        reason = result.get("reason", "No reason provided.")
    except Exception as e:
        best_index = 1
        reason = f"[PARSE ERROR] {e}\nRaw response: {raw}"

    return best_index, reason


def generate_best_script(topic: str, save_path: str = "script.txt"):
    scripts = generate_variants(topic, count=5)
    best_index, reason = evaluate_scripts(topic, scripts)
    best_script = scripts[best_index - 1]

    with open(save_path, "w", encoding="utf-8") as f:
        f.write(best_script)

    print(f"\n🎯 Best Script: Variant {best_index}\n🧠 Why: {reason}")
    return best_script