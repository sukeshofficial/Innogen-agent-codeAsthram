# import sys
# import json
# import os
# from dotenv import load_dotenv

# from block_knowledge import BlockKnowledgeBase
# from prompt import system_prompt, user_prompt
# from openai import OpenAI

# load_dotenv()

# # print("API KEY LOADED:", bool(os.getenv("OPENROUTER_API_KEY")))

# def main():
#     if len(sys.argv) < 2:
#         print(json.dumps({"error": "missing_problem"}))
#         sys.exit(1)

#     problem_text = sys.argv[1]

#     repair_instruction = sys.stdin.read().strip()
    
#     # ------------------------------
#     # 1️⃣ Load block knowledge (RAG)
#     # ------------------------------
#     kb = BlockKnowledgeBase()
#     relevant_blocks = kb.retrieve_relevant_blocks(problem_text)
#     formatted_blocks = kb.format_for_llm(relevant_blocks)

#     # ------------------------------
#     # 2️⃣ Build prompts
#     # ------------------------------
#     sys_prompt = system_prompt()
#     # usr_prompt = user_prompt(
#     #     problem_text,
#     #     json.dumps(formatted_blocks, indent=2)
#     # )
    
#     if repair_instruction:
#         usr_prompt = repair_instruction
#     else:
#         usr_prompt = user_prompt(
#             problem_text,
#             json.dumps(formatted_blocks, indent=2)
#         )

#     # ------------------------------
#     # 3️⃣ Call OpenRouter (OpenAI-compatible)
#     # ------------------------------
#     client = OpenAI(
#         base_url="https://openrouter.ai/api/v1",
#         api_key=os.getenv("OPENROUTER_API_KEY")
#     )

#     response = client.chat.completions.create(
#         model="meta-llama/llama-3-8b-instruct",
#         messages=[
#             {"role": "system", "content": sys_prompt},
#             {"role": "user", "content": usr_prompt}
#         ],
#         temperature=0,
#     )

#     output = response.choices[0].message.content.strip()

#     # ------------------------------
#     # 4️⃣ Output RAW JSON ONLY
#     # ------------------------------
#     print(output)


# if __name__ == "__main__":
#     main()


import sys
import json
import os
from dotenv import load_dotenv
from openai import OpenAI

from block_knowledge import BlockKnowledgeBase
from prompt import system_prompt, user_prompt

load_dotenv()


# ------------------------------
def main():
    if len(sys.argv) < 2:
        print(json.dumps({"error": "missing_problem"}))
        sys.exit(1)

    problem_text = sys.argv[1]

    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        print(json.dumps({"error": "OPENROUTER_API_KEY not set"}))
        sys.exit(1)

    # ------------------------------
    # 1️⃣ Load block knowledge (RAG)
    # ------------------------------
    kb = BlockKnowledgeBase()
    relevant_blocks = kb.retrieve_relevant_blocks(problem_text)
    formatted_blocks = kb.format_for_llm(relevant_blocks)

    # ------------------------------
    # 2️⃣ Build prompts
    # ------------------------------
    sys_prompt = system_prompt()
    usr_prompt = user_prompt(
        problem_text,
        json.dumps(formatted_blocks, indent=2)
    )

    # ------------------------------
    # 3️⃣ Call OpenRouter (WITH TIMEOUT)
    # ------------------------------
    client = OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=api_key
    )

    try:
        response = client.chat.completions.create(
            model="meta-llama/llama-3-8b-instruct",
            messages=[
                {"role": "system", "content": sys_prompt},
                {"role": "user", "content": usr_prompt}
            ],
            temperature=0,
            timeout=60  # 🔥 CRITICAL FIX
        )
    except Exception as e:
        print(json.dumps({
            "error": "llm_request_failed",
            "detail": str(e)
        }))
        sys.exit(1)

    output = response.choices[0].message.content.strip()

    # ------------------------------
    # 4️⃣ Output RAW JSON ONLY
    # ------------------------------
    print(output)


# ------------------------------
if __name__ == "__main__":
    main()
