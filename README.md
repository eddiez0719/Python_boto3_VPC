# Python_boto3_VPC

* Aim: This project is to create two EC2 instances from a VPC - One is in public subnet (bastion box or jumping server) and the other is in private subnet(application server). After ssh to bastion box, then application server, you should be fine to run `yum update` to access internete. Also, only ssh from the jumping box to ec2-pri is allowed.

* Language: Python boto3 SDK

* Use: Pull from this repository and run with python 
