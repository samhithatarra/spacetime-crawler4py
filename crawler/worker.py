from threading import Thread

from utils.download import download
from utils import get_logger
import scraper
import time


class Worker(Thread):
    def __init__(self, worker_id, config, frontier):
        self.logger = get_logger(f"Worker-{worker_id}", "Worker")
        self.config = config
        self.frontier = frontier
        super().__init__(daemon=True)
        
    def run(self):
        while True:
            tbd_url = self.frontier.get_tbd_url()
            if not tbd_url:
  
                print("************* REPORT ****************")
                print()
                print("Team Members:")
                print("    Kamaniya Sathish Kumar (56361951)")
                print("    Samhitha Tarra (69706915)")
                print("    Vani Anilkumar (36335618)")
                print()
                print("Number of Unique URLs:", scraper.count_unique_url)
                print()
                print("Longest URL:", scraper.longest_page)
                print("Number of Tokens in Longest URL:", scraper.num_words_longest_page)
                print()
                
                print("50 Most Common Words:")
                counter = 1
                for key, value in sorted(scraper.master_freq_dict.items(), key=lambda x: x[1], reverse = True):
                        if counter <= 50:
                            print(str(counter) + ". " + key + " (" + str(value) + ")")
                            counter = int(counter)
                            counter += 1
                        else:
                            break
                print()
                print("Subdomains in ics.uci.edu:")
                for tup, val in sorted(scraper.master_subdomain_dict.items(), key=lambda x: x[0]):
                    url_string = ""
                    url_string += tup[1] + "://" + tup[0] + ".ics.uci.edu,"
                    print(url_string, val)
                print()
                print("************* REPORT ****************")


                self.logger.info("Frontier is empty. Stopping Crawler.")
                break
            resp = download(tbd_url, self.config, self.logger)
            self.logger.info(
                f"Downloaded {tbd_url}, status <{resp.status}>, "
                f"using cache {self.config.cache_server}.")
            scraped_urls = scraper.scraper(tbd_url, resp)

            for scraped_url in scraped_urls:
                self.frontier.add_url(scraped_url)
            self.frontier.mark_url_complete(tbd_url)
            time.sleep(self.config.time_delay)
