provider "aws" {
  region = "us-east-1"
}

terraform {
  backend "s3" {
    bucket = "cgs-terraform"
    key    = "p12-python-api.tfstate"
    region = "us-east-1"
  }
}
