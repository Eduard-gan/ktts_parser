import argparse
from ktts import StatsPeriod, get_table, Filter, Order


# Парсинг аргументов
parser = argparse.ArgumentParser(description='Routine MFO operations helper')
parser.add_argument('--cuts', action='store_true', help='Display all available stat cuts')
parser.add_argument('-c', help='Select a statistics cut', default='latest')
parser.add_argument('-t', help='Filter tanks by tier')
parser.add_argument('-o', help='Order tanks by attribute', action='append')
parser.add_argument('-a', help='Calculate aggregate data', action='append')
parser.add_argument('-l', help='Only linear tanks', action='store_true')
parser.add_argument('-p', help='Only premium tanks', action='store_true')
args = parser.parse_args()


SPECIAL_STAT_CUTS = ('all', 'latest')


assert args.c in SPECIAL_STAT_CUTS or StatsPeriod(args.c)

stats = None
if args.cuts:
    for date in StatsPeriod.get_available_periods():
        print(str(date))

elif args.c == SPECIAL_STAT_CUTS[0]:  # all
    raise NotImplementedError

elif args.c == SPECIAL_STAT_CUTS[1]:  # latest
    stats = StatsPeriod().get_stats()


if stats:

    stats = [x for x in stats if not x.garbage]

    if args.l:
        stats = [x for x in stats if not x.premium and not x.promotional]
    elif args.p:
        stats = [x for x in stats if x.premium]

    if args.t:
        stats = Filter(tier=int(args.t)).apply(stats)

    if args.o:
        for order_attr in args.o:
            ordering = Order()
            setattr(ordering, order_attr, True)
            stats = ordering.apply(stats)

    if args.a:
        for aggr in args.a:
            if aggr == "avg_avg_damage":
                print(f"avg_avg_damage: {sum([x.stats.avg_damage for x in stats])/len(stats)}")
            if aggr == "avg_win_rate":
                print(f"avg_avg_damage: {sum([x.stats.win_rate for x in stats])/len(stats)}")

    print(get_table(stats))
