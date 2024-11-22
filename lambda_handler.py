# lambda_handler.py

import os

def lambda_handler(event, context):
    # Get the handler function name from environment variable
    handler = os.getenv('handler', 'default.handler')  # fallback to 'default.handler'
    print(" in lambda_handler.lambda_handler")
    # Dynamically import the handler module and get the function
    try:
        module_name, function_name = handler.rsplit('.', 1)
        module = __import__(module_name, fromlist=[function_name])
        handler_function = getattr(module, function_name)
    except Exception as e:
        return {
            "statusCode": 500,
            "body": f"Error loading handler {handler}: {str(e)}"
        }

    # Call the dynamically loaded function and return the result
    return handler_function(event, context)
