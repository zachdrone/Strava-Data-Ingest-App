# API Gateway to trigger the Lambda function
resource "aws_api_gateway_rest_api" "api" {
  name        = "my-api"
  description = "API Gateway for my Lambda functions"
}

resource "aws_api_gateway_deployment" "api_deployment" {
  rest_api_id = aws_api_gateway_rest_api.api.id
  stage_name  = "prod" # This is the stage name (e.g., prod, dev)

  depends_on = [
    aws_api_gateway_method.get_health,
    aws_api_gateway_method.post_health,
    aws_api_gateway_method.callback_get_method,
    aws_api_gateway_method.get_webhook,
    aws_api_gateway_method.post_webhook,
    aws_api_gateway_integration.get_health_integration,
    aws_api_gateway_integration.post_health_integration,
    aws_api_gateway_integration.callback_lambda_integration,
    aws_api_gateway_integration.get_webhook_integration,
    aws_api_gateway_integration.post_webhook_integration
  ]
}

# # Authorizer
# resource "aws_api_gateway_authorizer" "strava_authorizer" {
#   name             = "StravaSignatureAuthorizer"
#   rest_api_id      = aws_api_gateway_rest_api.api.id
#   authorizer_uri   = aws_lambda_function.authorizer.invoke_arn
#   authorizer_credentials = aws_iam_role.invocation_role.arn
# }

# # Modify the API Gateway method to use the authorizer
# resource "aws_api_gateway_method" "get_method" {
#   rest_api_id   = aws_api_gateway_rest_api.api.id
#   resource_id   = aws_api_gateway_resource.root.id
#   http_method   = "POST" # Or "GET" if applicable
#   authorization = "CUSTOM"
#   authorizer_id = aws_api_gateway_authorizer.strava_authorizer.id
# }


# Health
resource "aws_api_gateway_resource" "health" {
  rest_api_id = aws_api_gateway_rest_api.api.id
  parent_id   = aws_api_gateway_rest_api.api.root_resource_id
  path_part   = "health"
}

resource "aws_api_gateway_method" "get_health" {
  rest_api_id   = aws_api_gateway_rest_api.api.id
  resource_id   = aws_api_gateway_resource.health.id
  http_method   = "GET"
  authorization = "NONE"
}

resource "aws_api_gateway_method" "post_health" {
  rest_api_id   = aws_api_gateway_rest_api.api.id
  resource_id   = aws_api_gateway_resource.health.id
  http_method   = "POST"
  authorization = "NONE"
}

resource "aws_api_gateway_integration" "get_health_integration" {
  rest_api_id             = aws_api_gateway_rest_api.api.id
  resource_id             = aws_api_gateway_resource.health.id
  http_method             = aws_api_gateway_method.get_health.http_method
  integration_http_method = "POST"
  type                    = "AWS_PROXY"
  uri                     = "arn:aws:apigateway:${var.aws_region}:lambda:path/2015-03-31/functions/${aws_lambda_function.health_endpoint.arn}/invocations"
}

resource "aws_api_gateway_integration" "post_health_integration" {
  rest_api_id             = aws_api_gateway_rest_api.api.id
  resource_id             = aws_api_gateway_resource.health.id
  http_method             = aws_api_gateway_method.post_health.http_method
  integration_http_method = "POST"
  type                    = "AWS_PROXY"
  uri                     = "arn:aws:apigateway:${var.aws_region}:lambda:path/2015-03-31/functions/${aws_lambda_function.health_endpoint.arn}/invocations"
}

resource "aws_lambda_permission" "health_allow_apigateway" {
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.health_endpoint.function_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "arn:aws:execute-api:${var.aws_region}:${data.aws_caller_identity.current.account_id}:*/*/*/*"
}

# Callback
resource "aws_api_gateway_method" "callback_get_method" {
  rest_api_id   = aws_api_gateway_rest_api.api.id
  resource_id   = aws_api_gateway_resource.callback.id
  http_method   = "GET"
  authorization = "NONE"
}

resource "aws_api_gateway_resource" "callback" {
  rest_api_id = aws_api_gateway_rest_api.api.id
  parent_id   = aws_api_gateway_rest_api.api.root_resource_id
  path_part   = "callback"
}

resource "aws_api_gateway_integration" "callback_lambda_integration" {
  rest_api_id             = aws_api_gateway_rest_api.api.id
  resource_id             = aws_api_gateway_resource.callback.id
  http_method             = aws_api_gateway_method.callback_get_method.http_method
  integration_http_method = "POST"
  type                    = "AWS_PROXY"
  uri                     = "arn:aws:apigateway:${var.aws_region}:lambda:path/2015-03-31/functions/${aws_lambda_function.callback_endpoint.arn}/invocations"
}

resource "aws_lambda_permission" "callback_allow_api_gateway" {
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.callback_endpoint.function_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "arn:aws:execute-api:${var.aws_region}:${data.aws_caller_identity.current.account_id}:*/*/*/*"
}

# Webhook
resource "aws_api_gateway_resource" "webhook" {
  rest_api_id = aws_api_gateway_rest_api.api.id
  parent_id   = aws_api_gateway_rest_api.api.root_resource_id
  path_part   = "webhook"
}

resource "aws_api_gateway_method" "get_webhook" {
  rest_api_id   = aws_api_gateway_rest_api.api.id
  resource_id   = aws_api_gateway_resource.webhook.id
  http_method   = "GET"
  authorization = "NONE"
}

resource "aws_api_gateway_method" "post_webhook" {
  rest_api_id   = aws_api_gateway_rest_api.api.id
  resource_id   = aws_api_gateway_resource.webhook.id
  http_method   = "POST"
  authorization = "NONE"
}

resource "aws_api_gateway_integration" "get_webhook_integration" {
  rest_api_id             = aws_api_gateway_rest_api.api.id
  resource_id             = aws_api_gateway_resource.webhook.id
  http_method             = aws_api_gateway_method.get_webhook.http_method
  integration_http_method = "POST"
  type                    = "AWS_PROXY"
  uri                     = "arn:aws:apigateway:${var.aws_region}:lambda:path/2015-03-31/functions/${aws_lambda_function.webhook_endpoint.arn}/invocations"
}

resource "aws_api_gateway_integration" "post_webhook_integration" {
  rest_api_id             = aws_api_gateway_rest_api.api.id
  resource_id             = aws_api_gateway_resource.webhook.id
  http_method             = aws_api_gateway_method.post_webhook.http_method
  integration_http_method = "POST"
  type                    = "AWS_PROXY"
  uri                     = "arn:aws:apigateway:${var.aws_region}:lambda:path/2015-03-31/functions/${aws_lambda_function.webhook_endpoint.arn}/invocations"
}

resource "aws_lambda_permission" "webhook_allow_get" {
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.webhook_endpoint.function_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "arn:aws:execute-api:${var.aws_region}:${data.aws_caller_identity.current.account_id}:${aws_api_gateway_rest_api.api.id}/*/GET/webhook"
}

resource "aws_lambda_permission" "webhook_allow_post" {
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.webhook_endpoint.function_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "arn:aws:execute-api:${var.aws_region}:${data.aws_caller_identity.current.account_id}:${aws_api_gateway_rest_api.api.id}/*/POST/webhook"
}