def log_error_and_exit(error: BaseException):
    """Lot error and exit.

    Args:
        err (Exception): exception instance.
    """
    logger.error("%s", error)
    # match error:
    #     case HTTPError(_):
    #         _print_errors(error)
    sys.exit(-1)


# def _print_errors(error) -> None:
#     data = error.response.json()
#     for err in data.get("errors") or []:
#         logger.error(red("%(field)s: %(message)s"), err)
