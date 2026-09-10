variable "namespace" {
  description = "Kubernetes namespace for GameOps platform resources."
  type        = string
  default     = "gameops"
}

variable "kubeconfig_path" {
  description = "Path to the kubeconfig used by the Kubernetes provider."
  type        = string
  default     = "~/.kube/config"
}

variable "kube_context" {
  description = "Kubernetes context to target."
  type        = string
  default     = "kind-gameops"
}
