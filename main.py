from bs4 import BeautifulSoup
from geopy.geocoders import Nominatim
import pandas
import folium 

import requests


# Check variable env si differente actualiser sinon rien faire
DATA = []
URL = 'https://www.santepubliquefrance.fr/maladies-et-traumatismes/maladies-et-infections-respiratoires/infection-a-coronavirus/articles/infection-au-nouveau-coronavirus-sars-cov-2-covid-19-france-et-monde'


def map_generator():
    m = folium.Map(
            location=[48.8534, 2.3488],
            zoom_start=6
            )
    m.save('index.html')


def fetch(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    return soup.find_all('td')


def find_region_coordinates():
	global dataset
	geolocator = Nominatim()
	dataset = pandas.DataFrame(DATA)

	dataset['region_coord']  = dataset['Region'].apply(geolocator.geocode)
	dataset['Latitude'] = dataset['region_coord'].apply(lambda x: (x.latitude))
	dataset['Longitude'] = dataset['region_coord'].apply(lambda x: (x.longitude))


def populate_dict(data):
    for i in range(0, len(data)):
        if i % 2 == 0:
           region = data[i].text
           number = data[i+1].text

           if region == 'Total Métropole' or region == 'Total Outre Mer':
               pass
           else:
               DATA.append(
                       {
					   'Region': region,
                       'Persons': number,
                       'Latitude': None,
					   'Longitude': None,
					   }
			   )
    find_region_coordinates()



def main():
    data = fetch(URL)
    populate_dict(data)


if __name__ == '__main__':
    main()
    map_generator()
    print(dataset)
