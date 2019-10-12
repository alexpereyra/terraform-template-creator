provider "aws" {
  region  = "${var.aws_region}"
  profile = "${var.aws_profile}"

  version = "~>1.0"
}

# ------ Security Groups ------

resource "aws_security_group" "ORIGIN-WHITELIST-HTTPS-SG-1" {
  name        = "ORIGIN-WHITELIST-HTTPS-SG-1"
  description = "Origin whitelist HTTPS security group"
  vpc_id      = "${var.aws_vpc}"
