"""FinGenius command-line chat.

Run an interactive conversation with the LangGraph financial advisor agent:

    python main.py

Type 'exit' or 'quit' to leave.
"""

import uuid

from fingenius.agent import chat


def main() -> None:
    print("=" * 60)
    print("  FinGenius - AI Personal Finance Advisor")
    print("  Ask about budgeting, saving, debt, loans, investing.")
    print("  Type 'exit' or 'quit' to leave.")
    print("=" * 60)

    thread_id = str(uuid.uuid4())  # one conversation per session

    while True:
        try:
            user_input = input("\nYou: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nGoodbye!")
            break

        if not user_input:
            continue
        if user_input.lower() in {"exit", "quit"}:
            print("Goodbye!")
            break

        try:
            reply = chat(user_input, thread_id=thread_id)
        except Exception as exc:  # surface config/API errors plainly
            print(f"\n[error] {exc}")
            continue

        print(f"\nFinGenius: {reply}")


if __name__ == "__main__":
    main()
