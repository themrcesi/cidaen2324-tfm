output "ecr_repository_url" {
  value = aws_ecr_repository.bronze_products.repository_url
}

output "ecs_cluster_arn" {
  value = aws_ecs_cluster.fargate_cluster.arn
}

output "docker_image_uri" {
  value = null_resource.build_push_dkr_img.triggers.image_uri
}

output "ecs_task_definition_arn" {
  value = aws_ecs_task_definition.bronze_products.arn
}

output "bronze_categories_fn_arn" {
  value = aws_lambda_function.bronze_categories.arn
}

output "bronze_products_fn_arn" {
  value = aws_lambda_function.bronze_products.arn
}