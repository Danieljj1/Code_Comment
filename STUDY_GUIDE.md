# Code Comment — Project Study Guide

Use this file to prepare to explain Code Comment confidently to anyone: an interviewer, a friend, or a recruiter. Work through each section in order.

---

## 1. The 30-Second Pitch

> *What is it, who is it for, and what problem does it solve?*

**Code Comment is an AI-powered web tool** that takes raw source code and helps developers document it. You paste your code, pick your programming language and explanation level, and it can: add inline comments at the right verbosity, generate a professional README, explain the code in plain English, or add formal docstrings (Google-style for Python, JSDoc for JavaScript, etc.). It's built with Flask and the OpenAI API.

Practice saying this out loud until it takes under 30 seconds and feels natural.

---

## 2. Technical Architecture

```
User Browser (HTML form)
         |
         | HTTP POST / JSON
         v
   Flask Backend (Python)
         |
         | API call
         v
  OpenAI GPT-4o-mini
         |
    Returns AI response
         |
         v
   JSON response to browser
```

### Tech Stack at a Glance

| Layer | Technology | Why This Choice |
|---|---|---|
| Backend | Python + Flask | Single-file app; Flask is ideal when you just need a few routes |
| AI | OpenAI GPT-4o-mini | 15x cheaper than GPT-4o, quality difference minimal for code tasks |
| Frontend | HTML + Jinja2 templates | No framework needed — the UI is simple enough |
| Deployment | Render | Free tier, easy deploy from GitHub |

---

## 3. The Four Features — Know Each One

The entire app is built around four AI-powered actions. Each calls a separate Flask route and has its own tailored prompt.

### Feature 1: Generate Comments (`/generate-comments`)
- **What it does**: Adds inline comments throughout the code
- **Prompt key detail**: Tells the model to match verbosity to the selected level (Beginner = explain everything, Advanced = only non-obvious parts)
- **Returns**: The original code with comments added — no other text

### Feature 2: Generate README (`/generate-readme`)
- **What it does**: Creates a professional `README.md` for the code
- **Prompt key detail**: Instructs the model to include Description, Requirements, Usage, Parameters, Returns, and Notes — *only if relevant*
- **Returns**: A complete markdown README

### Feature 3: Explain Code (`/explain-code`)
- **What it does**: Explains what the code does in plain English, structured in four sections
- **Prompt key detail**: Each level gets different instructions — Beginner = analogies and simple language, Advanced = design decisions and complexity analysis
- **Returns**: Structured explanation with What it does / How it works / Key concepts / Potential issues

### Feature 4: Generate Docstrings (`/generate-docstrings`)
- **What it does**: Adds formal documentation comments to all functions and classes
- **Prompt key detail**: Uses language-specific styles — Google-style for Python, JSDoc for JavaScript/TypeScript, Javadoc for Java, Rustdoc for Rust
- **Returns**: Code with only docstrings added (no inline comments)

---

## 4. How It Works — The Request/Response Cycle

1. User pastes code into the browser form
2. User selects language (1–10) and level (1–3)
3. Browser POSTs JSON to the appropriate Flask route (e.g., `POST /generate-comments`)
4. Flask calls the matching function (e.g., `generate_code_comments(code, level, language)`)
5. That function builds a specific system prompt and sends it to `client.chat.completions.create()`
6. OpenAI returns the AI-generated text
7. Flask returns it as JSON: `{"commented_code": "..."}` or `{"output": "..."}`
8. Browser displays the result

---

## 5. Key Files and What They Do

```
ai_code_comment.py    — The entire backend (Flask app + all AI logic)
templates/
  index.html          — The frontend form and result display
requirements.txt      — flask, openai
render.yaml           — Render deployment config
```

### Inside `ai_code_comment.py`

```python
LANGUAGES = { '1': 'Python', '2': 'JavaScript', ... }   # 10 languages
LEVELS = { '1': 'Beginner', '2': 'Intermediate', '3': 'Advanced' }

def generate_code_comments(code, level, language) -> str  # Feature 1
def generate_readme(code, language) -> str                # Feature 2
def explain_code(code, level, language) -> str            # Feature 3
def generate_docstrings(code, language) -> str            # Feature 4

@app.route("/generate-comments", methods=["POST"])   # Route for Feature 1
@app.route("/generate-readme",   methods=["POST"])   # Route for Feature 2
@app.route("/explain-code",      methods=["POST"])   # Route for Feature 3
@app.route("/generate-docstrings", methods=["POST"]) # Route for Feature 4
```

---

## 6. Prompt Engineering — The Most Important Concept

The quality of each feature depends entirely on how the prompt is written. Here are the key techniques used:

### Technique 1: Output format constraint
```
"Return ONLY the commented code — no explanations before or after."
```
This stops the model from adding filler text like "Sure! Here is your commented code:" which would break the display.

### Technique 2: Low temperature for consistency
```python
temperature=0.5  # or 0.4
```
Lower temperature = less randomness = more predictable, accurate output. This is correct for documentation tasks where creativity is not wanted.

### Technique 3: Level-specific instructions
```python
level_instructions = {
    'Beginner': 'Explain as if to someone who is new to programming. Avoid jargon, use analogies.',
    'Intermediate': 'Assume basic programming knowledge...',
    'Advanced': 'Assume expert knowledge. Focus on design decisions, complexity, edge cases...',
}
```
The same code gets a completely different explanation depending on who's reading it.

### Technique 4: Language-specific docstring styles
```python
style_map = {
    'Python': 'Google-style docstrings',
    'JavaScript': 'JSDoc comments',
    'TypeScript': 'TSDoc comments',
    'Java': 'Javadoc comments',
}
```
This makes the output look native to each language rather than generic.

---

## 7. Concepts You Can Explain

- **Prompt engineering** — Writing precise instructions to get consistent, usable AI output
- **Temperature in LLMs** — Lower = more deterministic/accurate, higher = more creative/varied
- **System vs. user messages** — System message sets the AI's persona/role; user message is the actual input
- **API integration** — Using `client.chat.completions.create()` to call OpenAI, parsing the response
- **Flask routing** — `@app.route()` decorator maps URLs to Python functions
- **JSON as API protocol** — `request.get_json()` to read input, `jsonify()` to send output
- **Error handling** — Returning `400` for missing code, `500` for server errors with descriptive messages
- **Jinja2 templating** — `render_template('index.html')` serves the frontend from Flask

---

## 8. Interview Q&A — Practice These Out Loud

**Q: Walk me through what Code Comment does.**
> A: It's a web tool where you paste source code and choose a programming language and explanation level. Then you pick one of four actions: add inline comments, generate a README, get a plain-English explanation of what the code does, or add formal docstrings. Each action sends the code to OpenAI's API with a specifically crafted prompt, and the result is displayed back in the browser.

**Q: Why did you use GPT-4o-mini instead of GPT-4o?**
> A: For code documentation tasks, the quality difference between GPT-4o and GPT-4o-mini is minimal, but the cost difference is about 15x. Since this app makes one API call per button click, using GPT-4o-mini makes the app practical to run without burning through API credits. For a task that requires nuanced reasoning, I'd choose a more powerful model.

**Q: How do you get consistent output from the AI?**
> A: Two main ways. First, I use a low temperature (0.4–0.5) to reduce randomness — documentation tasks need accuracy, not creativity. Second, I write very explicit output format instructions in the prompt, like "Return ONLY the commented code — no explanations before or after." Without that constraint, the model often adds conversational text that would break the UI.

**Q: What's the difference between the system message and user message?**
> A: The system message sets the model's role and behavior — for example, "You are an expert code commenter" — and it persists across the conversation. The user message is the actual input for this specific request — the code plus the instructions. Separating them is an OpenAI convention that helps the model stay in character.

**Q: What's the hardest part of building an AI-powered app?**
> A: Prompt engineering — getting the AI to return output in exactly the format you need, every time. The model is probabilistic, so vague prompts produce unpredictable results. I learned to be extremely specific: specify the format, explicitly forbid things you don't want (like extra text), and test with edge cases like empty code or unusual languages.

**Q: What would you add next?**
> A: A few things: syntax highlighting in the output so the commented code looks like real code, a copy-to-clipboard button, and token counting before the API call so I can warn users if their code is too large. Long-term, I'd add support for uploading files directly instead of pasting.

---

## 9. Weak Points & Honest Answers

- **No input validation on size**: If someone pastes a 10,000-line file, the API call will either fail or be very expensive. I'd add token counting before submitting.
- **API key security**: The OpenAI key is an environment variable (correct), but there's no rate limiting on the Flask server — a bad actor could spam the endpoint and drain API credits.
- **No error recovery in the UI**: If the API call fails, the user just sees an error string. A better UX would retry once automatically or show a more helpful message.
- **Single-file architecture**: `ai_code_comment.py` does everything. For a larger app, I'd split routes, AI logic, and config into separate modules.

---

## 10. Self-Test Checklist

- [ ] Can I name all four features and what each one does?
- [ ] Can I explain what temperature does in an LLM in one sentence?
- [ ] Can I explain the difference between system and user messages?
- [ ] Can I explain why I used GPT-4o-mini over GPT-4o?
- [ ] Can I explain what prompt engineering is and give a concrete example from this project?
- [ ] Can I describe one honest limitation and how I'd fix it?
- [ ] Can I give the 30-second pitch without notes?

---

## 11. One-Line Answers for Small Talk

- **"What's Code Comment?"** → "An AI tool that takes raw code and adds comments, generates a README, or explains what the code does — you pick the language and how detailed you want the explanation."
- **"What tech did you use?"** → "Python Flask for the backend, OpenAI's API for the AI, and a simple HTML frontend."
- **"What did you learn building it?"** → "Prompt engineering — getting the AI to return exactly the format you need, consistently, took a lot of iteration."
