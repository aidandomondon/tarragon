from nicegui import ui
from nicegui.events import UploadEventArguments
from model.ContentLoader import ContentLoader
from State import State

async def _on_upload(file: UploadEventArguments, model: ContentLoader):
    upload_notifier = ui.notification('Upload successful. Storing...')
    upload_notifier.spinner = True
    await model.ingest(file.name, file.content.read(), file.type)
    upload_notifier.dismiss()

def ContentLoaderMenu(state: State):
    model: ContentLoader = state.content_loader
    with ui.row().classes('w-full'):
        upload = ui.upload(
            label='Upload Files',
            multiple=True,
            on_upload=lambda e: _on_upload(e, model),
            on_rejected=lambda _: ui.notify('Error! File upload failed.')
        ).classes('w-full').props("accept='.txt, .pdf' color='black' flat bordered")
        state.clear_uploads = upload.reset