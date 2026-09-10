output "namespace" {
  description = "Namespace created for the GameOps application."
  value       = kubernetes_namespace_v1.gameops.metadata[0].name
}

output "service_account" {
  description = "Restricted service account used by the API deployment."
  value       = kubernetes_service_account_v1.gameops_api.metadata[0].name
}
