import os
import threading
import img2pdf
import book_meta_data as book_meta_data
status_file_lock = threading.Lock()


def write_status_line(line):
    with status_file_lock:
        with open("status.txt", "a", encoding="utf-8") as status_file:
            status_file.write(f"{line}\n")
            status_file.flush()
            os.fsync(status_file.fileno())


def create_book_from_pages(output_book_name="restored_book.pdf", book_slug = "", pages = []):
    
    if book_slug == "":
        print("Error: No book slug provided. Cannot fetch metadata.")
        return
    
    print("Gathering pages in the correct sequence...")
    
    image_paths = []
    
    # Reconstruct the exact order using your pageInfo array
    for i in range(0, len(pages)):
        # Match the exact naming convention used in script
        img_path = os.path.join("restored", f"{pages[i]}")
        
        if os.path.exists(img_path):
            image_paths.append(img_path)
        else:
            print(f"Warning: Missing page for page index {i} ({img_path})")

    if not image_paths:
        print("No images found in the 'restored' folder!")
        return

    print(f"Found {len(image_paths)} pages. Compiling PDF")

    output_dir = os.path.dirname(output_book_name)
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)

    try:
        # Open the output PDF file and write the pages bytes directly into it
        with open(output_book_name, "wb") as f:
            # img2pdf.convert reads the pages and wraps them directly into a PDF layout
            f.write(img2pdf.convert(image_paths))
    except Exception as e:
        write_status_line(f"FAILED: '{output_book_name}'")
        raise

    if not os.path.exists(output_book_name):
        write_status_line(f"FAILED: '{output_book_name}'")
        raise FileNotFoundError(f"X X PDF output was not created: {output_book_name}")

    write_status_line(f"SUCCESS: '{output_book_name}'")
    print(f"_/ _/ Success! PDF Book successfully created and saved as '{output_book_name}'")
