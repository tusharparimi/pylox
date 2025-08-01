import sys
from scanner import Scanner
from tokens import Token
from error import ErrorReporter

class Pylox:
    @staticmethod
    def main():
        if len(sys.argv) > 2: # 2 cause python always takes .py file name as first argument
            print("Usage: pylox [script]")
            sys.exit(64)
        elif len(sys.argv) == 2: Pylox.run_file(sys.argv[1])
        else: Pylox.run_prompt()

    @staticmethod
    def run_file(path: str): 
        with open(path, encoding="utf-8", mode="r") as file:
            src_string: str = file.read()
        Pylox.run(src_string)
        if ErrorReporter.had_error: sys.exit(65)

    @staticmethod
    def run_prompt():
        while True:
            try:
                line: str = input(">>> ")
                Pylox.run(line)
                ErrorReporter.had_error = False
            except EOFError: break

    @staticmethod
    def run(src: str):
        scanner = Scanner(src)
        tokens: list[Token] = scanner.scan_tokens()

        for token in tokens: print(token)


if __name__ == "__main__":
    Pylox.main()