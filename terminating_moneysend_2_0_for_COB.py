#                                                     _ 
# _ __ ___   ___  _ __   ___ _   _ ___  ___ _ __   __| |
#| '_ ` _ \ / _ \| '_ \ / _ \ | | / __|/ _ \ '_ \ / _` |
#| | | | | | (_) | | | |  __/ |_| \__ \  __/ | | | (_| |
#|_| |_| |_|\___/|_| |_|\___|\__, |___/\___|_| |_|\__,_|
#                            |___/                      
#  ________________  __  ________   _____  ___________   ________   ___ 
# /_  __/ ____/ __ \/  |/  /  _/ | / /   |/_  __/  _/ | / / ____/  |__ \
#  / / / __/ / /_/ / /|_/ // //  |/ / /| | / /  / //  |/ / / __    __/ /
# / / / /___/ _, _/ /  / // // /|  / ___ |/ / _/ // /|  / /_/ /   / __/ 
#/_/ /_____/_/ |_/_/  /_/___/_/ |_/_/  |_/_/ /___/_/ |_/\____/   /____/ 
#
# done with http://www.network-science.de/ascii/ (standart and slant)
import binascii


def f_getReceivingMapped(destinationUri):
	"""
	This function give expected content on ReceivingMapped section
	giving a destinationUri
	"""
	IsTel=re.match("tel:\+\d+", destinationUri)
	if IsTel:
		subscriberId = destinationUri.replace("tel:+", "")
		subscriberType = 'PHONE_NUMBER'
		subsDetails =  [ ( 'SubscriberId' , { 'value' : extract(subscriberId, 'subscriberId') }),
										('SubscriberType', { 'value' : extract(subscriberType, 'subscriberType') } ),
										ifpresent(('SubscriberAlias', {'value': 'My Debit Card'}))]
		return subsDetails
		
	IsMh=re.match("mahstoken:\+\.*",destinationUri)
	if IsMh:
		subscriberId = destinationUri.replace("mahstoken:", "")
		subscriberType = 'TOKEN'
		subsDetails =  [ ( 'SubscriberId' , { 'value' : extract(subscriberId, 'subscriberId') }),
										('SubscriberType', { 'value' : extract(subscriberType, 'subscriberType') } ),
										ifpresent(('SubscriberAlias', {'value': 'My Debit Card'}))]
		return subsDetails
		
#	IsMail=re.match("email:\+\.*",destinationUri)
#	if IsMmail:
#		subscriberId = destinationUri.replace("email:", "")
#		subscriberType = 'EMAIL_ADDRESS'
#		subsDetails =  [ ( 'SubscriberId' , { 'value' : extract(subscriberId, 'subscriberId') }),
#										('SubscriberType', { 'value' : extract(subscriberType, 'subscriberType') } ),
#										ifpresent(('SubscriberAlias', {'value': 'My Debit Card'}))]
#		return subsDetails
		
	return None
	
	
##########################################################################################

def f_treatBanOrIban(accountNumber):
	"""
	treat uri of a ban or iban
	if only num from accountNumber is empty, then
	take the crc32 of accountNumber
	"""
	numAccountNumber = re.sub("[^0-9]", "", accountNumber)
	# first 20 one caracters
	numAccountNumber = numAccountNumber[:20]
	if len(numAccountNumber) == 0:
		log("take crc32 of accountnumber")
		return str(binascii.crc32(accountNumber))
	else:
		return numAccountNumber

#####################################################################################

def f_getFundingSectionInfos(sourceUri):
	"""
	This function gives 
	a section fundingCard or fundingMapped
	depending on pattern of the sourceUri
	"""
	
	IsMh=re.match("mahstoken:\+\.*",sourceUri)
	if IsMh:
		# sourceUri is a mahstoken
		subscriberId = sourceUri.replace("mahstoken:", "")
		subscriberType = 'TOKEN'
		fundingPart =  ( 'FundingMapped' , { 'children' : [
											( 'SubscriberId' , { 'value' : extract(subscriberId, 'subscriberId') }),
											('SubscriberType', { 'value' : extract(subscriberType, 'subscriberType')}),
																												]})
	else:
		# sourceUri is not a mahstoken
		IsTel=re.match("tel:\+\d+", sourceUri)
		if IsTel:
			accountNumber = sourceUri.replace("tel:+", "")
		
		elif re.match("ban:.*", sourceUri):
			# we got a source uri ban
			accountNumber = sourceUri.replace("ban:", "")
			#take only numeric char
			accountNumber = f_treatBanOrIban(accountNumber)
		elif re.match("iban:.*", sourceUri):
			# we got a source uri iban
			accountNumber = sourceUri.replace("iban:", "")
			accountNumber = f_treatBanOrIban(accountNumber)
		else:
			# anything else
			accountNumber = str(binascii.crc32(accountNumber))
			
		fundingPart = ( 'FundingCard' , { 'children' : [
												('AccountNumber', {'value': accountNumber}),
																										]})
									
		

		return fundingPart
	
#####################################################################################

def f_getFundingSource(sourceUri):
	"""
	This function gives
	the section fundingSource depending on sourceUri
	"""
	
	if re.match("tel:\+\d+", sourceUri):
		leCode = "05"
	elif re.match("mahstoken:\+\.*",sourceUri):
		leCode = "02"
	elif re.match("ban:.*|iban:.*",sourceUri):
		leCode = "04"
	else:
		leCode = "05"
	
	return ( 'FundingSource', { 'value' : leCode })
	
#####################################################################################

def f_getSenderAddressSectionInfos(senderPostalCode, line1, senderCity, countrySubdivision, senderCountry):
	"""
	This function gives 
	a section senderAddress depending on senderPostalCode that may be empty
	"""
	
	xsenderAddress = [
							('Line1', {'value': line1,}),
							('City', {'value': senderCity }),
								]
	if countrySubdivision != "":
		xsenderAddress.append(('CountrySubdivision', {'value': countrySubdivision }))
	
	if senderPostalCode != "":
		xsenderAddress.append(('PostalCode', {'value': senderPostalCode }))
	
	xsenderAddress.append(('Country', {'value': senderCountry }))
	
	return ('SenderAddress', {'children': xsenderAddress })
	
#####################################################################################

def f_getFullName(first, middle, last):
	"""
	construct content of section sender/ReceiverName in payment request
	"""
	if middle is any():
		return [
						('First', { 'value' : first }),
						('Middle', { 'value' : middle }),
						('Last', { 'value' : last }),
						]
	elif middle == "Z":
		return [
							('First', { 'value' : first }),
							('Last', { 'value' : last }),
						]
	
	else:
		return [
						('First', { 'value' : first }),
						('Middle', { 'value' : middle }),
						('Last', { 'value' : last }),
						]
	
		
	
#####################################################################################	

def f_getVsfValue(vsfs, vendorId, fieldId):
	"""
	function to check if a vsf vendorId:fieldId is in the list of vsfs
	if yes then return value associated
	else return None
	"""
	
	for vid, fid, val in vsfs:
		if vid == vendorId and fid == fieldId:
			return val
	
	return None	

####################################################################################

def f_formatLength(data, n = 50):
	"""
	if data is None then data = any()
	else
	get only the first n char of data
	"""
	if data is None:
		return any()
	else:
		return data[:n]
		
###############################################################################
# TMS/PanEligibility request
###############################################################################


def mw_tms_PanEligibility_request(subscriberId=any(),subscriberType=any()): 
	"""
	check the body of PanEligibility request
Body:
<?xml version="1.0" encoding="UTF-8" ?>
<PanEligibilityRequest>
     <ReceivingMapped>
          <SubscriberId>6367227000</SubscriberId >
          <SubscriberType>PHONE_NUMBER</SubscriberType >
          <SubscriberAlias>MyMasterCard</SubscriberAlias>
     </ReceivingMapped>
</PanEligibilityRequest>
	"""

	ret = ('PanEligibilityRequest', { 'children': [ 
					('ReceivingMapped', {'children': [
							('SubscriberId', {'value': extract(subscriberId, 'subscriberId')}),
							('SubscriberType', {'value': extract(subscriberType, 'subscriberType')}),
						]}),
						('DataResponseFlag', { 'value' : "0" })
																								] }
				)
																							
						
	return with_('xml', ret)


###############################################################################
# TMS/PanEligiblity response
###############################################################################


def m_tms_PanEligibility_response(eligible = True, networkPrimaryKey = "9000",
	alphaCurrencyCode = "USD", alphaCountryCode = "USA", requestId = "333000",
	reasonCode = "120016", accountNumber = "5555555555559998",
	numericCurrencyCode = "666", numericCountryCode = "666"): 
	"""
	the body of PanEligibility response
	"""
	
	if eligible:
		ret=u"""<?xml version="1.0" encoding="utf-8" standalone="yes"?>
			<PanEligibility>
				<RequestId>%(requestId)s</RequestId>
				<ReceivingEligibility>
					<Eligible>true</Eligible>
					<EnablementIndicator>D</EnablementIndicator>
					<AccountNumber>%(accountNumber)s</AccountNumber>
					<ICA>%(networkPrimaryKey)s</ICA>
					<Currency>
						<AlphaCurrencyCode>%(alphaCurrencyCode)s</AlphaCurrencyCode>
						<NumericCurrencyCode>%(numericCurrencyCode)s</NumericCurrencyCode>
					</Currency>
					<Country>
						<AlphaCountryCode>%(alphaCountryCode)s</AlphaCountryCode>
						<NumericCountryCode>%(numericCountryCode)s</NumericCountryCode>
					</Country>
					<Brand>
						<AcceptanceBrandCode>DMC</AcceptanceBrandCode>
						<ProductBrandCode>MPP</ProductBrandCode>
					</Brand>
				</ReceivingEligibility>
			</PanEligibility>
			""" % locals()
	else:
		ret=u"""<?xml version="1.0" encoding="utf-8" standalone="yes"?>
			<PanEligibility>
				<RequestId>%(requestId)s</RequestId>
				<ReceivingEligibility>
					<Eligible>false</Eligible>
					<ReasonCode>%(reasonCode)s</ReasonCode>   
					<AccountNumber>%(accountNumber)s</AccountNumber>
				</ReceivingEligibility>
			</PanEligibility>
			""" % locals()			
	return ret.encode('utf-8')

def m_tms_PanEligibility_error():
	"""
	the pan eligibility is going wrong
	"""
	ret=u"""
		<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
		<Errors>
			<Error>
				<RequestId>277588</RequestId>
				<Source>SubscriberId</Source>
				<ReasonCode>INVALID_INPUT_VALUE</ReasonCode>
				<Description>Phone Number is invalid.</Description>
				<Recoverable>false</Recoverable>
				<Details>
					<Detail>
						<Name>ErrorDetailCode</Name>
						<Value>080101</Value>
					</Detail>
				</Details>
			</Error>
		</Errors>
		"""
	return ret.encode('utf-8')

###############################################################################
# TMS/Payment request
###############################################################################

def mw_tms_payment_request2(sourceUri= any(), destinationUri= any(), localDate = any(), localTime = any(),
	transactionReference = any(),
	senderFirstName = any(),senderMiddleName = any(),senderLastName = any(),
	line1 = any(), senderCity = any(), countrySubdivision = any(),
	senderPostalCode = any(), senderCountry = any(),
	receiverFirstName = any(),receiverMiddleName = any(),receiverLastName = any(),
	value = any(), currency = any(),
	channel = any(),
	ica = any(), processorId = any(), routingAndTransitNumber = any(),
	caName = any(), caCity = any(), caState = any(), caPostalCode = any(),
	caCountry = any(), transactionDesc = any(), merchantId = any(),
	accountNumber=any(),fundingSource=any(),receiverAddress=any(),receivingMapped=any(),
	subscriberId=any(),subscriberType=any()
	):
	"""
	check the body of payment request
<?xml version="1.0" encoding="UTF-8"?>
<PaymentRequestV3>
   <LocalDate>0518</LocalDate>
   <LocalTime>085056</LocalTime>
   <TransactionReference>1113601463561458793</TransactionReference>
   <SenderName>
      <First>Suzane</First>
      <Middle>M</Middle>
      <Last>beaucoupEpee</Last>
   </SenderName>
   <SenderAddress>
      <Line1>3344 long long long but very long main st</Line1>
      <City>noTown</City>
      <CountrySubdivision>CA</CountrySubdivision>
      <PostalCode>92328</PostalCode>
      <Country>USA</Country>
   </SenderAddress>
   <FundingCard>
      <AccountNumber>33687352878</AccountNumber>
   </FundingCard>
   <FundingSource>05</FundingSource>
   <ReceiverName>
      <First>receiver</First>
      <Middle>r</Middle>
      <Last>name</Last>
   </ReceiverName>
   <ReceiverAddress />
   <ReceivingMapped>
      <SubscriberId>221123456</SubscriberId>
      <SubscriberType>PHONE_NUMBER</SubscriberType>
   </ReceivingMapped>
   <ReceivingAmount>
      <Value>100980</Value>
      <Currency>840</Currency>
   </ReceivingAmount>
   <ICA>009674</ICA>
   <ProcessorId>9000000442</ProcessorId>
   <RoutingAndTransitNumber>990442082</RoutingAndTransitNumber>
   <CardAcceptor>
      <Name>the local bank</Name>
      <City>Granoble</City>
      <State>PA</State>
      <PostalCode>18940</PostalCode>
      <Country>USA</Country>
   </CardAcceptor>
   <TransactionDesc>P2P</TransactionDesc>
   <MerchantId>123456</MerchantId>
   <Channel>M</Channel>
</PaymentRequestV3>

	"""
	
#	line1 = f_formatLength(line1)
#	senderNameFirst = f_formatLength(senderNameFirst, 35)
#	senderNameMiddle = f_formatLength(senderNameMiddle, 1)
#	senderNameLast = f_formatLength(senderNameLast, 35)
#	receiverNameFirst = f_formatLength(receiverNameFirst, 35)
#	receiverNameMiddle = f_formatLength(receiverNameMiddle, 1)
#	receiverNameLast = f_formatLength(receiverNameLast, 35)

	ret =  ('PaymentRequestV3', {'children': [
						('LocalDate', {'value': extract(localDate, 'localDate')}),
						('LocalTime', {'value': extract(localTime, 'localTime')}),
						('TransactionReference', {'value': extract(transactionReference, 'transactionReference')}),
						('SenderName', {'children': [
							('First', {'value': extract(senderFirstName, 'senderFirstName')}),
							ifpresent(('Middle', {'value': extract(senderMiddleName, 'senderMiddleName')})),
							any_or_none(),
							('Last', {'value': extract(senderLastName, 'senderLastName')}),

							]}
						),
						('ReceivingAmount', {'children': [
							('Value', {'value': extract(value, 'value')}),
							('Currency', {'value': extract(currency, 'currency')})
							]}
						),
						('FundingCard', {'children': [
							('AccountNumber', {'value': extract(accountNumber, 'accountNumber')}),
							]}
						),
						('FundingSource', {'value' : extract(fundingSource, 'fundingSource') } ),
						
						('ReceiverName', {'children': [
							('First', {'value': extract(receiverFirstName, 'receiverFirstName')}),
							ifpresent(('Middle', {'value': extract(receiverMiddleName, 'receiverMiddleName')})),
							('Last', {'value': extract(receiverLastName, 'receiverLastName')}),
							]}
						),

						('ReceiverAddress', {'value' : extract(receiverAddress, 'receiverAddress') } ),
						('ReceivingMapped', {'children': [
							('SubscriberId', {'value': extract(subscriberId, 'subscriberId')}),
							('SubscriberType', {'value': extract(subscriberType, 'subscriberType')}),
						]}),
						('SenderAddress', {'children': [
							('Line1', {'value': extract(line1, 'line1')}),
							('City', {'value': extract(senderCity, 'senderCity')}),
							ifpresent(('CountrySubdivision', {'value': extract(countrySubdivision, 'countrySubdivision')})),
							('PostalCode', {'value': extract(senderPostalCode, 'senderPostalCode')}),
							('Country', {'value': extract(senderCountry, 'senderCountry')}),
							]}
						),

						('ICA', {'value': extract(ica, 'ica')}),
						('ProcessorId', {'value': extract(processorId, 'processorId')}),
						('RoutingAndTransitNumber', {'value': extract(routingAndTransitNumber, 'routingAndTransitNumber')}),
						('CardAcceptor', {'children': [
							('Name', {'value': extract(caName, 'caName')}),
							('City', {'value': extract(caCity, 'caCity')}),
							('State', {'value': extract(caState, 'caState')}),
							('PostalCode', {'value': extract(caPostalCode, 'caPostalCode')}),
							('Country', {'value': extract(caCountry, 'caCountry')})
						]}),
						('TransactionDesc', {'value': extract(transactionDesc, 'transactionDesc')}),
						ifpresent(('MerchantId',{'value': extract(merchantId, 'merchantId')})),
						ifpresent(('Channel',   {'value': extract(channel, 'channel')})),
						any_or_none()
					]}
				)
																	
						
	return with_('xml', ret)



###############################################################################
# TMS/Payment request
###############################################################################

def mw_tms_payment_request(sourceUri= any(), destinationUri= any(), localDate = any(), localTime = any(),
	transactionReference = any(),
	senderName = any(),
	line1 = any(), senderCity = any(), countrySubdivision = any(),
	senderPostalCode = any(), senderCountry = any(),
	receiverName= any(),
	value = any(), currency = any(),
	channel = any(),
	ica = any(), processorId = any(), routingAndTransitNumber = any(),
	caName = any(), caCity = any(), caState = any(), caPostalCode = any(),
	caCountry = any(), transactionDesc = any(), merchantId = any(), channelId = any(),
	accountNumber=any(),fundingSource=any(),receiverAddress=any(),
	subscriberId=any(), subscriberType=any()
	):
	"""
	check the body of payment request
<?xml version="1.0" encoding="UTF-8"?>
<PaymentRequestV3>
   <LocalDate>0518</LocalDate>
   <LocalTime>085056</LocalTime>
   <TransactionReference>1113601463561458793</TransactionReference>
   <SenderName>
      <First>Suzane</First>
      <Middle>M</Middle>
      <Last>beaucoupEpee</Last>
   </SenderName>
   <SenderAddress>
      <Line1>3344 long long long but very long main st</Line1>
      <City>noTown</City>
      <CountrySubdivision>CA</CountrySubdivision>
      <PostalCode>92328</PostalCode>
      <Country>USA</Country>
   </SenderAddress>
   <FundingCard>
      <AccountNumber>33687352878</AccountNumber>
   </FundingCard>
   <FundingSource>05</FundingSource>
   <ReceiverName>
      <First>receiver</First>
      <Middle>r</Middle>
      <Last>name</Last>
   </ReceiverName>
   <ReceiverAddress />
   <ReceivingMapped>
      <SubscriberId>221123456</SubscriberId>
      <SubscriberType>PHONE_NUMBER</SubscriberType>
   </ReceivingMapped>
   <ReceivingAmount>
      <Value>100980</Value>
      <Currency>840</Currency>
   </ReceivingAmount>
   <ICA>009674</ICA>
   <ProcessorId>9000000442</ProcessorId>
   <RoutingAndTransitNumber>990442082</RoutingAndTransitNumber>
   <CardAcceptor>
      <Name>the local bank</Name>
      <City>Granoble</City>
      <State>PA</State>
      <PostalCode>18940</PostalCode>
      <Country>USA</Country>
   </CardAcceptor>
   <TransactionDesc>P2P</TransactionDesc>
   <MerchantId>123456</MerchantId>
   <Channel>M</Channel>
</PaymentRequestV3>

	"""
	
#	line1 = f_formatLength(line1)
#	senderNameFirst = f_formatLength(senderNameFirst, 35)
#	senderNameMiddle = f_formatLength(senderNameMiddle, 1)
#	senderNameLast = f_formatLength(senderNameLast, 35)
#	receiverNameFirst = f_formatLength(receiverNameFirst, 35)
#	receiverNameMiddle = f_formatLength(receiverNameMiddle, 1)
#	receiverNameLast = f_formatLength(receiverNameLast, 35)
# HRO 20170829	Have removed below					('FundingCard', { 'children':any_or_none() }),
#('MerchantId', {'value': extract(merchantId, 'merchantId')}),
#						('MerchantId', {'value': any_or_none() }),
#						('Channel', {'value': extract(channelId, 'channelId')}),

	ret = ('PaymentRequestV3', {'children': [
						('LocalDate', {'value': extract(localDate, 'localDate')}),
						('LocalTime', {'value': extract(localTime, 'localTime')}),
						('TransactionReference', {'value': extract(transactionReference, 'transactionReference')}),
						('SenderName', { 'children':any_or_none() }),
						('SenderAddress', { 'children':any_or_none() }),
						('FundingCard', { 'children': [
								('AccountNumber',{'value': extract(currency, 'accountNumber') }  )								
						]}),
						('FundingSource', {'value': extract(fundingSource, 'fundingSource')}),
						('ReceiverName', { 'children':any_or_none() }),
						('ReceiverAddress', {'value': any_or_none() }),
						('ReceivingMapped', { 'children': [
								('SubscriberId', {'value': extract(subscriberId, 'subscriberId') }),
								('SubscriberType', {'value': extract(subscriberType, 'subscriberType') }),
						]}),
						('ReceivingAmount', { 'children': [
								('Value', {'value': extract(value, 'value') }),
								('Currency', {'value': extract(currency, 'currency') }),
						]}),
						('ICA', {'value': extract(ica, 'ica')}),
						('ProcessorId', {'value': extract(processorId, 'processorId')}),
						('RoutingAndTransitNumber', {'value': extract(routingAndTransitNumber, 'routingAndTransitNumber')}),
						('CardAcceptor', { 'children':any_or_none() }),
						('TransactionDesc', {'value': extract(transactionDesc, 'transactionDesc')}),
						ifpresent(('MerchantId',{'value': any_or_none()})),
						ifpresent(('Channel',   {'value': extract(channel, 'channel')})),
						any_or_none() ]}
				)
																	
						
	return with_('xml', ret)




###############################################################################
# TMS/Payment response
###############################################################################

def m_tms_payment_response(transactionReference, settlementDate, submitDateTime, requestId = "333000", systemTraceAuditNumber = "503943",
	networkReferenceNumber = "411773828", responseCode = "00",
	description = "Approved or completed successfully",	sanctionScore = "000"): 
	"""
	the body of Payment response or transfert
	"""
	
	ret=u"""	
	<Transfer>
		<RequestId>%(requestId)s</RequestId>
		<TransactionReference>%(transactionReference)s</TransactionReference>
		<TransactionHistory>
			<Transaction>
				<Type>PAYMENT</Type>
				<SystemTraceAuditNumber>%(systemTraceAuditNumber)s</SystemTraceAuditNumber>
				<NetworkReferenceNumber>%(networkReferenceNumber)s</NetworkReferenceNumber>
				<SettlementDate>%(settlementDate)s</SettlementDate>
				<Response>
					<Code>%(responseCode)s</Code>
					<Description>%(description)s</Description>
				</Response>
				<SubmitDateTime>%(submitDateTime)s</SubmitDateTime>
			</Transaction>
		</TransactionHistory>
		<SanctionScore>%(sanctionScore)s</SanctionScore>
	</Transfer>
	""" % locals()
	return ret.encode('utf-8')	
		


###############################################################################
# TMS/check status response
###############################################################################

def m_tms_checkStatus_response(status = "true"): 
	"""
	the body of checkStatus response
	"""
	
	ret=u"""	
		<Status>%(status)s</Status>
	""" % locals()
	return ret.encode('utf-8')	


###############################################################################
# TMS/TransactionStatus request
###############################################################################

"""
<?xml version="1.0" encoding="UTF-8"?>
<TransactionStatusRequest>
    <TransactionReference>1000000000133051196</TransactionReference>
</TransactionStatusRequest>
"""

def mw_tms_transactionStatusRequest(transactionReference = any()):
	ret =  ('TransactionStatusRequest', {'children': [	
									('TransactionReference', {'value': extract(transactionReference, 'transactionReference')})
																										]
																			}
					)
	return with_('xml', ret)	
		
###############################################################################
# TMS/TransactionStatus response
###############################################################################	


def m_tms_transactionStatusResponse(transactionReference, settlementDate, submitDateTime, type = "PAYMENT",requestId = "333000",
	systemTraceAuditNumber = "503943", networkReferenceNumber = "411773828", responseCode = "00",
	description = "Approved or completed successfully",	sanctionScore = "000"): 
	"""
	send a transaction status response
	<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<TransactionStatusResponse>
<Transfer>
<RequestId>400398</RequestId>
<TransactionReference>0299999917719282101</TransactionReference>
<TransactionHistory>
<Transaction>
<Type>FUNDING</Type>
<SystemTraceAuditNumber>073147</SystemTraceAuditNumber>
<NetworkReferenceNumber>412371234</NetworkReferenceNumber>
<SettlementDate>0626</SettlementDate>
<Response>
<Code>00</Code>
<Description>Approved or completed successfully</Description>
</Response>
<SubmitDateTime>2012-06-25T19:28:23Z</SubmitDateTime>
</Transaction>
<Transaction>
<Type>PAYMENT</Type>
<SystemTraceAuditNumber>073147</SystemTraceAuditNumber>
<NetworkReferenceNumber>412371234</NetworkReferenceNumber >
<SettlementDate>0626</SettlementDate>
<Response>
<Code>00</Code>
<Description>Approved or completed successfully</Description>
</Response>
<SubmitDateTime>2012-06-25T19:28:23Z</SubmitDateTime>
</Transaction>
</TransactionHistory>
</Transfer>
</TransactionStatus>
	"""
	
	ret=u"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
					<TransactionStatusResponse>
						<Transfer>
							<RequestId>%(requestId)s</RequestId>
							<TransactionReference>%(transactionReference)s</TransactionReference>
							<TransactionHistory>
								<Transaction>
									<Type>%(type)s</Type>
									<SystemTraceAuditNumber>%(systemTraceAuditNumber)s</SystemTraceAuditNumber>
									<NetworkReferenceNumber>%(networkReferenceNumber)s</NetworkReferenceNumber >
									<SettlementDate>%(settlementDate)s</SettlementDate>
									<Response>
										<Code>%(responseCode)s</Code>
										<Description>%(description)s</Description>
									</Response>
									<SubmitDateTime>%(submitDateTime)s</SubmitDateTime>
								</Transaction>
							</TransactionHistory>
						</Transfer>
					</TransactionStatusResponse>
	"""	% locals()
	return ret.encode('utf-8')
	
	
###############################################################################
# TMS/TransferReversal request
###############################################################################		

def m_mfs_depositRemittance_response(correlationId, code = "depositremittance-3017-0000-S", status = "OK", description = "The Transaction is completed successfully."):
	return with_('json', {
		"DepositRemittanceResponse":{
			"ResponseHeader":{
				"GeneralResponse":{
					"correlationID":correlationId,
					"status":status,
					"code":code,
					"description":description
				}
			},
			"ResponseBody":{
				"transactionId":"CI141015.1453.A00101"
			}
		}
	}
)


###############################################################################
# TMS/TransferReversal response
###############################################################################		

def m_mfs_faultDepositRemittance_response(correlationId, errorDescription = "my god, this is an error", code = "depositremittance-3017-3001-E", status = "NOK"):
	return with_('json', {
		"Fault": {
			"faultcode":"env:Server",
			"faultstring":errorDescription,
			"detail": {
				"DepositRemittanceFault": {
					"ResponseHeader": {
						"GeneralResponse": {
							"correlationID": correlationId,
							"status": status,
							"code": code,
							"description": errorDescription
							}
						}
					}
				}
			}
		}
		)		

###############################################################################
# TMS/error response
###############################################################################	


def m_tms_error(responseCode, responseDescription = "dummy Description", requestId = "333000", source = "SYSTEM",
	reasonCode = "DECLINE", recoverable = "false"):

	"""
	send an error like this : 
<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Errors>
    <Error>
        <RequestId>284166</RequestId>
        <Source>SYSTEM</Source>
        <ReasonCode>DECLINE</ReasonCode>
        <Recoverable>false</Recoverable>
        <Details>
            <Detail>
                <Name>ResponseCode</Name>
                <Value>51</Value>
            </Detail>
            <Detail>
                <Name>ResponseDescription</Name>
                <Value>Not sufficient funds</Value>
            </Detail>
        </Details>
    </Error>
</Errors>
	"""
	ret=u"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?><Errors><Error><RequestId>%(requestId)s</RequestId><Source>%(source)s</Source><ReasonCode>%(reasonCode)s</ReasonCode><Recoverable>%(recoverable)s</Recoverable><Details><Detail><Name>ResponseCode</Name><Value>%(responseCode)s</Value></Detail><Detail><Name>ResponseDescription</Name><Value>%(responseDescription)s</Value></Detail></Details></Error></Errors>""" % locals()
	return ret.encode('utf-8')



#def m_tms_error(transactionReference, settlementDate, submitDateTime, requestId = "333000", systemTraceAuditNumber = "503943",
#	networkReferenceNumber = "411773828", responseCode = "00",
#	description = "Approved or completed successfully",	sanctionScore = "000"	):
#	"""
#	send error payment response
#	"""
#
#	ret=u"""	
#	<Transfer>
#		<RequestId>%(requestId)s</RequestId>
#		<TransactionReference>%(transactionReference)s</TransactionReference>
#		<TransactionHistory>
#			<Transaction>
#				<Type>PAYMENT</Type>
#				<SystemTraceAuditNumber>%(systemTraceAuditNumber)s</SystemTraceAuditNumber>
#				<NetworkReferenceNumber>%(networkReferenceNumber)s</NetworkReferenceNumber>
#				<SettlementDate>%(settlementDate)s</SettlementDate>
#				<Response>
#					<Code>%(responseCode)s</Code>
#					<Description>%(description)s</Description>
#				</Response>
#				<SubmitDateTime>%(submitDateTime)s</SubmitDateTime>
#			</Transaction>
#		</TransactionHistory>
#		<SanctionScore>%(sanctionScore)s</SanctionScore>
#	</Transfer>
#	""" % locals()
#	return ret.encode('utf-8')

###############################################################################
# TMS/transfertReversal request
###############################################################################


def mw_tms_transfertReversal_request(ica = any(), transactionReference = any(),
	reversalReason = "Transaction rejected"):
	"""
	check the body of transfertReversal request
<?xml version="1.0" encoding="UTF-8 "?>
<TransferReversalRequest>
   <ICA>999999</ICA>
   <TransactionReference>4239920003040253011</TransactionReference>
   <ReversalReason>Transaction rejected</ReversalReason>
</TransferReversalRequest>
	"""

	ret =  ('TransferReversalRequest', {'children': [
						('ICA', {'value': extract(ica, 'ica')}),
						('TransactionReference', {'value': extract(transactionReference, 'transactionReference')}),
						('ReversalReason', {'value': extract(reversalReason, 'reversalReason')}),
					]}
				)
						
	return with_('xml', ret)


###############################################################################
# TMS/transfertReversal response
###############################################################################

def m_tms_transfertReversal_response(transactionReference, settlementDate, submitDateTime,
	requestId = "333000", originalRequestId = "333000",  systemTraceAuditNumber = "503943",
	networkReferenceNumber = "411773828", responseCode = "00",
	description = "Approved or completed successfully"): 
	"""
	the body of transfertReversal response
<?xml version="1.0" encoding="UTF-8"?>

<TransferReversal>     
	<RequestId>1023</RequestId>     
	<OriginalRequestId>1005</OriginalRequestId>     
	<TransactionReference>0999999034810154901</TransactionReference>     
	<TransactionHistory>        
		<Transaction>            
			<Type>FUNDINGREVERSAL</Type>            
			<SystemTraceAuditNumber>192325</SystemTraceAuditNumber>            
			<NetworkReferenceNumber>214374824</NetworkReferenceNumber >            
			<SettlementDate>1214</SettlementDate>            
			<Response>                
				<Code>00</Code>                
				<Description>Approved or completed successfully</Description>           
			</Response>           
			<SubmitDateTime>2010-12-14T10:20:30</SubmitDateTime>        
		</Transaction>
	</TransactionHistory> 
</TransferReversal> 	
	"""
	
	ret=u"""	
	<TransferReversal>
		<RequestId>%(requestId)s</RequestId>
		<OriginalRequestId>%(originalRequestId)s</OriginalRequestId>     		
		<TransactionReference>%(transactionReference)s</TransactionReference>
		<TransactionHistory>
			<Transaction>
				<Type>FUNDINGREVERSAL</Type>
				<SystemTraceAuditNumber>%(systemTraceAuditNumber)s</SystemTraceAuditNumber>
				<NetworkReferenceNumber>%(networkReferenceNumber)s</NetworkReferenceNumber>
				<SettlementDate>%(settlementDate)s</SettlementDate>
				<Response>
					<Code>%(responseCode)s</Code>
					<Description>%(description)s</Description>
				</Response>
				<SubmitDateTime>%(submitDateTime)s</SubmitDateTime>
			</Transaction>
		</TransactionHistory>
	</TransferReversal>
	""" % locals()
	return ret.encode('utf-8')	
		
		

###############################################################################
# token request
###############################################################################


def mw_tokenization_request(accountNumber = any()): 
	"""
	check the body of tokenization  request
Body:
<?xml version="1.0" encoding="UTF-8"?>
<token_request>
<account_number>%(account_number)</account_number>
</token_request>
	"""
# <account_number>pan:5184680430000006</account_number>
	ret =  ('token_request', {'children': [	
									('account_number', {'value': extract(accountNumber, 'accountNumber')})
																										]
																			}
					)
	return with_('xml', ret)	


###############################################################################
# token response
###############################################################################


def m_tokenization_response(mahstoken): 
	"""
	the body of PanEligibility response
	"""
	ret=u"""<?xml version="1.0" encoding="utf-8" standalone="yes"?>
			<token>%(mahstoken)s</token>
			""" % locals()
	
	return ret.encode('utf-8')


