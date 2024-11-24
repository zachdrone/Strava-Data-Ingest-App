resource "aws_lambda_function" "health_endpoint" {
  function_name = "health_endpoint"
  package_type  = "Image"
  image_uri     = "${aws_ecr_repository.my_lambda_repo.repository_url}:latest"
  role          = aws_iam_role.lambda_execution_role.arn

  environment {
    variables = {
      handler = "lambdas.health.handler.lambda_handler"
    }
  }

  memory_size = 512
  timeout     = 30
}

resource "aws_lambda_function" "callback_endpoint" {
  function_name = "callback_endpoint"
  package_type  = "Image"
  image_uri     = "${aws_ecr_repository.my_lambda_repo.repository_url}:latest"
  role          = aws_iam_role.lambda_execution_role.arn

  environment {
    variables = {
      handler = "lambdas.callback.handler.lambda_handler"
    }
  }

  memory_size = 512
  timeout     = 30
}


# resource "aws_lambda_function" "authorizer" {
#   function_name = "authorizer"
#   package_type  = "Image"
#   image_uri     = "${aws_ecr_repository.my_lambda_repo.repository_url}:latest"
#   role          = aws_iam_role.lambda_execution_role.arn

#   environment {
#     variables = {
#       handler = "lambdas.authorizer.handler.lambda_handler"
#     }
#   }

#   memory_size = 512
#   timeout     = 30
# }