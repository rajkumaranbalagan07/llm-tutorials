import ollama
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

console = Console()

response = ollama.chat(
    model='llama3.1',
    messages=[{'role': 'user', 'content': '''Ich plane nächste Woche eine Reise nach Toronto für eine Geschäftskonferenz. 
Ich benötige detaillierte Informationen über das Wetter, mögliche Reisehinweise und Empfehlungen für geschäftsangemessene Kleidung 
basierend auf dem Klima. Außerdem interessiere ich mich für kulturelle Veranstaltungen während meines Aufenthalts, 
insbesondere solche, die sich gut zum Netzwerken eignen könnten. Können Sie zudem einige hochbewertete Restaurants 
in der Nähe des Finanzviertels empfehlen, die sich für Kundentreffen eignen würden? Zuletzt habe ich eine leichte Allergie gegen Pollen - 
sollte ich mir darüber während meines Besuchs Sorgen machen?'''}],

    tools=[
        {
            'type': 'function',
            'function': {
                'name': 'get_comprehensive_weather_info',
                'description': 'Get detailed weather information including current conditions, forecast, and climate data',
                'parameters': {
                    'type': 'object',
                    'properties': {
                        'city': {'type': 'string', 'description': 'The name of the city'},
                        'country': {'type': 'string', 'description': 'The country where the city is located'},
                        'start_date': {'type': 'string', 'format': 'date',
                                       'description': 'Start date of the trip (YYYY-MM-DD)'},
                        'end_date': {'type': 'string', 'format': 'date',
                                     'description': 'End date of the trip (YYYY-MM-DD)'},
                        'units': {'type': 'string', 'enum': ['metric', 'imperial'],
                                  'description': 'The unit system for measurements'},
                        'include_hourly': {'type': 'boolean', 'description': 'Include hourly forecast data'},
                        'include_alerts': {'type': 'boolean', 'description': 'Include weather alerts and warnings'},
                    },
                    'required': ['city', 'country', 'start_date', 'end_date'],
                },
            },
        },
        {
            'type': 'function',
            'function': {
                'name': 'get_air_quality_and_pollen_info',
                'description': 'Get current air quality and pollen information for a city',
                'parameters': {
                    'type': 'object',
                    'properties': {
                        'city': {'type': 'string', 'description': 'The name of the city'},
                        'country': {'type': 'string', 'description': 'The country where the city is located'},
                        'include_forecast': {'type': 'boolean',
                                             'description': 'Include air quality and pollen forecast'},
                        'forecast_days': {'type': 'integer', 'minimum': 1, 'maximum': 7,
                                          'description': 'Number of forecast days'},
                    },
                    'required': ['city', 'country'],
                },
            },
        },
        {
            'type': 'function',
            'function': {
                'name': 'get_travel_advisories',
                'description': 'Get current travel advisories and safety information for a destination',
                'parameters': {
                    'type': 'object',
                    'properties': {
                        'city': {'type': 'string', 'description': 'The name of the city'},
                        'country': {'type': 'string', 'description': 'The country where the city is located'},
                        'advisory_types': {'type': 'array', 'items': {'type': 'string',
                                                                      'enum': ['safety', 'health', 'entry_requirements',
                                                                               'local_laws']},
                                           'description': 'Types of advisories to include'},
                    },
                    'required': ['city', 'country'],
                },
            },
        },
        {
            'type': 'function',
            'function': {
                'name': 'get_local_events',
                'description': 'Get information about local events in a city during a specific date range',
                'parameters': {
                    'type': 'object',
                    'properties': {
                        'city': {'type': 'string', 'description': 'The name of the city'},
                        'start_date': {'type': 'string', 'format': 'date', 'description': 'Start date (YYYY-MM-DD)'},
                        'end_date': {'type': 'string', 'format': 'date', 'description': 'End date (YYYY-MM-DD)'},
                        'event_types': {'type': 'array', 'items': {'type': 'string',
                                                                   'enum': ['business', 'cultural', 'networking',
                                                                            'entertainment']},
                                        'description': 'Types of events to include'},
                        'max_results': {'type': 'integer', 'minimum': 1, 'maximum': 50,
                                        'description': 'Maximum number of events to return'},
                    },
                    'required': ['city', 'start_date', 'end_date'],
                },
            },
        },
        {
            'type': 'function',
            'function': {
                'name': 'get_restaurant_recommendations',
                'description': 'Get restaurant recommendations in a specific area of a city',
                'parameters': {
                    'type': 'object',
                    'properties': {
                        'city': {'type': 'string', 'description': 'The name of the city'},
                        'area': {'type': 'string', 'description': 'Specific area or district in the city'},
                        'cuisine_types': {'type': 'array', 'items': {'type': 'string'},
                                          'description': 'Types of cuisine to consider'},
                        'price_range': {'type': 'string', 'enum': ['$', '$$', '$$$', '$$$$'],
                                        'description': 'Price range of restaurants'},
                        'suitable_for': {'type': 'array', 'items': {'type': 'string',
                                                                    'enum': ['business_meetings', 'groups',
                                                                             'quiet_conversation', 'quick_meal']},
                                         'description': 'Suitability factors'},
                        'min_rating': {'type': 'number', 'minimum': 0, 'maximum': 5,
                                       'description': 'Minimum rating of restaurants'},
                        'max_results': {'type': 'integer', 'minimum': 1, 'maximum': 20,
                                        'description': 'Maximum number of recommendations'},
                    },
                    'required': ['city', 'area'],
                },
            },
        },
    ],
)

tool_calls = response['message']['tool_calls']

table = Table(title="Tool Calls")
table.add_column("Function Name", style="cyan")
table.add_column("Arguments", style="magenta")

for call in tool_calls:
    function_name = call['function']['name']
    arguments = call['function']['arguments']
    table.add_row(function_name, str(arguments))

console.print(Panel(table, title="Ollama Chat Response", border_style="bold green"))
