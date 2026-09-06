import json

from google.adk.agents import LlmAgent


def get_menu() -> str:
    """Retrieves the coffee shop menu from menu.json."""
    try:
        with open("menu.json", "r") as f:
            menu_data = json.load(f)
            return json.dumps(menu_data)
    except Exception as e:
        return json.dumps({"error": str(e)})


barista_agent = LlmAgent(
    name="barista_agent",
    model="gemini-3.8-flash",
    instruction="""
You are a friendly barista at Coffee Shop.

Recommend drinks and pastries ONLY from the menu returned by get_menu().

Rules:
1. Never invent menu items.
2. Use the menu's actual descriptions, tags and allergens.
3. If the customer is dairy-free or lactose intolerant,
   recommend only suitable items.
4. If an item is not in the menu, clearly say it is unavailable.
5. If the customer's preference is unclear, ask exactly ONE
   friendly clarifying question.
6. Be warm, helpful and professional.

Always use get_menu() before making recommendations.
""",
    tools=[get_menu]
)

