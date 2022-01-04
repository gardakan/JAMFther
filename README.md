# JAMFther.py
JAMF API interface &amp; job-specific shortcut hub to common job functions.  Name is portmanteau of "JAMF" and "Panther", with the panther being a significant symbol to my company, and JAMF being the device management platform that we use.

# JAMFther.py 
Main GUI classes.  Has sections for Billing and Inventory.
 - Billing section parses PDF invoices and extracts key information formatted for record keeping.
 - Inventory section aims to integrate the image finder module, with eventual goal to port entire inventory management functionality (check in/out, assignments, management commands for managed devices).

# get_inventory.py
Purpose of this module is to get current inventory list from Excel file and search online for thumbnail images of each item listed.  End goal is to find appropriate images to represent items in a diverse tech inventory as visual reference in in-office inventory database.

# inventory_image_select_gui.py
Runs through downloaded inventory images by item, displays the downloaded images and allows user to select best option (or skip if none work).
