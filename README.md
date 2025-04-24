# 🧠🔧 Autonomous Planning Agent

An intelligent agent that can **plan, generate, and verify Python code** for complex tasks — powered by a LangGraph agentic workflow, Jupyter kernel execution, and prompt-engineered subtask decomposition. Just give it a goal, and it does the rest!

---

## Demo Video
https://github.com/Shreyankthehacker/Planning-agent/blob/main/Screencast%20from%2024-04-25%2002%3A15%3A55%20PM%20IST.webm


## 🚀 Features

- 🧩 **Task Decomposition**: Automatically breaks down high-level user queries into smaller, manageable sub-tasks.
- 🧑‍💻 **Code Generation**: Writes clean, functional Python code for each sub-task using LLM prompts.
- ✅ **Live Code Execution**: Executes generated code in a Jupyter kernel to validate and test.
- 🧠 **Tool-Driven Agent**: Uses LangGraph with dynamic tool routing (e.g., code writer, executor, summarizer).
- 📋 **Final Report**: Outputs all subtasks, code snippets, and their results step-by-step.

---

## 📂 Project Structure

https://github.com/Shreyankthehacker/Planning-agent/blob/main/Screenshot%20from%202025-04-24%2014-17-21.png

---

## 💡 How It Works

1. **User Input**: A high-level instruction is given (e.g., _“Write a Fibonacci sequence generator and test it”_).
2. **Planning Agent** 🧭:
   - Breaks down the query into smaller sub-tasks.
   - Determines which tool to use for each sub-task.
3. **Tool Execution** 🔧:
   - Generates Python code using prompt templates.
   - Runs the code in a temporary Jupyter kernel.
4. **Outputs** 📤:
   - Shows code + results for every sub-task.
   - Creates a final structured output.

---

## 🛠️ Tech Stack

- 🐍 **Python 3.10+**
- 🧱 **LangGraph**
- 🤖 **OpenAI / LLM of your choice**
- 📦 **Jupyter Kernel via `jupyter_client`**
- 🛜 **Tavily Search / Custom Tooling (Optional)**

---

## ✨ Example

```python
User Query:
"Write and test code for generating the Fibonacci sequence."

➤ Task 1: Generate code to compute the Fibonacci sequence ✅
➤ Task 2: Test the code with 10 terms ✅
➤ Task 3: Improve efficiency & readability ✅
➤ Task 4: Add comments ✅
➤ Task 5: Test on 100 terms ✅
➤ Task 6: Generate documentation ✅

🧪 Try It Yourself
Coming soon: CLI + Web UI version 🔜
Wanna test it locally? Just clone the repo and run:

bash
Copy
Edit
git clone https://github.com/your-username/planning-agent.git
cd src
python agent.py

📬 Feedback & Contributions
Have ideas or want to extend this agent? Feel free to:

🤝 Open a PR

🐛 Submit issues

⭐ Star the repo if you like it!

📄 License
MIT License — Feel free to use, modify, and build upon it!

