import json
import os
import typing
import uuid
from typing import Any, Dict, List, Optional, Text

import requests
from dotenv import load_dotenv
from rasa_sdk import Action, Tracker
from rasa_sdk.events import ConversationPaused, UserUtteranceReverted
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.forms import FormValidationAction

if typing.TYPE_CHECKING:  # pragma: no cover
    from rasa_sdk import Tracker
    from rasa_sdk.executor import CollectingDispatcher
    from rasa_sdk.types import DomainDict

load_dotenv()


def get_env_var(key):
    env_var = os.getenv(key)
    if env_var is None:
        raise RuntimeError(f"Environment variable {key} was not found.")
    return env_var


airtable_api_key = get_env_var("AIRTABLE_API_KEY")
base_id = get_env_var("BASE_ID")
table_name = get_env_var("TABLE_NAME")


def create_newsletter_record(occupation, frequency, notifications, recommend, satisfaction):
    request_url = f"https://api.airtable.com/v0/{base_id}/{table_name}"

    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "Authorization": f"Bearer {airtable_api_key}",
    }

    data = {
        "fields": {
            "Id": str(uuid.uuid4()),
            "Occupation": occupation,
            "Frequency": frequency,
            "Found succeed?": notifications,
            "Would recommend?": recommend,
            "Satisfaction": satisfaction,
        }
    }

    print(request_url)
    print(headers)
    print(json.dumps(data))

    try:
        response = requests.post(
            request_url, headers=headers, data=json.dumps(data)
        )
        response.raise_for_status()
    except requests.exceptions.HTTPError as err:
        raise SystemExit(err)

    print(f"Response status code: {response.status_code}")
    return response


class ValidateNewsletterForm(FormValidationAction):
    def name(self) -> Text:
        return "validate_newsletter_form"

    async def required_slots(
            self,
            slots_mapped_in_domain: List[Text],
            dispatcher: "CollectingDispatcher",
            tracker: "Tracker",
            domain: "DomainDict",
    ) -> Optional[List[Text]]:
        if not tracker.get_slot("recommend"):
            slots_mapped_in_domain.remove("satisfaction")

        return slots_mapped_in_domain


class SubmitNewsletterForm(Action):

    def name(self) -> Text:
        return "submit_newsletter_form"

    async def run(
            self, dispatcher, tracker: Tracker, domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:
        occupation = tracker.get_slot("occupation")
        frequency = tracker.get_slot("frequency")
        notifications = tracker.get_slot("notifications")
        recommend = tracker.get_slot("recommend")
        satisfaction = tracker.get_slot("satisfaction")

        response = create_newsletter_record(
            occupation, frequency, notifications, recommend, satisfaction)

        dispatcher.utter_message(
            "¡Gracias, tus respuestas han sido registradas!")

        return []

    # class ActionDefaultFallback(Action):
    #     def name(self) -> Text:
    #         return "action_default_fallback"

    #     def run(self, dispatcher, tracker, domain):
    #         # output a message saying that the bot did not understood the message

    #         message = "Lo siento, no lo entendí. ¿Me lo puedes aclarar?"
    #         dispatcher.utter_message(text=message)
    #         # pause tracker
    #         # undo last user interaction
    #         return [ConversationPaused(), UserUtteranceReverted()]

# class ActionSayStuff(Action):
#     def name(self) -> Text:
#         return "action_say_stuff"
#
#     def run(self,
#             dispatcher: CollectingDispatcher,
#             tracker: Tracker,
#             domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
#         dispatcher.utter_message("Stuff")
#
#         return []
