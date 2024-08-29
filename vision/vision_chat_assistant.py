import os
import base64
import io
from typing import List
import instructor
from openai import OpenAI
from pydantic import BaseModel, Field
from PIL import Image, UnidentifiedImageError
from dotenv import load_dotenv
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

load_dotenv()

console = Console()


class Reply(BaseModel):
    reply: str


class GeneratedReplies(BaseModel):
    replies: List[Reply]


def resize_image(image_path: str, max_size: tuple[int, int]) -> Image:
    """Resize the image to the given maximum size while maintaining aspect ratio."""
    try:
        with Image.open(image_path) as img:
            if img.mode == 'RGBA':
                img = img.convert('RGB')
            img.thumbnail(max_size, Image.LANCZOS)
            return img.copy()
    except UnidentifiedImageError:
        raise ValueError(f"Unrecognized image format or corrupted image file: {image_path}")
    except FileNotFoundError:
        raise ValueError(f"Image file not found: {image_path}")
    except Exception as e:
        raise ValueError(f"An unexpected error occurred while processing the image: {e}")


def generate_reply(image_path: str, max_size: tuple[int, int] = (800, 800)) -> GeneratedReplies:
    """Generate replies from the provided image after resizing it to the specified size."""
    resized_img = resize_image(image_path, max_size)
    with io.BytesIO() as img_buffer:
        resized_img.save(img_buffer, format='JPEG')
        img_buffer.seek(0)
        base64_img = base64.b64encode(img_buffer.read()).decode('utf-8')

    content = [
        {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_img}"}}
    ]

    response = instructor.from_openai(OpenAI()).chat.completions.create(
        model="gpt-4o-mini",
        response_model=GeneratedReplies,
        messages=[
            {"role": "user",
             "content": "Analyze the given document images and generate only 3 better replies for the image"},
            {"role": "user", "content": content},
        ],
    )
    return response


def process_screenshots(directory: str, max_size: tuple[int, int] = (800, 800)) -> None:
    supported_image_formats = {".jpg", ".jpeg", ".png", ".bmp", ".gif", ".tiff", ".webp"}
    files = os.listdir(directory)

    for file in files:
        file_path = os.path.join(directory, file)
        file_extension = os.path.splitext(file)[1].lower()
        if file_extension in supported_image_formats:
            console.print(Panel(f"📸 Processing Image: {file}", style="bold magenta"))
            try:
                result = generate_reply(file_path, max_size)
                if result and result.replies:
                    table = Table(title=f"💬 Generated Replies for {file}", show_header=False, border_style="cyan")
                    for i, reply in enumerate(result.replies, 1):
                        table.add_row(f"[green]Reply {i}:[/green] {reply.reply}")
                    console.print(table)
                else:
                    console.print(f"[yellow]⚠️ No replies generated for {file}.[/yellow]")
            except Exception as e:
                console.print(f"[red]❌ Failed to process {file}: {e}[/red]")
            console.print("---")
        else:
            continue


if __name__ == "__main__":
    screenshots_directory = "./screenshots"
    console.print(Panel("🤖 Chat Assistant Demo", style="bold blue"))
    process_screenshots(screenshots_directory)
    console.print(Panel("✅ Demo Completed", style="bold green"))
