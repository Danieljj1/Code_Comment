import os
from flask import Flask, request, jsonify, render_template
from openai import OpenAI

client = OpenAI()

app = Flask(__name__)

def user_code() -> str:
    print("Enter your code here:")
    print("When finished, type 'END' and press Enter.")

    lines = []
    while True:
        line = input()
        if line.strip().upper() == 'END':
            break
        lines.append(line)
    return "\n".join(lines)
    

def user_level() -> str:
    print("Select coding level: \n1. Beginner \n2. Intermediate \n3. Advanced")
    return input("> ").strip()

def ask_comment_language() -> str:
    print("Select comment language: \n1. Python \n2. JavaScript \n3. Java \n4. C++ \n5. HTML \n6. React JavaScript")
    return input("> ").strip()



def comment_level(level_choice: str) -> str:
    levels = {
        '1': 'Beginner',
        '2': 'Intermediate',
        '3': 'Advanced'
    }
    return levels.get(level_choice, 'Beginner')

def comment_language(lang_choice: str) -> str:
    languages = {
        '1': 'Python',
        '2': 'JavaScript',
        '3': 'Java',
        '4': 'C++',
        '5': 'HTML',
        '6': 'React JavaScript'
    }
    return languages.get(lang_choice, 'Python')




def generate_code_comments(code: str, code_level: str, code_language: str) -> str:
    prompt = f""" 
You are a coding assistant that adds helpful comments to code. Add comments to the following code according to these instructions:
            - Explanation level: {code_level}
            - Code language / comment style: {code_language}
            - Keep the original code structure.
            - Add comments in a way that is natural for {code_language} code.
            - Make comments clear but not excessively long, matching the {code_level} level.
            - Return ONLY the code with comments added; do not add explanations before or after.

Code to comment:

{code}
"""
    
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are an expert code commenter."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=1500,
        temperature=0.7
    )
    
    return response.choices[0].message.content.strip()

@app.route("/", methods=["GET"])
def index():
    # Renders the HTML UI
    return render_template("index.html")

@app.route("/generate-comments", methods=["POST"])
def generate_comments():
    data = request.get_json(force=True)  # parse JSON body

    code = (data.get("code") or "").strip()
    level_choice = (data.get("level_choice") or "1").strip()
    lang_choice = (data.get("lang_choice") or "1").strip()

    if not code:
        return jsonify({"error": "Code is required"}), 400
    
    code_level = comment_level(level_choice)
    code_language = comment_language(lang_choice)

    try:
        commented_code = generate_code_comments(code, code_level, code_language)
        return jsonify({"commented_code": commented_code})
    except Exception as e:
        # Simple error handling so the frontend can show a message
        return jsonify({"error": f"Server error: {type(e).__name__}: {e}"}), 500





if __name__ == "__main__":
    app.run(debug=True)


