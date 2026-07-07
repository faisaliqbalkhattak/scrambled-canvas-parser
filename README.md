# Rekhta Books Downloader

This project was basically an exploration of how book preview websites work and what kind of data they return.

While looking into Rekhta books, I noticed that the pages are not given as normal clean images at first. The images come scrambled. Then another request from the API gives the mapping data that tells how the scrambled pieces should be arranged back into the real page. After understanding this, I built the logic to unscramble the image and restore the original page.

## What this project does

- takes a book slug from the user
- reads the book metadata from Rekhta
- gets the page ids and page names
- downloads the scrambled page images
- gets the mapping data for each page from the API
- reconstructs the page using the unscrambling logic
- saves the restored pages
- combines all restored pages into a single PDF

## How I built it

I first inspected the website and figured out that the book page is not just a simple image download. It needs a few requests to get the full data.

The main flow is:

1. `server.py` starts a Flask server and serves the frontend.
2. When the user enters a slug and clicks download, the frontend sends the slug to the backend.
3. `main.py` starts the full download process.
4. `get_and_built_pages.py` downloads the raw scrambled pages and rebuilds them using the mapping data.
5. `make_book.py` puts all restored pages into one PDF.

## Why threading was used

I used multithreading to make the downloading faster. Since every page can be fetched and restored separately, the project processes multiple pages at the same time instead of one by one.

That makes the whole download process faster and smoother.

## Live progress on the screen

I also added a live status system so the frontend can show what is happening while the download is running.

The backend keeps writing status updates into `status.txt`, and the frontend keeps reading those updates through a status stream. Because of that, the page can show:

- the current scrambled image
- the restored image
- the progress bar
- the current download status

So the user can actually see the book being rebuilt step by step.

## Frontend design

The frontend has an orange theme and a responsive layout.

It works on both desktop and mobile, and it also shows instructions for the slug in case someone does not know what slug means or where to find it.

### Features

* **Reverse-Engineered Matrix Stitching:** Translates coordinate arrays via Pillow to programmatically copy and patch image segments back into their original spatial order.
* **Multi-Threaded Performance:** Runs parallel fetch and processing workloads across all available CPU cores to overcome network and disk I/O bottlenecks.
* **Live Telemetry Stream:** Utilizes Server-Sent Events (SSE) to push live backend decryption statuses directly to a responsive vanilla JavaScript frontend interface.
* **Automated Compilation:** Binds sequentially verified images into a high-resolution offline PDF using `img2pdf`.


## Tech stack

- Python
- Flask
- JavaScript
- HTML
- CSS
- Pillow
- Requests
- img2pdf

## How to run

1. Start the Flask server.
2. Open the frontend in the browser at `http://127.0.0.1:5000`.
3. Enter the book slug.
4. Click download.
5. Wait until the PDF is created.

## Slug help

If you do not know the slug, open the Rekhta book page in the browser and copy the last part of the URL. That last part is the slug.

Example:

- if the URL is something like `https://www.site.com/ebooks/some-book-name`
- then `some-book-name` is the slug

## Final result

At the end, the project gives you a restored PDF of the book after downloading and rebuilding all the pages.