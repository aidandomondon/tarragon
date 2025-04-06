from nicegui import ui
from State import State

def open_kill_assistant_dialogue(state):

    async def _clear_assistant(state: State):
        # Wipe chat
        chat_notifier = ui.notification("Wiping chat...")
        chat_notifier.spinner = True
        state.chat_history = []
        state.displayed_chat_history = []
        state.refresh_chat()
        chat_notifier.dismiss()
        
        # Clear uploads
        state.clear_uploads()

        # Wipe data
        wiping_notifier = ui.notification("Wiping data and re-initializing...")
        wiping_notifier.spinner = True
        await state.content_loader.clean_and_reinit()
        wiping_notifier.dismiss()
        ui.notify("Data wipe successful.")

    with ui.dialog() as dialogue:
        with ui.card():
            with ui.column().classes('items-center'):
                ui.label(
                    "Are you sure you want to wipe and kill the assistant? " \
                    "This will remove all documents you have uploaded" \
                    "and erase the current chat history."
                )
                with ui.row():
                    ui.button(
                        text="Kill assistant",
                        color = 'red',
                        on_click = lambda _: _clear_assistant(state)
                    )
                    ui.button(
                        text = "Cancel",
                        color= "blue",
                        on_click = lambda _: dialogue.close()
                    )
    dialogue.open()


def Settings(state):
    with ui.column().classes('w-full items-center'):
        ui.markdown('#Manage Data')
        ui.button(
            text='Wipe and kill assistant',
            on_click=lambda _: open_kill_assistant_dialogue(state)
        ).props("color='black' unelevated")