import scrapy
from scrapy.crawler import CrawlerProcess
import matplotlib.pyplot as plt
import pandas as pd
import time
import requests
import shutil

# Initial link for breeds
link = ['https://www.akc.org/dog-breeds/']
# Lists to generate group links
groups = ['sporting', 'hound', 'working', 'terrier', 'toy', 'non-sporting', 'herding', 'miscellaneous-class',
          'foundation-stock-service']
# Lists to generate activity level links
activity_level = ['needs-lots-of-activity', 'regular-exercise', 'energetic', 'calm']
# Lists to generate barking level links
barking_level = ['when-necessary', 'infrequent', 'medium', 'frequent', 'likes-to-be-vocal']
# Lists to generate characteristics
characteristics = ['smallest-dog-breeds', 'medium-dog-breeds', 'largest-dog-breeds', 'smartest-dogs',
                   'hypoallergenic-dogs', 'best-family-dogs', 'best-guard-dogs', 'best-dogs-for-kids',
                   'best-dogs-for-apartments-dwellers', 'hairless-dog-breeds']
# Lists to generate coat type links
coat_type = ['hairless', 'short', 'medium', 'long', 'smooth', 'wire']
# Lists to generate shedding links
shedding = ['infrequent', 'seasonal', 'frequent', 'occasional', 'regularly']
# List to generate size links
size = ['xsmall', 'small', 'medium', 'large', 'xlarge']
# List to generate trainability links
trainability= ['may-be-stubborn', 'agreeable', 'eager-to-please', 'independent', 'easy-training']

fil_const = ['https://www.akc.org/dog-breeds/', 'page/', '/', '%5B%5D='] # URL constructor
filters = ['?group', '?activity_level', '?barking_level', '?characteristic', '?coat_type', '?shedding', '?size',
           '?trainability']
sub_filters = [groups, activity_level, barking_level, characteristics, coat_type, shedding, size, trainability]

df = pd.DataFrame(columns=['BREEDS', 'FIRST_PARAGRAPH', 'IMG_URL', 'GROUP', 'ACTIVITY_LEVEL', 'BARKING_LEVEL',
                           'CHARACTERISTIC', 'COAT_TYPE', 'SHEDDING', 'SIZE', 'TRAINABILITY'])


class DogBreedSpider(scrapy.Spider):
    name = "Dog_Breed_Spider"

    def start_requests(self):
        global link, filters, fil_const, sub_filters

        urls = [link[0]+'page/'+str(i)+'/' for i in range(2, 23)]
        link.extend(urls)
        for url in link:
            # Send the url to get the data for all the dog breeds
            yield scrapy.Request(url=url, callback=self.dog_breed)
            time.sleep(2)

        filter_urls = []
        for f in filters:
            # To send the urls with the different filters in the web
            checker = 1
            for sub_f in sub_filters:
                for sub_sub_f in sub_f:
                    if checker == 1:  # To know if the URL is the first page and avoid the 301 redirection of /page/1 url
                        new_url = fil_const[0] + f + fil_const[3] + sub_sub_f
                        filter_urls.append(new_url)
                        yield scrapy.Request(url=new_url, callback=self.filter_data, meta={'filter_col': f,
                                                                                           'sub_filter': sub_sub_f})
                        checker += 1
                    else:  # If we're not in the first filter page, generate the url for /page/#number
                        page_number = 1
                        status = 0
                        while status != 404:
                            # This loop executes until the script return a 404 status code for the page
                            new_url = fil_const[0] + fil_const[1] + str(page_number) + fil_const[2] + f + fil_const[3] \
                                      + sub_sub_f
                            filter_urls.append(new_url)
                            yield scrapy.Request(url=new_url, callback=self.filter_data, meta={'filter_col': f,
                                                                                               'sub_filter': sub_sub_f})
                            status = requests.get(new_url).status_code
                            page_number += 1

    def dog_breed(self, response):
        """
        In this function we scrape all the dog breed names, short description and the image url
        """
        global df
        breed = response.css('h3.breed-type-card__title::text').extract()
        first_paragraph = response.css('p.f-16::text').extract()
        img_url = response.css('img.wp-post-image').xpath('@df-src').getall()
        img_url = img_url[1:]
        df = pd.concat([df, pd.DataFrame({'BREEDS': breed,
                                          'FIRST_PARAGRAPH': first_paragraph,
                                          'IMG_URL': img_url})],
                       ignore_index=True)

    def filter_data(self, response):
        """
        Here we scrap the dog breeds for each filter and add this data in the breed row
        """
        global df
        breeds = response.css('h3.breed-type-card__title::text').extract()
        filter_col = response.meta['filter_col'][1:].upper()
        sub_filter_arr = response.meta['sub_filter'].split('-')
        sub_filter_data = " ".join(sub_filter_arr)
        sub_filter_data = sub_filter_data.capitalize()
        for breed in breeds:  # Find the breed to add the information in that row
            idx = df.index[df['BREEDS'] == breed].tolist()[0]
            df[filter_col][idx] = sub_filter_data


process = CrawlerProcess()
process.crawl(DogBreedSpider)
process.start()
# Saving all the data in the excel file
df.to_excel('output_v2.xlsx')

# Image Downloader
img_urls = df['IMG_URL'].tolist()
for image_url in img_urls:
    filename = image_url.split("/")[-1]

    # Open the url image, set stream to True, this will return the stream content.
    r = requests.get(image_url, stream=True)

    # Check if the image was retrieved successfully
    if r.status_code == 200:
        # Set decode_content value to True, otherwise the downloaded image file's size will be zero.
        r.raw.decode_content = True

        # Open a local file with wb ( write binary ) permission.
        with open(filename, 'wb') as f:
            shutil.copyfileobj(r.raw, f)

        print('Image sucessfully Downloaded: ', filename)
    else:
        print('Image Couldn\'t be retreived')

# Amount visualization for each filter
colors = ['#cc00ff', '#66ff66', '#ffcc66', '#3366ff', '#33cccc', '#33cccc', '#9933ff', '#996600']
df_for_visualization = pd.DataFrame()
sub_filter_idx = 0
for f in filters:
    amount_col_name = 'AMOUNT OF ' + f[1:].capitalize()
    col_name = f[1:].upper() + 'S'
    amounts = []
    types = []
    for sub_f in sub_filters[sub_filter_idx]:
        sub_filter_arr = sub_f.split('-')
        sub_filter_data = " ".join(sub_filter_arr)
        sub_filter_data = sub_filter_data.capitalize()
        amount_data = len(df[df[f[1:].upper()] == sub_filter_data][f[1:].upper()].tolist())
        types.append(sub_filter_data)
        amounts.append(amount_data)
    plt.bar(types, amounts, color= colors[sub_filter_idx])
    plt.xticks(rotation=25)
    chart_title = "BREEDS AMOUNT FOR EACH " + f[1:].upper() + " SUBCLASS"
    plt.title(chart_title)
    plt.savefig(chart_title + ".png")
    sub_filter_idx += 1
    plt.show()
