from __future__ import print_function
import time
import sib_api_v3_sdk
from sib_api_v3_sdk.rest import ApiException
from pprint import pprint

def sendemail(sendto, onetimepw ):
    configuration = sib_api_v3_sdk.Configuration()
    #api key will go here

    api_instance = sib_api_v3_sdk.TransactionalEmailsApi(sib_api_v3_sdk.ApiClient(configuration))
    subject = "confirm this email to proceed with WWU Zero Trust"

    # one time password goes on this line
    html_content = f"<html><body><h1>Enter the following code on the website to proceed {onetimepw} </h1></body></html>"
    sender = {"name":"zero trust team","email":"example@example.com"}
    # send to goes here
    to = [{"email":sendto,"name":"Jane Doe"}]
    #cc = [{"email":"example2@example2.com","name":"Janice Doe"}]
    #bcc = [{"name":"zero trust team","email":"example@example.com"}]
    reply_to = {"email":"wwuzerotrust@gmail.com","admin":"zero trust team"}
    headers = {"Some-Custom-Name":"unique-id-1234"}
    params = {"parameter":"My param value","subject":"New Subject"}
    send_smtp_email = sib_api_v3_sdk.SendSmtpEmail(to=to, bcc=None, cc=None, reply_to=reply_to, headers=headers, html_content=html_content, sender=sender, subject=subject)

    try:
        api_response = api_instance.send_transac_email(send_smtp_email)
        pprint(api_response)
    except ApiException as e:
        print("Exception when calling SMTPApi->send_transac_email: %s\n" % e)

