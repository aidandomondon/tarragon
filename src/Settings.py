from nicegui import ui

def open_kill_assistant_dialogue(state):

    def _clear_assistant(state: dict):
        state["content_loader"].clean_and_reinit()

    with ui.dialog() as dialogue:
        with ui.card():
            with ui.column().classes('items-center'):
                ui.label(
                    "Are you sure you want to wipe and kill the assistant? " \
                    "This will remove all documents you have uploaded."
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