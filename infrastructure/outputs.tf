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
############################ LAMBDAS ############################
output "raw_categories_function_arn" {
  value = module.raw_categories.lambda_fn_arn
}

output "raw_product_categories_function_arn" {
  value = module.raw_product_categories.lambda_fn_arn
}

output "bronze_categories_function_arn" {
  value = module.bronze_categories.lambda_fn_arn
}

output "silver_products_function_arn" {
  value = module.silver_products.lambda_fn_arn
}

output "gold_categories_function_arn" {
  value = module.gold_categories.lambda_fn_arn
}

output "gold_locations_function_arn" {
  value = module.gold_locations.lambda_fn_arn
}

output "gold_products_function_arn" {
  value = module.gold_products.lambda_fn_arn
}