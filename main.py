import csv
import requests

from bs4 import BeautifulSoup
from folium.features import DivIcon
from geopy.geocoders import Nominatim
import pandas
import folium


# Import data map 
# Check variable env si differente actualiser sinon rien faire
DATA = []
URL = 'https://www.santepubliquefrance.fr/maladies-et-traumatismes/maladies-et-infections-respiratoires/infection-a-coronavirus/articles/infection-au-nouveau-coronavirus-sars-cov-2-covid-19-france-et-monde'


def fetch_data_from_url(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    return soup.find_all('td')


def find_region_coordinates(dataset):
	geolocator = Nominatim(timeout=3)
	dataset['region_coord']  = dataset['Region'].apply(geolocator.geocode)
	dataset['Latitude'] = dataset['region_coord'].apply(lambda x: (x.latitude))
	dataset['Longitude'] = dataset['region_coord'].apply(lambda x: (x.longitude))
	return dataset


def create_csv():
	csv_columns = ['Region','Persons']
	csv_file = "regions.csv"
	try:
		with open(csv_file, 'w') as csvfile:
			writer = csv.DictWriter(csvfile, fieldnames=csv_columns)
			writer.writeheader()
			for d in DATA:
				writer.writerow(d)
	except IOError:
		print("I/O error")


def map_generator():
    m = folium.Map(
            location=[46.8534, 2.3488],
            zoom_start=6
            )
    dataset = pandas.read_csv('regions.csv')
    folium.Choropleth(
			columns=['Region', 'Persons'],
			data=dataset,
			fill_color='BuPu',
			fill_opacity=0.7,
			key_on='feature.properties.nom',
			legend_name='Nombre de personnes infectées par le covid 19',
			line_opacity=0.2,
            geo_data='regions.geojson',
            highlight=True,
            name='covid19',
    ).add_to(m)
    folium.LayerControl().add_to(m)

    dataset = find_region_coordinates(dataset)
    for i in range(0, len(dataset)):
        if dataset['Region'][i] == 'Saint-Martin':
            location = ['-63.052251', '18.08255']
        else:
            location = [dataset['Latitude'][i], dataset['Longitude'][i]]
        folium.Marker(
				location,
				icon=DivIcon(
					icon_size=(150,36),
					icon_anchor=(7,20),
					html='<div style="font-size: 12pt; color : black">{}</div>'.format(dataset['Persons'][i]),
					)
				).add_to(m)

    m.save('index.html')


def populate_dict(data):
    for i in range(0, len(data)):
        if i % 2 == 0:
           region = data[i].text
           number = data[i+1].text
           number = number.replace(' ', '')

           if region == 'Total Métropole' or region == 'Total Outre Mer':
               pass
           elif region == "Provence-Alpes-Côte d’Azur":
               DATA.append(
                       {'Region': "Provence-Alpes-Côte d\'Azur",
                       'Persons': int(number)}
               )
           elif region == "Ile-de-France":
               DATA.append(
                       {'Region': "Île-de-France",
                       'Persons': int(number)}
               )
           else:
               DATA.append(
                       {'Region': region,
                       'Persons': int(number)}
               )


def main():
    data = fetch_data_from_url(URL)
    populate_dict(data)
    create_csv()


if __name__ == '__main__':
    main()
    map_generator()
