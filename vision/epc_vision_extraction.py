import os
import base64
import instructor
from openai import OpenAI
from pypdf import PdfReader
from pdf2image import convert_from_path
from dotenv import load_dotenv
from datetime import date
from enum import Enum
from pydantic import BaseModel, Field, field_validator, model_validator
from typing import List, Literal, Any, Optional
import re
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


class EnergyUnit(str, Enum):
    KWH_PER_SQ_METER_YEAR = "kWh/(m²a)"

    @staticmethod
    def normalize_unit(value: str) -> str:
        default_value = EnergyUnit.KWH_PER_SQ_METER_YEAR
        if not isinstance(value, str):
            console.print(f"[yellow]Energy unit has wrong type, defaulting to {default_value}[/yellow]")
            return default_value.value

        pattern = r"kWh\s{0,2}/\s{0,2}\(m[2²]?\s{0,2}[-\*•·]?\s{0,2}a\)"
        if re.match(pattern, value):
            return EnergyUnit.KWH_PER_SQ_METER_YEAR.value
        else:
            console.print(f"[yellow]Invalid energy unit: {value}, defaulting to {default_value}[/yellow]")
            return default_value.value

    def __str__(self):
        return self.value


class EpcType(str, Enum):
    CONSUMPTION_CERTIFICATE = "CONSUMPTION_CERTIFICATE"
    DEMAND_CERTIFICATE = "DEMAND_CERTIFICATE"
    UNKNOWN_EPC_TYPE = "UNKNOWN_EPC_TYPE"

    def __str__(self):
        return self.value


HeatingSystem = Literal[
    "boiler",
    "block_heating_station",
    "fuel_cell",
    "heat_pump",
    "hybrid",
    "storage_heater",
    "stove",
]
EnergySource = Literal[
    "gas",
    "oil",
    "alternative",
    "electric",
    "coal",
]
HeatingConfiguration = Literal["central", "per_floor", "per_room"]


# Keeping EnergyPerformanceCertificate unchanged
class EnergyPerformanceCertificate(BaseModel):
    is_building_residential: bool = Field(
        default=False,
        description="This field is set to true if the building is residential",
    )
    building_type_translated_to_english: Optional[str] = Field(default=None)
    building_part_translated_to_english: Optional[str] = Field(default=None)
    building_address: str
    certificate_valid_until_date: Optional[date] = Field(default=None)
    certificate_date_of_issue: Optional[date] = Field(default=None)
    final_energy_consumption_of_building: Optional[float] = Field(
        description="Endenergieverbrauch"
    )
    final_energy_demand_of_building: Optional[float] = Field(
        description="Endenergiebedarf"
    )
    unit_of_final_energy_consumption_of_building: EnergyUnit = Field(
        default="kwh/(m²a)"
    )
    primary_energy_consumption_building: Optional[float] = Field(
        default=None, description="primarenergiebedarf"
    )
    unit_of_primary_energy_consumption_building: EnergyUnit = Field(default="kwh/(m²a)")
    recommended_improvement_measures: List[str] = Field(default_factory=list)
    year_of_building_construction: Optional[int]
    year_of_heat_generator_construction: Optional[int]
    space_heating_system: Optional[HeatingSystem] = Field(
        default=None,
        description=(
            "Indicates the system used for space heating. Select an appropriate value from the {HeatingSystem} enum."
            " Leave this field empty if the heating system is not specified in the document."
            " Available options include:"
            " - Boiler: A closed vessel where fluid (typically water) is heated."
            " - Block heating station: A central system providing heat to multiple buildings."
            " - Fuel cell: Converts chemical energy of fuel into electricity via a chemical reaction."
            " - Heat pump: Transfers heat from a cooler to a warmer area using mechanical energy."
            " - Hybrid: Combines two or more heating technologies."
            " - Storage heater: Stores thermal energy during the night and releases it during the day."
            " - Stove: Burns fuel to provide heat to a space or the stove itself."
        ),
    )
    space_heating_energy_source: Optional[EnergySource] = Field(
        default=None,
        description=(
            "Indicates the energy source used for space heating. Select an appropriate value from the {EnergySource} enum."
            " Leave this field empty if the energy source is not specified in the document."
            " Available options include:"
            " - Gas: A fossil fuel used for heating."
            " - Oil: A fossil fuel used for heating."
            " - Alternative: Includes renewable sources such as solar, wind, and geothermal energy."
            " - Electric: Uses electricity to generate heat."
            " - Coal: A fossil fuel used for heating."
        ),
    )
    space_heating_configuration: Optional[HeatingConfiguration] = Field(
        default=None,
        description=(
            "Indicates the configuration of the space heating system. Select an appropriate value from the {HeatingConfiguration} enum."
            " Leave this field empty if the heating configuration is not specified in the document."
            " Available options include:"
            " - Central: Provides heat to multiple rooms or buildings from one central location."
            " - Per floor: Heating systems are installed on each floor of the building."
            " - Per room: Heating systems are installed in each room of the building."
        ),
    )
    water_heating_system: Optional[HeatingSystem] = Field(
        default=None,
        description=(
            "Indicates the system used for Water heating. Select an appropriate value from the {HeatingSystem} enum."
            " Leave this field empty if the heating system is not specified in the document."
            " Available options include:"
            " - Boiler: A closed vessel where fluid (typically water) is heated."
            " - Block heating station: A central system providing heat to multiple buildings."
            " - Fuel cell: Converts chemical energy of fuel into electricity via a chemical reaction."
            " - Heat pump: Transfers heat from a cooler to a warmer area using mechanical energy."
            " - Hybrid: Combines two or more heating technologies."
            " - Storage heater: Stores thermal energy during the night and releases it during the day."
            " - Stove: Burns fuel to provide heat to a space or the stove itself."
        ),
    )
    water_heating_energy_source: Optional[EnergySource] = Field(
        default=None,
        description=(
            "Indicates the energy source used for Water heating. Select an appropriate value from the {EnergySource} enum."
            " Leave this field empty if the energy source is not specified in the document."
            " Available options include:"
            " - Gas: A fossil fuel used for heating."
            " - Oil: A fossil fuel used for heating."
            " - Alternative: Includes renewable sources such as solar, wind, and geothermal energy."
            " - Electric: Uses electricity to generate heat."
            " - Coal: A fossil fuel used for heating."
        ),
    )
    water_heating_configuration: Optional[HeatingConfiguration] = Field(
        default=None,
        description=(
            "Indicates the configuration of the Water heating system. Select an appropriate value from the {HeatingConfiguration} enum."
            " Leave this field empty if the heating configuration is not specified in the document."
            " Available options include:"
            " - Central: Provides heat to multiple rooms or buildings from one central location."
            " - Per floor: Heating systems are installed on each floor of the building."
            " - Per room: Heating systems are installed in each room of the building."
        ),
    )

    @field_validator(
        "unit_of_final_energy_consumption_of_building",
        "unit_of_primary_energy_consumption_building",
        mode="before",
    )
    def validate_energy_unit(cls, value):
        normalized_unit = EnergyUnit.normalize_unit(value)
        return EnergyUnit(normalized_unit)

    @model_validator(mode="after")
    def validate_epc_fields(cls, values):
        valid_until = values.certificate_valid_until_date
        date_of_issue = values.certificate_date_of_issue
        if valid_until and date_of_issue and valid_until < date_of_issue:
            raise ValueError(
                "certificate_valid_until_date must be greater than or equal to certificate_date_of_issue"
            )
        primary_energy_demand = values.primary_energy_consumption_building
        if primary_energy_demand is None:
            raise ValueError(
                "primary_energy_consumption_building cannot be null. Please recheck the document."
            )
        if values.building_address is None:
            raise ValueError(
                "building_address cannot be null. Please recheck the document."
            )
        return values

    @property
    def certificate_type(self):
        if (
                self.final_energy_consumption_of_building is None
                and self.final_energy_demand_of_building is not None
        ):
            return EpcType.DEMAND_CERTIFICATE
        if (
                self.final_energy_consumption_of_building is not None
                and self.final_energy_demand_of_building is None
        ):
            return EpcType.CONSUMPTION_CERTIFICATE
        return EpcType.UNKNOWN_EPC_TYPE

    def to_dict(self):
        def format_date(date):
            return date.isoformat() if date else None

        output_dict = self.model_dump()

        output_dict["certificate_valid_until_date"] = format_date(
            self.certificate_valid_until_date
        )
        output_dict["certificate_date_of_issue"] = format_date(
            self.certificate_date_of_issue
        )
        output_dict["certificate_type"] = self.certificate_type
        return output_dict

    @classmethod
    def get_queries(cls):
        return [
            "Final energy consumption",
            "Certificate expiry date",
            "Certificate issue date",
        ]


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

        image_dir = f"epc_docs/{pdf_filename}"
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


def extract_epc_document(encoded_images: List[str]) -> EnergyPerformanceCertificate:
    detailed_prompt = """
        Imagine three different experts are answering this question. All experts will write down one step of their thinking, then share it with the group. Then all experts will go on to the next step, etc. If any expert realizes they're wrong at any point, then they leave.

        EPC Document Details: Extract specific details such as EPC rating, unique reference number, date of certificate, valid until date, and inspection date. Make sure to correctly identify these fields as they are crucial for energy performance assessment.

        Property Address: Extract the full address of the property, which may include the street name and number, postal code, city, and subarea. The document may be in German, so refer to the data carefully.

        EPC Rating and Score: Identify and extract the EPC rating and the associated score, ensuring to capture the precise value without any rounding.

        Inspector Details: Extract details related to the inspector, such as inspector name, inspector contact number, inspector email, and inspector organization. Ensure to capture all relevant contact information.

        Date Details: Differentiate between the date of the certificate, the valid until date, and the inspection date. Extract these dates accurately.

        Construction and Refurbishment Details: Identify and extract information about the construction year and any refurbishment details, ensuring these are not confused.

        Document Language Consideration: The document may contain information in German, so ensure careful translation and extraction of data.

        Phone Numbers: While extracting phone numbers, ensure to capture the complete number without any truncation.

        Extraction Accuracy: Ensure that all extracted values match the exact values in the document without rounding up or down. Pay close attention to detail and accuracy in the extraction process.
    """
    messages = [
        {
            "role": "system",
            "content": """
                You are an expert data extraction system focused on analyzing EPC documents with precision.
                Your task is to carefully extract critical details such as EPC rating, unique reference number, property address, and inspector details.
                Pay close attention to differentiate between dates like the date of the certificate, valid until date, and inspection date.
                The document may be in German, so ensure accurate translation and extraction.
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
            Panel("[bold blue]Sending request to OpenAI API for document extraction.[/bold blue]", title="API Request"))
        with console.status("[bold yellow]Extracting document details...") as status:
            response = client.chat.completions.create(
                model="gpt-4o-2024-08-06",
                seed=946,
                tool_choice="auto",
                response_model=EnergyPerformanceCertificate,
                messages=messages,
                temperature=0.0,
            )
        console.print(
            Panel("[bold green]Successfully extracted document details.[/bold green]", title="Extraction Complete"))

        return response
    except Exception as e:
        console.print(
            Panel(f"[bold red]Error extracting document details:[/bold red] {str(e)}", title="Extraction Error"))
        raise


def display_result(file: str, result: EnergyPerformanceCertificate):
    table = Table(title=f"EPC Details for {file}", show_header=True, header_style="bold magenta")
    table.add_column("Field", style="cyan", no_wrap=True)
    table.add_column("Value", style="green")

    for field, value in result.model_dump().items():
        if isinstance(value, (list, dict)):
            value = str(value)
        table.add_row(field.replace('_', ' ').title(), str(value))

    console.print(Panel(table, expand=False, border_style="bold", title="Extraction Result",
                        subtitle="Energy Performance Certificate"))


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
                result = extract_epc_document(encoded_images)
                display_result(file, result)
                results.append({"file": file, "result": result})
            except Exception as e:
                console.print(
                    Panel(f"[bold red]Failed to process file[/bold red] '{file}': {str(e)}", title="Processing Error"))
                continue
    return results


def main():
    pdf_directory = "./epc_docs"
    try:
        results = process_files(pdf_directory)
        console.print(Panel("[bold green]Processing completed successfully.[/bold green]", title="Process Complete"))

    except Exception as e:
        console.print(
            Panel(f"[bold red]An error occurred during processing:[/bold red] {str(e)}", title="Processing Error"))


if __name__ == "__main__":
    console.print(
        Panel("[bold green]EPC Vision Extraction[/bold green]", title="Program Start", style="bold green on black"))
    main()
