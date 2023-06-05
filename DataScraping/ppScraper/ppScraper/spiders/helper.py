from urllib.parse import urlparse

def get_parsed_url(url):
        parsed_url = urlparse(url)
        return (parsed_url.scheme + "://" + parsed_url.netloc + parsed_url.path)