from twilio.rest import Client

# Read credentials file
with open('credentials.txt', 'r') as myfile:
  file_data = myfile.read()

# Convert it to dictionary
info_dic = eval(file_data)

# Your Account SID and AUTH TOKEN from twilio.com/console
account_sid = info_dic['ACCOUNT_SID']
auth_token = info_dic['AUTH_TOKEN']

# Set client and send message to check connection
client = Client(account_sid, auth_token)
client.messages.create(to=info_dic['ALERT_NUM'], from_=info_dic['TRIAL_NUM'], body="Hello World")
