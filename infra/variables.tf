variable "region" {
  type    = string
  default = "us-east-1"
}

variable "instance_type" {
  description = "GPU instance. g6.xlarge = 1x L4 24GB, ~$0.80/hr on-demand in us-east-1."
  type        = string
  default     = "g6.xlarge"
}

variable "root_volume_gb" {
  description = "Must be at least the DLAMI snapshot size."
  type        = number
  default     = 100
}

variable "checkpoint" {
  description = "Hugging Face repo of the decider adapter; the Qwen3.5-2B base is pulled automatically."
  type        = string
  default     = "StrandsAgents/strands-decider-2B-hobson-v19"
}

variable "packages" {
  description = "What uv installs on the box. PyPI strands-decider 0.1.0 has no [cuda] extra, so the GPU kernels are listed explicitly."
  type        = list(string)
  default     = [
    # PyPI 0.1.0 crashes on over-window prompts and lacks --strict-window; pin the GitHub commit instead.
    "strands-decider @ git+https://github.com/strands-labs/strands-decider@75c9fd32e664954cdc18481434018aa507eee8fb",
    "flash-linear-attention",
  ]
}

variable "port" {
  type    = number
  default = 8099
}

variable "auto_stop_minutes" {
  description = "Instance stops itself this many minutes after every boot. 0 disables."
  type        = number
  default     = 20
}
