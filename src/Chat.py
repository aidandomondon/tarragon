from nicegui import ui
from ChatMessage import ChatMessage



def Chat(state) -> None:
    # Sends a message to the chatbot
    def query_chatbot(message: str) -> None:
        print(message)

    def on_send_message(message: str) -> None:
        query_chatbot(message)
        state['unsent_prompt'] = ''

    with ui.column().classes('w-full h-[calc(100vh-2rem)]'):
        with ui.scroll_area().classes('w-full h-full'):
            ChatMessage('Hi!', from_bot=False)
            ChatMessage('Hi! How may I help you?', from_bot=True)
            ChatMessage('Give me money!', from_bot=False)
            ChatMessage('No!', from_bot=True)
            ChatMessage('But I can offer you a coupon.\nFive dollars worth', from_bot=True)
            ChatMessage('Give me money!', from_bot=False)
            ChatMessage('Give me money!', from_bot=False)
            ChatMessage('Give me money!', from_bot=False)
        with ui.row(wrap=False).classes('w-full'):
            ui.textarea('Ask a question...') \
                .bind_value(state, 'unsent_prompt') \
                .classes('w-full border') \
                .props("color='black'")
            ui.button('Send', 
                      on_click=lambda _: on_send_message(state['unsent_prompt']),
                      color='black'
            ).props("text-color='white'")