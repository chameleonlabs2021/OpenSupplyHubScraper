from osh_lib import OpenSupplyHubScraper

if __name__ == "__main__":
    keyword = "wilmar"
    scraper = OpenSupplyHubScraper(keyword)
    scraper.login()
    scraper.list_populator()

    # Keep the browser open until the user presses Enter
    input("Press Enter to close the browser...")
    scraper.quit_driver()