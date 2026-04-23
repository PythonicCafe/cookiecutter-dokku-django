def report_error(message: str, context: dict, level: str):
    """Report an error to Sentry (if configured) and stderr.

    The `message` should describe the class of error, without object IDs or other specifics, so that Sentry groups all
    errors of the same type. Put object-specific details in `context`.
    """
    import json
    import sys

    from sentry_sdk import Scope, capture_message

    scope = Scope()
    scope.set_context("context", context)
    capture_message(message, level=level, scope=scope)
    print(f"{message}: {json.dumps(context, default=str)}", file=sys.stderr)
