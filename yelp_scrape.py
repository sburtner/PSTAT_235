#Scrape data using the yelp api

# pip install yelp api
from yelpapi import YelpAPI
import pandas as pd
import os 
import pickle

def Yelp_ScrapeISP (api_key,city_names,business_data = 'businesses.csv',
                    business_reviews = 'businesses_reviews.csv'):

	"""
	====================================================================
	Version: 1.0.0
	Date: Tue 24 Nov 2020

	Purposes: Search and save yelp data about internet service providers
	within a region. 

	Input:
		Required:
			api_key = Api key assigned by yelp fusion
			city_names = List of locations for internet service providers
		Opitional:
			business_data = .csv file containing data from previous searches
			business_reviews = .csv file containing reviews of businesses from
								previous searches

	Output:
		'businesses.csv' containing information about internet 
			service providers

		'businesses_reviews.csv' containing reviews of internet service
			providers in the businesses.csv file

		'cities_list.txt' list of previous cities that have been searched.
			Data will only be extracted for cities that have not been
			previously searched.

	
	Example: 
	cities = ['Santa Barbara, CA','Los Angeles, CA','New York, NY']
	api_key = XIXIXIXLXJO

	Yelp_ScrapeISP(api_key,cities)


	Author: Jordan Garrett
	jordangarrett@ucsb.edu
	====================================================================
	"""
		
    data_dir =  os.path.join(os.getcwd(),'Yelp_Data\\')

    #check to see if any cities in the list have previously been searched
    if os.path.exists(data_dir+'cities_list.txt'):
    	prev_cities = pickle.load(open(data_dir+'cities_list.txt','rb'))
    	city_names = [city for city in prev_cities if city not in city_names]


    if city_names:
    	print(f'Searching Cities: {cities}')
    else:
    	print('All cities have already been searched')
    	return


    yelp_api = YelpAPI(api_key)
    
    all_business_df = pd.DataFrame()
    all_reviews_df = pd.DataFrame()

    for iCity in cities:
        
        # we can play around with the limit and offset parameters 
        # to control the number of results and what item to start the pull on
        search_results = yelp_api.search_query(term = 'Internet Service Provides',
                                               location = iCity, limit = 50)

        business_df = pd.DataFrame.from_dict(search_results['businesses'])


        # drop the phone, display_phone, transactions, is_closed, and image_url columns
        # we shouldn't need them
        unecessary_cols = ['phone', 'display_phone', 'transactions', 'is_closed','image_url']


        business_df2 = business_df.drop(unecessary_cols,1)

        #loop through businesses
        reviews = dict()

        reviews_df = pd.DataFrame()
        for iBiz, biz_id in enumerate(business_df2.loc[:,'id']):
            business_name = business_df2['name'][iBiz]

            #can only get 3 reviews through yelp api
            #BUT...we have the url...which means it should be easy to "not legally" scrape
            reviews[business_name] = yelp_api.reviews_query(biz_id)

            # temporary data frame we can use that will be appended to a master one later
            temp_df = pd.DataFrame.from_dict(reviews[business_name]['reviews'])

            temp_df = temp_df.drop('user',1)

            # add column for ISP provider
            temp_df.insert(0,'ISP_name',business_name)

            # add column for business id
            temp_df.insert(1,'business_id',biz_id)

            # add column for business location
            temp_df.insert(6,'location',
                           str(business_df2[business_df2['id'] == biz_id]['location'].item()['display_address']))


            temp_df = temp_df.rename(columns = {"id":"rev_id"})

            reviews_df = reviews_df.append(temp_df,ignore_index = True)


        all_business_df = all_business_df.append(business_df2, ignore_index=True)
        all_reviews_df = all_reviews_df.append(reviews_df,ignore_index=True)

    # Save data
    # if no previous files, just save the data. if previous files, append
    if business_data == None and business_reviews == None:
        all_business_df.to_csv(data_dir+'businesses.csv', index=False)
        all_reviews_df.to_csv(data_dir+'businesses_reviews.csv', index = False)

    else: #append data to previous loaded files

        prev_business_df = pd.read_csv(data_dir+business_data)

        prev_reviews_df = pd.read_csv(data_dir+business_reviews)

        new_business_df = prev_business_df.append(all_business_df, ignore_index = True)
        new_reviews_df = prev_reviews_df.append(all_reviews_df, ignore_index = True)

        new_business_df.to_csv(data_dir+'businesses.csv', index=False)
        new_reviews_df.to_csv(data_dir+'businesses_reviews.csv', index = False)


    # Save previous cities to ensure that we aren't looking at cities previously searched
    pickle.dump(city_names,open(data_dir+"cities_list.txt","wb"))


#get the api key by creating an account on yelp and then clicking on Create App. Fill out
#form and it will generate a key for you.
api_key = 'Gxa0LqhgTU-G3sf9RuA_kt5dHTxgH-m5BNMdM-0TpN56PYRFdEnoj811SGiz9O2-a5TazMI5VpOzzBH91ZMX9p4PJ1K-ALQ0VSnuuL3t4Yt97lrV-3dBdNikmVC3X3Yx'

cities = ['Los Angeles, CA','Santa Barbara, CA','Walnut, CA',
'Santa Clarita, CA','Pomona,CA','Fresno,CA']

if __name__ == '__main__':
	Yelp_ScrapeISP(api_key,cities,
		business_dataFile,business_reviewsFile)