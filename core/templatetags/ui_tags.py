from django import template

register = template.Library()

@register.simple_tag
def btn_primary():
    return "text-white bg-blue-700 hover:bg-blue-800 focus:ring-4 focus:ring-blue-300 font-medium rounded-lg text-sm px-5 py-2.5 me-2 mb-2 dark:bg-blue-600 dark:hover:bg-blue-700 focus:outline-none dark:focus:ring-blue-800"

@register.simple_tag
def btn_success():
    return "focus:outline-none text-white bg-green-700 hover:bg-green-800 focus:ring-4 focus:ring-green-300 font-medium rounded-lg text-sm px-5 py-2.5 me-2 mb-2 dark:bg-green-600 dark:hover:bg-green-700 dark:focus:ring-green-800"

@register.simple_tag
def btn_danger():
    return "focus:outline-none text-white bg-red-700 hover:bg-red-800 focus:ring-4 focus:ring-red-300 font-medium rounded-lg text-sm px-5 py-2.5 me-2 mb-2 dark:bg-red-600 dark:hover:bg-red-700 dark:focus:ring-red-900"

@register.simple_tag
def btn_warning():
    return "focus:outline-none text-white bg-yellow-400 hover:bg-yellow-500 focus:ring-4 focus:ring-yellow-300 font-medium rounded-lg text-sm px-5 py-2.5 me-2 mb-2 dark:focus:ring-yellow-900"

@register.simple_tag
def btn_secondary():
    return "text-white bg-gray-800 hover:bg-gray-900 focus:outline-none focus:ring-4 focus:ring-gray-300 font-medium rounded-lg text-sm px-5 py-2.5 me-2 mb-2 dark:bg-gray-800 dark:hover:bg-gray-700 dark:focus:ring-gray-700 dark:border-gray-700"

@register.simple_tag
def card_base():
    return "relative flex flex-col mt-6 text-gray-700 bg-white shadow-md bg-clip-border rounded-xl w-96 transform scale-110"

@register.simple_tag
def header_container():
    return "flex items-center justify-end h-auto mb-4 rounded bg-gray-100 dark:bg-gray-800 p-6"

@register.simple_tag
def header_title():
    return "mb-4 text-4xl font-extrabold leading-none tracking-tight text-gray-900 md:text-5xl lg:text-6xl dark:text-white"

@register.simple_tag
def header_mark():
    return "px-2 text-white bg-blue-700 rounded dark:bg-blue-500"

@register.simple_tag
def search_container():
    return "flex-col justify-start rounded bg-gray-100 h-full dark:bg-gray-800 p-4 max-w-full w-full"

@register.simple_tag
def table_container():
    return "relative overflow-x-auto shadow-md sm:rounded-lg max-w-full w-full px-10"

@register.simple_tag
def table_base():
    return "w-full text-sm text-left rtl:text-right text-gray-500 dark:text-gray-400"

@register.simple_tag
def table_head():
    return "text-xs text-white uppercase bg-blue-700 dark:bg-gray-700 dark:text-gray-400"

@register.simple_tag
def table_row():
    return "odd:bg-white odd:dark:bg-gray-900 even:bg-gray-100 even:dark:bg-gray-800 border-b dark:border-gray-700"

@register.simple_tag
def input_label():
    return "peer-focus:font-medium absolute text-sm text-gray-500 dark:text-gray-400 duration-300 transform -translate-y-6 scale-75 top-3 -z-10 origin-[0] peer-focus:start-0 rtl:peer-focus:translate-x-1/4 rtl:peer-focus:left-auto peer-focus:text-blue-600 peer-focus:dark:text-blue-500 peer-placeholder-shown:scale-100 peer-placeholder-shown:translate-y-0 peer-focus:scale-75 peer-focus:-translate-y-6"

@register.simple_tag
def page_container():
    return "flex items-center max-w-full w-full h-auto mb-4 rounded bg-gray-100 dark:bg-gray-800 p-6 gap-3 justify-center flex-wrap"

@register.simple_tag
def search_button():
    return "text-white bg-blue-700 hover:bg-blue-800 focus:ring-4 focus:ring-blue-300 flex justify-center items-center gap-4 font-medium rounded-lg text-sm px-5 py-2.5 me-2 mb-2 dark:bg-blue-600 dark:hover:bg-blue-700 focus:outline-none dark:focus:ring-blue-800"

@register.simple_tag
def form_container():
    return "flex-col justify-start rounded bg-gray-100 h-full dark:bg-gray-800 p-4 max-w-full w-full"

@register.simple_tag
def dashboard_card():
    return "flex flex-col bg-white rounded-lg shadow-md w-full m-6 overflow-hidden sm:w-52"

@register.simple_tag
def login_container():
    return "w-full max-w-sm p-4 bg-gray-50 border border-gray-800 rounded-tl-2xl shadow sm:p-6 md:p-8 dark:bg-gray-800 dark:border-gray-700"

@register.filter(name='add_class')
def add_class(value, arg):
    return value.as_widget(attrs={'class': arg})

@register.filter(name='style_input')
def style_input(value, extra_classes=""):
    base_classes = "bg-gray-50 border border-gray-300 text-gray-900 sm:text-sm rounded-lg focus:ring-brand-600 focus:border-brand-600 block w-full p-2.5 dark:bg-gray-800 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-brand-500 dark:focus:border-brand-500"
    if extra_classes:
        base_classes = f"{base_classes} {extra_classes}"
    return value.as_widget(attrs={'class': base_classes})

@register.inclusion_tag('ui/action_button.html')
def action_button(url, type='view', title=None, text=None, extra_classes='', target=None, confirm_message=None):
    extra_attrs = ""
    if target:
        extra_attrs += f' target="{target}"'
    if confirm_message:
        escaped_message = confirm_message.replace("'", "\\'")
        extra_attrs += f' onclick="return confirm(\'{escaped_message}\')"'

    return {
        'url': url,
        'type': type,
        'title': title,
        'text': text,
        'extra_classes': extra_classes,
        'extra_attrs': extra_attrs,
    }

@register.inclusion_tag('ui/status_badge.html')
def status_badge(status, type=None, text=None, extra_classes=''):
    """
    Renders a status badge with consistent styling and icons.
    Args:
        status: The status value (code or text) used for logic.
        type: Optional explicit type ('success', 'warning', 'danger', 'info').
        text: Optional text to display instead of the status value.
    """
    return {
        'status': status,
        'type': type,
        'text': text,
        'extra_classes': extra_classes
    }
