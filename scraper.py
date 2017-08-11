import urllib.request
from urllib.parse import urldefrag, urlparse
from bs4 import BeautifulSoup
import multiprocessing as mp
import re
import os
import logging
import argparse

from parsers.android_ref_parser import AndroidDocParser
from serializers.basic_serializer import BasicSerializer
from serializers.drqa_serializer import DrQASerializer

def _worker_loop(id, path_filter, url_queue, output_queue, busy_flag, save_path, Parser, Serializer):
    print('Worker %d started' % id)
    query_pattern = re.compile(path_filter)

    if len(save_path) > 0:
        os.makedirs(save_path, exist_ok=True)
    log_path = os.path.join(save_path, 'scrape-errors-%d.log' % id)
    logging.basicConfig(filename=log_path, level=logging.ERROR, filemode='w')
    
    
    while True:
        url = url_queue.get()
        if url is None:
            print('Worker %d exiting' % id)
            break
        
        busy_flag.value |= 1 << id
        print('%d Fetching' % id, url)

        try:
            with urllib.request.urlopen(url) as response:
                html = response.read()
            soup = BeautifulSoup(html, 'html5lib')
        except:
            print('%d Error fetching' % id, url)
            logging.error('Fetch Error: %s' % url)

        parser = Parser(soup)
        serializer = Serializer(url, parser, save_path=save_path)

        # Actual parsing happens here
        print('%d Parsing' % id, url)
        try:
            if parser.extract():
                serializer.save()
        except:
            print('%d Error parsing' % id, url)
            logging.error('Parse Error: %s' % url)


        items = soup.find_all('a', {'href': query_pattern})
        url_set = set()
        if len(items) > 0:
            for a in items:
                url, frag = urldefrag(a['href'])
                if url not in url_set:
                    url_set.add(url)
                    output_queue.put(url)
        else:
            output_queue.put(None)


        busy_flag.value &= ~(1 << id)

class Scraper(object):
    """
        Main Scraper Class
    """
    def __init__(self, start_url, parser_class, serializer_class, 
                 path_filters=None, save_path=None, num_workers=5, crawl=True):
        self._parser_class = parser_class
        self._serializer_class = serializer_class
        self._root_url = start_url
        self._crawl = crawl

        url = urlparse(start_url)
        domain = url.scheme + '://' + url.netloc
        if path_filters:
            filter_string = '%s/(%s)/.+html' % (domain, "|".join(path_filters))
        else:
            filter_string = '%s/.+html' % domain 

        self._url_queue = mp.Queue()
        self._output_queue = mp.Queue()
        self._busy_flag = mp.Value('i', 0)
        self._shutdown = False
        if not crawl:
            num_workers = 1

        self._workers = [mp.Process(target=_worker_loop, 
                                    args=(id, filter_string, self._url_queue, self._output_queue, self._busy_flag,
                                          save_path, self._parser_class, self._serializer_class))

                        for id in range(num_workers)]
        for w in self._workers:
            w.daemon = True
            w.start()

        

    def _shutdown_workers(self):
        if not self._shutdown:
            self._shutdown = True
            for _ in self._workers:
                self._url_queue.put(None)

    def __del__(self):
        self._shutdown_workers()
    
    def _fetch_links(self, soup, query_pattern):
        return [item["href"] for item in soup.find_all("a", {"href": query_pattern})]


    def start_scraping(self):

        url_set = set([self._root_url])
        self._busy_flag = mp.Value('i', 0)
        self._url_queue.put(self._root_url)

        while True:
            cur_url = self._output_queue.get()

            if cur_url != None and cur_url not in url_set:
                # print("Adding url", cur_url)
                url_set.add(cur_url)
                self._url_queue.put(cur_url)
                

            if (not self._crawl or
                (self._output_queue.qsize() == 0 and self._url_queue.qsize() == 0 
                and self._busy_flag.value == 0)):
                break
        
        print('Total links', len(url_set))
        return list(url_set)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--start_url', default=None, help='The starting URL to start scraping')
    parser.add_argument('--path_filters', default=None, nargs='*', 
                        help='[Optional] List of path segments to restrict scraping to')
    parser.add_argument('--parser', choices=['android-ref'], default='android-ref', help='Type of parser')      
    parser.add_argument('--save_format', choices=['basic', 'drqa'], default='basic', help='Format of saved files')
    parser.add_argument('--save_path', default='', help='[Optional] Path to save files')
    parser.add_argument('--num_workers', type=int, default=5, help='[Optional] Number of workers to run')
    parser.add_argument('--no_crawling', action='store_true', default=False, help='[Optional] Disable crawling')

    args = parser.parse_args()


    scraper = Scraper(args.start_url, path_filters=args.path_filters, parser_class=AndroidDocParser,
                      serializer_class=DrQASerializer if args.save_format == 'drqa' else BasicSerializer,
                      save_path=args.save_path, num_workers=args.num_workers, crawl=not args.no_crawling)
    scraper.start_scraping()


    # url = 'https://developer.android.com/reference/android/icu/text/BreakIterator.html'
    # with urllib.request.urlopen(url) as response:
    #         html = response.read()
    
    # soup = BeautifulSoup(html, 'html5lib')
    # parser = AndroidDocParser(soup)
    # serializer = DrQASerializer(url, parser)

    # print(parser.extract())
    #serializer.save()
