# # API Gateway to trigger the Lambda function
# resource "aws_api_gateway_rest_api" "api" {
#   name        = "my-api"
#   description = "API Gateway for my Lambda functions"
# }

# resource "aws_api_gateway_resource" "root" {
#   rest_api_id = aws_api_gateway_rest_api.api.id
#   parent_id   = aws_api_gateway_rest_api.api.root_resource_id
#   path_part   = "hello"
# }

# resource "aws_api_gateway_method" "get_method" {
#   rest_api_id   = aws_api_gateway_rest_api.api.id
#   resource_id   = aws_api_gateway_resource.root.id
#   http_method   = "GET"
#   authorization = "NONE"
# }

# resource "aws_api_gateway_integration" "lambda_integration" {
#   rest_api_id = aws_api_gateway_rest_api.api.id
#   resource_id = aws_api_gateway_resource.root.id
#   http_method = aws_api_gateway_method.get_method.http_method
#   integration_http_method = "POST"
#   type = "AWS_PROXY"
#   uri = "arn:aws:apigateway:${var.aws_region}:lambda:path/2015-03-31/functions/${aws_lambda_function.my_lambda.arn}/invocations"
# }

# resource "aws_lambda_permission" "allow_api_gateway" {
#   action        = "lambda:InvokeFunction"
#   function_name = aws_lambda_function.my_lambda.function_name
#   principal     = "apigateway.amazonaws.com"
# }

# resource "aws_api_gateway_deployment" "api_deployment" {
#   rest_api_id = aws_api_gateway_rest_api.api.id
#   stage_name  = "prod"  # This is the stage name (e.g., prod, dev)

#   depends_on = [
#     aws_api_gateway_integration.lambda_integration,
#     aws_api_gateway_method.get_method
#   ]
# }