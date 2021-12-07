import requests
from bs4 import BeautifulSoup


# Extract data from Website

def data_extraction():
    try:
        content = requests.get('https://bmkg.go.id')
    except Exception:
        return None

    if content.status_code == 200:
        # Get and assign Date and Time data
        soup = BeautifulSoup(content.text, 'html.parser')
        result = soup.find('span', {'class': 'waktu'})
        result = result.text.split(', ')
        date = result[0]
        time = result[1]

        # Get and assign magnitude, depth, ls, bt, location, and perceived data
        result = soup.find('div', {'class', 'col-md-6 col-xs-6 gempabumi-detail no-padding'})
        result = result.findChildren('li')

        i = 0
        magnitude = None
        depth = None
        ls = None
        bt = None
        location = None
        perceived = None

        for res in result:
            if i == 1:
                magnitude = res.text
            elif i == 2:
                depth = res.text
            elif i == 3:
                coordinate = res.text.split(' - ')
                ls = coordinate[0]
                bt = coordinate[1]
            elif i == 4:
                location = res.text
            elif i == 5:
                perceived = res.text
            i = i + 1

        output = dict()
        output['date'] = date
        output['time'] = time
        output['magnitude'] = magnitude
        output['depth'] = depth
        output['coordinate'] = {'ls': ls, 'bt': bt}
        output['location'] = location
        output['perceived'] = perceived

        return output
    else:
        return None

# Show the data from extraction

def show_data(result):
    if result is None:
        print('Latest earthquake data is not found')
        return
    print('Latest earthquacke based on BMKG')
    print(f"Date: {result['date']}")
    print(f"Time: {result['time']}")
    print(f"Magnitude: {result['magnitude']}")
    print(f"Depth: {result['depth']}")
    print(f"Coordinate: LS={result['coordinate']['ls']}, BT={result['coordinate']['bt']}")
    print(f"Location: {result['location']}")
    print(f"Perceived: {result['perceived']}")

if __name__ == '__main__':
    result = data_extraction()
    show_data(result)