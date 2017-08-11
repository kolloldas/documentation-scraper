# Documentation Scraper
A Python based web scraper for Android [documentation](https://developer.android.com/reference/classes.html). Currently it is tailored for the reference section. It can generate parsed output which is compatible with the [DrQA](https://github.com/facebookresearch/DrQA) question answering system.

# Usage
Documentation-scraper requires [Beautiful Soup 4](https://www.crummy.com/software/BeautifulSoup/bs4/doc/) to run. Install with pip:
```
pip install -U beautifulsoup4
```
To scrape a single page run `scraper.py` as follows:
```
python scraper.py --start_url https://developer.android.com/reference/android/app/Activity.html --no_crawling
```
This will generate an *Activity.json* file under `reference/android/app` relative to the current directory. To change the output directory add the flag `--save_path some/other/path`

Documentation-scraper can crawl for links which you can restrict to certain paths. To scrape Android documentation pages only under `android/app` and `android/content` run the following command:
```
python scraper.py --start_url https://developer.android.com/reference/android/app/Activity.html \ 
--path_filters reference/android/app reference/android/content --save_path dump
```
You can set the number of worker processes it uses to speed up scraping with the `--num_workers` flag
Occasionally certain pages can fail to parse. In that case Documentation-scraper will log the urls in `scrape-errors-x.log` where `x` is the worker id. Please log an issue with the URL and I'll try my best to fix the parser!
