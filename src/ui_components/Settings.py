from nicegui import ui
from nicegui.elements.dialog import Dialog
from State import State

def open_kill_assistant_dialogue(state):

    def _handle_clear_assistant(state: State, dialogue: Dialog) -> None:
        _clear_assistant(state)
        state.db_client.reinit_db_client()
        dialogue.close()

    def _clear_assistant(state: State):
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
        state.db_client.clean_and_reinit()
        wiping_notifier.dismiss()
        ui.notify("Data wipe successful.")


    with ui.dialog() as dialogue:
        with ui.card():
            with ui.column().classes('items-center'):
                ui.label(
                    "Are you sure you want to wipe and kill the assistant? " \
                    "The application will no longer have any of the documents " \
                    "you have uploaded and the current chat history will be erased."
                )
                with ui.row():
                    ui.button(
                        text="Kill assistant",
                        color = 'red',
                        on_click = lambda _: _handle_clear_assistant(state, dialogue)
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