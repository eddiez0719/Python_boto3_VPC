import time
import boto3

ec2 = boto3.resource('ec2')
ec2_client = boto3.client('ec2')

# create a VPC
vpc = ec2.create_vpc(CidrBlock='172.16.0.0/16')
vpc.wait_until_available()
vpc.create_tags(Tags=[{"Key": "Name", "Value": "python_created_vpc"}])
print('VPC created successfully with VPC ID: ' + vpc.id)

# create a public subnet
pub_subnet = ec2.create_subnet(CidrBlock='172.16.61.0/24', VpcId=vpc.id)
print(pub_subnet.id)

# create a private subnet
pri_subnet = ec2.create_subnet(CidrBlock='172.16.161.0/24', VpcId=vpc.id)
print('Private subnet create successfully with subnet id: ' + pri_subnet.id)

# acquire an eip

addr = ec2_client.allocate_address(Domain='vpc')
print('the EIP is ' + addr['PublicIp'])
#print(addr['AllocationId'])

# create then attach igw
ig = ec2.create_internet_gateway()
vpc.attach_internet_gateway(InternetGatewayId=ig.id)
print('Internet Gateway created successfully with gateway id: ' + ig.id)

# create a route table and a public route
route_table = vpc.create_route_table()
route = route_table.create_route(DestinationCidrBlock='0.0.0.0/0',
                                 GatewayId=ig.id)
print(route_table.id)

# create a nat gateway
nat_gw = ec2_client.create_nat_gateway(SubnetId=pub_subnet.id,
                                       AllocationId=addr['AllocationId'])
print('the nat gatway id is: ' + nat_gw['NatGateway']['NatGatewayId'])

#s = True

#while s:
#    if (nat_gw['NatGateway']['State']) != 'available':
#        print(nat_gw['NatGateway']['State'])
#        time.sleep(20)
#    else:
#        print('Nat Gateway is ready')
#        s = False

time.sleep(300)
print(nat_gw['NatGateway']['State'])

# create a route table and a private route
pri_route_table = vpc.create_route_table()
pri_route = pri_route_table.create_route(
    DestinationCidrBlock='0.0.0.0/0',
    NatGatewayId=nat_gw['NatGateway']['NatGatewayId'])
print(pri_route_table.id)

# associate the route table with public subnet
route_table_association = route_table.associate_with_subnet(
    SubnetId=pub_subnet.id,
    # GatewayId='ig.id'
)
#route_table.associate_with_subnet(SubnetId=pub_subnet.id)

# associate the private route table with private subnet
route_table_association = pri_route_table.associate_with_subnet(
    SubnetId=pri_subnet.id,
    # GatewayId='ig.id'
)

#pri_route_table.associate_with_subnet(SubnetId=pri_subnet.id)

# Create a security group
sec_group = ec2.create_security_group(GroupName='jumping_box',
                                      Description='jumping_box_sec_group',
                                      VpcId=vpc.id)
sec_group.authorize_ingress(CidrIp='0.0.0.0/0',
                            IpProtocol='tcp',
                            FromPort=22,
                            ToPort=22)
print(sec_group.id)

# create a key pair
keypair = ec2_client.create_key_pair(KeyName='python-keypair')

# create an instance in public subnet
instance = ec2.create_instances(ImageId='ami-075a72b1992cb0687',
                                InstanceType='t2.micro',
                                MaxCount=1,
                                MinCount=1,
                                KeyName='python-keypair',
                                NetworkInterfaces=[{
                                    'SubnetId':
                                    pub_subnet.id,
                                    'DeviceIndex':
                                    0,
                                    'AssociatePublicIpAddress':
                                    True,
                                    'Groups': [sec_group.group_id]
                                }])

# create an instance in private subnet
instance = ec2.create_instances(ImageId='ami-075a72b1992cb0687',
                                InstanceType='t2.micro',
                                MaxCount=1,
                                MinCount=1,
                                KeyName='python-keypair',
                                NetworkInterfaces=[{
                                    'SubnetId':
                                    pri_subnet.id,
                                    'DeviceIndex':
                                    0,
                                    'AssociatePublicIpAddress':
                                    False,
                                    'Groups': [sec_group.group_id]
                                }])
