from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class Country:
    name: str
    capital: str
    flag: str


ASIA = 'Asia'
AFRICA = 'Africa'
EUROPE = 'Europe'
NORTH_AMERICA = 'North America'
SOUTH_AMERICA = 'South America'
OCEANIA = 'OCEANIA'


COUNTRIES: dict[str, Country] = {
    'Afghanistan': Country(name='Afghanistan', capital='Kabul', flag='🇦🇫'),
    'Albania': Country(name='Albania', capital='Tirana', flag='🇦🇱'),
    'Algeria': Country(name='Algeria', capital='Algiers', flag='🇩🇿'),
    'Andorra': Country(name='Andorra', capital='Andorra la Vella', flag='🇦🇩'),
    'Angola': Country(name='Angola', capital='Luanda', flag='🇦🇴'),
    'Antigua and Barbuda': Country(name='Antigua and Barbuda', capital="Saint John's", flag='🇦🇬'),
    'Argentina': Country(name='Argentina', capital='Buenos Aires', flag='🇦🇷'),
    'Armenia': Country(name='Armenia', capital='Yerevan', flag='🇦🇲'),
    'Australia': Country(name='Australia', capital='Canberra', flag='🇦🇺'),
    'Austria': Country(name='Austria', capital='Vienna', flag='🇦🇹'),
    'Azerbaijan': Country(name='Azerbaijan', capital='Baku', flag='🇦🇿'),
}
