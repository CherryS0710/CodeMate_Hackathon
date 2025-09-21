# 🖥️ CodeMate Hackathon – AI Command Terminal

> A fully-functional command terminal built in Python for the CodeMate Hackathon, replicating real system terminal behavior while introducing modern enhancements like AI-powered command translation, smart auto-completion, and persistent command history.

---

## 🚀 Features

### ✅ Mandatory Requirements

-   **Core Commands:** Supports `ls`, `cd`, `pwd`, `mkdir`, `rm`, `touch`, and `mv`.
-   **System Monitoring:** `monitor` command displays real-time CPU and memory usage.
-   **Robust Error Handling:** Clear feedback for invalid commands or arguments.
-   **Responsive CLI:** Clean and interactive command-line interface.

### 🌟 Optional Enhancements

| Feature                    | Description                                                                                             |
| :------------------------- | :------------------------------------------------------------------------------------------------------ |
| 🧠 **AI-Powered Queries** | Use `ai` to execute tasks via natural language (e.g., `ai create a new folder called project_files`).     |
| 🔍 **Smart Auto-Completion** | Press `Tab` to complete commands; contextual suggestions for `ai` queries and file paths.               |
| 📜 **Command History** | Navigate with arrow keys; history persists across sessions.                                             |
| 🔗 **Command Chaining** | Use `&&` to execute multiple commands in sequence (e.g., `pwd && ls`).                                  |
| 🔐 **Secure API Key Handling** | A `.env` file securely manages the Gemini API key, keeping secrets out of the source code.              |

---

## ⚙️ Setup & Installation

1.  **Clone the Repository**
    ```bash
    git clone <your-repo-link>
    cd <your-repo-folder>
    ```

2.  **Install Dependencies**
    Ensure Python 3 is installed, then run:
    ```bash
    pip install -r requirements.txt
    ```

3.  **Set Up API Key**
    Create a `.env` file in the root directory and add your Gemini API key:
    ```env
    GEMINI_API_KEY="YOUR_API_KEY_HERE"
    ```

4.  **Run the Terminal**
    ```bash
    python terminal.py
    ```

---

## 📖 How to Use

-   **Standard Commands:** Type any of the supported commands (e.g., `ls`, `cd ..`, `monitor`).
-   **AI Commands:** Type `ai` followed by your request in plain English (e.g., `ai create a file named report.txt`).
-   **Exit:** Type `exit` to close the terminal.
-   **Note on Tab Key:** In some terminals, you may need to press `Esc` then `Tab` to trigger auto-completion.
