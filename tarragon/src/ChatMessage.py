from nicegui import ui

def ChatMessage(message: str, from_bot: bool = True):
    with ui.row().classes('w-full'):
        if from_bot:
            ui.chat_message(message, name='Tarragon').props("bg-color='black' text-color='white'")
        else:
            ui.space()
            ui.chat_message(message, name='You', sent=True)