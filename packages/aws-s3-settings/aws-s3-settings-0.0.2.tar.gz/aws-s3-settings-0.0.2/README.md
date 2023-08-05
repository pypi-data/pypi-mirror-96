# aws-s3-settings

The purpose of this project is very simple. Allow EC2 instances in an Auto Scaling Group named after Netflix standards to retrieve and expose environment variables from an S3 bucket.

The EC2 instances should use an IAM Role to allow reading those specific files only.

This will give your applicaton developers easy-to-use environment variables just like on Heroku or similar.

### How to install
```
pip install aws-s3-settings

cat << EOF
#!/bin/sh
aws-s3-settings
EOF > /etc/init.d/aws-s3-settings.sh

chmod 755 /etc/init.d/aws-s3-settings.sh
update-rc.d aws-s3-settings.sh defaults

echo "#!/bin/sh
. /tmp/envvars" > /etc/profile.d/ec2_user_data.sh
chmod +x /etc/profile.d/ec2_user_data.sh
```
