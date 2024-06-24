from robocorp.tasks import task
from robocorp import browser
from RPA.HTTP import HTTP
from RPA.Tables import Tables
from RPA.PDF import PDF
from RPA.Archive import Archive

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
    close_annoying_modal()
    orders = get_orders()
    for order in orders:
        fill_and_submit_sales_form(order)
        page = browser.page()
        page.click("#preview")
        screenshoted = screenshot_robot(order['Order number'])
        page.click("#order")


        if page.content().__contains__("Error"):
            page.click("text=ORDER")
        try:
            if page.locator("#receipt"):
                pdf_file = store_receipt_as_pdf(order['Order number'])
                embed_screenshot_to_receipt(screenshoted,pdf_file)
            page.click("#order-another")
            page.click("text=OK")
        except:
            page.click("text=ORDER")


    archive_receipts()
def open_robot_order_website():
    """Navigates to the given URL"""
    browser.goto("https://robotsparebinindustries.com/")
    page = browser.page()
    page.click("text=Order your robot!")


def get_orders():
    http = HTTP()
    http.download(url="https://robotsparebinindustries.com/orders.csv", overwrite=True)
    library = Tables()
    orders = library.read_table_from_csv(
        "orders.csv", columns=["Order number", "Head", "Body", "Legs", "Address"]
    )
    return orders

def close_annoying_modal():
    page = browser.page()
    page.click("text=OK")

def fill_and_submit_sales_form(row):
    """Fills in the sales data and click the 'Submit' button"""
    page = browser.page()
    page.select_option("#head", str(row["Head"]))
    page.set_checked("#id-body-"+str(row["Head"]), True)
    page.get_by_placeholder('Enter the part number for the legs').fill(row["Legs"])
    page.fill("#address", row["Address"])

def screenshot_robot(order_number):
    page = browser.page()
    page.locator("#robot-preview").screenshot(path="output/receipts/order_"+str(order_number)+".png")
    return "output/receipts/order_"+str(order_number)+".png"

def store_receipt_as_pdf(order_number):
    page = browser.page()
    sales_results_html = page.locator("#receipt").inner_html()
    pdf = PDF()
    pdf.html_to_pdf(sales_results_html, "output/pdf/order_"+str(order_number)+".pdf")
    
    return "output/pdf/order_"+str(order_number)+".pdf"


def embed_screenshot_to_receipt(screenshot, pdf_file):
    pdf = PDF()
    pdf.add_watermark_image_to_pdf(image_path=screenshot,source_path=pdf_file,output_path=pdf_file)
    
    
def archive_receipts():
    lib = Archive()
    lib.archive_folder_with_zip('output/pdf', 'output/orders.zip')