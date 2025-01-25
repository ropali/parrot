# Parrot: SQL Query Agent

## Installation

```bash
pip install parrot-query
```

## Usage

### With Arguments
```bash
parrot --host localhost --database mydb --user myuser --password mypass --groq-key your_groq_key
```

### Interactive Mode
```bash
parrot  # Will prompt for connection details
```

## Features

- 🦜 Natural language to SQL
- 💻 Interactive CLI
- 🔍 Database schema introspection
- 🎨 Rich output

## Requirements

- Python 3.8+
- Groq API Key
- PostgreSQL database