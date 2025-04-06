from nicegui import ui
from model.ContentLoader import ContentLoader
from ContentLoaderMenu import ContentLoaderMenu
from Chat import Chat
from Settings import Settings
from State import State

state = State()

with ui.column().classes('w-full h-[calc(100vh-2rem)]'):
    with ui.tabs().classes('w-full') as tabs:
        ui.tab('addContent', label='Add Content')
        ui.tab('chat', label='Chat')
        ui.tab('settings', label='Settings')
    with ui.tab_panels(tabs).classes('w-full'):
        with ui.tab_panel('addContent'):
            ContentLoaderMenu(state.content_loader)
        with ui.tab_panel('chat').classes('w-full'):
            Chat(state)
        with ui.tab_panel('settings').classes('w-full'):
            Settings(state)

ui.run(
    title='Tarragon', 
    favicon='../T.ico', 
    native=True, 
    port=8081
)