#!/bin/bash

printf "Generating a secret key... ";
secret_key=$(python -c "import random,string;print(''.join([random.SystemRandom().choice(\"{}{}{}\".format(string.ascii_letters, string.digits, string.punctuation)) for i in range(63)]))");
printf "done\n";

read -r -p "Enter email address           : " email
read -s -p "Enter email password          : " password

read -p "Enter Cloudinary cloud name      : " cloud_name
read -r -p "Enter Cloudinary API name     : " cloudinary_api
read -r -p "Enter Cloudinary SECRET key   : " cloudinary_secret

read -r -p "Enter MySQL database user     : " db_user
read -s -p "Enter MySQL database password : " db_password

echo "SECRET_KEY=$secret_key" > .env

{
  echo "EMAIL_HOST_USER=$email"
  echo "EMAIL_HOST_PASSWORD=$password"
  echo "CLOUD_NAME=$cloud_name"
  echo "CLOUDINARY_API_KEY=$cloudinary_api"
  echo "CLOUDINARY_SECRET=$cloudinary_secret"
  echo "DB_USER=$db_user"
  echo "DB_PASSWORD=$db_password"
} >> .env
