from icrawler.builtin import GoogleImageCrawler

crawler = GoogleImageCrawler(
    storage={'root_dir': 'cars'}
)

crawler.crawl(
    keyword='cars',
    max_num=100
)