# AI-Powered Multimedia Processing Project

This project leverages various AI and multimedia processing libraries to handle natural language processing, speech recognition, and multimedia manipulation.

## Table of Contents

- [Projects Overview](#projects-overview)
- [Dependencies](#dependencies)
- [Installation](#installation)
- [Environment Setup](#environment-setup)
- [Usage](#usage)
- [API Keys](#api-keys)
- [Contributing](#contributing)
- [License](#license)

## Projects Overview

This repository contains several AI-powered projects:

1. **Multimedia Processing**: Handles video editing, PDF manipulation, and image conversion.
2. **Natural Language Processing**: Utilizes LangChain and OpenAI for advanced NLP tasks.
3. **Speech Recognition**: Implements Deepgram for audio transcription and analysis.
4. **AI Model Integration**: Incorporates both OpenAI and Anthropic models for various AI tasks.

## Dependencies

Key libraries and frameworks used across our projects:

- **LangChain Ecosystem**: `langchain`, `langchain-core`, `langchain-text-splitters`, `langchain-experimental`, `langchain-openai`, `langchain-community`
- **Instructor**: Enhanced interface for OpenAI's language models ([Documentation](https://python.useinstructor.com/))
- **OpenAI**: Official OpenAI API integration
- **Anthropic**: Access to Anthropic's AI models
- **Deepgram**: Speech recognition SDK
- **MoviePy**: Video editing capabilities
- **PDF Processing**: `pypdf` and `pdf2image` for PDF handling

Utility libraries:
- `tiktoken`, `langgraph`, `python-dotenv`, `pydantic`, `numpy`, `httpx`, `rich`, `vapi-python`

For a complete list, refer to `requirements.txt`.

## Installation

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/your-repo-name.git
   cd your-repo-name
   ```

2. Create and activate a virtual environment:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
   ```

3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

## Environment Setup

1. Create a `.env` file in the project root:
   ```
   touch .env  # On Unix-based systems
   # Or manually create .env file in the root directory
   ```

2. Add the following to `.env`:
   ```
   OPENAI_API_KEY=your_openai_api_key_here
   ANTHROPIC_API_KEY=your_anthropic_api_key_here
   DEEPGRAM_API_KEY=your_deepgram_api_key_here
   # Add other API keys or config variables as needed
   ```

3. Ensure `.env` is in your `.gitignore`:
   ```
   echo ".env" >> .gitignore
   ```

## Usage

Each project in this repository has its own usage instructions. Please refer to the individual project directories for specific guidance on running and utilizing each component.

## API Keys

Obtain the following API keys and add them to your `.env` file:

1. **OpenAI API Key**: [OpenAI Platform](https://platform.openai.com/)
2. **Anthropic API Key**: [Anthropic](https://www.anthropic.com/)
3. **Deepgram API Key**: [Deepgram Console](https://console.deepgram.com/)

Load environment variables in Python:

python
from dotenv import load_dotenv
import os
load_dotenv()
openai_api_key = os.getenv('OPENAI_API_KEY')
anthropic_api_key = os.getenv('ANTHROPIC_API_KEY')
deepgram_api_key = os.getenv('DEEPGRAM_API_KEY')
