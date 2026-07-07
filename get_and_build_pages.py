import os
import threading
import concurrent.futures
from PIL import Image


os.makedirs("raw", exist_ok=True)
os.makedirs("restored", exist_ok=True)
os.makedirs("books", exist_ok=True)
status_update_file_path = "status.txt"
status_file_lock = threading.Lock()


def write_status_line(line):
    with status_file_lock:
        with open(status_update_file_path, "a", encoding="utf-8") as status_file:
            status_file.write(f"{line}\n")
            status_file.flush()
            os.fsync(status_file.fileno())


def _load_demo_source_image():
    """Use a local placeholder image to keep this repository publish-safe."""
    preferred = os.path.join("raw", "urdu-scrambled.png")
    fallback = os.path.join("restored", "urdu-restored.png")

    source_path = preferred if os.path.exists(preferred) else fallback
    if not os.path.exists(source_path):
        return Image.new("RGB", (900, 1200), color="white")

    return Image.open(source_path).convert("RGB")


def create_public_demo_page(page_name):
    """Create a non-sensitive sample page by resizing the local placeholder."""
    source_image = _load_demo_source_image()
    page_image = source_image.resize((900, 1200))

    raw_path = os.path.join("raw", page_name)
    restored_path = os.path.join("restored", page_name)

    page_image.save(raw_path)
    write_status_line(f"RAW: '{page_name}'")

    page_image.save(restored_path)
    write_status_line(f"RESTORED: '{page_name}'")


def build_single_page(index, pages):
    page_name = pages[index]
    try:
        create_public_demo_page(page_name)
    except Exception as exc:
        print(f"X X Failed to build demo page {page_name}: {exc}")


def download_and_build_pages(book_slug, pages, page_ids, book_id):
    _ = (book_slug, page_ids, book_id)

    total_pages = len(pages)
    with status_file_lock:
        with open(status_update_file_path, "w", encoding="utf-8") as status_file:
            status_file.write(f"Total Pages: {total_pages} pages.\n")
            status_file.flush()
            os.fsync(status_file.fileno())

    max_threads = max(4, os.cpu_count() or 4)
    print(f"Starting demo process with {max_threads} CPU threads...")

    with concurrent.futures.ThreadPoolExecutor(max_workers=max_threads) as executor:
        executor.map(lambda i: build_single_page(i, pages), range(0, total_pages))

    print("_/ _/ Demo pages have been generated!")
