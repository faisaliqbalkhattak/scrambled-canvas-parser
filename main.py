import shutil
import sys
import os
import make_book as make_book
from get_and_build_pages import download_and_build_pages
import book_meta_data as book_meta_data

if __name__ == "__main__":

    if len(sys.argv) < 2:
        print("X X Error: Please provide a project slug.")
        sys.exit(1)
        
    # Extract the slug from the argument list
    book_slug = sys.argv[1]

    # Load demo page metadata
    meta_data   = book_meta_data.get_book_metadata(book_slug)
    pages = meta_data[0]
    pageIds = meta_data[1]
    # Get a non-sensitive demo id
    book_id = book_meta_data.get_book_id(book_slug)

    download_and_build_pages(book_slug, pages, pageIds, book_id)

    # Compile generated pages into a single demo PDF.
    print("_/ _/ Compiling generated pages into a single PDF...")

    safe_slug = "".join(ch if ch.isalnum() or ch in "-_" else "_" for ch in book_slug).strip("_") or "demo-book"
    output_book_name = os.path.join("books", f"{safe_slug}.pdf")
    make_book.create_book_from_pages(output_book_name=output_book_name, book_slug=book_slug, pages=pages)


    

    print(f"- - Deleting the raw and restored pages to save space...")

    folders_to_delete = ["raw", "restored"]

    PROTECTED_FILES = {"urdu-restored.png", "urdu-scrambled.png"}
    for folder in folders_to_delete:
        if os.path.exists(folder):
            for file in os.listdir(folder):
                file_path = os.path.join(folder, file)
                if file in PROTECTED_FILES:
                    print(f"- - Skipping protected file: {file_path}")
                    continue
                try:
                    if os.path.isfile(file_path):
                        os.remove(file_path)
                    elif os.path.isdir(file_path):
                        shutil.rmtree(file_path)
                except Exception as e:
                    print(f"X X Failed to delete {file_path}. Reason: {e}")
           
        else:
            print(f"- - The '{folder}' folder does not exist, skipping deletion.")
    print(f"_/ _/ All done! The final demo PDF is saved as '{output_book_name}'")
