variable "lambda_fn_script_name" {
    type    = string
    description = "The name of the script of the lambda function"
}

variable "etl_lambda_layer_arn" {
    type    = string
    description = "The arn of the layer of the lambda function"
}

variable "lambda_fn_name" {
    type    = string
    description = "The name of the lambda function"
}

variable "memory_size" {
    type    = number
    description = "The memory size of the lambda function"
}

variable "timeout" {
    type    = number
    description = "The timeout of the lambda function"
}

variable "tfm_role" {
    type    = string
    description = "The arn of the role of the lambda function"
}