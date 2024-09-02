import os
import base64
import instructor
from openai import OpenAI
from pypdf import PdfReader
from pdf2image import convert_from_path
from dotenv import load_dotenv
from pydantic import BaseModel, Field
from typing import List, Optional
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

# Initialize Rich console
console = Console()

# Load environment variables
load_dotenv()
openai_api_key = os.getenv("OPENAI_API_KEY")

openai_client = OpenAI()
client = instructor.from_openai(openai_client)


def convert_pdf_to_images(pdf_path: str) -> List[str]:
    if not os.path.exists(pdf_path):
        console.print(Panel(f"[bold red]PDF file not found:[/bold red] {pdf_path}", title="Error"))
        raise FileNotFoundError(f"PDF file not found: {pdf_path}")
    try:
        pdf_reader = PdfReader(pdf_path)
        base64_images = []
        total_pages = len(pdf_reader.pages)
        pdf_filename = os.path.splitext(os.path.basename(pdf_path))[0]

        console.print(Panel(f"[bold blue]Converting PDF[/bold blue] '{pdf_path}' to images. Total pages: {total_pages}",
                            title="PDF Conversion"))

        image_dir = f"marksheet_docs_image/{pdf_filename}"
        os.makedirs(image_dir, exist_ok=True)

        with console.status("[bold green]Converting PDF pages...") as status:
            for page_number in range(total_pages):
                status.update(f"Processing page {page_number + 1}/{total_pages}")
                page_image = \
                    convert_from_path(pdf_path, dpi=100, first_page=page_number + 1, last_page=page_number + 1)[0]
                image_filename = f"{image_dir}/{pdf_filename}_page_{page_number + 1}.jpg"

                page_image = page_image.convert("RGB")
                page_image.save(image_filename, format="JPEG", quality=85)

                with open(image_filename, "rb") as image_file:
                    image_base64 = base64.b64encode(image_file.read()).decode('utf-8')
                    base64_images.append(f"data:image/jpeg;base64,{image_base64}")

        console.print(Panel(f"[bold green]Successfully converted[/bold green] {total_pages} pages to images",
                            title="Conversion Complete"))
        return base64_images
    except Exception as e:
        console.print(Panel(f"[bold red]Error converting PDF[/bold red] '{pdf_path}' to images: {str(e)}",
                            title="Conversion Error"))
        raise


class Subject(BaseModel):
    name: str
    marks: int


class MarksheetDetails(BaseModel):
    candidate_name: str
    division: str
    subjects: List[Subject]
    result: str
    percentage: float

    @classmethod
    def get_queries(cls):
        return [
            "Candidate name",
            "Division",
            "Subject names and marks",
            "Result",
            "Percentage",
        ]


# ... (keep the convert_pdf_to_images function as is) ...

def extract_marksheet_details(encoded_images: List[str]) -> MarksheetDetails:
    detailed_prompt = """
        Analyze the 12th marksheet_docs PDF and extract the following information:
        1. Candidate's full name
        2. Division achieved (e.g., First Division, Second Division)
        3. List of subjects with their respective marks
        4. Overall result (e.g., Pass, Fail)
        5. Percentage achieved

        Ensure accuracy in extracting numerical values and text. Pay attention to any specific formatting or layout in the marksheet_docs.
    """
    messages = [
        {
            "role": "system",
            "content": """
                You are an expert data extraction system focused on analyzing 12th marksheet_docs documents with precision.
                Your task is to carefully extract critical details such as candidate name, division, subject marks, result, and percentage.
                All extracted data should reflect the exact values without any rounding or truncation.
            """,
        },
        {
            "role": "user",
            "content": detailed_prompt,
        },
        {
            "role": "user",
            "content": [
                {"type": "image_url", "image_url": {"url": encoded_image}}
                for encoded_image in encoded_images
            ],
        },
    ]

    try:
        console.print(
            Panel("[bold blue]Sending request to OpenAI API for marksheet_docs extraction.[/bold blue]",
                  title="API Request"))
        with console.status("[bold yellow]Extracting marksheet_docs details...") as status:
            response = client.chat.completions.create(
                model="gpt-4o",
                seed=946,
                tool_choice="auto",
                response_model=MarksheetDetails,
                messages=messages,
                temperature=0.0,
            )
        console.print(
            Panel("[bold green]Successfully extracted marksheet_docs details.[/bold green]", title="Extraction Complete"))

        return response
    except Exception as e:
        console.print(
            Panel(f"[bold red]Error extracting marksheet_docs details:[/bold red] {str(e)}", title="Extraction Error"))
        raise


def display_result(file: str, result: MarksheetDetails):
    table = Table(title=f"Marksheet Details for {file}", show_header=True, header_style="bold magenta")
    table.add_column("Field", style="cyan", no_wrap=True)
    table.add_column("Value", style="green")

    table.add_row("Candidate Name", result.candidate_name)
    table.add_row("Division", result.division)
    table.add_row("Result", result.result)
    table.add_row("Percentage", f"{result.percentage:.2f}%")

    subjects_table = Table(show_header=True, header_style="bold blue")
    subjects_table.add_column("Subject", style="cyan")
    subjects_table.add_column("Marks", style="green")

    for subject in result.subjects:
        subjects_table.add_row(subject.name, str(subject.marks))

    table.add_row("Subjects", subjects_table)

    console.print(Panel(table, expand=False, border_style="bold", title="Extraction Result",
                        subtitle="12th Marksheet"))


def process_files(directory: str):
    results = []
    try:
        files = os.listdir(directory)
    except Exception as e:
        console.print(
            Panel(f"[bold red]Error reading directory[/bold red] '{directory}': {str(e)}", title="Directory Error"))
        raise

    for file in files:
        file_path = os.path.join(directory, file)
        file_extension = os.path.splitext(file)[1].lower()

        if file_extension == ".pdf":
            try:
                console.print(Panel(f"[bold blue]Processing file:[/bold blue] {file}", title="File Processing"))
                encoded_images = convert_pdf_to_images(file_path)
                result = extract_marksheet_details(encoded_images)
                display_result(file, result)
                results.append({"file": file, "result": result})
            except Exception as e:
                console.print(
                    Panel(f"[bold red]Failed to process file[/bold red] '{file}': {str(e)}", title="Processing Error"))
                continue
    return results


def main():
    pdf_directory = "./marksheet_docs"
    try:
        results = process_files(pdf_directory)
        console.print(Panel("[bold green]Processing completed successfully.[/bold green]", title="Process Complete"))

    except Exception as e:
        console.print(
            Panel(f"[bold red]An error occurred during processing:[/bold red] {str(e)}", title="Processing Error"))


if __name__ == "__main__":
    console.print(
        Panel("[bold green]12th Marksheet Extraction[/bold green]", title="Program Start", style="bold green on black"))
    main()
