# ！ /usr/bin/python3

import logging


def logging_setting(logPath, logLevel, logMsg):
    logFormat = "%(asctime)s %(levelname)s %(message)s "
    dateFormat = "%Y-%m-%d %H:%M:%S %a"
    logging.basicConfig(level=logging.DEBUG, format=logFormat, datefmt=dateFormat, filename=logPath)

    if logLevel == "debug":
        logging.debug(logMsg)
    elif logLevel == "info":
        logging.info(logMsg)
    elif logLevel == "warning":
        logging.warning(logMsg)
    elif logLevel == "error":
        logging.error(logMsg)
    elif logLevel == "critical":
        logging.critical(logMsg)


if __name__ == "__main__":
    log_dir = "../logs/application.log"
    logging_setting(log_dir, "info", "info test")
