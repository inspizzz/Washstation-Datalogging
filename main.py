import time
import test as wsapi
import JsonPlug as jp
from datetime import date, datetime

running = True

details = {"username":YOUR_EMAIL,
           "password":YOUR_PASSWORD,
           "client_id":YOUR_CLIENTID {"X_XXXXXXXXXX"},
           "client_secret":YOUR_CLIENT_SECRET {XXXXXXXXXXXXXXXXXXXXXXXXX},
           "Device":YOUR_DEVICE {XXXXXXXX-XXXX-XXXX-XXXX-XXXXXXXXXXXX}
}


if __name__ == "__main__":
  
    # initiate the modules
    api = wsapi.washstation(user=details, debug=True)
    json = jp.Storage()
    
    # connect to the server
    api.login()
    api.refresh()
    api.getProfile()

    # creat / open file to store data in, will make it generate a new file day in day out but for now not
    json.set_file_name(filename=YOUR_FILE_PATH)
    
    
    # start time
    start = time.time()
    
    while running:
      
        # restart connection if time has elapsed
        if time.time() - start > 1000:
            api.refresh()
        
        # update washer variables in the washstation class
        api.getWashers()
        
        # add number of washers available to the file
        json.add_data(data=api.washers_available, time=datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        
        # do this every 5 minutes ( dont set this to a small number as this will just send too many packets to the server)
        time.sleep(5 * 60)
