# AI-Powered Multimedia Processing Project

This project leverages various AI and multimedia processing libraries to handle natural language processing, speech recognition, and multimedia manipulation.

## Table of Contents

- [Dependencies](#dependencies)
- [Installation](#installation)
- [Environment Setup](#environment-setup)
- [Usage](#usage)
- [API Keys](#api-keys)
- [Contributing](#contributing)
- [License](#license)

## Dependencies

This project relies on the following main libraries:

- **LangChain Ecosystem**: For building language model applications
  - `langchain`, `langchain-core`, `langchain-text-splitters`, `langchain-experimental`, `langchain-openai`, `langchain-community`
- **Instructor library**: Interface with OpenAI's language models https://python.useinstructor.com/ 
- **OpenAI**: Interface with OpenAI's language models
- **Anthropic**: Use Anthropic's AI models
- **Deepgram**: Speech recognition SDK
- **MoviePy**: Video editing with Python
- **PDF Processing**: `pypdf` for PDF manipulation, `pdf2image` for PDF to image conversion

Utility libraries include:
- `tiktoken`: OpenAI's tokenizer
- `langgraph`: Building language model workflows
- `python-dotenv`: Environment variable management
- `pydantic`: Data validation and settings management
- `numpy`: Numerical computing
- `httpx`: HTTP client
- `rich`: Rich text and formatting in the terminal
- `vapi-python`: Custom or specific API client

For a full list of dependencies, see the `requirements.txt` file.

## Installation

To set up the project, follow these steps:

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/your-repo-name.git
   cd your-repo-name
   ```

2. Create a virtual environment (optional but recommended):
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
   ```

3. Install the dependencies:
   ```
   pip install -r requirements.txt
   ```

## Environment Setup

1. Create a `.env` file in the root directory of the project.
2. Add the following environment variables to the `.env` file:

   ```
   OPENAI_API_KEY=your_openai_api_key_here
   ANTHROPIC_API_KEY=your_anthropic_api_key_here
   DEEPGRAM_API_KEY=your_deepgram_api_key_here
   # Add any other API keys or configuration variables here
   ```


4. Make sure to add `.env` to your `.gitignore` file to prevent committing sensitive information.

## Usage

[Provide instructions on how to use your project, including any command-line interfaces, main functions, or scripts to run.]

## API Keys

To use this project, you'll need to obtain the following API keys:

1. **OpenAI API Key**: Required for OpenAI's language models and services.
   - Obtain from: [OpenAI Platform](https://platform.openai.com/)

2. **Anthropic API Key**: Needed for Anthropic's AI models.
   - Obtain from: [Anthropic](https://www.anthropic.com/)

3. **Deepgram API Key**: Used for speech recognition services.
   - Obtain from: [Deepgram Console](https://console.deepgram.com/)

Add these keys to your `.env` file as shown in the [Environment Setup](#environment-setup) section.

To use these environment variables in your Python code:

python
from dotenv import load_dotenv
import os
load_dotenv()
openai_api_key = os.getenv('OPENAI_API_KEY')
anthropic_api_key = os.getenv('ANTHROPIC_API_KEY')
deepgram_api_key = os.getenv('DEEPGRAM_API_KEY')

