# -*- coding: utf-8 -*-

"""The user interface for our app"""

import os,sys

# Import Qt modules
from PyQt4 import QtCore,QtGui

# Import the compiled UI module
from mailingUi import Ui_MainWindow

# Create a class for our main window
class Main(QtGui.QMainWindow):
	def __init__(self):
		QtGui.QMainWindow.__init__(self)

		# This is always the same
		self.ui=Ui_MainWindow()
		self.ui.setupUi(self)
		self.ui.lineEdit_Subject.insert(open('subject.txt', 'r').read())
		self.ui.lineEdit_PlainText.insert(open('msgtext.txt', 'r').read())
		self.ui.textEdit_Html.setPlainText(open('msghtml.txt', 'r').read())

	def closeEvent(close):
		QtGui.QMessageBox.information(self, "Bye", "Bye, bye!!", QtGui.QMessageBox.Ok, QtGui.QMessageBox.Ok)

	def sendEmail(self):
		import smtplib
		import shutil
		from email.MIMEMultipart import MIMEMultipart
		from email.MIMEText import MIMEText
		from email.MIMEImage import MIMEImage

		self.ui.statusbar.showMessage("Preparando para envio....")

		strSubject = str(self.ui.lineEdit_Subject.text().toLatin1())
		strPlainText = str(self.ui.lineEdit_PlainText.text().toLatin1())
		strHtml = str(self.ui.textEdit_Html.toPlainText().toLatin1())
		strFrom = '%s@gmail.com' % str(self.ui.comboBox_User.currentText())
		strPass = str(self.ui.lineEdit_Password.text())

		# Unique lines case insensitive
		filenamesource = r"%s.txt" % str(self.ui.comboBox_List.currentText())
		filename = "aux_%s.txt" % str(self.ui.comboBox_List.currentText())
		shutil.copy2(filenamesource, filename)

		with open(filename) as f:
			lines = sorted(set(line.strip('\n') for line in f))
		count = 0

		for i, line in enumerate(lines):
			strTo = line

			pos = strTo.find("<")
			strName = ""
			if pos == -1:
				pos = strTo.find("@")
			strName = strTo[0:pos]

			# Create the root message and fill in the from, to, and subject headers
			msgRoot = MIMEMultipart('related')
			msgRoot['Subject'] = strSubject % strName
			msgRoot['From'] = '"Banda Let' "'s" ' Dance" <%s>' % strFrom
			msgRoot['To'] = strTo
			msgRoot.preamble = 'This is a multi-part message in MIME format.'

			# Encapsulate the plain and HTML versions of the message body in an
			# 'alternative' part, so message agents can decide which they want to display.
			msgAlternative = MIMEMultipart('alternative')
			msgRoot.attach(msgAlternative)
			msgText = MIMEText(strPlainText)
			msgAlternative.attach(msgText)
			msgText = MIMEText(strHtml, 'html')
			msgAlternative.attach(msgText)

			try:
				mailServer = smtplib.SMTP("smtp.gmail.com", 587)
				mailServer.ehlo()
				mailServer.starttls()
				mailServer.ehlo()
				mailServer.login(strFrom, strPass)
				mailServer.sendmail(strFrom, strTo, msgRoot.as_string())
				# Should be mailServer.quit(), but that crashes...
				mailServer.close()
			except Exception, exc:
				filename = "aux_%s.txt" % unicode(self.ui.comboBox_List.currentText())
				newfile = open("notsent_%s.txt" % unicode(self.ui.comboBox_List.currentText()), "wb")
				for j in range(i, len(lines)):
					newfile.write(lines[j]+"\n")
				newfile.close()
				self.ui.statusbar.showMessage("")
				QtGui.QMessageBox.information(self, "Erro", str(exc), QtGui.QMessageBox.Ok, QtGui.QMessageBox.Ok)
				return
				#raise exc

			count+=1
			self.ui.statusbar.showMessage("Email sent to: %s.... %d" % (strTo.strip(), count))

		self.ui.statusbar.showMessage("Done.... %d" % count)

def main():
	# Again, this is boilerplate, it's going to be the same on
	# almost every app you write
	app = QtGui.QApplication(sys.argv)
	window=Main()
	window.show()
	# It's exec_ because exec is a reserved word in Python
	sys.exit(app.exec_())


if __name__ == "__main__":
	main()
