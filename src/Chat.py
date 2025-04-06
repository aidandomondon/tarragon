from State import State
from nicegui import ui
from ChatMessage import ChatMessage
from ollama import AsyncClient, ChatResponse
from PromptBuilder import PromptBuilder
import asyncio

MODEL = 'llama3.2:1b'

# Sends a message to the chatbot
async def query_chatbot(state: State):
    # await asyncio.sleep(5)
    # return { "message": { "role": "system", "content": "Hi" } }
    client = AsyncClient(host='http://localhost:11434')
    return await client.chat(MODEL, state.chat_history)

async def on_send_message(state: State) -> None:
    # Get user's question
    message = state.unsent_prompt

    # Clear new message entry field 
    state.unsent_prompt = ''

    # Update displayed chat history with user's new question
    state.displayed_chat_history.append({
        "role": "user",
        "content": message
    })
    MessagePane.refresh()


    # Update actual chat history with user's new question
    # and query the LLM for a response
    prepping_question_notifier = ui.notification("Processing question...")
    prepping_question_notifier.spinner = True
    state.chat_history.append({
        "role": "user",
        "content": await PromptBuilder().build_prompt(message)
    })
    prepping_question_notifier.dismiss()


    # Send message to chatbot
    pacifier = ui.notification("Thinking...")
    pacifier.spinner = True
    response: ChatResponse = await query_chatbot(state)
    pacifier.dismiss()
    

    # Add LLM response to chat history
    state.displayed_chat_history.append({
        "role": response["message"]["role"],
        "content": response["message"]["content"]
    })
    state.chat_history.append({
        "role": response["message"]["role"],
        "content": response["message"]["content"]
    })
    MessagePane.refresh()

@ui.refreshable
def MessagePane(state: State) -> None:
    with ui.column().classes('fit col'):
        with ui.scroll_area().classes('h-full') as scroll_area:
            for message in state.displayed_chat_history:
                if message["role"] == "user":
                    with ui.element('div').classes('w-2/3 self-center'):
                        ChatMessage(message["content"], from_bot=False)
                else:
                    with ui.element('div').classes('w-2/3 self-center'):
                        ChatMessage(message["content"], from_bot=True)
    scroll_area.scroll_to(percent=100)

def PromptPane(state: State) -> None:
    with ui.card().classes('w-2/3 bg-white self-center'):
        with ui.row(wrap=False).classes('w-full pt-0'):
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

def Chat(state: State) -> None:
    with ui.column().classes('w-full h-full gap-0'):
        MessagePane(state)
        PromptPane(state)