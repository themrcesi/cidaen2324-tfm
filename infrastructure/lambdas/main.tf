data "archive_file" "lambda_fn_code" {
  type             = "zip"
  source_file      = "${path.module}/../../src/infra/${var.lambda_fn_script_name}/lambda_function.py"
  output_file_mode = "0666"
  output_path      = "${path.module}/../../lambda_function_${var.lambda_fn_name}.zip"
}

resource "aws_lambda_function" "lambda_fn" {
  depends_on = [data.archive_file.lambda_fn_code]

  function_name = var.lambda_fn_name
  role          = var.tfm_role
  handler       = "lambda_function.lambda_handler"
  runtime       = "python3.10"
  memory_size   = var.memory_size
  timeout       = var.timeout
  architectures = ["arm64"]

  layers = [var.etl_lambda_layer_arn, "arn:aws:lambda:eu-west-3:336392948345:layer:AWSSDKPandas-Python310-Arm64:19"]

  environment {
    variables = {
      LOG_LEVEL = "DEBUG"
    }
  }

  filename         = "${path.module}/../../lambda_function_${var.lambda_fn_name}.zip"
}

resource "null_resource" "cleanup_lambda_zip" {
  depends_on = [ aws_lambda_function.lambda_fn ]
  provisioner "local-exec" {
    command = <<EOT
      rm -f ${path.module}/../../lambda_function_${var.lambda_fn_name}.zip
    EOT
  }
  triggers = {
    always_run = "${timestamp()}"
  }
}