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

1. **Joke Generator Agent**: Creates and refines jokes using AI models, targeting engineering students with tech-related humor.
   - File: `agents/joke_agent.py`

2. **Marksheet Extraction**: Extracts information from 12th-grade marksheet PDFs using OCR and AI.
   - File: `vision/12_marksheet_extraction.py`

3. **Vision Chat Assistant**: Processes and analyzes images to generate chat responses.
   - File: `vision/vision_chat_assistant.py`

4. **Video Generator Agent**: Creates short sigma lifestyle motivation videos for YouTube, including planning, script generation, audio creation, and video compilation.
   - File: `agents/video_generator/video_generator_agent.py`

5. **Tamil Movie Plot Generator**: Generates detailed Tamil movie plots and scripts, including characters, settings, and a scene-by-scene breakdown.
   - File: `generation/text_movie_plot_generator.py`

6. **VAPI Basic Example**: Demonstrates basic usage of the Voice API for interactive voice assistants, with customizable context and voice settings.
   - File: `agents/sts/vapi_basic.py`

7. **Ollama Local LLM Extraction**: (Mentioned in the conversation history, but code not provided in the snippets)

Each project utilizes various AI and multimedia processing libraries to handle tasks such as natural language processing, speech recognition, image analysis, and video creation.

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
   git clone https://github.com/rajkumaranbalagan07/llm-tutorials
   cd llm-tutorials
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


