from typing import List
from dataclasses import dataclass

@dataclass
class GlassDoorLocationResponse:
    compoundId: str
    countryName: str
    id: str
    label: str
    locationId: int
    locationType: str
    longName: str
    realId: int


def get_location_type(glassDoorLocationResponse: GlassDoorLocationResponse) -> str:
        """
        Private method to map locationType to a human-readable type.
        """
        if glassDoorLocationResponse.locationType == "C":
            return "CITY"
        elif glassDoorLocationResponse.locationType == "S":
            return "STATE"
        elif glassDoorLocationResponse.locationType == "N":
            return "COUNTRY"
        return "UNKNOWN"
    
def get_location_id(glassDoorLocationResponse: GlassDoorLocationResponse) -> int:
        """
        Private method to map locationType to a human-readable type.
        """
        return int(glassDoorLocationResponse.locationId);

def print_locations(glassDoorLocationResponses: list[GlassDoorLocationResponse]):
        """
        Loop over all locations and print the mapped location types.
        """
        for location in glassDoorLocationResponses:
            location_type = get_location_type(location)
            print(f"Location ID: {location.locationId}, Type: {location_type}")
