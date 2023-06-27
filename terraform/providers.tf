# Providers
# https://developer.hashicorp.com/terraform/language/data-sources

provider "aws" {
  alias  = "primary"
  region = "sa-east-1"
}

# provider "aws" {
#   alias  = "secondary"
#   region = "us-east-1"
# }

