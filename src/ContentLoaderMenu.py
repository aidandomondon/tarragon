from nicegui import ui
from nicegui.events import UploadEventArguments
from model.ContentLoader import ContentLoader

def _on_upload(file: UploadEventArguments, model: ContentLoader):
    ui.notify('Upload successful. Learning...')
    model.ingest(file.name, file.content.read(), file.type)

def ContentLoaderMenu(model: ContentLoader):
    with ui.row().classes('w-full'):
        ui.upload(
            label='Upload Files',
            multiple=True,
            on_upload=lambda e: _on_upload(e, model),
            on_rejected=lambda _: ui.notify('Error! File upload failed.')
        ).classes('w-full').props("accept='.txt, .pdf' color='black' flat bordered")