# Data Collection
This script contains the paragraph-set extraction algorithm which randomly selects a large paragraphs and adds its neighbors. The result is a csv containing 60 paragraphs to be used in the annotation inferface. 

## Data
- [Wikipedia](https://en.wikipedia.org/wiki/Wikipedia:Multiyear_ranking_of_most_viewed_pages)
- [Wikinews](https://en.wikinews.org/wiki/Wikinews:Featured_articles)
- [arXiv Abstracts](https://arxiv.org/search/advanced?advanced=1&terms-0-operator=AND&terms-0-term=&terms-0-field=title&classification-physics_archives=all&classification-include_cross_list=include&date-filter_by=all_dates&date-year=&date-from_date=&date-to_date=&date-date_type=submitted_date&abstracts=show&size=50&order=-announced_date_first) - The abstracts are copied and pasted into `arxiv.csv`
- [Dataset of Reddit Posts from August 2013](https://www.kaggle.com/ammar111/reddit-top-1000)

## TODO
- Specify arguments for generate_data and generate_diagrams scripts.
- Clean up the folder / delete outdated files