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

# Scraped data structure
The data scraped by Documentation-scraper is limited to the following:
  * Summary: Text and lists in the beginning of the file. Excludes code and tables
  * Type: Type of entity (class/interface)
  * API level: Available since Api level 
  * Parent class
  * Implemented interfaces
  * Nested Classes 
    * Type (class or interface)
    * Description
  * Constants
    * Name
    * Type
    * Value
    * Description
    * API level
  * Fields
    * Name
    * Type
    * Description
    * API level
  * Public Constructors
    * Name
    * Description
    * Parameters
      * Name
      * Type
      * Description
    * API level
  * Methods (public/protected)
    * Name
    * Description
    * Parameters
      * Name
      * Type
      * Description
    * Return info
      * Type
      * Description
    * API level

I'll enhance this list with more items as needed

# Output formats
Currently Documentation-scraper supports two output formats (implemented as serializers):
  * Basic: This is the default format. The serializer simply dumps all scraped data in the json format 
  * DrQA: This is a format compatible with Facebook's [DrQA](https://github.com/facebookresearch/DrQA). This serializer only keeps certain fields and also merges the name of field with the description
  
To select the format use the flag `--save_format` with the `basic` or `drqa` option

# Using with DrQA
Although [DrQA](https://github.com/facebookresearch/DrQA) isn't optimized for such datasets (It is trained on Stanford's [SQuAD](https://rajpurkar.github.io/SQuAD-explorer/) dataset and Wikipedia) you can run the pipeline on it and get some decent results. 
Follow the [Retriever instructions](https://github.com/facebookresearch/DrQA/tree/master/scripts/retriever) on how to setup the database and the model. You will also need to [set up the Reader](https://github.com/facebookresearch/DrQA/tree/master/scripts/reader) to use the full QA system. 
Here are some of the more sensible answers:

*"what is an activity?"
```
>>> process("what is an activity?")
08/12/2017 01:14:06 AM: [ Processing 1 queries... ]
08/12/2017 01:14:06 AM: [ Retrieving top 5 docs... ]
08/12/2017 01:14:07 AM: [ Reading 710 paragraphs... ]
08/12/2017 01:14:26 AM: [ Processed 1 queries in 20.3450 (s) ]
Top Predictions:
+------+------------------------------+----------------------------------------+--------------+-----------+
| Rank |         Answer               |                  Doc                   | Answer Score | Doc Score |
+------+------------------------------+----------------------------------------+--------------+-----------+
|  1   | a single, focused thing that | reference.android.app.Activity Summary |     206      |   14.444  |
|      | the user can do              |                                        |              |           |
+------+------------------------------+----------------------------------------+--------------+-----------+

Contexts:
[ Doc = reference.android.app.Activity Summary ]
An activity is a single, focused thing that the user can do. Almost all activities interact with the
user, so the Activity class takes care of creating a window for you in which you can place your UI 
with setContentView(View). While activities are often presented to the user as full-screen windows, 
they can also be used in other ways: as floating windows (via a theme with windowIsFloating set) or 
embedded inside of another activity (using ActivityGroup). There are two methods almost all subclasses 
of Activity will implement:
```

*"which method sets the focus of a view?"*
```
>>> process("which method sets the focus of a view?")
08/11/2017 10:57:06 PM: [ Processing 1 queries... ]
08/11/2017 10:57:06 PM: [ Retrieving top 5 docs... ]
08/11/2017 10:57:06 PM: [ Reading 1272 paragraphs... ]
08/11/2017 10:57:27 PM: [ Processed 1 queries in 21.4881 (s) ]
Top Predictions:
+------+--------------+-------------------------------------+--------------+-----------+
| Rank |    Answer    |                 Doc                 | Answer Score | Doc Score |
+------+--------------+-------------------------------------+--------------+-----------+
|  1   | requestFocus | reference.android.view.View Summary |    6652.1    |   59.214  |
+------+--------------+-------------------------------------+--------------+-----------+

Contexts:
[ Doc = reference.android.view.View Summary ]
Set properties: for example setting the text of a TextView. The available properties and the methods 
that set them will vary among the different subclasses of views. Note that properties that are known 
at build time can be set in the XML layout files. Set focus: The framework will handle moving focus 
in response to user input. To force focus to a specific view, call requestFocus(). Set up listeners: 
Views allow clients to set listeners that will be notified when something interesting happens to the 
view. For example, all views will let you set a listener to be notified when the view gains or loses 
focus. You can register such a listener using setOnFocusChangeListener(android.view.View.OnFocusChange
Listener).Other view subclasses offer more specialized listeners. For example, a Button exposes a 
listener to notify clients when the button is clicked. Set visibility: You can hide or show views using 
setVisibility(int).
```

*"what is the alarm manager required for?"*
```
>>> process("what is the alarm manager required for?")
08/11/2017 10:59:12 PM: [ Processing 1 queries... ]
08/11/2017 10:59:12 PM: [ Retrieving top 5 docs... ]
08/11/2017 10:59:12 PM: [ Reading 343 paragraphs... ]
08/11/2017 10:59:19 PM: [ Processed 1 queries in 6.3917 (s) ]
Top Predictions:
+------+------------------------------+--------------------------------------------+--------------+-----------+
| Rank |            Answer            |                    Doc                     | Answer Score | Doc Score |
+------+------------------------------+--------------------------------------------+--------------+-----------+
|  1   | cases where you want to have | reference.android.app.AlarmManager Summary |    7405.6    |   95.472  |
|      | your application code run at |                                            |              |           |
|      | a specific time              |                                            |              |           |
+------+------------------------------+--------------------------------------------+--------------+-----------+

Contexts:
[ Doc = reference.android.app.AlarmManager Summary ]
Note: The Alarm Manager is intended for cases where you want to have your application code run at a specific 
time, even if your application is not currently running. For normal timing operations (ticks, timeouts, etc) 
it is easier and much more efficient to use Handler.
```

*"What can I use to run tasks in the background?"*
```
>>> process("what can I use to run tasks in the background?")
08/11/2017 11:01:25 PM: [ Processing 1 queries... ]
08/11/2017 11:01:25 PM: [ Retrieving top 5 docs... ]
08/11/2017 11:01:26 PM: [ Reading 970 paragraphs... ]
08/11/2017 11:01:40 PM: [ Processed 1 queries in 14.5893 (s) ]
Top Predictions:
+------+-----------------------+---------------------------------------------+--------------+-----------+
| Rank |         Answer        |                     Doc                     | Answer Score | Doc Score |
+------+-----------------------+---------------------------------------------+--------------+-----------+
|  1   | JOB_SCHEDULER_SERVICE | reference.android.content.Context Constants |    3962.3    |   43.682  |
+------+-----------------------+---------------------------------------------+--------------+-----------+

Contexts:
[ Doc = reference.android.content.Context Constants ]
JOB_SCHEDULER_SERVICE is Use with getSystemService(Class) to retrieve a JobScheduler instance for managing 
occasional background tasks.
```

I believe that using embeddings built from this dataset as well as using [more specific ones](http://ai2-website.s3.amazonaws.com/publications/multivex.pdf) can improve the accuracy in overall. Another could be to generate more verbose descriptions from the structure data in order to match better answers.
