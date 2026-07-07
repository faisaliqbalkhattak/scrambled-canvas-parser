def get_book_metadata(book_slug):
    """
    Returns demo metadata only.
    The public version intentionally does not fetch or parse data from third-party sites.
    """
    total_pages = 16
    pages = [f"{i:03}.jpg" for i in range(1, total_pages + 1)]
    page_ids = [f"demo-{book_slug}-{i:03}" for i in range(1, total_pages + 1)]
    print(f"Prepared {len(pages)} demo pages for slug '{book_slug}'.")
    return pages, page_ids


def get_book_id(book_slug):
    """Returns a non-sensitive identifier for demo execution."""
    return f"demo-book-{book_slug}"