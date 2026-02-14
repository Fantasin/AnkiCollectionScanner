import logging, logging.config


def build_logging():

    dict_config = {

        "version": 1 ,
        "disable_existing_loggers": False,
        "formatters":{
            "default":{
                "format": "%(asctime)s | %(levelname)s | %(name)s | %(message)s",
                "datefmt": "%Y-%m-%d %H:%M:%S",
            }},
        "handlers": {
            "console":{
                "class": "logging.StreamHandler",
                "formatter": "default",
                "stream": "ext://sys.stderr",
                "level": "INFO"
            },
            "file":{
                "class":"logging.handlers.RotatingFileHandler",
                "filename": "app.log",
                "encoding": "utf-8",
                "formatter": "default",
                "maxBytes" : 5_000_000,
                "backupCount": 2,
                "level": "DEBUG",
            },
        },
        "root":{
            "level":"DEBUG",
            "handlers":["console", "file"],
        },
        "loggers": {
            "collection_scanner": {
                "level":"INFO",
                "propagate": True,
            },
        },
    }

    logging.config.dictConfig(dict_config)

