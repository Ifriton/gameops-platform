provider "kubernetes" {
  config_path    = pathexpand(var.kubeconfig_path)
  config_context = var.kube_context
}

locals {
  labels = {
    "app.kubernetes.io/name"       = "gameops-platform"
    "app.kubernetes.io/part-of"    = "gameops-platform"
    "app.kubernetes.io/managed-by" = "terraform"
  }
}

resource "kubernetes_namespace_v1" "gameops" {
  metadata {
    name   = var.namespace
    labels = local.labels
  }
}

resource "kubernetes_resource_quota_v1" "gameops" {
  metadata {
    name      = "gameops-quota"
    namespace = kubernetes_namespace_v1.gameops.metadata[0].name
    labels    = local.labels
  }
  spec {
    hard = {
      "pods"            = "10"
      "requests.cpu"    = "2"
      "requests.memory" = "2Gi"
      "limits.cpu"      = "4"
      "limits.memory"   = "4Gi"
    }
  }
}

resource "kubernetes_limit_range_v1" "gameops" {
  metadata {
    name      = "gameops-default-limits"
    namespace = kubernetes_namespace_v1.gameops.metadata[0].name
    labels    = local.labels
  }
  spec {
    limit {
      type = "Container"
      default = {
        cpu    = "500m"
        memory = "256Mi"
      }
      default_request = {
        cpu    = "100m"
        memory = "128Mi"
      }
    }
  }
}

resource "kubernetes_service_account_v1" "gameops_api" {
  metadata {
    name      = "gameops-api"
    namespace = kubernetes_namespace_v1.gameops.metadata[0].name
    labels    = local.labels
  }
  automount_service_account_token = false
}
