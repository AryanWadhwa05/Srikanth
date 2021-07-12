                  ##
# Tews Simulator for frames : accountInformation response & credit response.
#
# BEHAVIOR_TEWS_SERVER_PROCESSED_REPLIER():
#
# The currency mapping is 

# new version 20181115 coming from IOT platform

#enable_debug_logs()
##
"""
This TEWS simulator behaves differently depending on
the destinationUri.

Here is the scheme of URIs:

PAN:     pan:XXSSSHACMEEEEFFL
MWallet: tel:+[SSS]HACMEEEE
BAN:     ban:[SSS]HACMEEEE;bic=BIC
IBAN:    iban:[SSS]HACMEEEE
EWallet: ewallet:[SSS]HACMEEEE;sp=SP

where:
* X is the card prefix
* SSS is the country prefix (padded to 3 digits for PAN only), 
   allowing to choose currency e.g.
	   '1': 'USD',   # Etats-Unis d'Am?rique
		'32': 'EUR',    # Belgium
		'63': 'PHP',    # Philippines
		'20': 'EGP',    # Egypte
		'86': 'CNY',    # Egypte
		'212': 'MAD',   # Maroc
		'233': 'GHS',   # Ghana
		'255': 'TZS',   # Tanzania (Tanzanian Shilling)
		'880': 'BDT',   # Bangladesh (Taka)
		'91': 'INR',    # India (Indian Rupee)
		'84': 'VND',    # Vietnam (D?ng)
		'254': 'KES',   # Kenya (Kenyan Shilling)
		'92': 'PKR',    # Pakistan
		'974': 'QAR',   # Qatar
		'226': 'XOF',   # Burkina Faso
		'804': 'UAH',   # Ukraine

* H is the scenario:
     0 : AI error
		 1 : Synchronous OK
		 2 : Synchronous NOK
		 3 : Asynchronous OK
		 4 : Asynchronous NOK
		 5 : Cash OK (means 2390.500 is sent back in credit response)
		 6 : Cash NOK (means 2390.500 is sent back in credit response)
		 
* A is the AI sleep:
     0 : no sleep
		 1 : 30 sec 
		 2 : 60 sec
		 3 : 80 sec
		 4 : 120 sec
		 
* C is the Credit sleep:
     0 : no sleep
		 1 : 30 sec 
		 2 : 60 sec
		 3 : 80 sec
		 4 : 120 sec
		 
* M is the MaxCompletionDate:
     1 : 20 sec 
		 2 : 80 sec
		 3 : 120 sec
		 4 : 300 sec
		 5 : 600 sec
		 
* EEEE is the error code (for scenario 0, 2, 4 and 6)

* FFF last digits (unused here)

* L is the Luhn key





For tel URIs based on the last 6 digits:
SSEEEE


on TEWS/accountInformation request:

EEEE = 0030: wait for 60s before replying (useful to test a timeout)
EEEE = 0060: wait for 60s before replying (useful to test a timeout)
EEEE = 0080: wait for 80s before replying (useful to test a timeout)
EEEE = 0010: reply ER0010 unknown user
Other: reply OK

--
on TEWS/credit request: format: XXXSSEEEE

If XXX = 060: wait 60s before replying.
If XXX = 080: wait 80s before replying.
Otherwise, no wait.

Replies:

cash legacy (secret code):
SEEEE = 01001: cash legacy: OK response with a VSF 2390.500 (secret code)
SEEEE = 01002: ER0009 on first TEWS/credit, then complete OK on TEWS/credit retransmission with a VSF 2390.500
SEEEE = 01003: provisional response with a VSF 2390.500, then complete OK on TEWS/status

cash standard (secret code):
SEEEE = 11001: cash standard: provisional response with VSF 2390.500, then complete on TEWS/status
SEEEE = 11002: cash standard: ER0009 on first TEWS/credit, then provisional response with VSF 2390.500 on next TEWS/credit retransmission, then complete on TEWS/status
SEEEE = 10EEE: cash standard: provisional response with VSF 2390.500, then reject with 0EEE on TEWS/status
SEEEE = 41001: cash standard: provisional response with VSF 2390.500 with long completiondate (700 sec), then complete on TEWS/status

ewallet (no secret code):
SEEEE = 21001: ewallet: immediate OK response
SEEEE = 21002: ewallet: ER0009 on first TEWS/credit, then complete OK on TEWS/credit retransmission
SEEEE = 21003: ewallet: provisional response, then complete OK on TEWS/status


For compatibility with some test specifications:
SEEEE = 30009: ER0009 on first TEWS/credit, then complete OK on TEWS/credit retransmission (no VSF 2390.500)
SEEEE = 90000: ER0009 on first TEWS/credit, then complete OK on TEWS/credit retransmission (no VSF 2390.500)
SEEEE = 9EEEE: ER0009 on first TEWS/credit, then reject on EEEE on TEWS/credit retransmission (no VSF 2390.500)

EEEE = 0009: ER0009
EEEE = 0003: ER0003
EEEE = 0013: ER0013
EEEE = 0000: provisional response, then complete on TEWS/status.

default: OK response

For BAN URIs based on 5 last digits of account number.
(BAN=ACCOUNT_NUMBER;BIC)
and for EWALLET URI based on 5 last digits of name
(ewallet:<firstname>.<lastname with 5 trailing digits>;sp=XXXXXX

bank standard :
SEEEE = 11001: bank standard: provisional response without any VSF, then complete on TEWS/status
SEEEE = 11003: bank standard for cash out: provisional response with VSF 2390.500, then complete on TEWS/status
SEEEE = 11002: bank standard: ER0009 on first TEWS/credit, then provisional response without any VSF on next TEWS/credit retransmission, then complete on TEWS/status
SEEEE = 11004: bank standard: synchronous response without any VSF 
SEEEE = 11005: bank standard: synchronous response with VSF  2390.500
SEEEE = 10EEE: bank standard: provisional response without any VSF, then reject with 0EEE on TEWS/status
SEEEE = 20EEE: bank standard: provisional response with VSF 2390.500, then reject with 0EEE on TEWS/status

default behaviour : provisional response OK then completed on TEWS/status


"""


##

u"""
SUT URL: /
"""
#enable_debug_logs()

import homesend.iot.api_2_3.tews as TEWS
import xml.dom.minidom 
import libxml2
import base64
import xml.etree.ElementTree as xmltree
from M2Crypto import EVP, RSA, X509, BIO, SMIME
import binascii
import datetime
from xml.sax.saxutils import escape
import OpenSSL
import OpenSSL.crypto
from OpenSSL.crypto import PKCS7Type, load_pkcs7_data, verify
import random
import terminating_moneysend_2_0_for_COB as TMS



pemCertificate="""-----BEGIN CERTIFICATE-----
MIIBkDCB+gIJAJZ4tGktGk/TMA0GCSqGSIb3DQEBBQUAMA0xCzAJBgNVBAYTAkZS
MB4XDTEyMDUyOTEyNTgyMVoXDTEyMDYyODEyNTgyMVowDTELMAkGA1UEBhMCRlIw
gZ8wDQYJKoZIhvcNAQEBBQADgY0AMIGJAoGBAMUOEK2o7IO57A3b7oFi5ZSU1Tc7
JjAEmwoLHpgrvJ8XGj2hhKJv25ePgsjnjMYnLsq/dUCinl9RNlLlmuhWwQUeQJPN
Ep4sauNd0RjiA3ALLtFgAtZ71IW/WA8+7+1S4QimUW5eSgjaTnkptgSCCyzGJO0U
YFF08KM6HxP7p1bpAgMBAAEwDQYJKoZIhvcNAQEFBQADgYEAAICW59JjdKjRSbm5
NENGpY3ipKlaEfUgZVXkVLxYjSTGIu6v8PZzMr28zfVCQnbeqLUz4ZlooDMXII2g
MHRgQ4aU/XyufldrrKCpx6uFbn5e+1JeYOjFK+JCcUPQeC5/+2CjcmUm97ydwH+x
GPEZ++2ZQCJ7j7WBgfBh0XLFvj8=
-----END CERTIFICATE-----"""

pemKey = """-----BEGIN RSA PRIVATE KEY-----
MIICXwIBAAKBgQDFDhCtqOyDuewN2+6BYuWUlNU3OyYwBJsKCx6YK7yfFxo9oYSi
b9uXj4LI54zGJy7Kv3VAop5fUTZS5ZroVsEFHkCTzRKeLGrjXdEY4gNwCy7RYALW
e9SFv1gPPu/tUuEIplFuXkoI2k55KbYEggssxiTtFGBRdPCjOh8T+6dW6QIDAQAB
AoGBAI3KWhvrQgxi2sT6LPsy40lvcqBkUk0Y80pdx+ztA7Nh10LjluGfJV5AKHZR
js0CYrwG2eLhYJ3rfPBXQIjP6+Bz1EebcQrFP55oDgV0SsEzycbrJQFDCgIz/mgK
0BPmwTWoSBIgdqetWaLzo13OkR05GI5fJkEPoOMlmN6y5IqRAkEA8a8n1BzTEeKa
HlrwxSBYLJDSKnjkPe9dyyL7pipXC6UlQ5haspdyAgwldxc7uMy44fHk6DXWB/MT
ourY4N5UBQJBANC6KV6ekHTCn+FlhqE55oaCiOsy8bF4W9MtDB7LVmkrALgy69UJ
xH6Uw+E6p8p+M+hsjpq5Eg+tYW70q5wZsJUCQQCYoPEaN4nkhaKnAO+EzkRhAKR5
Rhd+NaiaHOGnsp1+MTEzWwgMOTA6sskGSJnivwcTSdwx+a3NH2mLPZzxhfaxAkEA
h0zFWFJMrYMjhEX9eTFBH1wqSNvjE/lC/KasvqFsSAvaEYzgll4Ygz0HpE4TSg14
tGb6IY1qCcOH7xamzy9P6QJBAKAiDbjqsDurtvkM/3ATnB0b594FKnm0yiHVSvyX
cisXdVwQcpggJExI+FM7mtDa0JGxuPoqFrzkUm8JW3i7Txs=
-----END RSA PRIVATE KEY-----"""



pemPubKey="""-----BEGIN PUBLIC KEY-----
MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQClgedkBYFL3wpFrrpEmGQTQf1p
pFt7HhGibfwufGTmciWikmtKYhk/jthQo1iSETKnOZup6G0LRS0j3jCdkWTt5AJA
gtYWaYKhB7XPhXQID26Bv/ob59eg7N7iOAShSLiS6gpfjUNIAAzuwkb/vKjBrmac
iyUXWtKh2xJ6eZzBOwIDAQAB
-----END PUBLIC KEY-----"""		

testVar=False

def t_wait(duration = 1.0):
	t = Timer(duration, name = "wait")
	t.start()
	t.timeout()


def generateSignature(stringToSign):
#		log("creating Signature" )		
		buf = BIO.MemoryBuffer(stringToSign)
		smime = SMIME.SMIME()
		bioKey = BIO.MemoryBuffer(pemKey)
		bioCertificate = BIO.MemoryBuffer(pemCertificate)
		smime.load_key_bio(bioKey,bioCertificate)
		p7 = smime.sign(buf)
		out = BIO.MemoryBuffer()
		p7.write(out)

		buf = out.read()
		encodedSignature=buf[len('-----BEGIN PKCS7-----'):-len('-----END PKCS7-----\n')]
		return encodedSignature
		
def verifySignature(stringToVerify,signature):
#	log("checking signature")
	s = SMIME.SMIME()
	bioCertificate = BIO.MemoryBuffer(pemCertificate)
	x509 = X509.load_cert_bio(bioCertificate)
	sk = X509.X509_Stack()
	sk.push(x509)
	s.set_x509_stack(sk)
	st = X509.X509_Store()
	#st.load_info('ca.pem')
	s.set_x509_store(st)

	biop7=BIO.MemoryBuffer(signature)
	
#	p7, data = SMIME.smime_load_pkcs7_bio(biop7)
#	assert data.read() == self.cleartext
#	assert isinstance(p7, SMIME.PKCS7), p7
#	v = s.verify(p7)
#	assert v == self.cleartext
	
	contactWSCertificate = X509.load_cert_string(pemCertificate,X509.FORMAT_PEM)
	pubkey = contactWSCertificate.get_pubkey()
	pubkey.reset_context(md="sha1")
	pubkey.verify_init()
	pubkey.verify_update(stringToVerify)
	
	log("signature verification=%s" % (pubkey.verify_final(signature) == 1))
	
	bio = BIO.MemoryBuffer(pemPubKey)
	rsa = RSA.load_pub_key_bio(bio)
	pubkey = EVP.PKey()
	pubkey.assign_rsa(rsa)
	# if you need a different digest than the default 'sha1':
#	pubkey.reset_context(md="sha1")
#	pubkey.verify_init()
#	pubkey.verify_update(stringToVerify)
#	log("verification = %s" % (pubkey.verify_final(signature) == 1))
	
	

def generateXml(ppCode,payload,signature):
		# Time calculation
		
		format = "%Y-%m-%dT%H:%M:%S"		
		hours, remainder = divmod(time.timezone, 3600) 
		minutes, seconds = divmod(remainder, 60)   
		timezone_formatted = "%s%02d:%02d" % (((hours<0) and "-" or "+"),abs(hours), minutes) 		
		timestamp="%s%s" % (datetime.datetime.today().strftime(format),timezone_formatted)
		
		
		inXmlFormat='''<?xml version =\"1.0\" standalone=\"yes\"?><CDTRN Version=\"1\" PPCode=\"%s\" Code=\"BASE64\" Lang=\"en\" Stamp=\"%s\"><DATA Pack=\"NONE\" Encryption=\"PLAIN\">%s</DATA><SIGNATURES><SIGNATURE ALGO=\"RSA\">%s</SIGNATURE></SIGNATURES></CDTRN>'''
		inXml=inXmlFormat % (ppCode,timestamp,payload,signature)
				
		escapedXml=escape(inXml)
		outXml='''<?xml version="1.0"?><env:Envelope xmlns:env="http://schemas.xmlsoap.org/soap/envelope/" xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:ns0="urn:TransmitterIntf-ITransmitter"><env:Body><ns0:Transmit env:encodingStyle="http://schemas.xmlsoap.org/soap/encoding/"><inXML xsi:type="xsd:string">%s</inXML><outXML xsi:type="xsd:string">%s</outXML></ns0:Transmit></env:Body></env:Envelope>''' % (escapedXml,escapedXml)
		outXml='''<?xml version="1.0"?><SOAP-ENV:Envelope xmlns:SOAP-ENV="http://schemas.xmlsoap.org/soap/envelope/" xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:SOAP-ENC="http://schemas.xmlsoap.org/soap/encoding/"><SOAP-ENV:Body SOAP-ENC:encodingStyle="http://schemas.xmlsoap.org/soap/envelope/"><NS1:TransmitResponse xmlns:NS1="urn:TransmitterIntf-ITransmitter"><return xsi:type="xsd:int">0</return><outXML xsi:type="xsd:string">%s</outXML></NS1:TransmitResponse></SOAP-ENV:Body></SOAP-ENV:Envelope>'''  % (escapedXml)


		return outXml
		

def createGenericRusslavResponse(ppCode,response,id):
		newOutgoingResponseFormat='<RESPONSE RE="%s" ID="%s" />'
		newOutgoingResponse= newOutgoingResponseFormat % (response,id)
		log("response = %s " % newOutgoingResponse)
		encodedPayload=base64.b64encode(newOutgoingResponse)
		encodedSignature=generateSignature(newOutgoingResponse)
		xmlResponse=generateXml(ppCode,encodedPayload,encodedSignature)
		return xmlResponse

def createNewOutgoinRusslavResponse(ppCode,response):
		docId="%s" % (random.randint(1,100000))
		trnReference="%s" % (random.randint(1,100))
		newOutgoingResponseFormat='<RESPONSE RE="%s" ID="%s" trnReference="%s" />'
		newOutgoingResponse= newOutgoingResponseFormat % (response,docId,trnReference)
		log("response = %s " % newOutgoingResponse)
		encodedPayload=base64.b64encode(newOutgoingResponse)
		encodedSignature=generateSignature(newOutgoingResponse)
		xmlResponse=generateXml(ppCode,encodedPayload,encodedSignature)
		return xmlResponse,docId


def createGetStateResponse(ppCode,response,id, state):
		getStateResponseFormat='<RESPONSE RE="%s" ID="%s" STATE="%s" />'
		getStateResponse= getStateResponseFormat % (response,id,state)
		log("response = %s " % getStateResponse)
		encodedPayload=base64.b64encode(getStateResponse)
		encodedSignature=generateSignature(getStateResponse)
		xmlResponse=generateXml(ppCode,encodedPayload,encodedSignature)
		return xmlResponse

def decodeRusslavFrame(russlavFrame):
		beneficiaryName=""
		docId=0
		newDoc=libxml2.parseDoc(russlavFrame)
		root = newDoc.getRootElement()
		child=root.children
		while child is not None:
			if child.name == 'DATA':
				dataElement=child.content
			if child.name == 'SIGNATURES':
				signature64=child.content
				signatureElement=base64.b64decode(child.content)
			child=child.next
	
		for property in root.properties:
			if property.type=='attribute':
				# do something with the attributes
				if property.name=='PPCode':
					ppCode=property.content
		newDoc.freeDoc()
		
		decodedContent=base64.b64decode(dataElement)
		log("incoming content= %s" % decodedContent)
		verifySignature(decodedContent,signature64)
		
		dataDoc=libxml2.parseDoc(decodedContent)		
		root = dataDoc.getRootElement()
		for property in root.properties:
			if property.type=='attribute':
				# do something with the attributes
				if property.name=='ACTION':
					action=property.content
				if property.name=='DOC_ID':
					docId=property.content

		if not docId == 0:
			child=root.children
			while child is not None:
#				log("%s=%s" % (child.name,child.content))
				if child.name == 'bLastName':
					beneficiaryName=child.content
				child=child.next
				
		return action, ppCode, docId, beneficiaryName



# -------------------------------------------------8<-------------------------------------------------
class BEHAVIOR_TEWS_SERVER_PROCESSED_REPLIER(Behaviour):
	"""
	PTC : Wait & Answer to AccountInfoRequest & CreditRequest with dedicated Responses (according to Requests)
	
	Runs on ComponentType {
		TcpPortType tews_port; // with autoconnection and no TCP notifications, and default http.request/response decoder/encoder.
	}
	
	This behaviour simulates a complex TEWS server that
	replies different currency to accountInfo according to destinationUri pattern and to credit requests.
	"""
	def body(self, currency_map = {}, country_map= {}, default_currency = "EUR" ):
		tews = self['tews_port']
		
		terminatingTransactionId = StateManager("testerman-t-%s" % time.time())
		
		# This map contains the transactions for which we replied a provisional response,
		# and which needs to be rejected on TEWS/status with the given code.
		self.registeredTransactionsToReject = {} # map[hsTransactionId] = dict(code = ERxxxx)
		
		# Register seen transactions for which we replied with a ER0009
		self.registeredAmbiguousTransactions = {} # map[hsTransactionId] = dict()
		
		# Register russlav cancelled transactions
		self.registeredCancelledTransactions = {} # map[hsTransactionId] = dict()

		self.testVar = False
		
		# -----------------------------------8<-----------------------------------
		# Process AccountInformationRequest :
		# - Wait 60 or 80sec, before sending AccountInfoResponse if destURI ends with 0030 or 0060 or 0080
		# - Return in AccountInfoResponse, currency = EUR if destinationUri pattern = +32
		# - Return in AccountInfoResponse, currency = PHP if destinationUri pattern = +63
		# -----------------------------------8<-----------------------------------		
		
		def handleAccountInfo():
			dest = value('destinationUri')
			scheme = dest.split(':')[0]
			destinationUri = value('destinationUri')
			log("scheme=%s" % scheme)
			if scheme == 'tel':
				handleAccountInfoURI(destinationUri)
				return
			if scheme == 'iban':
				handleAccountInfoURI(destinationUri)
				return
			if scheme == 'ewallet':
				destinationUri = value('destinationUri')
				#ewallet:user;sp=*
				destinationUri = dest.split(';')[0]			
				log("destination=%s" % destinationUri)
				handleAccountInfoURI(destinationUri)
				return
			elif scheme == 'ban':
				destinationUri = value('destinationUri')
				#ewallet:user;sp=*
				destinationUri = dest.split(';')[0]			
				log("destination=%s" % destinationUri)
				handleAccountInfoURI(destinationUri)
				return
			elif scheme == 'mahstoken':
				destinationUri = value('destinationUri')
				requestId = dest.split('r=')[1].split(';t=')[0]
				destinationUri="mahstoken:"+requestId
				log("MAHSTOKEN dest=%s" % value('destinationUri'))
				handleAccountInfoURI(destinationUri)
				return
			else:
				log("Unsupported URI scheme on Account Info (scheme=%s)" % scheme)
				tews.send({'status': 500, 'reason': 'Internal Server Error', 'headers': {'Content-Type': 'text/xml', 'Connection': 'close'}, 'body': TEWS.m_tews_terminatingService_exception(transactionId = value('transactionId'), terminatingTransactionId = value('terminatingTransactionId'), code = 'ER0010', message = 'Unsupported URI scheme') })
				return


		
		
		# -----------------------------------8<-----------------------------------
		# Process AccountInformationRequest :
		# - Wait 60 or 80sec, before sending AccountInfoResponse if destURI ends with 0030 or 0060 or 0080
		# - Return in AccountInfoResponse, currency = EUR if destinationUri pattern = +32
		# - Return in AccountInfoResponse, currency = PHP if destinationUri pattern = +63
		# -----------------------------------8<-----------------------------------
		def handleAccountInfoURI(destinationURI=any()):
			terminatingTransactionId.set("testerman-t-%s" % time.time())
#			dest = value('destinationUri')
			dest=destinationURI
			log("dest=%s" % (dest))
			
			
			#dest=dest.split(".")[1]
			
			
			scenarioSwitch = dest[-8:-7] 
			delaySwitch = dest[-7:-6] 
			panCurrencyPrefix=dest[-11:-8]
			log("scenario=%s delay=%s" % (scenarioSwitch,delaySwitch))
			
			#if dest.startswith('mahs'):
				# this is the common section which should apply to all scheme, "else" section should be removed
			if delaySwitch == "1":
				log("TEWS/accountInformation 30 sec. timeout response (start timeout)")
				time.sleep(30)
				log("TEWS/accountInformation 30 sec. timeout response (end timeout = send AccountInfoRresponse now...)")
			elif delaySwitch == "2":
				log("TEWS/accountInformation 60 sec. timeout response (start timeout)")
				time.sleep(60)
				log("TEWS/accountInformation 60 sec. timeout response (end timeout = send AccountInfoRresponse now...)")
			elif delaySwitch == "3":
				log("TEWS/accountInformation 80 sec. timeout response (start timeout)")
				time.sleep(80)
				log("TEWS/accountInformation 80 sec. timeout response (end timeout = send AccountInfoRresponse now...)")
			elif delaySwitch == "4":
				log("TEWS/accountInformation 120 sec. timeout response (start timeout)")
				time.sleep(120)
				log("TEWS/accountInformation 120 sec. timeout response (end timeout = send AccountInfoRresponse now...)")
				
			if scenarioSwitch == "0":
				error=dest[-4:]
				log("error case for AI: %s" % error)
				tews.send( {'status': 500, 'reason': 'Internal server error', 'headers': {'Content-Type': 'text/xml', 'Connection': 'close'}, 
					'body': TEWS.m_tews_terminatingService_exception(
						transactionId = value('transactionId'), terminatingTransactionId = value('terminatingTransactionId'),
						code = 'ER%s' % error, message = '')}, to = sender('tews_client')),
				log("TEWS/accountInformation ER%s reponse sent" % error)
				return
			#else:
				
				# Depending on the last 4 digits of the destination, behaves differently.
				#
				# suffix:
				# 0030: sleep for 30s
				# 0060: sleep for 60s
				# 0080: sleep for 80s
				# 0120: sleep for 120s
				# 0180: sleep for 180s
				# 0010: returns ER0010 (Unknown user)
				# Default:
				# Send a response (always OK), with a Currency that depends from the dest prefix.
				# -------8<-------
				# Simulate "timeout" for AccountInfoResponse
				
				
#				if dest.endswith('0030'):
#					# if destURI ends with 0060, sleep 60sec.
#					log("TEWS/accountInformation 30sec. timeout response (start timeout)")
#					time.sleep(30)
#					log("TEWS/accountInformation 30sec. timeout response (end timeout = send AccountInfoRresponse now...)")
#				if dest.endswith('0060'):
#					# if destURI ends with 0060, sleep 60sec.
#					log("TEWS/accountInformation 60sec. timeout response (start timeout)")
#					time.sleep(60)
#					log("TEWS/accountInformation 60sec. timeout response (end timeout = send AccountInfoRresponse now...)")
#				elif dest.endswith('0080'):
#					# if destURI ends with 0080, sleep 80sec.
#					log("TEWS/accountInformation 80sec. timeout response (start timeout)")
#					time.sleep(80)
#					log("TEWS/accountInformation 80sec. timeout response (end timeout = send AccountInfoRresponse now...)")
#				elif dest.endswith('0120'):
#					# if destURI ends with 0120, sleep 120sec.
#					log("TEWS/accountInformation 120sec. timeout response (start timeout)")
#					time.sleep(120)
#					log("TEWS/accountInformation 120sec. timeout response (end timeout = send AccountInfoRresponse now...)")
#				elif dest.endswith('0180'):
#					# if destURI ends with 0120, sleep 180sec.
#					log("TEWS/accountInformation 180sec. timeout response (start timeout)")
#					time.sleep(180)
#					log("TEWS/accountInformation 120sec. timeout response (end timeout = send AccountInfoRresponse now...)")
#				elif dest.endswith('0099'):
#					tews.send( {'status': 500, 'reason': 'Internal server error', 'headers': {'Content-Type': 'text/xml', 'Connection': 'close'}, 
#						'body': TEWS.m_tews_terminatingService_exception(
#							transactionId = value('transactionId'), terminatingTransactionId = value('terminatingTransactionId'),
#							code = 'ER0002', message = 'Service unathorized')}, to = sender('tews_client')),
#					log("TEWS/accountInformation ER0001 reponse sent")
#					return
#				elif dest.endswith('0010'):
#					tews.send( {'status': 500, 'reason': 'Internal server error', 'headers': {'Content-Type': 'text/xml', 'Connection': 'close'}, 
#						'body': TEWS.m_tews_terminatingService_exception(
#							transactionId = value('transactionId'), terminatingTransactionId = value('terminatingTransactionId'),
#							code = 'ER0010', message = 'Unknown Subscriber')}, to = sender('tews_client')),
#					log("TEWS/accountInformation ER0010 reponse sent")
#					return
#				elif dest.endswith('0037'):
#					tews.send( {'status': 500, 'reason': 'Internal server error', 'headers': {'Content-Type': 'text/xml', 'Connection': 'close'}, 
#						'body': TEWS.m_tews_terminatingService_exception(
#							transactionId = value('transactionId'), terminatingTransactionId = value('terminatingTransactionId'),
#							code = 'ER0037', message = 'missing field')}, to = sender('tews_client')),
#					log("TEWS/accountInformation ER0037 reponse sent")
#					return
#				else:
#					# else, continue...
#					log("TEWS/accountInformation no Timeout defined : 'immediate' continue.")


			# Get the currency from the map
			currency = default_currency
			for prefix, cur in currency_map.items():
				if dest.startswith('tel:+%s' % prefix):
					currency = cur
					break
				if dest.startswith('ban:%s' % prefix):
					currency = cur
					break
				if dest.startswith('iban:%s' % prefix):
					currency = cur
					break
				if dest.startswith('ewallet:%s' % prefix):
					currency = cur
					break
				if panCurrencyPrefix.startswith('%s' % prefix.zfill(3)):
					log("prefix=%s dest=%s" % (prefix.zfill(3),panCurrencyPrefix))
					currency = cur
					break

			log("TEWS/accountInformation: selected currency for %s: %s" % (dest, currency))
			tews.send( {'status': 200, 'reason': 'OK', 'headers': {'Content-Type': 'text/xml', 'Connection': 'close'}, 'body': TEWS.m_tews_accountInformation_response(transactionId = value('transactionId'), terminatingTransactionId = terminatingTransactionId.get(), currency = currency,secondaryCurrencies=["GBP"])}, to = sender('tews_client'))
			log("TEWS/accountInformation OK reponse sent, currency %s" % currency)



		def handlePanEligibilityRequest():
			log("handlePanEligibilityRequest")
										
			subscriberId = value('subscriberId')
			
			log("subscriberId=%s" % subscriberId)
			requestId = "1234"
			
			
			dest=subscriberId.split("r=")[1][8:19]
			log("	destinationUri = %s" % dest)
			transactionId = value('transactionId')
			
			errorCode= dest[-2:]
			
			scenarioSwitch = dest[-8:-7] 
			delaySwitch = dest[-7:-6] 
			panCurrencyPrefix=dest[-11:-8]
			log("scenario=%s delay=%s panCurrencyPrefix=%s" % (scenarioSwitch,delaySwitch,panCurrencyPrefix))

			
			log("TMS/Payment request received %s, %s" % (subscriberId,requestId) )	
	
	
			if delaySwitch == "1":
				log("TMS/PanEligibility 30 sec. timeout response (start timeout)")
				time.sleep(30)
				log("TMS/PanEligibility 30 sec. timeout response (end timeout = send AccountInfoRresponse now...)")
			elif delaySwitch == "2":
				log("TMS/PanEligibility 60 sec. timeout response (start timeout)")
				time.sleep(60)
				log("TMS/PanEligibility 60 sec. timeout response (end timeout = send AccountInfoRresponse now...)")
			elif delaySwitch == "3":
				log("TMS/PanEligibility 80 sec. timeout response (start timeout)")
				time.sleep(80)
				log("TMS/PanEligibility 80 sec. timeout response (end timeout = send AccountInfoRresponse now...)")
			elif delaySwitch == "4":
				log("TMS/PanEligibility 120 sec. timeout response (start timeout)")
				time.sleep(120)
				log("TMS/PanEligibility 120 sec. timeout response (end timeout = send AccountInfoRresponse now...)")
			
			if scenarioSwitch == "0":
				error=dest[-4:]
				log("error case for AI: %s" % error)
				aoc = TMS.m_tms_error(requestId = requestId, reasonCode = "DECLINE", responseCode = errorCode, responseDescription = "DECLINE")		
				log("Sending a TMS/error %s (%s)..." % (errorCode, "DECLINE"))
				tews.send( {'status': 500, 'reason': 'OK', 'headers': {'Content-Type': 'text/xml', 'Connection': 'close'}, 'body': aoc }, to = sender('last_client'))
			
				
				log("TEWS/accountInformation ER%s reponse sent" % error)
				return

			
			
						# Get the currency from the map
			currency = default_currency
			country = "USA"
			for prefix, cur in country_map.items():
				if panCurrencyPrefix.startswith('%s' % prefix.zfill(3)):
					log("prefix=%s dest=%s" % (prefix.zfill(3),panCurrencyPrefix))
					country = cur
					break
			currencyCode="USD"
			for prefix, cur in currency_map.items():
				if panCurrencyPrefix.startswith('%s' % prefix.zfill(3)):
					log("prefix=%s dest=%s" % (prefix.zfill(3),panCurrencyPrefix))
					currencyCode = cur
					break

			log("country=%s" % country)

			##
			# TMS/PanEligibility response <-
			##
			requestId = random.randint(0,999999)
			networkPrimaryKey="USA"
			alphaCountryCode="USA"
			body = TMS.m_tms_PanEligibility_response(requestId = requestId, networkPrimaryKey = country, alphaCurrencyCode = currencyCode,alphaCountryCode = country)
			log("sending TMS/PanElligibility response ok...")			
			tews.send( {'status': 200, 'reason': 'OK', 'headers': {'Content-Type': 'text/xml', 'Connection': 'close'}, 'body': body }, to = sender('tews_client'))
			log("... TMS/PanElligibility response ok sent")			


			

		def handlePaymentRequest():

			subscriberId = value('subscriberId')
			subscriberType = value('subscriberType')		
			transactionReference = value('transactionReference')	
			requestId = "1234"
			laDate = value('localDate')	
			submitDateTime = value('localTime')	
			log("TMS/Payment request received %s, %s %s %s" % (subscriberId, subscriberType,transactionReference,requestId) )	
	
	
	
			
			
			dest=subscriberId
			sample=dest.split("r=")
			log("%s dest=%s" % (sample[1],sample[1][8:19]))
			dest=sample[1][8:19]
			log("	destinationUri = %s" % dest)
			transactionId = value('transactionId')
			
			completionDate = [0,20, 80, 120, 300,600]
			
			scenarioSwitch = dest[-8:-7] 
			delaySwitch = dest[-6:-5] 
			log("3")
			maxCompletionDate = completionDate[int(dest[-5:-4])]
			errorCode= dest[-2:]
			systemTraceAuditNumber = random.randint(0,999999)
			now = datetime.datetime.utcnow()                
			submitDateTime = now.strftime("%Y-%m-%dT%H:%M:%SZ")
			systemTraceAuditNumber="22"
			
			log("handlePaymentRequest scenario=%s delay=%s MaxCompletionDate=%s error=%s" % (scenarioSwitch,delaySwitch,maxCompletionDate,errorCode))
			
			if delaySwitch == "1":
				log("TEWS/CreditRequest 30 sec. timeout response (start timeout)")
				time.sleep(30)
				log("TEWS/CreditRequest 30 sec. timeout response (end timeout = send CreditRequest now...)")
			elif delaySwitch == "2":
				log("TEWS/CreditRequest 60 sec. timeout response (start timeout)")
				time.sleep(60)
				log("TEWS/CreditRequest 60 sec. timeout response (end timeout = send CreditRequest now...)")
			elif delaySwitch == "3":
				log("TEWS/CreditRequest 80 sec. timeout response (start timeout)")
				time.sleep(80)
				log("TEWS/CreditRequest 80 sec. timeout response (end timeout = send CreditRequest now...)")
			elif delaySwitch == "4":
				log("TEWS/CreditRequest 120 sec. timeout response (start timeout)")
				time.sleep(120)
				log("TEWS/CreditRequest 120 sec. timeout response (end timeout = send CreditRequest now...)")
			else:
					log("TEWS/CreditRequest no Timeout defined : 'immediate' continue.")
				
			secretCode = ("%s" % time.time()).split('.')[1]

			# Provisional response (TEWS/status are always replied with OK)
			now = datetime.datetime.utcnow()
			# 20s by default for the max completion date
			defaultMaxCompletionDate = now + datetime.timedelta(seconds = maxCompletionDate)
			deadline = defaultMaxCompletionDate.strftime("%Y-%m-%dT%H:%M:%SZ")
			
			if (scenarioSwitch == "1"):
				# Synchronous OK response
				log("scenario 1")
				body = TMS.m_tms_payment_response(requestId = requestId, transactionReference = transactionReference, systemTraceAuditNumber = systemTraceAuditNumber,
					settlementDate = laDate, submitDateTime = submitDateTime)               
				tews.send( {'status': 200, 'reason': 'OK', 'headers': {'Content-Type': 'text/xml', 'Connection': 'close'}, 'body': body }, to = sender('last_client'))
			
				log("TEWS/credit OK response sent")

			elif (scenarioSwitch == "2"):
				# Synchronous NOK response
				log("scenario 2")
				body = TMS.m_tms_error(requestId = requestId, responseCode = errorCode, responseDescription = "DECLINE")		
			
				log("Sending a TMS/error %s (%s)..." % (errorCode, "DECLINE"))
				tews.send( {'status': 500, 'reason': 'OK', 'headers': {'Content-Type': 'text/xml', 'Connection': 'close'}, 'body': body }, to = sender('last_client'))
		
				log("TEWS/credit NOK response ER%s " % errorCode)

			elif (scenarioSwitch == "3"):
				# Asynchronous OK response
				log("scenario 3")
				body = TMS.m_tms_payment_response(requestId = requestId, transactionReference = transactionReference, systemTraceAuditNumber = systemTraceAuditNumber,
					settlementDate = laDate, submitDateTime = submitDateTime)               
				tews.send( {'status': 200, 'reason': 'OK', 'headers': {'Content-Type': 'text/xml', 'Connection': 'close'}, 'body': body }, to = sender('last_client'))
			
				log("TEWS/credit provisional response for a future accepted transaction, with maxCompletionDate = %s" % (deadline))


			elif (scenarioSwitch == "4"):
				# Asynchronous NOK response
				log("scenario 4")
				body = TMS.m_tms_payment_response(requestId = requestId, transactionReference = transactionReference, systemTraceAuditNumber = systemTraceAuditNumber,
					settlementDate = laDate, submitDateTime = submitDateTime)               
				tews.send( {'status': 200, 'reason': 'OK', 'headers': {'Content-Type': 'text/xml', 'Connection': 'close'}, 'body': body }, to = sender('last_client'))

				log("TEWS/credit provisional response for a future rejected transaction, maxCompletionDate = %s" % (deadline))
			
			elif (scenarioSwitch == "5"):
				# Cash OK response
				blog("scenario 5")
				ody = TMS.m_tms_payment_response(requestId = requestId, transactionReference = transactionReference, systemTraceAuditNumber = systemTraceAuditNumber,
					settlementDate = laDate, submitDateTime = submitDateTime)               
				tews.send( {'status': 200, 'reason': 'OK', 'headers': {'Content-Type': 'text/xml', 'Connection': 'close'}, 'body': body }, to = sender('last_client'))
			
				log("TEWS/credit provisional response for a future accepted transaction, with maxCompletionDate = %s" % (deadline))
				
			elif (scenarioSwitch == "6"):
				# Cash NOK response
				log("scenario 6")
				body = TMS.m_tms_payment_response(requestId = requestId, transactionReference = transactionReference, systemTraceAuditNumber = systemTraceAuditNumber,
					settlementDate = laDate, submitDateTime = submitDateTime)               
				tews.send( {'status': 200, 'reason': 'OK', 'headers': {'Content-Type': 'text/xml', 'Connection': 'close'}, 'body': body }, to = sender('last_client'))
		
				log("TEWS/credit provisional response for a future rejected transaction, with secret code %s, maxCompletionDate = %s" % (secretCode, deadline))
	
			else:
				# CreditResponse: OK
				# Always send a transaction code
				log("scenario default")
				vsfs = [ (2390, 500, ("%s" % time.time()).split('.')[1]  ) ]
				body = TMS.m_tms_payment_response(requestId = requestId, transactionReference = transactionReference, systemTraceAuditNumber = systemTraceAuditNumber,
					settlementDate = laDate, submitDateTime = submitDateTime)               
				tews.send( {'status': 200, 'reason': 'OK', 'headers': {'Content-Type': 'text/xml', 'Connection': 'close'}, 'body': body }, to = sender('last_client'))
			
				log("TEWS/credit OK reponse sent")
	
			


			##      
			# -> TMS/payment response OK
			##              
			log("Sending a TMS/payment response ...")





		def handleCreditRequest():
			dest = value('destinationUri')
			log("destinationUri=%s" % dest)
			scheme = dest.split(':')[0]
			destinationUri = value('destinationUri')
			log("scheme=%s" % scheme)
			
			if scheme == 'tel':
				handleCreditRequestNew(destinationUri)
#				handleCreditRequest_tel(destinationUri)
				return
			if scheme == 'mahstoken':
#				destinationUri = value('destinationUri')
#				destinationUri="mahstoken:"+destinationUri[15:18]+destinationUri[28:47]
				
				requestId = dest.split('r=')[1].split(';t=')[0]
				destinationUri="mahstoken:"+requestId
				
				log("MAHSTOKEN dest=%s" % value('destinationUri'))
				handleCreditRequestNew(destinationUri)
				return
			if scheme == 'iban':
				handleCreditRequestNew(destinationUri)
#				handleCreditRequest_tel(destinationUri)
				return
			if scheme == 'ewallet':
				destinationUri = value('destinationUri')
				#ewallet:user;sp=*
				#keeping only the user
				destinationUri = dest.split(';')[0]			
				log("SwitchScheme  destination=%s" % destinationUri)
				handleCreditRequestNew(destinationUri)
#				handleCreditRequest_ban(destinationUri)
				return
			elif scheme == 'ban':
				destinationUri = value('destinationUri')
				#ban:AccountNumber;bic=*
				#keeping only the AccountNumber
				destinationUri = dest.split(';')[0]			
				log("destination=%s" % destinationUri)
				handleCreditRequestNew(destinationUri)
##				handleCreditRequest_ban(destinationUri)
				return
			else:
				log("Unsupported URI scheme on Credit Request (scheme=%s)" % scheme)
				tews.send({'status': 500, 'reason': 'Internal Server Error', 'headers': {'Content-Type': 'text/xml', 'Connection': 'close'}, 'body': TEWS.m_tews_terminatingService_exception(transactionId = value('transactionId'), terminatingTransactionId = value('terminatingTransactionId'), code = 'ER0010', message = 'Unsupported URI scheme') })
				return




		# -----------------------------------8<-----------------------------------
		# Process CreditRequest :
		# - Wait 60sec, before sending creditResponse if destURI ends with 060
		# - Wait 80sec, before sending creditResponse if destURI ends with 080
		# - Return CreditRequest OK, if destinationUri NOT ends with 0009 or 0003
		# - Return CreditRequest Ambiguous, with ER0009 or ER0003, if destinationUri ends with 0009 or 0003
		# -----------------------------------8<-----------------------------------
		def handleCreditRequestNew(destinationURI=any()):
#			dest = value('destinationUri')
			log("handleCreditRequestNew begins")
			dest=destinationURI
			log("handleCreditRequestNew destinationUri=%s" % destinationURI)
			transactionId = value('transactionId')
			
			completionDate = [0,20, 80, 120, 300,600]
			partOfString = dest.split('.')
			stringCount=len(partOfString)
			secondPart=partOfString[0]
			if (stringCount>1):
				secondPart=partOfString[1]
			if (secondPart == " "):
				log("MerchantTrade scheme")
				scenarioSwitch = 1
				delaySwitch = 0 
				maxCompletionDate = 0
				errorCode= 0
			else:
				scenarioSwitch = dest[-8:-7] 
				log("scenario=%s" % scenarioSwitch)
				delaySwitch = dest[-6:-5] 
				log("delaySwitch=%s" % delaySwitch)
				maxCompletionDate = completionDate[int(dest[-5:-4])]
				log("maxCompletionDate=%s" % maxCompletionDate)
				errorCode= dest[-4:]
			log("handleCreditRequestNew scenario=%s delay=%s MaxCompletionDate=%s error=%s" % (scenarioSwitch,delaySwitch,maxCompletionDate,errorCode))
			
			if delaySwitch == "1":
				log("TEWS/CreditRequest 30 sec. timeout response (start timeout)")
				time.sleep(30)
				log("TEWS/CreditRequest 30 sec. timeout response (end timeout = send CreditRequest now...)")
			elif delaySwitch == "2":
				log("TEWS/CreditRequest 60 sec. timeout response (start timeout)")
				time.sleep(60)
				log("TEWS/CreditRequest 60 sec. timeout response (end timeout = send CreditRequest now...)")
			elif delaySwitch == "3":
				log("TEWS/CreditRequest 80 sec. timeout response (start timeout)")
				time.sleep(80)
				log("TEWS/CreditRequest 80 sec. timeout response (end timeout = send CreditRequest now...)")
			elif delaySwitch == "4":
				log("TEWS/CreditRequest 120 sec. timeout response (start timeout)")
				time.sleep(120)
				log("TEWS/CreditRequest 120 sec. timeout response (end timeout = send CreditRequest now...)")
			else:
					log("TEWS/CreditRequest no Timeout defined : 'immediate' continue.")
				
			secretCode = ("%s" % time.time()).split('.')[1]

			# Provisional response (TEWS/status are always replied with OK)
			now = datetime.datetime.utcnow()
			# 20s by default for the max completion date
			defaultMaxCompletionDate = now + datetime.timedelta(seconds = maxCompletionDate)
			deadline = defaultMaxCompletionDate.strftime("%Y-%m-%dT%H:%M:%SZ")
			
			if (scenarioSwitch == "1"):
				# Synchronous OK response
				tews.send( {'status': 200, 'reason': 'OK', 'headers': {'Content-Type': 'text/xml', 'Connection': 'close'}, 
									'body': TEWS.m_tews_credit_response(transactionId = value('transactionId'), 
									terminatingTransactionId = value('terminatingTransactionId'))}, to = sender('tews_client')),
				log("TEWS/credit OK response sent")

			elif (scenarioSwitch == "2"):
				# Synchronous NOK response
				tews.send( {'status': 500, 'reason': 'Internal server error', 'headers': {'Content-Type': 'text/xml', 'Connection': 'close'}, 
								'body': TEWS.m_tews_credit_response_KO(transactionId = value('transactionId'), 
								terminatingTransactionId = value('terminatingTransactionId'), 
								errorValue = 'ER%s' % errorCode, errorDescription = 'Explicit error code' )}, to = sender('tews_client')),
				log("TEWS/credit NOK response ER%s " % errorCode)

			elif (scenarioSwitch == "3"):
				# Asynchronous OK response
				tews.send( {'status': 200, 'reason': 'OK', 'headers': {'Content-Type': 'text/xml', 'Connection': 'close'}, 
						'body': TEWS.m_tews_credit_response(
						transactionId = value('transactionId'), 
						terminatingTransactionId = value('terminatingTransactionId'),
						provisionalResponse = ( deadline, "CreditInProgress", "Credit In Progress" ),
						)}, to = sender('tews_client'))
				log("TEWS/credit provisional response for a future accepted transaction, with maxCompletionDate = %s" % (deadline))


			elif (scenarioSwitch == "4"):
				# Asynchronous NOK response
				tews.send( {'status': 200, 'reason': 'OK', 'headers': {'Content-Type': 'text/xml', 'Connection': 'close'}, 
					'body': TEWS.m_tews_credit_response(
					transactionId = value('transactionId'), 
					terminatingTransactionId = value('terminatingTransactionId'),
					provisionalResponse = ( deadline, "CreditInProgress", "Credit In Progress" ),
					)}, to = sender('tews_client'))
				# Register the transaction so that it can be rejected in a TEWS/status
				self.registeredTransactionsToReject[value('transactionId')] = { 'code': "ER%s" % dest[-4:] }
				log("TEWS/credit provisional response for a future rejected transaction, maxCompletionDate = %s" % (deadline))
			
			elif (scenarioSwitch == "5"):
				# Cash OK response
				tews.send( {'status': 200, 'reason': 'OK', 'headers': {'Content-Type': 'text/xml', 'Connection': 'close'}, 
						'body': TEWS.m_tews_credit_response(
						transactionId = value('transactionId'), 
						terminatingTransactionId = value('terminatingTransactionId'),
						provisionalResponse = ( deadline, "CreditInProgress", "Credit In Progress" ),
						vsfs = [ (2390, 500, secretCode) ], # generate a transaction code
						)}, to = sender('tews_client'))
				log("TEWS/credit provisional response for a future accepted transaction, with maxCompletionDate = %s" % (deadline))
				
			elif (scenarioSwitch == "6"):
				# Cash NOK response
				tews.send( {'status': 200, 'reason': 'OK', 'headers': {'Content-Type': 'text/xml', 'Connection': 'close'}, 
					'body': TEWS.m_tews_credit_response(
					transactionId = value('transactionId'), 
					terminatingTransactionId = value('terminatingTransactionId'),
					provisionalResponse = ( deadline, "CreditInProgress", "Credit In Progress" ),
					vsfs = [ (2390, 500, secretCode) ], # generate a transaction code
					)}, to = sender('tews_client'))
				# Register the transaction so that it canr be rejected in a TEWS/status
				self.registeredTransactionsToReject[value('transactionId')] = { 'code': "ER%s" % dest[-4:] }
				log("TEWS/credit provisional response for a future rejected transaction, with secret code %s, maxCompletionDate = %s" % (secretCode, deadline))
	
			else:
				# CreditResponse: OK
				# Always send a transaction code
				vsfs = [ (2390, 500, ("%s" % time.time()).split('.')[1]  ) ]
				tews.send( {'status': 200, 'reason': 'OK', 'headers': {'Content-Type': 'text/xml', 'Connection': 'close'}, 'body': TEWS.m_tews_credit_response(transactionId = value('transactionId'), terminatingTransactionId = value('terminatingTransactionId'), vsfs = vsfs)}, to = sender('tews_client')),
				log("TEWS/credit OK reponse sent")
	
			return






		# -----------------------------------8<-----------------------------------
		# Process CreditRequest :
		# - Wait 60sec, before sending creditResponse if destURI ends with 060
		# - Wait 80sec, before sending creditResponse if destURI ends with 080
		# - Return CreditRequest OK, if destinationUri NOT ends with 0009 or 0003
		# - Return CreditRequest Ambiguous, with ER0009 or ER0003, if destinationUri ends with 0009 or 0003
		# -----------------------------------8<-----------------------------------
		def handleCreditRequest_tel(destinationURI=any()):
#			dest = value('destinationUri')

			log("handleCreditRequest_tel")
			dest=destinationURI
			transactionId = value('transactionId')
			
			completionDate = [20, 80, 120, 300,600]
			
#			scenarioSwitch = dest[-8:-7] 
#			delaySwitch = dest[-6:-5] 
#			maxCompletionDate = completionDate[int(dest[-5:-4])]
#			error= dest[-4:]
#			log("scenario=%s delay=%s MaxCompletionDate=%s error=%s" % (scenarioSwitch,delaySwitch,maxCompletionDate,error))
#			
				
			# XXXSEEEE with XXX = 060: 60s delay before replying anything
			# XXXSEEEE with XXX = 080: 80s delay before replying anything
			# XXXSEEEE with XXX = 180: 180s delay before replying anything
			if len(dest) > 8 and (dest[-8:-5] == "030" or dest[-8:-5] == "060" or dest[-8:-5] == "080" or dest[-8:-5] == "045" or dest[-8:-5] == "055" or dest[-8:-5] == "180" or dest[-8:-5] == "099"):
				if not transactionId in self.registeredAmbiguousTransactions:
					if (dest[-8:-5] == "030"):
						log("TEWS/credit delayed by 30s")
						self.testVar = True
						t_wait(30.0)
					elif (dest[-8:-5] == "045"):
						log("TEWS/credit delayed by 45s")
						t_wait(45.0)
					elif (dest[-8:-5] == "055"):
						log("TEWS/credit delayed by 55s")
						t_wait(55.0)
					elif (dest[-8:-5] == "031"):
						if self.testVar == False:
							log("TEWS/credit delayed by 30s")
							self.testVar = True
							t_wait(30.0)
					elif (dest[-8:-5] == "099"):
						log("TEWS/credit delayed by 130s")
						t_wait(130.0)
					elif (dest[-8:-5] == "180"):
						log("TEWS/credit delayed by 180s")
						t_wait(180.0)
					elif (dest[-8:-5] == "080"):
						log("TEWS/credit delayed by 80s")
						t_wait(80.0)
					else:
						log("TEWS/credit delayed by 60s for %s" % (dest[-8:-5]))
						t_wait(60.0)						
				else:
					log("Not delaying the TEWS/credit processing again: duplicate request")
	
			secretCode = ("%s" % time.time()).split('.')[1]

			# Provisional response (TEWS/status are always replied with OK)
			now = datetime.datetime.utcnow()
			# 20s by default for the max completion date
			defaultMaxCompletionDate = now + datetime.timedelta(seconds = 20)
			deadline = defaultMaxCompletionDate.strftime("%Y-%m-%dT%H:%M:%SZ")

			# -------8<-------
			# Specific high level behaviours
			
			# S == 0: Web to Cash, legacy
			if dest.endswith('01001'):
				# WEB_TO_CASH_LEGACY:
				# Synchronous response with a VSF secret code
				vsfs = [ (2390, 500, secretCode)  ]
				tews.send( {'status': 200, 'reason': 'OK', 'headers': {'Content-Type': 'text/xml', 'Connection': 'close'}, 'body': TEWS.m_tews_credit_response(transactionId = value('transactionId'), terminatingTransactionId = value('terminatingTransactionId'), vsfs = vsfs)}, to = sender('tews_client')),
				log("TEWS/credit OK response sent, with secret code set to %s" % secretCode)

			elif dest.endswith('01003'):
				# WEB_TO_MOBILE:
				# Synchronous response
				tews.send( {'status': 200, 'reason': 'OK', 'headers': {'Content-Type': 'text/xml', 'Connection': 'close'}, 'body': TEWS.m_tews_credit_response(transactionId = value('transactionId'), terminatingTransactionId = value('terminatingTransactionId'))}, to = sender('tews_client')),
				log("TEWS/credit OK response sent")


			# S == 1: Web to cash:
			elif dest.endswith('11001'):
				# WEB_TO_CASH: 11xxx
				# Asynchronous response with a VSF secret code, then a OK response
				tews.send( {'status': 200, 'reason': 'OK', 'headers': {'Content-Type': 'text/xml', 'Connection': 'close'}, 
					'body': TEWS.m_tews_credit_response(
					transactionId = value('transactionId'), 
					terminatingTransactionId = value('terminatingTransactionId'),
					provisionalResponse = ( deadline, "CreditInProgress", "Credit In Progress" ),
					vsfs = [ (2390, 500, secretCode) ], # generate a transaction code
					)}, to = sender('tews_client'))
				log("TEWS/credit provisional response for a future accepted transaction, with secret code %s, maxCompletionDate = %s" % (secretCode, deadline))


			# S == 4: Web to cash: long MaxCompletionDate
			elif dest.endswith('41001'):
				# Asynchronous response with a VSF secret code, then a OK response
				# Provisional response (TEWS/status are always replied with OK)
				now = datetime.datetime.utcnow()
				# 600s by default for the max completion date
				defaultMaxCompletionDate = now + datetime.timedelta(seconds = 600)
				deadline = defaultMaxCompletionDate.strftime("%Y-%m-%dT%H:%M:%SZ")
				tews.send( {'status': 200, 'reason': 'OK', 'headers': {'Content-Type': 'text/xml', 'Connection': 'close'}, 
					'body': TEWS.m_tews_credit_response(
					transactionId = value('transactionId'), 
					terminatingTransactionId = value('terminatingTransactionId'),
					provisionalResponse = ( deadline, "CreditInProgress", "Credit In Progress" ),
					vsfs = [ (2390, 500, secretCode) ], # generate a transaction code
					)}, to = sender('tews_client'))
				log("TEWS/credit provisional response for a future accepted transaction, with secret code %s, maxCompletionDate = %s (10 minutes)" % (secretCode, deadline))
				
			elif dest.endswith('41002'):
				# Asynchronous response with a VSF secret code, then a OK response
				# Provisional response (TEWS/status are always replied with OK)
				now = datetime.datetime.utcnow()
				# 300s by default for the max completion date
				defaultMaxCompletionDate = now + datetime.timedelta(seconds = 300)
				deadline = defaultMaxCompletionDate.strftime("%Y-%m-%dT%H:%M:%SZ")
				tews.send( {'status': 200, 'reason': 'OK', 'headers': {'Content-Type': 'text/xml', 'Connection': 'close'}, 
					'body': TEWS.m_tews_credit_response(
					transactionId = value('transactionId'), 
					terminatingTransactionId = value('terminatingTransactionId'),
					provisionalResponse = ( deadline, "CreditInProgress", "Credit In Progress" ),
					vsfs = [ (2390, 500, secretCode) ], # generate a transaction code
					)}, to = sender('tews_client'))
				log("TEWS/credit provisional response for a future accepted transaction, with secret code %s, maxCompletionDate = %s" % (secretCode, deadline))

			elif dest.endswith('41003'):
				# Asynchronous response with a VSF secret code, then a OK response
				# Provisional response (TEWS/status are always replied with OK)
				now = datetime.datetime.utcnow()
				# 80s by default for the max completion date
				defaultMaxCompletionDate = now + datetime.timedelta(seconds = 80)
				deadline = defaultMaxCompletionDate.strftime("%Y-%m-%dT%H:%M:%SZ")
				tews.send( {'status': 200, 'reason': 'OK', 'headers': {'Content-Type': 'text/xml', 'Connection': 'close'}, 
					'body': TEWS.m_tews_credit_response(
					transactionId = value('transactionId'), 
					terminatingTransactionId = value('terminatingTransactionId'),
					provisionalResponse = ( deadline, "CreditInProgress", "Credit In Progress" ),
					vsfs = [ (2390, 500, secretCode) ], # generate a transaction code
					)}, to = sender('tews_client'))
				log("TEWS/credit provisional response for a future accepted transaction, with secret code %s, maxCompletionDate = %s" % (secretCode, deadline))

			elif dest.endswith('41004'):
				# Asynchronous response with a VSF secret code, then a OK response
				# Provisional response (TEWS/status are always replied with OK)
				now = datetime.datetime.utcnow()
				# 120s by default for the max completion date
				defaultMaxCompletionDate = now + datetime.timedelta(seconds = 120)
				deadline = defaultMaxCompletionDate.strftime("%Y-%m-%dT%H:%M:%SZ")
				tews.send( {'status': 200, 'reason': 'OK', 'headers': {'Content-Type': 'text/xml', 'Connection': 'close'}, 
					'body': TEWS.m_tews_credit_response(
					transactionId = value('transactionId'), 
					terminatingTransactionId = value('terminatingTransactionId'),
					provisionalResponse = ( deadline, "CreditInProgress", "Credit In Progress" ),
					vsfs = [ (2390, 500, secretCode) ], # generate a transaction code
					)}, to = sender('tews_client'))
				log("TEWS/credit provisional response for a future accepted transaction, with secret code %s, maxCompletionDate = %s" % (secretCode, deadline))

			elif dest.endswith('41005'):
				# Asynchronous response without a VSF secret code, then a OK response
				# Provisional response (TEWS/status are always replied with OK)
				now = datetime.datetime.utcnow()
				# 120s by default for the max completion date
				defaultMaxCompletionDate = now + datetime.timedelta(seconds = 20)
				deadline = defaultMaxCompletionDate.strftime("%Y-%m-%dT%H:%M:%SZ")
				tews.send( {'status': 200, 'reason': 'OK', 'headers': {'Content-Type': 'text/xml', 'Connection': 'close'}, 
					'body': TEWS.m_tews_credit_response(
					transactionId = value('transactionId'), 
					terminatingTransactionId = value('terminatingTransactionId'),
					provisionalResponse = ( deadline, "CreditInProgress", "Credit In Progress" ),
					)}, to = sender('tews_client'))
				log("TEWS/credit provisional response for a future accepted transaction, with maxCompletionDate = %s" % (deadline))



			# S == 1: Web to cash (asynchronous, VSF secret code)
			elif len(dest) > 5 and dest[-5] == '1':
				# WEB_TO_CASH: 10xxx
				# Asynchronous response with a VSF secret code, then a NOK response using the last 4 digits for the rejection code
				tews.send( {'status': 200, 'reason': 'OK', 'headers': {'Content-Type': 'text/xml', 'Connection': 'close'}, 
					'body': TEWS.m_tews_credit_response(
					transactionId = value('transactionId'), 
					terminatingTransactionId = value('terminatingTransactionId'),
					provisionalResponse = ( deadline, "CreditInProgress", "Credit In Progress" ),
					vsfs = [ (2390, 500, secretCode) ], # generate a transaction code
					)}, to = sender('tews_client'))
				# Register the transaction so that it can be rejected in a TEWS/status
				self.registeredTransactionsToReject[value('transactionId')] = { 'code': "ER%s" % dest[-4:] }
				log("TEWS/credit provisional response for a future rejected transaction, with secret code %s, maxCompletionDate = %s" % (secretCode, deadline))
			elif dest.endswith('54321'):
				log("Sending a provisional response, with Unicode, maxCompletionDate = %s" % deadline)
				tews.send( {'status': 200, 'reason': 'OK', 'headers': {'Content-Type': 'text/xml', 'Connection': 'close'}, 
					'body': TEWS.m_tews_credit_response(
					transactionId = value('transactionId'), 
					terminatingTransactionId = value('terminatingTransactionId'),
					provisionalResponse = ( deadline, "CreditInProgress", "Credit In Progress" ),
					vsfs = [ (2390, 600, (u"code pour le b?n?ficiaire" )  ) ], # generate a transaction code
					)}, to = sender('tews_client'))		
			# S == 2: Web to ewallet (synchronous, no VSF secret code)
			elif dest.endswith('21001'):
				# WEB_TO_EWALLET:
				# Synchronous response without VSF secret code
				vsfs = []
				log("case WEB_TO_EWALLET")
				tews.send( {'status': 200, 'reason': 'OK', 'headers': {'Content-Type': 'text/xml', 'Connection': 'close'}, 
									'body': TEWS.m_tews_credit_response(transactionId = value('transactionId'), 
									terminatingTransactionId = value('terminatingTransactionId'), vsfs = vsfs)}, to = sender('tews_client')),
				log("TEWS/credit OK response sent, no secret code")


			# S == 2: Web to ewallet (synchronous, no VSF secret code)
			elif dest.endswith('21002'):
				# WEB_TO_EWALLET:
				# First an ambiguous response, then a OK response without VSF secret code
				vsfs = []
				if not transactionId in self.registeredAmbiguousTransactions:
					tews.send( {'status': 500, 'reason': 'Internal server error', 'headers': {'Content-Type': 'text/xml', 'Connection': 'close'}, 
										'body': TEWS.m_tews_credit_response_KO(transactionId = value('transactionId'), 
											terminatingTransactionId = value('terminatingTransactionId'), errorValue = 'ER0009', 
											errorDescription = 'Ambiguous case (explicit)', vsfs = [ (2390, 500, "Credited user name") ] )}, to = sender('tews_client')),
					log("TEWS/credit ER0009 reponse sent, will provide a OK response on next TEWS/credit retransmission")
					# Register the transaction so that it can be replied later
					self.registeredAmbiguousTransactions[value('transactionId')] = {}
				else:
					# This is a retransmission, provides a OK response if code is 0000
					# or a rejection otherwise
					code = self.registeredAmbiguousTransactions[transactionId].get('code', '0000')
					if code == '0000':
						# OK response
						tews.send( {'status': 200, 'reason': 'OK', 'headers': {'Content-Type': 'text/xml', 'Connection': 'close'}, 'body': TEWS.m_tews_credit_response(transactionId = value('transactionId'), terminatingTransactionId = value('terminatingTransactionId'), vsfs = vsfs)}, to = sender('tews_client')),
						log("TEWS/credit OK response sent after an ER0009 response, no secret code")
					else:
						tews.send( {'status': 500, 'reason': 'Internal server error', 'headers': {'Content-Type': 'text/xml', 'Connection': 'close'}, 'body': TEWS.m_tews_credit_response_KO(transactionId = value('transactionId'), terminatingTransactionId = value('terminatingTransactionId'), errorValue = 'ER%s' % code, errorDescription = 'Explicit error code aver TEWS/credit ambiguous retransmission' )}, to = sender('tews_client')),
						log("TEWS/credit NOK response ER%s sent after an ER0009 response" % code)


			# S == 3: ??
			elif dest.endswith('30009'):
				# First reply a ER0009, and register the transaction for a standard OK response on retransmission
				transactionId = value('transactionId')
				if not transactionId in self.registeredAmbiguousTransactions:
					tews.send( {'status': 500, 'reason': 'Internal server error', 'headers': {'Content-Type': 'text/xml', 'Connection': 'close'}, 'body': TEWS.m_tews_credit_response_KO(transactionId = value('transactionId'), terminatingTransactionId = value('terminatingTransactionId'), errorValue = 'ER0009', errorDescription = 'Ambiguous case (explicit)', vsfs = [ (2390, 500, "Credited user name") ] )}, to = sender('tews_client')),
					log("TEWS/credit ER0009 reponse sent, will provide a OK on next TEWS/credit retransmission")
					# Register the transaction so that it can be replied later
					self.registeredAmbiguousTransactions[value('transactionId')] = {}
				else:
					# This is a retransmission, provides a OK response
					vsfs = [ (2390, 500, secretCode)  ]
					tews.send( {'status': 200, 'reason': 'OK', 'headers': {'Content-Type': 'text/xml', 'Connection': 'close'}, 'body': TEWS.m_tews_credit_response(transactionId = value('transactionId'), terminatingTransactionId = value('terminatingTransactionId'), vsfs = vsfs)}, to = sender('tews_client')),
					log("TEWS/credit OK response sent after an ER0009 response, with secret code set to %s" % secretCode)
			
			# S == 9: ER0009, then final response on next TEWS/credit retransmission
			elif len(dest) > 5 and dest[-5] == '9':
				# First reply a ER0009, and register the transaction for a standard NOK response on retransmission
				transactionId = value('transactionId')
				if not transactionId in self.registeredAmbiguousTransactions:
					tews.send( {'status': 500, 'reason': 'Internal server error', 'headers': {'Content-Type': 'text/xml', 'Connection': 'close'}, 'body': TEWS.m_tews_credit_response_KO(transactionId = value('transactionId'), terminatingTransactionId = value('terminatingTransactionId'), errorValue = 'ER0009', errorDescription = 'Ambiguous case (explicit)', vsfs = [ (2390, 500, "Credited user name") ] )}, to = sender('tews_client')),
					log("TEWS/credit ER0009 reponse sent, will provide a OK (if ended by 0000) or NOK response on next TEWS/credit retransmission")
					# Register the transaction so that it can be replied later
					self.registeredAmbiguousTransactions[value('transactionId')] = {'code': dest[-4:]}
				else:
					# This is a retransmission, provides a OK response if code is 0000
					# or a rejection otherwise
					code = self.registeredAmbiguousTransactions[transactionId].get('code', '0000')
					if code == '0000':
						# OK response
						vsfs = [ (2390, 500, secretCode)  ]
						tews.send( {'status': 200, 'reason': 'OK', 'headers': {'Content-Type': 'text/xml', 'Connection': 'close'}, 'body': TEWS.m_tews_credit_response(transactionId = value('transactionId'), terminatingTransactionId = value('terminatingTransactionId'), vsfs = vsfs)}, to = sender('tews_client')),
						log("TEWS/credit OK response sent after an ER0009 response, with secret code set to %s" % secretCode)
					else:
						tews.send( {'status': 500, 'reason': 'Internal server error', 'headers': {'Content-Type': 'text/xml', 'Connection': 'close'}, 'body': TEWS.m_tews_credit_response_KO(transactionId = value('transactionId'), terminatingTransactionId = value('terminatingTransactionId'), errorValue = 'ER%s' % code, errorDescription = 'Explicit error code aver TEWS/credit ambiguous retransmission' )}, to = sender('tews_client')),
						log("TEWS/credit NOK response ER%s sent after an ER0009 response" % code)

			# Conditional OK or ER00xx response
			elif dest.endswith('0009'):
				# CreditResponse fault: ER0009
				tews.send( {'status': 500, 'reason': 'Internal server error', 'headers': {'Content-Type': 'text/xml', 'Connection': 'close'}, 'body': TEWS.m_tews_credit_response_KO(transactionId = value('transactionId'), terminatingTransactionId = value('terminatingTransactionId'), errorValue = 'ER0009', errorDescription = 'Ambiguous case (explicit)', vsfs = [ (2390, 500, "Credited user name") ] )}, to = sender('tews_client')),
				log("TEWS/credit ER0009 reponse sent")
			elif dest.endswith('0003'):
				# CreditResponse fault: ER0003
				tews.send( {'status': 500, 'reason': 'Internal server error', 'headers': {'Content-Type': 'text/xml', 'Connection': 'close'}, 'body': TEWS.m_tews_credit_response_KO(transactionId = value('transactionId'), terminatingTransactionId = value('terminatingTransactionId'), errorValue = 'ER0003', errorDescription = 'Already in progress', vsfs = [ (2390, 500, "Credited user name") ])}, to = sender('tews_client')),
				log("TEWS/credit ER0003 reponse sent")
			elif dest.endswith('0013'):
				# CreditResponse fault: ER00013
				tews.send( {'status': 500, 'reason': 'Internal server error', 'headers': {'Content-Type': 'text/xml', 'Connection': 'close'}, 'body': TEWS.m_tews_credit_response_KO(transactionId = value('transactionId'), terminatingTransactionId = value('terminatingTransactionId'), errorValue = 'ER0013', errorDescription = 'Generic Crediting Error', vsfs = [ (2390, 500, "Credited user name") ])}, to = sender('tews_client')),
				log("TEWS/credit ER0013 reponse sent")
			elif dest.endswith('0000'):
				log("Sending a provisional response, maxCompletionDate = %s" % deadline)
				tews.send( {'status': 200, 'reason': 'OK', 'headers': {'Content-Type': 'text/xml', 'Connection': 'close'}, 
					'body': TEWS.m_tews_credit_response(
					transactionId = value('transactionId'), 
					terminatingTransactionId = value('terminatingTransactionId'),
					provisionalResponse = ( deadline, "CreditInProgress", "Credit In Progress" ),
					vsfs = [ (2390, 500, ("%s" % time.time()).split('.')[1]  ) ], # generate a transaction code
					)}, to = sender('tews_client'))
			elif dest.endswith('0007'):
				log("Sending a provisional response, no secret code, maxCompletionDate = %s" % deadline)
				tews.send( {'status': 200, 'reason': 'OK', 'headers': {'Content-Type': 'text/xml', 'Connection': 'close'}, 
					'body': TEWS.m_tews_credit_response(
					transactionId = value('transactionId'), 
					terminatingTransactionId = value('terminatingTransactionId'),
					provisionalResponse = ( deadline, "CreditInProgress", "Credit In Progress" ),
					)}, to = sender('tews_client'))
			else:
				# CreditResponse: OK
				# Always send a transaction code
				vsfs = [ (2390, 500, ("%s" % time.time()).split('.')[1]  ) ]
				tews.send( {'status': 200, 'reason': 'OK', 'headers': {'Content-Type': 'text/xml', 'Connection': 'close'}, 'body': TEWS.m_tews_credit_response(transactionId = value('transactionId'), terminatingTransactionId = value('terminatingTransactionId'), vsfs = vsfs)}, to = sender('tews_client')),
				log("TEWS/credit OK reponse sent")






		def handleCreditRequest_ban(destinationUri=any()):
			vsfs = []
			log("destination=%s" % destinationUri)
			dest = value('destinationUri')
			log("destination=%s" % destinationUri)
			#ban:AccountNumber;bic=*
			dest = dest.split(';')[0]
			transactionId = value('transactionId')

			# XXXSEEEE with XXX = 060: 60s delay before replying anything
			# XXXSEEEE with XXX = 080: 80s delay before replying anything
			if len(dest) > 8 and (dest[-8:-5] == "060" or dest[-8:-5] == "080"):
				if not transactionId in self.registeredAmbiguousTransactions:
					if (dest[-8:-5] == "080"):
						log("TEWS/credit delayed by 80s")
						t_wait(80.0)
					else:
						log("TEWS/credit delayed by 60s")
						t_wait(60.0)					
				else:
					log("Not delaying the TEWS/credit processing again: duplicate request")

			# Provisional response (TEWS/status are always replied with OK)
			now = datetime.datetime.utcnow()
			# 20s by default for the max completion date
			defaultMaxCompletionDate = now + datetime.timedelta(seconds = 20)
			deadline = defaultMaxCompletionDate.strftime("%Y-%m-%dT%H:%M:%SZ")

			# -------8<-------
			# Specific high level behaviours
			
			# S == 1: Web to bank (asynchronous)
			if dest.endswith('11001'):
				# Asynchronous response then a OK response on next status
				tews.send( {'status': 200, 'reason': 'OK', 'headers': {'Content-Type': 'text/xml', 'Connection': 'close'}, 
					'body': TEWS.m_tews_credit_response(
					transactionId = value('transactionId'), 
					terminatingTransactionId = value('terminatingTransactionId'),
					provisionalResponse = ( deadline, "CreditInProgress", "Credit In Progress" ),
					)}, to = sender('tews_client'))
			# S == 1: Web to bank (asynchronous)
			elif dest.endswith('11002'):
				# 120s by default for the max completion date
				defaultMaxCompletionDate = now + datetime.timedelta(seconds = 120)
				deadline = defaultMaxCompletionDate.strftime("%Y-%m-%dT%H:%M:%SZ")
				# Asynchronous response then a OK response on next status
				tews.send( {'status': 200, 'reason': 'OK', 'headers': {'Content-Type': 'text/xml', 'Connection': 'close'}, 
					'body': TEWS.m_tews_credit_response(
					transactionId = value('transactionId'), 
					terminatingTransactionId = value('terminatingTransactionId'),
					provisionalResponse = ( deadline, "CreditInProgress", "Credit In Progress" ),
					)}, to = sender('tews_client'))
			elif dest.endswith('11003'):
				# Asynchronous response with a secret code then a OK response on next status
				secretCode = ("%s" % time.time()).split('.')[1]
				vsfs = [ (2390, 500, secretCode)  ]

				tews.send( {'status': 200, 'reason': 'OK', 'headers': {'Content-Type': 'text/xml', 'Connection': 'close'}, 
					'body': TEWS.m_tews_credit_response(
					transactionId = value('transactionId'), 
					terminatingTransactionId = value('terminatingTransactionId'),
					vsfs = vsfs,
					provisionalResponse = ( deadline, "CreditInProgress", "Credit In Progress" ),
					)}, to = sender('tews_client'))
				log("TEWS/credit OK response sent, with secret code set to %s" % secretCode)
			
			elif dest.endswith('11004'):
				# Synchronous response
				tews.send( {'status': 200, 'reason': 'OK', 'headers': {'Content-Type': 'text/xml', 'Connection': 'close'}, 
								'body': TEWS.m_tews_credit_response(transactionId = value('transactionId'), terminatingTransactionId = value('terminatingTransactionId'), vsfs = vsfs)}, to = sender('tews_client')),
				log("TEWS/credit OK response sent, with secret code set to %s" % secretCode)

			elif dest.endswith('11005'):
				# Synchronous response vith secret code (legacy)
				secretCode = ("%s" % time.time()).split('.')[1]
				vsfs = [ (2390, 500, secretCode)  ]
				tews.send( {'status': 200, 'reason': 'OK', 'headers': {'Content-Type': 'text/xml', 'Connection': 'close'}, 
						'body': TEWS.m_tews_credit_response(transactionId = value('transactionId'), terminatingTransactionId = value('terminatingTransactionId'), vsfs = vsfs)}, to = sender('tews_client')),
				log("TEWS/credit OK response sent, with secret code set to %s" % secretCode)

			elif dest[-5] == '2':
				# Asynchronous response then a NOK response using the last 4 digits for the rejection code
				# secret code sent
				log("Sending a provisional response, maxCompletionDate = %s" % deadline)
				secretCode = ("%s" % time.time()).split('.')[1]
				vsfs = [ (2390, 500, secretCode)  ]
				tews.send( {'status': 200, 'reason': 'OK', 'headers': {'Content-Type': 'text/xml', 'Connection': 'close'}, 
					'body': TEWS.m_tews_credit_response(
					transactionId = value('transactionId'), 
					terminatingTransactionId = value('terminatingTransactionId'),
					vsfs = vsfs,
					provisionalResponse = ( deadline, "CreditInProgress", "Credit In Progress" ),
					)}, to = sender('tews_client'))
				# Register the transaction so that it can be rejected in a TEWS/status
				self.registeredTransactionsToReject[value('transactionId')] = { 'code': "ER%s" % dest[-4:] }
				log("TEWS/credit provisional response for a future rejected transaction, maxCompletionDate = %s" % (deadline))

			else:
				# Asynchronous response then a NOK response using the last 4 digits for the rejection code
				log("Sending a provisional response, maxCompletionDate = %s" % deadline)
				tews.send( {'status': 200, 'reason': 'OK', 'headers': {'Content-Type': 'text/xml', 'Connection': 'close'}, 
					'body': TEWS.m_tews_credit_response(
					transactionId = value('transactionId'), 
					terminatingTransactionId = value('terminatingTransactionId'),
					provisionalResponse = ( deadline, "CreditInProgress", "Credit In Progress" ),
					)}, to = sender('tews_client'))
				# Register the transaction so that it can be rejected in a TEWS/status
				self.registeredTransactionsToReject[value('transactionId')] = { 'code': "ER%s" % dest[-4:] }
				log("TEWS/credit provisional response for a future rejected transaction, maxCompletionDate = %s" % (deadline))





		def handleStatusRequest():
			"""
			Handle a TEWS/status request.
			For now, always reply OK/complete to complete the transaction successfully.
			"""
			transactionId = value('transactionId')
			if transactionId in self.registeredTransactionsToReject:
				rejection = self.registeredTransactionsToReject[transactionId]
				# Remove from the map
				del self.registeredTransactionsToReject[transactionId]
				log("Sending a status response transaction rejected (code %s)" % rejection['code'])
				body = TEWS.m_tews_status_response(
					transactionId = transactionId,
					terminatingTransactionId = value('terminatingTransactionId'),
					status = "rejected",
					code = rejection['code'], message = "Rejected"
				)
				tews.send( {'status': 200, 'reason': 'OK', 'headers': {'Content-Type': 'text/xml', 'Connection': 'close'}, 
						'body': body}, to = sender('tews_client'))
				
			else:
				# The transaction was not registered to be rejected.
				log("Sending a status response transaction complete")
				body = TEWS.m_tews_status_response(
					transactionId = transactionId,
					terminatingTransactionId = value('terminatingTransactionId'),
					status = "complete",
					vsfs = None) # VSFs were already provided in provisional response
	
				tews.send( {'status': 200, 'reason': 'OK', 'headers': {'Content-Type': 'text/xml', 'Connection': 'close'}, 
						'body': body}, to = sender('tews_client'))
			
			
			
		def handleCancellationRequest():
			dest = value('destinationUri')
			transactionId = value('transactionId')
			tews.send( {'status': 200, 'reason': 'OK', 'headers': {'Content-Type': 'text/xml', 'Connection': 'close'}, 
					'body': TEWS.m_tews_cancellation_response(
					transactionId = value('transactionId'), 
					terminatingTransactionId = value('terminatingTransactionId'),
					)}, to = sender('tews_client'))
			# Register the transaction so that it can be rejected in a TEWS/status
			#self.registeredTransactionsToReject[value('transactionId')] = { 'code': "ER0033" }
			log("TEWS/cancellation response for a successful cancellation" )
			
			
			
			
		def handleRusslavRequest():
			log("TEWS/russlav request analysis" )
			inXML= value('inXML')
			
			action, ppCode, docId, beneficiaryName	= decodeRusslavFrame(inXML)
			if action == 'NewOutgoing':
				log("Received : NewOutgoing");
				response,docId=createNewOutgoinRusslavResponse(ppCode,"0")
				if beneficiaryName == "Rejected":
					log("transaction to be rejected : %s" % (docId))
					self.registeredTransactionsToReject[docId] = 8
			elif action == 'PayOutgoing':
				log("Received : PayOutgoing");
				response=createGenericRusslavResponse(ppCode,"0",docId)
			elif action == 'GetState':
				log("Received : GetState");
				if docId in self.registeredTransactionsToReject:
					log("transaction should be rejected")
					state = self.registeredTransactionsToReject[docId]
					if state == 10:
						# Remove from the map
						del self.registeredTransactionsToReject[docId]
				else: # transaction not recorded as to be rejected
					log("transaction should be accepted")
					state= 6
				response=createGetStateResponse(ppCode,"0",docId,state)
			elif action == 'ReturnOutgoing':
				log("Received : ReturnOutgoing");
				response=createGenericRusslavResponse(ppCode,"0",docId)
				if docId in self.registeredTransactionsToReject:
					self.registeredTransactionsToReject[docId] = 10
			else:
				log("Received : Unknown");



			log("TEWS/russlav request analysis done" )
			test='''<?xml version =\"1.0\" standalone=\"yes\" ?><CDTRN Version=\"1\" PPCode=\"832\" Code=\"BASE64\" Lang=\"en\" Stamp=\"2012-05-22T09:02:36+00:00\"><DATA Pack=\"NONE\" Encryption=\"PLAIN\">r</DATA><SIGNATURES><SIGNATURE ALGO=\"RSA\">r</SIGNATURE></SIGNATURES></CDTRN>'''
			tews.send( {'status': 200, 'reason': 'OK', 'headers': {'Content-Type': 'text/xml', 'Connection': 'close'}, 
					'body': response  }, to = sender('tews_client'))
			

			
		def handleAmendRequest():
			dest = value('destinationUri')
			transactionId = value('transactionId')

			tews.send( {'status': 200, 'reason': 'OK', 'headers': {'Content-Type': 'text/xml', 'Connection': 'close'}, 
					'body': TEWS.m_tews_amend_response(
					transactionId = value('transactionId'), 
					terminatingTransactionId = value('terminatingTransactionId'),
					)}, to = sender('tews_client'))
			log("TEWS/amend response" )
			

		def handleGetToken():
			
			
#			tews.send( {'status': 200, 'reason': 'OK', 'headers': {'Content-Type': 'text/xml', 'Connection': 'close'}, 
#					'body': TMS.m_tokenization_response(mahstoken = 'b=518468;f=0006;v=1;r=0000000000000373799;t=mNY63Ptfo32xNjkgtNO9xSxNJBh92gZ7YHzpbEW3MuQ=')
#								}, to = sender('tews_client'))
#			log("Fake PAN returned" )
#			
#
#			# Expected input is a pan:BPPPSADCEEEEFFFFL      
#                               where B is the prefix (such as 5 for MasterCard)
#                                     PPP is the country prefix for currency
#                                     S is the scenario
#                                     A is the code for AI sleep time 
#                                     D is the code for CR sleep time
#                                     C is the code for MaxCompletionDate
#                                     EEEE is the error code if error scenario
#                                     FFFF is the suffix (unused for the moment)
#
			dest = value('accountNumber')
#			dest = 'pan:123456789012'
			log("accountNumber received =%s" % (dest)) 
			
			if dest.startswith('pan:') and len(dest) == 20:
				log("PAN scheme detected with 16 digits" )
								
				# Expected output is a b=BBBBBB;f=FFFF;v=1;r=0000000000000SSEEEE;t=mNY63Ptfo32xNjkgtNO9xSxNJBh92gZ7YHzpbEW3MuQ=
				tokenizedDestinationUri = 'b=' + dest[4:10] + ';f=' + dest[16:20] + ';v=1;r=0000000' + dest[-15:-3] + ';t=mNY63Ptfo32xNjkgtNO9xSxNJBh92gZ7YHzpbEW3MuQX'

				log("token URI=%s" % tokenizedDestinationUri)
				tews.send( {'status': 200, 'reason': 'OK', 'headers': {'Content-Type': 'text/xml', 'Connection': 'close'}, 
					'body': TMS.m_tokenization_response(mahstoken = tokenizedDestinationUri)
								}, to = sender('tews_client'))
			elif dest.startswith('pan:') and len(dest) == 32:
				log("PAN scheme detected with 16 digits and expiry date" )
								
				# Expected output is a b=BBBBBB;f=FFFF;v=1;r=0000000000000SSEEEE;t=mNY63Ptfo32xNjkgtNO9xSxNJBh92gZ7YHzpbEW3MuQ=
				tokenizedDestinationUri = 'b=' + dest[4:10] + ';f=' + dest[16:20] + ';v=1;r=0000000' + dest[5:17] + ';t=mNY63Ptfo32xNjkgtNO9xSxNJBh92gZ7YHzpbEW3MuQX'

				log("token URI=%s" % tokenizedDestinationUri)
				tews.send( {'status': 200, 'reason': 'OK', 'headers': {'Content-Type': 'text/xml', 'Connection': 'close'}, 
					'body': TMS.m_tokenization_response(mahstoken = tokenizedDestinationUri)
								}, to = sender('tews_client'))
		  						
			else:
				log("No PAN scheme detected or unexpected length" )
				tews.send( {'status': 500, 'reason': 'Input value was not a PAN', 'headers': {'Content-Type': 'text/xml', 'Connection': 'close'}, 
					'body': TMS.m_tokenization_response(mahstoken = 'b=xxxxxx;f=xxxx;v=1;r=InvalidToken_for_InvalidPan;t=DummyValue')
								}, to = sender('tews_client'))
			log("TMS/token response" )
		
		
		mw_myTemplate = [ any_or_none(), { 'tag': any(), 'value': extract(any(), 'my_val') }, any_or_none() ]
		
		# -----------------------------------8<-----------------------------------
		# 'main' listening frame 'loop' for AccountInfo & CreditRequest frames :
		# -----------------------------------8<-----------------------------------
		alt([
			# AccountInformation requests
			[ tews.RECEIVE( {'body': TEWS.mw_tews_accountInformation_request()}, sender = 'tews_client'),
				lambda: log("TEWS/accountInformation request received (tdId=%s)" % (value('transactionId')) ),
				lambda: handleAccountInfo(),
				lambda: REPEAT,
			],
			# Pan Elligibility requests
			[ tews.RECEIVE({'body': TMS.mw_tms_PanEligibility_request()}, sender = 'tews_client'),
				lambda: log("TMS/panEligibility request received (tdId=%s)" % (value('transactionId')) ),
				lambda: handlePanEligibilityRequest(),
				lambda: REPEAT,
			],
			
			# Credit requests
			[ tews.RECEIVE( {'body': TEWS.mw_tews_credit_request()}, sender = 'tews_client'),
				lambda: log("TEWS/credit request received (tdId=%s, termId=%s)" % (value('transactionId'), value('terminatingTransactionId')) ),
				lambda: handleCreditRequest(),
				lambda: REPEAT,
			],
			# Payment requests
			[ tews.RECEIVE({'body': TMS.mw_tms_payment_request()}, sender = 'tews_client'),
				lambda: log("TMS/payment request received with terminating transaction id %s " % value('transactionReference')),
				lambda: handlePaymentRequest(),
				lambda: REPEAT,
			],
			
			# Status requests
			[ tews.RECEIVE( {'body': TEWS.mw_tews_status_request()}, sender = 'tews_client'),
				lambda: log("TEWS/status request received (tdId=%s, termId=%s)" % (value('transactionId'), value('terminatingTransactionId')) ),
				lambda: handleStatusRequest(),
				lambda: REPEAT,
			],
			# Cancellation requests
			[ tews.RECEIVE( {'body': TEWS.mw_tews_cancellation_request()}, sender = 'tews_client'),
				lambda: log("TEWS/cancellation request received (tdId=%s, termId=%s)" % (value('transactionId'), value('terminatingTransactionId')) ),
				lambda: handleCancellationRequest(),
				lambda: REPEAT,
			],
			# Amend requests
			[ tews.RECEIVE( {'body': TEWS.mw_tews_amend_request(amendedFields=None)}, sender = 'tews_client'),
				lambda: log("TEWS/amend request received (tdId=%s, termId=%s)" % (value('transactionId'), value('terminatingTransactionId')) ),
				lambda: handleAmendRequest(),
				lambda: REPEAT,
			],
			# Device watchdog requests
			[ tews.RECEIVE( {'body': TEWS.mw_tews_deviceWatchdog_request()}, sender = 'tews_client'),
				lambda: log("TEWS/deviceWatchdog request received"),
				lambda: tews.send({'status': 200, 'reason': 'OK', 'headers': {'Content-Type': 'text/xml', 'Connection': 'close'},'body':TEWS.m_tews_deviceWatchdog_response() }, to = sender('tews_client')),
				lambda: REPEAT,
			],			
			# Russlavbank  requests
			[ tews.RECEIVE( {'body': TEWS.mw_tews_russlav_request()}, sender = 'tews_client'),
				lambda: log("TEWS/russlav request received (inXML=%s)" % (value('inXML'))),
				lambda: handleRusslavRequest(),
				lambda: REPEAT,
			],				
			# GetToken requests (in order to generate our own token with a controlled content)
			[ tews.RECEIVE( {'body': TMS.mw_tokenization_request()}, sender = 'tews_client'),
#				tews.RECEIVE( {'body': TMS.mw_tokenization_request(accountNumber = any())}, sender = 'tews_client'),
				lambda: log("TMS/getToken request received (account_number=%s)" % (value('accountNumber')) ),
				lambda: handleGetToken(),
				lambda: REPEAT,
			],
			# Unknown/unsupported message
			[ tews.RECEIVE( {}, sender = 'tews_client'),
				lambda: log("Unknown/unsupported message received - replying with a default terminatingException"),
				lambda: tews.send({'status': 500, 'reason': 'Internal Server Error', 'headers': {'Content-Type': 'text/xml', 'Connection': 'close'}, 'body': TEWS.m_tews_terminatingService_exception(transactionId = "", terminatingTransactionId = "", code = 'ER0008', message = 'Unrecognized request') }),
				lambda: REPEAT,
			],
		])



# -------------------------------------------------8<-------------------------------------------------
class APP_TEWS_PROCESSED_SIMULATOR(TestCase):
	"""
	MTC : Tews "listening/answering" Simulator : process sent responses according to received frames.
	"""
	def body(self, duration = 90.0, currency_map = {}, country_map={},default_currency = "EUR"):

		# Build Container
		ptc = self.create(name = "TEWS Simulator")
		
		# Map system ports
		port_map(ptc["tews_port"], self.system["tews_listening"])
		test='<?xml version ="1.0" standalone="yes" ?><CDTRN Version="1" PPCode="TZCU" Code="BASE64" Lang="en" Stamp="2012-04-30T11:35:43+00:00"><DATA Pack="NONE" Encryption="PLAIN">PFJFUVVFU1QgRE9DX0lEPSItMSIgT0JKRUNUX0NMQVNTPSJUTW9uZXlPcmRlck9iamVjdCIgQUNUSU9OPSJOZXdPdXRnb2luZyIgSU5UX1NPRlRfSUQ9Ijk4RENCMUY4LTZDRjgtNDVEOS05OTkzLUEzMzdCRjUwNTcwQiIgUE9JTlRfSUQ9IjEwMDAwOTkiIFVTRVJfSUQ9IjgzMiIgTEFORz0iRU4iPjxzTmFtZT5TZW5kZXI8L3NOYW1lPjxzTGFzdE5hbWU+TmFtZTwvc0xhc3ROYW1lPjxzQ291bnRyeUM+RlI8L3NDb3VudHJ5Qz48c1Bob25lPjMyMS0yLTM0NTY3ODwvc1Bob25lPjxzUmVzaWRlbnQ+MDwvc1Jlc2lkZW50PjxiTmFtZT5zPC9iTmFtZT48Ykxhc3ROYW1lPm5hbWU8L2JMYXN0TmFtZT48dHJuU2VuZFBvaW50PlRaQ1U8L3RyblNlbmRQb2ludD48dHJuQW1vdW50PjEwMC4wMDwvdHJuQW1vdW50Pjx0cm5DdXJyZW5jeT5FVVI8L3RybkN1cnJlbmN5Pjx0cm5QaWNrdXBQb2ludD5NUlNCPC90cm5QaWNrdXBQb2ludD48dHJuU2VydmljZT4yPC90cm5TZXJ2aWNlPjx0cm5SZWZlcmVuY2U+MTI1OTQxPC90cm5SZWZlcmVuY2U+PHRybkRhdGU+MjAxMjA0MzA8L3RybkRhdGU+PC9SRVFVRVNUPg==</DATA><SIGNATURES><SIGNATURE ALGO="RSA">MIAGCSqGSIb3DQEHAqCAMIACAQExCzAJBgUrDgMCGgUAMIAGCSqGSIb3DQEHAQAAMYIBLzCCASsCAQEwKjAWMRQwEgYDVQQDEwtSVVNTTEFWQkFOSwIQHU72uupqbKJBL4s50U+sajAJBgUrDgMCGgUAoF0wGAYJKoZIhvcNAQkDMQsGCSqGSIb3DQEHATAcBgkqhkiG9w0BCQUxDxcNMTIwNDMwMTEzNTQzWjAjBgkqhkiG9w0BCQQxFgQUOBay35cw2EQLFAl0Qw43sFnoD6gwDQYJKoZIhvcNAQEBBQAEgYAQhp848MNEdyZudDUeonWdmGcQWLdaEIJqAfV8TKMBzY3VS/gErmiN6Tt0h1AiJmDHMk/Mh/sF8AUwsHuN6nNmlPyvgwAMrzzOYUqXv9S4g0glUaU291KzoEq5K/RKihgiW1johoJi+6df1N8gp0G+6Bt3rx1kK/EUpFCjGM72mAAAAAAAAA==</SIGNATURE></SIGNATURES></CDTRN>'

		testVar = False
		
		# Start the PTC
		ptc.start(BEHAVIOR_TEWS_SERVER_PROCESSED_REPLIER(), currency_map = currency_map,country_map=country_map, default_currency = default_currency)
		t = Timer(duration, "simulation duration")
		t.start()
		alt([
			[ t.TIMEOUT,
				lambda: log("Terminating simulator on timeout"),
			],
			[ ptc.DONE,
				lambda: log("Simulator stopped on exception."),
			]
		])



# -------------------------------------------------8<-------------------------------------------------
# Test Adapter Configurations
bind('tews_listening', 'probe:%s' % PX_TEWS_PROBE, 'tcp', listening_port = PX_TEWS_PORT, default_decoder = 'http.request', default_encoder = 'http.response')


# -------------------------------------------------8<-------------------------------------------------
# Possible Tests :
# APP_TEWS_OK_SIMULATOR().execute(duration = PX_DURATION)
# - Phone Prefix & Currency           : http://fr.wikipedia.org/wiki/Liste_des_indicatifs_t%C3%A9l%C3%A9phoniques_internationaux_par_indicatif
#                                       http://www.nbs.sk/en/statistics/exchange-rates/exchange-rates-of-selected-foreign-currencies-against-the-eur/_htm/klvcm-20090601/g
# - Exchange Rates (Currency <-> XDR) : http://www.mataf.net/en/change/XDR
#                                       http://www.nbs.sk/en/statistics/exchange-rates/exchange-rates-of-selected-foreign-currencies-against-the-eur/_htm/klvcm-20090601/g
currency_map = {  
		'1': 'USD',			# United States of America - US Dollar
		'32': 'EUR',    # Belgium - Euro
		'44' : 'GBP',   # UK - Pound
		'63': 'PHP',    # Philippines - Philippine Piso
		'86': 'CNY',    # China - Yuan Renminbi 
		'20': 'EGP',    # Egypt - Egyptian Pound
		'212': 'MAD',   # Morocco - Moroccan Dirham
		'233': 'GHS',   # Ghana - Ghana Cedi
		'255': 'TZS',   # Tanzania - Tanzanian Shilling
		'880': 'BDT',   # Bangladesh - Taka
		'91': 'INR',    # India - Indian Rupee
		'84': 'VND',    # Vietnam - D?ng
		'254': 'KES',   # Kenya - Kenyan Shilling
		'92': 'PKR',    # Pakistan - Pakistan Rupee
		'974': 'QAR',   # Qatar - Qatari Rial
		'226': 'XOF',   # Burkina Faso - CFA Franc BCEAO
		'804': 'UAH',   # Ukraine - Hryvnia
		'45': 'DKK',   	# Denmark - Danish Krone
		'46': 'SEK',   	# Sweden - Swedish Krona
		'7': 'RUB',   	# Russian Federation - Russian Ruble
		'65': 'SGD',    # Singapore - Singapore Dollar
		'399': 'EEE'    # test
	}
country_map = {  
		'1': 'USA',			# United States of America
		'32': 'EUR',    # Belgium*
		'44' : 'GBR',    # GBR
		'63': 'PHL',    # Philippines
		'86': 'CHN',    # China
		'20': 'EGY',    # Egypt
		'212': 'MAR',   # Morocco
		'233': 'GHA',   # Ghana
		'255': 'EAZ',   # Tanzania 
		'880': 'BGD',   # Bangladesh 
		'91': 'IND',    # India
		'84': 'VNM',    # Vietnam
		'254': 'KEN',   # Kenya
		'92': 'PAK',    # Pakistan
		'974': 'QAT',   # Qatar
		'226': 'BFA',   # Burkina Faso
		'804':'UKR',   	# Ukraine 
		'45': 'DNK',   	# Denmark
		'46': 'SEK',   	# Sweden
		'7': 'RUS',   	# Russian Federation 
		'65': 'SGP',   	# Singapore
		'399': 'EEE'   # test
	}

while True:	
	APP_TEWS_PROCESSED_SIMULATOR().execute(duration = PX_DURATION, currency_map = currency_map, country_map= country_map)
