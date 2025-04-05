from nicegui.binding import bindable_dataclass

@bindable_dataclass
class Messages:
    messages: list[dict] = []