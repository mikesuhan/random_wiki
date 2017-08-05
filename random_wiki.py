import bs4
import requests
import datetime
from time import sleep
from requests.exceptions import HTTPError, ReadTimeout
import os
import re
import argparse


class RandomWiki:

    def __init__(self, folder, rand_url='https://tr.wikipedia.org/wiki/%C3%96zel:Rastgele', limit=1000, rate=1,
                 file_ext='txt', encoding='utf-8', request_timeout=60, html_encoding='UTF-8',
                 verbose=True, log_file='log.txt', resume=False):
        """
        Scrapes the paragraphs from random pages on MediaWiki. Creates one file per page.
        
        Arguments:
            folder: The folder where the files are saved to.
        
        Keyword Arguments:
            rand_url: The value of the href attribute for the MediaWiki site. Defaults to Turkish Wikipedia.
            limit: How many pages to scrape. 
            rate: The argument that will be passed to sleep.time after each http request.
            file_ext: The file extension each page is saved as.
            encoding: The encoding each file is saved using.
            request_timeout: The timeout keyword argument that will be passed to requests.Session.get
            html_encoding: The charset used by the site being scraped.
            verbose: Prints updates to the console if True.
            log_file: Filename of the log. 
            resume: Resumes previous session based on log_file if True. Other keyword arguments should be added as they
            were in the previous session if resume is used.
        """
        if not os.path.exists(folder):
            os.mkdir(folder)

        self.folder = folder
        self.rand_url = rand_url
        self.limit = limit
        self.rate = rate
        self.file_ext = file_ext
        self.encoding = encoding
        self.request_timeout = request_timeout
        self.html_encoding = html_encoding
        self.verbose = verbose
        self.log_file = log_file

        if resume:
            with open(log_file) as f:
                log = f.read().splitlines()

            self.n = int(log[-1].split()[0]) + 1
            self.cached_urls = [url for n, d, y, url in (line.split() for line in log)]

            if verbose:
                print('Resuming based on', log_file)

        else:
            self.n = 0
            self.cached_urls = []

    def start(self):
        """Begins scraping"""
        while self.n < self.limit or not self.limit:
            self.scrape()

    def scrape(self):
        """Scrapes a page and proccesses the html."""
        url, html = self.get_html_rt(self.rand_url)
        title = html.find('h1', {'id': 'firstHeading'}).getText(separator=' ')

        if url not in self.cached_urls:
            self.cached_urls.append(title)
            content = html.find('div', {'id': 'bodyContent'}).find_all('p')
            content = '\n\n'.join(p.getText(separator=' ').strip() for p in content if p.getText(separator=' ').strip())

            if content:

                log_line = '{n} {time} {url}\n'.format(n=self.n,
                                                       time=datetime.datetime.today().strftime('%Y-%m-%d %X'),
                                                       url=url)

                with open(self.log_file, 'a+', encoding=self.encoding) as f:
                    f.write(log_line)

                self.write(title, content)
                self.n += 1

    def write(self, title, content):
        """Processes the title and saves the file."""
        title = re.sub('[\.\\,\?/`~!@#$%\^\&\*\+\=;:\'\"\{\}<>\|\s]', '', title, flags=re.IGNORECASE)
        fn = '{title}_{id}.{ext}'.format(title=title, id=self.n, ext=self.file_ext)
        p = os.path.join(self.folder, fn)

        with open(p, 'w', encoding=self.encoding) as f:
            f.write(content)

        if self.verbose:
            print(self.n, fn)

    def get_html(self, url):
        """Returns tuple of 1. the url and 2. a bs4 object."""

        if self.rate:
            sleep(self.rate)

        try:
            s = requests.Session()
            headers = {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.36',
                }
            html = s.get(url, timeout=self.request_timeout, headers=headers)
            url = html.url
            html.encoding = self.html_encoding
            html.raise_for_status()
            html = bs4.BeautifulSoup(html.text, 'html.parser')
            return url, html

        except HTTPError or ReadTimeout:
            return False

    def get_html_rt(self, url):
        """Keeps calling get_html until something is returned."""
        output = self.get_html(url)
        if not output:
            if self.verbose:
                print('retrying', url)

            return self.get_html_rt(url)
        else:
            return output


if __name__ == '__main__':

    def str2bool(v):
        if v.lower() in ('yes', 'true', 't', 'y', '1'):
            return True
        elif v.lower() in ('no', 'false', 'f', 'n', '0'):
            return False
        else:
            raise argparse.ArgumentTypeError('Boolean value expected.')

    parser = argparse.ArgumentParser()
    parser.add_argument('folder')
    parser.add_argument('--rand_url', dest='rand_url', default='https://tr.wikipedia.org/wiki/%C3%96zel:Rastgele')
    parser.add_argument('--limit', dest='limit', default=1000, type=int)
    parser.add_argument('--rate', dest='rate', default=1, type=int)
    parser.add_argument('--file_ext', dest='file_ext', default='txt')
    parser.add_argument('--encoding', dest='encoding', default='UTF-8')
    parser.add_argument('--request_timeout', dest='request_timeout', default=60, type=int)
    parser.add_argument('--html_encoding', dest='html_encoding', default='UTF-8')
    parser.add_argument('--verbose', dest='verbose', default=True, type=str2bool)
    parser.add_argument('--log_file', dest='log_file', default='urls.txt')
    parser.add_argument('--resume', dest='resume', default=False, type=str2bool)

    args = parser.parse_args()

    rw = RandomWiki(args.folder,
                    rand_url=args.rand_url,
                    limit=args.limit,
                    rate=args.rate,
                    file_ext=args.file_ext,
                    encoding=args.encoding,
                    request_timeout=args.request_timeout,
                    html_encoding=args.html_encoding,
                    verbose=args.verbose,
                    log_file=args.log_file,
                    resume=args.resume)
    rw.start()
