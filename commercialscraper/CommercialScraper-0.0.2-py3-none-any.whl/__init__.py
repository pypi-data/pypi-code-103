"""
A dynamic and complete data pipeline designed to safely and effectively extract both structured and unstructured data of products from airbnb.com 
and permanently store the data in various formats solely at the discretion of the user; either locally, on the cloud, or both.

airbnb.com provides no api, and has a 'bot unfriendly' dynamic website, therefore the crawler (built with selenium) is designed to "mimic a human" 
and click through all of the products, whilst collecting relevant data from each product page visited.

Data storage methods are built in and have been made easy as calling methods and inputting the correct credentials. Currently, any pandas dataframe and 
colection of image source links can be stored locally in neatly organised directories, on a postgresql server (provided you have an open connection), and/or
an AWS s3 bucket (provided that the bucket is open to recieving data from your local IP address). For more information on s3 bucket configuration, please visit
https://docs.aws.amazon.com/AmazonS3/latest/userguide/create-bucket-overview.html
"""