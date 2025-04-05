from nicegui import ui
from ChatMessage import ChatMessage
from ollama import chat, ChatResponse
from PromptBuilder import PromptBuilder
import asyncio

MODEL = 'llama3.2:1b'

# Sends a message to the chatbot
async def query_chatbot(state: dict):
    await asyncio.sleep(5)
    return { "message": { "role": "system", "content": "Hi" } }
    # return chat(MODEL, state["chat_history"])

async def on_send_message(state) -> None:
        # Get user's question
        message = state['unsent_prompt']
        
        # Clear new message entry field 
        state['unsent_prompt'] = ''

        # Update displayed chat history with user's new question
        state["displayed_chat_history"].append({
            "role": "user",
            "content": message
        })

        # Update actual chat history with user's new question
        # and query the LLM for a response
        state["chat_history"].append({
            "role": "user",
            "content": PromptBuilder().build_prompt(message)
        })

        pacifier = ui.notification("Thinking...")
        pacifier.spinner = True
        
        # Send message to chatbot
        response: ChatResponse = await query_chatbot(state)

        pacifier.spinner = False
        pacifier.dismiss()

        # Add LLM response to chat history
        state["displayed_chat_history"].append({
            "role": response["message"]["role"],
            "content": response["message"]["content"]
        })
        state["chat_history"].append({
            "role": response["message"]["role"],
            "content": response["message"]["content"]
        })

def Chat(state) -> None:

    with ui.column().classes('w-full h-[calc(100vh-2rem)]'):
        with ui.scroll_area().classes('w-full h-full'):
            for message in state["displayed_chat_history"]:
                if message["role"] == "user":
                    ChatMessage(message["content"], from_bot=False)
                else:
                    ChatMessage(message["content"], from_bot=True)
                    
        with ui.card().classes('w-[calc(100vh*0.85)] absolute bottom-1 bg-white self-center'):
            with ui.row(wrap=False).classes('w-full'):
                ui.textarea() \
                    .bind_value(state, 'unsent_prompt') \
                    .classes('w-full') \
                    .props("color=white") \
                    .props("standout") \
                    .props("dense") \
                    .props('autogrow') \
                    .props("label='Ask a question...'") \
                    .props("stack-label")
                ui.button('Send', 
                    on_click=lambda _: on_send_message(state),
                    color='black'
                ).props("text-color='white'")