import os
import shutil
import sys
import psutil
import json
import subprocess
import shlex

# For enhanced UI (history and auto-completion)
from prompt_toolkit import prompt
from prompt_toolkit.history import FileHistory
from prompt_toolkit.completion import Completer, Completion, WordCompleter, PathCompleter
from prompt_toolkit.document import Document
from dotenv import load_dotenv

# --- Core Terminal Command Functions ---

def list_directory(args):
    """Lists files and directories in the specified path."""
    path = args[0] if args else '.'
    try:
        items = os.listdir(path)
        for item in items:
            if os.path.isdir(os.path.join(path, item)):
                print(f"\033[94m{item}/\033[0m") # Blue color for directories
            else:
                print(item)
    except FileNotFoundError:
        print(f"ls: cannot access '{path}': No such file or directory")
    except Exception as e:
        print(f"ls: an unexpected error occurred: {e}")

def change_directory(args):
    """Changes the current working directory."""
    if not args:
        path = os.path.expanduser('~')
    else:
        path = args[0]
    try:
        os.chdir(path)
    except FileNotFoundError:
        print(f"cd: no such file or directory: {path}")
    except Exception as e:
        print(f"cd: an unexpected error occurred: {e}")

def print_working_directory(args):
    """Prints the current working directory."""
    try:
        print(os.getcwd())
    except Exception as e:
        print(f"pwd: an unexpected error occurred: {e}")

def make_directory(args):
    """Creates a new directory."""
    if not args:
        print("mkdir: missing operand")
        return
    path = args[0]
    try:
        os.mkdir(path)
        print(f"Created directory: {path}")
    except FileExistsError:
        print(f"mkdir: cannot create directory ‘{path}’: File exists")
    except Exception as e:
        print(f"mkdir: an unexpected error occurred: {e}")

def remove_item(args):
    """Removes a file or directory."""
    if not args:
        print("rm: missing operand")
        return
    
    path = args[0]
    is_recursive = '-r' in args or '-R' in args
    
    try:
        if os.path.isfile(path):
            os.remove(path)
            print(f"Removed file: {path}")
        elif os.path.isdir(path):
            if not os.listdir(path) : # Directory is empty
                 os.rmdir(path)
                 print(f"Removed empty directory: {path}")
            elif is_recursive:
                shutil.rmtree(path)
                print(f"Recursively removed directory: {path}")
            else:
                 print(f"rm: cannot remove '{path}': Is a non-empty directory. Use -r to remove recursively.")
        else:
            print(f"rm: cannot remove '{path}': No such file or directory")
    except Exception as e:
        print(f"rm: an unexpected error occurred: {e}")

def system_monitor(args):
    """Displays CPU and Memory usage."""
    try:
        cpu_usage = psutil.cpu_percent(interval=1)
        memory_info = psutil.virtual_memory()
        print("--- System Monitor ---")
        print(f"CPU Usage:    {cpu_usage}%")
        print(f"Memory Usage: {memory_info.percent}%")
        print(f"Total Memory: {memory_info.total / (1024**3):.2f} GB")
        print(f"Used Memory:  {memory_info.used / (1024**3):.2f} GB")
        print("----------------------")
    except Exception as e:
        print(f"monitor: an unexpected error occurred: {e}")

def exit_terminal(args):
    """Exits the terminal application."""
    print("Exiting terminal. Goodbye!")
    sys.exit(0)
    
def touch_file(args):
    """Creates an empty file."""
    if not args:
        print("touch: missing file operand")
        return
    file_path = args[0]
    try:
        with open(file_path, 'a'):
            os.utime(file_path, None)
        print(f"Created file: {file_path}")
    except Exception as e:
        print(f"touch: an unexpected error occurred: {e}")

def move_item(args):
    """Moves or renames a file or directory."""
    if len(args) < 2:
        print("mv: missing destination file operand after source")
        return
    source, destination = args[0], args[1]
    try:
        shutil.move(source, destination)
        print(f"Moved '{source}' to '{destination}'")
    except FileNotFoundError:
        print(f"mv: cannot stat '{source}': No such file or directory")
    except Exception as e:
        print(f"mv: an unexpected error occurred: {e}")

# --- AI-Powered Command Translation ---

def handle_ai_command(user_query):
    """Translates natural language to a shell command using Gemini API."""
    print("🤖 Thinking...")
    API_KEY = os.getenv("GEMINI_API_KEY")
    if not API_KEY:
        print("\033[91mAI Error: GEMINI_API_KEY not found.\033[0m")
        print("Please create a file named '.env' in the same directory and add your key like this:")
        print("GEMINI_API_KEY='your_api_key_here'")
        return None

    API_URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-preview-05-20:generateContent?key={API_KEY}"
    
    # This prompt guides the AI to give us only the command.
    system_prompt = (
        "You are an expert system that translates natural language into a single, "
        "executable shell command for a basic terminal that supports ls, cd, pwd, "
        "mkdir, rm, touch, mv, and monitor. You must only respond with the single, "
        "best-fit command and nothing else. You can chain commands with '&&'. For example, "
        "if the user says 'go to the parent folder and list its contents', you should respond with 'cd .. && ls'. "
        "If the command is ambiguous or you cannot determine a command, respond with 'UNKNOWN'."
    )
    
    payload = {
        "contents": [{"parts": [{"text": user_query}]}],
        "systemInstruction": {"parts": [{"text": system_prompt}]}
    }
    
    try:
        import requests
        response = requests.post(API_URL, json=payload, headers={'Content-Type': 'application/json'})
        response.raise_for_status() # Raise an exception for bad status codes
        
        result = response.json()
        command = result['candidates'][0]['content']['parts'][0]['text'].strip()
        
        if command == "UNKNOWN":
            print("Sorry, I couldn't understand that. Please try rephrasing.")
            return None
        
        print(f"🤖 Understood! Executing: \033[92m{command}\033[0m") # Green color for command
        return command
        
    except requests.exceptions.RequestException as e:
        print(f"AI Error: Could not connect to the AI service. {e}")
        return None
    except (KeyError, IndexError):
        print("AI Error: Received an unexpected response from the AI service.")
        return None
    except ImportError:
        print("AI Error: 'requests' library not found. Please run 'pip install requests'.")
        return None

# --- Custom Completer for AI and Commands ---

class AITerminalCompleter(Completer):
    """
    Smarter completer that offers contextual word-by-word suggestions for the 'ai' command
    and can complete file paths where appropriate.
    """
    def __init__(self, command_dict, ai_patterns):
        self.command_completer = WordCompleter(list(command_dict.keys()) + ['ai'], ignore_case=True)
        self.ai_patterns = ai_patterns
        self.path_completer = PathCompleter()

    def get_completions(self, document, complete_event):
        text = document.text_before_cursor
        words = text.split()

        # Handle standard command completion if not using 'ai' or just typing 'ai'
        if not words or (words[0] != 'ai' or (len(words) == 1 and not text.endswith(' '))):
            yield from self.command_completer.get_completions(document, complete_event)
            return

        # --- We are building an AI command ---
        ai_words = words[1:]
        
        # If the last word suggests a path is next, use the PathCompleter
        path_triggers = ['file', 'folder', 'directory', 'called', 'named', 'of', 'to']
        if ai_words and ai_words[-1] in path_triggers and text.endswith(' '):
            # Pass a new document that only contains the part to be completed as a path
            path_doc_text = document.get_word_before_cursor()
            path_doc = Document(path_doc_text, cursor_position=len(path_doc_text))
            yield from self.path_completer.get_completions(path_doc, complete_event)
            return

        # Traverse the pattern tree to find the current context
        current_level = self.ai_patterns
        for word in ai_words:
            if isinstance(current_level, dict) and word in current_level:
                current_level = current_level[word]
            else:
                current_level = None
                break
        
        # If we have a valid context, offer suggestions
        if isinstance(current_level, dict):
            word_to_complete = document.get_word_before_cursor() if not text.endswith(' ') else ''
            for suggestion in current_level.keys():
                if suggestion.startswith(word_to_complete):
                    yield Completion(suggestion, start_position=-len(word_to_complete))


def main():
    """Main function to run the terminal loop."""
    load_dotenv() # Load variables from .env file into the environment
    commands = {
        'ls': list_directory, 'cd': change_directory, 'pwd': print_working_directory,
        'mkdir': make_directory, 'rm': remove_item, 'monitor': system_monitor,
        'exit': exit_terminal, 'touch': touch_file, 'mv': move_item,
    }
    
    # Define a nested dictionary for more intelligent, contextual completions
    # 'None' marks the end of a valid phrase.
    ai_patterns = {
        "create": {"a": {"new": {"folder": {"called": None}, "file": {"named": None}}}},
        "move": {"the": {"file": {}}}, # Empty dict allows path completion
        "rename": {"the": {"file": {}, "to": None}},
        "delete": {"the": {"file": {}, "folder": {}}},
        "list": {"the": {"contents": {"of": {}}}},
        "show": {"me": {"the": {"current": {"directory": None}}}},
        "tell": {"me": {"the": {"system": {"status": None}}}},
    }
    
    # Setup for history and our custom auto-completion
    terminal_completer = AITerminalCompleter(commands, ai_patterns)
    history = FileHistory('.terminal_history.txt')

    while True:
        try:
            current_dir = os.path.basename(os.getcwd())
            prompt_message = f"🚀 py-term:{current_dir}$ "
            
            user_input = prompt(
                prompt_message,
                history=history,
                completer=terminal_completer,
            )

            if not user_input.strip():
                continue

            command_to_process = user_input

            # Check if it's an AI command that needs translation first
            try:
                first_segment = user_input.split('&&')[0]
                first_parts = shlex.split(first_segment)
                if first_parts and first_parts[0] == 'ai':
                    nl_parts = shlex.split(user_input)
                    natural_language_query = " ".join(nl_parts[1:])

                    if not natural_language_query:
                        print("Usage: ai <your command in plain English>")
                        continue
                    
                    translated = handle_ai_command(natural_language_query)
                    if translated:
                        command_to_process = translated
                    else:
                        continue # AI failed, restart loop
            except (ValueError, IndexError):
                pass # Let the main pipeline handler catch errors

            # Now, process the command pipeline, whether from user or AI
            command_pipeline = command_to_process.split('&&')
            is_first_command = True

            for command in command_pipeline:
                command = command.strip()
                if not command:
                    continue
                
                # Add a separator for chained commands to improve readability
                if not is_first_command:
                    print("-" * 20)
                is_first_command = False

                try:
                    parts = shlex.split(command)
                    if not parts:
                        continue
                    
                    command_name = parts[0]
                    args = parts[1:]

                    if command_name in commands:
                        commands[command_name](args)
                    else:
                        print(f"{command_name}: command not found")
                except ValueError:
                    print(f"Error: Unmatched quotes in command segment: '{command}'")
                    continue
        
        except KeyboardInterrupt:
            print("\nUse 'exit' to quit.")
        except EOFError:
            print("\nExiting terminal. Goodbye!")
            break

if __name__ == "__main__":
    main()