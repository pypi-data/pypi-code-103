import pipeline
import data_processing
from getpass import getpass

### User inputs

print('________________________Airbnb Webscraper___________________________', end = '\n\n')

# User input for speed
speed_decision = input('Welcome. Do you have an internet speed of less than 2.5Mb/s and wish to enable slow mode?\n\
Warning: It is recommended that you only run a sample of the scraper in slow mode, as the full session could take >12 hours.\n\
[y/n]: ')

speed_flag = True if speed_decision.lower() == 'y' or speed_decision.lower() == 'yes' else False

if speed_flag:
    print('Scraping at slow speed', end = '\n\n')
else:
    print('Scraping at normal speed', end='\n\n')


# User input for sample
sample_decision = input('Do you wish to run the full scraper, and scrape all products from arbnb? Selecting \'n\' will lock the scraper to a sample\n\
[y/n]: ')

sample_flag = False if sample_decision.lower() == 'y' or sample_decision.lower() == 'yes' else True

if sample_flag:
    print('Scraping a sample', end = '\n\n')
else:
    print('Scraping all data. Please ensure your PC has its power saving settings OFF before proceeding, and it is recommended to leave your laptop plugged in if the battery is poor.', end='\n\n')



bucket_name = input('Please enter the bucket name: ')
access_key = input('Please enter your s3 buckets access key: ')
secret_key = getpass('Please input the secret access key of your bucket: ')
region_name = input('Please enter region name: ')

img_name = input('Please enter the IMAGE directory inside the s3 bucket you wish to assign: ')
df_name = input('Please enter the DATASET directory inside the s3 bucket you wish to assign: ')


### Executing Scraper
scraper = pipeline.AirbnbScraper(slow_internet_speed=speed_flag, config='headless', messages = True)
df, images = scraper.scrape_all(sample = sample_flag)


### Executing Saver
# Save df to s3
try:
    data_processing.df_to_s3(df,access_key, region_name, secret_key, bucket_name, df_name)
except Exception as e:
    print(e)
# Save images to s3
try:
    data_processing.images_to_s3(images, access_key, region_name, secret_key, bucket_name, img_name)
except Exception as e:
    print(e)


