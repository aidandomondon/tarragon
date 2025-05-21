from json import loads
from State import State
from nicegui import ui
from ui_components.ChatMessage import ChatMessage
from openai import AsyncOpenAI
from openai.types.chat import ChatCompletion
from openai.types.chat.chat_completion import Choice

with open('./config.json', 'r') as file:
    config = loads(file.read())

# Sends a message to the chatbot
async def query_chatbot(state: State) -> Choice:
    client = AsyncOpenAI(
        base_url = f'http://localhost:{config["llm_port"]}/v1',
        api_key='sk-no-key-required'
    )
    completion: ChatCompletion = await client.chat.completions.create(
        model = config["chat"]["model"], 
        messages = state.chat_history
    )
    return completion.choices[0]

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
        "content": state.prompt_builder.build_prompt(message)
    })
    prepping_question_notifier.dismiss()


    # Send message to chatbot
    pacifier = ui.notification("Thinking...")
    pacifier.spinner = True
    response: Choice = await query_chatbot(state)
    pacifier.dismiss()


    # Add LLM response to chat history
    response_content = response.message.content
    response_content = response_content[:response_content.find("<|eot_id|>")]
    state.displayed_chat_history.append({
        "role": response.message.role,
        "content": response_content
    })
    state.chat_history.append({
        "role": response.message.role,
        "content": response_content
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

def refresh_chat():
    MessagePane.refresh()

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
    state.refresh_chat = refresh_chat