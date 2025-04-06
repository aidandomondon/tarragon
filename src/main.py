from nicegui import ui
from ui_components.ContentLoaderMenu import ContentLoaderMenu
from ui_components.Chat import Chat
from ui_components.Settings import Settings
from State import State
from json import loads

with open('./config.json') as file:
    config = loads(file.read())

state = State()

with ui.column().classes('w-full h-[calc(100vh-2rem)] overscroll-none'):
    with ui.tabs().classes('w-full') as tabs:
        ui.tab('addContent', label='Add Content')
        ui.tab('chat', label='Chat')
        ui.tab('settings', label='Settings')
    with ui.tab_panels(tabs).classes('w-full h-full'):
        with ui.tab_panel('addContent'):
            ContentLoaderMenu(state)
        with ui.tab_panel('chat').classes('w-full h-full'):
            Chat(state)
        with ui.tab_panel('settings').classes('w-full'):
            Settings(state)

ui.run(
    title='Tarragon', 
    favicon='../T.ico', 
    native=True, 
    port=config["main_port"]
)