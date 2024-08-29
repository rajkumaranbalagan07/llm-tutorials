from langgraph.graph import StateGraph, MessagesState
from langchain_core.messages import HumanMessage
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
from rich.console import Console
from rich.panel import Panel
from rich import print as rprint

load_dotenv()
console = Console()


def joke_writer(state: MessagesState):
    messages = state["messages"]
    response = model.invoke(messages + [HumanMessage(content="""
    Create a short, witty joke about coding or tech that engineering students will love. Use simple English, include an emoji, and keep it relatable for students in computer science or related fields.
    """)])
    console.print(Panel(f"💻 Student Coder's Draft:\n\n{response.content}", border_style="cyan"))
    return {"messages": [response]}


def joke_critic(state: MessagesState):
    messages = state['messages']
    joke = messages[-1].content
    rewritten_joke = model.invoke(f"""
    You're a cool Computer Science professor. Improve the following joke to make it funnier and more relatable for your engineering students:

    <joke>
    {joke}
    </joke>

    Make it snappier and add a tech-savvy twist if possible. Keep it short and sweet!
    """)
    console.print(Panel(f"🧑‍🏫 Prof's Punchline Polish:\n\n{rewritten_joke.content}", border_style="magenta"))
    return {"messages": [rewritten_joke]}


model = ChatOpenAI(model="gpt-4o-mini", temperature=1.0, max_tokens=200)

graph_builder = StateGraph(MessagesState)
graph_builder.add_node("agent", joke_writer)
graph_builder.add_node("joke_critic", joke_critic)
graph_builder.add_edge("agent", "joke_critic")
graph_builder.set_entry_point("agent")
graph_builder.set_finish_point("joke_critic")

graph = graph_builder.compile()

console.print(Panel("🚀 Engineering Humor Hub: Where Bugs Become Features!", style="bold green"))

response = graph.invoke(
    {"messages": [HumanMessage(content="Generate a hilarious coding joke that engineering students will love!")]})

console.print(Panel("🏆 Final Joke - Ready for the Lab", style="bold yellow"))
rprint(response["messages"][-1].content)

console.print(Panel("🎉 Humor Compilation Successful!", style="bold green"))
