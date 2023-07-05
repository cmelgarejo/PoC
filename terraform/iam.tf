resource "aws_iam_role" "aws_glue_role" {
  assume_role_policy = "{\"Version\":\"2012-10-17\",\"Statement\":[{\"Effect\":\"Allow\",\"Principal\":{\"Service\":\"glue.amazonaws.com\"},\"Action\":\"sts:AssumeRole\"}]}"
  description        = "Allows Glue to call AWS services on your behalf. "
  inline_policy {
  }

  managed_policy_arns  = ["arn:aws:iam::aws:policy/AmazonRDSDataFullAccess", "arn:aws:iam::aws:policy/AmazonS3FullAccess"]
  max_session_duration = 3600
  name                 = "aws-glue-role"
  path                 = aws_iam_group.terraform_group.path
}

resource "aws_iam_role_policy_attachment" "aws_glue_role_arn_aws_iam__aws_policy_amazonrdsdatafullaccess" {
  policy_arn = "arn:aws:iam::aws:policy/AmazonRDSDataFullAccess"
  role       = aws_iam_role.aws_glue_role.name
}

resource "aws_iam_role_policy_attachment" "aws_glue_role_arn_aws_iam__aws_policy_amazons3fullaccess" {
  policy_arn = "arn:aws:iam::aws:policy/AmazonS3FullAccess"
  role       = aws_iam_role.aws_glue_role.id
}

resource "aws_iam_group" "terraform_group" {
  name = "terraform-group"
  path = "/"
}

resource "aws_iam_group_policy_attachment" "terraform_group_arn_aws_iam__aws_policy_amazonec2fullaccess" {
  group      = aws_iam_group.terraform_group.name
  policy_arn = "arn:aws:iam::aws:policy/AmazonEC2FullAccess"
}

resource "aws_iam_group_policy_attachment" "terraform_group_arn_aws_iam__aws_policy_amazonkeyspacesfullaccess" {
  group      = aws_iam_group.terraform_group.id
  policy_arn = "arn:aws:iam::aws:policy/AmazonKeyspacesFullAccess"
}

resource "aws_iam_group_policy_attachment" "terraform_group_arn_aws_iam__aws_policy_amazonrdsfullaccess" {
  group      = aws_iam_group.terraform_group.name
  policy_arn = "arn:aws:iam::aws:policy/AmazonRDSFullAccess"
}

resource "aws_iam_group_policy_attachment" "terraform_group_arn_aws_iam__aws_policy_amazons3fullaccess" {
  group      = aws_iam_group.terraform_group.id
  policy_arn = "arn:aws:iam::aws:policy/AmazonS3FullAccess"
}

resource "aws_iam_group_policy_attachment" "terraform_group_arn_aws_iam__aws_policy_amazonvpcfullaccess" {
  group      = aws_iam_group.terraform_group.id
  policy_arn = "arn:aws:iam::aws:policy/AmazonVPCFullAccess"
}

resource "aws_iam_group_policy_attachment" "terraform_group_arn_aws_iam__aws_policy_awskeymanagementservicepoweruser" {
  group      = aws_iam_group.terraform_group.id
  policy_arn = "arn:aws:iam::aws:policy/AWSKeyManagementServicePowerUser"
}

resource "aws_iam_group_policy_attachment" "terraform_group_arn_aws_iam__aws_policy_resourcegroupsandtageditorfullaccess" {
  group      = aws_iam_group.terraform_group.id
  policy_arn = "arn:aws:iam::aws:policy/ResourceGroupsandTagEditorFullAccess"
}

resource "aws_iam_role" "rds_monitoring_role" {
  assume_role_policy = "{\"Version\":\"2012-10-17\",\"Statement\":[{\"Sid\":\"\",\"Effect\":\"Allow\",\"Principal\":{\"Service\":\"monitoring.rds.amazonaws.com\"},\"Action\":\"sts:AssumeRole\"}]}"
  inline_policy {
  }

  managed_policy_arns  = ["arn:aws:iam::aws:policy/service-role/AmazonRDSEnhancedMonitoringRole"]
  max_session_duration = 3600
  name                 = "rds-monitoring-role"
  path                 = aws_iam_group.terraform_group.path
}
