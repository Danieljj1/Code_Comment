import os
from flask import Flask, request, jsonify, render_template
from openai import OpenAI

client = OpenAI()
app = Flask(__name__)

LANGUAGES = {
    '1': 'Python',
    '2': 'JavaScript',
    '3': 'TypeScript',
    '4': 'Java',
    '5': 'C++',
    '6': 'HTML',
    '7': 'React (JSX)',
    '8': 'Go',
    '9': 'Rust',
    '10': 'SQL',
}

LEVELS = {
    '1': 'Beginner',
    '2': 'Intermediate',
    '3': 'Advanced',
}

def get_language(choice: str) -> str:
    return LANGUAGES.get(choice, 'Python')

def get_level(choice: str) -> str:
    return LEVELS.get(choice, 'Beginner')


def generate_code_comments(code: str, level: str, language: str) -> str:
    prompt = f"""You are a coding assistant that adds helpful comments to code. Add comments to the following code:
- Explanation level: {level}
- Language/comment style: {language}
- Keep the original code structure intact.
- Add comments natural to {language}.
- Match verbosity to the {level} level.
- Return ONLY the commented code — no explanations before or after.

Code:
{code}"""
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are an expert code commenter."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=2000,
        temperature=0.5
    )
    return response.choices[0].message.content.strip()


def generate_readme(code: str, language: str) -> str:
    prompt = f"""You are a technical documentation expert. Generate a clean, professional README.md for the following {language} code.

Include these sections (only if relevant):
# Project / Function Name
## Description
## Requirements / Dependencies (if any imports are visible)
## Usage
```{language.lower()}
(usage example)
```
## Parameters / Arguments (if it's a function/class)
## Returns (if applicable)
## Notes (edge cases, limitations)

Keep it concise and accurate. Use real information from the code — don't make things up.

Code:
{code}"""
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are a technical writer who creates clear, accurate README documentation."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=1500,
        temperature=0.4
    )
    return response.choices[0].message.content.strip()


def explain_code(code: str, level: str, language: str) -> str:
    level_instructions = {
        'Beginner': 'Explain as if to someone who is new to programming. Avoid jargon, use analogies.',
        'Intermediate': 'Assume basic programming knowledge. Explain what the code does and why each part exists.',
        'Advanced': 'Assume expert knowledge. Focus on design decisions, complexity, edge cases, and potential improvements.',
    }
    instruction = level_instructions.get(level, level_instructions['Intermediate'])
    prompt = f"""Explain the following {language} code clearly. {instruction}

Structure your explanation as:
**What it does:** (1-2 sentences)
**How it works:** (step-by-step breakdown)
**Key concepts:** (list any important patterns, algorithms, or language features used)
**Potential issues:** (any bugs, edge cases, or improvements worth noting)

Code:
{code}"""
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are an expert programming tutor who explains code clearly."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=1500,
        temperature=0.5
    )
    return response.choices[0].message.content.strip()


def generate_docstrings(code: str, language: str) -> str:
    style_map = {
        'Python': 'Google-style docstrings',
        'JavaScript': 'JSDoc comments',
        'TypeScript': 'TSDoc comments',
        'Java': 'Javadoc comments',
        'Go': 'Go doc comments',
        'Rust': 'Rustdoc comments',
    }
    style = style_map.get(language, f'{language} documentation comments')
    prompt = f"""Add {style} to all functions, classes, and methods in the following {language} code.
- Only add docstrings/doc comments — do not add inline comments.
- Follow the {style} format strictly.
- Include: description, parameters (with types if available), return value, raises/errors if applicable.
- Return ONLY the code with docstrings added.

Code:
{code}"""
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are an expert at writing documentation for code."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=2000,
        temperature=0.4
    )
    return response.choices[0].message.content.strip()


@app.route("/", methods=["GET"])
def index():
    return render_template("index.html")


@app.route("/generate-comments", methods=["POST"])
def generate_comments():
    data = request.get_json(force=True)
    code = (data.get("code") or "").strip()
    level_choice = (data.get("level_choice") or "1").strip()
    lang_choice = (data.get("lang_choice") or "1").strip()

    if not code:
        return jsonify({"error": "Code is required"}), 400

    level = get_level(level_choice)
    language = get_language(lang_choice)

    try:
        result = generate_code_comments(code, level, language)
        return jsonify({"commented_code": result})
    except Exception as e:
        return jsonify({"error": f"Server error: {type(e).__name__}: {e}"}), 500


@app.route("/generate-readme", methods=["POST"])
def generate_readme_route():
    data = request.get_json(force=True)
    code = (data.get("code") or "").strip()
    lang_choice = (data.get("lang_choice") or "1").strip()

    if not code:
        return jsonify({"error": "Code is required"}), 400

    language = get_language(lang_choice)
    try:
        result = generate_readme(code, language)
        return jsonify({"output": result})
    except Exception as e:
        return jsonify({"error": f"Server error: {type(e).__name__}: {e}"}), 500


@app.route("/explain-code", methods=["POST"])
def explain_code_route():
    data = request.get_json(force=True)
    code = (data.get("code") or "").strip()
    level_choice = (data.get("level_choice") or "1").strip()
    lang_choice = (data.get("lang_choice") or "1").strip()

    if not code:
        return jsonify({"error": "Code is required"}), 400

    level = get_level(level_choice)
    language = get_language(lang_choice)
    try:
        result = explain_code(code, level, language)
        return jsonify({"output": result})
    except Exception as e:
        return jsonify({"error": f"Server error: {type(e).__name__}: {e}"}), 500


@app.route("/generate-docstrings", methods=["POST"])
def generate_docstrings_route():
    data = request.get_json(force=True)
    code = (data.get("code") or "").strip()
    lang_choice = (data.get("lang_choice") or "1").strip()

    if not code:
        return jsonify({"error": "Code is required"}), 400

    language = get_language(lang_choice)
    try:
        result = generate_docstrings(code, language)
        return jsonify({"output": result})
    except Exception as e:
        return jsonify({"error": f"Server error: {type(e).__name__}: {e}"}), 500


if __name__ == "__main__":
    app.run(debug=True)
