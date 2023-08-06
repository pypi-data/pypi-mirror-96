import traceback

from NewLifeUtils.FileModule import DataStorage
from NewLifeUtils.LoggerModule import err, log, wrn
from NewLifeUtils.StringUtilModule import screate

default_lang = {
    "type": "Type",
    "unknown": "Unknown Error",
    "about": "More information",
    "attention": "Attention",
    "info": "Info",
    "warning": "Warn",
    "error": "Error",
    "fatal": "Fatal error",
    "wrong": "Something wrong...",
}
translation = DataStorage("lang.yml", "exceptsettings", default_lang)


def except_print(exception, exception_type="err", tb=True):
    error_text = "\n-------------- {ExceptionTitle} --------------------\n"
    error_text += f"{translation['type']}: {type(exception).__name__}\n\n"

    if exception.args == 0:
        error_text += f"{translation['unknown']}\n"
    else:
        error_text += (
            f'{translation["about"]}:\n\t{(chr(10) + chr(9)).join(exception.args)}\t\n'
        )

    if tb:
        error_text += f"\n{traceback.format_exc()}"

    error_text += "\n-------------- {ExceptionTitle} --------------------\n"

    if exception_type == "attention":
        print()
        log(
            error_text.replace(
                "{ExceptionTitle}",
                screate(translation["attention"], 20),
            )
        )
    elif exception_type == "wrn":
        print()
        wrn(
            error_text.replace(
                "{ExceptionTitle}",
                screate(translation["warning"], 20),
            )
        )
    elif exception_type == "err":
        print()
        err(
            error_text.replace(
                "{ExceptionTitle}",
                screate(translation["error"], 20),
            )
        )
    elif exception_type == "fatal":
        print()
        err(
            error_text.replace(
                "{ExceptionTitle}",
                screate(translation["fatal"], 20),
            )
        )
        exit(-1)
    else:
        print()
        err(
            error_text.replace(
                "{ExceptionTitle}",
                screate(translation["wrong"], 20),
            )
        )


def get_etypes(self):
    return ["attention", "wrn", "err", "fatal"]
