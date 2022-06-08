# A simple script to scrape upcomming movies from Carolina Theatre's website and generate an html table

import requests
from bs4 import BeautifulSoup
from datetime import datetime

def get_movies(url):
    """
    Get the movies from the given url
    :param url: The carolina theatre url to scrape from (string)
    :return: A list of tuples containing the movie title, url, and showtime in the format: (('title', 'url'), 'date', 'time')
    :rtype: list of tuples
    """
    page = requests.get(url)
    soup = BeautifulSoup(page.content, 'html.parser')

    # List all the movies on the page
    movies = soup.find_all('div', class_='card eventCard film')

    # Build a list of movies and their titles and links
    movie_list = []
    for movie in movies:
        title = movie.find('p', class_='card__title').get_text()
        link = movie.find('a')['href']
        movie_list.append((title, link))

    # Initialize a list to hold the showtimes for each movie in the movie_list
    showtime_list = []

    # Visit each movie's page and get showtimes
    for movie in movie_list:
        url = movie[1]
        page = requests.get(url)
        soup = BeautifulSoup(page.content, 'html.parser')

        # Find the showtimes
        showtimes = soup.find_all('div', class_='sidebar__showInfo')

        # Loop through and parse each showtime
        for showtime in showtimes:
            date_and_time = showtime.find_all('li', {"class" : lambda L: L and L.startswith('showInfo__date')})
            for dt in date_and_time:
                date = dt.find('span', class_='date').get_text()
                # Reformat the date to make it more human readable
                date = date.split(', ')[1] + ', ' + date.split(', ')[0]
                time = dt.find_all('span', class_='time')
                # A single date can have multiple showtimes so we need to loop through each time
                for t in time:
                    showtime_list.append((movie, date, t.get_text()))
    return showtime_list

def get_events(url):
    """
    Get the events from the given url
    :param url: The carolina theatre url to scrape from (string)
    :return: A list of tuples containing the movie title, url, and showtime in the format: (('title', 'url'), 'date', 'time')
    :rtype: list of tuples
    """    
    page = requests.get(url)
    soup = BeautifulSoup(page.content, 'html.parser')

    # List all the events on the page
    events = soup.find_all('div', class_='card eventCard event')

    # Build a list of events and their titles and links
    event_list = []
    for event in events:
        title = event.find('p', class_='card__title').get_text()
        link = event.find('a')['href']
        event_list.append((title, link))
    
    # Initialize a list to hold the showtimes for each event in the event_list
    showtime_list = []

    # Visit each event's page and get showtimes
    for event in event_list:
        url = event[1]
        page = requests.get(url)
        soup = BeautifulSoup(page.content, 'html.parser')

        # Find the showtime
        showtime = soup.find('li', class_='showInfo__date').get_text().strip()
        # Parse out the date and time from showtime
        try:
            date = showtime.split(' at ')[0]
            date = date.split(', ')[1] + ', ' + date.split(', ')[0]
            time = showtime.split(' at ')[1]
        except:
            date = 'TBD'
            time = 'TBD'

        showtime_list.append((event, date, time))
    
    return showtime_list


def sort_showtimes(showtime_list):
    """
    Sorts the showtimes by date
    :param showtime_list: A list of tuples containing the movie title, url, and showtime in the format: (('title', 'url'), 'date', 'time')
    :return: A list of tuples containing the movie title, url, and showtime in the format: (('title', 'url'), 'date', 'time') sorted by date
    """
    # Sort the showtimes by date
    # Date format: Sat, Mar 12
    # %B ---> for Month
    # %d ---> for Day
    # Use split to remove the day from the date
    print(showtime_list)

    def inner_function(date):
        if date[1] == 'TBD':
            return datetime.max
        else:
            try:
                return datetime.strptime(date[1].split(',')[0], '%B %d')
            except:
                return datetime.strptime(date[1].split(',')[0], '%b %d')

    showtime_list.sort(key = inner_function)

    return showtime_list

def gen_html_table(showtime_list):
    """
    Generates an html table from the given showtime_list
    :param showtime_list: A list of tuples containing the movie title, url, and showtime in the format: (('title', 'url'), 'date', 'time')
    :return: An html table (string)
    """
    html = '<table>'
    for showtime in showtime_list:
        title = showtime[0][0]
        url = showtime[0][1]
        date = showtime[1]
        time = showtime[2]
        html += '<tr><td>{}</td><td>{}</td><td><a href="{}">{}</a></td></tr>'.format(date, time, url, title)
    html += '</table>'
    return html

def write_html_table(showtime_list):
    """
    Writes the html table to a file titled 'showtimes.html'
    :param showtime_list: A list of tuples containing the movie title, url, and showtime in the format: (('title', 'url'), 'date', 'time')
    :return: None
    """
    html = gen_html_table(showtime_list)
    with open('showtimes.html', 'w') as f:
        f.write(html)

def write_html_table_today(showtime_list):
    """
    Writes the html table to a file titled 'showtimes_today.html' for all shows today
    :param showtime_list: A list of tuples containing the movie title, url, and showtime in the format: (('title', 'url'), 'date', 'time')
    :return: None
    """
    # Today's date in the format: Mar 12, Fri
    today = datetime.today().strftime('%b %d, %a')
    showtime_list = [showtime for showtime in showtime_list if showtime[1] == today]
    html = gen_html_table(showtime_list)
    with open('showtimes_today.html', 'w') as f:
        f.write(html)

# Start with basic now showing page
url = 'https://carolinatheatre.org/wp-admin/admin-ajax.php?action=film_filter&events=now-playing'
showtime_list = get_movies(url)


# Now do the same for upcoming movies
url = 'https://carolinatheatre.org/wp-admin/admin-ajax.php?action=film_filter&events=coming-soon'
showtime_list += get_movies(url)

# Now get all upcoming events
url = 'https://carolinatheatre.org/wp-admin/admin-ajax.php?action=event_filter&events=all'
showtime_list += get_movies(url)

# Finally get all upcoming events
url = 'https://carolinatheatre.org/wp-admin/admin-ajax.php?action=event_filter&events=all'

showtime_list += get_events(url)
showtime_list = sort_showtimes(showtime_list)
write_html_table(showtime_list)
write_html_table_today(showtime_list)
