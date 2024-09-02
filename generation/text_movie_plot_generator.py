import instructor
from pydantic import BaseModel
from openai import OpenAI
from dotenv import load_dotenv
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

load_dotenv()


class Character(BaseModel):
    name: str
    role: str
    description: str
    emoji: str


class TamilMoviePlot(BaseModel):
    title: str
    tagline: str
    hero: Character
    heroine: Character
    comedian: Character
    villain: Character
    setting: str
    time_period: str
    universe: str
    main_theme: str
    conflict: str
    twist: str
    climax: str
    plot_summary: str
    genre_emojis: str


client = instructor.from_openai(OpenAI())


def generate_tamil_movie_plot(prompt):
    detailed_prompt = """
        Create a detailed Tamil movie script that includes the following elements, written in a scene-by-scene format, with vivid descriptions, dialogue, and appropriate emojis:

        1. **Title 🎬**: Provide a captivating title that encapsulates the essence of the movie.
        2. **Tagline ✨**: Craft a short, catchy tagline that complements the title.
        3. **Characters 🎭**: Develop unique, memorable characters with distinct personalities:
           - **Hero**: A charismatic lead with special abilities or qualities.
           - **Heroine**: A strong female lead with her own storyline and agency.
           - **Comedian**: A witty character providing both humor and unexpected wisdom.
           - **Villain**: A compelling antagonist with complex motivations.
           For each character, provide a name, brief description, and a fitting emoji.

        4. **Setting 🌍**: Choose a unique and vividly described location. This could range from a bustling Chennai neighborhood to an alien world, or even multiple realities.

        5. **Time Period ⏳**: Specify when the story takes place. It could be the present, a historical era, the distant future, or span multiple time periods.

        6. **Universe 🌌**: Describe the universe or multiverse of the story. Is it our reality, a parallel dimension, or a completely fictional cosmos?

        7. **Main Theme 🎨**: Select a central theme that resonates throughout the story. This could be love, justice, identity, technological progress, cultural preservation, or any compelling concept.

        8. **Conflict 💥**: Develop a gripping conflict that ties into the main theme and setting. Make it personal, societal, or even cosmic in nature.

        9. **Plot Twist 🌪️**: Introduce a shocking or surprising turn of events that dramatically changes the course of the story.

        10. **Climax 🏆**: Describe an exhilarating and satisfying resolution to the conflict that showcases character growth and addresses the main theme.

        11. **Detailed Movie Script 📜**: Write the plot summary as a full-length movie script, broken down into scenes. Include:
            - **Scene Descriptions**: Provide vivid details of the setting, atmosphere, and relevant background elements.
            - **Character Actions**: Describe the movements, expressions, and behaviors of the characters in each scene.
            - **Dialogue**: Write realistic and emotionally engaging dialogue between characters.
            - **Emotional Beats**: Highlight key emotional moments that drive the narrative forward.
            - **Cinematic Elements**: Use emojis to add visual flair and represent key moments or transitions.
            - **Scene-by-Scene Breakdown**: Ensure each scene is richly detailed and follows a logical sequence, capturing the essence of Tamil cinema with all its emotional and dramatic nuances.

        12. **Genre Emojis 🎭🎬**: Provide 2-4 emojis that represent the genres or key elements of the movie.

        For the **plot_summary** field, write a full-length movie script in a detailed scene-by-scene format. Each scene should contain specific descriptions, character interactions, and dialogues that bring the story to life, just like a professional screenplay. Focus on key moments, character development, and emotional beats, while maintaining the flow and dramatic tension of a Tamil cinema experience.
    """

    messages = [
        {
            "role": "system",
            "content": """
                You are a visionary Tamil cinema scriptwriter known for creating groundbreaking, emotionally resonant, and globally appealing movie scripts. Your task is to generate a unique Tamil movie concept that could revolutionize the industry.
                Push the boundaries of storytelling while honoring the rich traditions of Tamil culture and cinema.
                Create a story that's vivid, detailed, and compelling, using emojis to add visual flair to your descriptions.
            """,
        },
        {
            "role": "user",
            "content": detailed_prompt,
        },
        {
            "role": "user",
            "content": prompt,
        },
    ]

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            response_model=TamilMoviePlot,
            messages=messages,
            temperature=0.8,
        )
        return response
    except Exception as e:
        print(f"An error occurred: {e}")
        return None


# Example usage
user_prompt = "Create an innovative and exciting Tamil movie plot. Feel free to incorporate any themes, settings, or concepts you think would make for a thrilling story. Make it colorful, emotional, and unforgettable!"
movie_plot = generate_tamil_movie_plot(user_prompt)

if movie_plot:
    console = Console()

    title = Text(f"🎬 {movie_plot.title}", style="bold magenta")
    tagline = Text(f"✨ {movie_plot.tagline}", style="italic cyan")
    
    console.print(Panel(f"{title}\n{tagline}", expand=False))

    character_table = Table(title="👥 Characters", show_header=True, header_style="bold blue")
    character_table.add_column("Role", style="dim", width=12)
    character_table.add_column("Name", style="cyan")
    character_table.add_column("Description", style="green")
    
    character_table.add_row("Hero", f"{movie_plot.hero.name} {movie_plot.hero.emoji}", movie_plot.hero.description)
    character_table.add_row("Heroine", f"{movie_plot.heroine.name} {movie_plot.heroine.emoji}", movie_plot.heroine.description)
    character_table.add_row("Comedian", f"{movie_plot.comedian.name} {movie_plot.comedian.emoji}", movie_plot.comedian.description)
    character_table.add_row("Villain", f"{movie_plot.villain.name} {movie_plot.villain.emoji}", movie_plot.villain.description)
    
    console.print(character_table)

    details_table = Table(show_header=False, show_edge=False, pad_edge=False)
    details_table.add_column("Attribute", style="bold yellow")
    details_table.add_column("Value")
    
    details_table.add_row("🌍 Setting", movie_plot.setting)
    details_table.add_row("⏳ Time Period", movie_plot.time_period)
    details_table.add_row("🌌 Universe", movie_plot.universe)
    details_table.add_row("🎨 Main Theme", movie_plot.main_theme)
    details_table.add_row("💥 Conflict", movie_plot.conflict)
    details_table.add_row("🌪️ Twist", movie_plot.twist)
    details_table.add_row("🏆 Climax", movie_plot.climax)
    
    console.print(details_table)

    console.print(Panel(movie_plot.plot_summary, title="📜 Plot Summary", expand=False))
    
    console.print(f"\nGenre: {movie_plot.genre_emojis}", style="bold")
else:
    console = Console()
    console.print("Failed to generate a movie plot.", style="bold red")