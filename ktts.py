import re
import time
from datetime import datetime, date
from functools import wraps

import requests
from bs4 import BeautifulSoup, Tag
from terminaltables import AsciiTable


BASE_URL = "https://kttc.ru"


PREMIUM_TANKS = ["T14", "Type 59", "Pudel", "50TP pr.", "105 leFH18B2", "FCM 36 Pak 40", "T34", "ИС-6", "M4 Improved", "T26E4 SuperPershing", "Panhard EBR 75 (FL 10)", "Т-44-100 (У)", "G142 M48RPz", "E75 TS", "AM 39 Gendron-Somua", "Type59 Gold", "Object 703 II", "СТГ Гвардеец", "HWK 30", "СТГ",
                 "R143 T 29", "R140 M4 Loza", "VK 168.01 (M)", "СУ-130ПМ", "ЛТ-432", "T-103", "Kanonenjagdpanzer 105", "Объект 252У Защитник", "Т-44-100 (Б)", "G138 VK168 02", "ИС-6 Ч", "Объект 252У", "КВ-122", "Schwarzpanzer 58", "Rheinmetall Skorpion G", "T-34-85 Rudy", "Progetto M35 mod 46",
                 "Progetto M35 mod 46", "Матильда IV", "Pz.Kpfw. V/IV", "T2 Light Tank", "Type 3 Chi-Nu Kai", "Škoda T 40", "Strv m/42-57 Alt A.2", "Черчилль III", "Pz.Kpfw. II Ausf. J", "Ram II", "Škoda T 27", "Pz.Kpfw. S35 739 (f)", "STA-2", "Strv S1", "БТ-СВ", "Pz.Kpfw. B2 740 (f)",
                 "M4A2E4 Sherman", "Heavy Tank No. VI", "S23 Strv 81", "Валентайн II", "Pz.Kpfw. 38H 735 (f)", "M6A2E1", "Primo Victoria", "M22 Locust", "AC 1 Sentinel", "EMIL 1951", "А-32", "Lansen C", "КВ-5", "Т-127", "Matilda Black Prince", "СУ-85И", "TOG II*", "КВ-220-2", "AT 15A", "СУ-76И",
                 "Löwe", "Excelsior", "Pz.Kpfw. T 25", "Sexton I", "СУ-100Y", "Pz.Kpfw. T 15", "Pz.Kpfw. IV hydrostat.", "FV201 (A45)", "СУ-122-44", "8,8 cm Pak 43 Jagdtiger", "E 25", "FV4202 (P)", "Cromwell B", "VK 75.01 (K)", "M4A3E8 Fury", "AC 4 Experimental", "M56 Scorpion", "GB93 Caernarvon AX",
                 "Centurion 5/1", "Dicker Max", "M46 Patton KR", "Firefly VC", "Pz.Kpfw. IV Schmalturm", "Panther/M10", "A99 T92 LT", "Т-34-85М", "FV1066 Senlac", "ИСУ-130", "A115 Chrysler K", "ИС-5 (Объект 730)", "T26E5", "ИС-2", "T26E5 Patriot", "T34 B", "ИСУ-122С", "Großtraktor - Krupp",
                 "A118 M4 Thunderbolt", "Т-54 первый образец", "T26E3 Eagle 7", "GB99 Turtle Mk1", "Объект 244", "Panther mit 8,8 cm L/71", "Chrysler K", "Bat.-Châtillon Bourrasque", "ИС-3 с МЗ", "A122 TS-5", "Bretagne Panther", "БТ-7 артиллерийский", "T78", "M10 RBFM", "Т-28Э с Ф-30",
                 "Pz.Kpfw. III Ausf. K", "King Tiger", "ELC EVEN 90", "Krupp-Steyr Waffenträger", "F89 Canon dassaut de 105", "Т-44-100", "T54E2", "M41D", "AMX M4 1949 Liberte", "TL-1 LPC", "Somua SM", "Rheinmetall Skorpion", "Lorraine 40 t", "AMX M4 mle. 49", "Т-44-100 (Р)",
                 "VK 45.03", "M4A1 Revalorisé", "Turán III prototípus", "WZ-120-1G FT", "AMX Chasseur de chars", "Panzer 58", "59-Patton", "AMX 13 57", "M 41 90 mm", "AMX 13 57 GF", "leKpz M 41 90 mm GF", "T-34-3", "FCM 50 t", "Panzer 58 Mutz", "112", "КВ-2 (р)", "Type 64", "Ch03 WZ 111 A"]

PROMO_TANKS = ["TKS 20", "Type 62", "WZ-111", "Type 97 Te-Ke", "FV215b", "FV215b (183)", "T23E3", "AMX 50 Foch (155)", "Chieftain/T95", "Объект 907", "M60", "AMR 35", "Объект 777", "Т-116", "Т-50-2", "ИС-2М",
               "Об. 279 (р)", "G144 Kpz 50t", "MKA", "Tiger 131", "Т-45", "КВ-220-2 Бета-Тест", "L-60", "MTLS-1G14", "М3 лёгкий", "T1E6", "T95E2", "Pz.Kpfw. V/IV Alpha", "Тетрарх", "Light Mk. VIC", "T7 Combat Car", "T95E6", "ЛТП", "T28 Concept", "A111 T25 Pilot", "Chimera",
               "Excalibur", "T95/FV4201", "Объект 260", "VK 72.01 (K)", "Pz.Kpfw. II Ausf. D", "StuG IV", "T 55A", "M4A1 FL10", "Т-22 ср.", "AE Phase I", "КВ-4 КТТС", "Super Hellcat", "Р128 КВ4 Креславский", "43 M. Toldi III", "121B"]

GARBAGE = ["tank_31233", "tank_31745", "tank_55377", "Black Prince 2019", "tank_60481", "tank_62753"]

def timer(func):

    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        elapsed_time = round(time.time() - start_time, 3)
        print(f"{func.__name__} took {elapsed_time}s")
        return result

    return wrapper


class Stats:
    total_battles: int = None
    total_wins: int = None
    win_rate: float = None
    total_damage: int = None
    avg_damage: float = None

    def __init__(self, total_battles: int, total_wins: int, win_rate: float, total_damage: int, avg_damage: float):
        self.total_battles = total_battles
        self.total_wins = total_wins
        self.win_rate = win_rate
        self.total_damage = total_damage
        self.avg_damage = avg_damage


class Tank:
    nation: str = None
    category: str = None
    title: str = None
    tier: int = None

    stats: Stats = None

    def __init__(self, nation: str, category: str, title: str, tier: int, stats: Stats = None):
        self.nation = nation
        self.category = category
        self.title = title
        self.tier = tier
        self.stats = stats

    def __str__(self):
        return f"{self.title} <{self.nation} {self.tier}>"

    @property
    def premium(self):
        return True if self.title in PREMIUM_TANKS else False

    @property
    def promotional(self):
        return True if self.title in PROMO_TANKS else False

    @property
    def garbage(self):
        return True if self.title in GARBAGE else False


class Extractor:
    raw_data = None
    prepared_data = None
    extracted_data = None

    def __init__(self, raw_data):
        self.raw_data = raw_data
        self._prepare()

    def _prepare(self):
        self.prepared_data = BeautifulSoup(self.raw_data, 'lxml')

    def get_exactly_one_element(self, tag, klass):
        try:
            elems = self.prepared_data.find_all(tag, klass)
            assert len(elems) < 2
            return elems[0]
        except IndexError:
            raise Exception(f"Элемент с тэгом {tag} и классом {klass} не найден")
        except AssertionError:
            raise Exception(f"Найдено слишко много элементов с тэгом {tag} и классом {klass}: {len(elems)}")

    @staticmethod
    def get_children_tags(tag):
        return [x for x in tag.children if isinstance(x, Tag)]

    def extract(self):
        raise NotImplementedError


class AvailablePeriods(Extractor):

    def extract(self):
        div = self.get_exactly_one_element('div', 'statistic_top_links')
        buttons = div.find_all('a', 'button')
        return [StatsPeriod._path_to_date(x.attrs['href']) for x in buttons]


class TankStats(Extractor):
    headers = None

    def get_value(self, contents, title):
        return contents[self.headers.index(title)].text.strip().split("\n")[0]

    def row_to_tank(self, row):
        contents = self.get_children_tags(row)
        tank = Tank(
            nation=self.get_value(contents, 'Нация'),
            category=self.get_value(contents, 'Тип'),
            title=self.get_value(contents, 'Название'),
            tier=int(self.get_value(contents, 'Уровень')),
            stats=Stats(
                total_battles=int(self.get_value(contents, 'Всего боев')),
                total_wins=int(self.get_value(contents, 'Всего побед')),
                win_rate=float(self.get_value(contents, 'Средний процент побед').replace("%", "")),
                total_damage=int(self.get_value(contents, 'Всего урона')),
                avg_damage=float(self.get_value(contents, 'Средний урон')),
            )
        )
        return tank

    def extract(self):
        table = self.get_exactly_one_element("table", "top_table")

        # Заголовок таблицы - это ключ по которому разбирать элементы. Порядок важен.
        self.headers = [str(x.string) for x in self.get_children_tags(table.thead)]

        return [self.row_to_tank(x) for x in self.get_children_tags(table.tbody)]


class Filter:
    tier: int = None

    def __init__(self, tier: int = None):
        self.tier = tier

    def apply(self, data):
        if self.tier:
            return [x for x in data if x.tier == self.tier]


class Order:
    avg_damage: bool = None
    win_rate: bool = None
    total_battles: bool = None

    reverse = True  # Максимальные значения будут сверху

    def apply(self, data):
        if self.avg_damage:
            return sorted(data, key=lambda x: x.stats.avg_damage, reverse=self.reverse)
        elif self.win_rate:
            return sorted(data, key=lambda x: x.stats.win_rate, reverse=self.reverse)
        elif self.total_battles:
            return sorted(data, key=lambda x: x.stats.total_battles, reverse=self.reverse)
        else:
            return data


class StatsPeriod:
    """
    Срез статистики за определенный период.
    """
    source_url = "/wot/ru/top/server/"
    date_format = "%Y-%m-%d"
    date_regex = re.compile('\\d{4}-\\d{2}-\\d{2}')
    period: date = None
    raw_data = None

    def __init__(self, period=None):
        if period:
            if isinstance(period, str):
                self.period = datetime.strptime(self.date_regex.search(period).group(0), self.date_format).date()
            elif issubclass(period.__class__, date):
                self.period = period

    @timer
    def _fetch_data(self):
        url = f"{BASE_URL}{self.source_url}{str(self.period) if self.period else ''}"
        print(f"Fetching {url}...")
        return requests.get(url).content

    @classmethod
    def _path_to_date(cls, url_path):
        return datetime.strptime(cls.date_regex.search(url_path).group(0), cls.date_format).date()

    @classmethod
    def _date_to_path(cls, d):
        return f"{BASE_URL}{cls.source_url}{str(d)}"

    @classmethod
    @timer
    def get_available_periods(cls):
        data = cls()._fetch_data()
        return AvailablePeriods(data).extract()

    @timer
    def get_stats(self, filter:Filter = None):
        self.raw_data = self._fetch_data()
        stats = TankStats(self.raw_data).extract()
        return stats


def get_table(stats):
    data = [
        (
            'Нация',
            'Тип',
            'Название',
            'Уровень',
            'Всего боев',
            'Всего побед',
            'Средний процент побед',
            'Всего урона',
            'Средний урон'
        )
    ]
    for tank in stats:
        data.append(
            (
                tank.nation,
                tank.category,
                tank.title,
                tank.tier,
                tank.stats.total_battles,
                tank.stats.total_wins,
                tank.stats.win_rate,
                tank.stats.total_damage,
                tank.stats.avg_damage
            )
        )

    t = AsciiTable(data, title="Статистика техники по сайту КТТС")
    return t.table
