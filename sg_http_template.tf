provider "aws" {
  region  = "${var.aws_region}"
  profile = "${var.aws_profile}"

  version = "~>1.0"
}

# ------ Security Groups ------

resource "aws_security_group" "ORIGIN-WHITELIST-HTTP-SG-2" {
  name        = "ORIGIN-WHITELIST-HTTP-SG-2"
  description = "Origin whitelist HTTP security group"
  vpc_id      = "${var.aws_vpc}"
