from robocorp.tasks import task
from robocorp import browser
from RPA.HTTP import HTTP
from RPA.Tables import Tables
from RPA.PDF import PDF
from RPA.Archive import Archive


def open_robot_order_website():
    """Opens RobotSpareBin website."""
    page = browser.page()
    page.goto('https://robotsparebinindustries.com/#/robot-order')


def close_annoying_modal():
    """Closes the annoying modal."""
    page = browser.page()
    page.click("button:text('OK')")


def get_orders():
    """Gets orders from order file."""
    http = HTTP()
    http.download(url='https://robotsparebinindustries.com/orders.csv',
                  overwrite=True,
                  target_file='output/orders.csv')
    library = Tables()
    orders = library.read_table_from_csv('output/orders.csv',
                                         header=True)
    return orders


def store_receipt_as_pdf(filepath):
    """Stores the receipt as a PDF file."""
    page = browser.page()
    receipt_html = page.locator('#receipt').inner_html()

    pdf = PDF()
    pdf.html_to_pdf(receipt_html, filepath)


def screenshot_robot(filepath):
    """Stores the screenshot of the robot."""
    page = browser.page()
    page.locator('#robot-preview-image').screenshot(path=filepath)


def embed_screenshot_to_receipt(pdf_filepath, screenshot_filepath):
    """Embeds the screenshot of the robot to the PDF receipt."""
    pdf = PDF()
    pdf.add_files_to_pdf(
        files=[pdf_filepath, screenshot_filepath], target_document=pdf_filepath)


def fill_order(row):
    """Fills a single order."""
    page = browser.page()
    # Get the page ready for the order
    close_annoying_modal()

    # Head
    page.select_option('#head', row['Head'])
    # Body
    page.check(f"#id-body-{row['Body']}")
    # Legs
    page.fill('.form-control', row['Legs'])
    # Address
    page.fill('#address', row['Address'])

    # Preview the robot
    page.click('#preview')
    # Submit the order
    page.click('#order')
    while page.locator('.alert-danger').is_visible():
        page.click('#order')    # Try again

    # pdf
    pdf_filepath = f"output/receipts/{row['Order number'].zfill(2)}_receipt.pdf"
    store_receipt_as_pdf(pdf_filepath)

    # screenshot
    screenshot_filepath = f"output/robots/robot_{row['Order number'].zfill(2)}.png"
    screenshot_robot(screenshot_filepath)

    # embed
    embed_screenshot_to_receipt(pdf_filepath, screenshot_filepath)

    # Order another
    page.click('#order-another')


def fill_the_form(orders):
    """Fills the form with data from orders."""
    for row in orders:
        print(f"Order number: {row['Order number']}")
        fill_order(row)


def archive_receipts():
    """Creates ZIP archive of the receipts."""
    archive = Archive()
    archive.archive_folder_with_zip(
        './output/receipts', './output/receipts.zip', recursive=True)


@task
def order_robots_from_RobotSpareBin():
    """
    Orders robots from RobotSpareBin Industries Inc.
    Saves the order HTML receipt as a PDF file.
    Saves the screenshot of the ordered robot.
    Embeds the screenshot of the robot to the PDF receipt.
    Creates ZIP archive of the receipts and the images.
    """
    browser.configure(
        slowmo=100,
    )
    open_robot_order_website()
    orders = get_orders()
    fill_the_form(orders)
    archive_receipts()
