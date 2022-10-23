import json
from datetime import datetime


class Storage:
    def __init__(self) -> None:
        
        # file instance
        self.file = None

        # file name for reference
        self.name = None


    def set_file_name(self, filename:str) -> None:
        print(f"[JSON] Filename set to {filename}")

        # set name of the file
        self.name = filename
    
    def open_file(self, mode:str) -> bool:
        print(f"[JSON] Opening file with name {self.name}")

        # open the file
        if self.name:
            try :
                self.file = open(file=self.name, mode=mode, encoding="utf-8")

                # success
                return True
            except:

                # failure
                return False
        else:

            # failure
            return False
        

    def close_file(self) -> None:
        print(f"[JSON] Closing file with name {self.name}")

        # close the file, do not replace the file name
        self.file.close()
        self.file = None


    def add_data(self, data:dict, time:datetime) -> None:
        print(f"[JSON] Adding data to the file")
        
        # reformat time
        date = time.split(" ")[0].split("-")
        time = time.split(" ")[1].split(":")

        # format to be written in
        towrite = {"years":date[0], "months":date[1], "days":date[2], "hours":time[0], "minutes":time[1], "seconds":time[2]}
        for id, value in zip(data.keys(), data.values()):
            towrite.setdefault(id, value)

        # check the length
        self.open_file(mode="r")
        length = len(self.file.readlines())
        self.close_file()

        # empty file?
        if length > 0:

            # write beginning of the file
            self.open_file(mode="r+")
            data = json.load(self.file)
            data["data"].append(towrite)
            self.file.seek(0)
            json.dump(data, self.file, ensure_ascii=False, indent=4, separators=(",", ":"))
            print(f"[JSON] Added {towrite} to file")
            self.close_file()
        else:

            # append to existing dictionary
            self.open_file(mode="a")
            towrite = {"data":[towrite]}
            json.dump(towrite, self.file, ensure_ascii=False, indent=4, separators=(",", ":"))
            self.file.flush()
            print(f"[JSON] Written {towrite}")
            self.close_file()


    def read_data(self) -> list:

        # read all json data from file
        self.open_file(mode="r+")
        a = json.load(self.file)
        self.close_file()

        # return it
        return a["data"]
