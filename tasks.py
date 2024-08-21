from robocorp.tasks import task
from robocorp import browser
from RPA.HTTP import HTTP
from RPA.Tables import Tables
from RPA.PDF import PDF
from RPA.Archive import Archive
import shutil


@task
def order_robots_from_RobotSpareBin():

    browser.configure(slowmo=200)
    open_robot_order_website()
    download_orders_file()
    fill_form_with_csv_data()
    archive_receipts()
    cleans_up()


def open_robot_order_website():
    """ navigate to the given url and click ok on popup"""
    browser.goto("https://robotsparebinindustries.com/#/robot-order")
    page = browser.page()
    page.click("text=OK")

def download_orders_file():
    """ download orders csv file from given URL"""
    http = HTTP()
    http.download("https://robotsparebinindustries.com/orders.csv", "wp", overwrite=True)


def fill_form_with_csv_data():
    """ get robot orders data from orders.csv and fill the form to order"""
    order_csv = Tables()
    robot_orders = order_csv.read_table_from_csv("orders.csv")
    
    for order in robot_orders:
        fill_and_submit_robot_order(order)

def fill_and_submit_robot_order(order):
    """ get order detail and fill the order detail and submit """
    page = browser.page()

    head_names = {
        "1" : "Roll-a-thor head",
        "2" : "Peanut crusher head",
        "3" : "D.A.V.E head",
        "4" : "Andy Roid head",
        "5" : "Spanner mate head",
        "6" : "Drillbit 2000 head"
    }

    head_number = order["Head"]

    page.select_option("#head",head_names.get(head_number))
    page.click("#id-body-"+order["Body"])
    page.fill("input[placeholder='Enter the part number for the legs']",order["Legs"])
    page.fill("#address", order["Address"])

    while True:
        page.click("#order")
        order_another = page.query_selector("#order-another")
        if order_another:
            pdf_path = store_receipt_as_pdf(int(order["Order number"]))
            screenshot_path = robot_screenshot(int(order["Order number"]))
            embed_screenshot_to_receipt(screenshot_path,pdf_path)
            order_another_robot()
            clicks_ok()
            break


def store_receipt_as_pdf(order_number):
    """ save receipt as pdf """
    page = browser.page()
    receipt_html = page.locator("#receipt").inner_html()

    pdf = PDF()
    pdf_path = "output/receipts/{0}.pdf".format(order_number)
    pdf.html_to_pdf(receipt_html,pdf_path)
    return pdf_path

def robot_screenshot(order_number):
    """ screen shot the robot and save it in output/screenshots/ """
    page = browser.page()
    screenshot_path = "output/screenshots/{0}.png".format(order_number)
    page.locator("#robot-preview-image").screenshot(path=screenshot_path)
    return screenshot_path


def embed_screenshot_to_receipt(screenshot, pdf_file):
    """ embed screenshot on the receipt page and generate pdf"""
    pdf = PDF()
    pdf.add_watermark_image_to_pdf(image_path=screenshot, source_path=pdf_file, output_path=pdf_file)


def order_another_robot():
    """Clicks on order another button to order another bot"""
    page = browser.page()
    page.click("#order-another")

def clicks_ok():
    """ click on ok button when new order to place"""
    page = browser.page()
    page.click("text=OK")


def archive_receipts():
    """ archive the receipts into a zip file """
    lib = Archive()
    lib.archive_folder_with_zip("./output/receipts", "./output/receipts.zip")

def cleans_up():
    """remove all receipts and screenshots after creating zip """
    shutil.rmtree("./output/receipts")
    shutil.rmtree("./output/screenshots")