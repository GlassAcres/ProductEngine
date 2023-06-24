import os
import requests
from datetime import datetime
from supabase_py import Client, create_client
import aiohttp

supabase_url = os.environ['SUPABASE_URL']
supabase_key = os.environ['SUPABASE_KEY']
supabase: Client = create_client(supabase_url, supabase_key)

class MessageHandler:
    def __init__(self):
        self.messages = []

    def print_and_store(self, message, supabase: Client):
        print(message)
        self.messages.append(message)
        self.messages[:] = self.messages[-15:]
        self.log_to_supabase(message, supabase)

    def log_to_supabase(self, message, supabase: Client):
        supabase.table('Events').insert([
            {
                'timestamp': datetime.now(),
                'event': message,
            },
        ])

def print_and_store(message_handler, message):
    message_handler.print_and_store(message, supabase)

def log_event(supabase: Client, event: dict):
    supabase.table('Events').insert([event]).execute()

def generate_blank_table():
    table = "| Field | Details |\n| --- | --- |\n"
    fields = [
        "Product/Service Name",
        "Description",
        "Target Audience",
        "User Needs",
        "Key Features",
        "Competitive Advantage",
        "Various Metadata Tags",
        "Tagline",
        "Suggested Keywords",
        "General SEO Suggestions"
    ]
    for field in fields:
        table += f"| {field} | |\n"
    return table
