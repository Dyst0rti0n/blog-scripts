# Medium Blog Post Command Fetcher

This repository contains a Python script to fetch commands embedded within Medium blog posts. By leveraging Medium's RSS feed, the script polls for the latest blog posts and extracts commands from their titles.

## Why Medium?

Medium is a popular platform for sharing ideas and stories. Using Medium as a covert C2 server has several advantages:
- **Public and Free:** Easily accessible and free to use.
- **Frequent Updates:** The platform is constantly updated with new posts.
- **Anonymity:** It's easy to create multiple accounts, ensuring anonymity.

## Setting Up

### Prerequisites

- Python 3.x
- `feedparser` library (can be installed using `pip install feedparser`)

### Instructions

1. **Create a Medium Account:** Use an anonymous or nondescript name to avoid drawing attention.
2. **Post Commands:** Embed commands within the titles of your blog posts.
3. **Clone the Repository:**

    ```sh
    git clone https://github.com/Dyst0rti0n/medium-fetcher.git
    cd medium-fetcher
    ```

4. **Install Dependencies:**

    ```sh
    pip install feedparser
    ```

5. **Configure the Script:**

    Edit the `feed_url` variable in the `main()` function to point to your Medium account's RSS feed. Replace `'https://medium.com/feed/@your_account'` with your actual feed URL.

6. **Run the Script:**

    ```sh
    python fetch_commands.py
    ```

    The script will continuously poll the RSS feed and print any new commands found in the blog post titles.

## License
This project is licensed under the MIT License. See the LICENSE file for details.