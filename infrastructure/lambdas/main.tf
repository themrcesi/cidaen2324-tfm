locals {
  etl_lambda_layer = "arn:aws:lambda:eu-west-3:480361390441:layer:cidaen2324-tfm-etl-layer-dev:20"
}

resource "null_resource" "create_lambda_zip" {
  provisioner "local-exec" {
    command = <<EOT
      cd ../src/infra
      echo $PWD
      zip -r9 ../../lambda_function_${var.lambda_fn_name}.zip ${var.lambda_fn_script_name}.py
    EOT
  }
  # Add a trigger to force the creation of the ZIP file if the source file changes
  triggers = {
    #file_hash = filemd5("../src/infra/${var.lambda_fn_script_name}.py")
    always_run = "${timestamp()}"
  }
}

resource "aws_lambda_function" "lambda_fn" {
  depends_on = [null_resource.create_lambda_zip]

  function_name = var.lambda_fn_name
  role          = var.tfm_role
  handler       = "${var.lambda_fn_script_name}.lambda_handler"
  runtime       = "python3.10"
  memory_size   = var.memory_size
  timeout       = var.timeout
  architectures = ["arm64"]

  layers = [local.etl_lambda_layer]

  environment {
    variables = {
      LOG_LEVEL = "DEBUG"
    }
  }

  filename         = "${path.module}/../../lambda_function_${var.lambda_fn_name}.zip"
  # source_code_hash = filebase64sha256("${path.module}/../lambda_function.zip")
}

resource "null_resource" "cleanup_lambda_zip" {
  depends_on = [ aws_lambda_function.lambda_fn ]
  provisioner "local-exec" {
    command = <<EOT
      echo $PWD
      rm -f ${path.module}/../../lambda_function_${var.lambda_fn_name}.zip
    EOT
    # command = "rm -f ${path.module}/../../lambda_function_${var.lambda_fn_name}.zip"
  }
  # triggers = {
  #   always_run = "${timestamp()}"
  # }
  triggers = {
    file_hash = filemd5("../src/infra/${var.lambda_fn_script_name}.py")
  }
}