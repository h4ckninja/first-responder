#!/usr/bin/env python

import subprocess
import os
import time
import shutil
import smtplib
from email.MIMEMultipart import MIMEMultipart
from email.MIMEBase import MIMEBase
from email.MIMEText import MIMEText
from email.Utils import formatdate
from email import Encoders


# SMTP information
SMTP_SERVER = "localhost"
SMTP_USER = ""
SMTP_PASS = ""
SMTP_AUTH = False
SMTP_FROM = ""

# Create a log file of all actions
f = open("log.txt", "a+")

def log(msg, display):
	# The message to write to the log file
	f.write(time.strftime("[%I:%M:%S] %d %b, %Y", time.gmtime()) + ": " + msg + "\n")

	# Boolean whether or not to display to the screen
	if(display):
		print msg

# Original method from: http://snippets.dzone.com/posts/show/2038
# Slight modifications by Micheal Cottingham
def send_mail(send_from, send_to, subject, body, files=[], server="localhost"):
	assert type(files) == list

	mail = MIMEMultipart()
	mail['From'] = send_from
	mail['To'] = send_to
	mail['Date'] = formatdate(localtime=True)
	mail['Subject'] = subject

	mail.attach(MIMEText(body))

	for f in files:
		part = MIMEBase("application", "octet-stream")
		part.set_payload(open(f, "rb").read())
		Encoders.encode_base64(part)
		part.add_header('Content-Disposition', 'attachment; filename="%s"' % os.path.basename(f))
		mail.attach(part)

	smtp = smtplib.SMTP(server)
	smtp.sendmail(send_from, send_to, mail.as_string())
	smtp.close()

# Ensure we are root
whoami = subprocess.Popen(["whoami"], stdout=subprocess.PIPE).communicate()

if(whoami[0].strip() != "root"):
	log("This must be run as root.", True)

else:
	# Prompt for the email address
	# The assumption is made that this is a valid email address
	# to speed up the program
	smtp_to = raw_input("Please enter the to email address for the logs: ")

	print ""

	log("============== Do not forget to start an incident report ==============", True)

	# netstat -pan - Pulls udp, tcp, raw, and unix connections 
	# and owning processes that netstat can see
	log("Dumping active connections. This may take a while.", True)
	os.system("netstat -pan > netstat.txt")
	log("'netstat -pan' executed", False)

	# ps aux - Pulls all running processes that ps can see
	log("Dumping current running processes.", True)
	os.system("ps aux > ps.txt")
	log("'ps aux' executed", False)

	# lsof - Pulls all open files, processes, ports that lsof can see
	log("Dumping all open files. This may take a while.", True)
	os.system("lsof > lsof.txt")
	log("'lsof' executed", False)

	# Mail the logs
	log("Mailing the logs now.", True)
	log("The log file will temporarily be closed for sending and reopened. This means that data written afterwards will not be sent to the email address!", True)

	# Temporarily closing the log file
	f.close()

	subj = "First Responder Results"
	body = "The attached files are the results from the First Responder script. Please ensure you start an incident report and follow the guidelines. The attached files should be added to the case."
	files = ["log.txt", "netstat.txt", "ps.txt", "lsof.txt"]
	send_mail(SMTP_FROM, smtp_to, subj, body, files, SMTP_SERVER)

	# Now opening it again
	f = open("log.txt", "a+")

	log("Mail was sent.", True)
	log("Please ensure you start a case if you have not already and you follow the guidelines.", True)

	# Close the file
	f.close()
