# get all xml filenames inside xml3 folder

import json
import os
from datetime import datetime
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
from threading import Semaphore
from duplicate_checker import DuplicateProcurementChecker
from parser import parse_procurement_xml




# Let's use a semaphore to protect file writting
write_semaphore = Semaphore(1)




def _create_output_file():
    timestamp = datetime.now().strftime("%Y%m%d_%H.%M.%S")
    filename = f"output_{timestamp}.json"

    # Just creating a file, using a context manager to ensure it's properly closed
    with open(filename, "w", encoding="utf-8") as f:
        pass

    # ensure it exists before continuing
    if not os.path.exists(filename):
        raise RuntimeError("Failed to create output file")

    return filename


def _process(filename, output_file,duplicate_checker):
    with open(filename, "r", encoding="utf-8") as f:
        content = f.read()

    parsed = parse_procurement_xml(content)

    if duplicate_checker.is_duplicate(parsed) == 1:
        # we just output to stdout for demonstration purposes, but we could also write to a separate file or database
        reference = parsed.get("tender", {}).get("referenceNumber")
        title = parsed.get("tender", {}).get("title")
        print(f"Duplicated procurement: {reference} - {title}")
        return

    write_semaphore.acquire()
    try:
        with open(output_file, "a", encoding="utf-8") as out:
            out.write(json.dumps(parsed) + "\n")
    finally:
        write_semaphore.release()


def process_files(max_workers=4):
    xml_folder = Path("xml3")
    filenames = xml_folder.glob("*.xml")
    
    # This could easly be replaced by a more evolved implementation and do fancier
    # such compare based on all fields using a simple classifier
    duplicate_checker = DuplicateProcurementChecker()

    output_file = _create_output_file()
    print(f"Setting outputfile: {output_file}")

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        for f in filenames:
            executor.submit(_process, f, output_file, duplicate_checker)


if __name__ == "__main__":
    process_files()