# **Parrot: Talk to Your Data** 🦜  

Parrot is a **terminal-based RAG + Agentic AI** tool that lets you interact with your data sources using natural language. Query CSV files, PostgreSQL databases, and more—right from your terminal.  


## Screenshots
![Screen 1](https://i.ibb.co/bM8rsF2j/Capture.png)
![Screen 2](https://i.ibb.co/Nd82mY2Z/Capture3.png)

## 🚀 **Features**  

✅ **Ask questions in natural language** – No SQL or scripting required  
✅ **Interactive CLI experience** – Simple and intuitive  
✅ **Rich output formatting** – Get well-structured responses  
✅ **Export Chat** – Export your chats to different formats like csv, JSON or text. 



## 🔧 **Installation**  

### **Requirements**  
- Python **3.8+**  
- [`uv`](https://github.com/astral-sh/uv) (Recommended for dependency management)
- LLM API Key (OpenAI, Claude, Groq)

### **Steps**  

1. Clone the repository:  
   ```bash
   git clone https://github.com/your-repo/parrot.git
   cd parrot
   ```
2. Create a virtual environment using `uv`:  
   ```bash
   uv venv
   ```
3. Install dependencies:  
   ```bash
   uv sync 
   ```


## 🛠 **Usage**  

### **Run in Interactive Mode**  
Start a session to chat with your data:  
```bash
uv run main.py
```  
or  
```bash
python main.py
```  

---

## 📂 **Supported Data Sources**  

✅ PostgreSQL  
✅ CSV Files  
🚧 Coming Soon: MySQL, Parquet, Avro, DOCX, XLSX, PDF, TXT, JSON  

