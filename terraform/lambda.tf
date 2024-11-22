resource "aws_lambda_function" "my_lambda" {
  function_name = "my_lambda_function"
  package_type  = "Image"
  image_uri     = "${aws_ecr_repository.my_lambda_repo.repository_url}:latest"
  role          = aws_iam_role.lambda_execution_role.arn

  environment {
    variables = {
      handler = "lambdas.my_lambda_2.handler.lambda_handler"
    }
  }

  memory_size = 512  # Memory allocation
  timeout     = 30   # Set timeout to 30 seconds (default is 3 seconds)
}