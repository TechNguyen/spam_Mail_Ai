import pandas as pd
import imaplib
import email
from sklearn.neighbors import KNeighborsClassifier

IMAP_SERVER = 'imap.gmail.com'
USERNAME = 'ndt13102003@gmail.com'
PASSWORD = 'cuxi xkwr ybcn xdhh'

imap = imaplib.IMAP4_SSL(IMAP_SERVER)
imap.login(USERNAME, PASSWORD)
imap.select('inbox')

status, response = imap.search(None, 'ALL')
email_ids = response[0].split()


latest_message_nums = email_ids[-10:] 

df = pd.read_csv('models/spam.csv', usecols=[0, 1], encoding='latin-1')
df.rename(columns={'v1': 'Label', 'v2': 'Message'}, inplace=True)
df['Type'] = df.apply(lambda row: 1 if row.Label == 'ham' else 0, axis=1)

X = list(df['Message'])
y = list(df['Type'])

n_neighbors = 10
knn = KNeighborsClassifier(n_neighbors)

vect = CountVectorizer()
vect.fit(X)

X_train_dtm = vect.transform(X)
knn.fit(X_train_dtm, y)

for email_id in latest_message_nums:
    status, response = imap.fetch(email_id, '(RFC822)')
    raw_email = response[0][1]
    email_message = email.message_from_bytes(raw_email)
    sender = email_message['From']
    subject = email_message['Subject']
    body = ''
    
    if email_message.is_multipart():
        for part in email_message.walk():
            content_type = part.get_content_type()
            if content_type == 'text/plain':
                body = part.get_payload(decode=True).decode('utf-8')
                break
    else:
        body = email_message.get_payload(decode=True).decode('utf-8')
    
    new = [body]
    dtm = vect.transform(new)
    typeofMessage = knn.predict(dtm.toarray())
    
    if typeofMessage == 0:
        print(f"Email from {sender} with subject '{subject}' is not spam")
    else:
        print(f"Email from {sender} with subject '{subject}' is spam")

imap.logout()