import json
import os
from typing import TypedDict, Annotated, List
from langchain_core.messages import HumanMessage, AIMessage
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, add_messages
from deepgram import DeepgramClient, PrerecordedOptions, FileSource
from dotenv import load_dotenv
from pydantic import BaseModel, Field
from openai import OpenAI
import numpy as np
from moviepy.editor import *
import traceback
import httpx
from rich.console import Console
from rich.panel import Panel
from rich import print as rprint

load_dotenv()

console = Console()

DEEPGRAM_API_KEY = os.getenv("DEEPGRAM_API")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Initialize clients
deepgram = DeepgramClient(DEEPGRAM_API_KEY)
client = OpenAI(api_key=OPENAI_API_KEY)


# Define our state
class AgentState(TypedDict):
    messages: Annotated[list[HumanMessage | AIMessage], add_messages]
    title: str
    script: str
    category: str
    sigma_topic: str
    audio_filename: str
    inspiration_source: str
    video_filename: str


# Initialize our graph and model
graph = StateGraph(AgentState)
model = ChatOpenAI(model="gpt-4o-mini")


# Define structured output schemas
class PlanSchema(BaseModel):
    title: str = Field(...,
                       description="Catchy title for a 10-second sigma lifestyle motivation YouTube short, should be in 4-5 words not more than that")
    sigma_theme: str = Field(...,
                             description="Core sigma lifestyle theme (e.g., Self-reliance, Personal growth, Unconventional success)")
    inspiration_source: str = Field(...,
                                    description="Source of inspiration (e.g., Historical figure, Movie character, Living legend)")
    key_point: str = Field(..., description="Single key motivational point for the script")


class ScriptSchema(BaseModel):
    script: str = Field(...,
                        description="Concise, motivational script for a 10-second sigma lifestyle-focused YouTube short")


class ValidationSchema(BaseModel):
    is_suitable: bool = Field(...,
                              description="Whether the script is suitable for a 10-second sigma lifestyle motivation YouTube short")
    improvements: List[str] = Field(..., description="List of specific improvements needed, if any")


class FinalSchema(BaseModel):
    title: str = Field(...,
                       description="Final title for the 10-second sigma lifestyle motivation YouTube short, should be in 4-5 words not more than that")
    script: str = Field(..., description="Final script for the 10-second sigma lifestyle motivation YouTube short")


class ProofreadSchema(BaseModel):
    corrected_script: str = Field(..., description="Proofread and corrected version of the script")
    changes_made: List[str] = Field(..., description="List of changes made to the script")


# Helper functions
def get_schema(schema_class):
    if hasattr(schema_class, 'model_json_schema'):
        schema = schema_class.model_json_schema()
    elif hasattr(schema_class, 'schema'):
        schema = schema_class.schema()
    else:
        raise AttributeError(f"{schema_class.__name__} has neither 'model_json_schema' nor 'schema' method")
    return {
        "name": schema_class.__name__,
        "description": f"Schema for {schema_class.__name__}",
        "parameters": schema
    }


def create_gradient_background(size, duration, start_color, end_color):
    def make_frame(t):
        progress = t / duration
        r = int(start_color[0] + (end_color[0] - start_color[0]) * progress)
        g = int(start_color[1] + (end_color[1] - start_color[1]) * progress)
        b = int(start_color[2] + (end_color[2] - start_color[2]) * progress)
        return np.tile(np.array([r, g, b]), (size[1], size[0], 1))

    return VideoClip(make_frame, duration=duration)


def animate_word(word, font_size=120, color='white', font='Arial-Bold', start_time=0, duration=1):
    clip = TextClip(word, fontsize=font_size, color=color, font=font, method='label')
    return (clip
            .set_start(start_time)
            .set_duration(duration)
            .set_position(('center', 'center'))
            .set_opacity(1)
            .resize(lambda t: max(0.1, min(1, 2 * t)))
            .crossfadein(duration / 2))


def transcribe_audio_file(audio_path):
    console.print(Panel(f"Transcribing audio: {audio_path}", border_style="cyan"))
    try:
        with open(audio_path, "rb") as file:
            buffer_data = file.read()
        payload: FileSource = {
            "buffer": buffer_data,
        }

        options = PrerecordedOptions(
            model="nova-2",
            language="en",
            summarize="v2",
            topics=True,
            smart_format=True,
            punctuate=True,
            diarize=True,
        )

        response = (deepgram.listen
                    .prerecorded.v("1")
                    .transcribe_file(payload, options, timeout=httpx.Timeout(300.0, connect=10.0)))
        return json.loads(response.to_json())
    except Exception as e:
        console.print(Panel(f"Exception during transcription: {e}", style="bold red"))
        return None


def get_word_timings(audio_file):
    deepgram_response = transcribe_audio_file(audio_file)
    if deepgram_response and 'results' in deepgram_response:
        words = deepgram_response['results']['channels'][0]['alternatives'][0]['words']
        return [(word['word'], word['start'], word['end']) for word in words]
    return []


def planner(state):
    messages = state["messages"]
    response = model.invoke(
        messages + [HumanMessage(
            content="You are a planner for 10-second sigma lifestyle motivation YouTube shorts. Create a brief plan for a short, inspiring video about sigma lifestyle. Choose a core theme relevant to sigma mentality such as self-reliance, personal growth, or unconventional success. Select an inspiration source from history, movies, living legends, or other notable figures/characters that hasn't been used before. The content should be simple, direct, and impactful.")],
        functions=[get_schema(PlanSchema)],
        function_call={"name": PlanSchema.__name__}
    )
    result = PlanSchema.parse_raw(response.additional_kwargs["function_call"]["arguments"])
    console.print(Panel(f"Planner output:\n{result.json()}", border_style="cyan"))
    return {
        "messages": [response],
        "title": result.title,
        "category": "Sigma Lifestyle Motivation",
        "sigma_topic": result.sigma_theme,
        "inspiration_source": result.inspiration_source,
    }


def is_video_generated(state):
    inspiration_source = state["inspiration_source"]
    data_file = "../generated_videos.json"
    if os.path.exists(data_file):
        with open(data_file, "r") as f:
            generated_videos = json.load(f)
    else:
        generated_videos = []
    if inspiration_source in generated_videos:
        console.print(
            Panel(f"Video for {inspiration_source} already exists. Generating a new plan.", border_style="yellow"))
        return {"messages": [HumanMessage(content="Please generate a new plan with a different inspiration source.")]}
    else:
        generated_videos.append(inspiration_source)
        with open(data_file, "w") as f:
            json.dump(generated_videos, f)
        console.print(Panel(f"New video for {inspiration_source} will be generated.", border_style="green"))
        return {"messages": [HumanMessage(content="Proceed with the current plan.")]}


def script_generator(state):
    messages = state["messages"]
    response = model.invoke(
        messages + [HumanMessage(
            content="Write a concise, motivational script for a 10-second sigma lifestyle-focused YouTube short. The script should be simple, direct, and inspiring, focusing on a single key point related to sigma mentality. Use the chosen inspiration source to illustrate the point. Use short, impactful sentences.")],
        functions=[get_schema(ScriptSchema)],
        function_call={"name": ScriptSchema.__name__}
    )
    result = ScriptSchema.parse_raw(response.additional_kwargs["function_call"]["arguments"])
    console.print(Panel(f"Script generator output:\n{result.json()}", border_style="magenta"))
    return {"messages": [response], "script": result.script}


def validator(state):
    messages = state["messages"]
    response = model.invoke(
        messages + [HumanMessage(
            content="Review the generated script. Is it concise, motivational, and suitable for a 10-second sigma lifestyle-focused YouTube short? Does it effectively use the inspiration source to deliver a clear, inspiring message aligned with sigma mentality? If not, what specific improvements are needed to make it more impactful and concise?")],
        functions=[get_schema(ValidationSchema)],
        function_call={"name": ValidationSchema.__name__}
    )
    result = ValidationSchema.parse_raw(response.additional_kwargs["function_call"]["arguments"])
    console.print(Panel(f"Validator output:\n{result.json()}", border_style="blue"))
    return {"messages": [response]}


def finalizer(state):
    messages = state["messages"]
    response = model.invoke(
        messages + [HumanMessage(
            content="Provide the final version of the title and script for the 10-second sigma lifestyle motivation YouTube short. Ensure the script is simple, direct, and inspiring, focusing on a single key point related to sigma mentality and effectively using the chosen inspiration source. The script must be suitable for a 10-second video. The title should be in 4-5 words not more than that.")],
        functions=[get_schema(FinalSchema)],
        function_call={"name": FinalSchema.__name__}
    )
    result = FinalSchema.parse_raw(response.additional_kwargs["function_call"]["arguments"])
    console.print(Panel(f"Finalizer output:\n{result.json()}", border_style="green"))
    return {
        "messages": [response],
        "title": result.title,
        "script": result.script,
        "category": "Sigma Lifestyle Motivation",
    }


def generate_audio(state):
    script = state['script']
    audio_filename = f"output_audio_{state['inspiration_source'].replace(' ', '_')}.mp3"
    response = client.audio.speech.create(model="tts-1", voice="alloy", input=script)
    if response.content:
        with open(audio_filename, "wb") as audio_file:
            audio_file.write(response.content)
        console.print(Panel(f"Audio saved as: {audio_filename}", border_style="cyan"))
        return {"audio_filename": audio_filename}
    else:
        console.print(Panel("Failed to generate audio.", style="bold red"))
        raise ValueError("Failed to generate audio.")


def proofreader(state):
    messages = state["messages"]
    script = state["script"]
    response = model.invoke(
        messages + [HumanMessage(
            content=f"Proofread and correct the following script, fixing any spelling or grammar issues. Make sure it remains concise and impactful for a 10-second video. Here's the script:\n\n{script}")],
        functions=[get_schema(ProofreadSchema)],
        function_call={"name": ProofreadSchema.__name__}
    )
    result = ProofreadSchema.parse_raw(response.additional_kwargs["function_call"]["arguments"])
    console.print(Panel(f"Proofreader output:\n{result.json()}", border_style="yellow"))
    return {"messages": [response], "script": result.corrected_script}


def generate_video(state):
    audio_file = state['audio_filename']
    title = state['title']
    script = state['script']
    duration = AudioFileClip(audio_file).duration

    # Create background
    background = ColorClip(size=(1080, 1920), color=(0, 0, 0), duration=duration)

    # Add title
    title_clip = TextClip(title, fontsize=70, color='white', font='Arial', size=(1080, 100))
    title_clip = title_clip.set_position(('center', 100)).set_duration(duration)

    # Get word timings
    word_timings = get_word_timings(audio_file)

    # Create clips for each word
    word_clips = []
    lines = []
    current_line = []
    line_width = 0
    max_width = 900  # Maximum width for text before wrapping

    for word, start, end in word_timings:
        word_clip = TextClip(word, fontsize=50, color='white', font='Arial')
        if line_width + word_clip.w > max_width:
            lines.append(current_line)
            current_line = []
            line_width = 0
        current_line.append((word, word_clip, start, end))
        line_width += word_clip.w + 10  # Add small gap between words

    if current_line:
        lines.append(current_line)

    # Calculate total height of all lines
    total_height = sum(max(clip.h for _, clip, _, _ in line) + 10 for line in lines)

    # Start y position to center all lines vertically
    y_position = (1920 - total_height) // 2

    for line in lines:
        line_width = sum(clip.w + 10 for _, clip, _, _ in line) - 10
        x_position = (1080 - line_width) // 2

        for word, clip, start, end in line:
            # Normal word
            normal_clip = clip.set_position((x_position, y_position))
            normal_clip = normal_clip.set_start(0).set_end(duration)
            word_clips.append(normal_clip)

            # Highlighted word
            highlight_clip = TextClip(word, fontsize=50, color='yellow', font='Arial')
            highlight_clip = highlight_clip.set_position((x_position, y_position))
            highlight_clip = highlight_clip.set_start(start).set_end(end)
            word_clips.append(highlight_clip)

            x_position += clip.w + 10

        y_position += max(clip.h for _, clip, _, _ in line) + 10

    # Compose video
    video = CompositeVideoClip([background, title_clip] + word_clips)

    # Add audio
    final_video = video.set_audio(AudioFileClip(audio_file))

    # Write video file
    output_filename = f"output_video_{state['inspiration_source'].replace(' ', '_')}.mp4"
    final_video.write_videofile(output_filename, fps=24)

    console.print(Panel(f"Video generated: {output_filename}", border_style="green"))
    return {"video_filename": output_filename}


# Set up the graph
graph.add_node("planner", planner)
graph.add_node("is_video_generated", is_video_generated)
graph.add_node("script_generator", script_generator)
graph.add_node("validator", validator)
graph.add_node("proofreader", proofreader)
graph.add_node("finalizer", finalizer)
graph.add_node("audio_generator", generate_audio)
graph.add_node("video_generator", generate_video)

graph.add_edge("planner", "is_video_generated")
graph.add_conditional_edges(
    "is_video_generated",
    lambda x: "planner" if "Please generate a new plan" in x["messages"][-1].content else "script_generator"
)
graph.add_edge("script_generator", "validator")
graph.add_edge("validator", "proofreader")
graph.add_edge("proofreader", "finalizer")
graph.add_edge("finalizer", "audio_generator")
graph.add_edge("audio_generator", "video_generator")

graph.set_entry_point("planner")
workflow = graph.compile()
input_state = {
    "messages": [HumanMessage(
        content="Create a 10-second YouTube short with a simple, motivational message about sigma lifestyle, using a historical figure, movie character, or living legend as inspiration.")],
    "title": "",
    "script": "",
    "category": "",
    "sigma_topic": "",
    "audio_filename": "",
    "inspiration_source": "",
    "video_filename": "",
}


def run_workflow():
    try:
        result = workflow.invoke(input_state)
        console.print(Panel("Final Result", style="bold green"))
        rprint(f"[bold]Title:[/bold] {result['title']}")
        rprint(f"[bold]Category:[/bold] {result['category']}")
        rprint(f"[bold]Sigma Topic:[/bold] {result['sigma_topic']}")
        rprint(f"[bold]Inspiration Source:[/bold] {result['inspiration_source']}")
        rprint(f"[bold]Script:[/bold] {result['script']}")
        rprint(f"[bold]Audio Filename:[/bold] {result['audio_filename']}")
        rprint(f"[bold]Video Filename:[/bold] {result['video_filename']}")
    except Exception as e:
        console.print(Panel(f"An error occurred: {str(e)}", style="bold red"))
        console.print("Full traceback:")
        console.print(traceback.format_exc())
        console.print(Panel("Last state of the workflow:", style="bold yellow"))
        if 'result' in locals():
            rprint(result)
        else:
            console.print("Result not available")


if __name__ == "__main__":
    console.print(Panel("🎬 Sigma Lifestyle Video Generator", style="bold cyan"))
    run_workflow()
    console.print(Panel("🎉 Workflow Completed!", style="bold green"))
