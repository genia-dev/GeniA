from os.path import abspath, dirname, join

from dynaconf import Dynaconf

settings = Dynaconf(
    envvar_prefix=False,
    settings_files=[
        join(dirname(abspath(__file__)), f)
        for f in [
            "settings/prompts.toml",
            "settings/settings.toml",
        ]
    ],
)
