from bs4 import BeautifulSoup
import requests

from datetime import datetime
from uuid import uuid4

from tools.handler import Handler
from util.handle_times import HandleTimes


class TravelMonitor:
    def __init__(self, datastore=None):

        self._datastore = datastore or Handler()
        self._handletime = HandleTimes()

        self._tfl = "https://tfl.gov.uk/tube-dlr-overground/status/#"
        self._tubes = [
            "Bakerloo",
            "Elizabeth line",
            "Jubilee",
            "London Overground",
            "Piccadilly",
            "Tram",
            "Waterloo & City",
            "Central",
            "Circle",
            "District",
            "Hammersmith & City",
            "Metropolitan",
            "Northern",
            "Victoria",
            "DLR",
        ]

    def cleaner(self, scraped, string, length):
        """Remove the provided string from the scraped list"""
        try:
            for elem in range(length):
                scraped.remove(string)
        except ValueError:
            pass
        return scraped

    @property
    def scraper(self):
        """scrape the tfl website to retrieve service information"""

        page_to_scrape = requests.get(self._tfl)
        soup = BeautifulSoup(page_to_scrape.text, "html.parser")

        content = soup.findAll(
            "div", attrs={"id": "rainbow-list-tube-dlr-overground-elizabeth-line-tram"}
        )[0].text

        line = content.split("\n")
        length = len(line)

        line = self.cleaner(line, "", length)
        line = self.cleaner(line, "\xa0", length)
        line = self.cleaner(line, "Replan your journey", length)
        line = self.cleaner(line, "Close status", length)
        return line[1:]

    @property
    def constructor(self):
        """construct the services dictionary"""

        line = self.scraper
        tfl = []
        isolater = [line[0]]

        for text in line[1:]:
            if text in self._tubes:
                tfl.append(isolater)
                isolater = []

            isolater.append(text)

        tfl.append(isolater)

        tfl_dict = {}
        for service in tfl:
            tube_name = service[0]
            tfl_dict[tube_name] = {}
            tfl_dict[tube_name]["name"] = tube_name
            tfl_dict[tube_name]["status"] = service[1]
            tfl_dict[tube_name]["message"] = " ".join(service[2:])

        self._datastore.overwrite(db_key="services", db_value=tfl_dict)
        return 200

    def service(self, name):
        """get further service information"""

        if name in self._tubes:
            return self._datastore.get_nested_value(["services", name])
        else:
            return 400

    @property
    def request(self):
        """refresh the service with a clean output message"""

        self.constructor
        tfl_data = self._datastore.get_value("services")
        now_ts = self._handletime.current_timestamp()

        comm = [f"```TFL Services Status Update:"]
        comm.append(
            f"Date [{self._handletime.convert_timestamp(now_ts)}] | TFL Update ID [#{str(uuid4().hex[:10])}]\n"
        )

        for service in tfl_data:
            meta = tfl_data[service]
            comm.append(f"Service: {meta['name']} [ {meta['status']}]")

        return ("\n").join(comm) + "```"
