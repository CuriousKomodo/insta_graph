import time
from multiprocessing import Process

def timed_scroll(webdriver, scroll_time, _scroll_pause_time=2):

    def scroll(driver, scroll_pause_time):
        """
        Infinite scrolling: https://dev.to/hellomrspaceman/python-selenium-infinite-scrolling-3o12
        """

        # Get scroll height
        last_height = driver.execute_script("return document.body.scrollHeight")

        while True:
            # Scroll down to bottom
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

            # Wait to load page
            time.sleep(scroll_pause_time)

            # Calculate new scroll height and compare with last scroll height
            new_height = driver.execute_script("return document.body.scrollHeight")

            if new_height == last_height:
                # If heights are the same it will exit the function
                break
            last_height = new_height

    scroll_process = Process(target=scroll(webdriver, _scroll_pause_time))
    scroll_process.start()
    scroll_process.join(timeout=scroll_time)
    scroll_process.terminate()
    print('Scrolling of {} seconds finished'.format(scroll_time))
