variable "ecr_bronze_products_repository_name" {
  description = "The name of the ECR repository"
  type        = string
  default     = "bronze_products"
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