from zipfile import ZipFile
import datetime
import calendar
import json

import pandas as pd

class DateNotValidException(Exception):
    pass

class FeedNotValidException(Exception):
    pass

REQUIRED_FILES = [
    'agency.txt', 'stops.txt', 'routes.txt', 'trips.txt', 'stop_times.txt'
    ]
OPTIONAL_FILES = [
    'calendar.txt', 'calendar_dates.txt', 'fare_attributes.txt', 
    'fare_rules.txt', 'shapes.txt', 'frequencies.txt', 'transfers.txt', 
    'pathways.txt', 'levels.txt', 'translations.txt', 'feed_info.txt', 
    'attributions.txt'
    ]


class GTFS:
    """A representation of a single static GTFS feed and associated data. 
    
    GTFS holds, as Pandas data frames, the various datasets as defined by the
    GTFS static protocol (http://gtfs.org/reference/static). Optional datasets
    are set to None if data is not passed.

    :param agency: Transit agencies with service represented in this dataset.
    :type agency: :py:mod:`pandas.DataFrame`
    :param stops: Stops where vehicles pick up or drop off riders. Also defines 
        stations and station entrances.
    :type stops: :py:mod:`pandas.DataFrame`
    :param routes: Transit routes. A route is a group of trips that are 
        displayed to riders as a single service.
    :type routes: :py:mod:`pandas.DataFrame`
    :param trips: Trips for each route. A trip is a sequence of two or more 
        stops that occur during a specific time period.
    :type trips: :py:mod:`pandas.DataFrame`
    :param stop_times: Times that a vehicle arrives at and departs from stops for each trip.
    :type stop_times: :py:mod:`pandas.DataFrame`
    :param calendar: Service dates specified using a weekly schedule with 
        start and end dates. This file is required unless all dates of service 
        are defined in calendar_dates.txt.
    :type calendar: :py:mod:`pandas.DataFrame`, conditionally required
    :param calendar_dates: Exceptions for the services defined in `calendar`. 
        If `calendar` is omitted, then calendar_dates.txt is required and must contain all dates of service.
    :type calendar_dates: :py:mod:`pandas.DataFrame`, conditionally required

    :param fare_attributes: Fare information for a transit agency's routes.
    :type fare_attributes: :py:mod:`pandas.DataFrame`, optional
    :param fare_rules: 	Rules to apply fares for itineraries.
    :type fare_rules: :py:mod:`pandas.DataFrame`, optional
    :param shapes: Rules for mapping vehicle travel paths, sometimes referred 
        to as route alignments.
    :type shapes: :py:mod:`pandas.DataFrame`, optional
    :param frequencies: Headway (time between trips) for headway-based service 
        or a compressed representation of fixed-schedule service.
    :type frequencies: :py:mod:`pandas.DataFrame`, optional
    :param transfers: Rules for making connections at transfer points between 
        routes.
    :type transfers: :py:mod:`pandas.DataFrame`, optional
    :param pathways: Pathways linking together locations within stations.
    :type pathways: :py:mod:`pandas.DataFrame`, optional
    :param levels: Levels within stations.
    :type levels: :py:mod:`pandas.DataFrame`, optional
    :param feed_info: Dataset metadata, including publisher, version, 
        and expiration information.
    :param translations: In regions that have multiple official languages, 
        transit agencies/operators typically have language-specific names and 
        web pages. In order to best serve riders in those regions, it is useful 
        for the dataset to include these language-dependent values..
    :type translations: :py:mod:`pandas.DataFrame`, optional
    :type feed_info: :py:mod:`pandas.DataFrame`, optional
    :param attributions: Dataset attributions.
    :type attributions: :py:mod:`pandas.DataFrame`, optional
    
    :raises FeedNotValidException: An exception indicating an invalid feed.
    """
    def __init__(self, agency, stops, routes, trips, stop_times, 
        calendar=None, calendar_dates=None, fare_attributes=None, 
        fare_rules=None, shapes=None, frequencies=None, transfers=None, 
        pathways=None, levels=None, translations=None, feed_info=None, 
        attributions=None):
        """Constructs and validates the datasets for the GTFS object.
        
        All parameters should be valid Pandas DataFrame objects that follow
        the structure corresponding to the dataset as defined by the GTFS
        standard (http://gtfs.org/reference/static).
        """

        # Mandatory Files
        self.agency = agency
        self.stops = stops 
        self.routes = routes
        self.trips = trips 
        self.stop_times = stop_times

        # Pairwise Mandatory Files
        self.calendar = calendar
        self.calendar_dates = calendar_dates

        if self.calendar is None and self.calendar_dates is None:
            raise FeedNotValidException("One of calendar or calendar_dates is required.")

        # Optional Files
        self.fare_attributes = fare_attributes
        self.fare_rules = fare_rules
        self.shapes = shapes
        self.frequencies = frequencies
        self.transfers = transfers
        self.pathways = pathways
        self.levels = levels
        self.attributions = attributions
        self.translations = translations
        self.feed_into = feed_info


    @staticmethod
    def load_zip(filepath):
        """Creates a :class:`GTFS` object from a zipfile containing the
        appropriate data.

        :param filepath: The filepath of the zipped GTFS feed.
        :type filepath: str

        :return: A :class:`GTFS` object with loaded and validated data.
        """
        with ZipFile(filepath, 'r') as zip_file:

            # Deal with nested files
            filepaths = dict()
            print(REQUIRED_FILES + OPTIONAL_FILES)
            for req in REQUIRED_FILES + OPTIONAL_FILES:
                filepaths[req] = None
            for file in zip_file.namelist():
                for req in REQUIRED_FILES + OPTIONAL_FILES:
                    if req in file:
                        filepaths[req] = file

            # Create pandas objects of the entire feed
            agency = pd.read_csv(
                zip_file.open(filepaths["agency.txt"]),
                dtype={
                    'agency_id': str, 'agency_name': str, 'agency_url': str,
                    'agency_timezone': str, 'agency_lang': str,
                    'agency_phone': str, 'agency_fare_url': str,
                    'agency_email': str
                },
                skipinitialspace=True
            )
            stops = pd.read_csv(
                zip_file.open(filepaths["stops.txt"]),
                dtype={
                    'stop_id': str, 'stop_code': str, 'stop_name': str,
                    'stop_desc': str, 'stop_lat': float, 'stop_lon': float,
                    'zone_id': str, 'stop_url': str, 'location_type': 'Int64',
                    'parent_station': str, 'stop_timezone': str,
                    'wheelchair_boarding': 'Int64', 'level_id': str,
                    'platform_code': str
                },
                skipinitialspace=True
            )
            routes = pd.read_csv(
                zip_file.open(filepaths["routes.txt"]),
                dtype={
                    'route_id': str, 'agency_id': str, 'route_short_name': str,
                    'route_long_name': str, 'route_desc': str,
                    'route_type': int, 'route_url': str, 'route_color': str,
                    'route_text_color': str, 'route_short_order': int
                },
                skipinitialspace=True
            )
            trips = pd.read_csv(
                zip_file.open(filepaths["trips.txt"]),
                dtype={
                    'route_id': str, 'service_id': str, 'trip_id': str,
                    'trip_headsign': str, 'trip_short_name': str,
                    'direction_id': 'Int64', 'block_id': str, 'shape_id': str,
                    'wheelchair_accessible': 'Int64', 'bikes_allowed': 'Int64'
                },
                skipinitialspace=True
            )
            stop_times = pd.read_csv(
                zip_file.open(filepaths["stop_times.txt"]),
                dtype={
                    'trip_id': str, 'arrival_time': str, 'departure_time': str,
                    'stop_id': str, 'stop_sequence': int, 'stop_headsign': str,
                    'pickup_type': 'Int64', 'drop_off_type': 'Int64', 
                    'shape_dist_traveled': float, 'timepoint': 'Int64'
                },
                skipinitialspace=True
            )

            if filepaths["calendar.txt"] in zip_file.namelist():
                calendar = pd.read_csv(
                    zip_file.open(filepaths["calendar.txt"]), 
                    dtype={
                        'service_id': str,'monday': bool, 'tuesday': bool,
                        'wednesday': bool, 'thursday': bool, 'friday': bool,
                        'saturday': bool, 'sunday': bool, 'start_date': str,
                        'end_date': str
                    },
                    parse_dates=['start_date', 'end_date'],
                    skipinitialspace=True
                )

            else:
                calendar = None

            if filepaths["calendar_dates.txt"] in zip_file.namelist():
                calendar_dates = pd.read_csv(
                    zip_file.open(filepaths["calendar_dates.txt"]),
                    dtype={
                        'service_id': str, 'date': str, 'exception_type': int
                    },
                    parse_dates=['date'],
                    skipinitialspace=True
                )
                if calendar_dates.shape[0] == 0:
                    calendar_dates = None
            else:
                calendar_dates = None

            if filepaths["fare_attributes.txt"] in zip_file.namelist():
                fare_attributes = pd.read_csv(
                    zip_file.open(filepaths["fare_attributes.txt"]),
                    dtype={
                        'fare_id': str, 'price': float, 'currency_type': str,
                        'payment_method': int, 'transfers': 'Int64',
                        'agency_id': str, 'transfer_duration': 'Int64'
                    },
                    skipinitialspace=True
                )
            else:
                fare_attributes = None

            if filepaths["fare_rules.txt"] in zip_file.namelist():
                fare_rules = pd.read_csv(
                    zip_file.open(filepaths["fare_rules.txt"]),
                    dtype={
                        'fare_id': str, 'route_id': str, 'origin_id': str,
                        'destination_id': str, 'contains_id': str
                    },
                    skipinitialspace=True    
                )
            else:
                fare_rules = None
            
            if filepaths["shapes.txt"] in zip_file.namelist():
                shapes = pd.read_csv(
                    zip_file.open(filepaths["shapes.txt"]),
                    dtype={
                        'shape_id': str, 'shape_pt_lat': float,
                        'shape_pt_lon': float, 'shape_pt_sequence': int,
                        'shape_dist_traveled': float
                    },
                    skipinitialspace=True
                )
            else:
                shapes = None

            if filepaths["frequencies.txt"] in zip_file.namelist():
                frequencies = pd.read_csv(
                    zip_file.open(filepaths["frequencies.txt"]),
                    dtype={
                        'trip_id': str, 'start_time': str, 'end_time': str,
                        'headway_secs': int, 'exact_times': int
                    },
                    parse_dates=['start_time', 'end_time'],
                    skipinitialspace=True
                )
            else:
                frequencies = None

            if filepaths["transfers.txt"] in zip_file.namelist():
                transfers = pd.read_csv(
                    zip_file.open(filepaths["transfers.txt"]),
                    dtype={
                        'from_stop_id': str, 'to_stop_id': str,
                        'transfer_type': 'Int64', 'min_transfer_time': 'Int64'
                    },
                    skipinitialspace=True
                )
            else:
                transfers = None

            if filepaths["pathways.txt"] in zip_file.namelist():
                pathways = pd.read_csv(
                    zip_file.open(filepaths["pathways.txt"]),
                    dtype={
                        'pathway_id': str, 'from_stop_id': str, 
                        'to_stop_id': str, 'pathway_mode': int,
                        'is_bidirectional': str, 'length': 'float64',
                        'traversal_time': 'Int64', 'stair_count': 'Int64',
                        'max_slope': 'float64', 'min_width': 'float64',
                        'signposted_as': str, 'reverse_signposted_as': str
                    },
                    skipinitialspace=True
                )
            else:
                pathways = None
            
            if filepaths["levels.txt"] in zip_file.namelist():
                levels = pd.read_csv(
                    zip_file.open(filepaths["levels.txt"]),
                    dtype={
                        'level_id': str, 'level_index': float,
                        'level_name': str
                    },
                    skipinitialspace=True
                )
            else:
                levels = None

            if filepaths["translations.txt"] in zip_file.namelist():
                translations = pd.read_csv(
                    zip_file.open(filepaths["translations.txt"]),
                    dtype={
                        'table_name': str, 'field_name': str, 'language': str,
                        'translation': str, 'record_id': str,
                        'record_sub_id': str, 'field_value': str
                    },
                    skipinitialspace=True
                )
                feed_info = pd.read_csv(
                    zip_file.open(filepaths["feed_info.txt"]),
                    dtype={
                        'feed_publisher_name': str, 'feed_publisher_url': str,
                        'feed_lang': str, 'default_lang': str,
                        'feed_start_date': str, 'feed_end_date': str,
                        'feed_version': str, 'feed_contact_email': str,
                        'feed_contact_url': str
                    },
                    skipinitialspace=True
                )
            elif filepaths["feed_info.txt"] in zip_file.namelist():
                feed_info = pd.read_csv(
                    zip_file.open(filepaths["feed_info.txt"]),
                    dtype={
                        'feed_publisher_name': str, 'feed_publisher_url': str,
                        'feed_lang': str, 'default_lang': str,
                        'feed_start_date': str, 'feed_end_date': str,
                        'feed_version': str, 'feed_contact_email': str,
                        'feed_contact_url': str
                    },
                    skipinitialspace=True   
                )
                translations=None
            else:
                translations = None
                feed_info = None

            if filepaths["attributions.txt"] in zip_file.namelist():
                attributions = pd.read_csv(
                    zip_file.open("attributions.txt"),
                    dtype={
                        'attribution_id': str, 'agency_id': str, 
                        'route_id': str, 'trip_id': str,
                    },
                    skipinitialspace=True
                )
            else:
                attributions = None

        return GTFS(agency, stops, routes, trips, stop_times, 
            calendar=calendar, calendar_dates=calendar_dates, 
            fare_attributes=fare_attributes, fare_rules=fare_rules, 
            shapes=shapes, frequencies=frequencies, transfers=transfers,
            pathways=pathways, levels=levels, translations=translations, 
            feed_info=feed_info, attributions=attributions)
    
    def summary(self):
        """ Assemble a series of attributes summarizing the GTFS feed with the
        following columns:

        * *agencies*: list of agencies in feed
        * *total_stops*: the total number of stops in the feed
        * *total_routes*: the total number of routes in the feed
        * *total_trips*: the total number of trips in the feed
        * *total_stops_made*: the total number of stop_times events
        * *first_date*: the first date the feed is valid for
        * *last_date*: the last date the feed is valid for
        * *total_shapes* (optional): the total number of shapes. 

        :returns: A :py:mod:`pandas.Series` containing the relevant data.
        """

        summary = pd.Series(dtype=str)
        summary['agencies'] = self.agency.agency_name.tolist()
        summary['total_stops'] = self.stops.shape[0]
        summary['total_routes'] = self.routes.shape[0]
        summary['total_trips'] = self.trips.shape[0]
        summary['total_stops_made'] = self.stop_times.shape[0]
        if self.calendar is not None:
            summary['first_date'] = self.calendar.start_date.min()
            summary['last_date'] = self.calendar.end_date.max()
        else:
            summary['first_date'] = self.calendar_dates.date.min()
            summary['last_date'] = self.calendar_dates.date.max()
        if self.shapes is not None:
            summary['total_shapes'] = self.shapes.shape[0]

        return summary

    def valid_date(self, date):
        """Checks whether the provided date falls within the feed's date range
        
        :param date: A datetime object with the date to be validated.
        :type date: :py:mod:`datetime.date`
        :return: `True` if the date is a valid one, `False` otherwise.
        :rtype: bool
        """

        summary = self.summary()
        if type(date) == str:
            date = datetime.datetime.strptime(date, "%Y%m%d")
        if summary.first_date > date or summary.last_date < date:
            return False
        else:
            return True

    def day_trips(self, date):
        """Finds all the trips that occur on a specified day. This method
        accounts for exceptions included in the `calendar_dates` dataset.

        :param date: The day to check
        :type date: :py:mod:`datetime.date`

        :return: A slice of the `trips` dataframe which corresponds to the
            provided date.
        :rtype: :py:mod:`pandas.DataFrame`
        """

        # First, get all standard trips that run on that particular day of the week
        if not self.valid_date(date):
            raise DateNotValidException

        dayname = date.strftime("%A").lower()
        date_compare = pd.to_datetime(date)
        if self.calendar is not None:
            service_ids = self.calendar[(self.calendar[dayname] == 1) & (self.calendar.start_date <= date_compare) & (self.calendar.end_date >= date_compare)].service_id
            if self.calendar_dates is not None:
                service_ids = service_ids.append(self.calendar_dates[(self.calendar_dates.date == date_compare) & (self.calendar_dates.exception_type == 1)].service_id)
                service_ids = service_ids[~service_ids.isin(self.calendar_dates[(self.calendar_dates.date == date_compare) & (self.calendar_dates.exception_type == 2)].service_id)]
        else:
            service_ids = self.calendar_dates[(self.calendar_dates.date == date_compare) & (self.calendar_dates.exception_type == 1)].service_id
        return self.trips[self.trips.service_id.isin(service_ids)]

    def stop_summary(self, date, stop_id):
        """Assemble a series of attributes summarizing a stop on a particular
        day. The following columns are returned:

        * *stop_id*: The ID of the stop summarized
        * *total_visits*: The total number of times a stop is visited
        * *first_arrival*: The earliest arrival of the bus for the day
        * *last_arrival*: The latest arrival of the bus for the day
        * *service_time*: The total service span, in hours
        * *average_headway*: Average time in minutes between arrivals

        :param date: The day to summarize
        :type date: :py:mod:`datetime.date`
        :param stop_id: The ID of the stop to summarize.
        :type stop_id: str
        :return: A :py:mod:`pandas.Series` object containing the summarized
            data.
        """

        # Create a summary of stops for a given stop_id

        trips = self.day_trips(date)
        stop_times = self.stop_times[self.stop_times.trip_id.isin(trips.trip_id) & (self.stop_times.stop_id == stop_id)]

        summary = self.stops[self.stops.stop_id == stop_id].iloc[0]
        summary['total_visits'] = len(stop_times.index)
        summary['first_arrival'] = stop_times.arrival_time.min()
        summary['last_arrival'] = stop_times.arrival_time.max()
        summary['service_time'] = (int(summary.last_arrival.split(":")[0]) + int(summary.last_arrival.split(":")[1])/60.0 + int(summary.last_arrival.split(":")[2])/3600.0) - (int(stop_times.arrival_time.min().split(":")[0]) + int(stop_times.arrival_time.min().split(":")[1])/60.0 + int(stop_times.arrival_time.min().split(":")[2])/3600.0)
        summary['average_headway'] = (summary.service_time/summary.total_visits)*60
        return summary

    def route_summary(self, date, route_id):
        """Assemble a series of attributes summarizing a route on a particular
        day. The following columns are returned:
        
        * *route_id*: The ID of the route summarized
        * *total_trips*: The total number of trips made on the route that day
        * *first_departure*: The earliest departure of the bus for the day
        * *last_arrival*: The latest arrival of the bus for the day
        * *service_time*: The total service span of the route, in hours
        * *average_headway*: Average time in minutes between trips on the route

        :param date: The day to summarize.
        :type date: :py:mod:`datetime.date`
        :param route_id: The ID of the route to summarize
        :type route_id: str
        :return: A :py:mod:`pandas.Series` object containing the summarized 
            data.
        """

        trips = self.day_trips(date)
        trips = trips[trips.route_id == route_id]
        stop_times = self.stop_times[self.stop_times.trip_id.isin(trips.trip_id)]
        summary = pd.Series()
        summary['route_id'] = route_id
        summary['total_trips'] = len(trips.index)
        summary['first_departure'] = stop_times.departure_time.min()
        summary['last_arrival'] = stop_times.arrival_time.max()
        summary['service_time'] = (int(summary.last_arrival.split(":")[0]) + int(summary.last_arrival.split(":")[1])/60.0 + int(summary.last_arrival.split(":")[2])/3600.0) - (int(summary.first_departure.split(":")[0]) + int(summary.first_departure.split(":")[1])/60.0 + int(summary.first_departure.split(":")[2])/3600.0)
        stop_id = stop_times.iloc[0].stop_id
        min_dep = stop_times[stop_times.stop_id == stop_id].departure_time.min()
        max_arr = stop_times[stop_times.stop_id == stop_id].arrival_time.max()
        visits = stop_times[stop_times.stop_id == stop_id].trip_id.count()
        route_headway = int(max_arr.split(":")[0]) + int(max_arr.split(":")[1])/60.0 + int(max_arr.split(":")[2])/3600.0 - (int(min_dep.split(":")[0]) + int(min_dep.split(":")[1])/60.0 + int(min_dep.split(":")[2])/3600.0)
        summary['average_headway'] = 60*route_headway/visits
        return summary
    
    def routes_summary(self, date):
        """Summarizes all routes in a given day. The columns of the resulting
        dataset match the columns of :func:`route_summary`

        :param date: The day to summarize.
        :type date: :py:mod:`datetime.date`
        :return: A :py:mod:`pandas.DataFrame` object containing the summarized
            data.
        """

        trips = self.day_trips(date)
        if "direction_id" in trips.columns: 
            trips = trips[trips.direction_id == 0]
        stop_times = self.stop_times[self.stop_times.trip_id.isin(trips.trip_id)]
        stop_times = pd.merge(stop_times, trips, on="trip_id", how="left")
        route_trips = trips[["route_id", "trip_id"]].groupby("route_id", as_index=False).count()
        route_trips['trips'] = route_trips.trip_id
        first_departures = stop_times[["route_id", "departure_time"]].groupby("route_id", as_index=False).min()
        last_arrivals = stop_times[["route_id", "arrival_time"]].groupby("route_id", as_index=False).max()
        summary = pd.merge(route_trips, first_departures, on=["route_id"])
        summary = pd.merge(summary, last_arrivals, on=["route_id"])
        summary['service_time'] = (summary.arrival_time.str.split(":", -1, expand=True)[0].astype(int) + summary.arrival_time.str.split(":", -1, expand=True)[1].astype(int)/60.0 + summary.arrival_time.str.split(":", -1, expand=True)[2].astype(int)/3600.0) - \
            (summary.departure_time.str.split(":", -1, expand=True)[0].astype(int) + summary.departure_time.str.split(":", -1, expand=True)[1].astype(int)/60.0 + summary.departure_time.str.split(":", -1, expand=True)[2].astype(int)/3600.0)
        summary['average_headway'] = 60*summary.service_time/summary.trips
        summary["last_arrival"] = summary.arrival_time 
        summary["first_departure"] = summary.departure_time
        summary = summary[["route_id", "trips", "first_departure", "last_arrival", "average_headway"]]
        summary = pd.merge(self.routes, summary, on="route_id", how="inner")
        return summary
    
    def service_hours(self, date, start_time=datetime.time(0, 0), end_time=datetime.time(23, 59)):
        """Computes the total service hours delivered for a specified date
        within a specified time slice.

        **Note:** This function currently does not support end_times that 
        are past 23:59. A new time slice for the following day must be 
        calculated separately.

        :param date: The date to calculate.
        :type date: :py:mod:`datetime.date`
        :param start_time: The time of day to start the calculation from.
            Defaults to 0:00
        :type start_time: :py:mod:`datetime.time`, optional
        :param end_time: The time of day to start the calculation from.
            Defaults to 23:59
        :type end_time: :py:mod:`datetime.time`, optional
        :raises DateNotValidException: An exception indicating an invalid date.
        :returns: The total service hours.
        :rtype: float
        """

        if not self.valid_date(date):
            raise DateNotValidException(f"Date falls outside of feed span: {date}")

        # First, we need to get the service_ids that apply.
        service_ids = []
        start = start_time.strftime("%H:%M:%S")
        end = end_time.strftime("%H:%M:%S")
        # Start with the calendar
        if self.calendar is not None:
            dow = date.strftime("%A").lower()
            service_ids.extend(self.calendar[(self.calendar[dow] == 1) & (self.calendar.start_date.dt.date <= date) & (self.calendar.end_date.dt.date >= date)].service_id.tolist())
        
        # Now handle exceptions if they are there
        if self.calendar_dates is not None:
            to_add = service_ids.extend(self.calendar_dates[(self.calendar_dates.date.dt == date) & self.calendar_dates.exception_type == 1].service_id.tolist())
            to_del = service_ids.extend(self.calendar_dates[(self.calendar_dates.date.dt == date) & self.calendar_dates.exception_type == 2].service_id.tolist())
            if to_add is not None:
                service_ids.extend(to_add)
            # Remove those that should be removed
            if to_del is not None:
                [service_ids.remove(i) for i in to_del]
        
        # Grab all the trips
        trips = self.trips[self.trips.service_id.isin(service_ids)]
        
        # Grab all the stop_times
        stop_times = self.stop_times[self.stop_times.trip_id.isin(trips.trip_id) & (self.stop_times.arrival_time >= start) & (self.stop_times.arrival_time <= end)]
        grouped = stop_times[['trip_id', 'arrival_time']].groupby('trip_id', as_index=False).agg({'arrival_time': ['max', 'min']})
        grouped.columns = ['trip_id', 'max', 'min']
        grouped.dropna()
        max_split = grouped['max'].str.split(":", expand=True).astype(int)
        min_split = grouped['min'].str.split(":", expand=True).astype(int)
        grouped['diff'] = (max_split[0] - min_split[0]) + (max_split[1] - min_split[1])/60 + (max_split[2] - min_split[2])/3600
        return(grouped['diff'].sum())

    def trip_distribution(self, start_date, end_date):
        """Summarize the distribution of service by day of week for a given
        date range. Repeated days of the week will be counted multiple times.
        
        :param start_date: The start date for the summary
        :type start_date: :py:mod:`datetime.date`
        :param end_date: The end date for the summary
        :type end_date: :py:mod:`datetime.date`
        
        :return: A :py:mod:`pandas.Series` object containing as indices the 
            days of the week and as values the total number of trips found in the 
            time slice.
        """

        days = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']
        dist = pd.Series(
            index=days, 
            name='trips',
            dtype='int'
            )

        # Start with calendar:
        if self.calendar is not None:
            for dow in dist.index:
                # Get rows where that DOW happens in the date range
                for idx, service in self.calendar[(self.calendar[dow] == True) & (self.calendar.start_date.dt.date <= start_date) & (self.calendar.end_date.dt.date >= end_date)].iterrows():
                    # We'll need the number of a given days of the week in that range to multiply the calendar.
                    week = {}
                    for i in range(((end_date + datetime.timedelta(days=1)) - start_date).days):
                        day       = calendar.day_name[(start_date + datetime.timedelta(days=i+1)).weekday()].lower()
                        week[day] = week[day] + 1 if day in week else 1

                     # Get trips with that service id and add them to the total, only if that day is in there.
                    if dow in week.keys():
                        dist[dow] = dist[dow] + week[dow]*self.trips[self.trips.service_id == service.service_id].trip_id.count()

        # Now check exceptions to add and remove
        if self.calendar_dates is not None:
            # Start by going through all the calendar dates within the date range
            # cd = self.calendar_dates.copy()
            for index, cd in self.calendar_dates[(self.calendar_dates['date'].dt.date >= start_date) & (self.calendar_dates['date'].dt.date <= end_date)].iterrows():
                if cd['exception_type'] == 1:
                    dist[days[cd['date'].dayofweek]] += self.trips[self.trips.service_id == cd['service_id']].trip_id.count()
                else:
                    dist[days[cd['date'].dayofweek]] -= self.trips[self.trips.service_id == cd['service_id']].trip_id.count()

        return dist

    def route_stops_inside(self, path_to_shape, format='geojson'):
        """Count the number of stops a given route has inside a geographical
        boundary or shape.

        :param path_to_shape: A path to the file containing the shapes. This
            file must contain unprojected geospatial information in WGS:84 format.
        :type path_to_shape: str
        :param format: The format of the geospatial file. **Note:** currently,
            only the default `geojson` is supported.
        :type format: str, optional
        :return: A :py:mod:`pandas.DataFrame` object listing each route and
            the number of stops served by that route that fall within the
            provided boundary.
        """

        from shapely.geometry import Point, shape, GeometryCollection
        
        count = 0
        # For starters, let's load a bounding box and check how many stops are in the point
        if format == 'geojson':
            with open(path_to_shape) as f:
                features = json.load(f)["features"]
                boundary = GeometryCollection([shape(feature["geometry"]).buffer(0) for feature in features])
                routes = []
                counts = []
                for idx, route in self.routes.iterrows():
                    # Get all the stops on trips for that route.
                    stops = self.stop_times[self.stop_times.trip_id.isin(self.trips[self.trips.route_id == route.route_id].trip_id)].stop_id.unique()
                # NOTE: buffer(0) is a trick for fixing scenarios where polygons have overlapping coordinates 
                    count = 0
                    for idx, stop in self.stops[self.stops.stop_id.isin(stops)].iterrows():
                        if Point(stop.stop_lon, stop.stop_lat).within(boundary):
                            count += 1
                    routes.append(route.route_id)
                    counts.append(count)
        
        stop_count = pd.DataFrame(counts, index=routes)
        return stop_count

    def trips_at_stops(self, stop_ids, date, start_time=datetime.time(0, 0), end_time=datetime.time(23, 59)):
        """Get a set of unique trips that visit a given stop
        
        :param stop_ids: A list of stop_ids to check for unique trips
        :type stop_ids: list of strings or integers
        :param date: The date to calculate.
        :type date: :py:mod:`datetime.date`
        :param start_time: The time of day to start the calculation from.
            Defaults to 0:00
        :type start_time: :py:mod:`datetime.time`, optional
        :param end_time: The time of day to start the calculation from.
            Defaults to 23:59
        :type end_time: :py:mod:`datetime.time`, optional
        
        :return: A :py:mod:`pandas.DataFrame` as a subset of the 
            :py:attr:`GTFS.trips` dataframe.
        """

        # Start by filtering all stop_trips by the given dateslice
        trips = self.day_trips(date)

        stop_ids = [str(s) for s in stop_ids]

        # Now let's grab the stop_trips
        stop_trips = self.stop_times[(self.stop_times.trip_id.isin(trips.trip_id)) & (self.stop_times.stop_id.isin(stop_ids))]

        # We've got the stop times, so let's grab the unique trips
        unique_trips = stop_trips.trip_id.unique()

        return self.trips[self.trips.trip_id.isin(unique_trips)]




