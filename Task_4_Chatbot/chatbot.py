import difflib
import json
import os
import re
from datetime import datetime

STOPWORDS = {
    "what", "are", "your", "of", "how", "do", "i", "my", "when", "will",
    "receive", "the", "a", "an", "is", "to", "in", "for", "can", "you", "me"
}

MOCK_ORDERS = {
    "ORD-101": "Shipped via BlueDart — Expected delivery tomorrow by 5:00 PM.",
    "ORD-205": "Delivered on Nov 18, 2026 — Signed by recipient.",
    "ORD-309": "Processing at warehouse — Dispatch scheduled within 24 hours."
}


class AdvancedTerminalAssistant:
    def __init__(self, faq_file="faq.json", log_file="chat_history.log"):
        self.faq_file = faq_file
        self.log_file = log_file
        self.greetings, self.faqs = self.load_faq_dataset()
        self.state = "ACTIVE"
        self.user_name = ""
        self.session_log = []
        self.ticket_counter = 401

    def load_faq_dataset(self):
        """Loads greetings and question-answer pairs directly from faq.json."""
        fallback_greetings = ["hello", "hi", "hey", "good morning", "good afternoon"]
        fallback_faqs = [
            {
                "question": "What are your hours of operation?",
                "answer": "We operate Monday through Friday from 9:00 AM to 6:00 PM IST."
            },
            {
                "question": "How do I submit my internship project?",
                "answer": "You can submit your public GitHub repository link through your Student Workspace."
            },
            {
                "question": "When will I receive my certificate?",
                "answer": "Certificates are reviewed and issued within 3-5 business days after your code review."
            }
        ]

        if not os.path.exists(self.faq_file):
            with open(self.faq_file, "w", encoding="utf-8") as f:
                json.dump({"greetings": fallback_greetings, "faqs": fallback_faqs}, f, indent=2)
            return fallback_greetings, fallback_faqs

        try:
            with open(self.faq_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                greetings = [g.strip().lower() for g in data.get("greetings", fallback_greetings)]
                faqs = data.get("faqs", fallback_faqs)
                return greetings, faqs
        except Exception as e:
            print(f"[System Warning] Could not read '{self.faq_file}' ({e}). Using fallback FAQs.")
            return fallback_greetings, fallback_faqs

    @staticmethod
    def get_time_greeting():
        hour = datetime.now().hour
        if hour < 12:
            return "Good morning"
        elif hour < 17:
            return "Good afternoon"
        return "Good evening"

    @staticmethod
    def normalize_text(text):
        cleaned = text.strip().lower()
        cleaned = re.sub(r"[^\w\s-]", "", cleaned)
        return cleaned

    def extract_user_name(self, raw_text):
        match = re.search(r"\b(?:my name is|i am|i'm|call me)\s+([a-zA-Z]{2,20})\b", raw_text, re.IGNORECASE)
        if match:
            self.user_name = match.group(1).capitalize()
            return True
        return False

    def is_greeting(self, normalized_query):
        """Matches against the 'greetings' list in faq.json using regex & fuzzy match."""
        for greet in self.greetings:
            if re.search(rf"\b{re.escape(greet)}\b", normalized_query):
                return True
            if difflib.SequenceMatcher(None, normalized_query, greet).ratio() >= 0.82:
                return True
        return False

    def match_faq(self, normalized_query):
        """Finds the best matching FAQ answer from faq.json using keyword overlap + fuzzy similarity."""
        query_words = {w for w in normalized_query.split() if w not in STOPWORDS}
        best_answer = None
        best_score = 0.0

        for item in self.faqs:
            question_norm = self.normalize_text(item.get("question", ""))
            question_words = {w for w in question_norm.split() if w not in STOPWORDS}

            # 1. Full-string fuzzy similarity
            seq_score = difflib.SequenceMatcher(None, normalized_query, question_norm).ratio()

            # 2. Meaningful keyword overlap + fuzzy word match (handles typos like 'certficate' or 'submt')
            keyword_hits = 0.0
            if query_words and question_words:
                for qw in query_words:
                    best_word_sim = max(
                        difflib.SequenceMatcher(None, qw, fw).ratio() for fw in question_words
                    )
                    if best_word_sim >= 0.80:
                        keyword_hits += best_word_sim
                overlap_score = keyword_hits / max(len(query_words), 1)
            else:
                overlap_score = 0.0

            combined_score = (0.45 * seq_score) + (0.55 * overlap_score)
            if combined_score > best_score:
                best_score = combined_score
                best_answer = item.get("answer")

        return best_answer if best_score >= 0.42 else None

    def handle_sub_state(self, raw_input, normalized):
        """Handles multi-turn interactive workflows."""
        if normalized in {"cancel", "back", "menu"}:
            self.state = "ACTIVE"
            return "Cancelled current action. How else can I assist you?"

        if self.state == "AWAITING_ORDER_ID":
            order_id = raw_input.strip().upper()
            self.state = "ACTIVE"
            if order_id in MOCK_ORDERS:
                return f"Order [{order_id}] Status: {MOCK_ORDERS[order_id]}"
            return f"Order ID '{order_id}' not found. Try 'ORD-101', 'ORD-205', or 'ORD-309'."

        if self.state == "AWAITING_TICKET_ISSUE":
            ticket_id = f"TCK-{self.ticket_counter}"
            self.ticket_counter += 1
            self.state = "ACTIVE"
            return (
                f"Support Ticket [{ticket_id}] logged: \"{raw_input.strip()}\"\n"
                "Our team will follow up within 1 business day."
            )

        self.state = "ACTIVE"
        return "How can I assist you?"

    def log_message(self, sender, message):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.session_log.append(f"[{timestamp}] {sender}: {message}")

    def save_transcript(self):
        with open(self.log_file, "a", encoding="utf-8") as f:
            f.write("\n" + "=" * 50 + "\n")
            f.write("\n".join(self.session_log) + "\n")

    def show_help(self):
        faq_list = "\n".join([f"  • {item['question']}" for item in self.faqs])
        return (
            "Loaded FAQ Topics (from faq.json):\n"
            f"{faq_list}\n"
            "Interactive Commands:\n"
            "  • 'track order'  - Check order delivery status\n"
            "  • 'raise ticket' - Log a support ticket\n"
            "  • 'bye' / 'exit' - Save chat transcript & exit"
        )

    def run(self):
        exit_commands = {"bye", "exit", "quit", "goodbye"}

        print("=" * 68)
        print("        DATHEON INTELLIGENT TERMINAL SUPPORT ASSISTANT")
        print("=" * 68)
        welcome = (
            f"{self.get_time_greeting()}! I'm your Datheon FAQ & Support Assistant.\n"
            "Ask me about working hours, project submission, certificates, or type 'help'."
        )
        print(f"Bot: {welcome}\n")
        self.log_message("Bot", welcome)

        while self.state != "EXIT":
            user_raw = input("You: ").strip()
            if not user_raw:
                print("Bot: Please type a question or keyword so I can help you.\n")
                continue

            self.log_message("User", user_raw)
            normalized = self.normalize_text(user_raw)

            # Exit transition
            if normalized in exit_commands or any(w in normalized.split() for w in exit_commands):
                self.state = "EXIT"
                bye_msg = f"Goodbye{', ' + self.user_name if self.user_name else ''}! Transcript saved to '{self.log_file}'."
                print(f"Bot: {bye_msg}")
                self.log_message("Bot", bye_msg)
                self.save_transcript()
                break

            # Built-in help
            if normalized == "help":
                reply = self.show_help()
                print(f"Bot: {reply}\n")
                self.log_message("Bot", reply)
                continue

            # Multi-turn follow-up states
            if self.state != "ACTIVE":
                reply = self.handle_sub_state(user_raw, normalized)
                print(f"Bot: {reply}\n")
                self.log_message("Bot", reply)
                continue

            # Name memory
            if self.extract_user_name(user_raw):
                reply = f"Nice to meet you, {self.user_name}! What would you like to ask?"
                print(f"Bot: {reply}\n")
                self.log_message("Bot", reply)
                continue

            # Multi-turn interactive triggers
            if re.search(r"\b(track|order|shipping|delivery)\b", normalized):
                self.state = "AWAITING_ORDER_ID"
                reply = "Please enter your Order ID (e.g., ORD-101, ORD-205, or ORD-309):"
                print(f"Bot: {reply}\n")
                self.log_message("Bot", reply)
                continue

            if re.search(r"\b(ticket|issue|bug|complaint)\b", normalized):
                self.state = "AWAITING_TICKET_ISSUE"
                reply = "Please briefly describe the issue to log a support ticket:"
                print(f"Bot: {reply}\n")
                self.log_message("Bot", reply)
                continue

            # Greeting check from faq.json
            if self.is_greeting(normalized):
                name_part = f", {self.user_name}" if self.user_name else ""
                reply = f"Hello{name_part}! How can I help you today? You can ask about hours, project submission, or certificates."
                print(f"Bot: {reply}\n")
                self.log_message("Bot", reply)
                continue

            # FAQ dataset lookup from faq.json
            faq_answer = self.match_faq(normalized)
            if faq_answer:
                print(f"Bot: {faq_answer}\n")
                self.log_message("Bot", faq_answer)
            else:
                fallback = (
                    "Sorry, I didn't find an exact match for that. Try asking about "
                    "'hours of operation', 'how to submit my project', 'certificate timeline', or type 'help'."
                )
                print(f"Bot: {fallback}\n")
                self.log_message("Bot", fallback)


if __name__ == "__main__":
    assistant = AdvancedTerminalAssistant()
    assistant.run()