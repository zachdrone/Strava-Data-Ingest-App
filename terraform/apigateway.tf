# API Gateway to trigger the Lambda function
resource "aws_api_gateway_rest_api" "api" {
  name        = "my-api"
  description = "API Gateway for my Lambda functions"
}

# Get Hello
resource "aws_api_gateway_resource" "health" {
  rest_api_id = aws_api_gateway_rest_api.api.id
  parent_id   = aws_api_gateway_rest_api.api.root_resource_id
  path_part   = "health"
}

resource "aws_api_gateway_method" "health_get_method" {
  rest_api_id   = aws_api_gateway_rest_api.api.id
  resource_id   = aws_api_gateway_resource.health.id
  http_method   = "GET"
  authorization = "NONE"
}

resource "aws_api_gateway_integration" "health_lambda_integration" {
  rest_api_id = aws_api_gateway_rest_api.api.id
  resource_id = aws_api_gateway_resource.health.id
  http_method = aws_api_gateway_method.health_get_method.http_method
  integration_http_method = "POST"
  type = "AWS_PROXY"
  uri = "arn:aws:apigateway:${var.aws_region}:lambda:path/2015-03-31/functions/${aws_lambda_function.health_endpoint.arn}/invocations"
}

resource "aws_lambda_permission" "health_allow_api_gateway" {
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
  rest_api_id = aws_api_gateway_rest_api.api.id
  resource_id = aws_api_gateway_resource.callback.id
  http_method = aws_api_gateway_method.callback_get_method.http_method
  integration_http_method = "POST"
  type = "AWS_PROXY"
  uri = "arn:aws:apigateway:${var.aws_region}:lambda:path/2015-03-31/functions/${aws_lambda_function.callback_endpoint.arn}/invocations"
}

resource "aws_lambda_permission" "callback_allow_api_gateway" {
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.callback_endpoint.function_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "arn:aws:execute-api:${var.aws_region}:${data.aws_caller_identity.current.account_id}:*/*/*/*"
}

resource "aws_api_gateway_deployment" "api_deployment" {
  rest_api_id = aws_api_gateway_rest_api.api.id
  stage_name  = "prod"  # This is the stage name (e.g., prod, dev)

  depends_on = [
    aws_api_gateway_integration.health_lambda_integration,
    aws_api_gateway_method.health_get_method,
    aws_api_gateway_integration.callback_lambda_integration,
    aws_api_gateway_method.callback_get_method
  ]
}