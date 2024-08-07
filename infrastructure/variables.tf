variable "utils_s3_bucket" {
  default = "cgarcia.cidaen.tfm.utils-code"
}

variable "utils_s3_bucket_layer_key" {
  default = "etl_layer.zip"
}

variable "utils_s3_bucket_layer_runtime" {
  default = "python3.10"
}

variable "ecr_bronze_products_repository_name" {
  description = "The name of the ECR repository"
  type        = string
  default     = "bronze_products"
}

variable "ecr_tfm-etl-pipeline_repository_name" {
  description = "The name of the ECR repository"
  type        = string
  default     = "tfm-etl-pipeline"
}

variable "ecs_pipeline_cluster_name" {
  description = "The name of the ECS Fargate cluster"
  type        = string
  default     = "cidaen-tfm-etl"  # Default value for the cluster name
}

variable "force_image_rebuild" {
  type    = bool
  default = false
}

variable "ecs_bronze_products_task_family_name" {
  description = "The family name of the ECS task definition"
  type        = string
  default     = "bronze_products"
}

variable "ecs_tfm-etl-pipeline_task_family_name" {
  description = "The family name of the ECS task definition"
  type        = string
  default     = "tfm-etl-pipeline"
}