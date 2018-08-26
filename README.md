# Bank Statement PDF to CSV
## Disclaimer
This project is not endorsed by, directly affiliated with, maintained, authorized, or sponsored by any bank or financial institution. All product and company names are the registered trademarks of their original owners. The use of any trade name or trademark is for identification and reference purposes only and does not imply any association with the trademark holder of their product brand.

## About the project
As far as I'm aware, my bank does not provide transactions as a CSV if the transaction happened more than 90ish days ago. However, they will provide PDF statements for up to 7 years if you signed up for them. So I made a parser to turn those statements into CSV files.

## Dependancies
Tested with Python 3.7. Also needs the Linux utility "pdftotext" (available with "sudo apt-get install poppler-utils" on Ubuntu). If you're not running on Ubuntu, you can use the Windows 10 Linux subsystem instead. Just install it, and then also install "pdftotext"

## Caution
Don't run this script on your only copy of the statements. The script renames files and creates new directories, etc. So it's wise to have two copies of your statements just in case a bug causes data loss.