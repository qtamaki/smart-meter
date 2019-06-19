import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
import settings

# pip install --upgrade firebase-admin

class StoreUtil():
  def __init__(self):
    # Use a service account
    cred = credentials.Certificate(settings.FireStore.certificate_json_file)
    firebase_admin.initialize_app(cred)
    self.db = firestore.client()

  def store(self, dt, pw, pwTotal):
    ref = self.db.collection(u'meter_logs').document(dt.strftime("%Y%m%d%H%M%S"))
    ref.set({
      u'power': str(pw),
      u'total_power': str(pwTotal),
      u'time': dt.strftime("%Y/%m/%d %H:%M:%S")
    })
