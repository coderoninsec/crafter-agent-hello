import sys
from agent import run_agent


def main():
    try:
        prompt = " ".join(sys.argv[1:]) if len(sys.argv) > 1 else input("Input > ")
    except (KeyboardInterrupt, EOFError):
        print("\nBye")
        return

    if not prompt.strip():
        print("Input vacío. Intenta de nuevo.")
        return

    prompt = " ".join(prompt.split())
    print(run_agent(prompt))


if __name__ == "__main__":
    main()
