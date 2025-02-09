"""Example with which we test UI elements with L10N support."""

import os
from contextlib import asynccontextmanager
from typing import Annotated

from fastapi import FastAPI, responses, Header, Request, Depends, BackgroundTasks
from fastapi.responses import StreamingResponse
from starlette.middleware.base import BaseHTTPMiddleware
from pydantic import BaseModel

from nc_py_api import NextcloudApp
from nc_py_api.ex_app import (
    run_app,
    set_handlers,
    AppAPIAuthMiddleware,
    SettingsField,
    SettingsFieldType,
    SettingsForm,
    nc_app,
)

from nc_py_api.files import ActionFileInfo, ActionFileInfoEx

from contextvars import ContextVar

from gettext import translation


from PIL import Image
from PIL.ExifTags import TAGS
import io
import ffmpeg
import tempfile
from datetime import datetime


LOCALE_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "locale")
# current_translator = ContextVar("current_translator")
# current_translator.set(translation(os.getenv("APP_ID"), LOCALE_DIR, languages=["en"], fallback=True))


def _(text):
    # return current_translator.get().gettext(text)
    return text

# class LocalizationMiddleware(BaseHTTPMiddleware):
#     async def dispatch(self, request: Request, call_next):
#         request_lang = request.headers.get('Accept-Language', 'en')
#         translator = translation(
#             os.getenv("APP_ID"), LOCALE_DIR, languages=[request_lang], fallback=True
#         )
#         current_translator.set(translator)
#         print(_("UI example"))
#         response = await call_next(request)
#         return response

@asynccontextmanager
async def lifespan(app: FastAPI):
    set_handlers(app, enabled_handler)
    print(_("UI example"))
    yield

APP = FastAPI(lifespan=lifespan)
APP.add_middleware(AppAPIAuthMiddleware)
# APP.add_middleware(LocalizationMiddleware)

SETTINGS_EXAMPLE = SettingsForm(
    id="settings_example",
    section_type="admin",
    section_id="ai_integration_team",
    title=_("Example of declarative settings"),
    description=_("These fields are rendered dynamically from declarative schema"),
    fields=[
        SettingsField(
            id="field1",
            title="Multi-selection",
            description=_("Select some option setting"),
            type=SettingsFieldType.MULTI_SELECT,
            default=["foo", "bar"],
            placeholder=_("Select some multiple options"),
            options=["foo", "bar", "baz"],
        ),
        SettingsField(
            id="some_real_setting",
            title=_("Choose init status check background job interval"),
            description=_("How often ExApp should check for initialization status"),
            type=SettingsFieldType.RADIO,
            default="40m",
            placeholder=_("Choose init status check background job interval"),
            options={
                _("Each 40 minutes"): "40m",
                _("Each 60 minutes"): "60m",
                _("Each 120 minutes"): "120m",
                _("Each day"): f"{60 * 24}m",
            },
        ),
        SettingsField(
            id="test_ex_app_field_1",
            title=_("Default text field"),
            description=_("Set some simple text setting"),
            type=SettingsFieldType.TEXT,
            default="foo",
            placeholder=_("Enter text setting"),
        ),
        SettingsField(
            id="test_ex_app_field_1_1",
            title=_("Email field"),
            description=_("Set email config"),
            type=SettingsFieldType.EMAIL,
            default="",
            placeholder=_("Enter email"),
        ),
        SettingsField(
            id="test_ex_app_field_1_2",
            title=_("Tel field"),
            description=_("Set tel config"),
            type=SettingsFieldType.TEL,
            default="",
            placeholder=_("Enter your tel"),
        ),
        SettingsField(
            id="test_ex_app_field_1_3",
            title=_("Url (website) field"),
            description=_("Set url config"),
            type=SettingsFieldType.URL,
            default="",
            placeholder=_("Enter url"),
        ),
        SettingsField(
            id="test_ex_app_field_1_4",
            title=_("Number field"),
            description=_("Set number config"),
            type=SettingsFieldType.NUMBER,
            default=0,
            placeholder=_("Enter number value"),
        ),
        SettingsField(
            id="test_ex_app_field_2",
            title=_("Password"),
            description=_("Set some secure value setting"),
            type=SettingsFieldType.PASSWORD,
            default="",
            placeholder=_("Set secure value"),
        ),
        SettingsField(
            id="test_ex_app_field_3",
            title=_("Selection"),
            description=_("Select some option setting"),
            type=SettingsFieldType.SELECT,
            default="foo",
            placeholder=_("Select some option setting"),
            options=["foo", "bar", "baz"],
        ),
        SettingsField(
            id="test_ex_app_field_3",
            title=_("Selection"),
            description=_("Select some option setting"),
            type=SettingsFieldType.SELECT,
            default="foo",
            placeholder=_("Select some option setting"),
            options=["foo", "bar", "baz"],
        ),
        SettingsField(
            id="test_ex_app_field_4",
            title=_("Toggle something"),
            description=_("Select checkbox option setting"),
            type=SettingsFieldType.CHECKBOX,
            default=False,
            label=_("Verify something if enabled"),
        ),
        SettingsField(
            id="test_ex_app_field_5",
            title=_("Multiple checkbox toggles, describing one setting"),
            description=_("Select checkbox option setting"),
            type=SettingsFieldType.MULTI_CHECKBOX,
            default={"foo": True, "bar": True},
            options={"Foo": "foo", "Bar": "bar", "Baz": "baz", "Qux": "qux"},
        ),
        SettingsField(
            id="test_ex_app_field_6",
            title=_("Radio toggles, describing one setting like single select"),
            description=_("Select radio option setting"),
            type=SettingsFieldType.RADIO,
            label=_("Select single toggle"),
            default="foo",
            options={_("First radio"): "foo", _("Second radio"): "bar", _("Third radio"): "baz"},
        ),
    ],
)

@APP.post("/api/rename_media")
async def rename_media(
    files: ActionFileInfoEx,
    nc: Annotated[NextcloudApp, Depends(nc_app)],
    background_tasks: BackgroundTasks,
):
    background_tasks.add_task(rename_media_handler, files, nc)
    return responses.JSONResponse(content={"rename_media": "success"})


import re

# Regex pattern for checking if the filename starts with the date-time format
pattern = r'^\d{4}-\d{2}-\d{2} \d{2}-\d{2}'

def rename_media_handler(files: ActionFileInfoEx, nc: NextcloudApp):
    total_files = len(files.files)
    if (total_files == 0):
        return
    current_progress = 0
    for file in files.files:
        current_progress += 1
        # if (current_progress % 10) == 0:
            # nc.notifications.create("info", _(f"Renaming {current_progress} of {total_files} files ({(current_progress / total_files) * 100:.2f}%)"))
        node = file.to_fs_node()
        media_type, file_ext = file.mime.split('/')

        if media_type not in ['image', 'video']:
            print(f"Unsupported media type: {media_type}")
            continue

        # check if the file is already renamed by checking if the file name starts with a date
        if re.match(pattern, file.name):
            continue

        creation_date = ''

        # Download the file from Nextcloud
        file_bytes = nc.files.download(node)

        have_creation_date = False

        try:
            if media_type == 'image':
                img = Image.open(io.BytesIO(file_bytes))
                exif_data = img._getexif()
                
                if exif_data:
                    for tag, value in exif_data.items():
                        tag_name = TAGS.get(tag, tag)
                        if tag_name == 'DateTimeOriginal':
                            creation_date = datetime.strptime(value, '%Y:%m:%d %H:%M:%S')
                            creation_date = creation_date.strftime('%Y-%m-%d %H-%M')
                            have_creation_date = True
                            break
                
                if not creation_date:
                    print("Creation date not found in EXIF data.")
            
            elif media_type == 'video':
                # Use tempfile to create a temporary file for the video
                with tempfile.NamedTemporaryFile(suffix='.mp4', delete=True) as temp_video_file:
                    temp_video_file.write(file_bytes)
                    temp_video_file.flush()  # Ensure all data is written
                    
                    # Get metadata using ffmpeg
                    probe = ffmpeg.probe(temp_video_file.name)
                    creation_date = probe['format']['tags'].get('creation_time', '')
                    if creation_date:
                        print(f"Creation date found: {creation_date}")
                    else:
                        print("Creation date not found in video metadata.")
                        
                # Format the creation date
                if creation_date:
                    try:
                        # Parse the date string to a datetime object
                        dt = datetime.fromisoformat(creation_date.replace('Z', '+00:00'))
                        # Format it to the desired output
                        creation_date = dt.strftime('%Y-%m-%d %H-%M')
                        have_creation_date = True
                    except ValueError:
                        print(f"Error parsing creation date: {creation_date}")
            
            else:
                print(f"Unsupported media type: {media_type}")

        
        except Exception as e:
            # nc.notifications.create("error", _(f"Error processing file {file.name}: {str(e)}"))
            print(f"Error processing file {file.name}: {str(e)}")

        if have_creation_date:
            # Rename the file
            new_name = f"{creation_date} {file.name}"
            dir = node.full_path.split('/')
            dir = dir[2:-1]
            dir = '/'.join(dir)
            old_path = node.full_path
            new_path = f"{dir}/{new_name}"
            nc.files.move(node, new_path)
        else:
            nc.notifications.create("error", f"Creation date not found for file {node.info.fileid}, media type: {media_type}, ext: {file_ext}")
            print(f"Creation date not found for file {node.info.fileid}, media type: {media_type}, ext: {file_ext}")
    


def enabled_handler(enabled: bool, nc: NextcloudApp) -> str:
    print(f"enabled={enabled}")
    if enabled:

        nc.ui.resources.set_script("top_menu", "index", "js/sunny-slide-show-main")
        nc.ui.top_menu.register("index", "Sunny Slide Show", "img/app.svg")
        nc.ui.files_dropdown_menu.register_ex("rename_media", _("Rename by Taken Date"), "api/rename_media", mime="image, video",
                                        icon="img/app-dark.svg")
        nc.ui.files_dropdown_menu.register_ex("redirect_slideshow", _("To Slide Show"), "api/redirect_slide_show", mime="image, video",
                                        icon="img/app-dark.svg")

        if nc.srv_version["major"] >= 29:
            nc.ui.settings.register_form(SETTINGS_EXAMPLE)
    else:
        nc.ui.resources.delete_script("top_menu", "index", "js/ui_example-main")
        nc.ui.top_menu.unregister("index")
        nc.ui.files_dropdown_menu.unregister("redirect_slideshow")
    return ""

class Button1Format(BaseModel):
    initial_value: str

nc_instance: NextcloudApp

@APP.post("/api/redirect_slide_show")
async def test_menu_handler(
    files: ActionFileInfoEx,
    nc: Annotated[NextcloudApp, Depends(nc_app)],
    accept_language: Annotated[str | None, Header()] = None
):
    print(f'Accept-Language: {accept_language}')
    return responses.JSONResponse(content={"redirect_handler": "index/slide_show"})

if __name__ == "__main__":
    run_app("main:APP", log_level="trace")
