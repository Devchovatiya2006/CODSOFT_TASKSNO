import re
import random
import datetime


# ── Predefined Rules ──────────────────────────────────────────────────────────
RULES = [
    {
        "patterns": [r"\b(hi|hello|hey|hola|howdy|greetings|good morning|good afternoon|good evening)\b"],
        "responses": [
            "Hello! 👋 How can I help you today?",
            "Hey there! What's on your mind?",
            "Hi! Great to see you. How can I assist?",
        ],
        "intent": "greeting",
    },
    {
        "patterns": [r"my name is (?P<name>[A-Za-z]+)", r"i am (?P<name>[A-Za-z]+)", r"call me (?P<name>[A-Za-z]+)", r"i'm (?P<name>[A-Za-z]+)"],
        "responses": ["Nice to meet you, {name}! 😊 How can I help you?", "Great to know you, {name}! What would you like to talk about?"],
        "intent": "set_name",
    },
    {
        "patterns": [r"what is my name", r"do you know my name", r"who am i"],
        "responses": ["__NAME__"],
        "intent": "get_name",
    },
    {
        "patterns": [r"how are you", r"how r u", r"how's it going", r"how do you do", r"you good", r"what'?s up"],
        "responses": [
            "I'm doing great, thanks for asking! 😄 How about you?",
            "All systems running smoothly! How can I help?",
            "Feeling fantastic and ready to chat! What's on your mind?",
        ],
        "intent": "how_are_you",
    },
    {
        "patterns": [r"i('m| am) (good|great|fine|awesome|fantastic|happy|wonderful|doing well)", r"not bad", r"pretty good"],
        "responses": ["That's great to hear! 😊 What can I do for you?", "Awesome! Let me know if there's anything I can help with. 🌟"],
        "intent": "user_good",
    },
    {
        "patterns": [r"i('m| am) (sad|tired|bored|stressed|upset|not good|not great|bad|terrible|awful|down)", r"having a bad day", r"i feel (bad|terrible|awful|down)"],
        "responses": [
            "I'm sorry to hear that. 💙 I hope things get better soon! Is there anything I can do?",
            "That sounds tough. I'm here if you want to chat! 😊",
        ],
        "intent": "user_bad",
    },
    {
        "patterns": [r"who are you", r"what are you", r"what is your name", r"are you a bot", r"are you (human|ai|robot|chatbot)", r"tell me about yourself"],
        "responses": [
            "I'm RuleBot 🤖 — a rule-based chatbot built with Python! I use pattern matching to understand your messages.",
            "I'm RuleBot! A conversational AI that chats, does math, tells jokes, and more. Ask me anything!",
        ],
        "intent": "identity",
    },
    {
        "patterns": [r"how old are you", r"what is your age", r"when were you (born|created|built|made)"],
        "responses": ["I was just built recently as a Python project! Age is just a number for a bot. 😄", "I'm brand new — fresh out of the Python oven! 🐍"],
        "intent": "age",
    },
    {
        "patterns": [r"what (is|'s) the time", r"current time", r"what time is it", r"tell me the time"],
        "responses": ["__TIME__"],
        "intent": "time",
    },
    {
        "patterns": [r"what (is|'s) (today'?s? )?date", r"what day is (today|it)", r"today'?s? date", r"what'?s? the date"],
        "responses": ["__DATE__"],
        "intent": "date",
    },
    {
        "patterns": [r"calculate (?P<expr>[0-9\+\-\*/\(\)\.\s]+)", r"what is (?P<expr>[0-9][0-9\+\-\*/\(\)\.\s]+)", r"solve (?P<expr>[0-9\+\-\*/\(\)\.\s]+)", r"compute (?P<expr>[0-9\+\-\*/\(\)\.\s]+)", r"(?P<expr>[0-9]+\s*[\+\-\*/]\s*[0-9]+)"],
        "responses": ["__MATH__"],
        "intent": "math",
    },
    {
        "patterns": [r"tell me a joke", r"make me laugh", r"know any jokes", r"another joke", r"say something funny", r"joke please", r"\bjoke\b"],
        "responses": [
            "Why do programmers prefer dark mode? Because light attracts bugs! 🐛",
            "There are 10 types of people: those who understand binary, and those who don't! 💻",
            "Why did the Python developer sell their house? They couldn't find the right indentation! 😄",
            "A SQL query walks into a bar and asks two tables: 'Can I join you?' 😂",
            "Why do Java developers wear glasses? Because they don't C#! 👓",
            "I told my computer I needed a break. Now it won't stop sending me Kit-Kat ads. 🍫",
        ],
        "intent": "joke",
    },
    {
        "patterns": [r"tell me a (fun )?fact", r"random fact", r"something interesting", r"did you know", r"\btrivia\b", r"surprise me"],
        "responses": [
            "🤓 Honey never spoils! Archaeologists found 3000-year-old honey in Egyptian tombs that was still edible.",
            "🤓 Octopuses have three hearts — two pump blood to the gills, one to the rest of the body!",
            "🤓 The first computer bug was a real bug — a moth found in a Harvard Mark II computer in 1947! 🦗",
            "🤓 Python was named after Monty Python's Flying Circus, not the snake! 🐍",
            "🤓 Bananas are slightly radioactive due to potassium — but totally safe to eat! 🍌",
        ],
        "intent": "trivia",
    },
    {
        "patterns": [r"what is python", r"tell me about python", r"what is nlp", r"what is (machine learning|ml)", r"what is (artificial intelligence|ai)", r"what is (deep learning|neural network)", r"how does (rule.based|this chatbot) work"],
        "responses": [
            "**Python** is a high-level programming language loved for its readability and powerful libraries like Flask, NumPy, and TensorFlow! 🐍",
            "**NLP (Natural Language Processing)** lets computers understand and generate human language — it powers chatbots and voice assistants! 🗣️",
            "**Machine Learning** is a subset of AI where systems learn from data to make predictions without being explicitly programmed for each task.",
            "**Rule-based chatbots** use predefined patterns (like Regex) to match inputs to responses — fast, predictable, and no training data needed!",
            "**Artificial Intelligence** simulates human intelligence in machines — including learning, reasoning, and understanding language.",
        ],
        "intent": "tech_info",
    },
    {
        "patterns": [r"what is codsoft", r"tell me about codsoft", r"codsoft task", r"about this project", r"what is this chatbot"],
        "responses": [
            "CodSoft is an internship program with hands-on tech projects! 🎓 This is the **Rule-Based Chatbot** task — built with Python, Flask, and Regex pattern matching.",
            "This chatbot was built for the **CodSoft AI/Python Internship** to demonstrate intent detection, pattern matching, and conversation flow!",
        ],
        "intent": "codsoft",
    },
    {
        "patterns": [r"what('s| is) the weather", r"will it rain", r"is it (hot|cold|sunny|raining|snowing)", r"weather (today|tomorrow|forecast)"],
        "responses": [
            "I don't have live weather data, but check **weather.com** or Google your city + 'weather' for instant results! ☀️🌧️",
            "I can't check the weather, but your phone's assistant can! Try asking Siri or Google. 🌤️",
        ],
        "intent": "weather",
    },
    {
        "patterns": [r"what (is|are) your (favorite|favourite)", r"do you (like|love|enjoy)", r"what do you like", r"do you have (hobbies|preferences)"],
        "responses": [
            "As a bot I don't have preferences — but if I did, **Python** would be my favourite language! 🐍",
            "I don't experience things like humans, but I'm passionate about helping people and solving problems! 💡",
        ],
        "intent": "preferences",
    },
    {
        "patterns": [r"what is the meaning of life", r"why are we here", r"purpose of life", r"is there a god", r"what happens after death"],
        "responses": [
            "The classic question! 🤔 Philosophers have debated this for centuries. Some say **42** (thanks Douglas Adams!). What do you think?",
            "Deep question! I'll leave the existential answers to philosophers — but I think meaning comes from what *you* make of your experiences. 🌟",
        ],
        "intent": "philosophy",
    },
    {
        "patterns": [r"i('m| am) bored", r"i have nothing to do", r"entertain me", r"nothing to do"],
        "responses": [
            "Let's fix that! 🎉\n• Ask me to **tell you a joke** 😄\n• Try **'calculate 999 * 888'**\n• Ask for a **random fact**\n• Say **'help'** to see everything I can do!",
        ],
        "intent": "bored",
    },
    {
        "patterns": [r"you('re| are) (smart|clever|amazing|great|awesome|cool|helpful|good|brilliant)", r"i like you", r"you'?re the best", r"good bot", r"well done", r"nice work"],
        "responses": [
            "Thank you so much! That really means a lot. 😊 How can I keep helping you?",
            "Aww, you're too kind! 🌟 I'm just doing my best to be helpful!",
        ],
        "intent": "compliment",
    },
    {
        "patterns": [r"thank you", r"thanks", r"\bty\b", r"\bthx\b", r"that('s| was) (helpful|great|amazing|perfect)", r"appreciate it", r"much appreciated"],
        "responses": [
            "You're very welcome! Let me know if you need anything else. 😊",
            "Glad I could help! Feel free to ask more anytime. 🌟",
            "Anytime! That's what I'm here for. 😄",
        ],
        "intent": "thanks",
    },
    {
        "patterns": [r"\b(help|what can you do|capabilities|options|commands|menu)\b", r"what can i ask you", r"what do you know"],
        "responses": [
            "Here's what I can do! 🚀\n\n💬 **Chat** — greetings, small talk, feelings\n👤 **Remember your name** — say 'my name is Alex'\n🧮 **Math** — say 'calculate 25 * 4'\n🕒 **Time & Date** — say 'what time is it?'\n😄 **Jokes** — say 'tell me a joke'\n🤓 **Fun facts** — say 'tell me a fact'\n💡 **Tech info** — ask about Python, AI, NLP\n🎓 **CodSoft info** — ask 'what is CodSoft?'\n\nJust type naturally and I'll do my best!"
        ],
        "intent": "help",
    },
    {
        "patterns": [r"\b(bye|goodbye|see you|farewell|cya|see ya|take care|good night|goodnight|gotta go)\b"],
        "responses": [
            "Goodbye! Have a fantastic day! 👋",
            "Farewell! Come back anytime. 😊",
            "Bye! It was great chatting with you! 🌟",
        ],
        "intent": "farewell",
    },
]

FALLBACKS = [
    "That's interesting! 🤔 I'm a rule-based bot so I might not have an answer for that. Type **'help'** to see what I can do!",
    "Hmm, I don't have a rule for that yet. 💭 Try typing **'help'** to see my capabilities!",
    "I didn't quite catch that! Could you rephrase? Or type **'help'** for topics I understand. 😊",
    "Great question, but it's outside my knowledge! 🤖 Type **'help'** to see what I can answer.",
]


# ── Chatbot Engine ─────────────────────────────────────────────────────────────
class RuleBasedChatbot:
    def __init__(self):
        self.memory = {}  # stores user_name, last_intent, etc.

    def _eval_math(self, expr: str) -> str:
        try:
            clean = re.sub(r"[^0-9\+\-\*/\(\)\.\s]", "", expr).strip()
            if not clean:
                return "I couldn't find a valid math expression."
            result = eval(clean, {"__builtins__": None}, {})
            if isinstance(result, float) and result.is_integer():
                result = int(result)
            return f"The result of `{clean}` is **{result}** 🧮"
        except Exception:
            return f"Sorry, I couldn't evaluate that expression. Try something like 'calculate 5 * 10'."

    def _get_time(self) -> str:
        now = datetime.datetime.now()
        return f"🕒 Current time: **{now.strftime('%I:%M %p')}**"

    def _get_date(self) -> str:
        now = datetime.datetime.now()
        return f"📅 Today is **{now.strftime('%A, %B %d, %Y')}**"

    def _get_name_response(self) -> str:
        name = self.memory.get("user_name")
        if name:
            return f"Your name is **{name}**! 😊"
        return "I don't know your name yet! Tell me by saying **'My name is Alex'** and I'll remember it. 😊"

    def respond(self, user_input: str) -> dict:
        text = user_input.strip()
        if not text:
            return {"response": "Please type something! I'm listening. 😊", "intent": "empty", "confidence": 0}

        best_rule = None
        best_score = 0.0
        best_entities = {}
        best_pattern = None

        for rule in RULES:
            for pattern in rule["patterns"]:
                try:
                    match = re.search(pattern, text, re.IGNORECASE)
                    if match:
                        score = round(min(1.0, len(match.group(0)) / max(len(text), 1) + 0.35), 2)
                        if score > best_score:
                            best_score = score
                            best_rule = rule
                            best_pattern = pattern
                            best_entities = match.groupdict()
                except re.error:
                    continue

        if best_rule and best_score > 0.3:
            intent = best_rule["intent"]

            # Store name in memory
            if "name" in best_entities and best_entities["name"]:
                self.memory["user_name"] = best_entities["name"].strip().capitalize()

            chosen = random.choice(best_rule["responses"])

            # Dynamic responses
            if chosen == "__TIME__":
                response = self._get_time()
            elif chosen == "__DATE__":
                response = self._get_date()
            elif chosen == "__MATH__":
                response = self._eval_math(best_entities.get("expr", text))
            elif chosen == "__NAME__":
                response = self._get_name_response()
            else:
                # Fill template placeholders
                fmt = dict(self.memory)
                fmt.update({k: v for k, v in best_entities.items() if v})
                if "user_name" in fmt:
                    fmt["name"] = fmt["user_name"]
                try:
                    response = chosen.format(**fmt)
                except KeyError:
                    response = chosen

            self.memory["last_intent"] = intent
            return {"response": response, "intent": intent, "confidence": best_score, "pattern": best_pattern}

        return {"response": random.choice(FALLBACKS), "intent": "fallback", "confidence": 0.0, "pattern": None}

    def reset(self):
        self.memory = {}


# ── CLI mode ───────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    bot = RuleBasedChatbot()
    print("=" * 55)
    print("🤖  RuleBot — Rule-Based Chatbot  (CodSoft Task)")
    print("    Type 'exit' to quit | 'reset' to clear memory")
    print("=" * 55)
    while True:
        try:
            user = input("\nYou: ").strip()
            if not user:
                continue
            if user.lower() in ("exit", "quit"):
                print("RuleBot: Goodbye! 👋")
                break
            if user.lower() == "reset":
                bot.reset()
                print("RuleBot: Memory cleared! 🧹")
                continue
            res = bot.respond(user)
            print(f"RuleBot: {res['response']}")
            print(f"  [intent={res['intent']} | score={res['confidence']}]")
        except (KeyboardInterrupt, EOFError):
            print("\nRuleBot: Goodbye! 👋")
            break
